from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Security(Base):
    __tablename__ = "securities"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    ticker: Mapped[str] = mapped_column(String, unique=True, index=True)
    isin: Mapped[str | None] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    short_name: Mapped[str | None] = mapped_column(String)
    sector: Mapped[str] = mapped_column(String)
    industry: Mapped[str | None] = mapped_column(String)
    exchange_code: Mapped[str] = mapped_column(ForeignKey("exchanges.code"), server_default="CSE")
    exchange: Mapped[str] = mapped_column(String, server_default="Casablanca Stock Exchange")
    country_code: Mapped[str] = mapped_column(String, server_default="MA")
    currency: Mapped[str] = mapped_column(String, server_default="MAD")
    listing_date: Mapped[date | None] = mapped_column(Date)
    free_float_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    shares_outstanding: Mapped[float | None] = mapped_column(Numeric(20, 4))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Exchange(Base):
    __tablename__ = "exchanges"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    country_code: Mapped[str] = mapped_column(String)
    currency: Mapped[str] = mapped_column(String)
    timezone: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DailyOHLCVPrice(Base):
    __tablename__ = "daily_ohlcv_prices"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    security_id: Mapped[UUID] = mapped_column(ForeignKey("securities.id"))
    ticker: Mapped[str] = mapped_column(ForeignKey("securities.ticker"))
    price_date: Mapped[date] = mapped_column(Date)
    open_mad: Mapped[float] = mapped_column(Numeric(14, 2))
    high_mad: Mapped[float] = mapped_column(Numeric(14, 2))
    low_mad: Mapped[float] = mapped_column(Numeric(14, 2))
    close_mad: Mapped[float] = mapped_column(Numeric(14, 2))
    adjusted_close_mad: Mapped[float | None] = mapped_column(Numeric(14, 2))
    volume: Mapped[float] = mapped_column(Numeric(18, 2), server_default="0")
    traded_value_mad: Mapped[float | None] = mapped_column(Numeric(20, 2))
    market_cap_mad: Mapped[float | None] = mapped_column(Numeric(20, 2))
    data_source: Mapped[str] = mapped_column(String, server_default="mock")
    ingestion_batch_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MarketDataImportLog(Base):
    __tablename__ = "market_data_import_logs"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    source_name: Mapped[str] = mapped_column(String, server_default="csv_upload")
    status: Mapped[str] = mapped_column(String)
    rows_received: Mapped[int] = mapped_column(Integer, server_default="0")
    rows_inserted: Mapped[int] = mapped_column(Integer, server_default="0")
    rows_rejected: Mapped[int] = mapped_column(Integer, server_default="0")
    rows_duplicate: Mapped[int] = mapped_column(Integer, server_default="0")
    warning_count: Mapped[int] = mapped_column(Integer, server_default="0")
    error_message: Mapped[str | None] = mapped_column(Text)
    import_summary: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    ticker: Mapped[str] = mapped_column(ForeignKey("securities.ticker"))
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    price_mad: Mapped[float] = mapped_column(Numeric(14, 2))
    volume: Mapped[float] = mapped_column(Numeric(18, 2))
    market_cap_mad: Mapped[float | None] = mapped_column(Numeric(18, 2))
    dividend_yield: Mapped[float | None] = mapped_column(Numeric(8, 4))
    volatility_30d: Mapped[float | None] = mapped_column(Numeric(8, 4))
    momentum_90d: Mapped[float | None] = mapped_column(Numeric(8, 4))
    data_source: Mapped[str] = mapped_column(String, server_default="mock")


