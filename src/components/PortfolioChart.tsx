import { useMemo, useState } from "react";
import type { PortfolioSeries } from "../types/market";
import { formatMad } from "../utils/formatters";

type Props = {
  latestLabel: string;
  series: PortfolioSeries;
};

export function PortfolioChart({ latestLabel, series }: Props) {
  const ranges = Object.keys(series) as Array<keyof PortfolioSeries>;
  const [activeRange, setActiveRange] = useState<keyof PortfolioSeries>("1M");
  const points = series[activeRange];

  const path = useMemo(() => {
    const width = 720;
    const height = 260;
    const padding = 24;
    const values = points.map((point) => point.value);
    const min = Math.min(...values) * 0.98;
    const max = Math.max(...values) * 1.02;

    const coords = points.map((point, index) => {
      const x = padding + (index * (width - padding * 2)) / (points.length - 1);
      const y = height - padding - ((point.value - min) / (max - min)) * (height - padding * 2);
      return `${x},${y}`;
    });

    return {
      line: coords.join(" "),
      area: `${padding},${height - padding} ${coords.join(" ")} ${width - padding},${height - padding}`,
    };
  }, [points]);

  return (
    <div className="chart-stack">
      <div className="segmented" role="group" aria-label="Chart range">
        {ranges.map((range) => (
          <button
            className={range === activeRange ? "active" : ""}
            key={range}
            type="button"
            onClick={() => setActiveRange(range)}
          >
            {range}
          </button>
        ))}
      </div>
      <svg viewBox="0 0 720 260" role="img" aria-label="Portfolio value simulation chart">
        <defs>
          <linearGradient id="portfolioFill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#2d8c6c" stopOpacity="0.28" />
            <stop offset="100%" stopColor="#2d8c6c" stopOpacity="0" />
          </linearGradient>
        </defs>
        {[42, 86, 130, 174, 218].map((y) => (
          <line key={y} x1="24" x2="696" y1={y} y2={y} stroke="#d8e0dc" strokeWidth="1" />
        ))}
        <polygon points={path.area} fill="url(#portfolioFill)" />
        <polyline points={path.line} fill="none" stroke="#15634d" strokeLinecap="round" strokeWidth="4" />
      </svg>
      <div className="chart-footer">
        <span>{latestLabel}</span>
        <strong>{formatMad(points[points.length - 1].value)}</strong>
      </div>
    </div>
  );
}
