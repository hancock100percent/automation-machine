# Python Backtesting Framework Comparison

Research date: 2026-02-07
Decision: **backtrader** (already implemented)

## Frameworks Evaluated

### 1. backtrader

- **GitHub:** mementum/backtrader (~14k stars)
- **Status:** Mature but maintenance-mode (last commit ~2023). API stable.
- **Architecture:** Event-driven. Cerebro engine runs strategies bar-by-bar.
- **Strengths:**
  - Full-featured: built-in indicators (200+), analyzers, observers, live trading support
  - Pandas-compatible data feeds
  - Extensible strategy classes with `params` tuples for parameter sweeps
  - Built-in commission models, slippage, position sizing
  - Good documentation and large community (StackOverflow, forums)
- **Weaknesses:**
  - No longer actively maintained
  - Slow for large datasets (pure Python event loop)
  - Verbose API -- simple strategies still need boilerplate (notify_order, etc.)
  - Plotting depends on matplotlib internals that break in newer versions
- **Best for:** Learning, medium-complexity strategies, prototyping

### 2. vectorbt

- **GitHub:** polanikov/vectorbt (~4k stars)
- **Status:** Active development (vectorbt PRO is commercial)
- **Architecture:** Vectorized. Uses NumPy/Pandas for fast columnar operations.
- **Strengths:**
  - 100-1000x faster than event-driven frameworks
  - Excellent for parameter optimization (sweep thousands of combos)
  - Built-in portfolio simulation, Sharpe/Sortino/Calmar ratios
  - Plotly-based interactive charts
  - Good integration with pandas_ta for indicators
- **Weaknesses:**
  - Steeper learning curve (think in arrays, not events)
  - Harder to model complex order logic (stop-losses, bracket orders)
  - Free version limited vs PRO; some features paywalled
  - Less intuitive for beginners
- **Best for:** Quantitative research, parameter sweeps, high-frequency analysis

### 3. zipline / zipline-reloaded

- **GitHub:** stefan-jansen/zipline-reloaded (~1.2k stars)
- **Status:** Community fork of Quantopian's zipline. Active but fragile installs.
- **Architecture:** Event-driven (similar to backtrader).
- **Strengths:**
  - Battle-tested at Quantopian (used by thousands of quants)
  - Pyfolio integration for professional tearsheets
  - Calendar-aware (handles market holidays)
  - Pipeline API for factor-based strategies
- **Weaknesses:**
  - Installation is painful (C dependencies, version conflicts)
  - Ingestion system is complex (bundles, not simple CSV/API)
  - Heavier dependency footprint
  - Community smaller than backtrader
- **Best for:** Factor-based strategies, institutional-style research

### 4. bt (by pmorissette)

- **GitHub:** pmorissette/bt (~2.1k stars)
- **Status:** Active, lightweight.
- **Architecture:** Tree-based. Strategies are composable trees of algos.
- **Strengths:**
  - Elegant API for portfolio allocation strategies
  - Built for asset allocation / rebalancing
  - Good integration with ffn (financial functions)
- **Weaknesses:**
  - Not designed for individual stock trading signals
  - Limited indicator library
  - Smaller community
- **Best for:** Portfolio rebalancing, asset allocation

### 5. lean (QuantConnect)

- **GitHub:** QuantConnect/Lean (~10k stars)
- **Status:** Very active (commercial platform behind it).
- **Architecture:** Event-driven, C# core with Python API.
- **Strengths:**
  - Production-grade (runs on QuantConnect cloud)
  - Multi-asset (stocks, options, futures, crypto, forex)
  - Tick-level data support
  - Live trading with multiple brokers
- **Weaknesses:**
  - C# core means Python is a wrapper (slower, less Pythonic)
  - Heavy installation (Docker recommended)
  - Designed for their cloud platform; local setup is complex
- **Best for:** Serious algo traders heading toward live deployment

## Decision Matrix

| Criterion         | backtrader | vectorbt | zipline | bt  | lean |
|-------------------|-----------|----------|---------|-----|------|
| Ease of setup     | A         | B+       | D       | A   | C    |
| Learning curve    | B+        | C+       | B       | B+  | C    |
| Speed             | C         | A+       | C       | B   | B    |
| Indicator library | A         | A        | B       | C   | A    |
| Community/docs    | A         | B        | B       | C   | B+   |
| Live trading      | B         | C        | D       | D   | A+   |
| Maintenance       | D (stale) | B        | C       | B   | A+   |
| Cost              | Free      | Freemium | Free    | Free| Free |

## Why backtrader (for now)

1. **Already implemented** -- Two working strategies, data pipeline, CLI runner
2. **Good enough** for learning and prototyping phase
3. **Event-driven model** is easier to reason about for strategy logic
4. **Risk:** Maintenance has stalled. If we hit API-breaking issues with newer Python, consider migrating to vectorbt for research or lean for production.

## Migration path

```
Phase 1 (now):  backtrader -- learn, prototype, iterate
Phase 2 (later): vectorbt  -- parameter optimization, faster iteration
Phase 3 (if needed): lean  -- live paper trading, multi-asset
```

## Key Insight: Position Sizing Problem

The existing backtests return only +0.12% and +0.06% because they trade **1 share at a time** with $100k capital. backtrader defaults to `size=1` when no sizer is configured. This makes the strategies appear to barely break even when in reality the signals may be valid -- just massively under-allocated.

**Fix:** Add a percentage-based sizer (e.g., `cerebro.addsizer(bt.sizers.PercentSizer, percents=95)`) to allocate most of the portfolio per trade. This is the single most impactful improvement to make next.
