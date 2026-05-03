import { useMemo, useState } from "react";
import type { DummyHolding, RiskMode, RiskSimulation } from "../types/market";
import { formatMad } from "../utils/formatters";

type Labels = {
  action: string;
  aiAnalysis: string;
  aiScore: string;
  allocation: string;
  expectedReturn: string;
  heading: string;
  holding: string;
  maxDrawdown: string;
  projectedValue: string;
  revenue: string;
  risk: Record<RiskMode, string>;
  sector: string;
  simulated: string;
  subheading: string;
  trades: string;
  value: string;
  volatility: string;
  winRate: string;
};

type Props = {
  actionLabels?: Partial<Record<DummyHolding["aiAction"], string>>;
  holdings: DummyHolding[];
  labels: Labels;
  simulations: RiskSimulation[];
};

export function TradingShowcase({ actionLabels, holdings, labels, simulations }: Props) {
  const [activeMode, setActiveMode] = useState<RiskMode>("medium");
  const activeSimulation = useMemo(
    () => simulations.find((simulation) => simulation.mode === activeMode) ?? simulations[0],
    [activeMode, simulations],
  );
  const portfolioValue = holdings.reduce((sum, holding) => sum + holding.valueMad, 0);

  return (
    <section className="showcase-panel">
      <div className="showcase-header">
        <div>
          <p className="eyebrow">{labels.subheading}</p>
          <h2>{labels.heading}</h2>
        </div>
        <div className="risk-tabs" role="tablist" aria-label={labels.risk.medium}>
          {simulations.map((simulation) => (
            <button
              aria-selected={activeMode === simulation.mode}
              className={activeMode === simulation.mode ? "active" : ""}
              key={simulation.mode}
              role="tab"
              type="button"
              onClick={() => setActiveMode(simulation.mode)}
            >
              {labels.risk[simulation.mode]}
            </button>
          ))}
        </div>
      </div>

      <div className="showcase-grid">
        <div className="portfolio-table">
          <div className="portfolio-total">
            <span>{labels.value}</span>
            <strong>{formatMad(portfolioValue)}</strong>
          </div>
          <div className="holding-head">
            <span>{labels.holding}</span>
            <span>{labels.sector}</span>
            <span>{labels.allocation}</span>
            <span>{labels.aiScore}</span>
            <span>{labels.action}</span>
          </div>
          {holdings.map((holding) => (
            <article className="holding-row" key={holding.ticker}>
              <div>
                <strong>{holding.ticker}</strong>
                <span>{holding.name}</span>
              </div>
              <span>{holding.sector}</span>
              <span>{holding.allocation}%</span>
              <span className="score">{holding.aiScore}</span>
              <strong>{actionLabels?.[holding.aiAction] ?? holding.aiAction}</strong>
            </article>
          ))}
        </div>

        <div className="simulation-card">
          <span className="signal-badge">{labels.simulated}</span>
          <h3>{activeSimulation.title}</h3>
          <p>{activeSimulation.aiSummary}</p>
          <div className="metric-grid">
            <article>
              <span>{labels.expectedReturn}</span>
              <strong className="positive">+{activeSimulation.expectedReturn}%</strong>
            </article>
            <article>
              <span>{labels.revenue}</span>
              <strong>{formatMad(activeSimulation.simulatedRevenueMad)}</strong>
            </article>
            <article>
              <span>{labels.projectedValue}</span>
              <strong>{formatMad(activeSimulation.projectedValueMad)}</strong>
            </article>
            <article>
              <span>{labels.maxDrawdown}</span>
              <strong className="negative">{activeSimulation.maxDrawdown}%</strong>
            </article>
            <article>
              <span>{labels.volatility}</span>
              <strong>{activeSimulation.volatility}%</strong>
            </article>
            <article>
              <span>{labels.winRate}</span>
              <strong>{activeSimulation.winRate}%</strong>
            </article>
          </div>
          <div className="trade-list">
            <strong>{labels.trades}</strong>
            {activeSimulation.recommendedTrades.map((trade) => (
              <span key={trade}>{trade}</span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
