from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class Balance(BaseModel):
    balance: Decimal
    deposit: Decimal
    profitLoss: Decimal
    available: Decimal


class Account(BaseModel):
    accountId: str
    accountName: str
    status: str
    accountType: str
    preferred: bool
    balance: Balance
    currency: str



class Accounts(BaseModel):
    accounts: List[Account]
