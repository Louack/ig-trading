"""
Massive market data implementation using API gateway client
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from polygon.rest.models import Agg

from ..interfaces.data_source import DataSource
from ..interfaces.market_data import MarketData, MarketDataPoint, PriceData
from api_gateway.massive_client import MassiveClient
from common.resilience import CircuitBreaker, RateLimiter, RetryConfig
from common.alerting import escalate_error, AlertSeverity

logger = logging.getLogger(__name__)


class MassiveDataSource(DataSource):
    """Massive API data source implementation"""

    # String name for TOML config mapping
    str_name: str = "massive"

    TIMEFRAME_MAPPING = {
        "1min": {"multiplier": 1, "timespan": "minute"},
        "5min": {"multiplier": 5, "timespan": "minute"},
        "15min": {"multiplier": 15, "timespan": "minute"},
        "1H": {"multiplier": 1, "timespan": "hour"},
        "4H": {"multiplier": 4, "timespan": "hour"},
        "1D": {"multiplier": 1, "timespan": "day"},
        "1W": {"multiplier": 1, "timespan": "week"},
        "1M": {"multiplier": 1, "timespan": "month"},
    }

    def __init__(
        self,
        api_key: str,
        name: str = "Massive",
        tier: str = "free",
        client: Optional[MassiveClient] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        rate_limiter: Optional[RateLimiter] = None,
        retry_config: Optional[RetryConfig] = None,
        max_retries: int = 3,
        retry_base_delay: float = 1.0,
        retry_max_delay: float = 30.0,
        circuit_breaker_threshold: int = 10,
        circuit_breaker_timeout: int = 60,
        rate_limit_calls: Optional[int] = None,
        rate_limit_period: int = 60,
    ):
        """
        Initialize Massive data source

        Args:
            name: Name identifier for this data source
            api_key: Massive API key (required)
            tier: API tier ('free', 'starter', 'developer', 'advanced')
            client: Optional MassiveClient instance (created if not provided)
            circuit_breaker: Optional CircuitBreaker instance (created if not provided)
            rate_limiter: Optional RateLimiter instance (created if not provided)
            retry_config: Optional RetryConfig instance (created if not provided)
            max_retries: Maximum number of retry attempts
            retry_base_delay: Base delay for retries in seconds
            retry_max_delay: Maximum delay for retries in seconds
            circuit_breaker_threshold: Number of failures before opening circuit
            circuit_breaker_timeout: Time in seconds before attempting recovery
            rate_limit_calls: Maximum number of calls per period (defaults based on tier)
            rate_limit_period: Time period in seconds for rate limiting
        """
        super().__init__(name)

        if not api_key:
            raise ValueError("Massive API key is required")
        self.api_key = api_key
        self.tier = tier

        # Use gateway client (resilience features are handled at gateway level)
        if client:
            self._client = client
        else:
            # Create gateway client with resilience features
            # Default rate limit based on tier
            if rate_limit_calls is None:
                rate_limit_calls = 4 if tier == "free" else 100

            rate_limiter = rate_limiter or RateLimiter(
                max_calls=rate_limit_calls,
                period_seconds=rate_limit_period,
            )

            circuit_breaker = circuit_breaker or CircuitBreaker(
                failure_threshold=circuit_breaker_threshold,
                recovery_timeout=circuit_breaker_timeout,
            )

            retry_config = retry_config or RetryConfig(
                max_attempts=max_retries,
                base_delay=retry_base_delay,
                max_delay=retry_max_delay,
                exponential=True,
                jitter=True,
            )

            self._client = MassiveClient(
                api_key=self.api_key,
                rate_limiter=rate_limiter,
                circuit_breaker=circuit_breaker,
                retry_config=retry_config,
            )

        self._connected = False

    def connect(self) -> bool:
        """Establish connection to Massive"""
        # If client already injected and connected, skip
        if self._client is not None and self._connected:
            return True

        try:
            # Test connection using gateway client
            self._client.rest.get_ticker_details("AAPL")
            self._connected = True
            logger.info("Connected to Massive")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Massive: {e}")
            escalate_error(
                e,
                {"component": "MassiveDataSource", "operation": "connect"},
                AlertSeverity.HIGH,
            )
            self._connected = False
            return False

    def disconnect(self) -> bool:
        """Close connection to Massive"""
        try:
            self._client = None
            self._connected = False
            logger.info("Disconnected from Massive")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from Massive: {e}")
            return False

    def get_available_symbols(self) -> List[str]:
        """Get list of available symbols from Massive"""
        if not self.is_connected():
            logger.warning("Not connected to Massive")
            return []

        try:
            return [
                "AAPL",
                "MSFT",
                "GOOGL",
                "AMZN",
                "META",
                "TSLA",
                "NVDA",
                "SPY",
                "QQQ",
                "DIA",
            ]
        except Exception as e:
            logger.error(f"Failed to get available symbols: {e}")
            return []

    def get_available_timeframes(self) -> List[str]:
        """Get list of available timeframes"""
        return list(self.TIMEFRAME_MAPPING.keys())

    def fetch_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Optional[MarketData]:
        """Fetch historical market data from Massive"""
        if not self.is_connected():
            logger.warning("Not connected to Massive")
            return None

        if timeframe not in self.TIMEFRAME_MAPPING:
            logger.error(f"Unsupported timeframe: {timeframe}")
            return None

        try:
            # Use gateway client - resilience features are handled at gateway level
            config = self.TIMEFRAME_MAPPING[timeframe]

            end_date_str = (end_date or datetime.now()).strftime("%Y-%m-%d")
            start_date_str = (
                start_date or datetime.now() - timedelta(days=365)
            ).strftime("%Y-%m-%d")

            # Gateway client handles rate limiting, circuit breaker, and retries
            aggs = []
            for agg in self._client.rest.list_aggs(
                ticker=symbol,
                multiplier=config["multiplier"],
                timespan=config["timespan"],
                from_=start_date_str,
                to=end_date_str,
                limit=limit or 50000,
            ):
                aggs.append(agg)

            market_data = self._convert_massive_response(aggs, symbol, timeframe)

            logger.info(
                f"Fetched {len(market_data.data_points)} data points for {symbol} ({timeframe})"
            )
            return market_data

        except Exception as e:
            logger.error(
                f"Failed to fetch historical data for {symbol} ({timeframe}): {e}"
            )
            escalate_error(
                e,
                {
                    "component": "MassiveDataSource",
                    "operation": "fetch_historical_data",
                    "symbol": symbol,
                    "timeframe": timeframe,
                },
                AlertSeverity.MEDIUM,
            )
            return None

    def fetch_latest_data(self, symbol: str, timeframe: str) -> Optional[MarketData]:
        """Fetch latest market data from Massive"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        return self.fetch_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            limit=2,
        )

    def _convert_massive_response(
        self, aggs: List[Agg], symbol: str, timeframe: str
    ) -> MarketData:
        """Convert Massive aggregates to unified MarketData format"""
        data_points = []

        for agg in aggs:
            open_price = PriceData(mid=float(agg.open))
            high_price = PriceData(mid=float(agg.high))
            low_price = PriceData(mid=float(agg.low))
            close_price = PriceData(mid=float(agg.close))

            data_point = MarketDataPoint(
                timestamp=datetime.fromtimestamp(agg.timestamp / 1000),
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
                volume=agg.volume,
                metadata={
                    "vwap": getattr(agg, "vwap", None),
                    "transactions": getattr(agg, "transactions", None),
                },
            )

            data_points.append(data_point)

        return MarketData(
            symbol=symbol,
            timeframe=timeframe,
            data_points=data_points,
            source="Massive",
            collected_at=datetime.now(),
            metadata={"total_bars": len(aggs)},
        )

    def is_connected(self) -> bool:
        """Check if connected to Massive"""
        return self._connected and self._client is not None
