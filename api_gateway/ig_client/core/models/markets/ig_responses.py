from decimal import Decimal
from typing import List, Optional, Literal

from pydantic import BaseModel, field_serializer


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


# Market Details Enums
MarketDetailsFilterType = Literal["ALL", "SNAPSHOT_ONLY"]
Unit = Literal["PERCENTAGE", "POINTS"]
MarketOrderPreference = Literal[
    "AVAILABLE_DEFAULT_OFF", "AVAILABLE_DEFAULT_ON", "NOT_AVAILABLE"
]
TrailingStopsPreference = Literal["AVAILABLE", "NOT_AVAILABLE"]
InstrumentType = Literal[
    "BINARY",
    "BUNGEE_CAPPED",
    "BUNGEE_COMMODITIES",
    "BUNGEE_CURRENCIES",
    "BUNGEE_INDICES",
    "COMMODITIES",
    "CURRENCIES",
    "INDICES",
    "KNOCKOUTS_COMMODITIES",
    "KNOCKOUTS_CURRENCIES",
    "KNOCKOUTS_INDICES",
    "KNOCKOUTS_SHARES",
    "OPT_COMMODITIES",
    "OPT_CURRENCIES",
    "OPT_INDICES",
    "OPT_RATES",
    "OPT_SHARES",
    "RATES",
    "SECTORS",
    "SHARES",
    "SPRINT_MARKET",
    "TEST_MARKET",
    "UNKNOWN",
]
TradeUnit = Literal["AMOUNT", "CONTRACTS", "SHARES"]
MarketStatus = Literal[
    "CLOSED",
    "EDITS_ONLY",
    "OFFLINE",
    "ON_AUCTION",
    "ON_AUCTION_NO_EDITS",
    "SUSPENDED",
    "TRADEABLE",
]
ExtendedMarketStatus = Literal[
    "OFFLINE",
    "CLOSED",
    "SUSPENDED",
    "ON_AUCTION",
    "ON_AUCTION_NO_EDITS",
    "EDITS_ONLY",
    "CLOSINGS_ONLY",
    "DEAL_NO_EDIT",
    "TRADEABLE",
]
Resolution = Literal[
    "DAY",
    "HOUR",
    "HOUR_2",
    "HOUR_3",
    "HOUR_4",
    "MINUTE",
    "MINUTE_10",
    "MINUTE_15",
    "MINUTE_2",
    "MINUTE_3",
    "MINUTE_30",
    "MINUTE_5",
    "MONTH",
    "SECOND",
    "WEEK",
]


class DealingRule(BaseModel):
    unit: Unit
    value: Decimal

    @field_serializer("value")
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value


class ControlledRiskSpacing(DealingRule):
    pass


class MaxStopOrLimitDistance(DealingRule):
    pass


class MinControlledRiskStopDistance(DealingRule):
    pass


class MinDealSize(DealingRule):
    pass


class MinNormalStopOrLimitDistance(DealingRule):
    pass


class MinStepDistance(DealingRule):
    pass


class LimitedRiskPremium(DealingRule):
    pass


class SlippageFactor(BaseModel):
    unit: str
    value: Decimal

    @field_serializer("value")
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value


class DealingRules(BaseModel):
    controlledRiskSpacing: Optional[ControlledRiskSpacing] = None
    marketOrderPreference: Optional[MarketOrderPreference] = None
    maxStopOrLimitDistance: Optional[MaxStopOrLimitDistance] = None
    minControlledRiskStopDistance: Optional[MinControlledRiskStopDistance] = None
    minDealSize: Optional[MinDealSize] = None
    minNormalStopOrLimitDistance: Optional[MinNormalStopOrLimitDistance] = None
    minStepDistance: Optional[MinStepDistance] = None
    trailingStopsPreference: Optional[TrailingStopsPreference] = None


class Currency(BaseModel):
    baseExchangeRate: Optional[Decimal] = None
    code: str
    exchangeRate: Optional[Decimal] = None
    isDefault: bool
    symbol: str

    @field_serializer("baseExchangeRate", "exchangeRate")
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value


