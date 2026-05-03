# Full-Stack MVP Skeleton

## Product Scope

morocco-ai-market-assistant helps Moroccan retail investors research Casablanca-listed stocks without executing trades. The product ranks stocks, explains research signals, tracks manually entered portfolios, and warns users when portfolio risk exceeds their profile.

## Runtime Services

- `apps/web`: Next.js dashboard for rankings, signals, charts, portfolios, alerts, and stock Q&A.
- `apps/api`: FastAPI service exposing market, ranking, signal, portfolio, alert, and assistant endpoints.
- `infra/db`: PostgreSQL schema with seeded Moroccan market demo data.

## API Surface

- `GET /health`
- `GET /market/securities`
- `GET /market/snapshots/latest`
- `POST /market/ingest/mock`
- `GET /stocks`
- `GET /stocks/{ticker}`
- `GET /rankings`
- `GET /rankings/{ticker}`
- `GET /signals`
- `POST /signals/rules`
- `POST /signals/explain`
- `GET /portfolio/demo`
- `POST /portfolio/{portfolio_id}/holdings`
- `GET /portfolio/{portfolio_id}/pnl`
- `GET /alerts`
- `POST /alerts/generate`
- `POST /assistant/ask`

## Database Boundary

The schema includes exchange metadata, Moroccan listed equities, daily OHLCV prices, market snapshots, rankings, signals, users, manual portfolios, holdings, watchlists, watchlist items, risk alerts, and model audit logs.

It deliberately excludes broker accounts, orders, executions, deposits, withdrawals, and custody records.

## ML Boundary

The MVP uses deterministic scoring and signal services for explainability. The `apps/api/app/ml/training.py` module sketches the future XGBoost training path once licensed historical data and labeled outcomes are available.

## Compliance Boundary

Every user-facing signal is framed as research support. The assistant writes audit logs, the dashboard repeats that no trade execution exists, and the architecture avoids anything that could be mistaken for broker functionality.
