"""
Cost Guardian -- Budget watchdog for multi-agent orchestration.

Zero token cost (plain Python, no LLM calls).
Monitors usage_log.json and enforces budget limits.
Writes PAUSE/STOP signals to agents/BULLETIN.md when limits are approached/exceeded.

Usage:
    python agents/cost-guardian.py --check          # One-time budget check
    python agents/cost-guardian.py --watch           # Continuous monitoring (every 5 min)
    python agents/cost-guardian.py --watch --interval 60  # Custom interval in seconds
    python agents/cost-guardian.py --reset-signal    # Clear PAUSE/STOP signal from BULLETIN.md
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
USAGE_LOG = REPO_ROOT / "usage_log.json"
BULLETIN = REPO_ROOT / "agents" / "BULLETIN.md"
AGENTS_DIR = REPO_ROOT / "agents"

# Budget limits
DAILY_WARNING = 3.00    # Warn at $3/day
DAILY_LIMIT = 5.00      # Pause at $5/day
MONTHLY_WARNING = 30.00  # Warn at $30/month
MONTHLY_LIMIT = 50.00    # Stop at $50/month
PER_AGENT_LIMIT = 5.00   # Per-agent session budget


def load_usage_log() -> dict | None:
    """Load usage_log.json, return None on failure."""
    try:
        return json.loads(USAGE_LOG.read_text(encoding="utf-8"))
    except Exception:
        return None


def get_today_spend(usage: dict) -> float:
    """Get today's total spend from usage log."""
    summary = usage.get("summary", {})
    daily = summary.get("daily", {})
    today_key = datetime.now().strftime("%Y-%m-%d")
    today_data = daily.get(today_key, {})
    return today_data.get("cost_usd", 0.0)


def get_month_spend(usage: dict) -> float:
    """Get current month's total spend from usage log."""
    summary = usage.get("summary", {})
    monthly = summary.get("monthly", {})
    month_key = datetime.now().strftime("%Y-%m")
    month_data = monthly.get(month_key, {})
    return month_data.get("cost_usd", 0.0)


def get_agent_session_costs() -> dict[str, float]:
    """Read all agent state.json files and return session costs."""
    costs = {}
    for agent_dir in AGENTS_DIR.iterdir():
        if agent_dir.is_dir() and agent_dir.name != "_template":
            state_file = agent_dir / "state.json"
            if state_file.exists():
                try:
                    state = json.loads(state_file.read_text(encoding="utf-8"))
                    costs[agent_dir.name] = state.get("session_cost_usd", 0.0)
                except Exception:
                    costs[agent_dir.name] = -1.0  # Error reading
    return costs


def update_bulletin_signal(signal: str, reason: str) -> None:
    """Update the SIGNAL line in BULLETIN.md."""
    if not BULLETIN.exists():
        print(f"  [!] BULLETIN.md not found at {BULLETIN}")
        return

    content = BULLETIN.read_text(encoding="utf-8")

    # Update the signal line
    new_signal_line = f"- SIGNAL: {signal} ({reason} at {datetime.now().strftime('%H:%M:%S')})"
    content = re.sub(
        r"- SIGNAL:.*",
        new_signal_line,
        content,
    )

    # Update budget status section
    today_spend = 0.0
    month_spend = 0.0
    usage = load_usage_log()
    if usage:
        today_spend = get_today_spend(usage)
        month_spend = get_month_spend(usage)

    status_word = "HEALTHY"
    if signal == "STOP":
        status_word = "STOPPED"
    elif signal == "PAUSE":
        status_word = "PAUSED"
    elif today_spend > DAILY_WARNING or month_spend > MONTHLY_WARNING:
        status_word = "WARNING"

    content = re.sub(
        r"- Today spent: \$[\d.]+",
        f"- Today spent: ${today_spend:.2f}",
        content,
    )
    content = re.sub(
        r"- Month spent: \$[\d.]+",
        f"- Month spent: ${month_spend:.2f}",
        content,
    )
    content = re.sub(
        r"- Status: \w+",
        f"- Status: {status_word}",
        content,
    )

    BULLETIN.write_text(content, encoding="utf-8")


