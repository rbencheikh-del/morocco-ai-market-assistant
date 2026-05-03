import type { AiSignal, MarketSummaryItem, PortfolioPoint, WatchlistItem } from "../types/market";

export type UserRiskProfile = {
  investmentHorizon: "short" | "medium" | "long";
  monthlyIncomeMad?: number;
  maximumDrawdownTolerance: number;
  riskScore: number;
};

export type PortfolioHolding = {
  averageCostMad: number;
  marketValueMad: number;
  quantity: number;
  ticker: string;
};

export type PortfolioSnapshot = {
  cashMad: number;
  holdings: PortfolioHolding[];
  totalValueMad: number;
  valueHistory: PortfolioPoint[];
};

export type MarketSnapshotResponse = {
  asOf: string;
  summary: MarketSummaryItem[];
  watchlist: WatchlistItem[];
};

export type SignalRequest = {
  holdings: PortfolioHolding[];
  riskProfile: UserRiskProfile;
  watchlistTickers: string[];
};

export type SignalResponse = {
  auditId: string;
  disclaimer: string;
  signal: AiSignal;
  suitabilityWarnings: string[];
};
