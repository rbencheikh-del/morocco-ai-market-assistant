from __future__ import annotations

from typing import Literal, TypedDict


SignalLabel = Literal["BUY", "HOLD", "SELL"]
RiskLevel = Literal["low", "medium", "high"]


class SignalInputs(TypedDict):
    ma_20: float
    ma_50: float
    rsi: float
    volatility_30d: float
    avg_daily_traded_value_mad: float
    momentum_1m: float
    momentum_3m: float


class SignalResult(TypedDict):
    signal: SignalLabel
    confidence: int
    risk_level: RiskLevel
    explanation: str
    reasons: list[str]


def _risk_level(volatility_30d: float, avg_daily_traded_value_mad: float, rsi: float) -> RiskLevel:
    if volatility_30d >= 0.22 or avg_daily_traded_value_mad < 1_000_000 or rsi >= 78 or rsi <= 22:
        return "high"
    if volatility_30d >= 0.14 or avg_daily_traded_value_mad < 5_000_000 or rsi >= 70 or rsi <= 30:
        return "medium"
    return "low"


def _confidence(base_score: int, risk_level: RiskLevel, rule_count: int) -> int:
    risk_penalty = {"low": 0, "medium": 6, "high": 14}[risk_level]
    evidence_bonus = min(rule_count * 4, 16)
    return max(35, min(92, 55 + abs(base_score) * 5 + evidence_bonus - risk_penalty))


def classify_signal(features: dict) -> tuple[str, int]:
    result = generate_rules_based_signal(
        {
            "ma_20": float(features.get("ma_20", features.get("moving_average_20d", 0))),
            "ma_50": float(features.get("ma_50", features.get("moving_average_50d", 0))),
            "rsi": float(features.get("rsi", 50)),
            "volatility_30d": float(features.get("volatility_30d", 0.15)),
            "avg_daily_traded_value_mad": float(features.get("avg_daily_traded_value_mad", 5_000_000)),
            "momentum_1m": float(features.get("momentum_1m", 0)),
            "momentum_3m": float(features.get("momentum_3m", 0)),
        }
    )
    return result["signal"], result["confidence"]


def generate_rules_based_signal(inputs: SignalInputs) -> SignalResult:
    score = 0
    bullish_reasons: list[str] = []
    bearish_reasons: list[str] = []
    caution_reasons: list[str] = []

    ma_20 = inputs["ma_20"]
    ma_50 = inputs["ma_50"]
    rsi = inputs["rsi"]
    volatility_30d = inputs["volatility_30d"]
    avg_daily_traded_value_mad = inputs["avg_daily_traded_value_mad"]
    momentum_1m = inputs["momentum_1m"]
    momentum_3m = inputs["momentum_3m"]

    if ma_20 > ma_50 * 1.01:
        score += 2
        bullish_reasons.append("the 20-day moving average is above the 50-day moving average")
    elif ma_20 < ma_50 * 0.99:
        score -= 2
        bearish_reasons.append("the 20-day moving average is below the 50-day moving average")
    else:
        caution_reasons.append("the moving averages are close together, so trend confirmation is limited")

    if 45 <= rsi <= 68:
        score += 1
        bullish_reasons.append("RSI is constructive without looking overbought")
    elif rsi > 75:
        score -= 2
        bearish_reasons.append("RSI is very high, which can indicate an overbought setup")
    elif rsi >= 70:
        score -= 1
        caution_reasons.append("RSI is elevated, so upside may be stretched")
    elif rsi < 30:
        score -= 1
        caution_reasons.append("RSI is weak and may reflect bearish pressure")

    if momentum_1m > 0.03:
        score += 1
        bullish_reasons.append("1-month momentum is positive")
    elif momentum_1m < -0.03:
        score -= 1
        bearish_reasons.append("1-month momentum is negative")

    if momentum_3m > 0.06:
        score += 2
        bullish_reasons.append("3-month momentum confirms a stronger trend")
    elif momentum_3m < -0.06:
        score -= 2
        bearish_reasons.append("3-month momentum is materially negative")

    if avg_daily_traded_value_mad >= 10_000_000:
        score += 1
        bullish_reasons.append("average daily traded value suggests healthy liquidity")
    elif avg_daily_traded_value_mad < 1_000_000:
        score -= 2
        bearish_reasons.append("average daily traded value is low for retail execution quality")
    elif avg_daily_traded_value_mad < 5_000_000:
        score -= 1
        caution_reasons.append("liquidity is moderate and position sizing should be conservative")

    risk_level = _risk_level(volatility_30d, avg_daily_traded_value_mad, rsi)
    if volatility_30d >= 0.22:
        score -= 2
        bearish_reasons.append("30-day volatility is elevated")
    elif volatility_30d >= 0.14:
        score -= 1
        caution_reasons.append("30-day volatility is moderate")
    else:
        bullish_reasons.append("30-day volatility is contained")

    if score >= 3 and risk_level != "high":
        signal: SignalLabel = "BUY"
    elif score <= -3 or (risk_level == "high" and score <= 1):
        signal = "SELL"
    else:
        signal = "HOLD"

    reasons = bullish_reasons + caution_reasons + bearish_reasons
    confidence = _confidence(score, risk_level, len(reasons))
    explanation = _plain_english_explanation(signal, confidence, risk_level, bullish_reasons, caution_reasons, bearish_reasons)

    return {
        "signal": signal,
        "confidence": confidence,
        "risk_level": risk_level,
        "explanation": explanation,
        "reasons": reasons,
    }


def _plain_english_explanation(
    signal: SignalLabel,
    confidence: int,
    risk_level: RiskLevel,
    bullish_reasons: list[str],
    caution_reasons: list[str],
    bearish_reasons: list[str],
) -> str:
    if signal == "BUY":
        lead = "The setup is positive enough for a BUY research signal"
    elif signal == "SELL":
        lead = "The setup is weak enough for a SELL research signal"
    else:
        lead = "The setup is mixed, so the engine returns HOLD"

    strongest = bullish_reasons[:2] if signal == "BUY" else bearish_reasons[:2]
    if not strongest:
        strongest = caution_reasons[:2] or bullish_reasons[:1] or bearish_reasons[:1]

    details = "; ".join(strongest)
    if details:
        return f"{lead} with {confidence}% confidence and {risk_level} risk because {details}."
    return f"{lead} with {confidence}% confidence and {risk_level} risk based on the supplied market indicators."
