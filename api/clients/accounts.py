from typing import Dict, Any
from api.rest import IGRest
from core.models.account.ig_responses import (
    Accounts, AccountPreferences, UpdatePreferencesResponse, ActivitiesResponse, ActivitiesByDateRangeResponse, TransactionsResponse
)
from core.models.account.request_bodies import UpdateAccountPreferencesRequest
from core.models.account.query_params import TransactionHistoryQueryParams


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

    def get_preferences(self) -> Dict[str, Any]:
        """
        GET /accounts/preferences (version 1)
        Returns account preferences.
        """
        json = self.rest.get(endpoint="/accounts/preferences", version="1")
        response = AccountPreferences(**json)
        return response.model_dump()

    def update_preferences(self, body_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PUT /accounts/preferences (version 1)
        Updates account preferences.
        """
        validated_request = UpdateAccountPreferencesRequest(**body_data)
        json = self.rest.put(
            endpoint="/accounts/preferences",
            version="1",
            data=validated_request.model_dump(exclude_none=True),
        )
        response = UpdatePreferencesResponse(**json)
        return response.model_dump()

    def get_activities(self, query_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        GET /history/activity (version 3)
        Returns the account activity history.
        
        Query parameters:
        - from: Start date (DateTime) - REQUIRED
        - to: End date (DateTime, default = current time)
        - detailed: Retrieve additional details (boolean, default = false)
        - dealId: Deal ID (String)
        - filter: FIQL filter (String)
        - pageSize: Page size (int, default = 50, min: 10, max: 500)
        """
        from datetime import datetime, timedelta
        
        # If no query params provided, create default with required 'from' date
        if query_params is None:
            query_params = {}
        
        # If 'from' is not provided, default to 7 days ago
        if 'from' not in query_params:
            seven_days_ago = datetime.now() - timedelta(days=7)
            query_params['from'] = seven_days_ago.strftime('%Y-%m-%dT%H:%M:%S')
            
        json = self.rest.get(endpoint="/history/activity", version="3", params=query_params)
        response = ActivitiesResponse(**json)
        return response.model_dump()

    def get_activities_by_date_range(self, from_date: str, to_date: str) -> Dict[str, Any]:
        """
        GET /history/activity/{fromDate}/{toDate} (version 1)
        Returns the account activity history for the given date range.
        
        Args:
            from_date: Start date in dd-mm-yyyy format (e.g., "01-01-2024")
            to_date: End date in dd-mm-yyyy format (e.g., "31-12-2024")
        """
        json = self.rest.get(endpoint=f"/history/activity/{from_date}/{to_date}", version="1")
        response = ActivitiesByDateRangeResponse(**json)
        return response.model_dump()

    def get_transactions(self, query_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        GET /history/transactions (version 2)
        Returns the transaction history.
        
        Query parameters:
        - type: Transaction type (ALL, ALL_DEAL, DEPOSIT, WITHDRAWAL, default = ALL)
        - from: Start date (DateTime)
        - to: End date (DateTime)
        - maxSpanSeconds: Limits timespan in seconds (default = 600)
        - pageSize: Page size (default = 20, disable paging = 0)
        - pageNumber: Page number (default = 1)
        """
        # Validate and convert query parameters using Pydantic
        if query_params is None:
            query_params = {}
        
        validated_params = TransactionHistoryQueryParams(**query_params)
        params_dict = validated_params.model_dump(by_alias=True, exclude_none=True)
        
        json = self.rest.get(endpoint="/history/transactions", version="2", params=params_dict)
        response = TransactionsResponse(**json)
        return response.model_dump()
