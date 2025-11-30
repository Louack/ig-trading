"""
Data validation utilities for market data
"""

import logging
from datetime import datetime
from typing import Optional, List
from .interfaces.market_data import MarketData, MarketDataPoint

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates market data integrity"""
    
    @staticmethod
    def validate_market_data(market_data: MarketData) -> bool:
        """
        Validate market data integrity
        
        Args:
            market_data: MarketData object to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not market_data.data_points:
            logger.error(f"No data points in {market_data.symbol}")
            return False
        
        # Check timestamps are monotonic
        if not DataValidator._validate_timestamps(market_data.data_points):
            logger.error(f"Non-monotonic timestamps in {market_data.symbol}")
            return False
        
        # Check for future timestamps
        if not DataValidator._validate_no_future_timestamps(market_data.data_points):
            logger.error(f"Future timestamps detected in {market_data.symbol}")
            return False
        
        # Validate OHLC relationships
        if not DataValidator._validate_ohlc_relationships(market_data.data_points):
            logger.error(f"Invalid OHLC relationships in {market_data.symbol}")
            return False
        
        # Validate price values are positive
        if not DataValidator._validate_positive_prices(market_data.data_points):
            logger.error(f"Non-positive prices detected in {market_data.symbol}")
            return False
        
        return True
    
    @staticmethod
    def _validate_timestamps(data_points: List[MarketDataPoint]) -> bool:
        """Check that timestamps are monotonically increasing"""
        timestamps = [p.timestamp for p in data_points]
        return timestamps == sorted(timestamps)
    
    @staticmethod
    def _validate_no_future_timestamps(data_points: List[MarketDataPoint]) -> bool:
        """Check that no timestamps are in the future"""
        now = datetime.now()
        return all(p.timestamp <= now for p in data_points)
    
    @staticmethod
    def _validate_ohlc_relationships(data_points: List[MarketDataPoint]) -> bool:
        """Validate OHLC price relationships"""
        for point in data_points:
            high = point.high_price.ohlc_price
            low = point.low_price.ohlc_price
            open_p = point.open_price.ohlc_price
            close = point.close_price.ohlc_price
            
            # Skip if any price is None
            if None in [high, low, open_p, close]:
                continue
            
            # High must be >= all other prices
            if high < low or high < open_p or high < close:
                logger.error(
                    f"Invalid OHLC at {point.timestamp}: "
                    f"high={high}, low={low}, open={open_p}, close={close}"
                )
                return False
            
            # Low must be <= all other prices
            if low > open_p or low > close:
                logger.error(
                    f"Invalid OHLC at {point.timestamp}: "
                    f"high={high}, low={low}, open={open_p}, close={close}"
                )
                return False
        
        return True
    
    @staticmethod
    def _validate_positive_prices(data_points: List[MarketDataPoint]) -> bool:
        """Validate that all prices are positive"""
        for point in data_points:
            prices = [
                point.open_price.ohlc_price,
                point.high_price.ohlc_price,
                point.low_price.ohlc_price,
                point.close_price.ohlc_price
            ]
            
            for price in prices:
                if price is not None and price <= 0:
                    logger.error(f"Non-positive price at {point.timestamp}: {price}")
                    return False
        
        return True
    
    @staticmethod
    def validate_volume(data_points: List[MarketDataPoint]) -> bool:
        """Validate volume data is non-negative"""
        for point in data_points:
            if point.volume is not None and point.volume < 0:
                logger.error(f"Negative volume at {point.timestamp}: {point.volume}")
                return False
        
        return True

