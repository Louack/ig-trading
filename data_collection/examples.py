"""
Examples demonstrating the improved data collection module features
"""

import logging
from datetime import datetime
from data_collection.data_collector import DataCollector
from data_collection.config_validation import validate_config
from common.alerting import alerting_service, AlertSeverity
from data_collection.storage.data_storage import DataStorage
from settings import MASSIVE_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Example 1: Basic data collection"""

    config = {
        "data_sources": {
            "ig_demo": {"type": "ig", "name": "IG Demo Account", "account_type": "prod"}
        },
        "storage": {"base_dir": "data", "timeframes": ["1D"]},
        "enable_health_checks": True,
    }

    # Validate configuration
    validated_config = validate_config(config)

    # Create storage with configured timeframes
    storage = DataStorage(
        data_dir=validated_config.storage.base_dir,
        timeframes=config["storage"]["timeframes"],
    )

    # Initialize collector with custom storage
    collector = DataCollector(validated_config.data_sources, storage=storage)

    # Collect and store data
    success = collector.collect_and_store(symbol="CS.D.BITCOIN.CFE.IP", timeframe="1D")

    if success:
        # Load stored data
        df = collector.load_data("CS.D.BITCOIN.CFE.IP", "1D")
        print(f"Loaded {len(df)} data points")

    collector.disconnect_all()


def example_massive_basic():
    """Example: Massive data source - single stock, 1D timeframe"""

    config = {
        "data_sources": {
            "massive": {
                "type": "massive",
                "name": "Massive",
                "api_key": MASSIVE_API_KEY,
                "tier": "free",
            }
        },
        "storage": {"base_dir": "data", "timeframes": ["1D"]},
        "enable_health_checks": True,
    }

    # Validate configuration
    validated_config = validate_config(config)

    # Create storage with configured timeframes
    storage = DataStorage(
        data_dir=validated_config.storage.base_dir,
        timeframes=config["storage"]["timeframes"],
    )

    # Initialize collector with custom storage
    collector = DataCollector(validated_config.data_sources, storage=storage)

    # Collect and store data for a single stock
    success = collector.collect_and_store(
        symbol="AAPL", timeframe="1D", source_name="massive"
    )

    if success:
        # Load stored data
        df = collector.load_data("AAPL", "1D")
        if df is not None:
            print(f"Loaded {len(df)} data points for AAPL")
            print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

    collector.disconnect_all()


def example_context_manager():
    """Example 2: Using context manager for automatic cleanup"""

    config = {
        "data_sources": {
            "ig_demo": {"type": "ig", "name": "IG Demo", "account_type": "demo"}
        }
    }

    validated_config = validate_config(config)

    with DataCollector(validated_config.data_sources) as collector:
        # Collect data for multiple symbols
        symbols = ["IX.D.FTSE.IFM.IP", "IX.D.DAX.IFM.IP"]

        for symbol in symbols:
            data = collector.collect_data_for_symbol(symbol, "1D")
            if data:
                collector.store_data(data)

    # Automatically disconnected


def example_health_monitoring():
    """Example 3: Health monitoring"""

    config = {
        "data_sources": {
            "ig_demo": {"type": "ig", "name": "IG Demo", "account_type": "demo"}
        },
        "enable_health_checks": True,
    }

    validated_config = validate_config(config)
    collector = DataCollector(
        validated_config.data_sources, enable_health_monitoring=True
    )

    # Check health
    health_results = collector.check_health()
    logger.info(f"Health check results: {health_results}")

    # Get detailed health status
    detailed_status = collector.get_health_status()
    for source, status in detailed_status.items():
        logger.info(f"Source: {source}")
        logger.info(f"  Healthy: {status['healthy']}")
        logger.info(f"  Success Rate: {status['success_rate']:.1f}%")
        logger.info(f"  Consecutive Failures: {status['consecutive_failures']}")

    # Check for unhealthy sources
    unhealthy = collector.get_unhealthy_sources()
    if unhealthy:
        logger.warning(f"Unhealthy sources detected: {unhealthy}")

    collector.disconnect_all()


def example_custom_alert_handler():
    """Example 4: Custom alert handler"""

    def send_to_telegram(alert):
        """Custom alert handler (placeholder)"""
        logger.info(
            f"Would send to Telegram: {alert['severity']} - {alert['error_message']}"
        )

    # Register custom handler
    alerting_service.register_handler(send_to_telegram)

    config = {
        "data_sources": {
            "ig_demo": {"type": "ig", "name": "IG Demo", "account_type": "demo"}
        }
    }

    validated_config = validate_config(config)
    collector = DataCollector(validated_config.data_sources)

    # Errors are automatically escalated through registered handlers
    collector.collect_and_store("INVALID_SYMBOL", "1D")

    # View recent alerts
    recent_alerts = alerting_service.get_recent_alerts(limit=5)
    logger.info(f"Recent alerts: {len(recent_alerts)}")

    collector.disconnect_all()


def example_resilience_configuration():
    """Example 5: Advanced resilience configuration"""

    config = {
        "data_sources": {
            "ig_demo": {
                "type": "ig",
                "name": "IG Demo",
                "account_type": "demo",
                # Timeout configuration
                "timeout": 30,
                # Retry configuration
                "max_retries": 5,
                "retry_base_delay": 2.0,
                "retry_max_delay": 60.0,
                # Circuit breaker configuration
                "circuit_breaker_threshold": 10,
                "circuit_breaker_timeout": 120,
                # Rate limiting configuration
                "rate_limit_calls": 30,  # Conservative for production
                "rate_limit_period": 60,
            }
        },
        "storage": {
            "base_dir": "production_data",
            "format": "csv",
            "enable_checksums": True,
            "atomic_writes": True,
        },
    }

    # Validation ensures all values are within acceptable ranges
    validated_config = validate_config(config)

    collector = DataCollector(validated_config.data_sources)

    # Collection automatically uses all resilience features:
    # - Retries with exponential backoff
    # - Circuit breaker protection
    # - Rate limiting
    # - Error escalation

    collector.collect_and_store("IX.D.FTSE.IFM.IP", "1D")

    collector.disconnect_all()


def example_batch_collection():
    """Example 6: Batch collection with error handling"""

    config = {
        "data_sources": {
            "ig_demo": {"type": "ig", "name": "IG Demo", "account_type": "demo"}
        },
        "enable_health_checks": True,
    }

    validated_config = validate_config(config)

    with DataCollector(validated_config.data_sources) as collector:
        symbols = ["IX.D.FTSE.IFM.IP", "IX.D.DAX.IFM.IP", "IX.D.SPTRD.IFM.IP"]

        results = {}

        for symbol in symbols:
            try:
                success = collector.collect_and_store(symbol, "1D")
                results[symbol] = "success" if success else "failed"
            except Exception as e:
                logger.error(f"Error collecting {symbol}: {e}")
                results[symbol] = "error"

        # Summary
        logger.info("Collection Results:")
        for symbol, status in results.items():
            logger.info(f"  {symbol}: {status}")

        # Check health after batch collection
        unhealthy = collector.get_unhealthy_sources()
        if unhealthy:
            logger.warning(f"Sources became unhealthy: {unhealthy}")


def example_data_validation():
    """Example 7: Data validation"""

    from data_collection.validation import DataValidator
    from data_collection.interfaces.market_data import (
        MarketData,
        MarketDataPoint,
        PriceData,
    )

    # Create sample data
    point = MarketDataPoint(
        timestamp=datetime.now(),
        open_price=PriceData(mid=7500.0),
        high_price=PriceData(mid=7520.0),
        low_price=PriceData(mid=7490.0),
        close_price=PriceData(mid=7510.0),
        volume=50000,
    )

    market_data = MarketData(
        symbol="IX.D.FTSE.IFM.IP", timeframe="1D", data_points=[point], source="IG"
    )

    # Validate before storing
    if DataValidator.validate_market_data(market_data):
        logger.info("Data validation passed")
        # Proceed with storage
    else:
        logger.error("Data validation failed")


def example_storage_info():
    """Example 8: Storage information and statistics"""

    config = {
        "data_sources": {
            "ig_demo": {"type": "ig", "name": "IG Demo", "account_type": "demo"}
        }
    }

    validated_config = validate_config(config)
    collector = DataCollector(validated_config.data_sources)

    # Get storage information
    storage_info = collector.get_storage_info()

    logger.info("Storage Information:")
    logger.info(f"  Directory: {storage_info['data_directory']}")
    logger.info(f"  Total Files: {storage_info['total_files']}")
    logger.info(f"  Total Size: {storage_info['total_size_mb']} MB")

    logger.info("\nTimeframe Details:")
    for timeframe, info in storage_info["timeframes"].items():
        logger.info(f"  {timeframe}:")
        logger.info(f"    Files: {info['files']}")
        logger.info(f"    Size: {info['size_mb']} MB")
        logger.info(f"    Symbols: {', '.join(info['symbols'][:5])}")

    collector.disconnect_all()


if __name__ == "__main__":
    print("Data Collection Module - Examples")
    print("=" * 50)

    # Run examples
    examples = [
        ("Basic Usage", example_basic_usage),
        ("Massive Basic", example_massive_basic),
        # ("Context Manager", example_context_manager),
        # ("Health Monitoring", example_health_monitoring),
        # ("Custom Alert Handler", example_custom_alert_handler),
        # ("Resilience Configuration", example_resilience_configuration),
        # ("Batch Collection", example_batch_collection),
        # ("Data Validation", example_data_validation),
        # ("Storage Info", example_storage_info)
    ]

    for name, func in examples:
        print(f"\nExample: {name}")
        print("-" * 50)
        try:
            func()
        except Exception as e:
            logger.error(f"Example failed: {e}")
        print()
