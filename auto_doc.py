#!/usr/bin/env python3
"""
Auto-Documentation System for Automation Machine
Automatically updates documentation based on system activity.
Hooks into automation_brain.py to track and document everything.
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Paths
BASE_DIR = Path("C:/automation-machine")
KNOWLEDGE_BASE = BASE_DIR / "knowledge-base"
USAGE_LOG = BASE_DIR / "usage_log.json"
AUTO_DOC_STATE = BASE_DIR / "auto_doc_state.json"

# Documentation paths
CONVERSATION_LOG = KNOWLEDGE_BASE / "research" / "conversation-log.md"
PROJECT_RECAP = KNOWLEDGE_BASE / "PROJECT-RECAP.md"
INDEX_MD = KNOWLEDGE_BASE / "index.md"
PATTERNS_DIR = KNOWLEDGE_BASE / "patterns"
DECISIONS_DIR = KNOWLEDGE_BASE / "decisions"
ACTIVE_PROJECTS = KNOWLEDGE_BASE / "ACTIVE-PROJECTS.md"

# Thresholds
COST_SPIKE_THRESHOLD = 1.0  # $1 per query triggers alert
PATTERN_REUSE_THRESHOLD = 3  # 3+ similar queries = pattern
REMINDER_QUERY_COUNT = 10  # Remind after this many queries


class AutoDoc:
    """
    Auto-documentation system that monitors automation_brain activity
    and updates documentation automatically.
    """

    def __init__(self):
        self.state = self._load_state()
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        PATTERNS_DIR.mkdir(parents=True, exist_ok=True)
        DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
        (KNOWLEDGE_BASE / "research").mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> dict:
        """Load auto-doc state from JSON."""
        if AUTO_DOC_STATE.exists():
            with open(AUTO_DOC_STATE, "r") as f:
                return json.load(f)
        return {
            "last_daily_update": None,
            "last_weekly_update": None,
            "queries_since_reminder": 0,
            "query_patterns": {},  # pattern -> count
            "detected_decisions": [],
            "files_indexed": [],
            "total_documented_queries": 0
        }

    def _save_state(self):
        """Save auto-doc state to JSON."""
        with open(AUTO_DOC_STATE, "w") as f:
            json.dump(self.state, f, indent=2, default=str)

    # =========================================================================
    # HOOKS - Call these from automation_brain.py
    # =========================================================================

    def on_query_complete(self, query: str, response: str, result: dict):
        """
        Hook: Called after each query completes.

        Args:
            query: The user's query
            response: The response text
            result: Dict with tool, model, tokens_in, tokens_out, cost
        """
        # 1. Log to conversation log
        self._append_conversation_log(query, response, result)

        # 2. Check for cost spike
        if result.get("cost", 0) >= COST_SPIKE_THRESHOLD:
            self._log_cost_spike(query, result)

        # 3. Track patterns
        self._track_pattern(query, result)

        # 4. Check for decision keywords
        if self._contains_decision(query, response):
            self._prompt_decision_documentation(query, response)

        # 5. Increment counters
        self.state["queries_since_reminder"] += 1
        self.state["total_documented_queries"] += 1

        # 6. Check if reminder needed
        if self.state["queries_since_reminder"] >= REMINDER_QUERY_COUNT:
            self._show_reminder()
            self.state["queries_since_reminder"] = 0

        # 7. Check for daily/weekly updates
        self._check_scheduled_updates()

        self._save_state()

    def on_file_created(self, file_path: str):
        """
        Hook: Called when a new file is created in knowledge-base.
        """
        path = Path(file_path)
        if KNOWLEDGE_BASE in path.parents or path.parent == KNOWLEDGE_BASE:
            self._update_index(path)
            self.state["files_indexed"].append(str(path))
            self._save_state()

    def on_tool_used(self, tool_name: str, success: bool, cost: float):
        """
        Hook: Called when a tool is used.
        """
        # Could be extended for tool-specific documentation
        pass

    # =========================================================================
    # CONVERSATION LOG
    # =========================================================================

    def _append_conversation_log(self, query: str, response: str, result: dict):
        """Append query/response to conversation log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tool = result.get("tool", "unknown")
        model = result.get("model", "unknown")
        cost = result.get("cost", 0)

        # Truncate long responses
        response_preview = response[:500] + "..." if len(response) > 500 else response

        entry = f"""
---
## [{timestamp}] via {tool} ({model}) - ${cost:.4f}

**Query:** {query}

**Response:**
{response_preview}

"""
        with open(CONVERSATION_LOG, "a", encoding="utf-8") as f:
            f.write(entry)

    # =========================================================================
    # COST SPIKE DETECTION
    # =========================================================================

    def _log_cost_spike(self, query: str, result: dict):
        """Log expensive queries for review."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cost = result.get("cost", 0)
        tool = result.get("tool", "unknown")

        spike_log = BASE_DIR / "cost_spikes.log"
        entry = f"[{timestamp}] ${cost:.4f} via {tool}: {query[:100]}...\n"

        with open(spike_log, "a") as f:
            f.write(entry)

        print(f"\n[AUTO-DOC] Cost spike detected: ${cost:.4f} for this query")
        print(f"           Logged to: {spike_log}")

    # =========================================================================
    # PATTERN TRACKING
    # =========================================================================

    def _track_pattern(self, query: str, result: dict):
        """Track query patterns for potential documentation."""
        # Normalize query to detect patterns
        pattern = self._extract_pattern(query)

        if pattern not in self.state["query_patterns"]:
            self.state["query_patterns"][pattern] = {
                "count": 0,
                "examples": [],
                "tools_used": []
            }

        self.state["query_patterns"][pattern]["count"] += 1

        # Store up to 3 examples
        if len(self.state["query_patterns"][pattern]["examples"]) < 3:
            self.state["query_patterns"][pattern]["examples"].append(query[:100])

        tool = result.get("tool", "unknown")
        if tool not in self.state["query_patterns"][pattern]["tools_used"]:
            self.state["query_patterns"][pattern]["tools_used"].append(tool)

        # Check if pattern should be documented
        if self.state["query_patterns"][pattern]["count"] == PATTERN_REUSE_THRESHOLD:
            self._document_pattern(pattern, self.state["query_patterns"][pattern])

    def _extract_pattern(self, query: str) -> str:
        """Extract a normalized pattern from a query."""
        # Remove specific details, keep structure
        pattern = query.lower()

        # Remove numbers
        pattern = re.sub(r'\d+', 'N', pattern)

        # Remove quoted strings
        pattern = re.sub(r'"[^"]*"', '"X"', pattern)
        pattern = re.sub(r"'[^']*'", "'X'", pattern)

        # Normalize whitespace
        pattern = " ".join(pattern.split())

        # Truncate
        return pattern[:50]

    def _document_pattern(self, pattern: str, data: dict):
        """Create a pattern document when threshold is reached."""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        safe_name = re.sub(r'[^\w\s-]', '', pattern)[:30].strip().replace(' ', '-')
        pattern_file = PATTERNS_DIR / f"{safe_name}.md"

        content = f"""# Pattern: {pattern[:50]}