def check_budgets() -> str:
    """
    Check all budget limits. Returns signal level:
    - "NONE" = all clear
    - "WARNING" = approaching limits
    - "PAUSE" = daily limit reached
    - "STOP" = monthly limit reached
    """
    usage = load_usage_log()
    if not usage:
        print("  [!] Cannot read usage_log.json -- skipping budget check")
        return "NONE"

    today_spend = get_today_spend(usage)
    month_spend = get_month_spend(usage)
    agent_costs = get_agent_session_costs()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n  Budget Check @ {now}")
    print(f"  {'='*40}")
    print(f"  Today:  ${today_spend:.4f} / ${DAILY_LIMIT:.2f}")
    print(f"  Month:  ${month_spend:.4f} / ${MONTHLY_LIMIT:.2f}")

    if agent_costs:
        print(f"  {'-'*40}")
        print(f"  Per-agent session costs:")
        for agent, cost in sorted(agent_costs.items()):
            flag = " [!]" if cost >= PER_AGENT_LIMIT else ""
            print(f"    {agent}: ${cost:.4f}{flag}")

    # Determine signal level
    signal = "NONE"
    reason = ""

    # Check per-agent limits
    for agent, cost in agent_costs.items():
        if cost >= PER_AGENT_LIMIT:
            signal = "PAUSE"
            reason = f"Agent '{agent}' exceeded session budget (${cost:.2f} >= ${PER_AGENT_LIMIT:.2f})"
            print(f"\n  [PAUSE] {reason}")

    # Check daily limits (overrides per-agent)
    if today_spend >= DAILY_LIMIT:
        signal = "PAUSE"
        reason = f"Daily spend ${today_spend:.2f} >= ${DAILY_LIMIT:.2f}"
        print(f"\n  [PAUSE] {reason}")
    elif today_spend >= DAILY_WARNING:
        if signal == "NONE":
            signal = "WARNING"
            reason = f"Daily spend ${today_spend:.2f} approaching limit ${DAILY_LIMIT:.2f}"
        print(f"\n  [WARNING] {reason}")

    # Check monthly limits (highest priority)
    if month_spend >= MONTHLY_LIMIT:
        signal = "STOP"
        reason = f"Monthly spend ${month_spend:.2f} >= ${MONTHLY_LIMIT:.2f}"
        print(f"\n  [STOP] {reason}")
    elif month_spend >= MONTHLY_WARNING:
        if signal not in ("PAUSE", "STOP"):
            signal = "WARNING"
            reason = f"Monthly spend ${month_spend:.2f} approaching limit ${MONTHLY_LIMIT:.2f}"
        print(f"\n  [WARNING] {reason}")

    if signal == "NONE":
        print(f"\n  [OK] All budgets healthy")

    return signal


def run_check():
    """Run a single budget check and update BULLETIN.md if needed."""
    signal = check_budgets()

    if signal in ("PAUSE", "STOP"):
        reason = "budget limit reached"
        usage = load_usage_log()
        if usage:
            today = get_today_spend(usage)
            month = get_month_spend(usage)
            reason = f"daily=${today:.2f} monthly=${month:.2f}"
        update_bulletin_signal(signal, reason)
        print(f"\n  >> BULLETIN.md updated with {signal} signal")
    elif signal == "WARNING":
        update_bulletin_signal("NONE", "warning issued")
        print(f"\n  >> Warning logged, no signal change")
    else:
        update_bulletin_signal("NONE", "healthy")


def run_watch(interval: int):
    """Continuous monitoring loop."""
    print(f"Cost Guardian watching (interval: {interval}s)")
    print(f"Press Ctrl+C to stop\n")

    try:
        while True:
            run_check()
            print(f"\n  Next check in {interval}s...")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\nCost Guardian stopped.")


def reset_signal():
    """Clear any PAUSE/STOP signal from BULLETIN.md."""
    update_bulletin_signal("NONE", "manual reset")
    print("Signal cleared in BULLETIN.md")


def main():
    parser = argparse.ArgumentParser(description="Cost Guardian -- Budget watchdog")
    parser.add_argument("--check", action="store_true", help="One-time budget check")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring")
    parser.add_argument("--interval", type=int, default=300, help="Watch interval in seconds (default: 300)")
    parser.add_argument("--reset-signal", action="store_true", help="Clear PAUSE/STOP signal")

    args = parser.parse_args()

    if args.reset_signal:
        reset_signal()
    elif args.watch:
        run_watch(args.interval)
    elif args.check:
        run_check()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
