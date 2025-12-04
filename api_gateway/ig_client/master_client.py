from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from common.resilience import RateLimiter

from api_gateway.ig_client.auth import IGAuthenticator
from api_gateway.ig_client.clients import (
    AccountsClient,
    DealingClient,
    MarketsClient,
    WatchlistsClient,
)
from api_gateway.ig_client.rest import IGRest


class IGClient:
    def __init__(
        self, 
        base_url: str, 
        api_key: str, 
        identifier: str, 
        password: str,
        rate_limiter: Optional['RateLimiter'] = None
    ):
        """
        Initialize IG client.
        
        Args:
            base_url: Base URL for IG API
            api_key: API key
            identifier: User identifier
            password: User password
            rate_limiter: Optional rate limiter instance (from common.resilience)
        """
        self.auth_session = IGAuthenticator(
            base_url=base_url, api_key=api_key, identifier=identifier, password=password
        )
        self.rest = IGRest(
            base_url=base_url, 
            auth_session=self.auth_session,
            rate_limiter=rate_limiter
        )
        self.accounts = AccountsClient(rest=self.rest)
        self.markets = MarketsClient(rest=self.rest)
        self.dealing = DealingClient(rest=self.rest)
        self.watchlists = WatchlistsClient(rest=self.rest)
