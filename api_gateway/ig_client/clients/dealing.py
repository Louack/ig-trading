from typing import Dict, Any

from api_gateway.ig_client.rest import IGRest
from api_gateway.ig_client.error_handling import (
    handle_api_errors,
    handle_validation_errors,
    handle_response_parsing,
)
from api_gateway.ig_client.core.validators import PathValidators
from api_gateway.ig_client.core.models.dealing.ig_responses import (
    Positions,
    Position,
    CreateOtcPosition,
    DealConfirmation,
    CloseOtcPosition,
    UpdateOtcPosition,
    WorkingOrders,
    CreateWorkingOrder,
    DeleteWorkingOrder,
    UpdateWorkingOrder,
)
from api_gateway.ig_client.core.models.dealing.request_bodies import (
    CreateOtcPositionRequest,
    CloseOtcPositionRequest,
    UpdateOtcPositionRequest,
    CreateWorkingOrderRequest,
    UpdateWorkingOrderRequest,
)


class DealingClient:
    def __init__(self, rest: IGRest):
        self.rest = rest

    @handle_api_errors("get_positions")
    @handle_response_parsing("get_positions")
    def get_positions(self) -> Positions:
        json = self.rest.get(endpoint="/positions", version="2")
        return Positions(**json)

    @handle_api_errors("get_position")
    @handle_response_parsing("get_position")
    def get_position(self, deal_id: str) -> Position:
        PathValidators.validate_deal_id(deal_id)

        json = self.rest.get(endpoint=f"/positions/{deal_id}", version="2")
        return Position(**json)

    @handle_api_errors("create_position_otc")
    @handle_validation_errors("create_position_otc")
    @handle_response_parsing("create_position_otc")
    def create_position_otc(self, body_data: Dict[str, Any]) -> CreateOtcPosition:
        validated_request = CreateOtcPositionRequest(**body_data)
        json = self.rest.post(
            endpoint="/positions/otc",
            version="2",
            data=validated_request.model_dump(exclude_none=True),
        )
        return CreateOtcPosition(**json)

    @handle_api_errors("get_deal_confirmation")
    @handle_response_parsing("get_deal_confirmation")
    def get_deal_confirmation(self, deal_reference: str) -> DealConfirmation:
        PathValidators.validate_deal_id(deal_reference)

        json = self.rest.get(endpoint=f"/confirms/{deal_reference}", version="1")
        return DealConfirmation(**json)

    @handle_api_errors("close_position_otc")
    @handle_validation_errors("close_position_otc")
    @handle_response_parsing("close_position_otc")
    def close_position_otc(self, body_data: Dict[str, Any]) -> CloseOtcPosition:
        validated_request = CloseOtcPositionRequest(**body_data)
        json = self.rest.delete(
            endpoint="/positions/otc",
            version="1",
            data=validated_request.model_dump(exclude_none=True),
        )
        return CloseOtcPosition(**json)

    @handle_api_errors("update_position_otc")
    @handle_validation_errors("update_position_otc")
    @handle_response_parsing("update_position_otc")
    def update_position_otc(
        self, deal_id: str, body_data: Dict[str, Any]
    ) -> UpdateOtcPosition:
        PathValidators.validate_deal_id(deal_id)

        validated_request = UpdateOtcPositionRequest(**body_data)
        json = self.rest.put(
            endpoint=f"/positions/otc/{deal_id}",
            version="2",
            data=validated_request.model_dump(exclude_none=True),
        )
        return UpdateOtcPosition(**json)

    @handle_api_errors("create_working_order_otc")
    @handle_validation_errors("create_working_order_otc")
    @handle_response_parsing("create_working_order_otc")
    def create_working_order_otc(self, body_data: Dict[str, Any]) -> CreateWorkingOrder:
        validated_request = CreateWorkingOrderRequest(**body_data)
        json = self.rest.post(
            endpoint="/workingorders/otc",
            version="2",
            data=validated_request.model_dump(exclude_none=True),
        )
        return CreateWorkingOrder(**json)

    @handle_api_errors("get_working_orders")
    @handle_response_parsing("get_working_orders")
    def get_working_orders(self) -> WorkingOrders:
        json = self.rest.get(endpoint="/workingorders", version="2")
        return WorkingOrders(**json)

    @handle_api_errors("delete_working_order_otc")
    @handle_response_parsing("delete_working_order_otc")
    def delete_working_order_otc(self, deal_id: str) -> DeleteWorkingOrder:
        PathValidators.validate_deal_id(deal_id)

        json = self.rest.delete(endpoint=f"/workingorders/otc/{deal_id}", version="2")
        return DeleteWorkingOrder(**json)

    @handle_api_errors("update_working_order_otc")
    @handle_validation_errors("update_working_order_otc")
    @handle_response_parsing("update_working_order_otc")
    def update_working_order_otc(
        self, deal_id: str, body_data: Dict[str, Any]
    ) -> UpdateWorkingOrder:
        PathValidators.validate_deal_id(deal_id)

        validated_request = UpdateWorkingOrderRequest(**body_data)
        json = self.rest.put(
            endpoint=f"/workingorders/otc/{deal_id}",
            version="2",
            data=validated_request.model_dump(exclude_none=True),
        )
        return UpdateWorkingOrder(**json)
