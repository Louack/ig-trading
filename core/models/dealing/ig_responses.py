from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

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
