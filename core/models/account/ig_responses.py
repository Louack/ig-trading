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


class AccountPreferences(BaseModel):
    trailingStopsEnabled: bool


# Status for account preferences update
PreferencesUpdateStatus = Literal["SUCCESS"]


class UpdatePreferencesResponse(BaseModel):
    status: PreferencesUpdateStatus


# Activity-related constants
Channel = Literal["DEALER", "MOBILE", "PUBLIC_FIX_API", "PUBLIC_WEB_API", "SYSTEM", "WEB"]

ActionType = Literal[
    "LIMIT_ORDER_AMENDED", "LIMIT_ORDER_DELETED", "LIMIT_ORDER_FILLED", 
    "LIMIT_ORDER_OPENED", "LIMIT_ORDER_ROLLED", "POSITION_CLOSED",
    "POSITION_DELETED", "POSITION_OPENED", "POSITION_PARTIALLY_CLOSED",
    "POSITION_ROLLED", "STOP_LIMIT_AMENDED", "STOP_ORDER_AMENDED",
    "STOP_ORDER_DELETED", "STOP_ORDER_FILLED", "STOP_ORDER_OPENED",
    "STOP_ORDER_ROLLED", "UNKNOWN", "WORKING_ORDER_DELETED"
]

ActivityDirection = Literal["BUY", "SELL"]

ActivityStatus = Literal["ACCEPTED", "REJECTED", "UNKNOWN"]

ActivityType = Literal["EDIT_STOP_AND_LIMIT", "POSITION", "SYSTEM", "WORKING_ORDER"]


class ActivityAction(BaseModel):
    actionType: ActionType
    affectedDealId: Optional[str] = None
    currency: Optional[str] = None
    dealReference: Optional[str] = None
    direction: Optional[ActivityDirection] = None
    goodTillDate: Optional[str] = None
    guaranteedStop: Optional[bool] = None
    level: Optional[Decimal] = None
    limitDistance: Optional[Decimal] = None
    limitLevel: Optional[Decimal] = None
    marketName: Optional[str] = None
    size: Optional[Decimal] = None
    stopDistance: Optional[Decimal] = None
    stopLevel: Optional[Decimal] = None
    trailingStep: Optional[Decimal] = None
    trailingStopDistance: Optional[Decimal] = None

    @field_serializer('level', 'limitDistance', 'limitLevel', 'size', 
                     'stopDistance', 'stopLevel', 'trailingStep', 'trailingStopDistance')
    def serialize_decimal(self, value):
        return float(value) if value is not None else None


class ActivityDetails(BaseModel):
    actions: Optional[List[ActivityAction]] = None


class PagingMetadata(BaseModel):
    next: Optional[str] = None
    size: Optional[int] = None


class Metadata(BaseModel):
    paging: PagingMetadata


class Activity(BaseModel):
    channel: Channel
    date: str
    dealId: Optional[str] = None
    description: str
    details: Optional[ActivityDetails] = None
    epic: Optional[str] = None
    period: Optional[str] = None
    status: ActivityStatus
    type: ActivityType


class ActivitiesResponse(BaseModel):
    activities: List[Activity]
    metadata: Metadata


# Activity by date range response models (different structure from v3)
class ActivityByDateRange(BaseModel):
    actionStatus: str
    activity: str
    activityHistoryId: str
    channel: str
    currency: str
    date: str
    dealId: str
    epic: str
    level: str
    limit: str
    marketName: str
    period: str
    result: str
    size: str
    stop: str
    stopType: str
    time: str


class ActivitiesByDateRangeResponse(BaseModel):
    activities: List[ActivityByDateRange]


# Transaction history response models
class Transaction(BaseModel):
    cashTransaction: bool
    closeLevel: str
    currency: str
    date: str
    dateUtc: str
    instrumentName: str
    openDateUtc: str
    openLevel: str
    period: str
    profitAndLoss: str
    reference: str
    size: str
    transactionType: str


class TransactionPageData(BaseModel):
    pageNumber: int
    pageSize: int
    totalPages: int
    size: Optional[int] = None  # Made optional as it might not always be present


class TransactionMetadata(BaseModel):
    pageData: TransactionPageData


class TransactionsResponse(BaseModel):
    metadata: TransactionMetadata
    transactions: List[Transaction]
