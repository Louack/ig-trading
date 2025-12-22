"""
Trading Orchestrator

Orchestrates the complete trading pipeline:
1. Data collection from configured sources
2. Strategy execution on collected data
3. Signal generation and alerting
"""

import logging
import importlib
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

from config import (
    load_config,
    TradingConfig,
    get_available_strategies,
)
from data_collection.data_collector import DataCollector
from data_collection.factory.data_source_factory import DataSourceFactory
from settings import secrets
from signal_dispatch.transports import TelegramTransport, ConsoleTransport
from common.logging import setup_logging

logger = logging.getLogger(__name__)


class TradingOrchestrator:
    """Orchestrates data collection, strategy execution, and signal alerting."""

    def __init__(self, config: TradingConfig):
        """
        Initialize the orchestrator with configuration.

        Args:
            config: Validated trading configuration
        """
        self.config = config
        self.data_collector = None
        self.telegram_transport = TelegramTransport()
        self.console_transport = ConsoleTransport()

        logger.info("Initialized TradingOrchestrator")

    def _initialize_data_collector(self) -> bool:
        """Initialize data collector with data sources instantiated upstream."""
        try:
            # Collect unique data source names from all instruments
            source_names = {
                ds_name
                for instrument in self.config.instruments
                for ds_name in instrument.data_sources
            }

            # Validate that all source names match factory names
            available_factory_sources = DataSourceFactory.get_available_sources()
            invalid_sources = [
                name for name in source_names if name not in available_factory_sources
            ]

            if invalid_sources:
                logger.error(
                    f"Invalid data source names in config: {invalid_sources}. "
                    f"Available sources: {available_factory_sources}"
                )
                return False

            # Instantiate data sources using factory (names must match exactly)
            data_sources = DataSourceFactory.create_multi_source(list(source_names))

            if not data_sources:
                logger.error("No data sources could be instantiated")
                return False

            # Create data collector with instantiated sources
            self.data_collector = DataCollector(
                data_sources=data_sources,
                enable_health_monitoring=True,
            )

            logger.info("Data collector initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize data collector: {e}")
            return False

    def _collect_data_for_instrument_timeframe(
        self,
        instrument: str,
        timeframe: str,
        factory_source_name: str,
    ) -> Optional[pd.DataFrame]:
        """
        Collect data for a specific instrument and timeframe.

        Args:
            instrument: Instrument symbol
            timeframe: Timeframe string
            factory_source_name: Data source name (must match factory name)

        Returns:
            DataFrame with collected data or None if failed
        """
        try:
            logger.info(
                f"Collecting data for {instrument} on {timeframe} from {factory_source_name}"
            )

            # Validate source exists
            if factory_source_name not in self.data_collector.data_sources:
                logger.error(
                    f"Data source {factory_source_name} not available in data collector"
                )
                return None

            # Get the DataSource to determine MarketData source name
            data_source = self.data_collector.data_sources[factory_source_name]
            # MarketData uses hardcoded source strings, map factory key to MarketData source
            market_data_source_map = {
                "ig_demo": "IG",
                "ig_prod": "IG",
                "massive": "Massive",
                "yfinance": "YFinance",
            }
            market_data_source = market_data_source_map.get(
                factory_source_name, data_source.name
            )

            # Collect and store data
            success = self.data_collector.collect_and_store(
                symbol=instrument, timeframe=timeframe, source_name=factory_source_name
            )

            if success:
                # Load the collected data - use MarketData source name for loading
                data = self.data_collector.storage.load_latest_data(
                    symbol=instrument, timeframe=timeframe, source=market_data_source
                )

                if data is not None and not data.empty:
                    logger.info(
                        f"Successfully collected {len(data)} records for {instrument}"
                    )
                    return data
                else:
                    logger.warning(f"No data collected for {instrument}")
                    return None
            else:
                logger.error(f"Failed to collect data for {instrument}")
                return None

        except Exception as e:
            logger.error(f"Error collecting data for {instrument}: {e}")
            return None

    def _load_strategy_class(self, class_name: str):
        """Dynamically load strategy class from module path."""
        try:
            module_path, class_name_only = class_name.rsplit(".", 1)
            module = importlib.import_module(module_path)
            strategy_class = getattr(module, class_name_only)
            return strategy_class
        except Exception as e:
            logger.error(f"Failed to load strategy class {class_name}: {e}")
            return None

    def _run_strategy(
        self,
        strategy_name: str,
        strategy_class_path: str,
        data: pd.DataFrame,
        instrument: str,
        timeframe: str,
        strategy_params: Dict[str, Any],
    ) -> List[Any]:
        """
        Run a strategy on collected data.

        Args:
            strategy_name: Logical strategy name from config
            strategy_class_path: Fully qualified class path
            data: Market data DataFrame
            instrument: Instrument symbol
            timeframe: Timeframe string
            strategy_params: Strategy parameters

        Returns:
            List of signals generated
        """
        try:
            # Load strategy class
            strategy_class = self._load_strategy_class(strategy_class_path)
            if not strategy_class:
                return []

            # Build strategy configuration from parameters + context
            base_config: Dict[str, Any] = {}
            base_config.update(strategy_params or {})
            base_config.update(
                {
                    "name": strategy_name,
                    "timeframe": timeframe,
                    "instrument": instrument,
                }
            )

            # Initialize strategy
            strategy = strategy_class(base_config)

            # Generate signals
            signals = strategy.generate_signals(data)

            logger.info(
                f"Strategy {strategy_name} generated {len(signals)} signals for {instrument}"
            )

            return signals

        except Exception as e:
            logger.error(f"Error running strategy {strategy_name}: {e}")
            return []

    def _send_alert(self, signal: Any, instrument: str, strategy_name: str):
        """Send alert for generated signal."""
        try:
            # Create alert payload
            alert_payload = {
                "timestamp": datetime.now().isoformat(),
                "instrument": instrument,
                "strategy": strategy_name,
                "signal_type": (
                    signal.signal_type.value
                    if hasattr(signal, "signal_type")
                    else str(signal)
                ),
                "strength": (
                    signal.strength.value if hasattr(signal, "strength") else "UNKNOWN"
                ),
                "price": getattr(signal, "price", None),
                "message": f"Signal: {strategy_name} on {instrument} - {signal.signal_type.value if hasattr(signal, 'signal_type') else 'UNKNOWN'}",
            }

            # Send via Telegram
            self.telegram_transport.send(alert_payload)

            # Also log to console
            self.console_transport.send(alert_payload)

            logger.info(f"Alert sent for {strategy_name} signal on {instrument}")

        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

    def run_orchestration(self) -> Dict[str, Any]:
        """
        Run the complete orchestration pipeline.

        Returns:
            Summary of orchestration results
        """
        logger.info("Starting trading orchestration pipeline")

        results = {
            "data_collection_success": 0,
            "data_collection_failed": 0,
            "strategy_executions": 0,
            "signals_generated": 0,
            "alerts_sent": 0,
            "errors": [],
        }

        # Initialize data collector
        if not self._initialize_data_collector():
            results["errors"].append("Failed to initialize data collector")
            return results

        # Registry of available strategies mapped by str_name
        available_strategies = get_available_strategies()

        # Process each instrument
        for instrument in self.config.instruments:
            if not instrument.enabled:
                logger.info(f"Skipping disabled instrument: {instrument.symbol}")
                continue

            logger.info(
                f"Processing instrument: {instrument.symbol} ({instrument.name})"
            )

            # Process each strategy configured for this instrument
            for strategy_cfg in instrument.strategies:
                if not strategy_cfg.enabled:
                    continue

                strategy_name = strategy_cfg.name
                strategy_class_path = available_strategies.get(strategy_name)
                if not strategy_class_path:
                    logger.warning(f"Strategy {strategy_name} not found in registry")
                    continue

                # Process each timeframe
                for timeframe in strategy_cfg.timeframes:
                    # Determine data source (use first available)
                    factory_source_name = (
                        instrument.data_sources[0] if instrument.data_sources else None
                    )
                    if not factory_source_name:
                        logger.warning(
                            f"No data source configured for {instrument.symbol}"
                        )
                        continue

                    # Validate source exists in data collector
                    if factory_source_name not in self.data_collector.data_sources:
                        logger.error(
                            f"Data source {factory_source_name} not available for {instrument.symbol}"
                        )
                        results["data_collection_failed"] += 1
                        continue

                    # Collect data
                    data = self._collect_data_for_instrument_timeframe(
                        instrument.symbol, timeframe, factory_source_name
                    )

                    if data is None or data.empty:
                        results["data_collection_failed"] += 1
                        continue

                    results["data_collection_success"] += 1

                    # Run strategy
                    # Resolve parameters for this timeframe:
                    # parameters is Dict[timeframe, List[Dict[str, Any]]]
                    params_for_timeframe: Dict[str, Any] = {}
                    tf_param_list = strategy_cfg.parameters.get(timeframe, [])
                    if tf_param_list:
                        # Use the last definition for determinism
                        params_for_timeframe = tf_param_list[-1].copy()

                    signals = self._run_strategy(
                        strategy_name,
                        strategy_class_path,
                        data,
                        instrument.symbol,
                        timeframe,
                        params_for_timeframe,
                    )

                    results["strategy_executions"] += 1

                    # Filter to only signals from the latest bar (most recent timestamp)
                    if signals:
                        # Get the most recent timestamp from the data
                        latest_timestamp = data["timestamp"].max()

                        # Filter signals to only those from the latest bar
                        latest_signals = [
                            s for s in signals if s.timestamp == latest_timestamp
                        ]

                        logger.info(
                            f"Strategy {strategy_name} generated {len(signals)} total signals, "
                            f"{len(latest_signals)} from latest bar ({latest_timestamp.date()})"
                        )

                        # Process only latest signals
                        for signal in latest_signals:
                            results["signals_generated"] += 1

                            # Send alert
                            self._send_alert(signal, instrument.symbol, strategy_name)
                            results["alerts_sent"] += 1
                    else:
                        logger.info(f"Strategy {strategy_name} generated 0 signals")

        logger.info(f"Orchestration completed: {results}")
        return results


def main():
    """Main entry point for the trading orchestrator."""
    # Setup logging
    setup_logging(
        level=secrets.log_level,
        fmt=secrets.log_format,
        dest=secrets.log_dest,
        filename=secrets.log_file,
    )

    try:
        # Load configuration
        logger.info("Loading trading configuration...")
        config = load_config()

        # Initialize orchestrator
        orchestrator = TradingOrchestrator(config)

        # Run orchestration
        results = orchestrator.run_orchestration()

        # Log summary
        logger.info("=== Orchestration Summary ===")
        logger.info(
            f"Data collection: {results['data_collection_success']} success, {results['data_collection_failed']} failed"
        )
        logger.info(f"Strategy executions: {results['strategy_executions']}")
        logger.info(f"Signals generated: {results['signals_generated']}")
        logger.info(f"Alerts sent: {results['alerts_sent']}")

        if results["errors"]:
            logger.error(f"Errors encountered: {results['errors']}")

    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        raise


if __name__ == "__main__":
    main()
