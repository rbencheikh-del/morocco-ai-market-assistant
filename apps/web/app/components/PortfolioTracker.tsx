import { WalletCards } from "lucide-react";
import type { Portfolio } from "../lib/types";

function formatMad(value: number) {
  return new Intl.NumberFormat("en-MA", {
    style: "currency",
    currency: "MAD",
    maximumFractionDigits: 0,
  }).format(value);
}

export function PortfolioTracker({ portfolio }: { portfolio: Portfolio }) {
  const costBasis = portfolio.holdings.reduce(
    (sum, holding) => sum + holding.quantity * holding.average_cost_mad,
    0,
  );
  const totalPl = portfolio.holdings.reduce((sum, holding) => sum + holding.unrealized_pl_mad, 0);
  const totalPlPct = costBasis ? (totalPl / costBasis) * 100 : 0;

  return (
    <article className="panel">
      <div className="sectionHeader">
        <div>
          <p className="eyebrow">Portfolio tracker</p>
          <h2>{portfolio.name}</h2>
        </div>
        <WalletCards size={22} />
      </div>
      <div className="portfolioTotal">
        <span>Total value</span>
        <strong>{formatMad(portfolio.total_value_mad)}</strong>
        <small className={totalPl >= 0 ? "positive" : "negative"}>
          {formatMad(totalPl)} unrealized P&L ({totalPlPct.toFixed(2)}%)
        </small>
      </div>
      <div className="holdingList">
        {portfolio.holdings.map((holding) => (
          <section className="holdingRow" key={holding.ticker}>
            <div>
              <strong>{holding.ticker}</strong>
              <span>{holding.manual_note}</span>
            </div>
            <div>
              <strong>{formatMad(holding.market_value_mad)}</strong>
              <span>{holding.allocation_pct.toFixed(1)}% allocation</span>
            </div>
            <div className={holding.unrealized_pl_mad >= 0 ? "positive" : "negative"}>
              {formatMad(holding.unrealized_pl_mad)}
            </div>
          </section>
        ))}
      </div>
    </article>
  );
}
