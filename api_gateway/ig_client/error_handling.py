"""
DRY error handling decorators for API client methods.
"""

import logging
from functools import wraps
from typing import Callable, Type, Tuple, Any
from pydantic import ValidationError

from api_gateway.ig_client.core.exceptions import (
    IGAPIError,
    IGValidationError,
    IGNotFoundError,
    IGAuthenticationError,
)

logger = logging.getLogger(__name__)


def handle_api_errors(operation_name: str = None):
    """
    Decorator to handle common API errors.

    Args:
        operation_name: Name of the operation for logging (defaults to function name)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__

            try:
                logger.debug(f"Starting {op_name}")
                result = func(*args, **kwargs)
                logger.info(f"Successfully completed {op_name}")
                return result

            except ValidationError as e:
                logger.error(f"Validation error in {op_name}: {e}")
                raise IGValidationError(f"Invalid {op_name} request/response: {str(e)}")

            except IGAuthenticationError:
                logger.error(f"Authentication failed in {op_name}")
                raise

            except IGValidationError:
                # Re-raise validation errors as-is
                raise

            except Exception as e:
                logger.error(f"Unexpected error in {op_name}: {e}")
                raise IGAPIError(f"Failed to {op_name}: {str(e)}")

        return wrapper

    return decorator


def handle_validation_errors(operation_name: str = None):
    """
    Decorator specifically for handling validation errors.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__

            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                logger.error(f"Validation error in {op_name}: {e}")
                raise IGValidationError(f"Invalid {op_name} request: {str(e)}")

        return wrapper

    return decorator


def handle_response_parsing(operation_name: str = None):
    """
    Decorator for handling response parsing errors.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__

            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                logger.error(f"Response parsing error in {op_name}: {e}")
                raise IGValidationError(f"Invalid {op_name} response format: {str(e)}")

        return wrapper

    return decorator
