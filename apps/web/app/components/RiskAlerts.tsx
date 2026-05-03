import { AlertTriangle } from "lucide-react";
import type { RiskAlert } from "../lib/types";

const severityLabel: Record<RiskAlert["severity"], string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
};

export function RiskAlerts({ alerts }: { alerts: RiskAlert[] }) {
  return (
    <article className="panel">
      <div className="sectionHeader">
        <div>
          <p className="eyebrow">Risk alerts</p>
          <h2>Risk-profile guidance</h2>
        </div>
        <AlertTriangle size={22} />
      </div>
      <div className="alertList">
        {alerts.map((alert) => (
          <section className={`alertItem ${alert.severity}`} key={alert.id}>
            <div>
              <span>{severityLabel[alert.severity]}</span>
              {alert.ticker ? <strong>{alert.ticker}</strong> : null}
            </div>
            <h3>{alert.title}</h3>
            <p>{alert.detail}</p>
          </section>
        ))}
      </div>
    </article>
  );
}
