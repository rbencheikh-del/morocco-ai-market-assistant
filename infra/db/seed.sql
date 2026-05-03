INSERT INTO exchanges (code, name, country_code, currency, timezone) VALUES
  ('CSE', 'Casablanca Stock Exchange', 'MA', 'MAD', 'Africa/Casablanca')
ON CONFLICT (code) DO NOTHING;

INSERT INTO securities (
  ticker,
  isin,
  name,
  short_name,
  sector,
  industry,
  exchange_code,
  exchange,
  shares_outstanding,
  free_float_pct
) VALUES
  ('ATW', 'MA0000012445', 'Attijariwafa Bank', 'Attijariwafa', 'Banking', 'Commercial Banking', 'CSE', 'Casablanca Stock Exchange', 203527226, 0.3000),
  ('IAM', 'MA0000011488', 'Maroc Telecom', 'IAM', 'Telecom', 'Telecommunications', 'CSE', 'Casablanca Stock Exchange', 879095340, 0.1700),
  ('LHM', 'MA0000012320', 'LafargeHolcim Maroc', 'LafargeHolcim', 'Materials', 'Construction Materials', 'CSE', 'Casablanca Stock Exchange', 23431240, 0.2500),
  ('TQM', 'MA0000012395', 'Taqa Morocco', 'Taqa Morocco', 'Utilities', 'Independent Power Producers', 'CSE', 'Casablanca Stock Exchange', 23595412, 0.1500),
  ('BOA', 'MA0000012437', 'Bank of Africa', 'BOA', 'Banking', 'Commercial Banking', 'CSE', 'Casablanca Stock Exchange', 215140839, 0.2700),
  ('MNG', 'MA0000011058', 'Managem', 'Managem', 'Mining', 'Metals and Mining', 'CSE', 'Casablanca Stock Exchange', 9991308, 0.1900),
  ('BCP', 'MA0000011884', 'Banque Centrale Populaire', 'BCP', 'Banking', 'Commercial Banking', 'CSE', 'Casablanca Stock Exchange', 203312473, 0.2100),
  ('AKT', 'MA0000012585', 'Akdital', 'Akdital', 'Healthcare', 'Healthcare Facilities', 'CSE', 'Casablanca Stock Exchange', 12666667, 0.3500)
ON CONFLICT (ticker) DO NOTHING;

INSERT INTO daily_ohlcv_prices (
  security_id,
  ticker,
  price_date,
  open_mad,
  high_mad,
  low_mad,
  close_mad,
  adjusted_close_mad,
  volume,
  traded_value_mad,
  market_cap_mad,
  data_source
)
SELECT s.id, p.ticker, p.price_date, p.open_mad, p.high_mad, p.low_mad, p.close_mad, p.adjusted_close_mad, p.volume, p.traded_value_mad, p.market_cap_mad, 'mock'
FROM securities s
JOIN (
  VALUES
    ('ATW', DATE '2026-04-29', 468.00, 477.00, 466.00, 474.00, 474.00, 121000, 57354000, 96411845124),
    ('ATW', DATE '2026-04-30', 474.00, 482.00, 472.00, 480.00, 480.00, 145000, 69600000, 97693068480),
    ('IAM', DATE '2026-04-29', 90.10, 91.80, 89.80, 90.70, 90.70, 198000, 17958600, 79793927538),
    ('IAM', DATE '2026-04-30', 90.70, 91.50, 90.20, 91.00, 91.00, 220000, 20020000, 79997675940),
    ('LHM', DATE '2026-04-29', 1748.00, 1788.00, 1742.00, 1765.00, 1765.00, 7200, 12708000, 41351738600),
    ('LHM', DATE '2026-04-30', 1765.00, 1795.00, 1760.00, 1780.00, 1780.00, 9800, 17444000, 41703207200),
    ('TQM', DATE '2026-04-29', 1020.00, 1045.00, 1015.00, 1034.00, 1034.00, 6400, 6617600, 24403756008),
    ('TQM', DATE '2026-04-30', 1034.00, 1048.00, 1030.00, 1040.00, 1040.00, 7600, 7904000, 24545308480),
    ('BOA', DATE '2026-04-29', 181.50, 185.50, 181.00, 184.00, 184.00, 73500, 13524000, 39585914376),
    ('BOA', DATE '2026-04-30', 184.00, 187.00, 183.00, 185.00, 185.00, 84000, 15540000, 39801055215),
    ('MNG', DATE '2026-04-29', 2135.00, 2190.00, 2120.00, 2168.00, 2168.00, 3600, 7804800, 21661275744),
    ('MNG', DATE '2026-04-30', 2168.00, 2210.00, 2155.00, 2180.00, 2180.00, 4100, 8938000, 21781111440),
    ('BCP', DATE '2026-04-29', 281.00, 286.50, 280.00, 284.00, 284.00, 59000, 16756000, 57700742332),
    ('BCP', DATE '2026-04-30', 284.00, 288.00, 283.00, 286.00, 286.00, 67000, 19162000, 58107367278),
    ('AKT', DATE '2026-04-29', 742.00, 764.00, 738.00, 752.00, 752.00, 29100, 21883200, 9525333584),
    ('AKT', DATE '2026-04-30', 752.00, 770.00, 750.00, 760.00, 760.00, 32500, 24700000, 9626666920)
) AS p(ticker, price_date, open_mad, high_mad, low_mad, close_mad, adjusted_close_mad, volume, traded_value_mad, market_cap_mad)
  ON s.ticker = p.ticker
