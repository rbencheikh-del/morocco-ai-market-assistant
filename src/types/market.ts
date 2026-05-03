export type Tone = "positive" | "neutral" | "negative";

export type MarketSummaryItem = {
  label: string;
  value: string;
  detail: string;
  tone: Tone;
};

export type PortfolioPoint = {
  label: string;
  value: number;
};

export type PortfolioSeries = {
  "1M": PortfolioPoint[];
  "6M": PortfolioPoint[];
  "1Y": PortfolioPoint[];
};

export type WatchlistItem = {
  ticker: string;
  name: string;
  sector: string;
  score: number;
  stance: string;
  signal: "Buy" | "Hold" | "Sell";
  reason: string;
  alert: string;
};

export type AiSignal = {
  confidence: number;
  label: string;
  narrative: string;
  title: string;
  tone: Tone;
};

export type RiskMode = "low" | "medium" | "high";

export type DummyHolding = {
  ticker: string;
  name: string;
  sector: string;
  shares: number;
  priceMad: number;
  valueMad: number;
  allocation: number;
  aiAction: "Buy" | "Hold" | "Sell";
  aiScore: number;
};

export type RiskAlert = {
  title: string;
  detail: string;
  severity: "low" | "medium" | "high";
};

export type RiskSimulation = {
  mode: RiskMode;
  title: string;
  expectedReturn: number;
  simulatedRevenueMad: number;
  projectedValueMad: number;
  maxDrawdown: number;
  volatility: number;
  winRate: number;
  tradeCount: number;
  aiSummary: string;
  recommendedTrades: string[];
};
