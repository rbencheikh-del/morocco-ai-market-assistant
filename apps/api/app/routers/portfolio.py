from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.schemas import AddHoldingRequest, PortfolioOut, PortfolioPnlOut
from app.services.portfolio import add_holding, calculate_portfolio_pnl, get_demo_portfolio

router = APIRouter(prefix="/portfolio", tags=["manual portfolio tracker"])


@router.get("/demo", response_model=PortfolioOut)
def demo_portfolio(db: Session = Depends(get_db)):
    portfolio = get_demo_portfolio(db)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Demo portfolio not found")
    return portfolio


@router.post("/{portfolio_id}/holdings", response_model=PortfolioOut)
def add_portfolio_holding(portfolio_id: UUID, payload: AddHoldingRequest, db: Session = Depends(get_db)):
    portfolio = add_holding(
        db,
        portfolio_id=portfolio_id,
        ticker=payload.ticker,
        quantity=payload.quantity,
        average_cost_mad=payload.average_cost_mad,
        manual_note=payload.manual_note,
        opened_at=payload.opened_at,
    )
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio or stock not found")
    return portfolio


@router.get("/{portfolio_id}/pnl", response_model=PortfolioPnlOut)
def portfolio_pnl(portfolio_id: UUID, db: Session = Depends(get_db)):
    pnl = calculate_portfolio_pnl(db, portfolio_id)
    if not pnl:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return pnl
