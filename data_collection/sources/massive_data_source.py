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
from common.alerting import escalate_error, AlertSeverity

logger = logging.getLogger(__name__)


class MassiveDataSource(DataSource):
    """Massive API data source implementation"""

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
        config: Dict[str, Any],
        client: Optional[MassiveClient] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize Massive data source

        Args:
            config: Configuration dictionary
            client: Optional MassiveClient instance (created if not provided)
            api_key: Optional API key (overrides config)
        """
        super().__init__(config)

        self.api_key = api_key or config.get("api_key")
        if not self.api_key:
            raise ValueError("Massive API key is required")

        # Use gateway client (resilience features are handled at gateway level)
        if client:
            self._client = client
        else:
            # Create gateway client with resilience features from config
            from common.resilience import CircuitBreaker, RateLimiter, RetryConfig

            tier = config.get("tier", "free")
            rate_limit = 4 if tier == "free" else config.get("rate_limit_calls", 100)

            rate_limiter = RateLimiter(
                max_calls=rate_limit, period_seconds=config.get("rate_limit_period", 60)
            )

            circuit_breaker = CircuitBreaker(
                failure_threshold=config.get("circuit_breaker_threshold", 10),
                recovery_timeout=config.get("circuit_breaker_timeout", 60),
            )

            retry_config = RetryConfig(
                max_attempts=config.get("max_retries", 3),
                base_delay=config.get("retry_base_delay", 1.0),
                max_delay=config.get("retry_max_delay", 30.0),
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
