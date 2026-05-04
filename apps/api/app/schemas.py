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
    id: UUID | None = None
    ticker: str
    sector: str | None = None
    quantity: float
    average_cost_mad: float
    current_price_mad: float
    price_status: str = "unknown"
    price_as_of: datetime | None = None
    avg_daily_traded_value_mad: float = 0
    volatility_30d: float | None = None
    market_value_mad: float
    unrealized_pl_mad: float
    unrealized_pl_pct: float = 0
    allocation_pct: float
    manual_note: str | None = None


class CreatePortfolioRequest(ApiModel):
    name: str = Field(min_length=1, max_length=120)
    user_id: UUID | None = None
    base_currency: str = Field(default="MAD", pattern="^MAD$")
    risk_profile: str = Field(default="balanced", pattern="^(conservative|balanced|growth)$")


class AddHoldingRequest(ApiModel):
    ticker: str = Field(min_length=2, max_length=8)
    quantity: float = Field(gt=0)
    average_cost_mad: float = Field(ge=0)
    manual_note: str | None = None
    opened_at: date | None = None


class UpdateHoldingRequest(ApiModel):
    quantity: float = Field(gt=0)
    average_cost_mad: float = Field(ge=0)
    manual_note: str | None = None


class PortfolioOut(ApiModel):
    id: UUID
    name: str
    base_currency: str
    total_value_mad: float
    sector_allocations: dict[str, float] = Field(default_factory=dict)
    data_quality_warnings: list[str] = Field(default_factory=list)
    holdings: list[HoldingOut]


class PortfolioPnlOut(ApiModel):
    portfolio_id: UUID
    portfolio_name: str
    base_currency: str
    cost_basis_mad: float
    current_value_mad: float
    unrealized_pl_mad: float
    unrealized_pl_pct: float
    sector_allocations: dict[str, float] = Field(default_factory=dict)
    data_quality_warnings: list[str] = Field(default_factory=list)
    holdings: list[HoldingOut]


class RiskAlertOut(ApiModel):
    id: UUID
    severity: str
    alert_type: str = "portfolio_risk"
    title: str
    detail: str
    ticker: str | None = None
    created_at: datetime
    is_read: bool = False


class AlertReadOut(ApiModel):
    id: UUID
    is_read: bool


class RiskAlertGenerationRequest(ApiModel):
    portfolio_id: UUID | None = None


class RiskAlertGenerationOut(ApiModel):
    generated: int
    alerts: list[RiskAlertOut]


class PortfolioRiskAlertOut(ApiModel):
    alert_type: str
    severity: str = Field(pattern="^(Low|Medium|High)$")
    symbol: str | None = None
    message: str
    recommended_action: str


class WatchlistItemOut(ApiModel):
    id: UUID | None = None
    ticker: str
    user_note: str | None = None
    alert_above_mad: float | None = None
    alert_below_mad: float | None = None


class WatchlistStockOut(WatchlistItemOut):
    latest_price_mad: float | None = None
    signal: str | None = None
    ranking_score: int | None = None
    daily_change_pct: float | None = None
    risk_level: str | None = None
    liquidity_score: int | None = None
    volatility_30d: float | None = None


class CreateWatchlistRequest(ApiModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    user_id: UUID | None = None
    is_default: bool = False


class AddWatchlistItemRequest(ApiModel):
    ticker: str = Field(min_length=2, max_length=8)
    user_note: str | None = Field(default=None, max_length=500)
    alert_above_mad: float | None = Field(default=None, ge=0)
    alert_below_mad: float | None = Field(default=None, ge=0)


class UpdateWatchlistItemRequest(ApiModel):
    user_note: str | None = Field(default=None, max_length=500)
    alert_above_mad: float | None = Field(default=None, ge=0)
    alert_below_mad: float | None = Field(default=None, ge=0)


class RenameWatchlistRequest(ApiModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class WatchlistOut(ApiModel):
    id: UUID
    name: str
    description: str | None = None
    is_default: bool
    items: list[WatchlistItemOut]


class WatchlistDetailOut(ApiModel):
    id: UUID
    name: str
    description: str | None = None
    is_default: bool
    items: list[WatchlistStockOut]


class UserAlertOut(ApiModel):
    alert_type: str
    severity: str = Field(pattern="^(Low|Medium|High)$")
    symbol: str | None = None
    message: str
    recommended_action: str
    current_price_mad: float | None = None


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


class PriceImportOut(ApiModel):
    status: str
    batch_id: str
    rows_received: int
    rows_inserted: int
    rows_rejected: int
    rows_duplicate: int
    warning_count: int
    warnings: list[dict] = Field(default_factory=list)
    rejected_rows: list[dict] = Field(default_factory=list)


class ImportStatusOut(ApiModel):
    status: str
    message: str | None = None
    id: UUID | None = None
    source_name: str | None = None
    rows_received: int | None = None
    rows_inserted: int | None = None
    rows_rejected: int | None = None
    rows_duplicate: int | None = None
    warning_count: int | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class DataQualityReportOut(ApiModel):
    as_of: date
    rows_checked: int
    issue_count: int
    issues: list[dict] = Field(default_factory=list)
    rules: dict
    latest_import_rejections: list[dict] = Field(default_factory=list)


class DailyRefreshOut(ApiModel):
    status: str
    message: str
    warning_count: int = 0
