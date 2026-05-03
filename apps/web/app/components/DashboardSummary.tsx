import { AlertTriangle, BarChart3, Bot, WalletCards } from "lucide-react";
import type { DashboardData } from "../lib/types";

function formatMad(value: number) {
  return new Intl.NumberFormat("en-MA", {
    style: "currency",
    currency: "MAD",
    maximumFractionDigits: 0,
  }).format(value);
}

export function DashboardSummary({ data }: { data: DashboardData }) {
  const buySignals = data.rankings.filter((stock) => stock.signal === "BUY").length;
  const highRiskStocks = data.rankings.filter((stock) => stock.risk_score >= 65).length;
  const totalPl = data.portfolio.holdings.reduce((sum, holding) => sum + holding.unrealized_pl_mad, 0);

  return (
    <section className="summaryGrid" aria-label="Dashboard summary">
      <article>
        <BarChart3 size={20} />
        <span>Top-ranked equities</span>
        <strong>{data.rankings.length}</strong>
      </article>
      <article>
        <Bot size={20} />
        <span>Buy signals</span>
        <strong>{buySignals}</strong>
      </article>
      <article>
        <AlertTriangle size={20} />
        <span>High-risk stocks</span>
        <strong>{highRiskStocks}</strong>
      </article>
      <article>
        <WalletCards size={20} />
        <span>Portfolio P&L</span>
        <strong className={totalPl >= 0 ? "positive" : "negative"}>{formatMad(totalPl)}</strong>
      </article>
    </section>
  );
}