class ExpiryDetails(BaseModel):
    lastDealingDate: Optional[str] = None
    settlementInfo: Optional[str] = None


class MarginDepositBand(BaseModel):
    currency: str
    margin: Decimal
    max: Optional[Decimal] = None
    min: Decimal
    marginFactor: Optional[Decimal] = None
    marginFactorUnit: Optional[Unit] = None

    @field_serializer("margin", "max", "min", "marginFactor")
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value


class MarketTime(BaseModel):
    closeTime: Optional[str] = None
    openTime: Optional[str] = None


class OpeningHours(BaseModel):
    marketTimes: List[MarketTime]


class RolloverDetails(BaseModel):
    lastRolloverTime: Optional[str] = None
    rolloverInfo: Optional[str] = None


class Instrument(BaseModel):
    chartCode: Optional[str] = None
    contractSize: Optional[str] = None
    controlledRiskAllowed: Optional[bool] = None
    country: Optional[str] = None
    currencies: Optional[List[Currency]] = None
    epic: str
    expiry: Optional[str] = None
    expiryDetails: Optional[ExpiryDetails] = None
    forceOpenAllowed: Optional[bool] = None
    limitedRiskPremium: Optional[LimitedRiskPremium] = None
    lotSize: Optional[Decimal] = None
    marginDepositBands: Optional[List[MarginDepositBand]] = None
    marketId: Optional[str] = None
    name: Optional[str] = None
    newsCode: Optional[str] = None
    onePipMeans: Optional[str] = None
    openingHours: Optional[OpeningHours] = None
    rolloverDetails: Optional[RolloverDetails] = None
    slippageFactor: Optional[SlippageFactor] = None
    specialInfo: Optional[List[str]] = None
    sprintMarketsMaximumExpiryTime: Optional[Decimal] = None
    sprintMarketsMinimumExpiryTime: Optional[Decimal] = None
    stopsLimitsAllowed: Optional[bool] = None
    streamingPricesAvailable: Optional[bool] = None
    type: Optional[InstrumentType] = None
    unit: Optional[TradeUnit] = None
    valueOfOnePip: Optional[str] = None

    @field_serializer(
        "lotSize", "sprintMarketsMaximumExpiryTime", "sprintMarketsMinimumExpiryTime"
    )
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value


class MarketSnapshot(BaseModel):
    bid: Optional[Decimal] = None
    binaryOdds: Optional[Decimal] = None
    controlledRiskExtraSpread: Optional[Decimal] = None
    decimalPlacesFactor: Optional[Decimal] = None
    delayTime: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    marketStatus: MarketStatus
    netChange: Optional[Decimal] = None
    offer: Optional[Decimal] = None
    percentageChange: Optional[Decimal] = None
    scalingFactor: Optional[Decimal] = None
    updateTime: Optional[str] = None

    @field_serializer(
        "bid",
        "binaryOdds",
        "controlledRiskExtraSpread",
        "decimalPlacesFactor",
        "delayTime",
        "high",
        "low",
        "netChange",
        "offer",
        "percentageChange",
        "scalingFactor",
    )
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value


class MarketDetails(BaseModel):
    dealingRules: Optional[DealingRules] = None
    instrument: Instrument
    snapshot: MarketSnapshot


class Markets(BaseModel):
    marketDetails: List[MarketDetails]


# Single Market Models (for /markets/{epic})
class PriceLadder(BaseModel):
    bid: str
    ask: str


class CurrencyLadder(BaseModel):
    currency: str
    bidSizes: List[Decimal]
    askSizes: List[Decimal]

    @field_serializer("bidSizes", "askSizes")
    def serialize_decimal_list(self, value):
        if value is not None:
            return [float(v) for v in value]
        return value


