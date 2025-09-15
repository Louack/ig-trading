from decimal import Decimal
from typing import List, Optional, Literal

from pydantic import BaseModel, field_serializer

# Import instrument and market types from markets
from api_gateway.ig_client.core.models.markets.ig_responses import (
    InstrumentType,
    MarketStatus,
)


# Position specific direction type
PositionDirection = Literal["BUY", "SELL"]


class PositionMarket(BaseModel):
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

    @field_serializer(
        "bid",
        "high",
        "lotSize",
        "low",
        "netChange",
        "offer",
        "percentageChange",
        "scalingFactor",
    )
    def serialize_decimal(self, value):
        return float(value) if value is not None else None


class PositionDetail(BaseModel):
    contractSize: Decimal
    controlledRisk: Optional[bool] = None
    createdDate: Optional[str] = None
    createdDateUTC: Optional[str] = None
    currency: str
    dealId: str
    dealReference: Optional[str] = None
    direction: PositionDirection
    level: Decimal
    limitLevel: Optional[Decimal] = None
    limitedRiskPremium: Optional[Decimal] = None
    size: Decimal
    stopLevel: Optional[Decimal] = None
    trailingStep: Optional[Decimal] = None
    trailingStopDistance: Optional[Decimal] = None

    @field_serializer(
        "contractSize",
        "level",
        "limitLevel",
        "limitedRiskPremium",
        "size",
        "stopLevel",
        "trailingStep",
        "trailingStopDistance",
    )
    def serialize_decimal(self, value):
        return float(value) if value is not None else None


class Position(BaseModel):
    position: PositionDetail
    market: PositionMarket


class Positions(BaseModel):
    positions: List[Position]


class PendingDeal(BaseModel):
    dealReference: str


# Deal Confirmation Enums
AffectedDealStatus = Literal[
    "AMENDED", "DELETED", "FULLY_CLOSED", "OPENED", "PARTIALLY_CLOSED"
]
DealStatus = Literal["ACCEPTED", "REJECTED"]
Direction = Literal["BUY", "SELL"]
Reason = Literal[
    "ACCOUNT_NOT_ENABLED_TO_TRADING",
    "ATTACHED_ORDER_LEVEL_ERROR",
    "ATTACHED_ORDER_TRAILING_STOP_ERROR",
    "CANNOT_CHANGE_STOP_TYPE",
    "CANNOT_REMOVE_STOP",
    "CLOSING_ONLY_TRADES_ACCEPTED_ON_THIS_MARKET",
    "CLOSINGS_ONLY_ACCOUNT",
    "CONFLICTING_ORDER",
    "CONTACT_SUPPORT_INSTRUMENT_ERROR",
    "CR_SPACING",
    "DUPLICATE_ORDER_ERROR",
    "EXCHANGE_MANUAL_OVERRIDE",
    "EXPIRY_LESS_THAN_SPRINT_MARKET_MIN_EXPIRY",
    "FINANCE_REPEAT_DEALING",
    "FORCE_OPEN_ON_SAME_MARKET_DIFFERENT_CURRENCY",
    "GENERAL_ERROR",
    "GOOD_TILL_DATE_IN_THE_PAST",
    "INSTRUMENT_NOT_FOUND",
    "INSTRUMENT_NOT_TRADEABLE_IN_THIS_CURRENCY",
    "INSUFFICIENT_FUNDS",
    "LEVEL_TOLERANCE_ERROR",
    "LIMIT_ORDER_WRONG_SIDE_OF_MARKET",
    "MANUAL_ORDER_TIMEOUT",
    "MARGIN_ERROR",
    "MARKET_CLOSED",
    "MARKET_CLOSED_WITH_EDITS",
    "MARKET_CLOSING",
    "MARKET_NOT_BORROWABLE",
    "MARKET_OFFLINE",
    "MARKET_ORDERS_NOT_ALLOWED_ON_INSTRUMENT",
    "MARKET_PHONE_ONLY",
    "MARKET_ROLLED",
    "MARKET_UNAVAILABLE_TO_CLIENT",
    "MAX_AUTO_SIZE_EXCEEDED",
    "MINIMUM_ORDER_SIZE_ERROR",
    "MOVE_AWAY_ONLY_LIMIT",
    "MOVE_AWAY_ONLY_STOP",
    "MOVE_AWAY_ONLY_TRIGGER_LEVEL",
    "NCR_POSITIONS_ON_CR_ACCOUNT",
    "OPPOSING_DIRECTION_ORDERS_NOT_ALLOWED",
    "OPPOSING_POSITIONS_NOT_ALLOWED",
    "ORDER_DECLINED",
    "ORDER_LOCKED",
    "ORDER_NOT_FOUND",
    "ORDER_SIZE_CANNOT_BE_FILLED",
    "OVER_NORMAL_MARKET_SIZE",
    "PARTIALY_CLOSED_POSITION_NOT_DELETED",
    "POSITION_ALREADY_EXISTS_IN_OPPOSITE_DIRECTION",
    "POSITION_NOT_AVAILABLE_TO_CANCEL",
    "POSITION_NOT_AVAILABLE_TO_CLOSE",
    "POSITION_NOT_FOUND",
    "REJECT_CFD_ORDER_ON_SPREADBET_ACCOUNT",
    "REJECT_SPREADBET_ORDER_ON_CFD_ACCOUNT",
    "SIZE_INCREMENT",
    "SPRINT_MARKET_EXPIRY_AFTER_MARKET_CLOSE",
    "STOP_OR_LIMIT_NOT_ALLOWED",
    "STOP_REQUIRED_ERROR",
    "STRIKE_LEVEL_TOLERANCE",
    "SUCCESS",
    "TRAILING_STOP_NOT_ALLOWED",
    "UNKNOWN",
    "WRONG_SIDE_OF_MARKET",
]
PositionStatus = Literal["AMENDED", "CLOSED", "DELETED", "OPEN", "PARTIALLY_CLOSED"]


