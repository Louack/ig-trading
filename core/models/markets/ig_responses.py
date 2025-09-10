from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class Market(BaseModel):
    epic: str
    instrumentName: str
    instrumentType: str
    lotSize: Decimal
    high: Decimal
    low: Decimal
    bid: Decimal
    offer: Decimal
    percentageChange: Decimal
    netChange: Decimal
