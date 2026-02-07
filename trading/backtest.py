"""Main backtest runner -- can be run as a standalone script.

Usage:
    python trading/backtest.py [--ticker SPY] [--strategy sma|rsi] [--period 2y] [--cash 100000]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import backtrader as bt
import pandas as pd

# Allow running as standalone script or as module import
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trading.config import DEFAULT_CASH, DEFAULT_PERIOD, RESULTS_PATH
from trading.data import download_historical
from trading.strategies import RSI_MeanReversion, SMA_Crossover

STRATEGY_MAP = {
    "sma": SMA_Crossover,
    "rsi": RSI_MeanReversion,
}


def run_backtest(ticker: str, strategy_name: str, period: str, cash: float) -> dict:
    """Run a backtest and return the results as a dict."""
    strategy_cls = STRATEGY_MAP.get(strategy_name)
    if strategy_cls is None:
        raise ValueError(f"Unknown strategy: {strategy_name}. Choose from: {list(STRATEGY_MAP.keys())}")

    # Download data
    print(f"Downloading {ticker} data ({period})...")
    df = download_historical(ticker, period=period)

    if df.empty:
        raise RuntimeError(f"No data returned for {ticker}")

    # Prepare data for Backtrader
    df = df.set_index("date")
    df.index = pd.to_datetime(df.index)
    data_feed = bt.feeds.PandasData(dataname=df)

    # Set up Cerebro
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy_cls)
    cerebro.adddata(data_feed)
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=0.001)

    # Position sizing: allocate 95% of portfolio per trade
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe", timeframe=bt.TimeFrame.Days, annualize=True)

    # Run
    print(f"Running {strategy_name.upper()} strategy on {ticker}...")
    results = cerebro.run()
    strat = results[0]

    final_value = cerebro.broker.getvalue()
    total_return = ((final_value - cash) / cash) * 100

    # Extract drawdown
    dd_analysis = strat.analyzers.drawdown.get_analysis()
    max_drawdown = dd_analysis.get("max", {}).get("drawdown", 0.0)

    # Extract Sharpe ratio
    sharpe_analysis = strat.analyzers.sharpe.get_analysis()
    sharpe_ratio = sharpe_analysis.get("sharperatio", None)
    if sharpe_ratio is not None:
        sharpe_ratio = round(sharpe_ratio, 4)

    # Extract trade count from strategy tracking
    strategy_results = strat.get_results()
    trade_count = strategy_results["trade_count"]

    result = {
        "ticker": ticker,
        "strategy": strategy_name,
        "period": period,
        "starting_cash": cash,
        "final_value": round(final_value, 2),
        "total_return_pct": round(total_return, 2),
        "max_drawdown_pct": round(max_drawdown, 2),
        "sharpe_ratio": sharpe_ratio,
        "trade_count": trade_count,
        "trades": strategy_results["trades"],
        "params": strategy_results["params"],
        "run_date": datetime.now().isoformat(),
    }

    return result


def save_results(result: dict) -> Path:
    """Save backtest results to a JSON file."""
    RESULTS_PATH.mkdir(parents=True, exist_ok=True)
    filename = f"{result['ticker']}_{result['strategy']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = RESULTS_PATH / filename
    filepath.write_text(json.dumps(result, indent=2))
    return filepath


def print_results(result: dict):
    """Print a summary of the backtest results."""
    print("\n" + "=" * 50)
    print(f"  BACKTEST RESULTS: {result['ticker']} / {result['strategy'].upper()}")
    print("=" * 50)
    print(f"  Period:         {result['period']}")
    print(f"  Starting Cash:  ${result['starting_cash']:,.2f}")
    print(f"  Final Value:    ${result['final_value']:,.2f}")
    print(f"  Total Return:   {result['total_return_pct']:+.2f}%")
    print(f"  Max Drawdown:   {result['max_drawdown_pct']:.2f}%")
    sharpe = result.get('sharpe_ratio')
    print(f"  Sharpe Ratio:   {sharpe if sharpe is not None else 'N/A'}")
    print(f"  Trade Count:    {result['trade_count']}")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Run a trading backtest")
    parser.add_argument("--ticker", default="SPY", help="Ticker symbol (default: SPY)")
    parser.add_argument("--strategy", default="sma", choices=list(STRATEGY_MAP.keys()), help="Strategy to test (default: sma)")
    parser.add_argument("--period", default=DEFAULT_PERIOD, help="Data period (default: 2y)")
    parser.add_argument("--cash", type=float, default=DEFAULT_CASH, help="Starting cash (default: 100000)")
    args = parser.parse_args()

    result = run_backtest(args.ticker, args.strategy, args.period, args.cash)
    print_results(result)

    filepath = save_results(result)
    print(f"\n  Results saved to: {filepath}")


if __name__ == "__main__":
    main()
