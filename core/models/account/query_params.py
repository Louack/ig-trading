from typing import Optional, Literal
from pydantic import BaseModel, Field


# Transaction types
TransactionType = Literal["ALL", "ALL_DEAL", "DEPOSIT", "WITHDRAWAL"]


class TransactionHistoryQueryParams(BaseModel):
    type: Optional[TransactionType] = "ALL"
    from_date: Optional[str] = Field(None, alias="from")
    to_date: Optional[str] = Field(None, alias="to")
    maxSpanSeconds: Optional[int] = 600
    pageSize: Optional[int] = 20
    pageNumber: Optional[int] = 1

    class Config:
        populate_by_name = True  # Allow both field names and aliases
