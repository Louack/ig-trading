from typing import Dict, Any

from api.rest import IGRest
from api.error_handling import handle_api_errors, handle_validation_errors, handle_response_parsing
from core.validators import PathValidators
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

    @handle_api_errors("get_positions")
    @handle_response_parsing("get_positions")
    def get_positions(self) -> Dict[str, Any]:
        json = self.rest.get(endpoint="/positions", version="2")
        response = Positions(**json)
        return response.model_dump()

    @handle_api_errors("get_position")
    @handle_response_parsing("get_position")
    def get_position(self, deal_id: str) -> Dict[str, Any]:
        PathValidators.validate_deal_id(deal_id)
        
        json = self.rest.get(endpoint=f"/positions/{deal_id}", version="2")
        response = Position(**json)
        return response.model_dump()

    @handle_api_errors("create_position_otc")
    @handle_validation_errors("create_position_otc")
    @handle_response_parsing("create_position_otc")
    def create_position_otc(self, body_data: Dict[str, Any]) -> Dict[str, Any]:
        validated_request = CreateOtcPositionRequest(**body_data)
        json = self.rest.post(
            endpoint="/positions/otc",
            version="2",
            data=validated_request.model_dump(exclude_none=True),
        )
        response = CreateOtcPositionResponse(**json)
        return response.model_dump()

    @handle_api_errors("get_deal_confirmation")
    @handle_response_parsing("get_deal_confirmation")
    def get_deal_confirmation(self, deal_reference: str) -> Dict[str, Any]:
        PathValidators.validate_deal_id(deal_reference)
        
        json = self.rest.get(endpoint=f"/confirms/{deal_reference}", version="1")
        response = DealConfirmation(**json)
        return response.model_dump()

    @handle_api_errors("close_position_otc")
    @handle_validation_errors("close_position_otc")
    @handle_response_parsing("close_position_otc")
    def close_position_otc(self, body_data: Dict[str, Any]) -> Dict[str, Any]:
        validated_request = CloseOtcPositionRequest(**body_data)
        json = self.rest.delete(
            endpoint="/positions/otc",
            version="1",
            data=validated_request.model_dump(exclude_none=True),
        )
        response = CloseOtcPositionResponse(**json)
        return response.model_dump()

    @handle_api_errors("update_position_otc")
    @handle_validation_errors("update_position_otc")
    @handle_response_parsing("update_position_otc")
    def update_position_otc(self, deal_id: str, body_data: Dict[str, Any]) -> Dict[str, Any]:
        PathValidators.validate_deal_id(deal_id)
        
        validated_request = UpdateOtcPositionRequest(**body_data)
        json = self.rest.put(
            endpoint=f"/positions/otc/{deal_id}",
            version="2",
            data=validated_request.model_dump(exclude_none=True),
        )
        response = UpdateOtcPositionResponse(**json)
        return response.model_dump()

    @handle_api_errors("create_working_order_otc")
    @handle_validation_errors("create_working_order_otc")
    @handle_response_parsing("create_working_order_otc")
    def create_working_order_otc(self, body_data: Dict[str, Any]) -> Dict[str, Any]:
        validated_request = CreateWorkingOrderRequest(**body_data)
        json = self.rest.post(
            endpoint="/workingorders/otc",
            version="2",
            data=validated_request.model_dump(exclude_none=True),
        )
        response = CreateWorkingOrderResponse(**json)
        return response.model_dump()

    @handle_api_errors("get_working_orders")
    @handle_response_parsing("get_working_orders")
    def get_working_orders(self) -> Dict[str, Any]:
        json = self.rest.get(endpoint="/workingorders", version="2")
        response = WorkingOrdersResponse(**json)
        return response.model_dump()

    @handle_api_errors("delete_working_order_otc")
    @handle_response_parsing("delete_working_order_otc")
    def delete_working_order_otc(self, deal_id: str) -> Dict[str, Any]:
        PathValidators.validate_deal_id(deal_id)
        
        json = self.rest.delete(endpoint=f"/workingorders/otc/{deal_id}", version="2")
        response = DeleteWorkingOrderResponse(**json)
        return response.model_dump()

    @handle_api_errors("update_working_order_otc")
    @handle_validation_errors("update_working_order_otc")
    @handle_response_parsing("update_working_order_otc")
    def update_working_order_otc(self, deal_id: str, body_data: Dict[str, Any]) -> Dict[str, Any]:
        PathValidators.validate_deal_id(deal_id)
        
        validated_request = UpdateWorkingOrderRequest(**body_data)
        json = self.rest.put(
            endpoint=f"/workingorders/otc/{deal_id}",
            version="2",
            data=validated_request.model_dump(exclude_none=True),
        )
        response = UpdateWorkingOrderResponse(**json)
        return response.model_dump()