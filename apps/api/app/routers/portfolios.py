from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import (
    AddHoldingRequest,
    CreatePortfolioRequest,
    PortfolioOut,
    PortfolioPnlOut,
    PortfolioRiskAlertOut,
    UpdateHoldingRequest,
)
from app.services.portfolio import (
    add_holding,
    calculate_portfolio_pnl,
    create_portfolio,
    get_portfolio_output,
    remove_holding,
    update_holding,
)
from app.services.risk import get_portfolio_risk_alerts

router = APIRouter(prefix="/portfolios", tags=["portfolio tracker"])


@router.post("", response_model=PortfolioOut, status_code=201)
def create_manual_portfolio(payload: CreatePortfolioRequest, db: Session = Depends(get_db)):
    portfolio = create_portfolio(
        db,
        name=payload.name,
        user_id=payload.user_id,
        base_currency=payload.base_currency,
        risk_profile=payload.risk_profile,
    )
    if not portfolio:
        raise HTTPException(status_code=404, detail="User not found")
    return portfolio


@router.get("/{portfolio_id}", response_model=PortfolioOut)
def get_manual_portfolio(portfolio_id: UUID, db: Session = Depends(get_db)):
    portfolio = get_portfolio_output(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


@router.post("/{portfolio_id}/holdings", response_model=PortfolioOut)
def add_manual_holding(portfolio_id: UUID, payload: AddHoldingRequest, db: Session = Depends(get_db)):
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


@router.put("/{portfolio_id}/holdings/{holding_id}", response_model=PortfolioOut)
def update_manual_holding(
    portfolio_id: UUID,
    holding_id: UUID,
    payload: UpdateHoldingRequest,
    db: Session = Depends(get_db),
):
    portfolio = update_holding(
        db,
        portfolio_id=portfolio_id,
        holding_id=holding_id,
        quantity=payload.quantity,
        average_cost_mad=payload.average_cost_mad,
        manual_note=payload.manual_note,
    )
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio holding not found")
    return portfolio


@router.delete("/{portfolio_id}/holdings/{holding_id}", status_code=204)
def delete_manual_holding(portfolio_id: UUID, holding_id: UUID, db: Session = Depends(get_db)):
    deleted = remove_holding(db, portfolio_id, holding_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Portfolio holding not found")
    return Response(status_code=204)


@router.get("/{portfolio_id}/summary", response_model=PortfolioPnlOut)
def get_portfolio_summary(portfolio_id: UUID, db: Session = Depends(get_db)):
    pnl = calculate_portfolio_pnl(db, portfolio_id)
    if not pnl:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return pnl


@router.get("/{portfolio_id}/risk-alerts", response_model=list[PortfolioRiskAlertOut])
def get_manual_portfolio_risk_alerts(portfolio_id: UUID, db: Session = Depends(get_db)):
    alerts = get_portfolio_risk_alerts(db, portfolio_id)
    if alerts is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return alerts
