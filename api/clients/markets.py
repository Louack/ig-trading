from typing import Dict, Any

from api.rest import IGRest
from core.models.markets.ig_responses import (
    MarketsResponse,
    SingleMarketDetails,
    HistoricalPricesResponse,
    SimpleHistoricalPricesResponse,
)


class MarketsClient:
    def __init__(self, rest: IGRest):
        self.rest = rest

    def get_markets(self, epics: str, filter_type: str = "ALL") -> Dict[str, Any]:
        params = {"epics": epics, "filter": filter_type}
        json = self.rest.get(endpoint="/markets", version="2", params=params)
        response = MarketsResponse(**json)
        return response.model_dump()

    def get_market(self, epic: str) -> Dict[str, Any]:
        json = self.rest.get(endpoint=f"/markets/{epic}", version="4")
        response = SingleMarketDetails(**json)
        return response.model_dump()

    def get_prices(
        self, epic: str, query_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        if query_params is None:
            query_params = {}
        json = self.rest.get(
            endpoint=f"/prices/{epic}", version="3", params=query_params
        )
        response = HistoricalPricesResponse(**json)
        return response.model_dump()

    def get_prices_by_points(
        self, epic: str, resolution: str, num_points: int
    ) -> Dict[str, Any]:
        json = self.rest.get(
            endpoint=f"/prices/{epic}/{resolution}/{num_points}", version="2"
        )
        response = SimpleHistoricalPricesResponse(**json)
        return response.model_dump()

    def get_prices_by_date_range(
        self, epic: str, resolution: str, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        json = self.rest.get(
            endpoint=f"/prices/{epic}/{resolution}/{start_date}/{end_date}", version="2"
        )
        response = SimpleHistoricalPricesResponse(**json)
        return response.model_dump()
