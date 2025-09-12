"""
IG Trading API Exception Hierarchy

This module defines a comprehensive set of exceptions for handling
various error scenarios when interacting with the IG Trading API.
"""

from typing import Optional, Dict, Any
from enum import Enum


class IGErrorType(Enum):
    """Enumeration of IG API error types"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    RATE_LIMIT = "rate_limit"
    NOT_FOUND = "not_found"
    SERVER_ERROR = "server_error"
    NETWORK = "network"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class IGAPIError(Exception):
    """
    Base exception for all IG Trading API errors.
    
    Attributes:
        message: Human-readable error message
        error_type: Type of error (from IGErrorType enum)
        status_code: HTTP status code if applicable
        error_code: IG-specific error code if available
        details: Additional error details
        request_id: Request identifier for tracing
    """
    
    def __init__(
        self,
        message: str,
        error_type: IGErrorType = IGErrorType.UNKNOWN,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        self.request_id = request_id
        super().__init__(self.message)
    
    def __str__(self) -> str:
        base_msg = f"IG API Error ({self.error_type.value}): {self.message}"
        if self.status_code:
            base_msg += f" [HTTP {self.status_code}]"
        if self.error_code:
            base_msg += f" [Code: {self.error_code}]"
        if self.request_id:
            base_msg += f" [Request ID: {self.request_id}]"
        return base_msg


class IGAuthenticationError(IGAPIError):
    """Raised when authentication fails or session expires"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, IGErrorType.AUTHENTICATION, **kwargs)


class IGAuthorizationError(IGAPIError):
    """Raised when the user lacks permission for the requested operation"""
    
    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(message, IGErrorType.AUTHORIZATION, **kwargs)


class IGValidationError(IGAPIError):
    """Raised when request validation fails"""
    
    def __init__(self, message: str = "Request validation failed", **kwargs):
        super().__init__(message, IGErrorType.VALIDATION, **kwargs)


class IGRateLimitError(IGAPIError):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, IGErrorType.RATE_LIMIT, **kwargs)


class IGNotFoundError(IGAPIError):
    """Raised when requested resource is not found"""
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, IGErrorType.NOT_FOUND, **kwargs)


class IGServerError(IGAPIError):
    """Raised when server returns 5xx error"""
    
    def __init__(self, message: str = "Server error", **kwargs):
        super().__init__(message, IGErrorType.SERVER_ERROR, **kwargs)


class IGNetworkError(IGAPIError):
    """Raised when network-related errors occur"""
    
    def __init__(self, message: str = "Network error", **kwargs):
        super().__init__(message, IGErrorType.NETWORK, **kwargs)


class IGTimeoutError(IGAPIError):
    """Raised when request times out"""
    
    def __init__(self, message: str = "Request timeout", **kwargs):
        super().__init__(message, IGErrorType.TIMEOUT, **kwargs)