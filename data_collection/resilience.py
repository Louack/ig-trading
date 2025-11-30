"""
Resilience utilities: circuit breakers, rate limiting, retries
"""

import logging
import time
import random
from typing import Optional, Callable, Any
from datetime import datetime, timedelta
from collections import deque
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"      # Failing, reject requests
    HALF_OPEN = "HALF_OPEN"  # Testing if recovered


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(
        self, 
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to track
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self) -> None:
        """Handle successful call"""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker recovered, now CLOSED")
    
    def _on_failure(self) -> None:
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker opened after {self.failure_count} failures"
            )
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def reset(self) -> None:
        """Manually reset circuit breaker"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
        logger.info("Circuit breaker manually reset")
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open"""
        return self.state == CircuitState.OPEN


class RateLimiter:
    """Rate limiter using token bucket algorithm"""
    
    def __init__(self, max_calls: int, period_seconds: int):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum number of calls allowed in period
            period_seconds: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls = deque()
    
    def acquire(self) -> None:
        """
        Acquire permission to make a call, blocking if necessary
        """
        now = time.time()
        
        # Remove calls outside the current window
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()
        
        # If at limit, wait until oldest call expires
        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0]) + 0.1
            logger.debug(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
            # Recursively try again
            self.acquire()
            return
        
        # Record this call
        self.calls.append(time.time())
    
    def try_acquire(self) -> bool:
        """
        Try to acquire permission without blocking
        
        Returns:
            True if acquired, False if rate limited
        """
        now = time.time()
        
        # Remove calls outside the current window
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()
        
        # Check if we're at limit
        if len(self.calls) >= self.max_calls:
            return False
        
        # Record this call
        self.calls.append(time.time())
        return True
    
    def get_remaining_calls(self) -> int:
        """Get number of remaining calls in current window"""
        now = time.time()
        
        # Remove calls outside the current window
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()
        
        return max(0, self.max_calls - len(self.calls))


def exponential_backoff_with_jitter(
    attempt: int, 
    base_delay: float = 1.0, 
    max_delay: float = 60.0,
    jitter: bool = True
) -> float:
    """
    Calculate exponential backoff delay with optional jitter
    
    Args:
        attempt: Attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Whether to add random jitter
        
    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    
    if jitter:
        # Add jitter: random value between 0 and delay
        delay = delay * random.uniform(0, 1)
    
    return delay


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential: bool = True,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential = exponential
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Get delay for a given attempt"""
        if self.exponential:
            return exponential_backoff_with_jitter(
                attempt, 
                self.base_delay, 
                self.max_delay, 
                self.jitter
            )
        else:
            delay = self.base_delay
            if self.jitter:
                delay = delay * random.uniform(0.5, 1.5)
            return delay


def retry_with_backoff(
    func: Callable,
    retry_config: RetryConfig,
    *args,
    **kwargs
) -> Any:
    """
    Retry function with exponential backoff
    
    Args:
        func: Function to retry
        retry_config: Retry configuration
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries failed
    """
    last_exception = None
    
    for attempt in range(retry_config.max_attempts):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            if attempt < retry_config.max_attempts - 1:
                delay = retry_config.get_delay(attempt)
                logger.warning(
                    f"Attempt {attempt + 1}/{retry_config.max_attempts} failed: {e}. "
                    f"Retrying in {delay:.2f}s..."
                )
                time.sleep(delay)
            else:
                logger.error(
                    f"All {retry_config.max_attempts} attempts failed. Last error: {e}"
                )
    
    raise last_exception

