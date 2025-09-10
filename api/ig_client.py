from api.auth import IGAuthenticator
from api.rest import IGRest
from core.models.account.ig_responses import Accounts
from core.models.dealing.ig_responses import Positions, Position, CreateOtcPositionResponse, DealConfirmation, CloseOtcPositionResponse
from core.models.dealing.request_bodies import CreateOtcPositionRequest, CloseOtcPositionRequest
from core.models.markets.ig_responses import MarketsResponse, SingleMarketDetails, HistoricalPricesResponse, SimpleHistoricalPricesResponse
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

    def get_deal_confirmation(self, deal_reference: str) -> Dict[str, Any]:
        json = self.rest.get(endpoint=f"/confirms/{deal_reference}", version="1")
        response = DealConfirmation(**json)
        return response.model_dump()

    def get_markets(self, epics: str, filter_type: str = "ALL") -> Dict[str, Any]:
        params = {"epics": epics, "filter": filter_type}
        json = self.rest.get(endpoint="/markets", version="2", params=params)
        response = MarketsResponse(**json)
        return response.model_dump()

    def get_market(self, epic: str) -> Dict[str, Any]:
        json = self.rest.get(endpoint=f"/markets/{epic}", version="4")
        response = SingleMarketDetails(**json)
        return response.model_dump()

    def get_prices(self, epic: str, query_params: Dict[str, Any] = None) -> Dict[str, Any]:
        if query_params is None:
            query_params = {}
        json = self.rest.get(endpoint=f"/prices/{epic}", version="3", params=query_params)
        response = HistoricalPricesResponse(**json)
        return response.model_dump()

    def get_prices_by_points(self, epic: str, resolution: str, num_points: int) -> Dict[str, Any]:
        json = self.rest.get(endpoint=f"/prices/{epic}/{resolution}/{num_points}", version="2")
        response = SimpleHistoricalPricesResponse(**json)
        return response.model_dump()

    def get_prices_by_date_range(self, epic: str, resolution: str, start_date: str, end_date: str) -> Dict[str, Any]:
        json = self.rest.get(endpoint=f"/prices/{epic}/{resolution}/{start_date}/{end_date}", version="2")
        response = SimpleHistoricalPricesResponse(**json)
        return response.model_dump()

    def close_position_otc(self, body_data: Dict[str, Any]) -> Dict[str, Any]:
        validated_request = CloseOtcPositionRequest(**body_data)
        json = self.rest.delete(endpoint="/positions/otc", version="1", data=validated_request.model_dump(exclude_none=True))
        response = CloseOtcPositionResponse(**json)
        return response.model_dump()
