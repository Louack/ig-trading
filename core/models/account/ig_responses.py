from decimal import Decimal
from typing import List, Literal, Optional
from pydantic import BaseModel, field_serializer

# Account type constants
AccountType = Literal["CFD", "PHYSICAL", "SPREADBET"]

# Account status constants  
AccountStatus = Literal["DISABLED", "ENABLED", "SUSPENDED_FROM_DEALING"]


class Balance(BaseModel):
    available: Decimal
    balance: Decimal
    deposit: Decimal
    profitLoss: Decimal

    @field_serializer('available', 'balance', 'deposit', 'profitLoss')
    def serialize_decimal(self, value):
        return float(value) if value is not None else None


class Account(BaseModel):
    accountAlias: Optional[str] = None
    accountId: str
    accountName: str
    accountType: AccountType
    balance: Balance
    canTransferFrom: bool
    canTransferTo: bool
    currency: str
    preferred: bool
    status: AccountStatus


class Accounts(BaseModel):
    accounts: List[Account]
