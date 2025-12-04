"""
YFinance REST API Client

Thin wrapper around yfinance library with resilience features.
"""

import logging
from typing import Optional, Callable, Any, TYPE_CHECKING

import yfinance as yf

from common.resilience import CircuitBreaker, RateLimiter, RetryConfig, retry_with_backoff
from .core.exceptions import (
    YFinanceAPIError,
    YFinanceValidationError,
    YFinanceRateLimitError,
    YFinanceNotFoundError,
    YFinanceNetworkError,
    YFinanceTimeoutError,
)

if TYPE_CHECKING:
    from common.resilience import RateLimiter

logger = logging.getLogger(__name__)


class YFinanceRest:
    """
    Thin wrapper around yfinance library with resilience features.
    
    This class wraps yfinance.Ticker and adds rate limiting, circuit breaker, and retry logic.
    """
    
    def __init__(
        self,
        rate_limiter: Optional['RateLimiter'] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize YFinance REST client wrapper.
        
        Args:
            rate_limiter: Optional rate limiter instance
            circuit_breaker: Optional circuit breaker instance
            retry_config: Optional retry configuration
        """
        self.rate_limiter = rate_limiter
        self.circuit_breaker = circuit_breaker
        self.retry_config = retry_config
    
    def _with_resilience(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with resilience features (rate limiting, circuit breaker, retries).
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        # Apply rate limiting
        if self.rate_limiter:
            self.rate_limiter.acquire()
        
        # Execute with circuit breaker and retry
        def _execute():
            if self.circuit_breaker:
                return self.circuit_breaker.call(func, *args, **kwargs)
            return func(*args, **kwargs)
        
        if self.retry_config:
            return retry_with_backoff(_execute, self.retry_config)
        else:
            return _execute()
    
    def _handle_exception(self, e: Exception) -> None:
        """
        Convert library exceptions to custom exceptions.
        
        Args:
            e: Exception to convert
            
        Raises:
            Appropriate YFinanceAPIError subclass
        """
        error_str = str(e).lower()
        
        if "404" in error_str or "not found" in error_str:
            raise YFinanceNotFoundError(f"Ticker not found: {e}")
        elif "429" in error_str or "rate limit" in error_str or "too many requests" in error_str:
            raise YFinanceRateLimitError(f"Rate limit exceeded: {e}")
        elif "timeout" in error_str:
            raise YFinanceTimeoutError(f"Request timeout: {e}")
        elif "network" in error_str or "connection" in error_str:
            raise YFinanceNetworkError(f"Network error: {e}")
        elif "validation" in error_str or "invalid" in error_str:
            raise YFinanceValidationError(f"Validation error: {e}")
        else:
            raise YFinanceAPIError(f"API error: {e}")
    
    def Ticker(self, symbol: str, **kwargs):
        """
        Create a Ticker object with resilience features.
        
        Args:
            symbol: Stock symbol
            **kwargs: Additional arguments for yfinance.Ticker
            
        Returns:
            Ticker object with wrapped methods
        """
        ticker = yf.Ticker(symbol, **kwargs)
        return _ResilientTicker(ticker, self._with_resilience, self._handle_exception)


class _ResilientTicker:
    """Wrapper around yfinance.Ticker that adds resilience to method calls"""
    
    def __init__(self, ticker: yf.Ticker, with_resilience: Callable, handle_exception: Callable):
        self._ticker = ticker
        self._with_resilience = with_resilience
        self._handle_exception = handle_exception
    
    def history(self, *args, **kwargs):
        """Get historical data with resilience"""
        try:
            return self._with_resilience(self._ticker.history, *args, **kwargs)
        except Exception as e:
            self._handle_exception(e)
            raise
    
    @property
    def info(self):
        """Get ticker info with resilience (property, not method)"""
        try:
            # info is a property in yfinance, so we need to access it differently
            # We'll wrap the property access in a lambda
            def _get_info():
                return self._ticker.info
            return self._with_resilience(_get_info)
        except Exception as e:
            self._handle_exception(e)
            raise
    
    def __getattr__(self, name: str):
        """
        Delegate any other methods/attributes to the underlying ticker.
        """
        if hasattr(self._ticker, name):
            attr = getattr(self._ticker, name)
            if callable(attr):
                def wrapper(*args, **kwargs):
                    try:
                        return self._with_resilience(attr, *args, **kwargs)
                    except Exception as e:
                        self._handle_exception(e)
                        raise
                return wrapper
            # For properties, wrap access in a lambda
            else:
                def _get_property():
                    return attr
                try:
                    return self._with_resilience(_get_property)
                except Exception as e:
                    self._handle_exception(e)
                    raise
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

