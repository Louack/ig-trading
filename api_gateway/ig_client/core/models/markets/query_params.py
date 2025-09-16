from typing import Optional, Literal
from pydantic import BaseModel, Field


class GetMarketsQueryParams(BaseModel):
    """Query parameters for GET /markets (version 2)"""
    epics: str = Field(..., description="Comma-separated list of epics")
    filter: Literal["ALL", "SNAPSHOT_ONLY"] = Field(default="ALL", description="Filter type")


class SearchMarketsQueryParams(BaseModel):
    """Query parameters for GET /markets?searchTerm (version 1)"""
    searchTerm: str = Field(..., description="The term to be used in the search")


class GetPricesQueryParams(BaseModel):
    """Query parameters for GET /prices/{epic} (version 3)"""
    from_: Optional[str] = Field(None, alias="from", description="Start date (YYYY-MM-DDTHH:mm:ss)")
    to: Optional[str] = Field(None, description="End date (YYYY-MM-DDTHH:mm:ss)")
    max: Optional[int] = Field(None, description="Maximum number of data points")
    pageSize: Optional[int] = Field(None, description="Page size")
    pageNumber: Optional[int] = Field(None, description="Page number")
