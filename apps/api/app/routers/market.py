from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import DailyOHLCVOut, IngestionResult, MarketSnapshotOut, SecurityOut
from app.services.market_data import daily_ohlcv_history, ingest_mock_snapshots, latest_snapshots, list_securities

router = APIRouter(prefix="/market", tags=["market data"])


@router.get("/securities", response_model=list[SecurityOut])
def securities(db: Session = Depends(get_db)):
    return list_securities(db)


@router.get("/snapshots/latest", response_model=list[MarketSnapshotOut])
def latest_market_snapshots(db: Session = Depends(get_db)):
    return latest_snapshots(db)


@router.get("/prices/{ticker}/daily", response_model=list[DailyOHLCVOut])
def daily_prices(ticker: str, limit: int = 120, db: Session = Depends(get_db)):
    return daily_ohlcv_history(db, ticker, limit)


@router.post("/ingest/mock", response_model=IngestionResult)
def ingest_mock_market_data(db: Session = Depends(get_db)):
    inserted = ingest_mock_snapshots(db)
    return {"inserted": inserted, "mode": "mock"}
