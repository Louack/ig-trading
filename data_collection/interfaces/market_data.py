"""
Unified market data models
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import pandas as pd


@dataclass
class PriceData:
    """Represents price data (bid, ask, mid)"""
    bid: Optional[float] = None
    ask: Optional[float] = None
    mid: Optional[float] = None
    
    def __post_init__(self):
        """Calculate mid price if not provided"""
        if self.mid is None and self.bid is not None and self.ask is not None:
            self.mid = round((self.bid + self.ask) / 2, 1)
        
        # Round all prices to 1 decimal place
        if self.bid is not None:
            self.bid = round(self.bid, 1)
        if self.ask is not None:
            self.ask = round(self.ask, 1)
        if self.mid is not None:
            self.mid = round(self.mid, 1)
    
    @property
    def spread(self) -> Optional[float]:
        """Calculate spread between ask and bid"""
        if self.ask is not None and self.bid is not None:
            return round(self.ask - self.bid, 1)
        return None
    
    @property
    def ohlc_price(self) -> Optional[float]:
        """Get the price to use for OHLC data (mid price)"""
        return self.mid


@dataclass
class MarketDataPoint:
    """Represents a single market data point"""
    timestamp: datetime
    open_price: PriceData
    high_price: PriceData
    low_price: PriceData
    close_price: PriceData
    volume: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'openPrice': self.open_price.ohlc_price,
            'highPrice': self.high_price.ohlc_price,
            'lowPrice': self.low_price.ohlc_price,
            'closePrice': self.close_price.ohlc_price,
            'lastTradedVolume': self.volume,
            'metadata': self.metadata
        }


@dataclass
class MarketData:
    """Represents market data for an instrument"""
    symbol: str  # Changed from 'instrument' to 'symbol' for standardization
    timeframe: str
    data_points: List[MarketDataPoint]
    source: str
    collected_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame"""
        if not self.data_points:
            return pd.DataFrame()
        
        # Convert all data points to dictionaries
        data_dicts = [point.to_dict() for point in self.data_points]
        
        # Create DataFrame
        df = pd.DataFrame(data_dicts)
        
        # Add symbol, timeframe, and source columns
        df['symbol'] = self.symbol
        df['timeframe'] = self.timeframe
        df['source'] = self.source
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Reorder columns
        metadata_cols = ['symbol', 'timeframe', 'source', 'timestamp']
        ohlc_cols = ['openPrice', 'highPrice', 'lowPrice', 'closePrice']
        volume_cols = ['lastTradedVolume']
        other_cols = [col for col in df.columns if col not in metadata_cols + ohlc_cols + volume_cols]
        
        df = df[metadata_cols + ohlc_cols + volume_cols + other_cols]
        
        return df
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> 'MarketData':
        """Create MarketData from DataFrame"""
        if df.empty:
            raise ValueError("DataFrame is empty")
        
        # Extract metadata from first row
        symbol = df['symbol'].iloc[0]
        timeframe = df['timeframe'].iloc[0]
        source = df['source'].iloc[0]
        
        data_points = []
        
        for _, row in df.iterrows():
            # Extract OHLC price data (using mid prices)
            open_price = PriceData(mid=row.get('openPrice'))
            high_price = PriceData(mid=row.get('highPrice'))
            low_price = PriceData(mid=row.get('lowPrice'))
            close_price = PriceData(mid=row.get('closePrice'))
            
            # Create data point
            data_point = MarketDataPoint(
                timestamp=pd.to_datetime(row['timestamp']),
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
                volume=row.get('lastTradedVolume'),
                metadata=row.get('metadata', {})
            )
            
            data_points.append(data_point)
        
        return cls(
            symbol=symbol,
            timeframe=timeframe,
            data_points=data_points,
            source=source
        )
    
    def get_latest_point(self) -> Optional[MarketDataPoint]:
        """Get the most recent data point"""
        if not self.data_points:
            return None
        
        return max(self.data_points, key=lambda x: x.timestamp)
    
    def get_price_range(self) -> Dict[str, float]:
        """Get price range statistics"""
        if not self.data_points:
            return {}
        
        all_prices = []
        for point in self.data_points:
            if point.open_price.ohlc_price is not None:
                all_prices.append(point.open_price.ohlc_price)
            if point.high_price.ohlc_price is not None:
                all_prices.append(point.high_price.ohlc_price)
            if point.low_price.ohlc_price is not None:
                all_prices.append(point.low_price.ohlc_price)
            if point.close_price.ohlc_price is not None:
                all_prices.append(point.close_price.ohlc_price)
        
        if not all_prices:
            return {}
        
        return {
            'min_price': min(all_prices),
            'max_price': max(all_prices),
            'avg_price': sum(all_prices) / len(all_prices)
        }
    
    def __len__(self) -> int:
        """Return number of data points"""
        return len(self.data_points)
    
    def __str__(self) -> str:
        return f"MarketData(symbol='{self.symbol}', timeframe='{self.timeframe}', points={len(self.data_points)})"
