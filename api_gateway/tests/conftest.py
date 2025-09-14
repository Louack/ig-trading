"""
Pytest configuration and shared fixtures for IG Trading API tests.
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any
import json


@pytest.fixture
def mock_ig_client():
    """Mock IGClient for unit tests."""
    client = Mock()
    client.accounts = Mock()
    client.dealing = Mock()
    client.markets = Mock()
    client.watchlists = Mock()
    return client


@pytest.fixture
def sample_accounts_response():
    """Sample accounts API response."""
    return {
        "accounts": [
            {
                "accountId": "ABC123",
                "accountName": "Test Account",
                "accountType": "CFD",
                "preferred": True,
                "balance": {
                    "balance": 1000.0,
                    "deposit": 1000.0,
                    "profitLoss": 0.0,
                    "available": 1000.0
                }
            }
        ]
    }


@pytest.fixture
def sample_positions_response():
    """Sample positions API response."""
    return {
        "positions": [
            {
                "position": {
                    "dealId": "DIAAAAUZTYEFZAH",
                    "epic": "IX.D.NASDAQ.IFE.IP",
                    "size": 1.0,
                    "direction": "BUY",
                    "level": 24000.0,
                    "currency": "EUR"
                }
            }
        ]
    }


@pytest.fixture
def sample_markets_response():
    """Sample markets API response."""
    return {
        "markets": [
            {
                "epic": "IX.D.NASDAQ.IFE.IP",
                "instrumentName": "US Tech 100",
                "instrumentType": "INDICES",
                "marketStatus": "TRADEABLE",
                "bid": 24000.0,
                "offer": 24010.0
            }
        ]
    }


@pytest.fixture
def sample_watchlists_response():
    """Sample watchlists API response."""
    return {
        "watchlists": [
            {
                "id": "123",
                "name": "My Watchlist",
                "defaultSystemWatchlist": False,
                "epics": ["IX.D.NASDAQ.IFE.IP"]
            }
        ]
    }


@pytest.fixture
def sample_error_response():
    """Sample error API response."""
    return {
        "errorCode": "validation.error",
        "errorMessage": "Invalid request parameters"
    }


@pytest.fixture
def mock_httpx_response():
    """Mock httpx response for testing."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"success": True}
    response.text = '{"success": true}'
    return response


@pytest.fixture
def mock_auth_session():
    """Mock authentication session."""
    session = Mock()
    session.get_headers.return_value = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-IG-API-KEY": "test-api-key",
        "Authorization": "Bearer test-token"
    }
    session.is_authenticated.return_value = True
    return session


@pytest.fixture
def valid_epic():
    """Valid epic for testing."""
    return "IX.D.NASDAQ.IFE.IP"


@pytest.fixture
def valid_deal_id():
    """Valid deal ID for testing."""
    return "DIAAAAUZTYEFZAH"


@pytest.fixture
def valid_date():
    """Valid date string for testing."""
    return "01-01-2024"


@pytest.fixture
def invalid_epic():
    """Invalid epic for testing."""
    return "INVALID"


@pytest.fixture
def invalid_deal_id():
    """Invalid deal ID for testing."""
    return ""


@pytest.fixture
def invalid_date():
    """Invalid date string for testing."""
    return "2024-01-01"


# Test data for parametrized tests
@pytest.fixture
def valid_epics():
    """List of valid epics for parametrized testing."""
    return [
        "IX.D.NASDAQ.IFE.IP",
        "CS.D.EURGBP.CFD.IP",
        "CS.D.GBPUSD.CFD.IP",
        "IX.D.FTSE.IFE.IP"
    ]


@pytest.fixture
def invalid_epics():
    """List of invalid epics for parametrized testing."""
    return [
        "INVALID",
        "TOOSHORT",
        "THIS_EPIC_IS_WAY_TOO_LONG_AND_EXCEEDS_THE_MAXIMUM_LENGTH",
        "invalid@epic",
        "epic with spaces"
    ]


@pytest.fixture
def valid_resolutions():
    """List of valid price resolutions."""
    return [
        "SECOND",
        "MINUTE",
        "MINUTE_2",
        "MINUTE_3",
        "MINUTE_5",
        "MINUTE_10",
        "MINUTE_15",
        "MINUTE_30",
        "HOUR",
        "HOUR_2",
        "HOUR_3",
        "HOUR_4",
        "DAY",
        "WEEK",
        "MONTH"
    ]


@pytest.fixture
def invalid_resolutions():
    """List of invalid price resolutions."""
    return [
        "INVALID",
        "MINUTE_1",
        "HOUR_1",
        "YEAR",
        "DECADE"
    ]
