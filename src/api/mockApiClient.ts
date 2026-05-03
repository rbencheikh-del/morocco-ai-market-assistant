import { marketSummary, portfolioSeries, watchlist } from "../data/mockMarketData";
import { buildRiskSignal } from "../services/aiSignalService";
import type { MarketSnapshotResponse, PortfolioSnapshot, SignalRequest, SignalResponse } from "./contracts";

const EDUCATIONAL_DISCLAIMER =
  "Maroq provides educational decision support only and does not provide financial advice or execute trades.";

export async function getMarketSnapshot(): Promise<MarketSnapshotResponse> {
  return {
    asOf: new Date().toISOString(),
    summary: marketSummary,
    watchlist,
  };
}

export async function getPortfolioSnapshot(): Promise<PortfolioSnapshot> {
  return {
    cashMad: 18000,
    holdings: [
      { averageCostMad: 462, marketValueMad: 28800, quantity: 60, ticker: "ATW" },
      { averageCostMad: 91, marketValueMad: 22750, quantity: 250, ticker: "IAM" },
      { averageCostMad: 1780, marketValueMad: 53400, quantity: 30, ticker: "LHM" },
    ],
    totalValueMad: 122950,
    valueHistory: portfolioSeries["1M"],
  };
}

export async function requestAiSignal(request: SignalRequest): Promise<SignalResponse> {
  const signal = buildRiskSignal(request.riskProfile.riskScore);
  const suitabilityWarnings =
    request.riskProfile.maximumDrawdownTolerance < 10
      ? ["Current risk profile suggests using conservative allocation limits before placing any order."]
      : [];

  return {
    auditId: crypto.randomUUID(),
    disclaimer: EDUCATIONAL_DISCLAIMER,
    signal,
    suitabilityWarnings,
  };
}
