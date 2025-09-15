"""
Unit tests for IG Trading API authentication module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import httpx
from api_gateway.ig_client.auth import IGAuthenticator
from api_gateway.ig_client.core.exceptions import IGAuthenticationError


class TestIGAuthenticator:
    """Test cases for IGAuthenticator class."""

    @pytest.fixture
    def authenticator(self):
        """Create IGAuthenticator instance for testing."""
        return IGAuthenticator(
            base_url="https://demo-api.ig.com",
            api_key="test-api-key",
            identifier="test-user",
            password="test-password",
        )

    @pytest.mark.unit
    def test_authenticator_initialization(self):
        """Test authenticator initialization."""
        auth = IGAuthenticator(
            base_url="https://demo-api.ig.com",
            api_key="test-api-key",
            identifier="test-user",
            password="test-password",
        )

        assert auth.base_url == "https://demo-api.ig.com"
        assert auth.api_key == "test-api-key"
        assert auth.identifier == "test-user"
        assert auth.password == "test-password"
        assert auth.tokens == {}

    @pytest.mark.unit
    @patch("httpx.Client")
    def test_login_success(self, mock_client_class, authenticator):
        """Test successful login."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "CST": "test-cst-token",
            "X-SECURITY-TOKEN": "test-security-token",
        }

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = authenticator.login()

        # Verify the request was made correctly
        mock_client.post.assert_called_once_with(
            "/session", json={"identifier": "test-user", "password": "test-password"}
        )

        # Verify tokens were stored correctly
        expected_tokens = {
            "X-IG-API-KEY": "test-api-key",
            "CST": "test-cst-token",
            "X-SECURITY-TOKEN": "test-security-token",
        }
        assert authenticator.tokens == expected_tokens
        assert result == expected_tokens

    @pytest.mark.unit
    @patch("httpx.Client")
    def test_login_failure_401(self, mock_client_class, authenticator):
        """Test login failure with 401 status."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid credentials"

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        with pytest.raises(IGAuthenticationError) as exc_info:
            authenticator.login()

        assert "Invalid credentials" in str(exc_info.value)
        assert authenticator.tokens == {}

    @pytest.mark.unit
    @patch("httpx.Client")
    def test_login_failure_400(self, mock_client_class, authenticator):
        """Test login failure with 400 status."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        with pytest.raises(IGAuthenticationError) as exc_info:
            authenticator.login()

        assert "Bad request" in str(exc_info.value)

    @pytest.mark.unit
    @patch("httpx.Client")
    def test_login_failure_500(self, mock_client_class, authenticator):
        """Test login failure with 500 status."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        with pytest.raises(IGAuthenticationError) as exc_info:
            authenticator.login()

        assert "Internal server error" in str(exc_info.value)

    @pytest.mark.unit
    @patch("httpx.Client")
    def test_login_network_error(self, mock_client_class, authenticator):
        """Test login with network error."""
        # Mock network error
        mock_client = Mock()
        mock_client.post.side_effect = httpx.ConnectError("Connection failed")
        mock_client_class.return_value.__enter__.return_value = mock_client

        with pytest.raises(httpx.ConnectError):
            authenticator.login()

    @pytest.mark.unit
    @patch("httpx.Client")
    def test_login_timeout_error(self, mock_client_class, authenticator):
        """Test login with timeout error."""
        # Mock timeout error
        mock_client = Mock()
        mock_client.post.side_effect = httpx.TimeoutException("Request timeout")
        mock_client_class.return_value.__enter__.return_value = mock_client

        with pytest.raises(httpx.TimeoutException):
            authenticator.login()

    @pytest.mark.unit
    @patch("httpx.Client")
    def test_login_missing_headers(self, mock_client_class, authenticator):
        """Test login with missing security headers."""
        # Mock response without security headers
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}  # No CST or X-SECURITY-TOKEN

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = authenticator.login()

        # Should still work but with None values for missing headers
        expected_tokens = {
            "X-IG-API-KEY": "test-api-key",
            "CST": None,
            "X-SECURITY-TOKEN": None,
        }
        assert authenticator.tokens == expected_tokens
        assert result == expected_tokens

    @pytest.mark.unit
    def test_get_headers_with_existing_tokens(self, authenticator):
        """Test get_headers when tokens already exist."""
        # Set up existing tokens
        authenticator.tokens = {
            "X-IG-API-KEY": "test-api-key",
            "CST": "test-cst-token",
            "X-SECURITY-TOKEN": "test-security-token",
        }

        result = authenticator.get_headers()

        assert result == authenticator.tokens
        # Should not call login again

    @pytest.mark.unit
    @patch.object(IGAuthenticator, "login")
    def test_get_headers_without_tokens(self, mock_login, authenticator):
        """Test get_headers when no tokens exist."""
        # Mock login to return tokens
        mock_tokens = {
            "X-IG-API-KEY": "test-api-key",
            "CST": "test-cst-token",
            "X-SECURITY-TOKEN": "test-security-token",
        }
        mock_login.return_value = mock_tokens

        result = authenticator.get_headers()

        # Should call login and return the tokens
        mock_login.assert_called_once()
        assert result == mock_tokens

    @pytest.mark.unit
    @patch("httpx.Client")
    def test_login_request_headers(self, mock_client_class, authenticator):
        """Test that login request includes correct headers."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "CST": "test-cst-token",
            "X-SECURITY-TOKEN": "test-security-token",
        }

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        authenticator.login()

        # Verify httpx.Client was initialized with correct headers
        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args

        assert call_args[1]["base_url"] == "https://demo-api.ig.com"
        assert call_args[1]["headers"] == {
            "X-IG-API-KEY": "test-api-key",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @pytest.mark.unit
    @patch("httpx.Client")
    def test_login_request_body(self, mock_client_class, authenticator):
        """Test that login request includes correct body."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "CST": "test-cst-token",
            "X-SECURITY-TOKEN": "test-security-token",
        }

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        authenticator.login()

        # Verify the request body
        mock_client.post.assert_called_once_with(
            "/session", json={"identifier": "test-user", "password": "test-password"}
        )

    @pytest.mark.unit
    @patch("httpx.Client")
    def test_login_with_different_credentials(self, mock_client_class):
        """Test login with different credential combinations."""
        # Test with different credentials
        auth = IGAuthenticator(
            base_url="https://live-api.ig.com",
            api_key="live-api-key",
            identifier="live-user",
            password="live-password",
        )

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "CST": "live-cst-token",
            "X-SECURITY-TOKEN": "live-security-token",
        }

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = auth.login()

        # Verify the request was made with correct credentials
        mock_client.post.assert_called_once_with(
            "/session", json={"identifier": "live-user", "password": "live-password"}
        )

        # Verify tokens were stored correctly
        expected_tokens = {
            "X-IG-API-KEY": "live-api-key",
            "CST": "live-cst-token",
            "X-SECURITY-TOKEN": "live-security-token",
        }
        assert result == expected_tokens

    @pytest.mark.unit
    def test_authenticator_attributes(self, authenticator):
        """Test that authenticator attributes are properly set."""
        assert hasattr(authenticator, "base_url")
        assert hasattr(authenticator, "api_key")
        assert hasattr(authenticator, "identifier")
        assert hasattr(authenticator, "password")
        assert hasattr(authenticator, "tokens")
        assert hasattr(authenticator, "login")
        assert hasattr(authenticator, "get_headers")

    @pytest.mark.unit
    @patch("httpx.Client")
    def test_login_multiple_calls(self, mock_client_class, authenticator):
        """Test multiple login calls."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "CST": "test-cst-token",
            "X-SECURITY-TOKEN": "test-security-token",
        }

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Call login multiple times
        result1 = authenticator.login()
        result2 = authenticator.login()

        # Should make multiple requests
        assert mock_client.post.call_count == 2
        assert result1 == result2

    @pytest.mark.unit
    @patch("httpx.Client")
    def test_login_with_special_characters_in_credentials(self, mock_client_class):
        """Test login with special characters in credentials."""
        auth = IGAuthenticator(
            base_url="https://demo-api.ig.com",
            api_key="test-api-key-with-special-chars!@#",
            identifier="user@domain.com",
            password="password with spaces and !@#$%",
        )

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "CST": "test-cst-token",
            "X-SECURITY-TOKEN": "test-security-token",
        }

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = auth.login()

        # Verify the request was made with special characters preserved
        mock_client.post.assert_called_once_with(
            "/session",
            json={
                "identifier": "user@domain.com",
                "password": "password with spaces and !@#$%",
            },
        )

        # Verify API key with special characters is preserved
        assert result["X-IG-API-KEY"] == "test-api-key-with-special-chars!@#"
