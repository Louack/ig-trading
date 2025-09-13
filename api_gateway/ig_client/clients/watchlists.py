from typing import Dict, Any
from api_gateway.ig_client.rest import IGRest
from api_gateway.ig_client.error_handling import (
    handle_api_errors,
    handle_validation_errors,
    handle_response_parsing,
)
from api_gateway.ig_client.core.validators import PathValidators
from api_gateway.ig_client.core.models.watchlists.ig_responses import (
    Watchlists,
    CreateWatchlist,
    WatchlistDetails,
    DeleteWatchlist,
    AddMarketToWatchlist,
    RemoveMarketFromWatchlist,
)
from api_gateway.ig_client.core.models.watchlists.request_bodies import (
    CreateWatchlistRequest,
    AddMarketToWatchlistRequest,
)


class WatchlistsClient:
    def __init__(self, rest: IGRest):
        self.rest = rest

    @handle_api_errors("get_watchlists")
    @handle_response_parsing("get_watchlists")
    def get_watchlists(self) -> Watchlists:
        json = self.rest.get(endpoint="/watchlists", version="1")
        return Watchlists(**json)

    @handle_api_errors("create_watchlist")
    @handle_validation_errors("create_watchlist")
    @handle_response_parsing("create_watchlist")
    def create_watchlist(self, body_data: Dict[str, Any]) -> CreateWatchlist:
        validated_request = CreateWatchlistRequest(**body_data)
        json = self.rest.post(
            endpoint="/watchlists",
            version="1",
            data=validated_request.model_dump(exclude_none=True),
        )
        return CreateWatchlist(**json)

    @handle_api_errors("get_watchlist")
    @handle_response_parsing("get_watchlist")
    def get_watchlist(self, watchlist_id: str) -> WatchlistDetails:
        PathValidators.validate_watchlist_id(watchlist_id)

        json = self.rest.get(endpoint=f"/watchlists/{watchlist_id}", version="1")
        return WatchlistDetails(**json)

    @handle_api_errors("delete_watchlist")
    @handle_response_parsing("delete_watchlist")
    def delete_watchlist(self, watchlist_id: str) -> DeleteWatchlist:
        PathValidators.validate_watchlist_id(watchlist_id)

        json = self.rest.delete(endpoint=f"/watchlists/{watchlist_id}", version="1")
        return DeleteWatchlist(**json)

    @handle_api_errors("add_market_to_watchlist")
    @handle_validation_errors("add_market_to_watchlist")
    @handle_response_parsing("add_market_to_watchlist")
    def add_market_to_watchlist(
        self, watchlist_id: str, body_data: Dict[str, Any]
    ) -> AddMarketToWatchlist:
        PathValidators.validate_watchlist_id(watchlist_id)

        validated_request = AddMarketToWatchlistRequest(**body_data)
        json = self.rest.put(
            endpoint=f"/watchlists/{watchlist_id}",
            version="1",
            data=validated_request.model_dump(exclude_none=True),
        )
        return AddMarketToWatchlist(**json)

    @handle_api_errors("remove_market_from_watchlist")
    @handle_response_parsing("remove_market_from_watchlist")
    def remove_market_from_watchlist(
        self, watchlist_id: str, epic: str
    ) -> RemoveMarketFromWatchlist:
        PathValidators.validate_watchlist_id(watchlist_id)
        PathValidators.validate_epic(epic)

        json = self.rest.delete(
            endpoint=f"/watchlists/{watchlist_id}/{epic}", version="1"
        )
        return RemoveMarketFromWatchlist(**json)
