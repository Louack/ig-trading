from typing import Dict, Any
from api.rest import IGRest
from core.models.watchlists.ig_responses import (
    WatchlistsResponse, CreateWatchlistResponse, WatchlistDetailsResponse,
    DeleteWatchlistResponse, AddMarketToWatchlistResponse, RemoveMarketFromWatchlistResponse
)
from core.models.watchlists.request_bodies import (
    CreateWatchlistRequest, AddMarketToWatchlistRequest
)


class WatchlistsClient:
    def __init__(self, rest: IGRest):
        self.rest = rest

    def get_watchlists(self) -> Dict[str, Any]:
        """
        GET /watchlists (version 1)
        Returns all watchlists belonging to the active account.
        """
        json = self.rest.get(endpoint="/watchlists", version="1")
        response = WatchlistsResponse(**json)
        return response.model_dump()

    def create_watchlist(self, body_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /watchlists (version 1)
        Creates a watchlist.
        """
        validated_request = CreateWatchlistRequest(**body_data)
        json = self.rest.post(
            endpoint="/watchlists",
            version="1",
            data=validated_request.model_dump(exclude_none=True),
        )
        response = CreateWatchlistResponse(**json)
        return response.model_dump()

    def get_watchlist(self, watchlist_id: str) -> Dict[str, Any]:
        """
        GET /watchlists/{watchlistId} (version 1)
        Returns a watchlist.
        """
        json = self.rest.get(endpoint=f"/watchlists/{watchlist_id}", version="1")
        response = WatchlistDetailsResponse(**json)
        return response.model_dump()

    def delete_watchlist(self, watchlist_id: str) -> Dict[str, Any]:
        """
        DELETE /watchlists/{watchlistId} (version 1)
        Deletes a watchlist.
        """
        json = self.rest.delete(endpoint=f"/watchlists/{watchlist_id}", version="1")
        response = DeleteWatchlistResponse(**json)
        return response.model_dump()

    def add_market_to_watchlist(self, watchlist_id: str, body_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PUT /watchlists/{watchlistId} (version 1)
        Add a market to a watchlist.
        """
        validated_request = AddMarketToWatchlistRequest(**body_data)
        json = self.rest.put(
            endpoint=f"/watchlists/{watchlist_id}",
            version="1",
            data=validated_request.model_dump(exclude_none=True),
        )
        response = AddMarketToWatchlistResponse(**json)
        return response.model_dump()

    def remove_market_from_watchlist(self, watchlist_id: str, epic: str) -> Dict[str, Any]:
        """
        DELETE /watchlists/{watchlistId}/{epic} (version 1)
        Remove a market from a watchlist.
        """
        json = self.rest.delete(endpoint=f"/watchlists/{watchlist_id}/{epic}", version="1")
        response = RemoveMarketFromWatchlistResponse(**json)
        return response.model_dump()
