"""Batch backtest runner -- runs both strategies across the full watchlist.

Usage:
    python trading/run_all_backtests.py [--period 2y] [--cash 100000]

Outputs:
    - Individual result JSON files in trading/results/
    - Consolidated report in trading/results/report_YYYYMMDD.md
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trading.backtest import run_backtest, save_results
from trading.config import DEFAULT_CASH, DEFAULT_PERIOD, RESULTS_PATH, WATCHLIST

STRATEGIES = ["sma", "rsi"]


def run_all(tickers: list[str], period: str, cash: float) -> list[dict]:
    """Run all strategy/ticker combinations and return results."""
    all_results = []
    total = len(tickers) * len(STRATEGIES)
    idx = 0

    for ticker in tickers:
        for strategy in STRATEGIES:
            idx += 1
            print(f"\n[{idx}/{total}] {ticker} / {strategy.upper()}")
            print("-" * 40)
            try:
                result = run_backtest(ticker, strategy, period, cash)
                save_results(result)
                all_results.append(result)
                print(f"  Return: {result['total_return_pct']:+.2f}%  |  "
                      f"Drawdown: {result['max_drawdown_pct']:.2f}%  |  "
                      f"Sharpe: {result.get('sharpe_ratio', 'N/A')}  |  "
                      f"Trades: {result['trade_count']}")
            except Exception as e:
                print(f"  ERROR: {e}")
                all_results.append({
                    "ticker": ticker,
                    "strategy": strategy,
                    "error": str(e),
                })

    return all_results


def generate_report(results: list[dict], period: str, cash: float) -> str:
    """Generate a markdown performance report from backtest results."""
    lines = []
    lines.append(f"# Backtest Performance Report")
    lines.append(f"")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Period:** {period}  |  **Starting Capital:** ${cash:,.0f}  |  **Position Sizing:** 95% per trade")
    lines.append(f"**Commission:** 0.1% per trade")
    lines.append(f"")

    # Separate successful results from errors
    ok = [r for r in results if "error" not in r]
    errors = [r for r in results if "error" in r]

    if not ok:
        lines.append("No successful backtests to report.")
        return "\n".join(lines)

    # Summary table by strategy
    for strat in STRATEGIES:
        strat_results = [r for r in ok if r["strategy"] == strat]
        if not strat_results:
            continue

        strat_label = "SMA Crossover (20/50)" if strat == "sma" else "RSI Mean Reversion (14, 30/70)"
        lines.append(f"## {strat_label}")
        lines.append(f"")
        lines.append(f"| Ticker | Return % | Max DD % | Sharpe | Trades | Final Value |")
        lines.append(f"|--------|----------|----------|--------|--------|-------------|")

        for r in sorted(strat_results, key=lambda x: x["total_return_pct"], reverse=True):
            sharpe = r.get("sharpe_ratio")
            sharpe_str = f"{sharpe:.2f}" if sharpe is not None else "N/A"
            lines.append(
                f"| {r['ticker']} | {r['total_return_pct']:+.2f} | "
                f"{r['max_drawdown_pct']:.2f} | {sharpe_str} | "
                f"{r['trade_count']} | ${r['final_value']:,.2f} |"
            )

        # Aggregate stats
        avg_return = sum(r["total_return_pct"] for r in strat_results) / len(strat_results)
        avg_dd = sum(r["max_drawdown_pct"] for r in strat_results) / len(strat_results)
        winners = sum(1 for r in strat_results if r["total_return_pct"] > 0)
        losers = sum(1 for r in strat_results if r["total_return_pct"] < 0)
        best = max(strat_results, key=lambda x: x["total_return_pct"])
        worst = min(strat_results, key=lambda x: x["total_return_pct"])

        lines.append(f"")
        lines.append(f"**Avg Return:** {avg_return:+.2f}%  |  **Avg Max DD:** {avg_dd:.2f}%")
        lines.append(f"**Winners:** {winners}  |  **Losers:** {losers}  |  **Flat:** {len(strat_results) - winners - losers}")
        lines.append(f"**Best:** {best['ticker']} ({best['total_return_pct']:+.2f}%)  |  **Worst:** {worst['ticker']} ({worst['total_return_pct']:+.2f}%)")
        lines.append(f"")

    # Overall comparison
    lines.append(f"## Strategy Comparison")
    lines.append(f"")
    for strat in STRATEGIES:
        strat_results = [r for r in ok if r["strategy"] == strat]
        if not strat_results:
            continue
        strat_label = "SMA Crossover" if strat == "sma" else "RSI Mean Reversion"
        avg_ret = sum(r["total_return_pct"] for r in strat_results) / len(strat_results)
        avg_dd = sum(r["max_drawdown_pct"] for r in strat_results) / len(strat_results)
        sharpes = [r["sharpe_ratio"] for r in strat_results if r.get("sharpe_ratio") is not None]
        avg_sharpe = sum(sharpes) / len(sharpes) if sharpes else None
        sharpe_str = f"{avg_sharpe:.2f}" if avg_sharpe is not None else "N/A"
        lines.append(f"- **{strat_label}:** Avg Return {avg_ret:+.2f}%, Avg DD {avg_dd:.2f}%, Avg Sharpe {sharpe_str}")

    # Errors section
    if errors:
        lines.append(f"")
        lines.append(f"## Errors")
        lines.append(f"")
        for e in errors:
            lines.append(f"- {e['ticker']}/{e['strategy']}: {e['error']}")

    lines.append(f"")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run backtests across all tickers and strategies")
    parser.add_argument("--period", default=DEFAULT_PERIOD, help="Data period (default: 2y)")
    parser.add_argument("--cash", type=float, default=DEFAULT_CASH, help="Starting cash (default: 100000)")
    parser.add_argument("--tickers", nargs="+", default=None, help="Override watchlist (default: all 10)")
    args = parser.parse_args()

    tickers = args.tickers if args.tickers else WATCHLIST

    print(f"Batch Backtest Runner")
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Strategies: {', '.join(s.upper() for s in STRATEGIES)}")
    print(f"Period: {args.period}  |  Cash: ${args.cash:,.0f}")
    print(f"Total runs: {len(tickers) * len(STRATEGIES)}")
    print("=" * 50)

    results = run_all(tickers, args.period, args.cash)

    # Generate and save report
    report = generate_report(results, args.period, args.cash)
    RESULTS_PATH.mkdir(parents=True, exist_ok=True)
    report_path = RESULTS_PATH / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(report)

    print("\n" + "=" * 50)
    print(f"Report saved to: {report_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
