import { mockDashboardData } from "./mockData";
import type { AskResponse, DashboardData, MarketSnapshot, PortfolioSummary, RankedStock, Signal, StockDetailData } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { next: { revalidate: 30 } });
  if (!response.ok) {
    throw new Error(`API request failed: ${path}`);
  }
  return response.json() as Promise<T>;
}

export async function getDashboardData(): Promise<DashboardData> {
  try {
    const [rankings, signals, snapshots, demoPortfolio] = await Promise.all([
      getJson<RankedStock[]>("/rankings"),
      getJson<Signal[]>("/signals"),
      getJson<MarketSnapshot[]>("/market/snapshots/latest"),
      getJson<{ id: string }>("/portfolio/demo"),
    ]);

    const [portfolio, alerts] = await Promise.all([
      getJson<PortfolioSummary>(`/portfolios/${demoPortfolio.id}/summary`),
      getJson<DashboardData["alerts"]>(`/portfolios/${demoPortfolio.id}/risk-alerts`),
    ]);

    const enrichedRankings = rankings.map((stock) => {
      const snapshot = snapshots.find((item) => item.ticker === stock.ticker);
      return {
        ...stock,
        latest_price_mad: snapshot?.price_mad,
        momentum_1m: stock.momentum_1m ?? (stock.momentum_score - 50) / 1_000,
        momentum_3m: snapshot?.momentum_90d ?? stock.momentum_3m,
      };
    });
    return { rankings: enrichedRankings, signals, snapshots, portfolio, alerts };
  } catch {
    return mockDashboardData;
  }
}

export async function getStockDetailData(symbol: string): Promise<StockDetailData> {
  const ticker = symbol.toUpperCase();
  try {
    const [stock, ranking, signal, snapshots] = await Promise.all([
      getJson<StockDetailData["stock"]>(`/stocks/${ticker}`),
      getJson<RankedStock>(`/rankings/${ticker}`),
      getJson<Signal>(`/signals/${ticker}`),
      getJson<MarketSnapshot[]>("/market/snapshots/latest"),
    ]);
    return {
      stock,
      ranking,
      signal,
      snapshot: snapshots.find((item) => item.ticker === ticker),
    };
  } catch {
    const ranking = mockDashboardData.rankings.find((item) => item.ticker === ticker) ?? mockDashboardData.rankings[0];
    const signal = mockDashboardData.signals.find((item) => item.ticker === ranking.ticker);
    const snapshot = mockDashboardData.snapshots.find((item) => item.ticker === ranking.ticker);
    return {
      stock: {
        ticker: ranking.ticker,
        name: ranking.name,
        sector: ranking.sector,
        latest_price_mad: ranking.latest_price_mad,
        ai_score: ranking.ai_score,
        rank_position: ranking.rank_position,
        signal: ranking.signal,
        confidence: ranking.confidence,
        risk_note: ranking.risk_note,
      },
      ranking,
      signal,
      snapshot,
    };
  }
}

export async function askAssistant(question: string): Promise<AskResponse> {
  const response = await fetch(`${API_URL}/assistant/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, risk_profile: "balanced", tickers: [] }),
  });
  if (!response.ok) {
    return {
      answer: "The assistant can review ranked stocks, explain signals, and highlight risk alerts. The live API is not connected, so this is a local fallback response.",
      tickers: [],
      citations: ["local fallback"],
      disclaimer: "Research support only. No financial advice and no trade execution.",
      audit_id: "fallback",
    };
  }
  return response.json() as Promise<AskResponse>;
}
