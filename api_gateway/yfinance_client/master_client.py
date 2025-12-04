"""
YFinance API Master Client

Main client interface for YFinance API.
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from common.resilience import RateLimiter, CircuitBreaker, RetryConfig

from .rest import YFinanceRest


class YFinanceClient:
    """
    Master client for YFinance API.

    Provides a unified interface to the YFinance API with resilience features.
    """

    def __init__(
        self,
        rate_limiter: Optional["RateLimiter"] = None,
        circuit_breaker: Optional["CircuitBreaker"] = None,
        retry_config: Optional["RetryConfig"] = None,
    ):
        """
        Initialize YFinance client.

        Args:
            rate_limiter: Optional rate limiter instance
            circuit_breaker: Optional circuit breaker instance
            retry_config: Optional retry configuration
        """
        self.rest = YFinanceRest(
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker,
            retry_config=retry_config,
        )
