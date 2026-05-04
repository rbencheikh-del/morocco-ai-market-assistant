from sqlalchemy.orm import Session

from app.services.market_ingestion import run_daily_refresh


def refresh_market_data(db: Session) -> dict:
    """Manual/scheduler entry point for daily market data refreshes."""
    return run_daily_refresh(db)
