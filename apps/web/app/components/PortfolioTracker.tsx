import { WalletCards } from "lucide-react";
import type { PortfolioSummary } from "../lib/types";

function formatMad(value: number) {
  return new Intl.NumberFormat("en-MA", {
    style: "currency",
    currency: "MAD",
    maximumFractionDigits: 0,
  }).format(value);
}

export function PortfolioTracker({ portfolio }: { portfolio: PortfolioSummary }) {
  return (
    <article className="panel">
      <div className="sectionHeader">
        <div>
          <p className="eyebrow">Portfolio tracker</p>
          <h2>{portfolio.portfolio_name}</h2>
        </div>
        <WalletCards size={22} />
      </div>
      <div className="portfolioTotal">
        <span>Total value</span>
        <strong>{formatMad(portfolio.current_value_mad)}</strong>
        <small className={portfolio.unrealized_pl_mad >= 0 ? "positive" : "negative"}>
          {formatMad(portfolio.unrealized_pl_mad)} unrealized P&L ({portfolio.unrealized_pl_pct.toFixed(2)}%)
        </small>
      </div>
      <div className="allocationGrid" aria-label="Allocation by sector">
        {Object.entries(portfolio.sector_allocations).map(([sector, allocation]) => (
          <section key={sector}>
            <span>{sector}</span>
            <strong>{allocation.toFixed(1)}%</strong>
            <meter min="0" max="100" value={allocation} />
          </section>
        ))}
      </div>
      <div className="holdingList">
        {portfolio.holdings.map((holding) => (
          <section className="holdingRow" key={holding.ticker}>
            <div>
              <strong>{holding.ticker}</strong>
              <span>{holding.sector ?? holding.manual_note ?? "Manual holding"}</span>
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
