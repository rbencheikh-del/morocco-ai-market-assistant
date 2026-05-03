import { mockDashboardData } from "./mockData";
import type { AskResponse, DashboardData } from "./types";

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
    const [rankings, signals, snapshots, portfolio, alerts] = await Promise.all([
      getJson<DashboardData["rankings"]>("/rankings"),
      getJson<DashboardData["signals"]>("/signals"),
      getJson<DashboardData["snapshots"]>("/market/snapshots/latest"),
      getJson<DashboardData["portfolio"]>("/portfolio/demo"),
      getJson<DashboardData["alerts"]>("/alerts"),
    ]);
    return { rankings, signals, snapshots, portfolio, alerts };
  } catch {
    return mockDashboardData;
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
