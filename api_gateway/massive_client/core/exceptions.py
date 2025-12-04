"""
Massive API Exception Hierarchy

This module defines exceptions for handling errors when interacting
with the Massive (Polygon.io) API.
"""

from typing import Optional, Dict, Any
from enum import Enum


class MassiveErrorType(Enum):
    """Enumeration of Massive API error types"""

    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    RATE_LIMIT = "rate_limit"
    NOT_FOUND = "not_found"
    SERVER_ERROR = "server_error"
    NETWORK = "network"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class MassiveAPIError(Exception):
    """
    Base exception for all Massive API errors.

    Attributes:
        message: Human-readable error message
        error_type: Type of error (from MassiveErrorType enum)
        status_code: HTTP status code if applicable
        error_code: Massive-specific error code if available
        details: Additional error details
    """

    def __init__(
        self,
        message: str,
        error_type: MassiveErrorType = MassiveErrorType.UNKNOWN,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        base_msg = f"Massive API Error ({self.error_type.value}): {self.message}"
        if self.status_code:
            base_msg += f" [HTTP {self.status_code}]"
        if self.error_code:
            base_msg += f" [Code: {self.error_code}]"
        return base_msg


class MassiveAuthenticationError(MassiveAPIError):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, MassiveErrorType.AUTHENTICATION, **kwargs)


class MassiveValidationError(MassiveAPIError):
    """Raised when request validation fails"""

    def __init__(self, message: str = "Request validation failed", **kwargs):
        super().__init__(message, MassiveErrorType.VALIDATION, **kwargs)


class MassiveRateLimitError(MassiveAPIError):
    """Raised when rate limit is exceeded"""

    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, MassiveErrorType.RATE_LIMIT, **kwargs)


class MassiveNotFoundError(MassiveAPIError):
    """Raised when requested resource is not found"""

    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, MassiveErrorType.NOT_FOUND, **kwargs)


class MassiveServerError(MassiveAPIError):
    """Raised when server returns 5xx error"""

    def __init__(self, message: str = "Server error", **kwargs):
        super().__init__(message, MassiveErrorType.SERVER_ERROR, **kwargs)


class MassiveNetworkError(MassiveAPIError):
    """Raised when network-related errors occur"""

    def __init__(self, message: str = "Network error", **kwargs):
        super().__init__(message, MassiveErrorType.NETWORK, **kwargs)


class MassiveTimeoutError(MassiveAPIError):
    """Raised when request times out"""

    def __init__(self, message: str = "Request timeout", **kwargs):
        super().__init__(message, MassiveErrorType.TIMEOUT, **kwargs)

