# Rules-Based Signal Engine

The MVP signal engine is deterministic and explainable. It is designed for Casablanca Stock Exchange equities where liquidity and volatility constraints matter as much as trend.

## Inputs

- `ma_20`: 20-day moving average
- `ma_50`: 50-day moving average
- `rsi`: Relative Strength Index, 0-100
- `volatility_30d`: 30-day volatility as a decimal
- `avg_daily_traded_value_mad`: average daily traded value in MAD
- `momentum_1m`: 1-month momentum as a decimal
- `momentum_3m`: 3-month momentum as a decimal

## Output

- `signal`: `BUY`, `HOLD`, or `SELL`
- `confidence`: 35-92 score
- `risk_level`: `low`, `medium`, or `high`
- `explanation`: plain-English explanation
- `reasons`: individual rule reasons
- `model_version`: `rules-cse-v1`

## API

`POST /signals/rules`

```json
{
  "ma_20": 482.4,
  "ma_50": 465.2,
  "rsi": 61.5,
  "volatility_30d": 0.12,
  "avg_daily_traded_value_mad": 14000000,
  "momentum_1m": 0.045,
  "momentum_3m": 0.081
}
```

The engine returns research support only. It does not place trades or provide financial advice.

## Explanation Generator

`POST /signals/explain`

```json
{
  "signal": "BUY",
  "confidence": 74,
  "risk_level": "medium",
  "reasons": [
    "Price above 50-day moving average",
    "Strong 3-month momentum",
    "Liquidity acceptable",
    "Volatility medium"
  ]
}
```

Example response:

```json
{
  "en": "Buy signal with 74% confidence. The setup looks medium risk because the price is above its 50-day moving average, 3-month momentum is strong, liquidity appears acceptable, and volatility is medium. This is research support only, not financial advice.",
  "fr": "Signal Achat avec 74% de confiance. Le profil de risque est modere car le prix est au-dessus de sa moyenne mobile a 50 jours, la dynamique sur 3 mois est forte, la liquidite semble acceptable, et la volatilite est moyenne. Ceci est une aide a la recherche, pas un conseil financier.",
  "ar": "إشارة شراء بثقة 74%. مستوى المخاطر متوسط لأن السعر أعلى من المتوسط المتحرك لـ 50 يوما، الزخم خلال 3 أشهر قوي، تبدو السيولة مقبولة، والتقلبات متوسطة. هذا دعم بحثي فقط وليس نصيحة مالية."
}
```
