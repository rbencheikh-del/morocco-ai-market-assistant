from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SecurityOut(ApiModel):
    ticker: str
    isin: str | None = None
    name: str
    short_name: str | None = None
    sector: str
    industry: str | None = None
    exchange: str = "Casablanca Stock Exchange"
    currency: str = "MAD"


class StockDetailOut(SecurityOut):
    latest_price_mad: float | None = None
    latest_price_as_of: datetime | None = None
    latest_close_mad: float | None = None
    latest_close_date: date | None = None
    ai_score: int | None = None
    rank_position: int | None = None
    signal: str | None = None
    confidence: int | None = None
    risk_note: str | None = None


class DailyOHLCVOut(ApiModel):
    ticker: str
    price_date: date
    open_mad: float
    high_mad: float
    low_mad: float
    close_mad: float
    adjusted_close_mad: float | None = None
    volume: float
    traded_value_mad: float | None = None
    market_cap_mad: float | None = None
    data_source: str


class MarketSnapshotOut(ApiModel):
    ticker: str
    as_of: datetime
    price_mad: float
    volume: float
    market_cap_mad: float | None = None
    dividend_yield: float | None = None
    volatility_30d: float | None = None
    momentum_90d: float | None = None


class RankedStockOut(ApiModel):
    ticker: str
    name: str
    sector: str
    ai_score: int
    rank_position: int
    liquidity_score: int
    quality_score: int
    momentum_score: int
    risk_score: int
    rationale: str
    signal: str
    confidence: int
    reason: str
    risk_note: str


class SignalOut(ApiModel):
    ticker: str
    signal_date: date
    signal: str
    confidence: int
    reason: str
    risk_note: str
    model_version: str


class RulesSignalRequest(ApiModel):
    ma_20: float = Field(gt=0)
    ma_50: float = Field(gt=0)
    rsi: float = Field(ge=0, le=100)
    volatility_30d: float = Field(ge=0)
    avg_daily_traded_value_mad: float = Field(ge=0)
    momentum_1m: float
    momentum_3m: float


class RulesSignalOut(ApiModel):
    signal: str
    confidence: int
    risk_level: str
    ranking_score: int
    component_scores: dict[str, int]
    liquidity_acceptable: bool
    missing_data: list[str] = Field(default_factory=list)
    explanation: str
    reasons: list[str]
    model_version: str = "rules-cse-v2"


class SignalExplanationRequest(ApiModel):
    signal: str = Field(pattern="^(BUY|HOLD|SELL|Buy|Hold|Sell|buy|hold|sell)$")
    confidence: int = Field(ge=0, le=100)
    reasons: list[str] = Field(default_factory=list)
    risk_level: str | None = Field(default=None, pattern="^(low|medium|high)$")


class SignalExplanationOut(ApiModel):
    en: str
    fr: str
    ar: str


class HoldingOut(ApiModel):
    ticker: str
    quantity: float
    average_cost_mad: float
    current_price_mad: float
    market_value_mad: float
    unrealized_pl_mad: float
    allocation_pct: float
    manual_note: str | None = None


class AddHoldingRequest(ApiModel):
    ticker: str = Field(min_length=2, max_length=8)
    quantity: float = Field(gt=0)
    average_cost_mad: float = Field(ge=0)
    manual_note: str | None = None
    opened_at: date | None = None


class PortfolioOut(ApiModel):
    id: UUID
    name: str
    base_currency: str
    total_value_mad: float
    holdings: list[HoldingOut]


class PortfolioPnlOut(ApiModel):
    portfolio_id: UUID
    portfolio_name: str
    base_currency: str
    cost_basis_mad: float
    current_value_mad: float
    unrealized_pl_mad: float
    unrealized_pl_pct: float
    holdings: list[HoldingOut]


class RiskAlertOut(ApiModel):
    id: UUID
    severity: str
    alert_type: str = "portfolio_risk"
    title: str
    detail: str
    ticker: str | None = None
    created_at: datetime


class RiskAlertGenerationRequest(ApiModel):
    portfolio_id: UUID | None = None


class RiskAlertGenerationOut(ApiModel):
    generated: int
    alerts: list[RiskAlertOut]


class WatchlistItemOut(ApiModel):
    ticker: str
    user_note: str | None = None
    alert_above_mad: float | None = None
    alert_below_mad: float | None = None


class WatchlistOut(ApiModel):
    id: UUID
    name: str
    description: str | None = None
    is_default: bool
    items: list[WatchlistItemOut]


class AskRequest(ApiModel):
    question: str = Field(min_length=1, max_length=500)
    risk_profile: str = "balanced"
    tickers: list[str] = Field(default_factory=list)


class AskResponse(ApiModel):
    answer: str
    tickers: list[str]
    citations: list[str]
    disclaimer: str
    audit_id: UUID


class IngestionResult(ApiModel):
    inserted: int
    mode: str
