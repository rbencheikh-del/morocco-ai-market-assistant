from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.db.models import DailyOHLCVPrice, MarketSnapshot, Security, StockRanking, StockSignal


MOCK_SNAPSHOTS = [
    {"ticker": "ATW", "price_mad": 480.0, "volume": 145000, "market_cap_mad": 96_500_000_000, "dividend_yield": 0.035, "volatility_30d": 0.118, "momentum_90d": 0.072},
    {"ticker": "IAM", "price_mad": 91.0, "volume": 220000, "market_cap_mad": 80_000_000_000, "dividend_yield": 0.041, "volatility_30d": 0.092, "momentum_90d": 0.031},
    {"ticker": "LHM", "price_mad": 1780.0, "volume": 9800, "market_cap_mad": 42_000_000_000, "dividend_yield": 0.028, "volatility_30d": 0.164, "momentum_90d": 0.085},
    {"ticker": "TQM", "price_mad": 1040.0, "volume": 7600, "market_cap_mad": 24_500_000_000, "dividend_yield": 0.039, "volatility_30d": 0.127, "momentum_90d": 0.024},
    {"ticker": "BOA", "price_mad": 185.0, "volume": 84000, "market_cap_mad": 38_500_000_000, "dividend_yield": 0.030, "volatility_30d": 0.143, "momentum_90d": 0.066},
]


def list_securities(db: Session) -> list[Security]:
    return db.query(Security).filter(Security.is_active.is_(True)).order_by(Security.ticker).all()


def get_security(db: Session, ticker: str) -> Security | None:
    return db.query(Security).filter(Security.ticker == ticker.upper(), Security.is_active.is_(True)).first()


def get_stock_detail(db: Session, ticker: str) -> dict | None:
    security = get_security(db, ticker)
    if not security:
        return None

    snapshot = (
        db.query(MarketSnapshot)
        .filter(MarketSnapshot.ticker == security.ticker)
        .order_by(MarketSnapshot.as_of.desc())
        .first()
    )
    daily_price = (
        db.query(DailyOHLCVPrice)
        .filter(DailyOHLCVPrice.ticker == security.ticker)
        .order_by(DailyOHLCVPrice.price_date.desc())
        .first()
    )
    ranking = (
        db.query(StockRanking)
        .filter(StockRanking.ticker == security.ticker)
        .order_by(StockRanking.rank_date.desc())
        .first()
    )
    signal = (
        db.query(StockSignal)
        .filter(StockSignal.ticker == security.ticker)
        .order_by(StockSignal.signal_date.desc())
        .first()
    )

    return {
        "ticker": security.ticker,
        "isin": security.isin,
        "name": security.name,
        "short_name": security.short_name,
        "sector": security.sector,
        "industry": security.industry,
        "exchange": security.exchange,
        "currency": security.currency,
        "latest_price_mad": float(snapshot.price_mad) if snapshot else None,
        "latest_price_as_of": snapshot.as_of if snapshot else None,
        "latest_close_mad": float(daily_price.close_mad) if daily_price else None,
        "latest_close_date": daily_price.price_date if daily_price else None,
        "ai_score": ranking.ai_score if ranking else None,
        "rank_position": ranking.rank_position if ranking else None,
        "signal": signal.signal if signal else None,
        "confidence": signal.confidence if signal else None,
        "risk_note": signal.risk_note if signal else None,
    }


def latest_snapshots(db: Session) -> list[MarketSnapshot]:
    rows = []
    for security in list_securities(db):
        snapshot = (
            db.query(MarketSnapshot)
            .filter(MarketSnapshot.ticker == security.ticker)
            .order_by(MarketSnapshot.as_of.desc())
            .first()
        )
        if snapshot:
            rows.append(snapshot)
    return rows


def daily_ohlcv_history(db: Session, ticker: str, limit: int = 120) -> list[DailyOHLCVPrice]:
    return (
        db.query(DailyOHLCVPrice)
        .filter(DailyOHLCVPrice.ticker == ticker.upper())
        .order_by(DailyOHLCVPrice.price_date.desc())
        .limit(limit)
        .all()
    )


def ingest_mock_snapshots(db: Session) -> int:
    as_of = datetime.now(UTC)
    inserted = 0
    for row in MOCK_SNAPSHOTS:
        db.add(MarketSnapshot(as_of=as_of, **row))
        inserted += 1
    db.commit()
    return inserted