class SingleMarketSnapshot(BaseModel):
    decimalPlacesFactor: Optional[Decimal] = None
    delayTime: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    marketStatus: ExtendedMarketStatus
    netChange: Optional[Decimal] = None
    percentageChange: Optional[Decimal] = None
    scalingFactor: Optional[Decimal] = None
    updateTimestampUTC: Optional[Decimal] = None
    priceLadder: Optional[List[PriceLadder]] = None
    currencyLadders: Optional[List[CurrencyLadder]] = None

    @field_serializer(
        "decimalPlacesFactor",
        "delayTime",
        "high",
        "low",
        "netChange",
        "percentageChange",
        "scalingFactor",
        "updateTimestampUTC",
    )
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value


class SingleMarketInstrument(BaseModel):
    chartCode: Optional[str] = None
    contractSize: Optional[str] = None
    country: Optional[str] = None
    currencies: Optional[List[Currency]] = None
    epic: str
    expiry: Optional[str] = None
    limitedRiskPremium: Optional[LimitedRiskPremium] = None
    lotSize: Optional[Decimal] = None
    marketId: Optional[str] = None
    name: Optional[str] = None
    newsCode: Optional[str] = None
    streamingPricesAvailable: Optional[bool] = None
    limitAllowed: Optional[bool] = None
    stopAllowed: Optional[bool] = None
    type: Optional[InstrumentType] = None
    unit: Optional[TradeUnit] = None
    valueOfOnePip: Optional[str] = None

    @field_serializer("lotSize")
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value


class SingleMarketDetails(BaseModel):
    dealingRules: Optional[DealingRules] = None
    instrument: SingleMarketInstrument
    snapshot: SingleMarketSnapshot


# Historical Prices Models (for /prices/{epic})
class Price(BaseModel):
    ask: Optional[Decimal] = None
    bid: Optional[Decimal] = None
    lastTraded: Optional[Decimal] = None

    @field_serializer("ask", "bid", "lastTraded")
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value


class HistoricalPrice(BaseModel):
    closePrice: Optional[Price] = None
    highPrice: Optional[Price] = None
    lastTradedVolume: Optional[Decimal] = None
    lowPrice: Optional[Price] = None
    openPrice: Optional[Price] = None
    snapshotTime: str
    snapshotTimeUTC: Optional[str] = None

    @field_serializer("lastTradedVolume")
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value


class PageData(BaseModel):
    pageNumber: Decimal
    pageSize: Decimal
    totalPages: Decimal
    size: Optional[Decimal] = None

    @field_serializer("pageNumber", "pageSize", "totalPages", "size")
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value


class Allowance(BaseModel):
    allowanceExpiry: Decimal
    remainingAllowance: Decimal
    totalAllowance: Decimal

    @field_serializer("allowanceExpiry", "remainingAllowance", "totalAllowance")
    def serialize_decimal(self, value):
        if value is not None:
            return float(value)
        return value


class Metadata(BaseModel):
    pageData: PageData
    allowance: Allowance


class HistoricalPrices(BaseModel):
    instrumentType: InstrumentType
    metadata: Metadata
    prices: List[HistoricalPrice]


# Simplified Historical Prices Models (for /prices/{epic}/{resolution}/{numPoints})
class SimpleHistoricalPrices(BaseModel):
    allowance: Allowance
    instrumentType: InstrumentType
    prices: List[HistoricalPrice]


class SearchMarket(BaseModel):
    bid: Optional[Decimal] = None
    delayTime: Optional[int] = None
    epic: str
    expiry: Optional[str] = None
    high: Optional[Decimal] = None
    instrumentName: str
    instrumentType: InstrumentType
    low: Optional[Decimal] = None
    marketStatus: Optional[MarketStatus] = None
    netChange: Optional[Decimal] = None
    offer: Optional[Decimal] = None
    percentageChange: Optional[Decimal] = None
    scalingFactor: Optional[Decimal] = None
    streamingPricesAvailable: Optional[bool] = None
    updateTime: Optional[str] = None
    updateTimeUTC: Optional[str] = None

    @field_serializer(
        "bid",
        "high",
        "low",
        "netChange",
        "offer",
        "percentageChange",
        "scalingFactor",
    )
    def serialize_decimal(self, value):
        return float(value) if value is not None else None


class SearchMarkets(BaseModel):
    markets: List[SearchMarket]
