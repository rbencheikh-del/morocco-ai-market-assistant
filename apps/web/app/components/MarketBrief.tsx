import { AlertTriangle, TrendingUp } from "lucide-react";
import type { DashboardData, RankedStock } from "../lib/types";
import { SignalBadge } from "./SignalBadge";

function formatMad(value?: number) {
  if (value === undefined || value === null) {
    return "No price";
  }
  return new Intl.NumberFormat("en-MA", {
    style: "currency",
    currency: "MAD",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatChange(value?: number) {
  if (value === undefined || value === null) {
    return "n/a";
  }
  return `${value > 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function changeClass(value?: number) {
  if (!value) {
    return "";
  }
  return value > 0 ? "positive" : "negative";
}

function riskWarnings(stocks: RankedStock[]) {
  return stocks
    .filter((stock) => stock.signal === "SELL" || stock.risk_score >= 60 || (stock.daily_change_pct ?? 0) <= -5)
    .slice(0, 4)
    .map((stock) => ({
      ticker: stock.ticker,
      text:
        stock.signal === "SELL"
          ? `${stock.ticker} has a negative research signal; review the explanation and data freshness.`
          : (stock.daily_change_pct ?? 0) <= -5
            ? `${stock.ticker} moved down more than 5% today; verify news and data quality.`
            : `${stock.ticker} has an elevated risk score; review volatility, liquidity, and concentration.`,
    }));
}

function narrative(top: RankedStock[], movers: RankedStock[], warnings: ReturnType<typeof riskWarnings>) {
  const leader = top[0];
  const mover = movers[0];
  if (!leader) {
    return "No ranked market data is available yet. Import daily prices to generate today’s brief.";
  }
  const caution = warnings.length > 0 ? ` Main caution: ${warnings[0].text}` : " No major risk warning is active in the current sample.";
  return `${leader.ticker} leads the ranked list with a ${leader.ai_score}/100 score and a ${leader.signal} research signal. ${mover?.ticker ?? leader.ticker} is the biggest mover in the current dataset at ${formatChange(mover?.daily_change_pct ?? leader.daily_change_pct)}.${caution} This is market analytics only, not financial advice.`;
}

export function MarketBrief({ data }: { data: DashboardData }) {
  const topFive = [...data.rankings].sort((a, b) => a.rank_position - b.rank_position).slice(0, 5);
  const movers = [...data.rankings]
    .filter((stock) => stock.daily_change_pct !== undefined)
    .sort((a, b) => Math.abs(b.daily_change_pct ?? 0) - Math.abs(a.daily_change_pct ?? 0))
    .slice(0, 5);
  const warnings = riskWarnings(data.rankings);

  return (
    <article className="panel marketBriefPanel">
      <div className="sectionHeader">
        <div>
          <p className="eyebrow">Today’s market brief</p>
          <h2>Top 5 Moroccan stocks today</h2>
        </div>
        <TrendingUp size={22} />
      </div>

      <div className="briefGrid">
        <section>
          <h3>Top ranked</h3>
          <div className="briefList">
            {topFive.map((stock) => (
              <div key={stock.ticker}>
                <strong>{stock.ticker}</strong>
                <span>{stock.ai_score}/100</span>
                <SignalBadge signal={stock.signal} />
                <small>{formatMad(stock.latest_price_mad)}</small>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h3>Biggest movers</h3>
          <div className="briefList">
            {movers.map((stock) => (
              <div key={stock.ticker}>
                <strong>{stock.ticker}</strong>
                <span className={changeClass(stock.daily_change_pct)}>{formatChange(stock.daily_change_pct)}</span>
                <small>{stock.name}</small>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h3>Risk warnings</h3>
          <div className="warningList">
            {warnings.length > 0 ? (
              warnings.map((warning) => (
                <p key={warning.ticker}>
                  <AlertTriangle size={15} />
                  {warning.text}
                </p>
              ))
            ) : (
              <p>No major warning in the current dataset.</p>
            )}
          </div>
        </section>
      </div>

      <section className="narrativeSummary">
        <strong>Simple narrative summary</strong>
        <p>{narrative(topFive, movers, warnings)}</p>
      </section>
    </article>
  );
}
