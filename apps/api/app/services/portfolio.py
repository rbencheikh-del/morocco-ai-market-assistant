from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import ManualPortfolio, MarketSnapshot, PortfolioHolding, Security, User


def _latest_price_info(db: Session, ticker: str, fallback: float) -> dict:
    snapshot = (
        db.query(MarketSnapshot)
        .filter(MarketSnapshot.ticker == ticker)
        .order_by(MarketSnapshot.as_of.desc())
        .first()
    )
    if snapshot:
        return {
            "current_price_mad": float(snapshot.price_mad),
            "price_status": "live",
            "price_as_of": snapshot.as_of,
            "avg_daily_traded_value_mad": float(snapshot.price_mad) * float(snapshot.volume),
            "volatility_30d": float(snapshot.volatility_30d) if snapshot.volatility_30d is not None else None,
            "data_quality_note": None,
        }
    return {
        "current_price_mad": fallback,
        "price_status": "missing",
        "price_as_of": None,
        "avg_daily_traded_value_mad": 0.0,
        "volatility_30d": None,
        "data_quality_note": "No latest market price was available; average cost is used as a fallback.",
    }


def _latest_price(db: Session, ticker: str, fallback: float) -> float:
    return _latest_price_info(db, ticker, fallback)["current_price_mad"]


def _security_sector(db: Session, ticker: str) -> str:
    security = db.query(Security).filter(Security.ticker == ticker).first()
    return security.sector if security else "Unknown"


def build_portfolio_summary(portfolio: ManualPortfolio, holding_rows: list, market_data_lookup, sector_lookup) -> dict:
    holdings = []
    sector_exposures: dict[str, float] = {}
    data_quality_warnings: list[str] = []
    total_value = 0.0
    cost_basis = 0.0

    for holding in holding_rows:
        average_cost = float(holding.average_cost_mad)
        quantity = float(holding.quantity)
        price_info = market_data_lookup(holding.ticker, average_cost)
        current_price = float(price_info["current_price_mad"])
        market_value = quantity * current_price
        holding_cost_basis = quantity * average_cost
        sector = sector_lookup(holding.ticker)
        total_value += market_value
        cost_basis += holding_cost_basis
        sector_exposures[sector] = sector_exposures.get(sector, 0.0) + market_value
        if price_info.get("data_quality_note"):
            data_quality_warnings.append(f"{holding.ticker}: {price_info['data_quality_note']}")
        holdings.append(
            {
                "id": holding.id,
                "ticker": holding.ticker,
                "sector": sector,
                "quantity": quantity,
                "average_cost_mad": average_cost,
                "current_price_mad": current_price,
                "price_status": price_info["price_status"],
                "price_as_of": price_info["price_as_of"],
                "avg_daily_traded_value_mad": price_info["avg_daily_traded_value_mad"],
                "volatility_30d": price_info["volatility_30d"],
                "market_value_mad": market_value,
                "unrealized_pl_mad": market_value - holding_cost_basis,
                "unrealized_pl_pct": round(((market_value - holding_cost_basis) / holding_cost_basis) * 100, 2)
                if holding_cost_basis
                else 0.0,
                "allocation_pct": 0.0,
                "manual_note": holding.manual_note,
            }
        )

    for holding in holdings:
        holding["allocation_pct"] = round((holding["market_value_mad"] / total_value) * 100, 2) if total_value else 0

    sector_allocations = {
        sector: round((value / total_value) * 100, 2) if total_value else 0.0
        for sector, value in sector_exposures.items()
    }
    unrealized_pl = total_value - cost_basis
    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "base_currency": portfolio.base_currency,
        "total_value_mad": total_value,
        "cost_basis_mad": cost_basis,
        "unrealized_pl_mad": unrealized_pl,
        "unrealized_pl_pct": round((unrealized_pl / cost_basis) * 100, 2) if cost_basis else 0.0,
        "sector_allocations": sector_allocations,
        "data_quality_warnings": data_quality_warnings,
        "holdings": holdings,
    }


def _portfolio_output(db: Session, portfolio: ManualPortfolio) -> dict:
    holding_rows = db.query(PortfolioHolding).filter(PortfolioHolding.portfolio_id == portfolio.id).all()
    return build_portfolio_summary(
        portfolio,
        holding_rows,
        lambda ticker, fallback: _latest_price_info(db, ticker, fallback),
        lambda ticker: _security_sector(db, ticker),
    )


def get_demo_portfolio(db: Session) -> dict | None:
    portfolio = db.query(ManualPortfolio).order_by(ManualPortfolio.created_at.desc()).first()
    if not portfolio:
        return None
    return _portfolio_output(db, portfolio)


def get_portfolio(db: Session, portfolio_id: UUID) -> ManualPortfolio | None:
    return db.query(ManualPortfolio).filter(ManualPortfolio.id == portfolio_id).first()


def get_portfolio_output(db: Session, portfolio_id: UUID) -> dict | None:
    portfolio = get_portfolio(db, portfolio_id)
    if not portfolio:
        return None
    return _portfolio_output(db, portfolio)


def create_portfolio(
    db: Session,
    name: str,
    user_id: UUID | None = None,
    base_currency: str = "MAD",
    risk_profile: str = "balanced",
) -> dict | None:
    user = db.query(User).filter(User.id == user_id).first() if user_id else db.query(User).order_by(User.created_at.asc()).first()
    if not user:
        return None
    portfolio = ManualPortfolio(
        user_id=user.id,
        name=name,
        base_currency=base_currency,
        risk_profile=risk_profile,
        is_default=False,
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return _portfolio_output(db, portfolio)


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


def update_holding(
    db: Session,
    portfolio_id: UUID,
    holding_id: UUID,
    quantity: float,
    average_cost_mad: float,
    manual_note: str | None = None,
) -> dict | None:
    portfolio = get_portfolio(db, portfolio_id)
    holding = (
        db.query(PortfolioHolding)
        .filter(PortfolioHolding.portfolio_id == portfolio_id, PortfolioHolding.id == holding_id)
        .first()
    )
    if not portfolio or not holding:
        return None
    holding.quantity = quantity
    holding.average_cost_mad = average_cost_mad
    holding.manual_note = manual_note if manual_note is not None else holding.manual_note
    db.commit()
    db.refresh(portfolio)
    return _portfolio_output(db, portfolio)


def remove_holding(db: Session, portfolio_id: UUID, holding_id: UUID) -> bool:
    holding = (
        db.query(PortfolioHolding)
        .filter(PortfolioHolding.portfolio_id == portfolio_id, PortfolioHolding.id == holding_id)
        .first()
    )
    if not holding:
        return False
    db.delete(holding)
    db.commit()
    return True


def calculate_portfolio_pnl(db: Session, portfolio_id: UUID) -> dict | None:
    portfolio = get_portfolio(db, portfolio_id)
    if not portfolio:
        return None

    output = _portfolio_output(db, portfolio)
    return {
        "portfolio_id": portfolio.id,
        "portfolio_name": portfolio.name,
        "base_currency": portfolio.base_currency,
        "cost_basis_mad": output["cost_basis_mad"],
        "current_value_mad": output["total_value_mad"],
        "unrealized_pl_mad": output["unrealized_pl_mad"],
        "unrealized_pl_pct": output["unrealized_pl_pct"],
        "sector_allocations": output["sector_allocations"],
        "data_quality_warnings": output["data_quality_warnings"],
        "holdings": output["holdings"],
    }
