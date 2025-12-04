"""
YFinance API Exception Hierarchy

This module defines exceptions for handling errors when interacting
with the YFinance API.
"""

from typing import Optional, Dict, Any
from enum import Enum


class YFinanceErrorType(Enum):
    """Enumeration of YFinance API error types"""

    VALIDATION = "validation"
    RATE_LIMIT = "rate_limit"
    NOT_FOUND = "not_found"
    SERVER_ERROR = "server_error"
    NETWORK = "network"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class YFinanceAPIError(Exception):
    """
    Base exception for all YFinance API errors.

    Attributes:
        message: Human-readable error message
        error_type: Type of error (from YFinanceErrorType enum)
        details: Additional error details
    """

    def __init__(
        self,
        message: str,
        error_type: YFinanceErrorType = YFinanceErrorType.UNKNOWN,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        base_msg = f"YFinance API Error ({self.error_type.value}): {self.message}"
        return base_msg


class YFinanceValidationError(YFinanceAPIError):
    """Raised when request validation fails"""

    def __init__(self, message: str = "Request validation failed", **kwargs):
        super().__init__(message, YFinanceErrorType.VALIDATION, **kwargs)


class YFinanceRateLimitError(YFinanceAPIError):
    """Raised when rate limit is exceeded"""

    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, YFinanceErrorType.RATE_LIMIT, **kwargs)


class YFinanceNotFoundError(YFinanceAPIError):
    """Raised when requested resource is not found"""

    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, YFinanceErrorType.NOT_FOUND, **kwargs)


class YFinanceServerError(YFinanceAPIError):
    """Raised when server returns error"""

    def __init__(self, message: str = "Server error", **kwargs):
        super().__init__(message, YFinanceErrorType.SERVER_ERROR, **kwargs)


class YFinanceNetworkError(YFinanceAPIError):
    """Raised when network-related errors occur"""

    def __init__(self, message: str = "Network error", **kwargs):
        super().__init__(message, YFinanceErrorType.NETWORK, **kwargs)


class YFinanceTimeoutError(YFinanceAPIError):
    """Raised when request times out"""

    def __init__(self, message: str = "Request timeout", **kwargs):
        super().__init__(message, YFinanceErrorType.TIMEOUT, **kwargs)


