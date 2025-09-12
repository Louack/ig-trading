from pydantic import BaseModel


class UpdateAccountPreferencesRequest(BaseModel):
    trailingStopsEnabled: bool
