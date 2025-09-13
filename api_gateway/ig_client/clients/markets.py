from typing import Dict, Any

from api_gateway.ig_client.rest import IGRest
from api_gateway.ig_client.core.models.markets.ig_responses import (
    Markets,
    SingleMarketDetails,
    HistoricalPrices,
    SimpleHistoricalPrices,
)


class MarketsClient:
    def __init__(self, rest: IGRest):
        self.rest = rest

    def get_markets(self, epics: str, filter_type: str = "ALL") -> Markets:
        params = {"epics": epics, "filter": filter_type}
        json = self.rest.get(endpoint="/markets", version="2", params=params)
        return Markets(**json)

    def get_market(self, epic: str) -> SingleMarketDetails:
        json = self.rest.get(endpoint=f"/markets/{epic}", version="4")
        return SingleMarketDetails(**json)

    def get_prices(
        self, epic: str, query_params: Dict[str, Any] = None
    ) -> HistoricalPrices:
        if query_params is None:
            query_params = {}
        json = self.rest.get(
            endpoint=f"/prices/{epic}", version="3", params=query_params
        )
        return HistoricalPrices(**json)

    def get_prices_by_points(
        self, epic: str, resolution: str, num_points: int
    ) -> SimpleHistoricalPrices:
        json = self.rest.get(
            endpoint=f"/prices/{epic}/{resolution}/{num_points}", version="2"
        )
        return SimpleHistoricalPrices(**json)

    def get_prices_by_date_range(
        self, epic: str, resolution: str, start_date: str, end_date: str
    ) -> SimpleHistoricalPrices:
        json = self.rest.get(
            endpoint=f"/prices/{epic}/{resolution}/{start_date}/{end_date}", version="2"
        )
        return SimpleHistoricalPrices(**json)
