"""
Data collector that can work with multiple data sources
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

from .interfaces.data_source import DataSource
from .interfaces.market_data import MarketData
from .factory.data_source_factory import DataSourceFactory
from .storage.data_storage import DataStorage
from .health import HealthMonitor
from common.alerting import escalate_error, AlertSeverity
from data_collection.config import INSTRUMENTS, TIMEFRAMES

logger = logging.getLogger(__name__)


class DataCollector:
    """Data collector that can work with multiple data sources"""
    
    def __init__(
        self, 
        data_sources: Dict[str, Dict[str, Any]], 
        storage: Optional[DataStorage] = None,
        health_monitor: Optional[HealthMonitor] = None,
        enable_health_monitoring: bool = True
    ):
        """
        Initialize data collector with multiple data sources
        
        Args:
            data_sources: Dictionary mapping source names to their configurations
            storage: Optional DataStorage instance (created if not provided)
            health_monitor: Optional HealthMonitor instance (created if not provided)
            enable_health_monitoring: Enable health monitoring for data sources
        """
        self.data_sources: Dict[str, DataSource] = {}
        self.storage = storage or DataStorage()
        self.enable_health_monitoring = enable_health_monitoring
        
        # Initialize health monitor
        if enable_health_monitoring:
            self.health_monitor = health_monitor or HealthMonitor()
        else:
            self.health_monitor = None
        
        # Initialize data sources
        for source_name, config in data_sources.items():
            try:
                source_type = config.get('type', source_name)
                source = DataSourceFactory.create_data_source(source_type, config)
                
                # Connect to data source
                if source.connect():
                    self.data_sources[source_name] = source
                    logger.info(f"Connected to {source_name} data source")
                    
                    # Add to health monitoring
                    if self.health_monitor:
                        self.health_monitor.add_source(source_name, source)
                else:
                    logger.error(f"Failed to connect to {source_name} data source")
                    escalate_error(
                        Exception(f"Failed to connect to {source_name}"),
                        {'component': 'DataCollector', 'source': source_name},
                        AlertSeverity.HIGH
                    )
                    
            except Exception as e:
                logger.error(f"Failed to initialize {source_name} data source: {e}")
                escalate_error(
                    e,
                    {'component': 'DataCollector', 'source': source_name, 'config': config},
                    AlertSeverity.HIGH
                )
        
        # Configuration
        self.symbols = INSTRUMENTS  # Keep using INSTRUMENTS config but treat as symbols
        self.timeframes = TIMEFRAMES
    
    def collect_data_for_symbol(
        self, 
        symbol: str, 
        timeframe: str, 
        source_name: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Optional[MarketData]:
        """
        Collect data for a specific symbol and timeframe
        
        Args:
            symbol: Symbol identifier
            timeframe: Timeframe
            source_name: Specific source to use (optional)
            limit: Maximum number of data points
            
        Returns:
            MarketData object or None if failed
        """
        # Select data source
        if source_name:
            if source_name not in self.data_sources:
                logger.error(f"Data source {source_name} not available")
                return None
            source = self.data_sources[source_name]
        else:
            # Use first available source
            if not self.data_sources:
                logger.error("No data sources available")
                return None
            source = next(iter(self.data_sources.values()))
        
        try:
            # Fetch data
            market_data = source.fetch_historical_data(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit
            )
            
            if market_data:
                logger.info(f"Collected {len(market_data)} data points for {symbol} ({timeframe}) from {source.name}")
                return market_data
            else:
                logger.warning(f"No data collected for {symbol} ({timeframe})")
                return None
                
        except Exception as e:
            logger.error(f"Failed to collect data for {symbol} ({timeframe}): {e}")
            return None
    
    def collect_data_for_category(
        self, 
        category: str, 
        timeframe: str, 
        source_name: Optional[str] = None
    ) -> List[MarketData]:
        """
        Collect data for all instruments in a category
        
        Args:
            category: Instrument category
            timeframe: Timeframe
            source_name: Specific source to use (optional)
            
        Returns:
            List of MarketData objects
        """
        if category not in self.symbols:
            logger.error(f"Unknown category: {category}")
            return []
        
        data_list = []
        for symbol in self.symbols[category]:
            market_data = self.collect_data_for_symbol(
                symbol, timeframe, source_name
            )
            if market_data:
                data_list.append(market_data)
        
        return data_list
    
    def collect_all_data(self, source_name: Optional[str] = None) -> Dict[str, List[MarketData]]:
        """
        Collect data for all instruments and timeframes
        
        Args:
            source_name: Specific source to use (optional)
            
        Returns:
            Dictionary mapping categories to lists of MarketData objects
        """
        all_data = {}
        
        for category in self.symbols.keys():
            all_data[category] = []
            
            for timeframe in self.timeframes.keys():
                category_data = self.collect_data_for_category(
                    category, timeframe, source_name
                )
                all_data[category].extend(category_data)
        
        return all_data
    
    def store_data(self, market_data: MarketData) -> bool:
        """
        Store market data to storage
        
        Args:
            market_data: MarketData object to store
            
        Returns:
            True if successful, False otherwise
        """
        return self.storage.store_market_data(market_data)
    
    def store_multiple_data(self, market_data_list: List[MarketData]) -> Dict[str, bool]:
        """
        Store multiple market data objects
        
        Args:
            market_data_list: List of MarketData objects
            
        Returns:
            Dictionary mapping instrument names to success status
        """
        return self.storage.store_multiple_market_data(market_data_list)
    
    def collect_and_store(
        self, 
        symbol: str, 
        timeframe: str, 
        source_name: Optional[str] = None
    ) -> bool:
        """
        Collect data and store it in one operation
        
        Args:
            symbol: Symbol identifier
            timeframe: Timeframe
            source_name: Specific source to use (optional)
            
        Returns:
            True if successful, False otherwise
        """
        # Collect data
        market_data = self.collect_data_for_symbol(symbol, timeframe, source_name)
        
        if market_data:
            # Store data
            return self.store_data(market_data)
        else:
            return False
    
    def collect_and_store_all(self, source_name: Optional[str] = None) -> Dict[str, bool]:
        """
        Collect and store data for all instruments and timeframes
        
        Args:
            source_name: Specific source to use (optional)
            
        Returns:
            Dictionary mapping instrument names to success status
        """
        # Collect all data
        all_data = self.collect_all_data(source_name)
        
        # Store all data
        results = {}
        for category, market_data_list in all_data.items():
            category_results = self.store_multiple_data(market_data_list)
            results.update(category_results)
        
        return results
    
    def get_available_sources(self) -> List[str]:
        """
        Get list of available data sources
        
        Returns:
            List of source names
        """
        return list(self.data_sources.keys())
    
    def get_source_info(self, source_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific data source
        
        Args:
            source_name: Name of the data source
            
        Returns:
            Source information or None if not found
        """
        if source_name in self.data_sources:
            return self.data_sources[source_name].get_source_info()
        return None
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get information about stored data
        
        Returns:
            Storage information
        """
        return self.storage.get_storage_info()
    
    def get_source_for_symbol(self, symbol: str, timeframe: str) -> Optional[str]:
        """
        Get the data source for a specific symbol and timeframe
        
        Args:
            symbol: Symbol identifier
            timeframe: Timeframe
            
        Returns:
            Source name or None if not found
        """
        return self.storage.get_source_for_symbol(symbol, timeframe)
    
    def get_sources_for_timeframe(self, timeframe: str) -> Dict[str, str]:
        """
        Get all symbols and their sources for a timeframe
        
        Args:
            timeframe: Timeframe
            
        Returns:
            Dictionary mapping symbols to their sources
        """
        return self.storage.get_sources_for_timeframe(timeframe)
    
    def load_data(
        self, 
        symbol: str, 
        timeframe: str, 
        source: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Load data from storage
        
        Args:
            symbol: Symbol identifier
            timeframe: Timeframe
            source: Optional source filter
            
        Returns:
            DataFrame with data or None if not found
        """
        return self.storage.load_latest_data(symbol, timeframe, source)
    
    def disconnect_all(self) -> None:
        """Disconnect from all data sources"""
        for source_name, source in self.data_sources.items():
            try:
                source.disconnect()
                logger.info(f"Disconnected from {source_name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {source_name}: {e}")
        
        self.data_sources.clear()
    
    def check_health(self) -> Dict[str, bool]:
        """
        Check health of all data sources
        
        Returns:
            Dictionary mapping source names to health status
        """
        if not self.health_monitor:
            logger.warning("Health monitoring is not enabled")
            return {}
        
        return self.health_monitor.check_all()
    
    def get_health_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed health status of all data sources
        
        Returns:
            Dictionary with health status information
        """
        if not self.health_monitor:
            logger.warning("Health monitoring is not enabled")
            return {}
        
        return self.health_monitor.get_all_status()
    
    def get_unhealthy_sources(self) -> List[str]:
        """
        Get list of unhealthy data sources
        
        Returns:
            List of source names that are unhealthy
        """
        if not self.health_monitor:
            return []
        
        return self.health_monitor.get_unhealthy_sources()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect_all()
