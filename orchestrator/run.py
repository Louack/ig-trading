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
from data_collection.config_validation import validate_config  # noqa: E402
from config import load_config_with_secrets  # noqa: E402
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
    config, secrets = load_config_with_secrets()
    setup_logging(
        level=config.logging.level,
        fmt=config.logging.format,
        dest=config.logging.dest,
        filename=config.logging.file,
    )
    logger = logging.getLogger(__name__)

    # --- Configuration ---
    as_of_raw = config.orchestrator.as_of
    as_of = pd.Timestamp(as_of_raw) if as_of_raw else None
    timeframe = config.orchestrator.timeframe
    symbol = config.orchestrator.symbol
    data_path = Path(config.orchestrator.data_path)
    instrument_type = config.orchestrator.instrument_type
    source = config.orchestrator.source

    strategy_cfgs = []
    for scfg in config.strategies:
        # Dynamic import of strategy class
        module_name, class_name = scfg.class_name.rsplit(".", 1)
        module = __import__(module_name, fromlist=[class_name])
        strategy_class = getattr(module, class_name)

        strategy_cfgs.append(
            {
                "name": scfg.name,
                "class": strategy_class,
                "params": scfg.params,
                "window": scfg.window,
                "latest_only": scfg.latest_only,
            }
        )

    dispatch_cfg = DispatchConfig(
        min_strength=config.dispatch.min_strength,
        allowed_instruments=config.dispatch.allowed_instruments,
        allowed_strategies=config.dispatch.allowed_strategies,
        dedupe=config.dispatch.dedupe,
    )
    transports = []
    for t in config.dispatch.transports:
        if t == "telegram":
            transports.append(TelegramTransport())
        elif t == "console":
            transports.append(ConsoleTransport())

    # --- Fetch latest data before loading ---
    collector_config = config.data_collection.to_dict()
    validated_cfg = validate_config(collector_config)
    collector = DataCollector(
        validated_cfg.data_sources,
        enable_health_monitoring=validated_cfg.enable_health_checks,
    )

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