*Auto-generated: {timestamp}*
*Occurrences: {data['count']}*

## Description

This pattern was detected {data['count']} times in queries.

## Examples

"""
        for i, example in enumerate(data['examples'], 1):
            content += f"{i}. {example}\n"

        content += f"""
## Tools Used

{', '.join(data['tools_used'])}

## Notes

*(Add notes about when to use this pattern)*
"""

        with open(pattern_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"\n[AUTO-DOC] New pattern documented: {pattern_file.name}")
        print(f"           Detected {data['count']} similar queries")

    # =========================================================================
    # DECISION DETECTION
    # =========================================================================

    def _contains_decision(self, query: str, response: str) -> bool:
        """Check if query/response contains decision keywords."""
        decision_keywords = [
            "decided", "chose", "going with", "selected", "picked",
            "will use", "opting for", "decision:", "approach:",
            "strategy:", "solution:", "recommendation:"
        ]

        text = (query + " " + response).lower()
        return any(kw in text for kw in decision_keywords)

    def _prompt_decision_documentation(self, query: str, response: str):
        """Prompt user to document a detected decision."""
        self.state["detected_decisions"].append({
            "timestamp": datetime.now().isoformat(),
            "query": query[:100],
            "response_preview": response[:200]
        })

        print("\n" + "=" * 50)
        print("[AUTO-DOC] Decision detected!")
        print("=" * 50)
        print(f"Query: {query[:80]}...")
        print("\nWould you like to document this decision?")
        print("  1. Run: python auto_doc.py --document-decision")
        print("  2. Or ignore if not important")
        print("=" * 50)

    # =========================================================================
    # SCHEDULED UPDATES
    # =========================================================================

    def _check_scheduled_updates(self):
        """Check if daily/weekly updates are due."""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")

        # Daily update (after 6 PM)
        if now.hour >= 18:
            if self.state["last_daily_update"] != today:
                self._update_daily_stats()
                self.state["last_daily_update"] = today

        # Weekly update (Sunday)
        if now.weekday() == 6:  # Sunday
            week = now.strftime("%Y-W%W")
            if self.state["last_weekly_update"] != week:
                self._create_weekly_summary()
                self.state["last_weekly_update"] = week

    def _update_daily_stats(self):
        """Update PROJECT-RECAP with daily stats."""
        usage = self._load_usage_log()
        today = datetime.now().strftime("%Y-%m-%d")

        daily = usage.get("summary", {}).get("daily", {}).get(today, {})
        if not daily:
            return

        print(f"\n[AUTO-DOC] Daily stats update for {today}")
        print(f"           Queries: {daily.get('queries', 0)}")
        print(f"           Cost: ${daily.get('cost_usd', 0):.4f}")

    def _create_weekly_summary(self):
        """Create weekly summary document."""
        now = datetime.now()
        week_num = now.strftime("%Y-W%W")

        usage = self._load_usage_log()
        summary = usage.get("summary", {})

        # Calculate week's stats from daily data
        week_start = now - timedelta(days=now.weekday() + 1)
        week_queries = 0
        week_cost = 0.0

        for day_str, day_data in summary.get("daily", {}).items():
            try:
                day = datetime.strptime(day_str, "%Y-%m-%d")
                if day >= week_start:
                    week_queries += day_data.get("queries", 0)
                    week_cost += day_data.get("cost_usd", 0)
            except ValueError:
                continue

        # Create weekly summary file
        summary_file = DECISIONS_DIR / f"weekly-summary-{week_num}.md"

        content = f"""# Weekly Summary: {week_num}

