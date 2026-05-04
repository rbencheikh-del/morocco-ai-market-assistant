from __future__ import annotations

from typing import Literal, TypedDict

from app.ml.ranking_model import rank_stock


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
    ranking_score: int
    component_scores: dict[str, int]
    liquidity_acceptable: bool
    missing_data: list[str]
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
    ranking = rank_stock(inputs)
    ranking_score = ranking["ranking_score"]
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

    if ranking["missing_data"]:
        signal: SignalLabel = "SELL"
        bearish_reasons.append(
            "required market data is missing or invalid, so the engine fails safely with SELL/AVOID"
        )
    elif ranking["liquidity_weak"]:
        signal: SignalLabel = "SELL"
        bearish_reasons.append("liquidity is weak, so the stock is marked SELL/AVOID for this analytics-only MVP")
    elif ranking_score >= 75 and ranking["liquidity_acceptable"]:
        signal: SignalLabel = "BUY"
    elif 50 <= ranking_score <= 74:
        signal = "HOLD"
    else:
        signal = "SELL"

    reasons = bullish_reasons + caution_reasons + bearish_reasons
    confidence = _confidence_from_ranking(signal, ranking_score, risk_level, len(reasons))
    explanation = _plain_english_explanation(
        signal,
        confidence,
        risk_level,
        ranking_score,
        ranking["liquidity_acceptable"],
        ranking["missing_data"],
        bullish_reasons,
        caution_reasons,
        bearish_reasons,
    )

    return {
        "signal": signal,
        "confidence": confidence,
        "risk_level": risk_level,
        "ranking_score": ranking_score,
        "component_scores": ranking["component_scores"],
        "liquidity_acceptable": ranking["liquidity_acceptable"],
        "missing_data": ranking["missing_data"],
        "explanation": explanation,
        "reasons": reasons,
    }


def _plain_english_explanation(
    signal: SignalLabel,
    confidence: int,
    risk_level: RiskLevel,
    ranking_score: int,
    liquidity_acceptable: bool,
    missing_data: list[str],
    bullish_reasons: list[str],
    caution_reasons: list[str],
    bearish_reasons: list[str],
) -> str:
    if missing_data:
        lead = "The engine cannot calculate a reliable research signal"
    elif signal == "BUY":
        lead = "The setup is positive enough for a BUY research signal"
    elif signal == "SELL":
        lead = "The setup is weak enough for a SELL research signal"
    else:
        lead = "The setup is mixed, so the engine returns HOLD"

    strongest = bullish_reasons[:2] if signal == "BUY" else bearish_reasons[:2]
    if not strongest:
        strongest = caution_reasons[:2] or bullish_reasons[:1] or bearish_reasons[:1]

    details = "; ".join(strongest)
    liquidity_note = "liquidity is acceptable" if liquidity_acceptable else "liquidity is weak"
    if missing_data:
        return (
            f"{signal} ({confidence}% confidence)\n\n"
            "Why:\n"
            "- Required market data is missing or invalid\n\n"
            "Risks:\n"
            f"- Missing fields: {', '.join(missing_data)}\n\n"
            "Action:\n"
            "Refresh or verify market data before relying on this research signal.\n\n"
            "Market analytics only, not financial advice."
        )
    why = bullish_reasons[:3] if signal == "BUY" else (caution_reasons[:2] or bearish_reasons[:2])
    if signal == "SELL":
        why = bearish_reasons[:3] or caution_reasons[:2]
    risks = (caution_reasons + bearish_reasons)[:3] if signal != "SELL" else bearish_reasons[:3]
    if not risks:
        risks = [f"{risk_level} risk profile", liquidity_note]
    action = {
        "BUY": "Watch for confirmation above the next resistance level or a fresh price breakout.",
        "HOLD": "Keep monitoring price, liquidity, and the next signal update.",
        "SELL": "Review risk drivers and data freshness before making any manual decision.",
    }[signal]
    why_text = "\n".join(f"- {item}" for item in (why or [details or "Indicators are mixed"]))
    risk_text = "\n".join(f"- {item}" for item in risks)
    if details:
        return (
            f"{signal} ({confidence}% confidence)\n\n"
            f"Why:\n{why_text}\n\n"
            f"Risks:\n{risk_text}\n\n"
            f"Action:\n{action}\n\n"
            "Market analytics only, not financial advice."
        )
    return (
        f"{signal} ({confidence}% confidence)\n\n"
        f"Why:\n- Ranking score is {ranking_score}/100\n- {liquidity_note}\n\n"
        f"Risks:\n- {risk_level} risk profile\n\n"
        f"Action:\n{action}\n\n"
        "Market analytics only, not financial advice."
    )


def _confidence_from_ranking(signal: SignalLabel, ranking_score: int, risk_level: RiskLevel, rule_count: int) -> int:
    if signal == "BUY":
        distance = ranking_score - 75
    elif signal == "SELL":
        distance = 50 - ranking_score
    else:
        distance = 74 - abs(62 - ranking_score)
    risk_penalty = {"low": 0, "medium": 5, "high": 12}[risk_level]
    evidence_bonus = min(rule_count * 2, 10)
    return max(40, min(95, round(62 + distance * 0.6 + evidence_bonus - risk_penalty)))
