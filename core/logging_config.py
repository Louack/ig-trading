"""
Logging configuration for IG Trading API client.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    include_request_id: bool = True
) -> None:
    """
    Setup logging configuration for the IG Trading API client.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
        include_request_id: Whether to include request ID in log format
    """
    
    if format_string is None:
        if include_request_id:
            format_string = (
                "%(asctime)s - %(name)s - %(levelname)s - "
                "%(funcName)s:%(lineno)d - %(message)s"
            )
        else:
            format_string = (
                "%(asctime)s - %(name)s - %(levelname)s - "
                "%(funcName)s:%(lineno)d - %(message)s"
            )
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Set our API client loggers to the specified level
    api_loggers = [
        "api.rest",
        "api.clients.accounts",
        "api.clients.dealing", 
        "api.clients.markets",
        "api.clients.watchlists"
    ]
    
    for logger_name in api_loggers:
        logging.getLogger(logger_name).setLevel(getattr(logging, level.upper()))


class ErrorTracker:
    """
    Simple error tracking for monitoring and alerting.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_counts = {}
        self.total_errors = 0
    
    def track_error(self, error: Exception, context: dict = None):
        """Track and log errors for monitoring"""
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.total_errors += 1
        
        # Log structured error information
        self.logger.error(
            f"Error tracked: {error_type}",
            extra={
                "error_type": error_type,
                "error_message": str(error),
                "error_count": self.error_counts[error_type],
                "total_errors": self.total_errors,
                "context": context or {}
            }
        )
        
        # Alert on critical errors
        if error_type in ["IGAuthenticationError", "IGServerError"]:
            self._send_alert(error, context)
    
    def _send_alert(self, error: Exception, context: dict):
        """Send alerts for critical errors"""
        self.logger.critical(
            f"CRITICAL ERROR ALERT: {type(error).__name__}",
            extra={
                "error": str(error),
                "context": context or {}
            }
        )
    
    def get_error_summary(self) -> dict:
        """Get summary of error counts"""
        return {
            "total_errors": self.total_errors,
            "error_counts": self.error_counts
        }


# Global error tracker instance
error_tracker = ErrorTracker()
