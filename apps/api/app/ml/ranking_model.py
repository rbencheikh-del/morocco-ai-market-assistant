def score_stock(features: dict) -> int:
    liquidity = float(features.get("liquidity_score", 60))
    quality = float(features.get("quality_score", 60))
    momentum = float(features.get("momentum_score", 50))
    risk = float(features.get("risk_score", 50))
    score = 0.30 * liquidity + 0.30 * quality + 0.25 * momentum + 0.15 * (100 - risk)
    return max(0, min(100, round(score)))
