import { useMemo, useState } from "react";
import type { WatchlistItem } from "../types/market";

type Props = {
  items: WatchlistItem[];
  labels: {
    alert: string;
    eyebrow: string;
    heading: string;
    reason: string;
    signal: string;
    sort: string;
  };
};

export function WatchlistTable({ items, labels }: Props) {
  const [sortMode, setSortMode] = useState<"score" | "ticker">("score");
  const sortedItems = useMemo(() => {
    return [...items].sort((first, second) => {
      if (sortMode === "ticker") {
        return first.ticker.localeCompare(second.ticker);
      }

      return second.score - first.score;
    });
  }, [items, sortMode]);

  return (
    <div className="panel watchlist-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">{labels.eyebrow}</p>
          <h2>{labels.heading}</h2>
        </div>
        <button
          className="ghost-button"
          type="button"
          onClick={() => setSortMode((current) => (current === "score" ? "ticker" : "score"))}
        >
          {labels.sort}
        </button>
      </div>
      <div className="table">
        {sortedItems.map((item) => (
          <article className="table-row" key={item.ticker}>
            <div>
              <strong>{item.ticker}</strong>
              <span>{item.name}</span>
            </div>
            <div>
              <strong>{item.stance}</strong>
              <span>{item.sector}</span>
            </div>
            <div>
              <strong className={`signal-${item.signal.toLowerCase()}`}>{item.signal}</strong>
              <span>{labels.signal}</span>
            </div>
            <div>
              <strong>{labels.reason}</strong>
              <span>{item.reason}</span>
            </div>
            <div>
              <strong>{labels.alert}</strong>
              <span>{item.alert}</span>
            </div>
            <span className="score">{item.score}</span>
          </article>
        ))}
      </div>
    </div>
  );
}
