CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS exchanges (
  code TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  country_code CHAR(2) NOT NULL,
  currency CHAR(3) NOT NULL,
  timezone TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS securities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  ticker TEXT NOT NULL UNIQUE,
  isin TEXT UNIQUE,
  name TEXT NOT NULL,
  short_name TEXT,
  sector TEXT NOT NULL,
  industry TEXT,
  exchange_code TEXT NOT NULL DEFAULT 'CSE' REFERENCES exchanges(code),
  exchange TEXT NOT NULL DEFAULT 'Casablanca Stock Exchange',
  country_code CHAR(2) NOT NULL DEFAULT 'MA',
  currency CHAR(3) NOT NULL DEFAULT 'MAD',
  listing_date DATE,
  free_float_pct NUMERIC(8, 4),
  shares_outstanding NUMERIC(20, 4),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_ohlcv_prices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  security_id UUID NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
  ticker TEXT NOT NULL REFERENCES securities(ticker) ON UPDATE CASCADE,
  price_date DATE NOT NULL,
  open_mad NUMERIC(14, 2) NOT NULL CHECK (open_mad >= 0),
  high_mad NUMERIC(14, 2) NOT NULL CHECK (high_mad >= 0),
  low_mad NUMERIC(14, 2) NOT NULL CHECK (low_mad >= 0),
  close_mad NUMERIC(14, 2) NOT NULL CHECK (close_mad >= 0),
  adjusted_close_mad NUMERIC(14, 2),
  volume NUMERIC(18, 2) NOT NULL DEFAULT 0 CHECK (volume >= 0),
  traded_value_mad NUMERIC(20, 2),
  market_cap_mad NUMERIC(20, 2),
  data_source TEXT NOT NULL DEFAULT 'mock',
  ingestion_batch_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (security_id, price_date),
  CHECK (high_mad >= low_mad),
  CHECK (high_mad >= open_mad AND high_mad >= close_mad),
  CHECK (low_mad <= open_mad AND low_mad <= close_mad)
);

CREATE TABLE IF NOT EXISTS market_data_import_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_name TEXT NOT NULL DEFAULT 'csv_upload',
  status TEXT NOT NULL CHECK (status IN ('success', 'partial_success', 'failed')),
  rows_received INTEGER NOT NULL DEFAULT 0,
  rows_inserted INTEGER NOT NULL DEFAULT 0,
  rows_rejected INTEGER NOT NULL DEFAULT 0,
  rows_duplicate INTEGER NOT NULL DEFAULT 0,
  warning_count INTEGER NOT NULL DEFAULT 0,
  error_message TEXT,
  import_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS market_snapshots (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  ticker TEXT NOT NULL REFERENCES securities(ticker) ON UPDATE CASCADE,
  as_of TIMESTAMPTZ NOT NULL,
  price_mad NUMERIC(14, 2) NOT NULL,
  volume NUMERIC(18, 2) NOT NULL,
  market_cap_mad NUMERIC(20, 2),
  dividend_yield NUMERIC(8, 4),
  volatility_30d NUMERIC(8, 4),
  momentum_90d NUMERIC(8, 4),
  data_source TEXT NOT NULL DEFAULT 'mock',
  UNIQUE (ticker, as_of)
);

CREATE TABLE IF NOT EXISTS stock_rankings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  ticker TEXT NOT NULL REFERENCES securities(ticker) ON UPDATE CASCADE,
  rank_date DATE NOT NULL,
  ai_score INTEGER NOT NULL CHECK (ai_score BETWEEN 0 AND 100),
  rank_position INTEGER NOT NULL CHECK (rank_position > 0),
  liquidity_score INTEGER NOT NULL CHECK (liquidity_score BETWEEN 0 AND 100),
  quality_score INTEGER NOT NULL CHECK (quality_score BETWEEN 0 AND 100),
  momentum_score INTEGER NOT NULL CHECK (momentum_score BETWEEN 0 AND 100),
  risk_score INTEGER NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
  rationale TEXT NOT NULL,
  model_version TEXT NOT NULL DEFAULT 'ranking-mock-v1',
  feature_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (ticker, rank_date),
  UNIQUE (rank_date, rank_position)
);

