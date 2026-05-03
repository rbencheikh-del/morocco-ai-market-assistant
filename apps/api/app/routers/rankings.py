from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import RankedStockOut
from app.services.ranking import get_ranked_stocks, get_stock_ranking

router = APIRouter(prefix="/rankings", tags=["stock ranking engine"])


@router.get("", response_model=list[RankedStockOut])
def ranked_stocks(db: Session = Depends(get_db)):
    return get_ranked_stocks(db)


@router.get("/{ticker}", response_model=RankedStockOut)
def stock_ai_ranking(ticker: str, db: Session = Depends(get_db)):
    ranking = get_stock_ranking(db, ticker)
    if not ranking:
        raise HTTPException(status_code=404, detail="AI ranking not found")
    return ranking
