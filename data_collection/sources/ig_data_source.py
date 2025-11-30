"""
IG API data source implementation
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from api_gateway.ig_client.master_client import IGClient
from settings import BASE_URLS, API_KEYS, IDENTIFIERS, PASSWORDS
from ..interfaces.data_source import DataSource
from ..interfaces.market_data import MarketData, MarketDataPoint, PriceData
from ..resilience import CircuitBreaker, RateLimiter, RetryConfig, retry_with_backoff
from ..alerting import escalate_error, AlertSeverity

logger = logging.getLogger(__name__)


class IGDataSource(DataSource):
    """IG API data source implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # IG-specific configuration
        self.account_type = config.get('account_type', 'demo')
        self.base_url = BASE_URLS[self.account_type]
        self.api_key = API_KEYS[self.account_type]
        self.identifier = IDENTIFIERS[self.account_type]
        self.password = PASSWORDS[self.account_type]
        
        # IG client
        self._client: Optional[IGClient] = None
        self._connected = False
        
        # Timeframe mapping
        self.timeframe_mapping = {
            '1H': {'resolution': 'HOUR', 'points': 1000},
            '4H': {'resolution': 'HOUR_4', 'points': 1000},
            '1D': {'resolution': 'DAY', 'points': 1000},
            '1W': {'resolution': 'WEEK', 'points': 1000},
            '1M': {'resolution': 'MONTH', 'points': 1000}
        }
        
        # Resilience configuration
        self.timeout = config.get('timeout', 30)
        self.max_retries = config.get('max_retries', 3)
        
        # Circuit breaker: open after 5 failures, wait 60s before retry
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.get('circuit_breaker_threshold', 5),
            recovery_timeout=config.get('circuit_breaker_timeout', 60)
        )
        
        # Rate limiter: IG limits are ~60 requests per minute
        # We'll be conservative: 40 requests per 60 seconds
        self.rate_limiter = RateLimiter(
            max_calls=config.get('rate_limit_calls', 40),
            period_seconds=config.get('rate_limit_period', 60)
        )
        
        # Retry configuration
        self.retry_config = RetryConfig(
            max_attempts=self.max_retries,
            base_delay=config.get('retry_base_delay', 1.0),
            max_delay=config.get('retry_max_delay', 30.0),
            exponential=True,
            jitter=True
        )
    
    def connect(self) -> bool:
        """Establish connection to IG API"""
        try:
            # Use retry mechanism for connection
            def _connect():
                client = IGClient(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    identifier=self.identifier,
                    password=self.password
                )
                
                # Test connection by getting account info
                account_info = client.accounts.get_accounts()
                if not account_info:
                    raise Exception("No account info received")
                
                return client
            
            self._client = retry_with_backoff(_connect, self.retry_config)
            self._connected = True
            logger.info(f"Connected to IG API ({self.account_type} account)")
            return True
                
        except Exception as e:
            logger.error(f"Failed to connect to IG API after retries: {e}")
            escalate_error(
                e, 
                {'component': 'IGDataSource', 'operation': 'connect', 'account_type': self.account_type},
                AlertSeverity.HIGH
            )
            self._connected = False
            return False
    
    def disconnect(self) -> bool:
        """Close connection to IG API"""
        try:
            self._client = None
            self._connected = False
            logger.info("Disconnected from IG API")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from IG API: {e}")
            return False
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available symbols from IG"""
        if not self.is_connected():
            logger.warning("Not connected to IG API")
            return []
        
        try:
            # This would need to be implemented based on IG API capabilities
            # For now, return a default list
            return [
                "IX.D.FTSE.IFM.IP",  # FTSE 100
                "IX.D.DAX.IFM.IP",   # DAX
                "IX.D.SPTRD.IFM.IP", # S&P 500
                "IX.D.NASDAQ.IFM.IP" # NASDAQ
            ]
        except Exception as e:
            logger.error(f"Failed to get available symbols: {e}")
            return []
    
    def get_available_timeframes(self) -> List[str]:
        """Get list of available timeframes from IG"""
        return list(self.timeframe_mapping.keys())
    
    def fetch_historical_data(
        self, 
        symbol: str, 
        timeframe: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> Optional[MarketData]:
        """Fetch historical market data from IG with resilience features"""
        if not self.is_connected():
            logger.warning("Not connected to IG API")
            return None
        
        if timeframe not in self.timeframe_mapping:
            logger.error(f"Unsupported timeframe: {timeframe}")
            return None
        
        # Check circuit breaker
        if self.circuit_breaker.is_open:
            logger.warning(f"Circuit breaker is open for IG API, skipping request for {symbol}")
            return None
        
        try:
            # Apply rate limiting
            self.rate_limiter.acquire()
            
            # Fetch with retries and circuit breaker
            def _fetch():
                config = self.timeframe_mapping[timeframe]
                
                # Use limit if provided, otherwise use default
                points = limit if limit else config['points']
                
                # Fetch data from IG API (using symbol as epic for IG)
                response = self._client.markets.get_prices_by_points(
                    epic=symbol,
                    resolution=config['resolution'],
                    num_points=points
                )
                
                return response
            
            # Execute with circuit breaker and retry
            response = self.circuit_breaker.call(
                lambda: retry_with_backoff(_fetch, self.retry_config)
            )
            
            # Convert IG response to unified format
            market_data = self._convert_ig_response_to_market_data(
                response, symbol, timeframe
            )
            
            logger.info(f"Fetched {len(market_data.data_points)} data points for {symbol} ({timeframe})")
            return market_data
            
        except Exception as e:
            logger.error(f"Failed to fetch historical data for {symbol} ({timeframe}): {e}")
            escalate_error(
                e,
                {
                    'component': 'IGDataSource',
                    'operation': 'fetch_historical_data',
                    'symbol': symbol,
                    'timeframe': timeframe
                },
                AlertSeverity.MEDIUM
            )
            return None
    
    def fetch_latest_data(
        self, 
        symbol: str, 
        timeframe: str
    ) -> Optional[MarketData]:
        """Fetch latest market data from IG"""
        # For IG, we'll fetch a small amount of recent data
        return self.fetch_historical_data(symbol, timeframe, limit=1)
    
    def _convert_ig_response_to_market_data(
        self, 
        response: Any, 
        symbol: str, 
        timeframe: str
    ) -> MarketData:
        """Convert IG API response to unified MarketData format"""
        data_dict = response.model_dump()
        prices = data_dict.get('prices', [])
        
        data_points = []
        
        for price_data in prices:
            # Extract price information
            open_price = self._extract_price_data(price_data.get('openPrice', {}))
            high_price = self._extract_price_data(price_data.get('highPrice', {}))
            low_price = self._extract_price_data(price_data.get('lowPrice', {}))
            close_price = self._extract_price_data(price_data.get('closePrice', {}))
            
            # Create data point
            data_point = MarketDataPoint(
                timestamp=datetime.fromisoformat(price_data['snapshotTimeUTC'].replace('Z', '+00:00')),
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
                volume=price_data.get('lastTradedVolume'),
                metadata={
                    'ig_snapshot_time': price_data.get('snapshotTimeUTC'),
                    'ig_last_update': price_data.get('lastUpdateTimeUTC')
                }
            )
            
            data_points.append(data_point)
        
        return MarketData(
            symbol=symbol,
            timeframe=timeframe,
            data_points=data_points,
            source='IG',
            collected_at=datetime.now(),
            metadata={
                'ig_response': data_dict,
                'account_type': self.account_type
            }
        )
    
    def _extract_price_data(self, price_dict: Dict[str, Any]) -> PriceData:
        """Extract price data from IG price dictionary"""
        if not isinstance(price_dict, dict):
            return PriceData()
        
        bid = price_dict.get('bid')
        ask = price_dict.get('ask')
        
        # Calculate mid price from bid/ask average
        mid = None
        if bid is not None and ask is not None:
            mid = round((bid + ask) / 2, 1)
        elif price_dict.get('mid') is not None:
            mid = round(price_dict.get('mid'), 1)
        
        return PriceData(
            bid=round(bid, 1) if bid is not None else None,
            ask=round(ask, 1) if ask is not None else None,
            mid=mid
        )
    
    def is_connected(self) -> bool:
        """Check if connected to IG API"""
        return self._connected and self._client is not None
