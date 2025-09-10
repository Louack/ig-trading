from api.rest import IGRest
from core.models.account.ig_responses import Accounts


class AccountsClient:
    def __init__(self, rest: IGRest):
        self.rest = rest

    def get_accounts(self) -> Accounts:
        json = self.rest.get(endpoint="/accounts", version="1")
        return Accounts(**json)
