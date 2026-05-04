import { AlertTriangle } from "lucide-react";
import type { RiskAlert } from "../lib/types";

const severityLabel: Record<RiskAlert["severity"], string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
  Low: "Low",
  Medium: "Medium",
  High: "High",
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
        {alerts.map((alert, index) => {
          const severity = alert.severity.toLowerCase();
          return (
          <section className={`alertItem ${severity}`} key={alert.id ?? `${alert.alert_type}-${index}`}>
            <div>
              <span>{severityLabel[alert.severity]}</span>
              {alert.ticker || alert.symbol ? <strong>{alert.ticker ?? alert.symbol}</strong> : null}
            </div>
            <h3>{alert.title ?? alert.alert_type?.replaceAll("_", " ") ?? "Portfolio risk alert"}</h3>
            <p>{alert.detail ?? alert.message}</p>
            {alert.recommended_action ? <small>{alert.recommended_action}</small> : null}
          </section>
          );
        })}
      </div>
    </article>
  );
}