*Generated: {now.strftime("%Y-%m-%d %H:%M")}*

## Statistics

| Metric | Value |
|--------|-------|
| Total Queries | {week_queries} |
| Total Cost | ${week_cost:.4f} |
| Avg Cost/Query | ${week_cost/max(week_queries,1):.4f} |

## Tool Usage

"""
        by_tool = summary.get("by_tool", {})
        for tool, stats in by_tool.items():
            if stats.get("queries", 0) > 0:
                content += f"- **{tool}**: {stats['queries']} queries, ${stats['cost_usd']:.4f}\n"

        content += """
## Patterns Detected

"""
        # Add top patterns
        patterns = sorted(
            self.state["query_patterns"].items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:5]

        for pattern, data in patterns:
            content += f"- {pattern}: {data['count']} occurrences\n"

        content += """
## Decisions Made

"""
        for dec in self.state.get("detected_decisions", [])[-5:]:
            content += f"- {dec['query'][:60]}...\n"

        content += """
## Notes

*(Add weekly observations here)*
"""

        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"\n[AUTO-DOC] Weekly summary created: {summary_file}")

    # =========================================================================
    # INDEX UPDATES
    # =========================================================================

    def _update_index(self, new_file: Path):
        """Update index.md with new file."""
        relative = new_file.relative_to(KNOWLEDGE_BASE)

        # Determine section based on path
        if "patterns" in str(relative):
            section = "Patterns"
        elif "decisions" in str(relative):
            section = "Decisions"
        elif "research" in str(relative):
            section = "Research"
        elif "projects" in str(relative):
            section = "Projects"
        else:
            section = "Other"

        print(f"\n[AUTO-DOC] New file detected: {relative}")
        print(f"           Section: {section}")
        print(f"           Update index.md manually or run: python auto_doc.py --rebuild-index")

    # =========================================================================
    # REMINDERS
    # =========================================================================

    def _show_reminder(self):
        """Show reminder to document decisions."""
        print("\n" + "=" * 50)
        print(f"[AUTO-DOC] {REMINDER_QUERY_COUNT} queries completed!")
        print("=" * 50)
        print("Quick check:")
        print("  - Any decisions made that should be documented?")
        print("  - Any patterns emerging in your queries?")
        print("  - Run: python auto_doc.py --status for details")
        print("=" * 50)

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def _load_usage_log(self) -> dict:
        """Load usage log."""
        if USAGE_LOG.exists():
            with open(USAGE_LOG, "r") as f:
                return json.load(f)
        return {}

    # =========================================================================
    # CLI COMMANDS
    # =========================================================================

    def show_status(self):
        """Show auto-doc status."""
        print("\n" + "=" * 60)
        print("AUTO-DOCUMENTATION STATUS")
        print("=" * 60)

        print(f"\nTotal documented queries: {self.state['total_documented_queries']}")
        print(f"Queries since last reminder: {self.state['queries_since_reminder']}")
        print(f"Last daily update: {self.state['last_daily_update'] or 'Never'}")
        print(f"Last weekly update: {self.state['last_weekly_update'] or 'Never'}")

        print(f"\nPatterns tracked: {len(self.state['query_patterns'])}")
        if self.state['query_patterns']:
            print("Top patterns:")
            sorted_patterns = sorted(
                self.state['query_patterns'].items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:5]
            for pattern, data in sorted_patterns:
                print(f"  - {pattern[:40]}: {data['count']} times")

        print(f"\nPending decisions: {len(self.state['detected_decisions'])}")
        for dec in self.state['detected_decisions'][-3:]:
            print(f"  - {dec['query'][:50]}...")

        print(f"\nFiles indexed: {len(self.state['files_indexed'])}")

        print("\n" + "=" * 60)

    def document_decision(self):
        """Interactive decision documentation."""
        if not self.state['detected_decisions']:
            print("No pending decisions to document.")
            return

        dec = self.state['detected_decisions'][-1]

        print("\n" + "=" * 60)
        print("DOCUMENT DECISION")
        print("=" * 60)
        print(f"\nQuery: {dec['query']}")
        print(f"\nResponse preview: {dec['response_preview']}")

        title = input("\nDecision title (or 'skip'): ").strip()
        if title.lower() == 'skip':
            self.state['detected_decisions'].pop()
            self._save_state()
            return

        context = input("Context/reason: ").strip()

        # Create decision document
        timestamp = datetime.now().strftime("%Y-%m-%d")
        safe_title = re.sub(r'[^\w\s-]', '', title)[:30].strip().replace(' ', '-')
        decision_file = DECISIONS_DIR / f"{timestamp}-{safe_title}.md"

        content = f"""# Decision: {title}

