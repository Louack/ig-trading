"""
Unit tests for IG Trading API error handling decorators.
"""

import pytest
from unittest.mock import Mock, patch
from pydantic import ValidationError
from api_gateway.ig_client.error_handling import (
    handle_api_errors,
    handle_validation_errors,
    handle_response_parsing,
)
from api_gateway.ig_client.core.exceptions import (
    IGAPIError,
    IGValidationError,
    IGAuthenticationError,
)


class TestHandleApiErrors:
    """Test cases for handle_api_errors decorator."""

    @pytest.mark.unit
    def test_handle_api_errors_success(self):
        """Test successful function execution."""
        @handle_api_errors("test_operation")
        def test_func():
            return "success"
        
        result = test_func()
        assert result == "success"

    @pytest.mark.unit
    def test_handle_api_errors_with_operation_name(self):
        """Test decorator with custom operation name."""
        @handle_api_errors("custom_operation")
        def test_func():
            return "success"
        
        result = test_func()
        assert result == "success"

    @pytest.mark.unit
    def test_handle_api_errors_without_operation_name(self):
        """Test decorator without operation name (uses function name)."""
        @handle_api_errors()


        def test_operation():
            return "success"
        
        result = test_operation()
        assert result == "success"

    @pytest.mark.unit
    def test_handle_api_errors_validation_error(self):
        """Test handling of ValidationError."""
        @handle_api_errors("test_operation")
        def test_func():
            raise ValidationError.from_exception_data(
                "ValidationError",
                [{"type": "missing", "loc": ("field",), "msg": "Field required"}]
            )
        
        with pytest.raises(IGValidationError) as exc_info:
            test_func()
        
        assert "Invalid test_operation request/response" in str(exc_info.value)

    @pytest.mark.unit
    def test_handle_api_errors_ig_authentication_error(self):
        """Test handling of IGAuthenticationError (should re-raise)."""
        @handle_api_errors("test_operation")
        def test_func():
            raise IGAuthenticationError("Authentication failed")
        
        with pytest.raises(IGAuthenticationError) as exc_info:
            test_func()
        
        assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.unit
    def test_handle_api_errors_ig_validation_error(self):
        """Test handling of IGValidationError (should re-raise)."""
        @handle_api_errors("test_operation")
        def test_func():
            raise IGValidationError("Validation failed")
        
        with pytest.raises(IGValidationError) as exc_info:
            test_func()
        
        assert "Validation failed" in str(exc_info.value)

    @pytest.mark.unit
    def test_handle_api_errors_generic_exception(self):
        """Test handling of generic exceptions."""
        @handle_api_errors("test_operation")
        def test_func():
            raise ValueError("Something went wrong")
        
        with pytest.raises(IGAPIError) as exc_info:
            test_func()
        
        assert "Failed to test_operation" in str(exc_info.value)
        assert "Something went wrong" in str(exc_info.value)

    @pytest.mark.unit
    def test_handle_api_errors_with_args_and_kwargs(self):
        """Test decorator with function that takes arguments."""
        @handle_api_errors("test_operation")
        def test_func(arg1, arg2=None, **kwargs):
            return f"{arg1}-{arg2}-{kwargs.get('extra', 'default')}"
        
        result = test_func("test", arg2="value", extra="data")
        assert result == "test-value-data"

    @pytest.mark.unit
    @patch('api_gateway.ig_client.error_handling.logger')
    def test_handle_api_errors_logging(self, mock_logger):
        """Test that appropriate logging occurs."""
        @handle_api_errors("test_operation")
        def test_func():
            return "success"
        
        test_func()
        
        # Check that debug and info logs were called
        mock_logger.debug.assert_called_with("Starting test_operation")
        mock_logger.info.assert_called_with("Successfully completed test_operation")

    @pytest.mark.unit
    @patch('api_gateway.ig_client.error_handling.logger')
    def test_handle_api_errors_error_logging(self, mock_logger):
        """Test that error logging occurs on exceptions."""
        @handle_api_errors("test_operation")
        def test_func():
            raise ValueError("Test error")
        
        with pytest.raises(IGAPIError):
            test_func()
        
        # Check that error log was called
        mock_logger.error.assert_called()


class TestHandleValidationErrors:
    """Test cases for handle_validation_errors decorator."""

    @pytest.mark.unit
    def test_handle_validation_errors_success(self):
        """Test successful function execution."""
        @handle_validation_errors("test_operation")
        def test_func():
            return "success"
        
        result = test_func()
        assert result == "success"

    @pytest.mark.unit
    def test_handle_validation_errors_validation_error(self):
        """Test handling of ValidationError."""
        @handle_validation_errors("test_operation")
        def test_func():
            raise ValidationError.from_exception_data(
                "ValidationError",
                [{"type": "missing", "loc": ("field",), "msg": "Field required"}]
            )
        
        with pytest.raises(IGValidationError) as exc_info:
            test_func()
        
        assert "Invalid test_operation request" in str(exc_info.value)

    @pytest.mark.unit
    def test_handle_validation_errors_other_exception(self):
        """Test that other exceptions are not caught."""
        @handle_validation_errors("test_operation")
        def test_func():
            raise ValueError("Other error")
        
        with pytest.raises(ValueError) as exc_info:
            test_func()
        
        assert "Other error" in str(exc_info.value)

    @pytest.mark.unit
    @patch('api_gateway.ig_client.error_handling.logger')
    def test_handle_validation_errors_logging(self, mock_logger):
        """Test that validation error logging occurs."""
        @handle_validation_errors("test_operation")
        def test_func():
            raise ValidationError.from_exception_data(
                "ValidationError",
                [{"type": "missing", "loc": ("field",), "msg": "Field required"}]
            )
        
        with pytest.raises(IGValidationError):
            test_func()
        
        # Check that error log was called
        mock_logger.error.assert_called()


