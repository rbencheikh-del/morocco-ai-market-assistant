import type { RiskAlert } from "../types/market";

type Props = {
  alerts: RiskAlert[];
  eyebrow: string;
  heading: string;
};

export function RiskAlertsPanel({ alerts, eyebrow, heading }: Props) {
  return (
    <div className="panel alerts-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h2>{heading}</h2>
        </div>
      </div>
      <div className="alerts-list">
        {alerts.map((alert) => (
          <article className={`alert-item alert-${alert.severity}`} key={alert.title}>
            <strong>{alert.title}</strong>
            <span>{alert.detail}</span>
          </article>
        ))}
      </div>
    </div>
  );
}
