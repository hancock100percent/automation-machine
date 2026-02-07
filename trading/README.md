# Trading Research & Backtesting

Algorithmic trading research and backtesting system. Research and paper trading only -- no live trading.

## Project Structure

```
trading/
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── __init__.py         # Package init
├── config.py           # Watchlist, defaults, paths
├── data.py             # Market data pipeline (yfinance + SQLite cache)
├── strategies.py       # Backtrader strategy implementations
├── backtest.py         # CLI backtest runner
├── data/
│   └── market_data.db  # SQLite cache for OHLCV data
├── results/            # Backtest result JSON files
└── research/           # Strategy research notes and analysis
```

## Quick Start

```bash
# Install dependencies
pip install -r trading/requirements.txt

# Run SMA crossover backtest on SPY (default)
python trading/backtest.py

# Run RSI mean reversion on AAPL
python trading/backtest.py --ticker AAPL --strategy rsi

# Custom parameters
python trading/backtest.py --ticker QQQ --strategy sma --period 5y --cash 50000
```

## Strategies

| Strategy | Entry Signal | Exit Signal | Params |
|----------|-------------|-------------|--------|
| SMA Crossover | SMA(20) crosses above SMA(50) | SMA(20) crosses below SMA(50) | fast_period, slow_period |
| RSI Mean Reversion | RSI(14) < 30 (oversold) | RSI(14) > 70 (overbought) | rsi_period, oversold, overbought |

## Watchlist

SPY, QQQ, AAPL, MSFT, NVDA, AMZN, GOOGL, META, TSLA, AMD

## Data Pipeline

- Source: Yahoo Finance via `yfinance`
- Cache: SQLite at `trading/data/market_data.db`
- Auto-skips download if today's data already cached
- Period: configurable (default 2y)

## Backtest Output

Results saved to `trading/results/` as JSON with:
- Total return %, max drawdown %, trade count
- Full trade log (date, action, price)
- Strategy parameters used

## Cost

$0 -- all data from free sources, all computation local.
