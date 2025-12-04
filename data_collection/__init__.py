"""
Data Collection Service for IG Trading System
"""

from .data_collector import DataCollector
from .storage import CSVStorage, StorageFactory, StorageInterface
from .interfaces.data_source import DataSource
from .interfaces.market_data import MarketData, MarketDataPoint, PriceData
from .factory.data_source_factory import DataSourceFactory
from .sources.ig_data_source import IGDataSource

__all__ = [
    "DataCollector",
    "CSVStorage",
    "StorageFactory",
    "StorageInterface",
    "DataSource",
    "MarketData",
    "MarketDataPoint",
    "PriceData",
    "DataSourceFactory",
    "IGDataSource",
]
