from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import ManualPortfolio, MarketSnapshot, PortfolioHolding, Security


def _latest_price(db: Session, ticker: str, fallback: float) -> float:
    snapshot = (
        db.query(MarketSnapshot)
        .filter(MarketSnapshot.ticker == ticker)
        .order_by(MarketSnapshot.as_of.desc())
        .first()
    )
    return float(snapshot.price_mad) if snapshot else fallback


def _portfolio_output(db: Session, portfolio: ManualPortfolio) -> dict:
    holding_rows = db.query(PortfolioHolding).filter(PortfolioHolding.portfolio_id == portfolio.id).all()
    holdings = []
    total_value = 0.0
    for holding in holding_rows:
        current_price = _latest_price(db, holding.ticker, float(holding.average_cost_mad))
        market_value = float(holding.quantity) * current_price
        total_value += market_value
        holdings.append(
            {
                "ticker": holding.ticker,
                "quantity": float(holding.quantity),
                "average_cost_mad": float(holding.average_cost_mad),
                "current_price_mad": current_price,
                "market_value_mad": market_value,
                "unrealized_pl_mad": market_value - float(holding.quantity) * float(holding.average_cost_mad),
                "allocation_pct": 0.0,
                "manual_note": holding.manual_note,
            }
        )

    for holding in holdings:
        holding["allocation_pct"] = round((holding["market_value_mad"] / total_value) * 100, 2) if total_value else 0

    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "base_currency": portfolio.base_currency,
        "total_value_mad": total_value,
        "holdings": holdings,
    }


def get_demo_portfolio(db: Session) -> dict | None:
    portfolio = db.query(ManualPortfolio).order_by(ManualPortfolio.created_at.desc()).first()
    if not portfolio:
        return None
    return _portfolio_output(db, portfolio)


def get_portfolio(db: Session, portfolio_id: UUID) -> ManualPortfolio | None:
    return db.query(ManualPortfolio).filter(ManualPortfolio.id == portfolio_id).first()


def add_holding(
    db: Session,
    portfolio_id: UUID,
    ticker: str,
    quantity: float,
    average_cost_mad: float,
    manual_note: str | None = None,
    opened_at=None,
) -> dict | None:
    portfolio = get_portfolio(db, portfolio_id)
    security = db.query(Security).filter(Security.ticker == ticker.upper(), Security.is_active.is_(True)).first()
    if not portfolio or not security:
        return None

    existing = (
        db.query(PortfolioHolding)
        .filter(PortfolioHolding.portfolio_id == portfolio.id, PortfolioHolding.ticker == security.ticker)
        .first()
    )
    if existing:
        old_quantity = float(existing.quantity)
        new_quantity = old_quantity + quantity
        old_cost_basis = old_quantity * float(existing.average_cost_mad)
        added_cost_basis = quantity * average_cost_mad
        existing.quantity = new_quantity
        existing.average_cost_mad = (old_cost_basis + added_cost_basis) / new_quantity
        existing.manual_note = manual_note or existing.manual_note
        existing.opened_at = opened_at or existing.opened_at
    else:
        db.add(
            PortfolioHolding(
                portfolio_id=portfolio.id,
                ticker=security.ticker,
                quantity=quantity,
                average_cost_mad=average_cost_mad,
                manual_note=manual_note,
                opened_at=opened_at,
            )
        )

    db.commit()
    db.refresh(portfolio)
    return _portfolio_output(db, portfolio)


def calculate_portfolio_pnl(db: Session, portfolio_id: UUID) -> dict | None:
    portfolio = get_portfolio(db, portfolio_id)
    if not portfolio:
        return None

    output = _portfolio_output(db, portfolio)
    holding_rows = db.query(PortfolioHolding).filter(PortfolioHolding.portfolio_id == portfolio.id).all()
    cost_basis = sum(float(holding.quantity) * float(holding.average_cost_mad) for holding in holding_rows)
    current_value = output["total_value_mad"]
    unrealized_pl = current_value - cost_basis
    return {
        "portfolio_id": portfolio.id,
        "portfolio_name": portfolio.name,
        "base_currency": portfolio.base_currency,
        "cost_basis_mad": cost_basis,
        "current_value_mad": current_value,
        "unrealized_pl_mad": unrealized_pl,
        "unrealized_pl_pct": round((unrealized_pl / cost_basis) * 100, 2) if cost_basis else 0.0,
        "holdings": output["holdings"],
    }
