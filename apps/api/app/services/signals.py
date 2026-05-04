from sqlalchemy.orm import Session

from app.db.models import StockSignal
from app.ml.explanation_generator import generate_multilingual_explanation
from app.ml.signal_model import classify_signal, generate_rules_based_signal


def list_signals(db: Session) -> list[StockSignal]:
    return db.query(StockSignal).order_by(StockSignal.signal_date.desc(), StockSignal.ticker.asc()).all()


def get_latest_signal(db: Session, ticker: str) -> StockSignal | None:
    return (
        db.query(StockSignal)
        .filter(StockSignal.ticker == ticker.upper())
        .order_by(StockSignal.signal_date.desc())
        .first()
    )


def generate_signal(features: dict) -> dict:
    signal, confidence = classify_signal(features)
    rules_result = generate_rules_based_signal(
        {
            "ma_20": float(features.get("ma_20", features.get("moving_average_20d", 1))),
            "ma_50": float(features.get("ma_50", features.get("moving_average_50d", 1))),
            "rsi": float(features.get("rsi", 50)),
            "volatility_30d": float(features.get("volatility_30d", 0.15)),
            "avg_daily_traded_value_mad": float(features.get("avg_daily_traded_value_mad", 5_000_000)),
            "momentum_1m": float(features.get("momentum_1m", 0)),
            "momentum_3m": float(features.get("momentum_3m", 0)),
        }
    )
    return {
        "signal": signal,
        "confidence": confidence,
        "reason": rules_result["explanation"],
        "risk_note": f"Risk level: {rules_result['risk_level']}. Signals are research support only; no trade execution is available.",
        "model_version": "rules-cse-v2",
    }


def generate_rules_signal(features: dict) -> dict:
    result = generate_rules_based_signal(
        {
            "ma_20": float(features["ma_20"]),
            "ma_50": float(features["ma_50"]),
            "rsi": float(features["rsi"]),
            "volatility_30d": float(features["volatility_30d"]),
            "avg_daily_traded_value_mad": float(features["avg_daily_traded_value_mad"]),
            "momentum_1m": float(features["momentum_1m"]),
            "momentum_3m": float(features["momentum_3m"]),
        }
    )
    return {
        **result,
        "model_version": "rules-cse-v2",
    }


def explain_signal(payload: dict) -> dict:
    return generate_multilingual_explanation(
        {
            "signal": payload["signal"].upper(),
            "confidence": int(payload["confidence"]),
            "reasons": payload.get("reasons", []),
            "risk_level": payload.get("risk_level"),
        }
    )
