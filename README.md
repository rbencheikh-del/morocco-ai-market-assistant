# morocco-ai-market-assistant

morocco-ai-market-assistant is a full-stack MVP repo for an AI-powered Moroccan stock market assistant. It helps retail investors view ranked Casablanca-listed stocks, understand explainable research signals, manually track MAD-denominated portfolios, and receive risk alerts.

The MVP intentionally has no trade execution. It is a research, education, and portfolio-monitoring product skeleton.

## Stack

- Frontend: Next.js app in `apps/web`
- Backend: Python FastAPI app in `apps/api`
- Database: PostgreSQL with seed data in `infra/db`
- ML: scikit-learn and XGBoost stubs in `apps/api/app/ml`
- Charts: TradingView Lightweight Charts in the Next.js dashboard
- Legacy prototype: previous Vite prototype remains under `src`

## Modules

- Market data ingestion
- Stock ranking engine
- Buy/hold/sell signal engine
- Portfolio tracker
- Watchlists
- Risk alerts
- User dashboard
- Stock Q&A assistant with audit logging
- No trade execution, broker orders, deposits, withdrawals, or custody flows

## Portfolio and Risk Logic

The portfolio tracker values manually entered holdings in MAD, calculates cost basis and unrealized P&L, and reports allocation by holding and sector. If a latest market price is unavailable, the API marks the holding with `price_status: missing`, uses average cost only as a safe display fallback, and returns a data-quality warning.

The risk alert engine is rules-based and explainable. It generates alerts for:

- Single-stock concentration above 25%
- High single-stock concentration above 35%
- Sector concentration above 50%
- High sector concentration above 60%
- Holding down more than 10% versus average buy price
- Holding up more than 20% versus average buy price
- Low-liquidity stocks held in the portfolio
- High-volatility stocks held in the portfolio
- Missing price data
- Existing holdings with a SELL / AVOID research signal

Portfolio endpoints:

- `POST /portfolios`
- `GET /portfolios/{id}`
- `POST /portfolios/{id}/holdings`
- `PUT /portfolios/{id}/holdings/{holding_id}`
- `DELETE /portfolios/{id}/holdings/{holding_id}`
- `GET /portfolios/{id}/summary`
- `GET /portfolios/{id}/risk-alerts`

Risk alerts are research-only and return `alert_type`, `severity`, `symbol`, `message`, and `recommended_action`. The app never places orders or executes trades.

## Run Locally

1. Copy environment values:

```bash
copy .env.example .env
```

2. Start PostgreSQL and the FastAPI backend:

```bash
docker compose up --build
```

The API will run at `http://127.0.0.1:8000`.
API docs are available at `http://127.0.0.1:8000/docs`.

3. In a second terminal, install frontend dependencies and start Next.js:

```bash
npm install
npm run dev:web
```

The Next.js MVP dashboard will run at `http://127.0.0.1:3000`.

On Windows, if PowerShell blocks `npm.ps1`, run npm through `npm.cmd`:

```powershell
& "C:\Program Files\nodejs\npm.cmd" install
& "C:\Program Files\nodejs\npm.cmd" run dev:web
```

The old Vite prototype can still run with:

```bash
npm run legacy:dev
```

Run backend unit tests:

```bash
python -m pytest
```

Run the frontend and prototype checks:

```bash
npm run test:web
npm run build:web
npm run legacy:check
```

On Windows, if the Next.js build reports a process-spawn permission error, run the build through Node directly from the web workspace:

```powershell
cd apps\web
& "C:\Program Files\nodejs\node.exe" ..\..\node_modules\next\dist\bin\next build
```

Current verification for the portfolio tracker and risk alert engine:

- Backend unit tests: `17 passed`
- Next.js production build: passed
- Frontend dashboard tests: passed
- Legacy TypeScript check: passed

## Frontend Dashboard

The Next.js dashboard connects to the FastAPI analytics endpoints and falls back to local mock data when the API is unavailable. The main page shows ranked Moroccan equities with research signal, confidence, risk level, latest MAD price, and 1M / 3M momentum. Stock detail pages are available at `/stocks/{symbol}` and show company profile, sector, latest price, ranking score, signal explanation, technical indicators, and risk warnings.

The portfolio section uses the portfolio summary and risk alert endpoints to show current MAD value, unrealized P&L, stock allocation, sector allocation, and active risk alerts. Every dashboard surface keeps the MVP disclaimer visible: `This is market analytics only, not financial advice.`

## Market Data Ingestion

Daily Casablanca Stock Exchange prices can be imported through the admin CSV endpoint:

```bash
curl -X POST http://127.0.0.1:8000/admin/import-prices \
  -H "Content-Type: text/csv" \
  --data-binary @prices.csv
```

Required CSV columns:

```csv
symbol,date,open,high,low,close,volume
ATW,2026-05-01,480,486,476,482,145000
IAM,2026-05-01,91,92,90,91,220000
```

Optional columns are `adjusted_close`, `traded_value`, and `market_cap`. Dates must use ISO format: `YYYY-MM-DD`. Prices are MAD-denominated. The importer validates symbols against active listed securities, rejects invalid rows safely, skips duplicate symbol/date records, and stores clean rows in `daily_ohlcv_prices`.

Admin market-data endpoints:

- `POST /admin/import-prices`: import CSV daily OHLCV data from the request body.
- `GET /admin/import-status`: view the latest import or refresh job status.
- `GET /admin/data-quality-report`: inspect quality issues across stored prices.
- `POST /admin/daily-refresh`: manually trigger the scheduled refresh structure.

Data quality rules flag:

- Missing close price
- Negative prices
- Zero volume
- Duplicate symbol/date records
- Stale prices older than 7 days
- Large unexplained close-to-close moves above 15%

Known limitations: this MVP does not yet connect to an official CSE data provider, reconcile corporate actions, backfill holidays, or authenticate admin endpoints. Before production, admin routes need authentication, source allowlisting, provider-specific adapters, and an operations runbook.

## Ranking and Signal Logic

The backend uses a transparent, rules-based ranking engine for Casablanca Stock Exchange equities. It does not use black-box AI and does not execute trades.

Technical inputs:

- 20-day moving average
- 50-day moving average
- RSI 14
- 30-day volatility
- 1-month momentum
- 3-month momentum
- Average daily traded value in MAD

Ranking score, 0-100:

- 30% momentum
- 20% trend
- 20% liquidity
- 15% volatility
- 15% RSI / technical strength

Signal rules:

- `BUY`: score >= 75 and liquidity is acceptable
- `HOLD`: score between 50 and 74
- `SELL`: score < 50 or liquidity is weak

If required indicator data is missing or invalid, the engine fails safely with `SELL` / `AVOID`, a `0` ranking score, and a `missing_data` explanation instead of producing a misleading positive signal.

## Project Structure

- `apps/web`: Next.js dashboard, stock assistant UI, and charts.
- `apps/api`: FastAPI backend, routers, services, schemas, and ML stubs.
- `infra/db`: PostgreSQL schema and seed data.
- `docs`: MVP, architecture, and compliance notes.
- `src`: preserved legacy React/Vite prototype.

## Important Disclaimer

This project does not provide financial advice, investment recommendations, or live trading execution. Any production trading app for Moroccan retail investors should be reviewed with qualified legal, compliance, cybersecurity, and financial-market experts before launch.
