from typing import List, Literal, Optional
from decimal import Decimal
from pydantic import BaseModel, field_serializer


class Watchlist(BaseModel):
    defaultSystemWatchlist: bool
    deleteable: bool
    editable: bool
    id: str
    name: str


class WatchlistsResponse(BaseModel):
    watchlists: List[Watchlist]


# Instrument types for watchlist markets
InstrumentType = Literal[
    "BINARY", "BUNGEE_CAPPED", "BUNGEE_COMMODITIES", "BUNGEE_CURRENCIES", 
    "BUNGEE_INDICES", "COMMODITIES", "CURRENCIES", "INDICES", 
    "KNOCKOUTS_COMMODITIES", "KNOCKOUTS_CURRENCIES", "KNOCKOUTS_INDICES", 
    "KNOCKOUTS_SHARES", "OPT_COMMODITIES", "OPT_CURRENCIES", "OPT_INDICES", 
    "OPT_RATES", "OPT_SHARES", "RATES", "SECTORS", "SHARES", 
    "SPRINT_MARKET", "TEST_MARKET", "UNKNOWN"
]


# Market status for watchlist markets
MarketStatus = Literal[
    "CLOSED", "EDITS_ONLY", "OFFLINE", "ON_AUCTION", 
    "ON_AUCTION_NO_EDITS", "SUSPENDED", "TRADEABLE"
]


class WatchlistMarket(BaseModel):
    bid: Optional[Decimal] = None
    delayTime: Optional[int] = None
    epic: str
    expiry: Optional[str] = None
    high: Optional[Decimal] = None
    instrumentName: str
    instrumentType: InstrumentType
    lotSize: Optional[Decimal] = None
    low: Optional[Decimal] = None
    marketStatus: Optional[MarketStatus] = None
    netChange: Optional[Decimal] = None
    offer: Optional[Decimal] = None
    percentageChange: Optional[Decimal] = None
    scalingFactor: Optional[Decimal] = None
    streamingPricesAvailable: Optional[bool] = None
    updateTime: Optional[str] = None
    updateTimeUTC: Optional[str] = None

    @field_serializer('bid', 'high', 'lotSize', 'low', 'netChange', 'offer', 
                     'percentageChange', 'scalingFactor')
    def serialize_decimal(self, value):
        return float(value) if value is not None else None


class WatchlistDetailsResponse(BaseModel):
    markets: List[WatchlistMarket]


# Response statuses
WatchlistOperationStatus = Literal["SUCCESS"]


class DeleteWatchlistResponse(BaseModel):
    status: WatchlistOperationStatus


class AddMarketToWatchlistResponse(BaseModel):
    status: WatchlistOperationStatus


class RemoveMarketFromWatchlistResponse(BaseModel):
    status: WatchlistOperationStatus


# Response status for create watchlist
CreateWatchlistStatus = Literal[
    "SUCCESS",
    "SUCCESS_NOT_ALL_INSTRUMENTS_ADDED"
]


class CreateWatchlistResponse(BaseModel):
    status: CreateWatchlistStatus
    watchlistId: Optional[str] = None
