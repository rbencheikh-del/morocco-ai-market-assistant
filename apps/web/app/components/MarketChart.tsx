"use client";

import { createChart, ColorType, type IChartApi } from "lightweight-charts";
import { useEffect, useMemo, useRef } from "react";
import type { MarketSnapshot } from "../lib/types";

type Props = {
  snapshots: MarketSnapshot[];
};

export function MarketChart({ snapshots }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);

  const orderedSnapshots = useMemo(
    () => [...snapshots].sort((a, b) => a.ticker.localeCompare(b.ticker)),
    [snapshots],
  );

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }

    const chart = createChart(containerRef.current, {
      height: 300,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#536171",
      },
      grid: {
        vertLines: { color: "#edf2f7" },
        horzLines: { color: "#edf2f7" },
      },
      rightPriceScale: {
        borderVisible: false,
      },
      timeScale: {
        borderVisible: false,
        fixLeftEdge: true,
        fixRightEdge: true,
      },
      crosshair: {
        mode: 1,
      },
    });

    const lineSeries = chart.addLineSeries({
      color: "#1266f1",
      lineWidth: 3,
      priceFormat: { type: "price", precision: 2, minMove: 0.01 },
    });

    lineSeries.setData(
      orderedSnapshots.map((snapshot, index) => ({
        time: `2026-05-${String(index + 1).padStart(2, "0")}`,
        value: snapshot.price_mad,
      })),
    );

    chart.timeScale().fitContent();
    chartRef.current = chart;

    const resizeObserver = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) {
        chart.applyOptions({ width: Math.floor(entry.contentRect.width) });
      }
    });
    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
    };
  }, [orderedSnapshots]);

  return (
    <article className="panel chartPanel">
      <div className="sectionHeader">
        <div>
          <p className="eyebrow">Market data ingestion</p>
          <h2>Casablanca watchlist prices</h2>
        </div>
        <span className="pill">MAD</span>
      </div>
      <div ref={containerRef} className="chartCanvas" aria-label="Casablanca stock price chart" />
      <div className="tickerStrip">
        {orderedSnapshots.map((snapshot) => (
          <span key={snapshot.ticker}>
            <strong>{snapshot.ticker}</strong> {snapshot.price_mad.toLocaleString()} MAD
          </span>
        ))}
      </div>
    </article>
  );
}
