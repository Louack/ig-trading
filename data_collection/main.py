"""
Main script for data collection service
"""

import logging


from market_data_collector import MarketDataCollector
from data_storage import DataStorage

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting IG Trading Data Collection Service...")

    collector = MarketDataCollector()
    storage = DataStorage()

    logger.info("Testing data collection...")
    try:
        sample_data = collector.collect_data_for_category("forex", "hourly")
        if sample_data:
            logger.info(f"Successfully collected {len(sample_data)} forex instruments")
            storage.store_data({"forex": sample_data}, "hourly")
            logger.info("Data collection and storage successful")
        else:
            logger.warning("No data collected")

    except Exception as e:
        logger.error(f"Data collection failed: {e}")
        return


if __name__ == "__main__":
    main()
