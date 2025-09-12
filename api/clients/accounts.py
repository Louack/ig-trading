import logging
from typing import Dict, Any
from pydantic import ValidationError

from api.rest import IGRest
from api.error_handling import handle_api_errors, handle_validation_errors, handle_response_parsing
from core.models.account.ig_responses import (
    Accounts, AccountPreferences, UpdatePreferencesResponse, ActivitiesResponse, 
    ActivitiesByDateRangeResponse, TransactionsResponse
)
from core.models.account.request_bodies import UpdateAccountPreferencesRequest
from core.models.account.query_params import TransactionHistoryQueryParams
from core.validators import PathValidators
from core.exceptions import IGValidationError

logger = logging.getLogger(__name__)


class AccountsClient:
    def __init__(self, rest: IGRest):
        self.rest = rest

    @handle_api_errors("get_accounts")
    @handle_response_parsing("get_accounts")
    def get_accounts(self) -> Dict[str, Any]:
        json = self.rest.get(endpoint="/accounts", version="1")
        response = Accounts(**json)
        return response.model_dump()

    @handle_api_errors("get_preferences")
    @handle_response_parsing("get_preferences")
    def get_preferences(self) -> Dict[str, Any]:
        json = self.rest.get(endpoint="/accounts/preferences", version="1")
        response = AccountPreferences(**json)
        return response.model_dump()

    @handle_api_errors("update_preferences")
    @handle_validation_errors("update_preferences")
    @handle_response_parsing("update_preferences")
    def update_preferences(self, body_data: Dict[str, Any]) -> Dict[str, Any]:
        validated_request = UpdateAccountPreferencesRequest(**body_data)
        
        json = self.rest.put(
            endpoint="/accounts/preferences",
            version="1",
            data=validated_request.model_dump(exclude_none=True),
        )
        response = UpdatePreferencesResponse(**json)
        return response.model_dump()

    @handle_api_errors("get_activities")
    @handle_response_parsing("get_activities")
    def get_activities(self, query_params: Dict[str, Any] = None) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        
        if query_params is None:
            query_params = {}
        
        if 'from' not in query_params:
            seven_days_ago = datetime.now() - timedelta(days=7)
            query_params['from'] = seven_days_ago.strftime('%Y-%m-%dT%H:%M:%S')
            
        json = self.rest.get(endpoint="/history/activity", version="3", params=query_params)
        response = ActivitiesResponse(**json)
        return response.model_dump()

    @handle_api_errors("get_activities_by_date_range")
    @handle_response_parsing("get_activities_by_date_range")
    def get_activities_by_date_range(self, from_date: str, to_date: str) -> Dict[str, Any]:
        # Validate path parameters
        PathValidators.validate_date_format(from_date)
        PathValidators.validate_date_format(to_date)
        
        json = self.rest.get(endpoint=f"/history/activity/{from_date}/{to_date}", version="1")
        response = ActivitiesByDateRangeResponse(**json)
        return response.model_dump()

    @handle_api_errors("get_transactions")
    @handle_validation_errors("get_transactions")
    @handle_response_parsing("get_transactions")
    def get_transactions(self, query_params: Dict[str, Any] = None) -> Dict[str, Any]:
        if query_params is None:
            query_params = {}
        
        validated_params = TransactionHistoryQueryParams(**query_params)
        params_dict = validated_params.model_dump(by_alias=True, exclude_none=True)
        
        json = self.rest.get(endpoint="/history/transactions", version="2", params=params_dict)
        response = TransactionsResponse(**json)
        return response.model_dump()
