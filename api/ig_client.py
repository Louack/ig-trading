from api.auth import IGAuthenticator
from api.clients.accounts import AccountsClient
from api.clients.dealing import DealingClient
from api.clients.markets import MarketsClient
from api.rest import IGRest


class IGClient:
    def __init__(self, base_url: str, api_key: str, identifier: str, password: str):
        self.auth_session = IGAuthenticator(
            base_url=base_url, api_key=api_key, identifier=identifier, password=password
        )
        self.rest = IGRest(base_url=base_url, auth_session=self.auth_session)
        self.accounts = AccountsClient(rest=self.rest)
        self.markets = MarketsClient(rest=self.rest)
        self.dealing = DealingClient(rest=self.rest)
