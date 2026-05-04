import type { RankedStock } from "../lib/types";
import { RiskLevelBadge } from "./RiskLevelBadge";
import { SignalBadge } from "./SignalBadge";

function formatMad(value?: number) {
  if (value === undefined) {
    return "No price";
  }
  return new Intl.NumberFormat("en-MA", {
    style: "currency",
    currency: "MAD",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatMomentum(value?: number) {
  if (value === undefined) {
    return "n/a";
  }
  return `${(value * 100).toFixed(1)}%`;
}

export function RankedStocksTable({ rankings }: { rankings: RankedStock[] }) {
  return (
    <article className="panel tablePanel">
      <div className="sectionHeader">
        <div>
          <p className="eyebrow">Stock ranking engine</p>
          <h2>Top-ranked Moroccan equities</h2>
        </div>
        <span className="pill">Top {rankings.length}</span>
      </div>
      <div className="tableWrap">
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Stock</th>
              <th>Sector</th>
              <th>AI score</th>
              <th>Signal</th>
              <th>Confidence</th>
              <th>Risk level</th>
              <th>Latest price</th>
              <th>1M / 3M momentum</th>
              <th>Why</th>
            </tr>
          </thead>
          <tbody>
            {rankings.map((stock) => (
              <tr key={stock.ticker}>
                <td>#{stock.rank_position}</td>
                <td>
                  <a className="stockLink" href={`/stocks/${stock.ticker}`}>
                    <strong>{stock.ticker}</strong>
                  </a>
                  <span>{stock.name}</span>
                </td>
                <td>{stock.sector}</td>
                <td>
                  <meter min="0" max="100" value={stock.ai_score} />
                  <strong>{stock.ai_score}</strong>
                </td>
                <td>
                  <SignalBadge signal={stock.signal} />
                </td>
                <td>
                  <meter min="0" max="100" value={stock.confidence} />
                  <strong>{stock.confidence}%</strong>
                </td>
                <td>
                  <RiskLevelBadge riskScore={stock.risk_score} />
                  <span>Score {stock.risk_score}</span>
                </td>
                <td>{formatMad(stock.latest_price_mad)}</td>
                <td>
                  <strong>{formatMomentum(stock.momentum_1m)}</strong>
                  <span>{formatMomentum(stock.momentum_3m)} 3M</span>
                </td>
                <td>{stock.rationale}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  );
}
