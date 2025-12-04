"""
Massive REST API Client

Thin wrapper around polygon.RESTClient with resilience features.
"""

import logging
from typing import Optional, Callable, Any
from polygon import RESTClient

from common.resilience import CircuitBreaker, RateLimiter, RetryConfig, retry_with_backoff
from .core.exceptions import (
    MassiveAPIError,
    MassiveAuthenticationError,
    MassiveValidationError,
    MassiveRateLimitError,
    MassiveNotFoundError,
    MassiveServerError,
    MassiveNetworkError,
    MassiveTimeoutError,
)

logger = logging.getLogger(__name__)


class MassiveRest:
    """
    Thin wrapper around polygon.RESTClient with resilience features.
    
    This class delegates all API calls to the underlying polygon.RESTClient
    while adding rate limiting, circuit breaker, and retry logic.
    """
    
    def __init__(
        self,
        api_key: str,
        rate_limiter: Optional[RateLimiter] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize Massive REST client wrapper.
        
        Args:
            api_key: Massive API key
            rate_limiter: Optional rate limiter instance
            circuit_breaker: Optional circuit breaker instance
            retry_config: Optional retry configuration
        """
        self._client = RESTClient(api_key=api_key)
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
            Appropriate MassiveAPIError subclass
        """
        error_str = str(e).lower()
        
        if "401" in error_str or "unauthorized" in error_str or "authentication" in error_str:
            raise MassiveAuthenticationError(f"Authentication failed: {e}")
        elif "403" in error_str or "forbidden" in error_str:
            raise MassiveAuthenticationError(f"Access forbidden: {e}")
        elif "404" in error_str or "not found" in error_str:
            raise MassiveNotFoundError(f"Resource not found: {e}")
        elif "429" in error_str or "rate limit" in error_str:
            raise MassiveRateLimitError(f"Rate limit exceeded: {e}")
        elif "400" in error_str or "bad request" in error_str or "validation" in error_str:
            raise MassiveValidationError(f"Validation error: {e}")
        elif "500" in error_str or "502" in error_str or "503" in error_str or "server error" in error_str:
            raise MassiveServerError(f"Server error: {e}")
        elif "timeout" in error_str:
            raise MassiveTimeoutError(f"Request timeout: {e}")
        elif "network" in error_str or "connection" in error_str:
            raise MassiveNetworkError(f"Network error: {e}")
        else:
            raise MassiveAPIError(f"API error: {e}")
    
    # Delegate all polygon.RESTClient methods with resilience
    
    def list_aggs(self, *args, **kwargs):
        """Get aggregate bars for a ticker"""
        try:
            return self._with_resilience(self._client.list_aggs, *args, **kwargs)
        except Exception as e:
            self._handle_exception(e)
            raise
    
    def get_aggs(self, *args, **kwargs):
        """Get aggregate bars for a ticker (alternative method)"""
        try:
            return self._with_resilience(self._client.get_aggs, *args, **kwargs)
        except Exception as e:
            self._handle_exception(e)
            raise
    
    def get_ticker_details(self, *args, **kwargs):
        """Get ticker details"""
        try:
            return self._with_resilience(self._client.get_ticker_details, *args, **kwargs)
        except Exception as e:
            self._handle_exception(e)
            raise
    
    def get_ticker_news(self, *args, **kwargs):
        """Get ticker news"""
        try:
            return self._with_resilience(self._client.get_ticker_news, *args, **kwargs)
        except Exception as e:
            self._handle_exception(e)
            raise
    
    def list_tickers(self, *args, **kwargs):
        """List all tickers"""
        try:
            return self._with_resilience(self._client.list_tickers, *args, **kwargs)
        except Exception as e:
            self._handle_exception(e)
            raise
    
    def __getattr__(self, name: str):
        """
        Delegate any other methods to the underlying client.
        This allows access to all polygon.RESTClient methods without
        explicitly defining each one.
        """
        if hasattr(self._client, name):
            attr = getattr(self._client, name)
            if callable(attr):
                def wrapper(*args, **kwargs):
                    try:
                        return self._with_resilience(attr, *args, **kwargs)
                    except Exception as e:
                        self._handle_exception(e)
                        raise
                return wrapper
            return attr
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

