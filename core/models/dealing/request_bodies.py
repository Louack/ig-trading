from decimal import Decimal
from typing import Optional, Literal

from pydantic import BaseModel, Field, root_validator


Direction = Literal["BUY", "SELL"]
OrderType = Literal["LIMIT", "MARKET", "QUOTE"]
TimeInForce = Literal["EXECUTE_AND_ELIMINATE", "FILL_OR_KILL"]


class CreateOtcPositionRequest(BaseModel):
    currencyCode: str = Field(..., regex=r"[A-Z]{3}")
    dealReference: Optional[str] = Field(None, regex=r"[A-Za-z0-9_\-]{1,30}")
    direction: Direction
    epic: str = Field(..., regex=r"[A-Za-z0-9._]{6,30}")
    expiry: str = Field(..., regex=r"(\d{2}-)?[A-Z]{3}-\d{2}|-|DFB")
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

    @root_validator
    def validate_constraints(cls, v):
        force_open = v.get("forceOpen")
        limit_distance = v.get("limitDistance")
        limit_level = v.get("limitLevel")
        stop_distance = v.get("stopDistance")
        stop_level = v.get("stopLevel")
        guaranteed_stop = v.get("guaranteedStop")
        order_type = v.get("orderType")
        level = v.get("level")
        quote_id = v.get("quoteId")
        trailing_stop = v.get("trailingStop")
        trailing_inc = v.get("trailingStopIncrement")
        size = v.get("size")

        # size precision (<= 12 decimals)
        if size is not None and isinstance(size, Decimal):
            exponent = -size.as_tuple().exponent
            if exponent > 12:
                raise ValueError("size must not have more than 12 decimal places")

        # If limitDistance/limitLevel set => forceOpen must be true
        if (limit_distance is not None or limit_level is not None) and not force_open:
            raise ValueError("forceOpen must be true when limitDistance/limitLevel is set")

        # If stopDistance/stopLevel set => forceOpen must be true
        if (stop_distance is not None or stop_level is not None) and not force_open:
            raise ValueError("forceOpen must be true when stopDistance/stopLevel is set")

        # guaranteedStop constraints
        if guaranteed_stop:
            if (stop_level is None) == (stop_distance is None):
                raise ValueError("guaranteedStop true: set only one of stopLevel or stopDistance")

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
                raise ValueError("trailingStop true: set stopDistance and trailingStopIncrement")

        # exclusivity
        if (limit_level is not None) and (limit_distance is not None):
            raise ValueError("Set only one of {limitLevel, limitDistance}")
        if (stop_level is not None) and (stop_distance is not None):
            raise ValueError("Set only one of {stopLevel, stopDistance}")

        return v