*Date: {timestamp}*

## Context

{context}

## Decision

{dec['query']}

## Rationale

{dec['response_preview']}

## Consequences

*(To be filled in)*
"""

        with open(decision_file, "w", encoding="utf-8") as f:
            f.write(content)

        self.state['detected_decisions'].pop()
        self._save_state()

        print(f"\nDecision documented: {decision_file}")

    def rebuild_index(self):
        """Rebuild index.md with all files."""
        print("Scanning knowledge base...")

        files_by_section = {
            "patterns": [],
            "decisions": [],
            "research": [],
            "projects": []
        }

        for md_file in KNOWLEDGE_BASE.rglob("*.md"):
            if md_file.name in ["index.md", "PROJECT-RECAP.md"]:
                continue

            relative = md_file.relative_to(KNOWLEDGE_BASE)
            parts = relative.parts

            if parts[0] in files_by_section:
                files_by_section[parts[0]].append(relative)

        print("\nFiles found:")
        for section, files in files_by_section.items():
            print(f"  {section}: {len(files)} files")
            for f in files:
                print(f"    - {f}")

        print("\nTo update index.md, edit it manually with these files.")

    def force_daily_update(self):
        """Force daily stats update."""
        self._update_daily_stats()
        self.state["last_daily_update"] = datetime.now().strftime("%Y-%m-%d")
        self._save_state()
        print("Daily update completed.")

    def force_weekly_summary(self):
        """Force weekly summary creation."""
        self._create_weekly_summary()
        self.state["last_weekly_update"] = datetime.now().strftime("%Y-W%W")
        self._save_state()
        print("Weekly summary created.")

    def standalone_mode(self, use_local_llm: bool = True):
        """
        Standalone mode - works without cloud LLMs.
        Routes queries to local Ollama models when available.

        Args:
            use_local_llm: If True, enables querying local LLMs
        """
        self._print_banner()

        # Check local LLM availability
        local_llm_available = False
        brain = None

        if use_local_llm:
            local_llm_available = self._check_local_llm()
            if local_llm_available:
                try:
                    sys.path.insert(0, str(BASE_DIR))
                    from automation_brain import AutomationBrain
                    brain = AutomationBrain(verbose=False)
                    print("\n[LOCAL LLM CONNECTED] Queries will use Ollama models")
                except Exception as e:
                    print(f"\n[LOCAL LLM ERROR] {e}")
                    local_llm_available = False

        # Load and display current state
        print("\n[LOADING STATE...]")
        self._display_project_status()

        # Interactive loop
        print("\n" + "=" * 60)
        print("STANDALONE MODE - Interactive Helper")
        if local_llm_available:
            print("LOCAL LLM: ENABLED (type any question to ask)")
        else:
            print("LOCAL LLM: DISABLED (install Ollama for AI queries)")
        print("=" * 60)
        print("Commands:")
        print("  status    - Show current project status")
        print("  next      - Show suggested next steps")
        print("  files     - List key files and their purposes")
        print("  checklist - Show todo checklist from active project")
        print("  commands  - Show useful commands to run")
        print("  context   - Show project context (for pasting to LLM)")
        print("  help      - Show this help")
        print("  quit      - Exit standalone mode")
        if local_llm_available:
            print("\nOr just type a question to query local LLM:")
            print("  Example: \"How do I create a ComfyUI workflow?\"")
        print("-" * 60)

        while True:
            try:
                user_input = input("\nstandalone> ").strip()

                if not user_input:
                    continue

                cmd = user_input.lower()

                if cmd == "quit" or cmd == "exit":
                    print("Exiting standalone mode.")
                    break
                elif cmd == "status":
                    self._display_project_status()
                elif cmd == "next":
                    self._suggest_next_steps()
                elif cmd == "files":
                    self._show_key_files()
                elif cmd == "checklist":
                    self._show_checklist()
                elif cmd == "commands":
                    self._show_useful_commands()
                elif cmd == "context":
                    self._show_context_for_llm()
                elif cmd == "help":
                    print("\nCommands:")
                    print("  status    - Show current project status")
                    print("  next      - Show suggested next steps")
                    print("  files     - List key files and their purposes")
                    print("  checklist - Show todo checklist from active project")
                    print("  commands  - Show useful commands to run")
                    print("  context   - Show project context (for pasting to LLM)")
                    print("  help      - Show this help")
                    print("  quit      - Exit standalone mode")
                    if local_llm_available:
                        print("\nOr type any question to query local LLM")
                elif local_llm_available and brain:
                    # Treat as a query to local LLM
                    self._query_local_llm(brain, user_input)
                else:
                    print(f"Unknown command: {cmd}")
                    print("Type 'help' for available commands.")
                    if not local_llm_available:
                        print("(Install Ollama to enable free-form queries)")

            except KeyboardInterrupt:
                print("\nExiting standalone mode.")
                break
            except Exception as e:
                print(f"Error: {e}")

    def _check_local_llm(self) -> bool:
        """Check if local Ollama is available."""
        import urllib.request
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except Exception:
            return False

    def _query_local_llm(self, brain, query: str):
        """Query the local LLM through automation_brain."""
        print("\n[Querying local LLM...]")
        print("-" * 40)

        try:
            # Force local tool (qwen or deepseek)
            response = brain.process(query, force_tool="local-qwen")
            print(response)
        except Exception as e:
            # Try fallback to deepseek
            try:
                response = brain.process(query, force_tool="local-deepseek")
                print(response)
            except Exception as e2:
                print(f"[ERROR] Could not query local LLM: {e2}")
                print("Make sure Ollama is running with qwen or deepseek model.")

        print("-" * 40)

    def _show_context_for_llm(self):
        """Show project context formatted for pasting to external LLM."""
        print("\n" + "=" * 60)
        print("PROJECT CONTEXT (copy this to any LLM)")
        print("=" * 60)

        print("\n## Current Project\n")

        if ACTIVE_PROJECTS.exists():
            with open(ACTIVE_PROJECTS, "r", encoding="utf-8") as f:
                # Only show first 100 lines to keep it manageable
                lines = f.readlines()[:100]
                print("".join(lines))

        print("\n## System Info\n")
        print("- Location: C:\\automation-machine")
        print("- Main script: automation_brain.py")
        print("- Local LLMs: Ollama (qwen, deepseek)")
        print("- Remote: ComfyUI at 100.64.130.71:8188")

        print("\n" + "=" * 60)

    def _print_banner(self):
        """Print standalone mode banner."""
        print("\n" + "=" * 60)
        print("     AUTOMATION MACHINE - STANDALONE MODE")
        print("=" * 60)
        print("No external LLM needed. This tool provides:")
        print("  - Current project status")
        print("  - Suggested next steps")
        print("  - File references")
        print("  - Useful commands")
        print("=" * 60)

    def _display_project_status(self):
        """Display current project status from ACTIVE-PROJECTS.md."""
        print("\n" + "-" * 40)
        print("CURRENT PROJECT STATUS")
        print("-" * 40)

        if ACTIVE_PROJECTS.exists():
            with open(ACTIVE_PROJECTS, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract key information
            lines = content.split('\n')
            in_current_phase = False
            in_next_steps = False

            for line in lines:
                # Find project name and status
                if line.startswith("## ") and "Backlog" not in line and "EOD" not in line and "Handoff" not in line:
                    print(f"\nProject: {line[3:]}")
                elif line.startswith("**Status:**"):
                    print(f"  {line}")
                elif line.startswith("**Deadline:**"):
                    print(f"  {line}")
                elif "Current Phase:" in line:
                    in_current_phase = True
                    print(f"\n{line}")
                elif in_current_phase and line.startswith("**"):
                    print(f"  {line}")
                    in_current_phase = False
                elif "Next Steps" in line:
                    in_next_steps = True
                    print(f"\n{line}")
                elif in_next_steps:
                    if line.startswith("###") or line.startswith("---"):
                        in_next_steps = False
                    elif line.strip():
                        print(f"  {line}")
        else:
            print("[ACTIVE-PROJECTS.md not found]")

        # Show usage stats
        print("\n" + "-" * 40)
        print("USAGE STATS")
        print("-" * 40)
        usage = self._load_usage_log()
        if usage:
            summary = usage.get("summary", {})
            total = summary.get("total", {})
            print(f"  Total queries: {total.get('queries', 0)}")
            print(f"  Total cost: ${total.get('cost_usd', 0):.6f}")

            today = datetime.now().strftime("%Y-%m-%d")
            daily = summary.get("daily", {}).get(today, {})
            if daily:
                print(f"  Today's queries: {daily.get('queries', 0)}")
                print(f"  Today's cost: ${daily.get('cost_usd', 0):.6f}")
        else:
            print("  [No usage data]")

    def _suggest_next_steps(self):
        """Suggest next steps based on ACTIVE-PROJECTS.md."""
        print("\n" + "-" * 40)
        print("SUGGESTED NEXT STEPS")
        print("-" * 40)

        if ACTIVE_PROJECTS.exists():
            with open(ACTIVE_PROJECTS, "r", encoding="utf-8") as f:
                content = f.read()

            # Find incomplete items ([ ])
            incomplete = []
            lines = content.split('\n')
            for line in lines:
                if "[ ]" in line:
                    item = line.replace("[ ]", "").strip()
                    item = item.lstrip("0123456789.-) ")
                    if item:
                        incomplete.append(item)

            if incomplete:
                print("\nIncomplete tasks from ACTIVE-PROJECTS.md:")
                for i, item in enumerate(incomplete[:5], 1):
                    print(f"  {i}. {item}")
                if len(incomplete) > 5:
                    print(f"  ... and {len(incomplete) - 5} more")

                print("\nRecommendation:")
                print(f"  Start with: {incomplete[0]}")
            else:
                print("  All tasks appear complete!")
                print("  Check ACTIVE-PROJECTS.md for what's next.")
        else:
            print("  [Cannot load ACTIVE-PROJECTS.md]")

        print("\nGeneral workflow:")
        print("  1. Pick a task from the checklist")
        print("  2. Run relevant commands")
        print("  3. Update ACTIVE-PROJECTS.md when done")
        print("  4. Run: python auto_doc.py --update-projects")

    def _show_key_files(self):
        """Show key files and their purposes."""
        print("\n" + "-" * 40)
        print("KEY FILES")
        print("-" * 40)

        files = [
            ("automation_brain.py", "Main orchestrator - routes queries to tools"),
            ("auto_doc.py", "This file - documentation system"),
            ("tools_config.json", "API keys and tool configurations"),
            ("HANDOFF.md", "Handoff protocol for resuming work"),
            ("knowledge-base/ACTIVE-PROJECTS.md", "Current project status and todos"),
            ("knowledge-base/PROJECT-RECAP.md", "System architecture overview"),
            ("auto_doc_state.json", "Auto-doc state (patterns, decisions)"),
            ("usage_log.json", "Query history and cost tracking"),
        ]

        print("\nCore Files:")
        for filename, purpose in files:
            filepath = BASE_DIR / filename
            exists = "OK" if filepath.exists() else "MISSING"
            print(f"  [{exists}] {filename}")
            print(f"         {purpose}")

    def _show_checklist(self):
        """Show todo checklist from active project."""
        print("\n" + "-" * 40)
        print("PROJECT CHECKLIST")
        print("-" * 40)

        if ACTIVE_PROJECTS.exists():
            with open(ACTIVE_PROJECTS, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split('\n')
            in_whatneeded = False

            print("\nFrom ACTIVE-PROJECTS.md:")
            for line in lines:
                if "What's needed" in line:
                    in_whatneeded = True
                    continue
                elif in_whatneeded:
                    if line.startswith("###") or line.startswith("---"):
                        in_whatneeded = False
                    elif "[x]" in line.lower() or "[ ]" in line:
                        status = "DONE" if "[x]" in line.lower() else "TODO"
                        item = line.replace("[x]", "").replace("[X]", "").replace("[ ]", "").strip()
                        item = item.lstrip("0123456789.-) ")
                        if item:
                            print(f"  [{status}] {item}")
        else:
            print("  [Cannot load ACTIVE-PROJECTS.md]")

    def _show_useful_commands(self):
        """Show useful commands the user can run."""
        print("\n" + "-" * 40)
        print("USEFUL COMMANDS")
        print("-" * 40)

        print("\nStatus & Info:")
        print("  python auto_doc.py --status")
        print("  python auto_doc.py --standalone-mode")

        print("\nRunning Queries:")
        print("  python automation_brain.py \"your question here\"")
        print("  python automation_brain.py --tool perplexity \"web search\"")
        print("  python automation_brain.py --tool local-qwen \"code help\"")

        print("\nUpdating Documentation:")
        print("  python auto_doc.py --update-projects")
        print("  python auto_doc.py --update-projects --eod \"summary\"")
        print("  python auto_doc.py --daily-update")
        print("  python auto_doc.py --weekly-summary")

        print("\nEmergency Handoff:")
        print("  emergency-handoff.bat")
        print("  (Outputs everything for pasting to another LLM)")

    def update_projects(self, eod_summary: Optional[str] = None):
        """
        Update ACTIVE-PROJECTS.md with current state data.

        Args:
            eod_summary: Optional end-of-day summary to append
        """
        if not ACTIVE_PROJECTS.exists():
            print(f"[AUTO-DOC] ACTIVE-PROJECTS.md not found at {ACTIVE_PROJECTS}")
            return

        # Load current state data
        usage = self._load_usage_log()
        today = datetime.now().strftime("%Y-%m-%d")

        # Read current file
        with open(ACTIVE_PROJECTS, "r", encoding="utf-8") as f:
            content = f.read()

        # Update last auto-update timestamp
        content = re.sub(
            r'\*Last auto-update:.*\*',
            f'*Last auto-update: {today}*',
            content
        )

        # Prepare stats summary
        summary = usage.get("summary", {})
        today_stats = summary.get("daily", {}).get(today, {})
        total_queries = today_stats.get("queries", 0)
        total_cost = today_stats.get("cost_usd", 0)

        # If EOD summary provided, add it
        if eod_summary:
            # Find the EOD Summaries section and add entry
            eod_section_pattern = r'(## EOD Summaries\n)'
            new_entry = f"### {today}\n- {eod_summary}\n- Queries today: {total_queries}, Cost: ${total_cost:.6f}\n\n"

            if re.search(eod_section_pattern, content):
                # Add after the header
                content = re.sub(
                    eod_section_pattern,
                    f'\\1\n{new_entry}',
                    content
                )
            else:
                # Append new section before handoff command
                handoff_pattern = r'(## Handoff Command)'
                if re.search(handoff_pattern, content):
                    content = re.sub(
                        handoff_pattern,
                        f'## EOD Summaries\n\n{new_entry}---\n\n\\1',
                        content
                    )

        # Write updated content
        with open(ACTIVE_PROJECTS, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"\n[AUTO-DOC] ACTIVE-PROJECTS.md updated")
        print(f"           Date: {today}")
        print(f"           Today's queries: {total_queries}")
        print(f"           Today's cost: ${total_cost:.6f}")
        if eod_summary:
            print(f"           EOD summary added: {eod_summary[:50]}...")


# =============================================================================
# WRAPPER FOR automation_brain.py
# =============================================================================

def wrap_brain():
    """
    Wrapper that runs automation_brain with auto-doc hooks.
    Use this instead of running automation_brain.py directly.
    """
    # Import brain
    sys.path.insert(0, str(BASE_DIR))
    from automation_brain import AutomationBrain

    # Create auto-doc instance
    auto_doc = AutoDoc()

    # Create brain with our hooks
    brain = AutomationBrain(verbose="-v" in sys.argv or "--verbose" in sys.argv)

    # Override the process method to add hooks
    original_process = brain.process

    def hooked_process(query: str, force_tool: Optional[str] = None) -> str:
        response = original_process(query, force_tool)

        # Get last result from usage log
        usage = auto_doc._load_usage_log()
        if usage.get("history"):
            last_entry = usage["history"][-1]
            result = {
                "tool": last_entry.get("tool", "unknown"),
                "model": last_entry.get("model", "unknown"),
                "tokens_in": last_entry.get("tokens_in", 0),
                "tokens_out": last_entry.get("tokens_out", 0),
                "cost": last_entry.get("cost_usd", 0)
            }
            auto_doc.on_query_complete(query, response, result)

        return response

    brain.process = hooked_process
    return brain, auto_doc


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Auto-Documentation System for Automation Machine"
    )
    parser.add_argument("query", nargs="*", help="Query to process (with auto-doc)")
    parser.add_argument("--status", action="store_true", help="Show auto-doc status")
    parser.add_argument("--document-decision", action="store_true",
                        help="Document a pending decision")
    parser.add_argument("--rebuild-index", action="store_true",
                        help="Show files to add to index.md")
    parser.add_argument("--daily-update", action="store_true",
                        help="Force daily stats update")
    parser.add_argument("--weekly-summary", action="store_true",
                        help="Force weekly summary creation")
    parser.add_argument("--update-projects", action="store_true",
                        help="Update ACTIVE-PROJECTS.md with current state")
    parser.add_argument("--eod", type=str, default=None,
                        help="EOD summary to append (use with --update-projects)")
    parser.add_argument("--standalone-mode", action="store_true",
                        help="Interactive standalone mode (no external LLM needed)")
    parser.add_argument("--tool", help="Force specific tool")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose mode")

    args = parser.parse_args()

    auto_doc = AutoDoc()

    if args.status:
        auto_doc.show_status()
        return

    if args.document_decision:
        auto_doc.document_decision()
        return

    if args.rebuild_index:
        auto_doc.rebuild_index()
        return

    if args.daily_update:
        auto_doc.force_daily_update()
        return

    if args.weekly_summary:
        auto_doc.force_weekly_summary()
        return

    if args.update_projects:
        auto_doc.update_projects(eod_summary=args.eod)
        return

    if args.standalone_mode:
        auto_doc.standalone_mode()
        return

    if args.query:
        # Run query with auto-doc hooks
        query = " ".join(args.query)
        brain, auto_doc = wrap_brain()

        try:
            response = brain.process(query, args.tool)
            print(response)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Interactive mode with auto-doc
        print("Auto-Doc Wrapped Brain - Interactive Mode")
        print("All queries automatically documented.")
        print("Commands: 'quit', 'status', '--help'")
        print("-" * 40)

        brain, auto_doc = wrap_brain()

        while True:
            try:
                query = input("\n> ").strip()
                if not query:
                    continue
                if query.lower() == "quit":
                    break
                if query.lower() == "status":
                    auto_doc.show_status()
                    continue

                response = brain.process(query, args.tool)
                print(f"\n{response}")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
