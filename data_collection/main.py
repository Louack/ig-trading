#!/usr/bin/env python3
"""
Main script for the data collection service
"""

import sys
import os
from common.logging import setup_logging  # noqa: E402
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_collection.data_collector import DataCollector
from data_collection.factory.data_source_factory import DataSourceFactory
from data_collection.config_validation import validate_config

logger = logging.getLogger(__name__)


def main():
    """Main function to demonstrate data collection"""
    setup_logging()

    config = {
        "data_sources": {
            "ig_demo": {
                "type": "ig",
                "name": "IG Demo Account",
                "account_type": "demo",
                "timeout": 30,
                "max_retries": 3,
                "circuit_breaker_threshold": 5,
                "circuit_breaker_timeout": 60,
                "rate_limit_calls": 40,
                "rate_limit_period": 60,
            },
            # 'massive_backup': {
            #     'type': 'massive',
            #     'name': 'Massive',
            #     'api_key': MASSIVE_API_KEY,  # from settings
            #     'tier': 'free',
            #     'timeout': 30,
            #     'max_retries': 3,
            #     'circuit_breaker_threshold': 10,
            #     'circuit_breaker_timeout': 60
            # }
        },
        "storage": {
            "base_dir": "data",
            "format": "csv",
            "enable_checksums": True,
            "atomic_writes": True,
        },
        "enable_health_checks": True,
        "health_check_interval": 300,
    }

    try:
        # Validate configuration
        logger.info("Validating configuration...")
        validated_config = validate_config(config)
        logger.info("Configuration validated successfully")

        # Initialize data collector
        logger.info("Initializing data collector...")
        collector = DataCollector(
            validated_config.data_sources,
            enable_health_monitoring=validated_config.enable_health_checks,
        )

        # Check available sources
        available_sources = collector.get_available_sources()
        logger.info(f"Available data sources: {available_sources}")

        if not available_sources:
            logger.error("No data sources available!")
            return

        # Perform health check
        logger.info("Performing health check on data sources...")
        health_status = collector.check_health()
        logger.info(f"Health check results: {health_status}")

        # Get detailed health status
        detailed_health = collector.get_health_status()
        for source_name, status in detailed_health.items():
            logger.info(f"Health status for {source_name}: {status}")

        # Check for unhealthy sources
        unhealthy = collector.get_unhealthy_sources()
        if unhealthy:
            logger.warning(f"Unhealthy data sources: {unhealthy}")

        # Get source information
        for source_name in available_sources:
            source_info = collector.get_source_info(source_name)
            logger.info(f"Source {source_name}: {source_info}")

        # Collect data for a specific symbol
        symbol = "IX.D.FTSE.IFM.IP"  # FTSE 100
        timeframe = "1D"  # Daily

        logger.info(f"Collecting data for {symbol} ({timeframe})...")

        # Collect and store data
        success = collector.collect_and_store(symbol, timeframe)

        if success:
            logger.info("Data collection and storage successful!")

            # Load the stored data to verify
            stored_data = collector.load_data(symbol, timeframe)
            if stored_data is not None:
                logger.info(f"Loaded {len(stored_data)} data points from storage")
                logger.info(
                    f"Date range: {stored_data['timestamp'].min()} to {stored_data['timestamp'].max()}"
                )
                logger.info(
                    f"Price range: {stored_data['closePrice'].min():.1f} to {stored_data['closePrice'].max():.1f}"
                )
                logger.info(
                    f"Data source: {stored_data['source'].iloc[0] if 'source' in stored_data.columns else 'unknown'}"
                )
                logger.info(f"Sample data columns: {list(stored_data.columns)}")

                # Demonstrate source information retrieval
                source = collector.get_source_for_symbol(symbol, timeframe)
                logger.info(f"Source for {symbol} ({timeframe}): {source}")
            else:
                logger.warning("Could not load stored data")
        else:
            logger.error("Data collection and storage failed!")

        # Get storage information
        storage_info = collector.get_storage_info()
        logger.info(f"Storage info: {storage_info}")

        # Collect data for all instruments (commented out for demo)
        # logger.info("Collecting data for all instruments...")
        # results = collector.collect_and_store_all()
        # logger.info(f"Collection results: {results}")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

    finally:
        # Clean up connections
        logger.info("Disconnecting from data sources...")
        collector.disconnect_all()
        logger.info("Done!")


if __name__ == "__main__":
    main()
