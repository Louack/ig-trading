"""
Abstract interface for data sources
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from .market_data import MarketData


class DataSource(ABC):
    """Abstract base class for all data sources"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize data source with configuration
        
        Args:
            config: Data source specific configuration
        """
        self.config = config
        self.name = config.get('name', self.__class__.__name__)
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the data source
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Close connection to the data source
        
        Returns:
            True if disconnection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_available_symbols(self) -> List[str]:
        """
        Get list of available symbols from this data source
        
        Returns:
            List of symbol identifiers
        """
        pass
    
    @abstractmethod
    def get_available_timeframes(self) -> List[str]:
        """
        Get list of available timeframes from this data source
        
        Returns:
            List of timeframe identifiers
        """
        pass
    
    @abstractmethod
    def fetch_historical_data(
        self, 
        symbol: str, 
        timeframe: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> Optional[MarketData]:
        """
        Fetch historical market data for a symbol
        
        Args:
            symbol: Symbol identifier
            timeframe: Timeframe (e.g., '1H', '4H', '1D')
            start_date: Start date for data (optional)
            end_date: End date for data (optional)
            limit: Maximum number of data points (optional)
            
        Returns:
            MarketData object or None if failed
        """
        pass
    
    @abstractmethod
    def fetch_latest_data(
        self, 
        symbol: str, 
        timeframe: str
    ) -> Optional[MarketData]:
        """
        Fetch latest market data for a symbol
        
        Args:
            symbol: Symbol identifier
            timeframe: Timeframe
            
        Returns:
            MarketData object or None if failed
        """
        pass
    
    def is_connected(self) -> bool:
        """
        Check if data source is connected
        
        Returns:
            True if connected, False otherwise
        """
        # Default implementation - can be overridden
        return hasattr(self, '_connected') and self._connected
    
    def get_source_info(self) -> Dict[str, Any]:
        """
        Get information about this data source
        
        Returns:
            Dictionary with source information
        """
        return {
            'name': self.name,
            'type': self.__class__.__name__,
            'connected': self.is_connected(),
            'config': self.config
        }
