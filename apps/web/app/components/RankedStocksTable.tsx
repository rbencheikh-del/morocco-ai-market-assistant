import type { RankedStock } from "../lib/types";
import { RiskLevelBadge } from "./RiskLevelBadge";
import { SignalBadge } from "./SignalBadge";

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
              <th>Why</th>
            </tr>
          </thead>
          <tbody>
            {rankings.map((stock) => (
              <tr key={stock.ticker}>
                <td>#{stock.rank_position}</td>
                <td>
                  <strong>{stock.ticker}</strong>
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
                <td>{stock.rationale}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  );
}
