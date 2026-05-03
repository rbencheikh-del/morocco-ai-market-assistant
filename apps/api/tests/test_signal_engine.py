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
