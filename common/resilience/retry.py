"""
Retry utilities with exponential backoff
"""

import logging
import time
import random
from typing import Callable, Any

logger = logging.getLogger(__name__)


def exponential_backoff_with_jitter(
    attempt: int, base_delay: float = 1.0, max_delay: float = 60.0, jitter: bool = True
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
    delay = min(base_delay * (2**attempt), max_delay)

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
        jitter: bool = True,
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
                attempt, self.base_delay, self.max_delay, self.jitter
            )
        else:
            delay = self.base_delay
            if self.jitter:
                delay = delay * random.uniform(0.5, 1.5)
            return delay


def retry_with_backoff(
    func: Callable, retry_config: RetryConfig, *args, **kwargs
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
