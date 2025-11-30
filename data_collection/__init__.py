"""
Data Collection Service for IG Trading System
"""

from .unified_data_collector import UnifiedDataCollector
from .storage.unified_data_storage import UnifiedDataStorage
from .interfaces.data_source import DataSource
from .interfaces.market_data import MarketData, MarketDataPoint, PriceData
from .factory.data_source_factory import DataSourceFactory
from .sources.ig_data_source import IGDataSource

# Legacy imports for backward compatibility
from .market_data_collector import MarketDataCollector
from .data_storage import DataStorage

__all__ = [
    # New unified system
    "UnifiedDataCollector",
    "UnifiedDataStorage",
    "DataSource",
    "MarketData",
    "MarketDataPoint",
    "PriceData",
    "DataSourceFactory",
    "IGDataSource",
    
    # Legacy system (deprecated)
    "MarketDataCollector",
    "DataStorage",
]
