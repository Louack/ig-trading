#!/usr/bin/env python3
"""
Main script for the data collection service
"""

import sys
import os
from datetime import datetime
from typing import List
import logging

from common.logging import setup_logging  # noqa: E402
from config import load_config  # noqa: E402
from settings import secrets  # noqa: E402

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_collection.data_collector import DataCollector
from data_collection.factory.data_source_factory import DataSourceFactory

logger = logging.getLogger(__name__)


def main():
    """Main function to demonstrate data collection"""
    config = load_config()
    setup_logging(
        level=secrets.log_level,
        fmt=secrets.log_format,
        dest=secrets.log_dest,
        filename=secrets.log_file,
    )

    # Collect unique data source names from all instruments
    source_names = {
        ds_name
        for instrument in config.instruments
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
        return

    try:
        # Instantiate data sources using factory (names must match exactly)
        logger.info("Instantiating data sources...")
        data_sources = DataSourceFactory.create_multi_source(list(source_names))
        logger.info(f"Instantiated {len(data_sources)} data sources")

        if not data_sources:
            logger.error("No data sources could be instantiated")
            return

        # Initialize data collector with instantiated sources
        logger.info("Initializing data collector...")
        collector = DataCollector(
            data_sources=data_sources,
            enable_health_monitoring=True,
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
        logger.error(f"Error in main: {e}", exc_info=True)
        raise

    finally:
        # Clean up connections
        logger.info("Disconnecting from data sources...")
        collector.disconnect_all()
        logger.info("Done!")


if __name__ == "__main__":
    main()