ON CONFLICT (security_id, price_date) DO NOTHING;

INSERT INTO market_snapshots (ticker, as_of, price_mad, volume, market_cap_mad, dividend_yield, volatility_30d, momentum_90d, data_source) VALUES
  ('ATW', NOW(), 480.00, 145000, 97693068480, 0.0350, 0.1180, 0.0720, 'mock'),
  ('IAM', NOW(), 91.00, 220000, 79997675940, 0.0410, 0.0920, 0.0310, 'mock'),
  ('LHM', NOW(), 1780.00, 9800, 41703207200, 0.0280, 0.1640, 0.0850, 'mock'),
  ('TQM', NOW(), 1040.00, 7600, 24545308480, 0.0390, 0.1270, 0.0240, 'mock'),
  ('BOA', NOW(), 185.00, 84000, 39801055215, 0.0300, 0.1430, 0.0660, 'mock'),
  ('MNG', NOW(), 2180.00, 4100, 21781111440, 0.0150, 0.2120, 0.1120, 'mock'),
  ('BCP', NOW(), 286.00, 67000, 58107367278, 0.0330, 0.1320, 0.0440, 'mock'),
  ('AKT', NOW(), 760.00, 32500, 9626666920, 0.0000, 0.1880, 0.1560, 'mock')
ON CONFLICT (ticker, as_of) DO NOTHING;

INSERT INTO stock_rankings (ticker, rank_date, ai_score, rank_position, liquidity_score, quality_score, momentum_score, risk_score, rationale, model_version, feature_payload) VALUES
  ('ATW', CURRENT_DATE, 84, 1, 87, 88, 72, 38, 'High quality and liquidity, but banking concentration needs monitoring.', 'ranking-mock-v1', '{"liquidity":"high","sector_weight":"banking"}'),
  ('IAM', CURRENT_DATE, 79, 2, 82, 80, 55, 30, 'Defensive dividend profile with lower volatility.', 'ranking-mock-v1', '{"dividend_profile":"defensive"}'),
  ('LHM', CURRENT_DATE, 74, 3, 62, 76, 73, 61, 'Improving volume and trend, but concentration risk can be high.', 'ranking-mock-v1', '{"concentration_watch":true}'),
  ('TQM', CURRENT_DATE, 71, 4, 58, 74, 49, 44, 'Defensive cash-flow profile with neutral momentum.', 'ranking-mock-v1', '{"cash_flow_profile":"defensive"}'),
  ('BOA', CURRENT_DATE, 68, 5, 75, 68, 66, 52, 'Momentum is improving but confidence is below top-ranked names.', 'ranking-mock-v1', '{"sector_overlap":"banking"}'),
  ('AKT', CURRENT_DATE, 66, 6, 64, 61, 82, 68, 'Strong momentum but elevated volatility for retail portfolios.', 'ranking-mock-v1', '{"volatility":"elevated"}'),
  ('BCP', CURRENT_DATE, 64, 7, 72, 66, 44, 49, 'Banking exposure overlaps with ATW and BOA.', 'ranking-mock-v1', '{"sector_overlap":"banking"}'),
  ('MNG', CURRENT_DATE, 61, 8, 45, 59, 70, 76, 'Higher volatility and lower liquidity require caution.', 'ranking-mock-v1', '{"liquidity":"lower","volatility":"high"}')
ON CONFLICT (ticker, rank_date) DO NOTHING;

