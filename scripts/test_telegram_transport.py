"""
Live-like signal check on NDX 1D as of 2025-05-13 and Telegram dispatch.
"""

from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from strategies.implementations.golden_death_cross import GoldenDeathCrossStrategy  # noqa: E402
from signal_dispatch.transports import TelegramTransport  # noqa: E402


AS_OF = pd.Timestamp("2025-05-13")
SHORT_MA = 20
LONG_MA = 50
CONFIRMATION_PERIODS = 2


def main() -> None:
    data_path = PROJECT_ROOT / "data_collection" / "data" / "1D" / "NDX_YFinance.csv"
    df = pd.read_csv(data_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    # Add instrument_type for IG CFDs
    df["instrument_type"] = "CFD"

    # Limit data to as-of date
    df = df[df["timestamp"] <= AS_OF].copy()
    if df.empty:
        print("No data up to AS_OF date")
        return

    # Live-style window: warm-up + small cushion
    window = max(SHORT_MA, LONG_MA, CONFIRMATION_PERIODS) + 5
    recent = df.tail(window).copy()

    config = {
        "name": "golden_death_cross_live_check",
        "timeframe": "1D",
        "short_ma_period": SHORT_MA,
        "long_ma_period": LONG_MA,
        "confirmation_periods": CONFIRMATION_PERIODS,
        "volume_filter": False,
        "volume_sma_period": 20,
        "rsi_filter": False,
        "rsi_period": 14,
        "rsi_oversold": 30,
        "rsi_overbought": 70,
    }

    strat = GoldenDeathCrossStrategy(config)
    signals = strat.generate_signals(recent)

    if not signals:
        print("No signals generated in recent window.")
        return

    # Only send signals for the latest bar
    last_ts = recent["timestamp"].iloc[-1]
    latest_signals = [s for s in signals if s.timestamp == last_ts]

    if not latest_signals:
        print("Signals exist, but none on the latest bar.")
        return

    transport = TelegramTransport()
    for sig in latest_signals:
        payload = sig.to_dict()
        transport.send(payload)
        print("Dispatched signal:", payload)


if __name__ == "__main__":
    main()
