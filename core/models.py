from typing import List

from pydantic import BaseModel


class Account(BaseModel):
    accountId: str


class Accounts(BaseModel):
    accounts: List[Account]
