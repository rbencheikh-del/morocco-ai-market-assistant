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

    generated: list[RiskAlert] = []
    for holding in pnl["holdings"]:
        allocation = holding["allocation_pct"]
        unrealized_pl = holding["unrealized_pl_mad"]
        market_value = holding["market_value_mad"]

        if allocation >= 30:
            generated.append(
                RiskAlert(
                    user_id=portfolio.user_id,
                    portfolio_id=portfolio.id,
                    ticker=holding["ticker"],
                    alert_type="concentration",
                    severity="high",
                    title="Single-stock concentration",
                    detail=f"{holding['ticker']} is {allocation:.1f}% of this portfolio.",
                    trigger_payload={"allocation_pct": allocation, "threshold_pct": 30},
                )
            )
        elif allocation >= 20:
            generated.append(
                RiskAlert(
                    user_id=portfolio.user_id,
                    portfolio_id=portfolio.id,
                    ticker=holding["ticker"],
                    alert_type="concentration",
                    severity="medium",
                    title="Position size needs review",
                    detail=f"{holding['ticker']} is above the 20% review threshold.",
                    trigger_payload={"allocation_pct": allocation, "threshold_pct": 20},
                )
            )

        if market_value and (unrealized_pl / market_value) <= -0.10:
            generated.append(
                RiskAlert(
                    user_id=portfolio.user_id,
                    portfolio_id=portfolio.id,
                    ticker=holding["ticker"],
                    alert_type="portfolio_risk",
                    severity="medium",
                    title="Unrealized loss threshold",
                    detail=f"{holding['ticker']} has moved more than 10% below its current market value basis.",
                    trigger_payload={"unrealized_pl_mad": unrealized_pl, "market_value_mad": market_value},
                )
            )

        signal = _latest_signal(db, holding["ticker"])
        if signal and signal.signal == "SELL":
            generated.append(
                RiskAlert(
                    user_id=portfolio.user_id,
                    portfolio_id=portfolio.id,
                    ticker=holding["ticker"],
                    alert_type="signal",
                    severity="high" if signal.confidence >= 70 else "medium",
                    title="AI signal conflicts with holding",
                    detail=f"{holding['ticker']} currently has a SELL signal with {signal.confidence}% confidence.",
                    trigger_payload={"signal": signal.signal, "confidence": signal.confidence},
                )
            )

    if generated:
        db.add_all(generated)
        db.commit()
        for alert in generated:
            db.refresh(alert)

    return generated
