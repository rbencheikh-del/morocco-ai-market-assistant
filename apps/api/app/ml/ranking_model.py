from __future__ import annotations

from statistics import mean, pstdev
from typing import TypedDict


class IndicatorInputs(TypedDict):
    ma_20: float
    ma_50: float
    rsi: float
    volatility_30d: float
    avg_daily_traded_value_mad: float
    momentum_1m: float
    momentum_3m: float


class RankingResult(TypedDict):
    ranking_score: int
    component_scores: dict[str, int]
    liquidity_acceptable: bool
    liquidity_weak: bool
    missing_data: list[str]
    explanation: str


def calculate_technical_indicators(price_rows: list[dict]) -> IndicatorInputs:
    """Calculate CSE-focused indicators from ascending daily OHLCV rows."""
    if len(price_rows) < 64:
        raise ValueError("At least 64 daily price rows are required for 3-month momentum and MA50.")

    closes = [float(row["close_mad"]) for row in price_rows]
    traded_values = [
        float(row.get("traded_value_mad") or (float(row.get("close_mad", 0)) * float(row.get("volume", 0))))
        for row in price_rows
    ]

    ma_20 = mean(closes[-20:])
    ma_50 = mean(closes[-50:])
    rsi = _rsi(closes, period=14)
    volatility_30d = _volatility(closes[-31:])
    momentum_1m = _momentum(closes, lookback=21)
    momentum_3m = _momentum(closes, lookback=63)
    avg_daily_traded_value_mad = mean(traded_values[-30:])

    return {
        "ma_20": ma_20,
        "ma_50": ma_50,
        "rsi": rsi,
        "volatility_30d": volatility_30d,
        "avg_daily_traded_value_mad": avg_daily_traded_value_mad,
        "momentum_1m": momentum_1m,
        "momentum_3m": momentum_3m,
    }


def score_stock(features: dict) -> int:
    return rank_stock(features)["ranking_score"]


def rank_stock(features: dict) -> RankingResult:
    missing_data = _missing_or_invalid_indicators(features)
    if missing_data:
        return {
            "ranking_score": 0,
            "component_scores": {
                "momentum": 0,
                "trend": 0,
                "liquidity": 0,
                "volatility": 0,
                "technical_strength": 0,
            },
            "liquidity_acceptable": False,
            "liquidity_weak": True,
            "missing_data": missing_data,
            "explanation": (
                "Ranking was not calculated because required market indicators are missing or invalid: "
                f"{', '.join(missing_data)}."
            ),
        }

    indicators = _coerce_indicators(features)
    component_scores = {
        "momentum": _momentum_score(indicators["momentum_1m"], indicators["momentum_3m"]),
        "trend": _trend_score(indicators["ma_20"], indicators["ma_50"]),
        "liquidity": _liquidity_score(indicators["avg_daily_traded_value_mad"]),
        "volatility": _volatility_score(indicators["volatility_30d"]),
        "technical_strength": _rsi_score(indicators["rsi"]),
    }
    ranking_score = round(
        0.30 * component_scores["momentum"]
        + 0.20 * component_scores["trend"]
        + 0.20 * component_scores["liquidity"]
        + 0.15 * component_scores["volatility"]
        + 0.15 * component_scores["technical_strength"]
    )
    liquidity_weak = indicators["avg_daily_traded_value_mad"] < 1_000_000
    liquidity_acceptable = indicators["avg_daily_traded_value_mad"] >= 1_000_000
    return {
        "ranking_score": max(0, min(100, ranking_score)),
        "component_scores": component_scores,
        "liquidity_acceptable": liquidity_acceptable,
        "liquidity_weak": liquidity_weak,
        "missing_data": [],
        "explanation": _ranking_explanation(component_scores, liquidity_acceptable),
    }


