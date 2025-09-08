from api.auth import IGAuthenticator
from api.rest import IGRest
from core.models import Accounts


class IGClient:
    def __init__(self, base_url: str, api_key: str, identifier: str, password: str):
        self.auth_session = IGAuthenticator(
            base_url=base_url, api_key=api_key, identifier=identifier, password=password
        )
        self.rest = IGRest(base_url=base_url, auth_session=self.auth_session)

    def get_accounts(self) -> Accounts:
        json = self.rest.get(endpoint="/accounts", version="1")
        return Accounts(**json)
