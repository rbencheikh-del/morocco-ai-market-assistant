# PostgreSQL Schema

## Core Market Tables

- `exchanges`: Exchange metadata. The MVP seeds `CSE` for the Casablanca Stock Exchange.
- `securities`: Moroccan listed equities, including ticker, ISIN, company name, sector, industry, currency, listing metadata, float, shares outstanding, and active status.
- `daily_ohlcv_prices`: Daily OHLCV market data in MAD, with adjusted close, traded value, market cap, data source, and ingestion batch tracking.
- `market_snapshots`: Latest or intraday-style snapshots used by the current dashboard and signal pipeline.

## Research Tables

- `stock_rankings`: Daily ranked equities with liquidity, quality, momentum, risk, rationale, model version, and feature payload.
- `stock_signals`: Buy/hold/sell research signals by risk profile and horizon, with confidence, reasons, risk notes, source price links, model version, features, and disclaimers.
- `model_audit_logs`: Assistant and model-request audit trail for compliance review.

## User Product Tables

- `users`: Demo user identity, risk profile, and language preference.
- `manual_portfolios`: User-created manual portfolios. No broker, account, order, or execution tables exist.
- `portfolio_holdings`: Manually tracked holdings with quantity, average cost, and notes.
- `watchlists`: User watchlists for tracked Moroccan equities.
- `watchlist_items`: Watchlist tickers, notes, and simple price alert thresholds.
- `risk_alerts`: Portfolio, watchlist, price, signal, volatility, concentration, and data-quality alerts with severity, trigger payload, and resolution lifecycle.

## API Coverage

- `GET /market/securities`
- `GET /stocks`
- `GET /stocks/{ticker}`
- `GET /market/prices/{ticker}/daily`
- `GET /market/snapshots/latest`
- `GET /rankings`
- `GET /rankings/{ticker}`
- `GET /signals`
- `POST /signals/rules`
- `POST /signals/explain`
- `GET /portfolio/demo`
- `POST /portfolio/{portfolio_id}/holdings`
- `GET /portfolio/{portfolio_id}/pnl`
- `GET /watchlists`
- `GET /alerts`
- `POST /alerts/generate`

## Guardrail

The schema intentionally excludes live trading entities such as broker accounts, orders, executions, deposits, withdrawals, custody records, and settlement records.