CREATE TABLE IF NOT EXISTS stock_signals (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  ticker TEXT NOT NULL REFERENCES securities(ticker) ON UPDATE CASCADE,
  signal_date DATE NOT NULL,
  signal TEXT NOT NULL CHECK (signal IN ('BUY', 'HOLD', 'SELL')),
  confidence INTEGER NOT NULL CHECK (confidence BETWEEN 0 AND 100),
  risk_profile TEXT NOT NULL DEFAULT 'balanced' CHECK (risk_profile IN ('conservative', 'balanced', 'growth', 'speculative')),
  horizon TEXT NOT NULL DEFAULT 'swing' CHECK (horizon IN ('intraday', 'swing', 'position', 'long_term')),
  reason TEXT NOT NULL,
  risk_note TEXT NOT NULL,
  source_snapshot_id UUID REFERENCES market_snapshots(id),
  source_price_id UUID REFERENCES daily_ohlcv_prices(id),
  model_version TEXT NOT NULL DEFAULT 'signal-mock-v1',
  feature_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  disclaimer TEXT NOT NULL DEFAULT 'Research support only. Not financial advice. No trade execution.',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (ticker, signal_date, risk_profile, horizon)
);

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  risk_profile TEXT NOT NULL CHECK (risk_profile IN ('conservative', 'balanced', 'growth', 'speculative')),
  preferred_language TEXT NOT NULL DEFAULT 'en' CHECK (preferred_language IN ('en', 'fr', 'ar')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS manual_portfolios (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  base_currency CHAR(3) NOT NULL DEFAULT 'MAD',
  risk_profile TEXT NOT NULL DEFAULT 'balanced' CHECK (risk_profile IN ('conservative', 'balanced', 'growth', 'speculative')),
  is_default BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (user_id, name)
);

CREATE TABLE IF NOT EXISTS portfolio_holdings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  portfolio_id UUID NOT NULL REFERENCES manual_portfolios(id) ON DELETE CASCADE,
  ticker TEXT NOT NULL REFERENCES securities(ticker) ON UPDATE CASCADE,
  quantity NUMERIC(18, 4) NOT NULL CHECK (quantity >= 0),
  average_cost_mad NUMERIC(14, 2) NOT NULL CHECK (average_cost_mad >= 0),
  manual_note TEXT,
  opened_at DATE,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (portfolio_id, ticker)
);

CREATE TABLE IF NOT EXISTS watchlists (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  is_default BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (user_id, name)
);

CREATE TABLE IF NOT EXISTS watchlist_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  watchlist_id UUID NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
  ticker TEXT NOT NULL REFERENCES securities(ticker) ON UPDATE CASCADE,
  added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  user_note TEXT,
  alert_above_mad NUMERIC(14, 2),
  alert_below_mad NUMERIC(14, 2),
  UNIQUE (watchlist_id, ticker)
);

CREATE TABLE IF NOT EXISTS risk_alerts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  portfolio_id UUID REFERENCES manual_portfolios(id) ON DELETE CASCADE,
  watchlist_id UUID REFERENCES watchlists(id) ON DELETE CASCADE,
  ticker TEXT REFERENCES securities(ticker) ON UPDATE CASCADE,
  alert_type TEXT NOT NULL CHECK (alert_type IN ('price', 'signal', 'portfolio_risk', 'concentration', 'volatility', 'data_quality')),
  severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high')),
  title TEXT NOT NULL,
  detail TEXT NOT NULL,
  trigger_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
  resolved_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CHECK (
    (is_resolved = FALSE AND resolved_at IS NULL)
    OR (is_resolved = TRUE AND resolved_at IS NOT NULL)
  )
);

CREATE TABLE IF NOT EXISTS model_audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  request_type TEXT NOT NULL,
  prompt TEXT,
  input_payload JSONB NOT NULL,
  output_payload JSONB NOT NULL,
  model_version TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_securities_exchange_sector ON securities(exchange_code, sector, is_active);
CREATE INDEX IF NOT EXISTS idx_daily_ohlcv_ticker_date ON daily_ohlcv_prices(ticker, price_date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_ohlcv_security_date ON daily_ohlcv_prices(security_id, price_date DESC);
CREATE INDEX IF NOT EXISTS idx_import_logs_started ON market_data_import_logs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_market_snapshots_ticker_as_of ON market_snapshots(ticker, as_of DESC);
CREATE INDEX IF NOT EXISTS idx_rankings_rank_date ON stock_rankings(rank_date, rank_position);
CREATE INDEX IF NOT EXISTS idx_rankings_ticker_date ON stock_rankings(ticker, rank_date DESC);
CREATE INDEX IF NOT EXISTS idx_signals_signal_date ON stock_signals(signal_date, ticker);
CREATE INDEX IF NOT EXISTS idx_signals_ticker_profile ON stock_signals(ticker, risk_profile, signal_date DESC);
CREATE INDEX IF NOT EXISTS idx_portfolios_user ON manual_portfolios(user_id, is_default);
CREATE INDEX IF NOT EXISTS idx_holdings_portfolio ON portfolio_holdings(portfolio_id, ticker);
CREATE INDEX IF NOT EXISTS idx_watchlists_user ON watchlists(user_id, is_default);
CREATE INDEX IF NOT EXISTS idx_watchlist_items_watchlist ON watchlist_items(watchlist_id, ticker);
CREATE INDEX IF NOT EXISTS idx_alerts_user_created ON risk_alerts(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_portfolio ON risk_alerts(portfolio_id, severity);
CREATE INDEX IF NOT EXISTS idx_audit_user_created ON model_audit_logs(user_id, created_at DESC);