class TestHandleResponseParsing:
    """Test cases for handle_response_parsing decorator."""

    @pytest.mark.unit
    def test_handle_response_parsing_success(self):
        """Test successful function execution."""
        @handle_response_parsing("test_operation")
        def test_func():
            return "success"
        
        result = test_func()
        assert result == "success"

    @pytest.mark.unit
    def test_handle_response_parsing_validation_error(self):
        """Test handling of ValidationError for response parsing."""
        @handle_response_parsing("test_operation")
        def test_func():
            raise ValidationError.from_exception_data(
                "ValidationError",
                [{"type": "missing", "loc": ("field",), "msg": "Field required"}]
            )
        
        with pytest.raises(IGValidationError) as exc_info:
            test_func()
        
        assert "Invalid test_operation response format" in str(exc_info.value)

    @pytest.mark.unit
    def test_handle_response_parsing_other_exception(self):
        """Test that other exceptions are not caught."""
        @handle_response_parsing("test_operation")
        def test_func():
            raise ValueError("Other error")
        
        with pytest.raises(ValueError) as exc_info:
            test_func()
        
        assert "Other error" in str(exc_info.value)

    @pytest.mark.unit
    @patch('api_gateway.ig_client.error_handling.logger')
    def test_handle_response_parsing_logging(self, mock_logger):
        """Test that response parsing error logging occurs."""
        @handle_response_parsing("test_operation")
        def test_func():
            raise ValidationError.from_exception_data(
                "ValidationError",
                [{"type": "missing", "loc": ("field",), "msg": "Field required"}]
            )
        
        with pytest.raises(IGValidationError):
            test_func()
        
        # Check that error log was called
        mock_logger.error.assert_called()


class TestDecoratorComposition:
    """Test cases for using multiple decorators together."""

    @pytest.mark.unit
    def test_multiple_decorators_success(self):
        """Test successful execution with multiple decorators."""
        @handle_api_errors("test_operation")
        @handle_validation_errors("test_operation")
        @handle_response_parsing("test_operation")
        def test_func():
            return "success"
        
        result = test_func()
        assert result == "success"

    @pytest.mark.unit
    def test_multiple_decorators_validation_error(self):
        """Test validation error handling with multiple decorators."""
        @handle_api_errors("test_operation")
        @handle_validation_errors("test_operation")
        @handle_response_parsing("test_operation")
        def test_func():
            raise ValidationError.from_exception_data(
                "ValidationError",
                [{"type": "missing", "loc": ("field",), "msg": "Field required"}]
            )
        
        with pytest.raises(IGValidationError) as exc_info:
            test_func()
        
        # The validation error should be caught by the first decorator that handles it
        # In this case, it could be either "request" or "response format" depending on decorator order
        error_message = str(exc_info.value)
        assert ("Invalid test_operation request" in error_message or 
                "Invalid test_operation response format" in error_message)

    @pytest.mark.unit
    def test_multiple_decorators_generic_error(self):
        """Test generic error handling with multiple decorators."""
        @handle_api_errors("test_operation")
        @handle_validation_errors("test_operation")
        @handle_response_parsing("test_operation")
        def test_func():
            raise ValueError("Generic error")
        
        with pytest.raises(IGAPIError) as exc_info:
            test_func()
        
        assert "Failed to test_operation" in str(exc_info.value)

    @pytest.mark.unit
    def test_decorator_preserves_function_metadata(self):
        """Test that decorators preserve function metadata."""
        @handle_api_errors("test_operation")
        def test_func(arg1, arg2=None):
            """Test function docstring."""
            return f"{arg1}-{arg2}"
        
        # Check that function name and docstring are preserved
        assert test_func.__name__ == "test_func"
        assert test_func.__doc__ == "Test function docstring."
        
        # Check that function still works
        result = test_func("test", arg2="value")
        assert result == "test-value"


class TestDecoratorEdgeCases:
    """Test edge cases for error handling decorators."""

    @pytest.mark.unit
    def test_decorator_with_no_operation_name(self):
        """Test decorator behavior when no operation name is provided."""
        @handle_api_errors()
        def some_function():
            raise ValueError("Test error")
        
        with pytest.raises(IGAPIError) as exc_info:
            some_function()
        
        assert "Failed to some_function" in str(exc_info.value)

    @pytest.mark.unit
    def test_decorator_with_none_operation_name(self):
        """Test decorator behavior when operation name is None."""
        @handle_api_errors(None)
        def test_func():
            raise ValueError("Test error")
        
        with pytest.raises(IGAPIError) as exc_info:
            test_func()
        
        assert "Failed to test_func" in str(exc_info.value)

    @pytest.mark.unit
    def test_decorator_with_empty_string_operation_name(self):
        """Test decorator behavior when operation name is empty string."""
        @handle_api_errors("")
        def test_func():
            raise ValueError("Test error")
        
        with pytest.raises(IGAPIError) as exc_info:
            test_func()
        
        assert "Failed to test_func" in str(exc_info.value)
