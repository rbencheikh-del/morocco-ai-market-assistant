from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import ManualPortfolio, RiskAlert, StockSignal
from app.services.portfolio import calculate_portfolio_pnl, get_portfolio


def list_risk_alerts(db: Session) -> list[RiskAlert]:
    return db.query(RiskAlert).order_by(RiskAlert.created_at.desc()).all()


def _latest_signal(db: Session, ticker: str) -> StockSignal | None:
    return (
        db.query(StockSignal)
        .filter(StockSignal.ticker == ticker)
        .order_by(StockSignal.signal_date.desc())
        .first()
    )


def build_portfolio_risk_alerts(portfolio: ManualPortfolio, pnl: dict, latest_signal_lookup) -> list[dict]:
    alerts: list[dict] = []

    for holding in pnl["holdings"]:
        allocation = holding["allocation_pct"]
        unrealized_pl = holding["unrealized_pl_mad"]
        market_value = holding["market_value_mad"]

        if holding.get("price_status") == "missing":
            alerts.append(
                {
                    "user_id": portfolio.user_id,
                    "portfolio_id": portfolio.id,
                    "ticker": holding["ticker"],
                    "alert_type": "data_quality",
                    "severity": "medium",
                    "title": "Missing market price",
                    "detail": f"{holding['ticker']} is valued using average cost because no latest market price is available.",
                    "trigger_payload": {"price_status": "missing"},
                }
            )

        if allocation >= 35:
            alerts.append(
                {
                    "user_id": portfolio.user_id,
                    "portfolio_id": portfolio.id,
                    "ticker": holding["ticker"],
                    "alert_type": "concentration",
                    "severity": "high",
                    "title": "High single-stock concentration",
                    "detail": f"{holding['ticker']} is {allocation:.1f}% of this portfolio.",
                    "trigger_payload": {"allocation_pct": allocation, "threshold_pct": 35},
                }
            )
        elif allocation >= 25:
            alerts.append(
                {
                    "user_id": portfolio.user_id,
                    "portfolio_id": portfolio.id,
                    "ticker": holding["ticker"],
                    "alert_type": "concentration",
                    "severity": "medium",
                    "title": "Single-stock concentration",
                    "detail": f"{holding['ticker']} is above the 25% review threshold.",
                    "trigger_payload": {"allocation_pct": allocation, "threshold_pct": 25},
                }
            )

        if market_value and (unrealized_pl / market_value) <= -0.10:
            alerts.append(
                {
                    "user_id": portfolio.user_id,
                    "portfolio_id": portfolio.id,
                    "ticker": holding["ticker"],
                    "alert_type": "portfolio_risk",
                    "severity": "medium",
                    "title": "Unrealized loss threshold",
                    "detail": f"{holding['ticker']} has an unrealized loss greater than 10% of current market value.",
                    "trigger_payload": {"unrealized_pl_mad": unrealized_pl, "market_value_mad": market_value},
                }
            )

        signal = latest_signal_lookup(holding["ticker"])
        if signal and signal.signal == "SELL":
            alerts.append(
                {
                    "user_id": portfolio.user_id,
                    "portfolio_id": portfolio.id,
                    "ticker": holding["ticker"],
                    "alert_type": "signal",
                    "severity": "high" if signal.confidence >= 70 else "medium",
                    "title": "Research signal conflicts with holding",
                    "detail": f"{holding['ticker']} currently has a SELL/AVOID research signal with {signal.confidence}% confidence.",
                    "trigger_payload": {"signal": signal.signal, "confidence": signal.confidence},
                }
            )

    for sector, allocation in pnl.get("sector_allocations", {}).items():
        if allocation >= 60:
            alerts.append(
                {
                    "user_id": portfolio.user_id,
                    "portfolio_id": portfolio.id,
                    "ticker": None,
                    "alert_type": "concentration",
                    "severity": "high",
                    "title": "High sector concentration",
                    "detail": f"{sector} is {allocation:.1f}% of this portfolio.",
                    "trigger_payload": {"sector": sector, "allocation_pct": allocation, "threshold_pct": 60},
                }
            )
        elif allocation >= 45:
            alerts.append(
                {
                    "user_id": portfolio.user_id,
                    "portfolio_id": portfolio.id,
                    "ticker": None,
                    "alert_type": "concentration",
                    "severity": "medium",
                    "title": "Sector concentration",
                    "detail": f"{sector} is above the 45% review threshold.",
                    "trigger_payload": {"sector": sector, "allocation_pct": allocation, "threshold_pct": 45},
                }
            )

    return alerts


def generate_portfolio_alerts(db: Session, portfolio_id: UUID | None = None) -> list[RiskAlert]:
    portfolio: ManualPortfolio | None
    if portfolio_id:
        portfolio = get_portfolio(db, portfolio_id)
    else:
        portfolio = db.query(ManualPortfolio).order_by(ManualPortfolio.created_at.desc()).first()

    if not portfolio:
        return []

    pnl = calculate_portfolio_pnl(db, portfolio.id)
    if not pnl:
        return []

    alert_payloads = build_portfolio_risk_alerts(portfolio, pnl, lambda ticker: _latest_signal(db, ticker))
    generated = [RiskAlert(**payload) for payload in alert_payloads]

    if generated:
        db.add_all(generated)
        db.commit()
        for alert in generated:
            db.refresh(alert)

    return generated
