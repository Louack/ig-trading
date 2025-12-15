import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

from ..base.strategy import BaseStrategy
from ..base.signal import Signal, SignalType, SignalStrength


class DummyStrategy2(BaseStrategy):
    """Dummy strategy for testing purposes"""

    # String name for TOML config mapping
    str_name: str = "dummy_strategy_2"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Strategy parameters
        self.send_signal = config.get("send_signal", False)

    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """Generate signals based on send_signal parameter"""
        if not self.validate_data(data):
            return []

        signals = []

        if self.send_signal:
            # Get the latest data point
            latest = data.iloc[-1]
            timestamp = latest["timestamp"]
            if isinstance(timestamp, pd.Timestamp):
                timestamp = timestamp.to_pydatetime()
            elif isinstance(timestamp, str):
                timestamp = pd.to_datetime(timestamp).to_pydatetime()

            # Get instrument identifier
            instrument = latest.get("symbol") or latest.get("epic", "UNKNOWN")
            price = float(latest["closePrice"])

            # Create a dummy signal
            signal = Signal(
                instrument=str(instrument),
                signal_type=SignalType.BUY,
                strength=SignalStrength.MEDIUM,
                timestamp=timestamp,
                price=price,
                confidence=0.5,
                metadata={"strategy": self.str_name, "dummy": True},
            )
            signals.append(signal)

        return signals

    def should_enter_position(self, signal: Signal) -> bool:
        """Determine if a signal should trigger a position entry"""
        return self.send_signal and signal.signal_type in [
            SignalType.BUY,
            SignalType.SELL,
        ]

    def should_exit_position(
        self, signal: Signal, current_position: Dict[str, Any]
    ) -> bool:
        """Determine if a signal should trigger a position exit"""
        return False