INSERT INTO stock_signals (ticker, signal_date, signal, confidence, risk_profile, horizon, reason, risk_note, model_version, feature_payload) VALUES
  ('ATW', CURRENT_DATE, 'HOLD', 76, 'balanced', 'swing', 'Quality and liquidity are strong, but sector exposure is already meaningful.', 'Watch banking concentration.', 'signal-mock-v1', '{"ranking_score":84}'),
  ('IAM', CURRENT_DATE, 'BUY', 73, 'balanced', 'swing', 'Defensive dividend profile fits balanced manual portfolios.', 'Confirm latest source timestamp before relying on signal.', 'signal-mock-v1', '{"ranking_score":79}'),
  ('LHM', CURRENT_DATE, 'SELL', 69, 'balanced', 'swing', 'Manual portfolio concentration is high relative to the risk profile.', 'Review single-name exposure.', 'signal-mock-v1', '{"ranking_score":74}'),
  ('TQM', CURRENT_DATE, 'HOLD', 66, 'balanced', 'swing', 'Useful defensive cash-flow exposure with neutral entry timing.', 'Monitor volatility.', 'signal-mock-v1', '{"ranking_score":71}'),
  ('BOA', CURRENT_DATE, 'HOLD', 62, 'balanced', 'swing', 'Momentum is improving but confidence remains below top names.', 'Avoid over-adding banking exposure.', 'signal-mock-v1', '{"ranking_score":68}')
ON CONFLICT (ticker, signal_date, risk_profile, horizon) DO NOTHING;

INSERT INTO users (email, display_name, risk_profile, preferred_language) VALUES
  ('demo@market-assistant.local', 'Demo Investor', 'balanced', 'en')
ON CONFLICT (email) DO NOTHING;

INSERT INTO manual_portfolios (user_id, name, risk_profile, is_default)
SELECT id, 'Demo Manual Portfolio', 'balanced', TRUE
FROM users
WHERE email = 'demo@market-assistant.local'
ON CONFLICT (user_id, name) DO NOTHING;

INSERT INTO portfolio_holdings (portfolio_id, ticker, quantity, average_cost_mad, manual_note, opened_at)
SELECT p.id, h.ticker, h.quantity, h.average_cost_mad, h.manual_note, DATE '2026-04-01'
FROM manual_portfolios p
CROSS JOIN (
  VALUES
    ('ATW', 60, 462.00, 'Core banking position'),
    ('IAM', 250, 91.00, 'Defensive dividend exposure'),
    ('LHM', 30, 1780.00, 'High concentration, review'),
    ('TQM', 18, 1040.00, 'Utilities exposure'),
    ('BOA', 120, 185.00, 'Banking overlap with ATW')
) AS h(ticker, quantity, average_cost_mad, manual_note)
WHERE p.name = 'Demo Manual Portfolio'
ON CONFLICT (portfolio_id, ticker) DO NOTHING;

INSERT INTO watchlists (user_id, name, description, is_default)
SELECT id, 'Casablanca Core Watchlist', 'Large and liquid Moroccan listed equities for MVP research.', TRUE
FROM users
WHERE email = 'demo@market-assistant.local'
ON CONFLICT (user_id, name) DO NOTHING;

INSERT INTO watchlist_items (watchlist_id, ticker, user_note, alert_above_mad, alert_below_mad)
SELECT w.id, i.ticker, i.user_note, i.alert_above_mad, i.alert_below_mad
FROM watchlists w
CROSS JOIN (
  VALUES
    ('ATW', 'Track banking exposure before adding.', 510.00, 450.00),
    ('IAM', 'Defensive candidate for balanced profile.', 98.00, 86.00),
    ('LHM', 'Monitor concentration and construction cycle.', 1850.00, 1690.00),
    ('AKT', 'High momentum healthcare name.', 810.00, 710.00),
    ('MNG', 'Volatile mining exposure.', 2320.00, 2020.00)
) AS i(ticker, user_note, alert_above_mad, alert_below_mad)
WHERE w.name = 'Casablanca Core Watchlist'
ON CONFLICT (watchlist_id, ticker) DO NOTHING;

INSERT INTO risk_alerts (user_id, portfolio_id, ticker, alert_type, severity, title, detail, trigger_payload)
SELECT p.user_id, p.id, 'LHM', 'concentration', 'high', 'Single-stock concentration', 'LHM represents a large share of the manual portfolio.', '{"allocation_pct":36.61,"threshold_pct":25}'
FROM manual_portfolios p
WHERE p.name = 'Demo Manual Portfolio';

INSERT INTO risk_alerts (user_id, portfolio_id, ticker, alert_type, severity, title, detail, trigger_payload)
SELECT p.user_id, p.id, NULL, 'portfolio_risk', 'medium', 'Banking sector exposure', 'ATW and BOA together create meaningful banking-sector concentration.', '{"sector":"Banking","tickers":["ATW","BOA"]}'
FROM manual_portfolios p
WHERE p.name = 'Demo Manual Portfolio';
