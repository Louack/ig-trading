"""
Backtesting engine wiring project strategies into backtrader.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Type, Protocol
import pandas as pd
import backtrader as bt

from strategies.base.signal import Signal
from strategies.implementations.golden_death_cross import GoldenDeathCrossStrategy


class MarketDataFeed(bt.feeds.PandasData):
    """
    Pandas feed mapping project OHLCV schema to backtrader.
    """

    params = (
        ("datetime", "timestamp"),
        ("open", "openPrice"),
        ("high", "highPrice"),
        ("low", "lowPrice"),
        ("close", "closePrice"),
        ("volume", "lastTradedVolume"),
    )


@dataclass
class BacktestResult:
    signals: pd.DataFrame
    starting_cash: float
    ending_cash: float
    return_pct: float


class SignalExecutionStrategy(bt.Strategy):
    """
    Backtrader strategy that executes precomputed signals (BUY/SELL) at bar close.
    """

    params = dict(signals=None, stake=1.0)

    def __init__(self):
        # signals_df expected sorted by timestamp (datetime64[ns])
        self.signals_df: pd.DataFrame = self.p.signals
        self._signal_idx = 0

    def next(self):
        if self.signals_df is None or self.signals_df.empty:
            return

        dt = self.data.datetime.datetime(0)

        # Process all signals matching current bar datetime
        while (
            self._signal_idx < len(self.signals_df)
            and pd.Timestamp(self.signals_df.iloc[self._signal_idx]["timestamp"]) == dt
        ):
            signal = self.signals_df.iloc[self._signal_idx]
            sig_type = signal["signal_type"]

            if sig_type == "BUY":
                if self.position.size <= 0:
                    if self.position.size < 0:
                        self.close()  # flatten shorts
                    self.buy(size=self.p.stake)
            elif sig_type == "SELL":
                if self.position.size >= 0:
                    if self.position.size > 0:
                        self.close()  # flatten longs
                    self.sell(size=self.p.stake)

            self._signal_idx += 1


class SignalGenerator(Protocol):
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]: ...


def _compute_signals(
    strategy_cls: Type[SignalGenerator],
    data: pd.DataFrame,
    strategy_config: Dict[str, Any],
) -> pd.DataFrame:
    strat = strategy_cls(strategy_config)
    signals = strat.generate_signals(data)
    if not signals:
        return pd.DataFrame()
    return pd.DataFrame([s.to_dict() for s in signals]).sort_values("timestamp")


def run_golden_death_cross_backtest(
    data: pd.DataFrame,
    strategy_config: Optional[Dict[str, Any]] = None,
    starting_cash: float = 100_000.0,
    stake: float = 1.0,
    commission: float = 0.0,
    strategy_cls: Type[SignalGenerator] = GoldenDeathCrossStrategy,
) -> BacktestResult:
    """
    Run a simple backtest for Golden/Death Cross strategy.

    Args:
        data: OHLCV DataFrame with columns timestamp, openPrice, highPrice, lowPrice, closePrice, lastTradedVolume
        strategy_config: config for GoldenDeathCrossStrategy
        starting_cash: initial broker cash
        stake: order size per signal (units)
        commission: broker commission (fractional, e.g., 0.001 for 0.1%)
        strategy_cls: strategy class implementing generate_signals
    """
    strategy_config = strategy_config or {}
    signals_df = _compute_signals(strategy_cls, data, strategy_config)

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(starting_cash)
    if commission:
        cerebro.broker.setcommission(commission=commission)

    feed = MarketDataFeed(dataname=data)
    cerebro.adddata(feed)
    cerebro.addstrategy(SignalExecutionStrategy, signals=signals_df, stake=stake)

    cerebro.run()
    ending_cash = cerebro.broker.getvalue()
    return_pct = (ending_cash - starting_cash) / starting_cash if starting_cash else 0.0

    return BacktestResult(
        signals=signals_df,
        starting_cash=starting_cash,
        ending_cash=ending_cash,
        return_pct=return_pct,
    )