class StockRanking(Base):
    __tablename__ = "stock_rankings"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    ticker: Mapped[str] = mapped_column(ForeignKey("securities.ticker"))
    rank_date: Mapped[date] = mapped_column(Date)
    ai_score: Mapped[int] = mapped_column(Integer)
    rank_position: Mapped[int] = mapped_column(Integer)
    liquidity_score: Mapped[int] = mapped_column(Integer)
    quality_score: Mapped[int] = mapped_column(Integer)
    momentum_score: Mapped[int] = mapped_column(Integer)
    risk_score: Mapped[int] = mapped_column(Integer)
    rationale: Mapped[str] = mapped_column(Text)
    model_version: Mapped[str] = mapped_column(String, server_default="ranking-mock-v1")
    feature_payload: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class StockSignal(Base):
    __tablename__ = "stock_signals"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    ticker: Mapped[str] = mapped_column(ForeignKey("securities.ticker"))
    signal_date: Mapped[date] = mapped_column(Date)
    signal: Mapped[str] = mapped_column(String)
    confidence: Mapped[int] = mapped_column(Integer)
    risk_profile: Mapped[str] = mapped_column(String, server_default="balanced")
    horizon: Mapped[str] = mapped_column(String, server_default="swing")
    reason: Mapped[str] = mapped_column(Text)
    risk_note: Mapped[str] = mapped_column(Text)
    source_snapshot_id: Mapped[UUID | None] = mapped_column(ForeignKey("market_snapshots.id"))
    source_price_id: Mapped[UUID | None] = mapped_column(ForeignKey("daily_ohlcv_prices.id"))
    model_version: Mapped[str] = mapped_column(String, server_default="signal-mock-v1")
    feature_payload: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    disclaimer: Mapped[str] = mapped_column(Text, server_default="Research support only. Not financial advice. No trade execution.")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    email: Mapped[str] = mapped_column(String, unique=True)
    display_name: Mapped[str] = mapped_column(String)
    risk_profile: Mapped[str] = mapped_column(String)
    preferred_language: Mapped[str] = mapped_column(String, server_default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ManualPortfolio(Base):
    __tablename__ = "manual_portfolios"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String)
    base_currency: Mapped[str] = mapped_column(String, server_default="MAD")
    risk_profile: Mapped[str] = mapped_column(String, server_default="balanced")
    is_default: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    holdings: Mapped[list["PortfolioHolding"]] = relationship(back_populates="portfolio")


class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    portfolio_id: Mapped[UUID] = mapped_column(ForeignKey("manual_portfolios.id"))
    ticker: Mapped[str] = mapped_column(ForeignKey("securities.ticker"))
    quantity: Mapped[float] = mapped_column(Numeric(18, 4))
    average_cost_mad: Mapped[float] = mapped_column(Numeric(14, 2))
    manual_note: Mapped[str | None] = mapped_column(Text)
    opened_at: Mapped[date | None] = mapped_column(Date)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    portfolio: Mapped[ManualPortfolio] = relationship(back_populates="holdings")


class Watchlist(Base):
    __tablename__ = "watchlists"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    items: Mapped[list["WatchlistItem"]] = relationship(back_populates="watchlist")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    watchlist_id: Mapped[UUID] = mapped_column(ForeignKey("watchlists.id"))
    ticker: Mapped[str] = mapped_column(ForeignKey("securities.ticker"))
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user_note: Mapped[str | None] = mapped_column(Text)
    alert_above_mad: Mapped[float | None] = mapped_column(Numeric(14, 2))
    alert_below_mad: Mapped[float | None] = mapped_column(Numeric(14, 2))
    watchlist: Mapped[Watchlist] = relationship(back_populates="items")


class RiskAlert(Base):
    __tablename__ = "risk_alerts"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    portfolio_id: Mapped[UUID | None] = mapped_column(ForeignKey("manual_portfolios.id"))
    watchlist_id: Mapped[UUID | None] = mapped_column(ForeignKey("watchlists.id"))
    ticker: Mapped[str | None] = mapped_column(ForeignKey("securities.ticker"))
    alert_type: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    detail: Mapped[str] = mapped_column(Text)
    trigger_payload: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    is_read: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"))
    is_resolved: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ModelAuditLog(Base):
    __tablename__ = "model_audit_logs"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    request_type: Mapped[str] = mapped_column(String)
    prompt: Mapped[str | None] = mapped_column(Text)
    input_payload: Mapped[dict] = mapped_column(JSONB)
    output_payload: Mapped[dict] = mapped_column(JSONB)
    model_version: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
