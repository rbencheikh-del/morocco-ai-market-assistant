from sqlalchemy.orm import Session

from app.db.models import Security, StockRanking, StockSignal
from app.ml.ranking_model import score_stock


def get_ranked_stocks(db: Session) -> list[dict]:
    rankings = db.query(StockRanking).order_by(StockRanking.rank_position.asc()).all()
    output = []
    for ranking in rankings:
        security = db.query(Security).filter(Security.ticker == ranking.ticker).first()
        signal = (
            db.query(StockSignal)
            .filter(StockSignal.ticker == ranking.ticker)
            .order_by(StockSignal.signal_date.desc())
            .first()
        )
        if not security or not signal:
            continue
        output.append(
            {
                "ticker": ranking.ticker,
                "name": security.name,
                "sector": security.sector,
                "ai_score": ranking.ai_score,
                "rank_position": ranking.rank_position,
                "liquidity_score": ranking.liquidity_score,
                "quality_score": ranking.quality_score,
                "momentum_score": ranking.momentum_score,
                "risk_score": ranking.risk_score,
                "rationale": ranking.rationale,
                "signal": signal.signal,
                "confidence": signal.confidence,
                "reason": signal.reason,
                "risk_note": signal.risk_note,
            }
        )
    return output


def get_stock_ranking(db: Session, ticker: str) -> dict | None:
    ticker = ticker.upper()
    ranking = (
        db.query(StockRanking)
        .filter(StockRanking.ticker == ticker)
        .order_by(StockRanking.rank_date.desc())
        .first()
    )
    if not ranking:
        return None

    security = db.query(Security).filter(Security.ticker == ticker).first()
    signal = (
        db.query(StockSignal)
        .filter(StockSignal.ticker == ticker)
        .order_by(StockSignal.signal_date.desc())
        .first()
    )
    if not security or not signal:
        return None

    return {
        "ticker": ranking.ticker,
        "name": security.name,
        "sector": security.sector,
        "ai_score": ranking.ai_score,
        "rank_position": ranking.rank_position,
        "liquidity_score": ranking.liquidity_score,
        "quality_score": ranking.quality_score,
        "momentum_score": ranking.momentum_score,
        "risk_score": ranking.risk_score,
        "rationale": ranking.rationale,
        "signal": signal.signal,
        "confidence": signal.confidence,
        "reason": signal.reason,
        "risk_note": signal.risk_note,
    }


def explain_rank(features: dict) -> dict:
    score = score_stock(features)
    return {
        "ai_score": score,
        "rationale": "Score combines liquidity, quality, momentum, and volatility controls.",
    }
