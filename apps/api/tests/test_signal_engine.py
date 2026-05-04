from app.ml.ranking_model import calculate_technical_indicators, rank_stock
from app.ml.explanation_generator import generate_multilingual_explanation
from app.ml.signal_model import generate_rules_based_signal


def test_low_liquidity_stock_is_flagged_high_risk():
    result = generate_rules_based_signal(
        {
            "ma_20": 100,
            "ma_50": 96,
            "rsi": 58,
            "volatility_30d": 0.10,
            "avg_daily_traded_value_mad": 750_000,
            "momentum_1m": 0.04,
            "momentum_3m": 0.08,
        }
    )

    assert result["risk_level"] == "high"
    assert result["liquidity_acceptable"] is False
    assert result["signal"] == "SELL"
    assert "average daily traded value is low" in " ".join(result["reasons"])


def test_negative_momentum_and_high_volatility_does_not_generate_buy():
    result = generate_rules_based_signal(
        {
            "ma_20": 92,
            "ma_50": 100,
            "rsi": 42,
            "volatility_30d": 0.26,
            "avg_daily_traded_value_mad": 12_000_000,
            "momentum_1m": -0.05,
            "momentum_3m": -0.11,
        }
    )

    assert result["signal"] != "BUY"
    assert result["signal"] == "SELL"
    assert result["risk_level"] == "high"


def test_weighted_ranking_score_uses_expected_components():
    result = rank_stock(
        {
            "ma_20": 110,
            "ma_50": 100,
            "rsi": 58,
            "volatility_30d": 0.10,
            "avg_daily_traded_value_mad": 18_000_000,
            "momentum_1m": 0.06,
            "momentum_3m": 0.12,
        }
    )

    assert result["ranking_score"] >= 75
    assert result["component_scores"]["momentum"] >= 80
    assert result["component_scores"]["trend"] == 100
    assert result["liquidity_acceptable"] is True


def test_weighted_ranking_formula_is_exact_for_known_components():
    result = rank_stock(
        {
            "ma_20": 100,
            "ma_50": 100,
            "rsi": 55,
            "volatility_30d": 0.08,
            "avg_daily_traded_value_mad": 20_000_000,
            "momentum_1m": 0,
            "momentum_3m": 0,
        }
    )

    assert result["component_scores"] == {
        "momentum": 50,
        "trend": 50,
        "liquidity": 100,
        "volatility": 100,
        "technical_strength": 100,
    }
    assert result["ranking_score"] == 75


def test_high_score_and_acceptable_liquidity_generates_buy():
    result = generate_rules_based_signal(
        {
            "ma_20": 110,
            "ma_50": 100,
            "rsi": 58,
            "volatility_30d": 0.10,
            "avg_daily_traded_value_mad": 18_000_000,
            "momentum_1m": 0.06,
            "momentum_3m": 0.12,
        }
    )

    assert result["ranking_score"] >= 75
    assert result["liquidity_acceptable"] is True
    assert result["signal"] == "BUY"


def test_score_between_50_and_74_generates_hold():
    result = generate_rules_based_signal(
        {
            "ma_20": 100,
            "ma_50": 100,
            "rsi": 55,
            "volatility_30d": 0.16,
            "avg_daily_traded_value_mad": 6_000_000,
            "momentum_1m": 0,
            "momentum_3m": 0,
        }
    )

    assert 50 <= result["ranking_score"] <= 74
    assert result["signal"] == "HOLD"


def test_missing_indicator_data_fails_safely_without_buy():
    result = generate_rules_based_signal(
        {
            "ma_20": 0,
            "ma_50": 100,
            "rsi": 55,
            "volatility_30d": 0.10,
            "avg_daily_traded_value_mad": 12_000_000,
            "momentum_1m": 0.04,
            "momentum_3m": 0.08,
        }
    )

    assert result["ranking_score"] == 0
    assert result["signal"] == "SELL"
    assert "ma_20" in result["missing_data"]
    assert "Required market data is missing or invalid" in result["explanation"]


def test_technical_indicators_are_calculated_from_daily_prices():
    rows = [
        {
            "close_mad": 100 + index,
            "volume": 10_000 + index,
            "traded_value_mad": (100 + index) * (10_000 + index),
        }
        for index in range(70)
    ]

    indicators = calculate_technical_indicators(rows)

    assert indicators["ma_20"] > indicators["ma_50"]
    assert indicators["rsi"] == 100
    assert indicators["momentum_1m"] > 0
    assert indicators["momentum_3m"] > 0
    assert indicators["avg_daily_traded_value_mad"] > 0


def test_multilingual_explanations_are_clear_actionable_and_not_advice():
    explanation = generate_multilingual_explanation(
        {
            "signal": "BUY",
            "confidence": 74,
            "reasons": [
                "price above 50-day moving average",
                "strong 3-month momentum",
                "liquidity acceptable",
                "volatility medium",
            ],
            "risk_level": "medium",
        }
    )

    assert "BUY (74% confidence)" in explanation["en"]
    assert "Why:" in explanation["en"]
    assert "- Strong 3M momentum" in explanation["en"]
    assert "Risks:" in explanation["en"]
    assert "Action:" in explanation["en"]
    assert "not financial advice" in explanation["en"]
    assert "Pourquoi:" in explanation["fr"]
    assert "Risques:" in explanation["fr"]
    assert "\u0627\u0644\u0633\u0628\u0628:" in explanation["ar"]
    assert "\u0627\u0644\u0645\u062e\u0627\u0637\u0631:" in explanation["ar"]
    assert "\u00d8" not in explanation["ar"]


def test_rules_signal_explanation_uses_scannable_sections():
    result = generate_rules_based_signal(
        {
            "ma_20": 110,
            "ma_50": 100,
            "rsi": 58,
            "volatility_30d": 0.10,
            "avg_daily_traded_value_mad": 18_000_000,
            "momentum_1m": 0.06,
            "momentum_3m": 0.12,
        }
    )

    assert result["explanation"].startswith("BUY (")
    assert "Why:" in result["explanation"]
    assert "Risks:" in result["explanation"]
    assert "Action:" in result["explanation"]
    assert "Market analytics only, not financial advice." in result["explanation"]
