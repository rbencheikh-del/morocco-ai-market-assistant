import { Activity, AlertTriangle, Building2, LineChart } from "lucide-react";
import type { StockDetailData } from "../lib/types";
import { RiskLevelBadge } from "./RiskLevelBadge";
import { SignalBadge } from "./SignalBadge";

function formatMad(value?: number) {
  if (value === undefined || value === null) {
    return "No price available";
  }
  return new Intl.NumberFormat("en-MA", {
    style: "currency",
    currency: "MAD",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatPercent(value?: number) {
  if (value === undefined || value === null) {
    return "n/a";
  }
  return `${(value * 100).toFixed(1)}%`;
}

export function StockDetailView({ data }: { data: StockDetailData }) {
  const signal = data.signal?.signal ?? data.ranking?.signal ?? data.stock.signal ?? "HOLD";
  const confidence = data.signal?.confidence ?? data.ranking?.confidence ?? data.stock.confidence ?? 0;
  const rankingScore = data.ranking?.ai_score ?? data.stock.ai_score ?? 0;
  const riskScore = data.ranking?.risk_score ?? 50;
  const latestPrice = data.snapshot?.price_mad ?? data.stock.latest_price_mad ?? data.ranking?.latest_price_mad;

  const indicators = [
    { label: "Ranking score", value: `${rankingScore}/100` },
    { label: "1M momentum", value: formatPercent(data.ranking?.momentum_1m) },
    { label: "3M momentum", value: formatPercent(data.snapshot?.momentum_90d ?? data.ranking?.momentum_3m) },
    { label: "30D volatility", value: formatPercent(data.snapshot?.volatility_30d) },
    { label: "Liquidity score", value: `${data.ranking?.liquidity_score ?? "n/a"}` },
    { label: "Momentum score", value: `${data.ranking?.momentum_score ?? "n/a"}` },
  ];

  return (
    <main className="detailShell">
      <a className="backLink" href="/">Back to dashboard</a>
      <section className="hero detailHero">
        <div>
          <p className="eyebrow">Stock detail</p>
          <h1>{data.stock.name}</h1>
          <p>
            {data.stock.ticker} on the Casablanca Stock Exchange. This page explains the research signal,
            technical context, and risk warnings in plain language.
          </p>
        </div>
        <div className="detailQuote">
          <span>Latest price</span>
          <strong>{formatMad(latestPrice)}</strong>
          <small>{data.stock.sector}</small>
        </div>
      </section>

      <section className="detailGrid">
        <article className="panel">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Signal explanation</p>
              <h2>Research signal</h2>
            </div>
            <SignalBadge signal={signal} />
          </div>
          <p className="leadText">
            {data.signal?.reason ?? data.ranking?.reason ?? "Signal explanation is unavailable from the API."}
          </p>
          <div className="metricStrip">
            <section>
              <span>Confidence score</span>
              <strong>{confidence}%</strong>
            </section>
            <section>
              <span>Ranking score</span>
              <strong>{rankingScore}/100</strong>
            </section>
            <section>
              <span>Risk level</span>
              <RiskLevelBadge riskScore={riskScore} />
            </section>
          </div>
        </article>

        <article className="panel">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Company profile</p>
              <h2>Company and sector</h2>
            </div>
            <Building2 size={22} />
          </div>
          <div className="detailList">
            <span>Company name</span>
            <strong>{data.stock.name}</strong>
            <span>Sector</span>
            <strong>{data.stock.sector}</strong>
            <span>Rank position</span>
            <strong>#{data.ranking?.rank_position ?? data.stock.rank_position ?? "n/a"}</strong>
          </div>
        </article>

        <article className="panel">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Technical indicators</p>
              <h2>Market metrics</h2>
            </div>
            <Activity size={22} />
          </div>
          <div className="indicatorGrid">
            {indicators.map((indicator) => (
              <section key={indicator.label}>
                <span>{indicator.label}</span>
                <strong>{indicator.value}</strong>
              </section>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Risk warnings</p>
              <h2>Retail guardrails</h2>
            </div>
            <AlertTriangle size={22} />
          </div>
          <ul className="riskList">
            <li>{data.signal?.risk_note ?? data.ranking?.risk_note ?? data.stock.risk_note}</li>
            <li>Check liquidity and data freshness before relying on any signal.</li>
            <li>This is market analytics only, not financial advice.</li>
          </ul>
        </article>
      </section>

      <section className="panel disclaimerPanel">
        <LineChart size={18} />
        <strong>This is market analytics only, not financial advice.</strong>
      </section>
    </main>
  );
}
