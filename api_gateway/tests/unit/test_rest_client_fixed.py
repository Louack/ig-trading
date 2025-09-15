"""
Unit tests for IG Trading API REST client.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import httpx
from api_gateway.ig_client.rest import IGRest
from api_gateway.ig_client.core.exceptions import (
    IGAPIError,
    IGAuthenticationError,
    IGValidationError,
    IGRateLimitError,
    IGNotFoundError,
    IGServerError,
    IGNetworkError,
    IGTimeoutError,
)


class TestIGRest:
    """Test cases for IGRest class."""

    @pytest.fixture
    def mock_auth_session(self):
        """Mock authentication session."""
        session = Mock()
        session.get_headers.return_value = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-IG-API-KEY": "test-api-key",
            "Authorization": "Bearer test-token",
        }
        return session

    @pytest.fixture
    def rest_client(self, mock_auth_session):
        """Create IGRest client instance."""
        with patch("httpx.Client") as mock_client:
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance
            client = IGRest("https://demo-api.ig.com", mock_auth_session)
            client.client = mock_client_instance
            return client

    @pytest.mark.unit
    def test_rest_client_initialization(self, mock_auth_session):
        """Test REST client initialization."""
        with patch("httpx.Client") as mock_client:
            client = IGRest("https://demo-api.ig.com", mock_auth_session)

            # Verify httpx.Client was called with correct parameters
            mock_client.assert_called_once()
            call_args = mock_client.call_args

            assert call_args[1]["base_url"] == "https://demo-api.ig.com"
            assert call_args[1]["headers"] == mock_auth_session.get_headers.return_value
            assert call_args[1]["timeout"] == 30.0

    @pytest.mark.unit
    def test_get_request_success(self, rest_client):
        """Test successful GET request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_response.content = b'{"success": true}'
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        result = rest_client.get("/accounts", "1")

        # Verify request was made correctly
        rest_client.client.request.assert_called_once()
        call_args = rest_client.client.request.call_args

        assert call_args[1]["method"] == "GET"
        assert call_args[1]["url"] == "/accounts"
        assert call_args[1]["headers"]["VERSION"] == "1"

        assert result == {"success": True}

    @pytest.mark.unit
    def test_post_request_success(self, rest_client):
        """Test successful POST request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"created": True}
        mock_response.content = b'{"created": true}'
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        data = {"name": "Test Watchlist"}
        result = rest_client.post("/watchlists", "1", data=data)

        # Verify request was made correctly
        rest_client.client.request.assert_called_once()
        call_args = rest_client.client.request.call_args

        assert call_args[1]["method"] == "POST"
        assert call_args[1]["url"] == "/watchlists"
        assert call_args[1]["headers"]["VERSION"] == "1"
        assert call_args[1]["json"] == data

        assert result == {"created": True}

    @pytest.mark.unit
    def test_put_request_success(self, rest_client):
        """Test successful PUT request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"updated": True}
        mock_response.content = b'{"updated": true}'
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        data = {"trailingStopsEnabled": True}
        result = rest_client.put("/accounts/preferences", "1", data=data)

        # Verify request was made correctly
        rest_client.client.request.assert_called_once()
        call_args = rest_client.client.request.call_args

        assert call_args[1]["method"] == "PUT"
        assert call_args[1]["url"] == "/accounts/preferences"
        assert call_args[1]["headers"]["VERSION"] == "1"
        assert call_args[1]["json"] == data

        assert result == {"updated": True}

    @pytest.mark.unit
    def test_delete_request_success(self, rest_client):
        """Test successful DELETE request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"deleted": True}
        mock_response.content = b'{"deleted": true}'
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        result = rest_client.delete("/watchlists/123", "1")

        # Verify request was made correctly
        rest_client.client.request.assert_called_once()
        call_args = rest_client.client.request.call_args

        assert call_args[1]["method"] == "DELETE"
        assert call_args[1]["url"] == "/watchlists/123"
        assert call_args[1]["headers"]["VERSION"] == "1"

        assert result == {"deleted": True}

    @pytest.mark.unit
    def test_request_with_query_params(self, rest_client):
        """Test request with query parameters."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_response.content = b'{"data": []}'
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        params = {"pageSize": 10, "pageNumber": 1}
        result = rest_client.get("/accounts", "1", params=params)

        # Verify request was made with query params
        rest_client.client.request.assert_called_once()
        call_args = rest_client.client.request.call_args

        assert call_args[1]["method"] == "GET"
        assert call_args[1]["url"] == "/accounts"
        assert call_args[1]["params"] == params

        assert result == {"data": []}

    @pytest.mark.unit
    def test_authentication_error_401(self, rest_client):
        """Test handling of 401 authentication error."""
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "errorCode": "error.security.invalid-session"
        }
        mock_response.content = b'{"errorCode": "error.security.invalid-session"}'
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        with pytest.raises(IGAuthenticationError) as exc_info:
            rest_client.get("/accounts", "1")

        assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.unit
    def test_validation_error_400(self, rest_client):
        """Test handling of 400 validation error."""
        # Mock 400 response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "errorCode": "validation.error",
            "errorMessage": "Invalid request parameters",
        }
        mock_response.content = b'{"errorCode": "validation.error", "errorMessage": "Invalid request parameters"}'
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        with pytest.raises(IGValidationError) as exc_info:
            rest_client.get("/accounts", "1")

        assert "Invalid request parameters" in str(exc_info.value)

    @pytest.mark.unit
    def test_rate_limit_error_429(self, rest_client):
        """Test handling of 429 rate limit error."""
        # Mock 429 response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"errorCode": "error.rate.limit.exceeded"}
        mock_response.content = b'{"errorCode": "error.rate.limit.exceeded"}'
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        with pytest.raises(IGRateLimitError) as exc_info:
            rest_client.get("/accounts", "1")

        assert "Rate limit exceeded" in str(exc_info.value)

    @pytest.mark.unit
    def test_not_found_error_404(self, rest_client):
        """Test handling of 404 not found error."""
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"errorCode": "error.not.found"}
        mock_response.content = b'{"errorCode": "error.not.found"}'
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        with pytest.raises(IGNotFoundError) as exc_info:
            rest_client.get("/accounts", "1")

        assert "Resource not found" in str(exc_info.value)

    @pytest.mark.unit
    def test_server_error_500(self, rest_client):
        """Test handling of 500 server error."""
        # Mock 500 response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"errorCode": "error.server.internal"}
        mock_response.content = b'{"errorCode": "error.server.internal"}'
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        with pytest.raises(IGServerError) as exc_info:
            rest_client.get("/accounts", "1")

        assert "Server error" in str(exc_info.value)

    @pytest.mark.unit
    def test_network_error(self, rest_client):
        """Test handling of network errors."""
        # Mock network error
        rest_client.client.request.side_effect = httpx.ConnectError("Connection failed")

        with pytest.raises(IGNetworkError) as exc_info:
            rest_client.get("/accounts", "1")

        assert "Network error" in str(exc_info.value)

    @pytest.mark.unit
    def test_timeout_error(self, rest_client):
        """Test handling of timeout errors."""
        # Mock timeout error
        rest_client.client.request.side_effect = httpx.TimeoutException(
            "Request timeout"
        )

        with pytest.raises(IGTimeoutError) as exc_info:
            rest_client.get("/accounts", "1")

        assert "Request timeout" in str(exc_info.value)

    @pytest.mark.unit
    def test_generic_http_error(self, rest_client):
        """Test handling of generic HTTP errors."""
        # Mock generic HTTP error
        mock_response = Mock()
        mock_response.status_code = 418  # I'm a teapot
        mock_response.json.return_value = {"errorCode": "error.unknown"}
        mock_response.content = b'{"errorCode": "error.unknown"}'
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        with pytest.raises(IGAPIError) as exc_info:
            rest_client.get("/accounts", "1")

        assert "HTTP 418" in str(exc_info.value)

    @pytest.mark.unit
    def test_json_decode_error(self, rest_client):
        """Test handling of JSON decode errors."""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.content = b"invalid json"
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        with pytest.raises(IGAPIError) as exc_info:
            rest_client.get("/accounts", "1")

        assert "Failed to parse JSON response" in str(exc_info.value)

    @pytest.mark.unit
    def test_request_exception(self, rest_client):
        """Test handling of general request exceptions."""
        # Mock general exception
        rest_client.client.request.side_effect = Exception("Unexpected error")

        with pytest.raises(IGAPIError) as exc_info:
            rest_client.get("/accounts", "1")

        assert "Unexpected error" in str(exc_info.value)

    @pytest.mark.unit
    def test_endpoint_versioning(self, rest_client):
        """Test that endpoints are properly versioned."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_response.content = b'{"success": true}'
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        # Test different versions
        rest_client.get("/accounts", "1")
        rest_client.get("/accounts", "2")
        rest_client.get("/accounts", "3")

        # Verify all calls were made with correct versioning
        calls = rest_client.client.request.call_args_list
        assert len(calls) == 3

        # Check that all calls use the correct versioning
        for i, call in enumerate(calls):
            args, kwargs = call
            assert kwargs["method"] == "GET"
            assert kwargs["url"] == "/accounts"
            assert kwargs["headers"]["VERSION"] == str(i + 1)

    @pytest.mark.unit
    def test_request_headers(self, rest_client):
        """Test that request headers are properly set."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_response.content = b'{"success": true}'
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        rest_client.get("/accounts", "1")

        # Verify headers were set correctly
        call_args = rest_client.client.request.call_args
        headers = call_args[1]["headers"]

        assert "VERSION" in headers
        assert headers["VERSION"] == "1"

    @pytest.mark.unit
    def test_empty_response_handling(self, rest_client):
        """Test handling of empty responses."""
        # Mock empty response
        mock_response = Mock()
        mock_response.status_code = 204  # No Content
        mock_response.json.side_effect = ValueError("No JSON content")
        mock_response.content = b""
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        # Should handle empty responses gracefully
        result = rest_client.get("/accounts", "1")
        assert result is None

    @pytest.mark.unit
    def test_large_response_handling(self, rest_client):
        """Test handling of large responses."""
        # Mock large response
        large_data = {"items": [{"id": i} for i in range(1000)]}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = large_data
        mock_response.content = b'{"items": [{"id": 0}]}'  # Simplified for testing
        mock_response.headers = {"X-Request-ID": "test-123"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        rest_client.client.request.return_value = mock_response

        result = rest_client.get("/accounts", "1")
        assert result == large_data
        assert len(result["items"]) == 1000
