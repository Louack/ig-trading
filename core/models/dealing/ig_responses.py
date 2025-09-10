from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Literal

from pydantic import BaseModel, field_serializer

from core.models.markets.ig_responses import Market


class PositionDetail(BaseModel):
    dealId: str
    contractSize: Decimal
    createdDateUTC: datetime
    direction: str
    limitLevel: Optional[Decimal]
    stopLevel: Optional[Decimal]
    level: Decimal
    currency: str




class Position(BaseModel):
    position: PositionDetail
    market: Market


class Positions(BaseModel):
    positions: List[Position]


class CreateOtcPositionResponse(BaseModel):
    dealReference: str


class CloseOtcPositionResponse(BaseModel):
    dealReference: str


# Deal Confirmation Enums
AffectedDealStatus = Literal["AMENDED", "DELETED", "FULLY_CLOSED", "OPENED", "PARTIALLY_CLOSED"]
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
    "WRONG_SIDE_OF_MARKET"
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

    @field_serializer('level', 'limitDistance', 'limitLevel', 'profit', 'size', 'stopDistance', 'stopLevel')
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value
