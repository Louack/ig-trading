from api.auth import IGAuthenticator
from api.rest import IGRest
from core.models.account.ig_responses import Accounts
from core.models.dealing.ig_responses import Positions, Position, CreateOtcPositionResponse
from core.models.dealing.request_bodies import CreateOtcPositionRequest
from typing import Dict, Any


class IGClient:
    def __init__(self, base_url: str, api_key: str, identifier: str, password: str):
        self.auth_session = IGAuthenticator(
            base_url=base_url, api_key=api_key, identifier=identifier, password=password
        )
        self.rest = IGRest(base_url=base_url, auth_session=self.auth_session)

    def get_accounts(self) -> Accounts:
        json = self.rest.get(endpoint="/accounts", version="1")
        return Accounts(**json)

    def get_positions(self) -> Positions:
        json = self.rest.get(endpoint="/positions", version="2")
        print(json)
        return Positions(**json)

    def get_position(self, deal_id: str) -> Position:
        json = self.rest.get(endpoint=f"/positions/{deal_id}", version="2")
        print(json)
        return Position(**json)

    def create_position_otc(self, body_data: Dict[str, Any]) -> Dict[str, Any]:
        validated_request = CreateOtcPositionRequest(**body_data)
        json = self.rest.post(endpoint="/positions/otc", version="2", data=validated_request.model_dump(exclude_none=True))
        response = CreateOtcPositionResponse(**json)
        return response.model_dump()
