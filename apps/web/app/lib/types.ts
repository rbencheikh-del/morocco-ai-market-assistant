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
};

export type Portfolio = {
  id: string;
  name: string;
  base_currency: string;
  total_value_mad: number;
  holdings: Array<{
    ticker: string;
    quantity: number;
    average_cost_mad: number;
    current_price_mad: number;
    market_value_mad: number;
    unrealized_pl_mad: number;
    allocation_pct: number;
    manual_note?: string;
  }>;
};

export type RiskAlert = {
  id: string;
  severity: "low" | "medium" | "high";
  title: string;
  detail: string;
  ticker?: string;
  created_at: string;
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
  portfolio: Portfolio;
  alerts: RiskAlert[];
};
