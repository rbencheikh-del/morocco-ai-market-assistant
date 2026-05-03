# API Route Plan

These routes are the backend shape for the first real product build. The current app uses `src/api/mockApiClient.ts` until a server is added.

## Auth and User

- `POST /api/auth/register`: create retail investor account.
- `POST /api/auth/login`: start authenticated session.
- `GET /api/me`: return user profile, language, and compliance flags.
- `PUT /api/me/risk-profile`: update suitability and risk profile answers.

## Market Data

- `GET /api/markets/ma/summary`: MASI, liquidity, market status, and as-of timestamp.
- `GET /api/markets/ma/securities`: Casablanca-listed securities and sectors.
- `GET /api/markets/ma/securities/:ticker/history`: historical prices, volumes, dividends, and corporate actions.

## Portfolio and Paper Trading

- `GET /api/portfolio`: holdings, MAD cash, value history, and exposure summary.
- `POST /api/paper-orders`: simulate buy or sell order after suitability checks.
- `GET /api/paper-orders`: paper order history and status.

## AI and Risk

- `POST /api/ai/signals`: generate explainable educational signal for watchlist and portfolio.
- `POST /api/ai/scenario`: simulate drawdown, liquidity, currency, and sector scenarios.
- `GET /api/audit/:auditId`: retrieve prompt inputs, model version, output, and compliance notes.

## Compliance

- `GET /api/compliance/disclosures`: product disclaimers and user acknowledgements.
- `POST /api/compliance/acknowledgements`: record user review of required disclosures.
