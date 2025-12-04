"""
Massive API Master Client

Main client interface for Massive API, similar to IGClient.
"""

from typing import Optional

from common.resilience import CircuitBreaker, RateLimiter, RetryConfig
from .rest import MassiveRest


class MassiveClient:
    """
    Master client for Massive API.
    
    Provides a unified interface to the Massive API with resilience features.
    """
    
    def __init__(
        self,
        api_key: str,
        rate_limiter: Optional[RateLimiter] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize Massive client.
        
        Args:
            api_key: Massive API key
            rate_limiter: Optional rate limiter instance
            circuit_breaker: Optional circuit breaker instance
            retry_config: Optional retry configuration
        """
        self.rest = MassiveRest(
            api_key=api_key,
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker,
            retry_config=retry_config,
        )

