from typing import Dict, Any
from api.rest import IGRest
from core.models.account.ig_responses import Accounts


class AccountsClient:
    def __init__(self, rest: IGRest):
        self.rest = rest

    def get_accounts(self) -> Dict[str, Any]:
        """
        GET /accounts (version 1)
        Returns a list of the logged-in client's accounts.
        """
        json = self.rest.get(endpoint="/accounts", version="1")
        response = Accounts(**json)
        return response.model_dump()
