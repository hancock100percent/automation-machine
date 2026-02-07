"""Backtrader strategies for backtesting."""

import backtrader as bt


class SMA_Crossover(bt.Strategy):
    """Buy when SMA(20) crosses above SMA(50), sell when it crosses below."""

    params = (
        ("fast_period", 20),
        ("slow_period", 50),
    )

    def __init__(self):
        self.sma_fast = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.fast_period)
        self.sma_slow = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.slow_period)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

        # Tracking
        self.trade_log = []
        self.trade_count = 0
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.crossover > 0:
                self.order = self.buy()
                self._log_trade("BUY", self.data.close[0])
        else:
            if self.crossover < 0:
                self.order = self.sell()
                self._log_trade("SELL", self.data.close[0])

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.trade_count += 1
            self.order = None
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.order = None

    def _log_trade(self, action: str, price: float):
        self.trade_log.append({
            "date": self.data.datetime.date(0).isoformat(),
            "action": action,
            "price": round(price, 2),
            "size": self.position.size if self.position else 0,
        })

    def get_results(self) -> dict:
        return {
            "strategy": "SMA_Crossover",
            "params": {"fast_period": self.params.fast_period, "slow_period": self.params.slow_period},
            "trade_count": self.trade_count,
            "trades": self.trade_log,
        }


class RSI_MeanReversion(bt.Strategy):
    """Buy when RSI(14) < 30 (oversold), sell when RSI(14) > 70 (overbought)."""

    params = (
        ("rsi_period", 14),
        ("oversold", 30),
        ("overbought", 70),
    )

    def __init__(self):
        self.rsi = bt.indicators.RelativeStrengthIndex(self.data.close, period=self.params.rsi_period)

        # Tracking
        self.trade_log = []
        self.trade_count = 0
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.rsi < self.params.oversold:
                self.order = self.buy()
                self._log_trade("BUY", self.data.close[0])
        else:
            if self.rsi > self.params.overbought:
                self.order = self.sell()
                self._log_trade("SELL", self.data.close[0])

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.trade_count += 1
            self.order = None
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.order = None

    def _log_trade(self, action: str, price: float):
        self.trade_log.append({
            "date": self.data.datetime.date(0).isoformat(),
            "action": action,
            "price": round(price, 2),
            "size": self.position.size if self.position else 0,
        })

    def get_results(self) -> dict:
        return {
            "strategy": "RSI_MeanReversion",
            "params": {
                "rsi_period": self.params.rsi_period,
                "oversold": self.params.oversold,
                "overbought": self.params.overbought,
            },
            "trade_count": self.trade_count,
            "trades": self.trade_log,
        }
