"""
Rate limiter using token bucket algorithm
"""

import logging
import time
from collections import deque

logger = logging.getLogger(__name__)


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

