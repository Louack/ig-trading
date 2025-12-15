"""
YFinance market data implementation using API gateway client
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd

from ..interfaces.data_source import DataSource
from ..interfaces.market_data import MarketData, MarketDataPoint, PriceData
from api_gateway.yfinance_client import YFinanceClient
from common.alerting import escalate_error, AlertSeverity

logger = logging.getLogger(__name__)


class YFinanceDataSource(DataSource):
    """YFinance API data source implementation"""

    # String name for TOML config mapping
    str_name: str = "yfinance"

    TIMEFRAME_MAPPING = {
        "1min": "1m",
        "5min": "5m",
        "15min": "15m",
        "30min": "30m",
        "1H": "1h",
        "1D": "1d",
        "1W": "1wk",
        "1M": "1mo",
    }

    # Common index symbols that need caret prefix for YFinance
    INDEX_SYMBOLS = {
        "NDX": "^NDX",  # NASDAQ-100
        "SPX": "^GSPC",  # S&P 500
        "DJI": "^DJI",  # Dow Jones
        "IXIC": "^IXIC",  # NASDAQ Composite
    }

    @classmethod
    def _normalize_symbol(cls, symbol: str) -> str:
        """
        Normalize symbol for YFinance API

        YFinance requires caret (^) prefix for indices to get proper OHLC data.
        Without the caret, indices may return identical OHLC values.

        Args:
            symbol: Original symbol

        Returns:
            Normalized symbol with caret prefix if it's a known index
        """
        # If already has caret, return as-is
        if symbol.startswith("^"):
            return symbol

        # Check if it's a known index symbol
        return cls.INDEX_SYMBOLS.get(symbol, symbol)

    def __init__(
        self,
        config: Dict[str, Any],
        client: Optional[YFinanceClient] = None,
    ):
        """
        Initialize YFinance data source

        Args:
            config: Configuration dictionary
            client: Optional YFinanceClient instance (created if not provided)
        """
        super().__init__(config)

        if client:
            self._client = client
        else:
            from common.resilience import CircuitBreaker, RateLimiter, RetryConfig

            # YFinance has strict rate limits (free tier: ~2000 requests/hour)
            rate_limiter = RateLimiter(
                max_calls=config.get("rate_limit_calls", 30),
                period_seconds=config.get("rate_limit_period", 60),
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

            self._client = YFinanceClient(
                rate_limiter=rate_limiter,
                circuit_breaker=circuit_breaker,
                retry_config=retry_config,
            )

        self._connected = False

    def connect(self) -> bool:
        """Establish connection to YFinance"""
        # YFinance doesn't require explicit connection, but we can test it
        if self._client is not None and self._connected:
            return True

        try:
            # Test connection by fetching a well-known ticker
            # info is a property, not a method
            ticker = self._client.rest.Ticker("AAPL")
            _ = ticker.info  # Access property to test connection
            self._connected = True
            logger.info("Connected to YFinance")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to YFinance: {e}")
            escalate_error(
                e,
                {"component": "YFinanceDataSource", "operation": "connect"},
                AlertSeverity.HIGH,
            )
            self._connected = False
            return False

    def disconnect(self) -> bool:
        """Close connection to YFinance"""
        try:
            self._client = None
            self._connected = False
            logger.info("Disconnected from YFinance")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from YFinance: {e}")
            return False

    def get_available_symbols(self) -> List[str]:
        """Get list of available symbols from YFinance"""
        if not self.is_connected():
            logger.warning("Not connected to YFinance")
            return []

        try:
            # YFinance supports most stock symbols, ETFs, indices
            # Return a sample list of common symbols
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
                "IWM",
                "VTI",
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
        """Fetch historical market data from YFinance"""
        if not self.is_connected():
            logger.warning("Not connected to YFinance")
            return None

        if timeframe not in self.TIMEFRAME_MAPPING:
            logger.error(f"Unsupported timeframe: {timeframe}")
            return None

        try:
            yf_interval = self.TIMEFRAME_MAPPING[timeframe]

            end_date = end_date or datetime.now()
            start_date = start_date or (end_date - timedelta(days=365))

            # Normalize symbol for YFinance (add caret prefix for indices)
            normalized_symbol = self._normalize_symbol(symbol)
            if normalized_symbol != symbol:
                logger.info(
                    f"Normalizing symbol '{symbol}' to '{normalized_symbol}' for YFinance "
                    f"(indices require caret prefix for proper OHLC data)"
                )

            ticker = self._client.rest.Ticker(normalized_symbol)

            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=yf_interval,
            )

            if df is None or df.empty:
                logger.warning(
                    f"No data returned for {normalized_symbol} ({timeframe})"
                )
                return None

            if limit:
                df = df.tail(limit)

            # Use original symbol in MarketData (not normalized) to preserve user's symbol
            market_data = self._convert_yfinance_response(df, symbol, timeframe)

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
                    "component": "YFinanceDataSource",
                    "operation": "fetch_historical_data",
                    "symbol": symbol,
                    "timeframe": timeframe,
                },
                AlertSeverity.MEDIUM,
            )
            return None

    def fetch_latest_data(self, symbol: str, timeframe: str) -> Optional[MarketData]:
        """Fetch latest market data from YFinance"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        return self.fetch_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            limit=2,
        )

    def _convert_yfinance_response(
        self, df: pd.DataFrame, symbol: str, timeframe: str
    ) -> MarketData:
        """Convert YFinance DataFrame to unified MarketData format"""
        data_points = []

        for idx, row in df.iterrows():
            # YFinance returns timestamps as index
            timestamp = idx
            if isinstance(timestamp, pd.Timestamp):
                timestamp = timestamp.to_pydatetime()
                # Convert to timezone-naive (UTC) for consistency
                if timestamp.tzinfo is not None:
                    timestamp = timestamp.replace(tzinfo=None)

            open_price = PriceData(mid=float(row["Open"]))
            high_price = PriceData(mid=float(row["High"]))
            low_price = PriceData(mid=float(row["Low"]))
            close_price = PriceData(mid=float(row["Close"]))

            volume = float(row["Volume"]) if "Volume" in row else 0.0

            data_point = MarketDataPoint(
                timestamp=timestamp,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
                volume=volume,
                metadata={
                    "dividends": float(row.get("Dividends", 0)),
                    "stock_splits": float(row.get("Stock Splits", 0)),
                },
            )

            data_points.append(data_point)

        return MarketData(
            symbol=symbol,
            timeframe=timeframe,
            data_points=data_points,
            source="YFinance",
            collected_at=datetime.now(),
            metadata={"total_bars": len(data_points)},
        )

    def is_connected(self) -> bool:
        """Check if connected to YFinance"""
        return self._connected and self._client is not None
