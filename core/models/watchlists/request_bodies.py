from typing import List
from pydantic import BaseModel, Field


class CreateWatchlistRequest(BaseModel):
    epics: List[str]
    name: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u00ff. _]+$",
    )


class AddMarketToWatchlistRequest(BaseModel):
    epic: str = Field(..., pattern=r"[A-Za-z0-9._]{6,30}")
