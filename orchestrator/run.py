"""
Orchestrator for running strategies and dispatching signals.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

# Ensure project root on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common.logging import setup_logging  # noqa: E402
from signal_dispatch.router import dispatch_signals, DispatchConfig  # noqa: E402
from signal_dispatch.transports import TelegramTransport, ConsoleTransport  # noqa: E402
from strategies.implementations.golden_death_cross import GoldenDeathCrossStrategy  # noqa: E402
from data_collection.data_collector import DataCollector  # noqa: E402
from data_collection.factory.data_source_factory import DataSourceFactory  # noqa: E402
from data_collection.config_validation import validate_config  # noqa: E402
import logging


def load_data(
    path: Path, as_of: pd.Timestamp | None, instrument_type: str, source: str
) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["instrument_type"] = instrument_type
    df["source"] = source
    if as_of is not None:
        df = df[df["timestamp"] <= as_of].copy()
    return df


def run_strategies(df: pd.DataFrame, strategy_cfgs: List[Dict[str, Any]]):
    signals = []
    for cfg in strategy_cfgs:
        strat = cfg["class"](cfg["params"])
        window = cfg.get("window")
        data_slice = df.tail(window) if window else df
        sigs = strat.generate_signals(data_slice)
        if cfg.get("latest_only"):
            if sigs:
                last_ts = data_slice["timestamp"].iloc[-1]
                sigs = [s for s in sigs if s.timestamp == last_ts]
        signals.extend(sigs)
    return signals


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    # --- Configuration ---
    as_of = None  # e.g., pd.Timestamp("2025-05-13") for replay; None = full range
    timeframe = "1D"
    symbol = "NDX"
    data_path = (
        PROJECT_ROOT / "data_collection" / "data" / timeframe / "NDX_YFinance.csv"
    )
    instrument_type = "INDEX"
    source = "YFinance"

    strategy_cfgs = [
        {
            "name": "golden_death_cross_20_50",
            "class": GoldenDeathCrossStrategy,
            "params": {
                "name": "golden_death_cross_20_50",
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
            },
            # window: warm-up + cushion
            "window": max(50, 20, 2) + 5,
            "latest_only": True,
        }
    ]

    dispatch_cfg = DispatchConfig(
        min_strength=None,  # e.g., "MEDIUM"
        allowed_instruments=None,
        allowed_strategies=None,
        dedupe=True,
    )
    transports = [TelegramTransport(), ConsoleTransport()]

    # --- Fetch latest data before loading ---
    # Minimal data collector config for YFinance (extend as needed)
    collector_config = {
        "data_sources": {
            "yfinance": {"type": "yfinance", "name": "YFinance"},
        },
        "storage": {
            "base_dir": str(PROJECT_ROOT / "data_collection" / "data"),
            "format": "csv",
            "enable_checksums": True,
            "atomic_writes": True,
        },
        "enable_health_checks": False,
    }

    validated_cfg = validate_config(collector_config)
    collector = DataCollector(validated_cfg.data_sources)

    updated = collector.collect_and_store(symbol, timeframe)
    if not updated:
        logger.warning(
            "No new data collected; skipping signal generation to avoid stale signals."
        )
        return

    # --- Load data ---
    df = load_data(data_path, as_of, instrument_type, source)
    if df.empty:
        logger.warning("No data available after fetch; skipping.")
        return

    # --- Run strategies ---
    signals = run_strategies(df, strategy_cfgs)

    # --- Dispatch ---
    dispatch_signals(signals, transports=transports, config=dispatch_cfg)


if __name__ == "__main__":
    main()