def _missing_or_invalid_indicators(features: dict) -> list[str]:
    required_positive = ["ma_20", "ma_50", "avg_daily_traded_value_mad"]
    required_present = ["rsi", "volatility_30d", "momentum_1m", "momentum_3m"]
    missing: list[str] = []

    for field in required_positive:
        value = _safe_float(features.get(field))
        if value is None or value <= 0:
            missing.append(field)

    for field in required_present:
        if _safe_float(features.get(field)) is None:
            missing.append(field)

    rsi = _safe_float(features.get("rsi"))
    volatility = _safe_float(features.get("volatility_30d"))
    if rsi is not None and not 0 <= rsi <= 100:
        missing.append("rsi")
    if volatility is not None and volatility < 0:
        missing.append("volatility_30d")

    return sorted(set(missing))


def _safe_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_indicators(features: dict) -> IndicatorInputs:
    return {
        "ma_20": float(features.get("ma_20", features.get("moving_average_20d", 0))),
        "ma_50": float(features.get("ma_50", features.get("moving_average_50d", 0))),
        "rsi": float(features.get("rsi", 50)),
        "volatility_30d": float(features.get("volatility_30d", 0.15)),
        "avg_daily_traded_value_mad": float(features.get("avg_daily_traded_value_mad", 0)),
        "momentum_1m": float(features.get("momentum_1m", 0)),
        "momentum_3m": float(features.get("momentum_3m", 0)),
    }


def _rsi(closes: list[float], period: int) -> float:
    changes = [closes[index] - closes[index - 1] for index in range(1, len(closes))]
    recent = changes[-period:]
    gains = [change for change in recent if change > 0]
    losses = [abs(change) for change in recent if change < 0]
    avg_gain = mean(gains) if gains else 0
    avg_loss = mean(losses) if losses else 0
    if avg_loss == 0:
        return 100.0 if avg_gain else 50.0
    relative_strength = avg_gain / avg_loss
    return 100 - (100 / (1 + relative_strength))


def _volatility(closes: list[float]) -> float:
    returns = [(closes[index] / closes[index - 1]) - 1 for index in range(1, len(closes)) if closes[index - 1]]
    return pstdev(returns) if len(returns) > 1 else 0.0


def _momentum(closes: list[float], lookback: int) -> float:
    previous = closes[-lookback - 1]
    return (closes[-1] / previous) - 1 if previous else 0.0


def _bounded_linear(value: float, low: float, high: float) -> int:
    if value <= low:
        return 0
    if value >= high:
        return 100
    return round(((value - low) / (high - low)) * 100)


def _momentum_score(momentum_1m: float, momentum_3m: float) -> int:
    one_month = _bounded_linear(momentum_1m, -0.08, 0.08)
    three_month = _bounded_linear(momentum_3m, -0.15, 0.15)
    return round(0.40 * one_month + 0.60 * three_month)


def _trend_score(ma_20: float, ma_50: float) -> int:
    if ma_50 <= 0:
        return 0
    trend_gap = (ma_20 / ma_50) - 1
    return _bounded_linear(trend_gap, -0.05, 0.05)


def _liquidity_score(avg_daily_traded_value_mad: float) -> int:
    if avg_daily_traded_value_mad < 1_000_000:
        return _bounded_linear(avg_daily_traded_value_mad, 0, 1_000_000) // 2
    if avg_daily_traded_value_mad >= 20_000_000:
        return 100
    return 50 + round(((avg_daily_traded_value_mad - 1_000_000) / 19_000_000) * 50)


def _volatility_score(volatility_30d: float) -> int:
    return 100 - _bounded_linear(volatility_30d, 0.08, 0.30)


def _rsi_score(rsi: float) -> int:
    if 45 <= rsi <= 65:
        return 100
    if rsi < 45:
        return _bounded_linear(rsi, 20, 45)
    return 100 - _bounded_linear(rsi, 65, 85)


def _ranking_explanation(component_scores: dict[str, int], liquidity_acceptable: bool) -> str:
    strongest = max(component_scores, key=component_scores.get)
    weakest = min(component_scores, key=component_scores.get)
    liquidity_note = "liquidity is acceptable" if liquidity_acceptable else "liquidity is weak"
    return (
        f"Ranking combines momentum, trend, liquidity, volatility, and RSI strength. "
        f"The strongest factor is {strongest}; the weakest factor is {weakest}; {liquidity_note}."
    )
