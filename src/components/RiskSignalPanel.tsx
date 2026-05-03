import type { AiSignal } from "../types/market";

type Props = {
  labels: {
    heading: string;
    modelBadge: string;
    riskAppetite: string;
  };
  riskScore: number;
  signal: AiSignal;
  onRiskScoreChange: (value: number) => void;
};

export function RiskSignalPanel({ labels, riskScore, signal, onRiskScoreChange }: Props) {
  return (
    <div className="panel ai-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">{labels.heading}</p>
          <h2>{signal.title}</h2>
        </div>
        <span className="signal-badge">{labels.modelBadge}</span>
      </div>
      <p>{signal.narrative}</p>
      <div className="slider-row">
        <label htmlFor="riskSlider">{labels.riskAppetite}</label>
        <input
          id="riskSlider"
          max="10"
          min="1"
          type="range"
          value={riskScore}
          onChange={(event) => onRiskScoreChange(Number(event.target.value))}
        />
        <span>{riskScore}</span>
      </div>
      <div className="meter" aria-hidden="true">
        <span style={{ width: `${riskScore * 10}%` }} />
      </div>
    </div>
  );
}
