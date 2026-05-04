from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import ManualPortfolio, RiskAlert, StockSignal
from app.services.portfolio import calculate_portfolio_pnl, get_portfolio

LOW_LIQUIDITY_TRADED_VALUE_MAD = 1_000_000
HIGH_VOLATILITY_30D = 0.22


def list_risk_alerts(db: Session) -> list[RiskAlert]:
    return db.query(RiskAlert).order_by(RiskAlert.created_at.desc()).all()


def _latest_signal(db: Session, ticker: str) -> StockSignal | None:
    return (
        db.query(StockSignal)
        .filter(StockSignal.ticker == ticker)
        .order_by(StockSignal.signal_date.desc())
        .first()
    )


def _alert(
    portfolio: ManualPortfolio,
    ticker: str | None,
    alert_type: str,
    severity: str,
    title: str,
    detail: str,
    trigger_payload: dict,
    recommended_action: str,
) -> dict:
    return {
        "user_id": portfolio.user_id,
        "portfolio_id": portfolio.id,
        "ticker": ticker,
        "alert_type": alert_type,
        "severity": severity,
        "title": title,
        "detail": detail,
        "trigger_payload": {
            **trigger_payload,
            "recommended_action": recommended_action,
        },
    }


def build_portfolio_risk_alerts(portfolio: ManualPortfolio, pnl: dict, latest_signal_lookup) -> list[dict]:
    alerts: list[dict] = []

    for holding in pnl["holdings"]:
        allocation = holding["allocation_pct"]
        unrealized_pl_pct = holding.get("unrealized_pl_pct", 0.0)
        avg_daily_traded_value_mad = holding.get("avg_daily_traded_value_mad", 0.0)
        volatility_30d = holding.get("volatility_30d")

        if holding.get("price_status") == "missing":
            alerts.append(
                _alert(
                    portfolio,
                    holding["ticker"],
                    "missing_market_price",
                    "medium",
                    "Missing market price",
                    f"{holding['ticker']} is valued using average cost because no latest market price is available.",
                    {"price_status": "missing"},
                    "Refresh or verify market data before relying on this portfolio valuation.",
                )
            )

        if allocation > 35:
            alerts.append(
                _alert(
                    portfolio,
                    holding["ticker"],
                    "single_stock_exposure",
                    "high",
                    "High single-stock exposure",
                    f"{holding['ticker']} is {allocation:.1f}% of this portfolio.",
                    {"allocation_pct": allocation, "threshold_pct": 35},
                    "Review position size and diversification. This app does not execute trades.",
                )
            )
        elif allocation > 25:
            alerts.append(
                _alert(
                    portfolio,
                    holding["ticker"],
                    "single_stock_exposure",
                    "medium",
                    "Single-stock exposure",
                    f"{holding['ticker']} is above the 25% portfolio review threshold.",
                    {"allocation_pct": allocation, "threshold_pct": 25},
                    "Review whether this exposure matches the portfolio risk profile.",
                )
            )

        if unrealized_pl_pct < -10:
            alerts.append(
                _alert(
                    portfolio,
                    holding["ticker"],
                    "drawdown",
                    "medium",
                    "Holding drawdown",
                    f"{holding['ticker']} is down {abs(unrealized_pl_pct):.1f}% versus average buy price.",
                    {"unrealized_pl_pct": unrealized_pl_pct, "threshold_pct": -10},
                    "Review the investment thesis and risk tolerance before making any manual decision.",
                )
            )

        if unrealized_pl_pct > 20:
            alerts.append(
                _alert(
                    portfolio,
                    holding["ticker"],
                    "large_unrealized_gain",
                    "low",
                    "Large unrealized gain",
                    f"{holding['ticker']} is up {unrealized_pl_pct:.1f}% versus average buy price.",
                    {"unrealized_pl_pct": unrealized_pl_pct, "threshold_pct": 20},
                    "Review allocation and rebalance rules if this gain has changed portfolio concentration.",
                )
            )

        if avg_daily_traded_value_mad and avg_daily_traded_value_mad < LOW_LIQUIDITY_TRADED_VALUE_MAD:
            alerts.append(
                _alert(
                    portfolio,
                    holding["ticker"],
                    "low_liquidity",
                    "high",
                    "Low-liquidity holding",
                    f"{holding['ticker']} has average daily traded value below {LOW_LIQUIDITY_TRADED_VALUE_MAD:,.0f} MAD.",
                    {
                        "avg_daily_traded_value_mad": avg_daily_traded_value_mad,
                        "threshold_mad": LOW_LIQUIDITY_TRADED_VALUE_MAD,
                    },
                    "Use conservative sizing assumptions and verify liquidity before relying on analysis.",
                )
            )

        if volatility_30d is not None and volatility_30d > HIGH_VOLATILITY_30D:
            alerts.append(
                _alert(
                    portfolio,
                    holding["ticker"],
                    "high_volatility",
                    "medium",
                    "High-volatility holding",
                    f"{holding['ticker']} has elevated 30-day volatility.",
                    {"volatility_30d": volatility_30d, "threshold": HIGH_VOLATILITY_30D},
                    "Review whether this holding fits the selected risk profile.",
                )
            )

        signal = latest_signal_lookup(holding["ticker"])
        if signal and signal.signal == "SELL":
            alerts.append(
                _alert(
                    portfolio,
                    holding["ticker"],
                    "signal_conflict",
                    "high" if signal.confidence >= 70 else "medium",
                    "Research signal conflicts with holding",
                    f"{holding['ticker']} currently has a SELL/AVOID research signal with {signal.confidence}% confidence.",
                    {"signal": signal.signal, "confidence": signal.confidence},
                    "Review the research signal and underlying metrics. This is not a trade instruction.",
                )
            )

    for sector, allocation in pnl.get("sector_allocations", {}).items():
        if allocation > 60:
            alerts.append(
                _alert(
                    portfolio,
                    None,
                    "sector_exposure",
                    "high",
                    "High sector exposure",
                    f"{sector} is {allocation:.1f}% of this portfolio.",
                    {"sector": sector, "allocation_pct": allocation, "threshold_pct": 60},
                    "Review diversification across sectors and keep any changes manual.",
                )
            )
        elif allocation > 50:
            alerts.append(
                _alert(
                    portfolio,
                    None,
                    "sector_exposure",
                    "medium",
                    "Sector exposure",
                    f"{sector} is above the 50% portfolio review threshold.",
                    {"sector": sector, "allocation_pct": allocation, "threshold_pct": 50},
                    "Review whether sector concentration matches the portfolio objective.",
                )
            )

    return alerts


def to_portfolio_alert_output(alert: dict) -> dict:
    severity_label = {
        "low": "Low",
        "medium": "Medium",
        "high": "High",
    }.get(alert["severity"], alert["severity"].title())
    return {
        "alert_type": alert["alert_type"],
        "severity": severity_label,
        "symbol": alert.get("ticker"),
        "message": alert["detail"],
        "recommended_action": alert.get("trigger_payload", {}).get(
            "recommended_action",
            "Review this analytics alert before making any manual decision.",
        ),
    }


def get_portfolio_risk_alerts(db: Session, portfolio_id: UUID) -> list[dict] | None:
    portfolio = get_portfolio(db, portfolio_id)
    if not portfolio:
        return None
    pnl = calculate_portfolio_pnl(db, portfolio.id)
    if not pnl:
        return []
    alerts = build_portfolio_risk_alerts(portfolio, pnl, lambda ticker: _latest_signal(db, ticker))
    return [to_portfolio_alert_output(alert) for alert in alerts]


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
