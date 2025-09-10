from decimal import Decimal
from typing import Optional, Literal

from pydantic import BaseModel, Field, model_validator, field_serializer


Direction = Literal["BUY", "SELL"]
OrderType = Literal["LIMIT", "MARKET", "QUOTE"]
TimeInForce = Literal["EXECUTE_AND_ELIMINATE", "FILL_OR_KILL"]


class CreateOtcPositionRequest(BaseModel):
    currencyCode: str = Field(..., pattern=r"[A-Z]{3}")
    dealReference: Optional[str] = Field(None, pattern=r"[A-Za-z0-9_\-]{1,30}")
    direction: Direction
    epic: str = Field(..., pattern=r"[A-Za-z0-9._]{6,30}")
    expiry: str = Field(..., pattern=r"(\d{2}-)?[A-Z]{3}-\d{2}|-|DFB")
    forceOpen: bool
    guaranteedStop: bool
    level: Optional[Decimal] = None
    limitDistance: Optional[Decimal] = None
    limitLevel: Optional[Decimal] = None
    orderType: OrderType
    quoteId: Optional[str] = None
    size: Decimal
    stopDistance: Optional[Decimal] = None
    stopLevel: Optional[Decimal] = None
    timeInForce: Optional[TimeInForce] = None
    trailingStop: Optional[bool] = None
    trailingStopIncrement: Optional[Decimal] = None

    @field_serializer(
        "size",
        "level",
        "limitDistance",
        "limitLevel",
        "stopDistance",
        "stopLevel",
        "trailingStopIncrement",
    )
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value

    @model_validator(mode="after")
    def validate_constraints(self):
        force_open = self.forceOpen
        limit_distance = self.limitDistance
        limit_level = self.limitLevel
        stop_distance = self.stopDistance
        stop_level = self.stopLevel
        guaranteed_stop = self.guaranteedStop
        order_type = self.orderType
        level = self.level
        quote_id = self.quoteId
        trailing_stop = self.trailingStop
        trailing_inc = self.trailingStopIncrement
        size = self.size

        # size precision (<= 12 decimals)
        if size is not None and isinstance(size, Decimal):
            exponent = -size.as_tuple().exponent
            if exponent > 12:
                raise ValueError("size must not have more than 12 decimal places")

        # If limitDistance/limitLevel set => forceOpen must be true
        if (limit_distance is not None or limit_level is not None) and not force_open:
            raise ValueError(
                "forceOpen must be true when limitDistance/limitLevel is set"
            )

        # If stopDistance/stopLevel set => forceOpen must be true
        if (stop_distance is not None or stop_level is not None) and not force_open:
            raise ValueError(
                "forceOpen must be true when stopDistance/stopLevel is set"
            )

        # guaranteedStop constraints
        if guaranteed_stop:
            if (stop_level is None) == (stop_distance is None):
                raise ValueError(
                    "guaranteedStop true: set only one of stopLevel or stopDistance"
                )

        # orderType constraints
        if order_type == "LIMIT":
            if quote_id is not None:
                raise ValueError("orderType LIMIT: do not set quoteId")
            if level is None:
                raise ValueError("orderType LIMIT: level is required")
        elif order_type == "MARKET":
            if level is not None or quote_id is not None:
                raise ValueError("orderType MARKET: do not set level or quoteId")
        elif order_type == "QUOTE":
            if level is None or quote_id is None:
                raise ValueError("orderType QUOTE: set both level and quoteId")

        # trailingStop constraints
        if trailing_stop is False and trailing_inc is not None:
            raise ValueError("trailingStop false: do not set trailingStopIncrement")
        if trailing_stop is True:
            if stop_level is not None:
                raise ValueError("trailingStop true: do not set stopLevel")
            if guaranteed_stop:
                raise ValueError("trailingStop true: guaranteedStop must be false")
            if stop_distance is None or trailing_inc is None:
                raise ValueError(
                    "trailingStop true: set stopDistance and trailingStopIncrement"
                )

        # exclusivity
        if (limit_level is not None) and (limit_distance is not None):
            raise ValueError("Set only one of {limitLevel, limitDistance}")
        if (stop_level is not None) and (stop_distance is not None):
            raise ValueError("Set only one of {stopLevel, stopDistance}")

        return self


class CloseOtcPositionRequest(BaseModel):
    dealId: Optional[str] = Field(None, pattern=r".{1,30}")
    direction: Direction
    epic: Optional[str] = Field(None, pattern=r"[A-Za-z0-9._]{6,30}")
    expiry: Optional[str] = Field(None, pattern=r"(\d{2}-)?[A-Z]{3}-\d{2}|-|DFB")
    level: Optional[Decimal] = None
    orderType: OrderType
    quoteId: Optional[str] = None
    size: Decimal
    timeInForce: Optional[TimeInForce] = None

    @field_serializer("level", "size")
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value

    @model_validator(mode="after")
    def validate_constraints(self):
        deal_id = self.dealId
        epic = self.epic
        expiry = self.expiry
        order_type = self.orderType
        level = self.level
        quote_id = self.quoteId
        size = self.size

        # size precision (<= 12 decimals)
        if size is not None and isinstance(size, Decimal):
            exponent = -size.as_tuple().exponent
            if exponent > 12:
                raise ValueError("size must not have more than 12 decimal places")

        # Set only one of {dealId, epic}
        if (deal_id is not None) and (epic is not None):
            raise ValueError("Set only one of {dealId, epic}")

        # If epic is defined, then set expiry
        if epic is not None and expiry is None:
            raise ValueError("If epic is defined, then set expiry")

        # orderType constraints
        if order_type == "LIMIT":
            if quote_id is not None:
                raise ValueError("orderType LIMIT: do not set quoteId")
            if level is None:
                raise ValueError("orderType LIMIT: level is required")
        elif order_type == "MARKET":
            if level is not None or quote_id is not None:
                raise ValueError("orderType MARKET: do not set level or quoteId")
        elif order_type == "QUOTE":
            if level is None or quote_id is None:
                raise ValueError("orderType QUOTE: set both level and quoteId")

        return self
