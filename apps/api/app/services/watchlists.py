from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import MarketSnapshot, Security, StockSignal, User, Watchlist, WatchlistItem


def list_watchlists(db: Session) -> list[Watchlist]:
    return db.query(Watchlist).order_by(Watchlist.is_default.desc(), Watchlist.created_at.desc()).all()


def get_watchlist(db: Session, watchlist_id: UUID) -> Watchlist | None:
    return db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()


def create_watchlist(
    db: Session,
    name: str,
    description: str | None = None,
    user_id: UUID | None = None,
    is_default: bool = False,
) -> Watchlist | None:
    user = db.query(User).filter(User.id == user_id).first() if user_id else db.query(User).order_by(User.created_at.asc()).first()
    if not user:
        return None
    watchlist = Watchlist(user_id=user.id, name=name, description=description, is_default=is_default)
    db.add(watchlist)
    db.commit()
    db.refresh(watchlist)
    return watchlist


def add_watchlist_item(
    db: Session,
    watchlist_id: UUID,
    ticker: str,
    user_note: str | None = None,
    alert_above_mad: float | None = None,
    alert_below_mad: float | None = None,
) -> Watchlist | None:
    watchlist = get_watchlist(db, watchlist_id)
    security = db.query(Security).filter(Security.ticker == ticker.upper(), Security.is_active.is_(True)).first()
    if not watchlist or not security:
        return None

    existing = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.watchlist_id == watchlist.id, WatchlistItem.ticker == security.ticker)
        .first()
    )
    if existing:
        existing.user_note = user_note if user_note is not None else existing.user_note
        existing.alert_above_mad = alert_above_mad
        existing.alert_below_mad = alert_below_mad
    else:
        db.add(
            WatchlistItem(
                watchlist_id=watchlist.id,
                ticker=security.ticker,
                user_note=user_note,
                alert_above_mad=alert_above_mad,
                alert_below_mad=alert_below_mad,
            )
        )
    db.commit()
    db.refresh(watchlist)
    return watchlist


def update_watchlist_item(
    db: Session,
    watchlist_id: UUID,
    item_id: UUID,
    user_note: str | None = None,
    alert_above_mad: float | None = None,
    alert_below_mad: float | None = None,
) -> Watchlist | None:
    watchlist = get_watchlist(db, watchlist_id)
    item = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.watchlist_id == watchlist_id, WatchlistItem.id == item_id)
        .first()
    )
    if not watchlist or not item:
        return None
    item.user_note = user_note if user_note is not None else item.user_note
    item.alert_above_mad = alert_above_mad
    item.alert_below_mad = alert_below_mad
    db.commit()
    db.refresh(watchlist)
    return watchlist


def remove_watchlist_item(db: Session, watchlist_id: UUID, item_id: UUID) -> bool:
    item = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.watchlist_id == watchlist_id, WatchlistItem.id == item_id)
        .first()
    )
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def _latest_snapshot(db: Session, ticker: str) -> MarketSnapshot | None:
    return (
        db.query(MarketSnapshot)
        .filter(MarketSnapshot.ticker == ticker)
        .order_by(MarketSnapshot.as_of.desc())
        .first()
    )


def _latest_signal(db: Session, ticker: str) -> StockSignal | None:
    return (
        db.query(StockSignal)
        .filter(StockSignal.ticker == ticker)
        .order_by(StockSignal.signal_date.desc())
        .first()
    )


def build_watchlist_user_alerts(watchlist: Watchlist, items: list, price_lookup, signal_lookup) -> list[dict]:
    alerts: list[dict] = []
    for item in items:
        snapshot = price_lookup(item.ticker)
        if not snapshot:
            alerts.append(
                {
                    "alert_type": "missing_market_price",
                    "severity": "Medium",
                    "symbol": item.ticker,
                    "message": f"{item.ticker} has no latest market price available for this watchlist.",
                    "recommended_action": "Refresh or verify market data before relying on this alert.",
                    "current_price_mad": None,
                }
            )
            continue

        current_price = float(snapshot.price_mad)
        if item.alert_above_mad is not None and current_price >= float(item.alert_above_mad):
            alerts.append(
                {
                    "alert_type": "price_above_threshold",
                    "severity": "Medium",
                    "symbol": item.ticker,
                    "message": f"{item.ticker} is at {current_price:.2f} MAD, above the user alert level of {float(item.alert_above_mad):.2f} MAD.",
                    "recommended_action": "Review the stock research page. This alert is not a trade instruction.",
                    "current_price_mad": current_price,
                }
            )
        if item.alert_below_mad is not None and current_price <= float(item.alert_below_mad):
            alerts.append(
                {
                    "alert_type": "price_below_threshold",
                    "severity": "Medium",
                    "symbol": item.ticker,
                    "message": f"{item.ticker} is at {current_price:.2f} MAD, below the user alert level of {float(item.alert_below_mad):.2f} MAD.",
                    "recommended_action": "Review the stock risk notes before making any manual decision.",
                    "current_price_mad": current_price,
                }
            )

        signal = signal_lookup(item.ticker)
        if signal and signal.signal == "SELL":
            alerts.append(
                {
                    "alert_type": "signal_watch",
                    "severity": "High" if signal.confidence >= 70 else "Medium",
                    "symbol": item.ticker,
                    "message": f"{item.ticker} has a SELL/AVOID research signal with {signal.confidence}% confidence.",
                    "recommended_action": "Review the explanation and data freshness. No order can be placed in this app.",
                    "current_price_mad": current_price,
                }
            )
    return alerts


def get_watchlist_alerts(db: Session, watchlist_id: UUID) -> list[dict] | None:
    watchlist = get_watchlist(db, watchlist_id)
    if not watchlist:
        return None
    items = db.query(WatchlistItem).filter(WatchlistItem.watchlist_id == watchlist_id).all()
    return build_watchlist_user_alerts(watchlist, items, lambda ticker: _latest_snapshot(db, ticker), lambda ticker: _latest_signal(db, ticker))
