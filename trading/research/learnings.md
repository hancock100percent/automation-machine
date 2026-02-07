# Trading Research Learnings

**Date:** 2026-02-07
**Status:** Phase 1 complete (backtrader prototyping)

## What Worked

### 1. RSI Mean Reversion outperformed on risk-adjusted basis
- Avg return +34.46%, Sharpe 0.76, **zero losers** across 10 tickers
- The strategy benefits from buying temporary dips in fundamentally strong large-cap stocks
- Works best on stocks with high volatility but strong upward drift (META +73%, TSLA +68%)

### 2. SMA Crossover captured large trend moves
- Best single result: GOOGL +109.82% (only 3 trades -- let winners run)
- When it catches a multi-month trend, returns are outsized
- Low trade count on winners = low commission drag

### 3. yfinance + SQLite caching = zero-cost, fast iteration
- First download takes ~2s per ticker; subsequent runs use cache instantly
- SQLite is lightweight, portable, no server needed
- Cache-by-date means re-running same-day backtests is instant

### 4. Position sizing was the single biggest fix
- Before: 1 share per trade with $100k capital = meaningless returns (+0.06%)
- After: 95% allocation per trade = returns reflect actual signal quality
- Lesson: **Always validate that your sizing matches your intent.** Default backtrader sizing makes strategies look broken.

### 5. backtrader is adequate for prototyping
- Event-driven model is intuitive: `next()` method, check position, buy/sell
- Built-in analyzers (Sharpe, DrawDown, TradeAnalyzer) save boilerplate
- Parameterized strategies via `params` tuple enable easy sweeps later

## What Didn't Work / Limitations Found

### 1. SMA Crossover has tail risk
- AMD lost 12.67% (max DD 38.89%), AMZN lost 13.72%
- Whipsaw-prone in sideways markets: frequent buy/sell signals that erode capital
- 9-12 trades on losers vs 3 trades on GOOGL -- overtrading is the enemy

### 2. No stop-loss protection
- Both strategies are "always in or always out" with no risk management
- AMD's 53.16% max drawdown (RSI) and 38.89% (SMA) would be unacceptable for real capital
- Next iteration must add trailing stops or fixed stop-losses

### 3. Commission sensitivity not tested
- Current 0.1% commission is realistic for a discount broker
- But with 95% position sizing, commission on each round trip = ~0.2% of portfolio
- High-frequency strategies would be crushed; current trade counts (2-12) are fine

### 4. Look-ahead bias risk in RSI
- RSI uses close price which is only known at end of bar
- For daily bars this is acceptable (you'd place the order next day)
- But the backtest executes at the signal bar's close, not next open -- slight optimistic bias

### 5. No benchmark comparison
- Returns look good in isolation (+32-34%) but the 2-year period included a strong bull market
- SPY itself returned +20.91% via SMA and +9.86% via RSI (both below the "just hold SPY" benchmark of ~25% over 2 years)
- Need to add a buy-and-hold benchmark to every backtest

### 6. Single-ticker strategies only
- Current architecture trades one ticker at a time with 95% allocation
- No portfolio diversification, correlation analysis, or multi-asset logic
- Real deployment would need to divide capital across positions

## Key Metrics Summary

| Metric | SMA Crossover | RSI Mean Reversion |
|--------|--------------|-------------------|
| Avg Return | +32.57% | +34.46% |
| Avg Max DD | 21.49% | 22.05% |
| Avg Sharpe | 0.61 | 0.76 |
| Win Rate | 80% (8/10) | 100% (10/10) |
| Best | GOOGL +109.82% | META +73.15% |
| Worst | AMZN -13.72% | AMD +3.15% |
| Avg Trades | 8.7 | 4.2 |

## Architecture Assessment

### Current Stack
```
yfinance --> SQLite cache --> backtrader --> JSON results --> MD reports
```

**Strengths:** Simple, zero-cost, self-contained, resume-friendly
**Weaknesses:** No parameter optimization, no visualization, no multi-asset

### What to Build Next (Priority Order)

1. **Stop-loss / trailing stop** -- Critical risk management. Add `StopTrail` order to both strategies. Without this, max drawdowns are dangerous.

2. **Buy-and-hold benchmark** -- Add SPY buy-and-hold as a comparison line in every report. If the strategy doesn't beat holding SPY, it's not worth the complexity.

3. **Parameter sweep** -- Use backtrader's `optstrategy` or migrate to vectorbt for fast grid search. Test SMA periods (10/30, 20/50, 30/100) and RSI thresholds (20/80, 25/75, 30/70).

4. **Multi-asset portfolio** -- Divide $100k across top 3-5 tickers by Sharpe ratio. Need correlation matrix to avoid concentrated bets.

5. **Out-of-sample testing** -- Current 2-year backtest is in-sample. Split data: train on first 1.5y, validate on last 0.5y. Or walk-forward analysis.

6. **Visualization** -- Equity curve plots, drawdown charts. Consider plotly for interactive charts that can embed in the Streamlit dashboard.

## Framework Migration Decision

**Stay on backtrader for now.** The current codebase is clean and working. Migrate to vectorbt only when:
- Parameter sweeps require >100 combinations (backtrader `optstrategy` becomes too slow)
- We need portfolio-level backtesting with rebalancing
- We want interactive Plotly visualization (vectorbt has this built in)

Estimated migration effort: ~4 hours (rewrite strategies as vectorized signals).

## Lessons for Automation Machine

1. **Pre-existing code is an asset** -- Iterations 1-5 were fast-tracked because prior work existed. The resume system (state.json) made this seamless.

2. **Batch runners save time** -- `run_all_backtests.py` runs 20 tests in minutes. Always build batch tooling early.

3. **Default configs lie** -- backtrader's default 1-share sizing made strategies look worthless. Always inspect framework defaults before trusting results.

4. **Consistency > peak performance** -- RSI's 100% win rate is more valuable than SMA's occasional 110% moonshot. For a Fiverr consultancy demo, reliable wins build trust.
