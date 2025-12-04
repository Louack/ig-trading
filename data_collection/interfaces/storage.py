"""
Storage interface for market data persistence
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

from .market_data import MarketData


class StorageInterface(ABC):
    """Abstract interface for market data storage implementations"""

    @abstractmethod
    def store_market_data(self, market_data: MarketData) -> bool:
        """
        Store market data

        Args:
            market_data: MarketData object to store

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def load_latest_data(
        self, symbol: str, timeframe: str, source: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Load the most recent data for a symbol

        Args:
            symbol: Symbol identifier
            timeframe: Timeframe
            source: Optional source filter

        Returns:
            DataFrame with latest data or None if not found
        """
        pass

    @abstractmethod
    def load_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> Optional[pd.DataFrame]:
        """
        Load historical data for a symbol

        Args:
            symbol: Symbol identifier
            timeframe: Timeframe
            start_date: Start date filter
            end_date: End date filter
            source: Optional source filter

        Returns:
            DataFrame with historical data or None if not found
        """
        pass

    @abstractmethod
    def list_available_symbols(
        self, timeframe: str, source: Optional[str] = None
    ) -> List[str]:
        """
        List available symbols for a timeframe

        Args:
            timeframe: Timeframe
            source: Optional source filter

        Returns:
            List of symbol identifiers
        """
        pass
