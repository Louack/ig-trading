"""
Run Golden/Death Cross backtest on NDX 1D data using the shared backtesting engine.
"""

from pathlib import Path
import sys
import pandas as pd

# Ensure project root on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtesting.engine import run_golden_death_cross_backtest  # noqa: E402


def main() -> None:
    data_path = PROJECT_ROOT / "data_collection" / "data" / "1D" / "NDX_YFinance.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    df = pd.read_csv(data_path)
    if df["timestamp"].dtype == object:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    config = {
        "name": "golden_death_cross_ndx_backtest",
        "timeframe": "1D",
        "short_ma_period": 20,
        "long_ma_period": 50,
        "confirmation_periods": 2,
        "volume_filter": False,
        "volume_sma_period": 20,
        "rsi_filter": False,
        "rsi_period": 14,
        "rsi_oversold": 30,
        "rsi_overbought": 70,
    }

    result = run_golden_death_cross_backtest(
        df,
        config,
        starting_cash=100_000,
        stake=1.0,
        commission=0.0,
    )

    print("=== Backtest Result ===")
    print(f"Starting cash: {result.starting_cash:,.2f}")
    print(f"Ending cash:   {result.ending_cash:,.2f}")
    print(f"Return %:      {result.return_pct * 100:.2f}%")

    signals_df = result.signals
    print("=== Signals ===")
    if signals_df.empty:
        print("No signals generated.")
    else:
        buys = (signals_df["signal_type"] == "BUY").sum()
        sells = (signals_df["signal_type"] == "SELL").sum()
        print(f"Total: {len(signals_df)}, BUY: {buys}, SELL: {sells}")
        print(f"First signal: {signals_df['timestamp'].min()}")
        print(f"Last signal:  {signals_df['timestamp'].max()}")
        print("Last 5 signals:")
        print(signals_df.tail())


if __name__ == "__main__":
    main()
