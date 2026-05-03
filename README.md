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

## Project Structure

- `apps/web`: Next.js dashboard, stock assistant UI, and charts.
- `apps/api`: FastAPI backend, routers, services, schemas, and ML stubs.
- `infra/db`: PostgreSQL schema and seed data.
- `docs`: MVP, architecture, and compliance notes.
- `src`: preserved legacy React/Vite prototype.

## Important Disclaimer

This project does not provide financial advice, investment recommendations, or live trading execution. Any production trading app for Moroccan retail investors should be reviewed with qualified legal, compliance, cybersecurity, and financial-market experts before launch.
