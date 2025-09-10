from typing import Dict, Any

from api.rest import IGRest
from core.models.dealing.ig_responses import (
    Positions,
    Position,
    CreateOtcPositionResponse,
    DealConfirmation,
    CloseOtcPositionResponse,
)
from core.models.dealing.request_bodies import (
    CreateOtcPositionRequest,
    CloseOtcPositionRequest,
)


class DealingClient:
    def __init__(self, rest: IGRest):
        self.rest = rest

    def get_positions(self) -> Positions:
        json = self.rest.get(endpoint="/positions", version="2")
        return Positions(**json)

    def get_position(self, deal_id: str) -> Position:
        json = self.rest.get(endpoint=f"/positions/{deal_id}", version="2")
        return Position(**json)

    def create_position_otc(self, body_data: Dict[str, Any]) -> Dict[str, Any]:
        validated_request = CreateOtcPositionRequest(**body_data)
        json = self.rest.post(
            endpoint="/positions/otc",
            version="2",
            data=validated_request.model_dump(exclude_none=True),
        )
        response = CreateOtcPositionResponse(**json)
        return response.model_dump()

    def get_deal_confirmation(self, deal_reference: str) -> Dict[str, Any]:
        json = self.rest.get(endpoint=f"/confirms/{deal_reference}", version="1")
        response = DealConfirmation(**json)
        return response.model_dump()

    def close_position_otc(self, body_data: Dict[str, Any]) -> Dict[str, Any]:
        validated_request = CloseOtcPositionRequest(**body_data)
        json = self.rest.delete(
            endpoint="/positions/otc",
            version="1",
            data=validated_request.model_dump(exclude_none=True),
        )
        response = CloseOtcPositionResponse(**json)
        return response.model_dump()
