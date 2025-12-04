"""
Data Collection Service for IG Trading System
"""

from .data_collector import DataCollector
from .storage.data_storage import DataStorage
from .interfaces.data_source import DataSource
from .interfaces.market_data import MarketData, MarketDataPoint, PriceData
from .factory.data_source_factory import DataSourceFactory
from .sources.ig_data_source import IGDataSource

__all__ = [
    "DataCollector",
    "DataStorage",
    "DataSource",
    "MarketData",
    "MarketDataPoint",
    "PriceData",
    "DataSourceFactory",
    "IGDataSource",
]
