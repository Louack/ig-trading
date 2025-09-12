from typing import Dict, Any

from api.rest import IGRest
from core.models.dealing.ig_responses import (
    Positions,
    Position,
    CreateOtcPositionResponse,
    DealConfirmation,
    CloseOtcPositionResponse,
    UpdateOtcPositionResponse,
    WorkingOrdersResponse,
    CreateWorkingOrderResponse,
    DeleteWorkingOrderResponse,
    UpdateWorkingOrderResponse,
)
from core.models.dealing.request_bodies import (
    CreateOtcPositionRequest,
    CloseOtcPositionRequest,
    UpdateOtcPositionRequest,
    CreateWorkingOrderRequest,
    UpdateWorkingOrderRequest,
)


class DealingClient:
    def __init__(self, rest: IGRest):
        self.rest = rest

    def get_positions(self) -> Dict[str, Any]:
        """
        GET /positions (version 2)
        Returns all open positions for the active account.
        """
        json = self.rest.get(endpoint="/positions", version="2")
        response = Positions(**json)
        return response.model_dump()

    def get_position(self, deal_id: str) -> Dict[str, Any]:
        """
        GET /positions/{dealId} (version 2)
        Returns an open position for the active account by deal identifier.
        """
        json = self.rest.get(endpoint=f"/positions/{deal_id}", version="2")
        response = Position(**json)
        return response.model_dump()

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

    def update_position_otc(self, deal_id: str, body_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PUT /positions/otc/{dealId} (version 2)
        Updates an OTC position.
        """
        validated_request = UpdateOtcPositionRequest(**body_data)
        json = self.rest.put(
            endpoint=f"/positions/otc/{deal_id}",
            version="2",
            data=validated_request.model_dump(exclude_none=True),
        )
        response = UpdateOtcPositionResponse(**json)
        return response.model_dump()

    def create_working_order_otc(self, body_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /workingorders/otc (version 2)
        Creates an OTC working order.
        """
        validated_request = CreateWorkingOrderRequest(**body_data)
        json = self.rest.post(
            endpoint="/workingorders/otc",
            version="2",
            data=validated_request.model_dump(exclude_none=True),
        )
        response = CreateWorkingOrderResponse(**json)
        return response.model_dump()

    def get_working_orders(self) -> Dict[str, Any]:
        """
        GET /workingorders (version 2)
        Returns all open working orders for the active account.
        """
        json = self.rest.get(endpoint="/workingorders", version="2")
        response = WorkingOrdersResponse(**json)
        return response.model_dump()

    def delete_working_order_otc(self, deal_id: str) -> Dict[str, Any]:
        """
        DELETE /workingorders/otc/{dealId} (version 2)
        Deletes an OTC working order.
        """
        json = self.rest.delete(endpoint=f"/workingorders/otc/{deal_id}", version="2")
        response = DeleteWorkingOrderResponse(**json)
        return response.model_dump()

    def update_working_order_otc(self, deal_id: str, body_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PUT /workingorders/otc/{dealId} (version 2)
        Updates an OTC working order.
        """
        validated_request = UpdateWorkingOrderRequest(**body_data)
        json = self.rest.put(
            endpoint=f"/workingorders/otc/{deal_id}",
            version="2",
            data=validated_request.model_dump(exclude_none=True),
        )
        response = UpdateWorkingOrderResponse(**json)
        return response.model_dump()
