import { Eye } from "lucide-react";
import type { Watchlist } from "../lib/types";
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

function changeClass(value?: number) {
  if (!value) {
    return "";
  }
  return value > 0 ? "positive" : "negative";
}

export function WatchlistPage({ watchlists }: { watchlists: Watchlist[] }) {
  const selected = watchlists[0];

  return (
    <article className="panel tablePanel">
      <div className="sectionHeader">
        <div>
          <p className="eyebrow">Watchlists</p>
          <h2>{selected?.name ?? "No watchlist yet"}</h2>
          <p>{selected?.description ?? "Create a watchlist to track Moroccan equities and analytics alerts."}</p>
        </div>
        <Eye size={22} />
      </div>
      <div className="tableWrap">
        <table>
          <thead>
            <tr>
              <th>Stock</th>
              <th>Latest price</th>
              <th>Signal</th>
              <th>Ranking score</th>
              <th>Daily change</th>
              <th>Alert levels</th>
            </tr>
          </thead>
          <tbody>
            {(selected?.items ?? []).map((stock) => (
              <tr key={stock.ticker}>
                <td>
                  <strong>{stock.ticker}</strong>
                  <span>{stock.user_note ?? stock.risk_level ?? "Research watch"}</span>
                </td>
                <td>{formatMad(stock.latest_price_mad)}</td>
                <td>{stock.signal ? <SignalBadge signal={stock.signal} /> : "n/a"}</td>
                <td>
                  <meter min="0" max="100" value={stock.ranking_score ?? 0} />
                  <strong>{stock.ranking_score ?? "n/a"}</strong>
                </td>
                <td className={changeClass(stock.daily_change_pct)}>
                  {stock.daily_change_pct === undefined ? "n/a" : `${stock.daily_change_pct.toFixed(2)}%`}
                </td>
                <td>
                  <span>Above {formatMad(stock.alert_above_mad)}</span>
                  <span>Below {formatMad(stock.alert_below_mad)}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  );
}
