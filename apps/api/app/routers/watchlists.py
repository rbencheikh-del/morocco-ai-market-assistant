from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import WatchlistOut
from app.services.watchlists import list_watchlists

router = APIRouter(prefix="/watchlists", tags=["watchlists"])


@router.get("", response_model=list[WatchlistOut])
def watchlists(db: Session = Depends(get_db)):
    return list_watchlists(db)
