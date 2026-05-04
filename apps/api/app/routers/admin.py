from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import DataQualityReportOut, DailyRefreshOut, ImportStatusOut, PriceImportOut
from app.services.market_ingestion import data_quality_report, import_prices_from_csv, latest_import_status, run_daily_refresh

router = APIRouter(prefix="/admin", tags=["admin market data"])


@router.post("/import-prices", response_model=PriceImportOut)
async def import_prices(request: Request, db: Session = Depends(get_db)):
    csv_text = (await request.body()).decode("utf-8-sig")
    source_name = request.headers.get("x-source-name", "csv_upload")
    return import_prices_from_csv(db, csv_text, source_name=source_name)


@router.get("/import-status", response_model=ImportStatusOut)
def import_status(db: Session = Depends(get_db)):
    return latest_import_status(db)


@router.get("/data-quality-report", response_model=DataQualityReportOut)
def market_data_quality_report(db: Session = Depends(get_db)):
    return data_quality_report(db)


@router.post("/daily-refresh", response_model=DailyRefreshOut)
def trigger_daily_refresh(db: Session = Depends(get_db)):
    return run_daily_refresh(db)