class AffectedDeal(BaseModel):
    dealId: str
    status: AffectedDealStatus


class DealConfirmation(BaseModel):
    affectedDeals: List[AffectedDeal]
    date: str
    dealId: str
    dealReference: str
    dealStatus: DealStatus
    direction: Direction
    epic: str
    expiry: Optional[str] = None
    guaranteedStop: bool
    level: Optional[Decimal] = None
    limitDistance: Optional[Decimal] = None
    limitLevel: Optional[Decimal] = None
    profit: Optional[Decimal] = None
    profitCurrency: Optional[str] = None
    reason: Reason
    size: Optional[Decimal] = None
    status: Optional[PositionStatus] = None
    stopDistance: Optional[Decimal] = None
    stopLevel: Optional[Decimal] = None
    trailingStop: bool

    @field_serializer(
        "level",
        "limitDistance",
        "limitLevel",
        "profit",
        "size",
        "stopDistance",
        "stopLevel",
    )
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value


# Working Orders Models
Direction = Literal["BUY", "SELL"]
WorkingOrderType = Literal["LIMIT", "STOP"]
TimeInForce = Literal["GOOD_TILL_CANCELLED", "GOOD_TILL_DATE"]

# Import InstrumentType and MarketStatus from markets
from api_gateway.ig_client.core.models.markets.ig_responses import (
    InstrumentType,
    MarketStatus,
)


class WorkingOrderMarketData(BaseModel):
    bid: Optional[Decimal] = None
    delayTime: Optional[int] = None
    epic: str
    exchangeId: Optional[str] = None
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

    @field_serializer(
        "bid",
        "high",
        "lotSize",
        "low",
        "netChange",
        "offer",
        "percentageChange",
        "scalingFactor",
    )
    def serialize_decimal(self, value):
        return float(value) if value is not None else None


class WorkingOrderData(BaseModel):
    createdDate: Optional[str] = None
    createdDateUTC: Optional[str] = None
    currencyCode: str
    dealId: str
    direction: Direction
    dma: Optional[bool] = None
    epic: str
    goodTillDate: Optional[str] = None
    goodTillDateISO: Optional[str] = None
    guaranteedStop: Optional[bool] = None
    limitDistance: Optional[Decimal] = None
    limitedRiskPremium: Optional[Decimal] = None
    orderLevel: Decimal
    orderSize: Decimal
    orderType: WorkingOrderType
    stopDistance: Optional[Decimal] = None
    timeInForce: Optional[TimeInForce] = None

    @field_serializer(
        "limitDistance", "limitedRiskPremium", "orderLevel", "orderSize", "stopDistance"
    )
    def serialize_decimal(self, value):
        return float(value) if value is not None else None


class WorkingOrder(BaseModel):
    marketData: WorkingOrderMarketData
    workingOrderData: WorkingOrderData


class WorkingOrders(BaseModel):
    workingOrders: List[WorkingOrder]
