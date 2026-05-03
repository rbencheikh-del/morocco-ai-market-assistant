from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import SecurityOut, StockDetailOut
from app.services.market_data import get_stock_detail, list_securities

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("", response_model=list[SecurityOut])
def list_stocks(db: Session = Depends(get_db)):
    return list_securities(db)


@router.get("/{ticker}", response_model=StockDetailOut)
def stock_details(ticker: str, db: Session = Depends(get_db)):
    detail = get_stock_detail(db, ticker)
    if not detail:
        raise HTTPException(status_code=404, detail="Stock not found")
    return detail
