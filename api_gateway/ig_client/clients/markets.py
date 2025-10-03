from typing import Dict, Any

from api_gateway.ig_client.rest import IGRest
from api_gateway.ig_client.error_handling import (
    handle_api_errors,
    handle_validation_errors,
    handle_response_parsing,
)
from api_gateway.ig_client.core.validators import PathValidators
from api_gateway.ig_client.core.models.markets.ig_responses import (
    Markets,
    SingleMarketDetails,
    HistoricalPrices,
    SimpleHistoricalPrices,
    SearchMarkets,
)
from api_gateway.ig_client.core.models.markets.query_params import (
    GetMarketsQueryParams,
    SearchMarketsQueryParams,
    GetPricesQueryParams,
)


class MarketsClient:
    def __init__(self, rest: IGRest):
        self.rest = rest

    @handle_api_errors("get_markets")
    @handle_validation_errors("get_markets")
    @handle_response_parsing("get_markets")
    def get_markets(self, epics: str, filter_type: str = "ALL") -> Markets:
        # Validate query parameters with Pydantic
        query_params = GetMarketsQueryParams(epics=epics, filter=filter_type)
        params = query_params.model_dump(by_alias=True, exclude_none=True)
        
        json = self.rest.get(endpoint="/markets", version="2", params=params)
        return Markets(**json)

    @handle_api_errors("search_markets")
    @handle_validation_errors("search_markets")
    @handle_response_parsing("search_markets")
    def search_markets(self, search_term: str) -> SearchMarkets:
        # Validate query parameters with Pydantic
        query_params = SearchMarketsQueryParams(searchTerm=search_term)
        params = query_params.model_dump(by_alias=True, exclude_none=True)

        json = self.rest.get(endpoint="/markets", version="1", params=params)
        return SearchMarkets(**json)

    @handle_api_errors("get_market")
    @handle_response_parsing("get_market")
    def get_market(self, epic: str) -> SingleMarketDetails:
        PathValidators.validate_epic(epic)
        json = self.rest.get(endpoint=f"/markets/{epic}", version="4")
        return SingleMarketDetails(**json)

    @handle_api_errors("get_prices")
    @handle_validation_errors("get_prices")
    @handle_response_parsing("get_prices")
    def get_prices(
        self, epic: str, query_params: Dict[str, Any] = None
    ) -> HistoricalPrices:
        PathValidators.validate_epic(epic)
        if query_params is None:
            query_params = {}
        validated_params = GetPricesQueryParams(**query_params)
        params = validated_params.model_dump(by_alias=True, exclude_none=True)

        json = self.rest.get(endpoint=f"/prices/{epic}", version="3", params=params)
        return HistoricalPrices(**json)

    @handle_api_errors("get_prices_by_points")
    @handle_validation_errors("get_prices_by_points")
    @handle_response_parsing("get_prices_by_points")
    def get_prices_by_points(
        self, epic: str, resolution: str, num_points: int
    ) -> SimpleHistoricalPrices:
        PathValidators.validate_epic(epic)
        PathValidators.validate_resolution(resolution)
        PathValidators.validate_num_points(num_points)
        json = self.rest.get(
            endpoint=f"/prices/{epic}/{resolution}/{num_points}", version="2"
        )
        return SimpleHistoricalPrices(**json)

    @handle_api_errors("get_prices_by_date_range")
    @handle_validation_errors("get_prices_by_date_range")
    @handle_response_parsing("get_prices_by_date_range")
    def get_prices_by_date_range(
        self, epic: str, resolution: str, start_date: str, end_date: str
    ) -> SimpleHistoricalPrices:
        PathValidators.validate_epic(epic)
        PathValidators.validate_resolution(resolution)
        PathValidators.validate_date_format(start_date)
        PathValidators.validate_date_format(end_date)
        json = self.rest.get(
            endpoint=f"/prices/{epic}/{resolution}/{start_date}/{end_date}", version="2"
        )
        return SimpleHistoricalPrices(**json)
