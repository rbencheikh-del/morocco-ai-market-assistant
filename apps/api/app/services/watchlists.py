from sqlalchemy.orm import Session

from app.db.models import Watchlist


def list_watchlists(db: Session) -> list[Watchlist]:
    return db.query(Watchlist).order_by(Watchlist.is_default.desc(), Watchlist.created_at.desc()).all()
