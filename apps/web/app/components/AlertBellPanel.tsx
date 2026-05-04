import { Bell } from "lucide-react";
import type { RiskAlert } from "../lib/types";

function label(alert: RiskAlert) {
  return alert.message ?? alert.detail ?? "Analytics alert";
}

export function AlertBellPanel({ alerts }: { alerts: RiskAlert[] }) {
  const unreadCount = alerts.filter((alert) => !alert.is_read).length;

  return (
    <article className="alertBellPanel" aria-label="Alert notifications">
      <div className="bellIcon">
        <Bell size={18} />
        {unreadCount > 0 ? <span>{unreadCount}</span> : null}
      </div>
      <div>
        <strong>Alerts</strong>
        <small>{unreadCount} unread research alert{unreadCount === 1 ? "" : "s"}</small>
      </div>
      <div className="miniAlertList">
        {alerts.slice(0, 3).map((alert, index) => (
          <section key={alert.id ?? `${alert.alert_type}-${index}`}>
            <span>{alert.symbol ?? alert.ticker ?? "Portfolio"}</span>
            <p>{label(alert)}</p>
          </section>
        ))}
      </div>
    </article>
  );
}
