export type RankedStock = {
  ticker: string;
  name: string;
  sector: string;
  ai_score: number;
  rank_position: number;
  liquidity_score: number;
  quality_score: number;
  momentum_score: number;
  risk_score: number;
  rationale: string;
  signal: "BUY" | "HOLD" | "SELL";
  confidence: number;
  reason: string;
  risk_note: string;
  latest_price_mad?: number;
  momentum_1m?: number;
  momentum_3m?: number;
};

export type Signal = {
  ticker: string;
  signal_date: string;
  signal: "BUY" | "HOLD" | "SELL";
  confidence: number;
  reason: string;
  risk_note: string;
  model_version: string;
};

export type MarketSnapshot = {
  ticker: string;
  as_of: string;
  price_mad: number;
  volume: number;
  momentum_90d?: number;
  volatility_30d?: number;
};

export type PortfolioHolding = {
  ticker: string;
  sector?: string;
  quantity: number;
  average_cost_mad: number;
  current_price_mad: number;
  market_value_mad: number;
  unrealized_pl_mad: number;
  unrealized_pl_pct?: number;
  allocation_pct: number;
  manual_note?: string;
};

export type PortfolioSummary = {
  portfolio_id: string;
  portfolio_name: string;
  base_currency: string;
  cost_basis_mad: number;
  current_value_mad: number;
  unrealized_pl_mad: number;
  unrealized_pl_pct: number;
  sector_allocations: Record<string, number>;
  data_quality_warnings: string[];
  holdings: PortfolioHolding[];
};

export type RiskAlert = {
  id?: string;
  severity: "low" | "medium" | "high" | "Low" | "Medium" | "High";
  alert_type?: string;
  title?: string;
  detail?: string;
  ticker?: string;
  symbol?: string;
  message?: string;
  recommended_action?: string;
  created_at?: string;
};

export type StockDetail = {
  ticker: string;
  name: string;
  sector: string;
  latest_price_mad?: number;
  latest_price_as_of?: string;
  latest_close_mad?: number;
  latest_close_date?: string;
  ai_score?: number;
  rank_position?: number;
  signal?: "BUY" | "HOLD" | "SELL";
  confidence?: number;
  risk_note?: string;
};

export type StockDetailData = {
  stock: StockDetail;
  ranking?: RankedStock;
  signal?: Signal;
  snapshot?: MarketSnapshot;
};

export type AskResponse = {
  answer: string;
  tickers: string[];
  citations: string[];
  disclaimer: string;
  audit_id: string;
};

export type DashboardData = {
  rankings: RankedStock[];
  signals: Signal[];
  snapshots: MarketSnapshot[];
  portfolio: PortfolioSummary;
  alerts: RiskAlert[];
};
