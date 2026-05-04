from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import DailyOHLCVPrice, MarketSnapshot, RiskAlert, Security, StockRanking, StockSignal, User, Watchlist, WatchlistItem

LOW_LIQUIDITY_SCORE = 40
HIGH_VOLATILITY_30D = 0.22
RANKING_ALERT_THRESHOLD = 75
DAILY_MOVE_THRESHOLD = 5.0


def list_watchlists(db: Session) -> list[Watchlist]:
    return db.query(Watchlist).order_by(Watchlist.is_default.desc(), Watchlist.created_at.desc()).all()


def get_watchlist(db: Session, watchlist_id: UUID) -> Watchlist | None:
    return db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()


def _risk_level(risk_score: int | None) -> str | None:
    if risk_score is None:
        return None
    if risk_score >= 65:
        return "high"
    if risk_score >= 40:
        return "medium"
    return "low"


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


def rename_watchlist(db: Session, watchlist_id: UUID, name: str, description: str | None = None) -> Watchlist | None:
    watchlist = get_watchlist(db, watchlist_id)
    if not watchlist:
        return None
    watchlist.name = name
    watchlist.description = description
    db.commit()
    db.refresh(watchlist)
    return watchlist


def delete_watchlist(db: Session, watchlist_id: UUID) -> bool:
    watchlist = get_watchlist(db, watchlist_id)
    if not watchlist:
        return False
    db.delete(watchlist)
    db.commit()
    return True


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


def remove_watchlist_stock(db: Session, watchlist_id: UUID, ticker: str) -> bool:
    item = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.watchlist_id == watchlist_id, WatchlistItem.ticker == ticker.upper())
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


def _latest_ranking(db: Session, ticker: str) -> StockRanking | None:
    return (
        db.query(StockRanking)
        .filter(StockRanking.ticker == ticker)
        .order_by(StockRanking.rank_date.desc())
        .first()
    )


def _recent_signals(db: Session, ticker: str) -> list[StockSignal]:
    return (
        db.query(StockSignal)
        .filter(StockSignal.ticker == ticker)
        .order_by(StockSignal.signal_date.desc())
        .limit(2)
        .all()
    )


def _recent_rankings(db: Session, ticker: str) -> list[StockRanking]:
    return (
        db.query(StockRanking)
        .filter(StockRanking.ticker == ticker)
        .order_by(StockRanking.rank_date.desc())
        .limit(2)
        .all()
    )


def _recent_prices(db: Session, ticker: str) -> list[DailyOHLCVPrice]:
    return (
        db.query(DailyOHLCVPrice)
        .filter(DailyOHLCVPrice.ticker == ticker)
        .order_by(DailyOHLCVPrice.price_date.desc())
        .limit(2)
        .all()
    )


def _daily_change_pct(prices: list) -> float | None:
    if len(prices) < 2:
        return None
    latest_close = float(prices[0].close_mad)
    previous_close = float(prices[1].close_mad)
    if not previous_close:
        return None
    return round(((latest_close - previous_close) / previous_close) * 100, 2)


def watchlist_detail(db: Session, watchlist_id: UUID) -> dict | None:
    watchlist = get_watchlist(db, watchlist_id)
    if not watchlist:
        return None

    rows = db.query(WatchlistItem).filter(WatchlistItem.watchlist_id == watchlist_id).all()
    items = []
    for item in rows:
        snapshot = _latest_snapshot(db, item.ticker)
        signal = _latest_signal(db, item.ticker)
        ranking = _latest_ranking(db, item.ticker)
        recent_prices = _recent_prices(db, item.ticker)
        items.append(
            {
                "id": item.id,
                "ticker": item.ticker,
                "user_note": item.user_note,
                "alert_above_mad": item.alert_above_mad,
                "alert_below_mad": item.alert_below_mad,
                "latest_price_mad": float(snapshot.price_mad) if snapshot else None,
                "signal": signal.signal if signal else None,
                "ranking_score": ranking.ai_score if ranking else None,
                "daily_change_pct": _daily_change_pct(recent_prices),
                "risk_level": _risk_level(ranking.risk_score if ranking else None),
                "liquidity_score": ranking.liquidity_score if ranking else None,
                "volatility_30d": float(snapshot.volatility_30d) if snapshot and snapshot.volatility_30d is not None else None,
            }
        )
    return {
        "id": watchlist.id,
        "name": watchlist.name,
        "description": watchlist.description,
        "is_default": watchlist.is_default,
        "items": items,
    }


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


def build_watchlist_trigger_alerts(
    watchlist: Watchlist,
    items: list,
    recent_signal_lookup,
    recent_price_lookup,
    recent_ranking_lookup,
    snapshot_lookup,
) -> list[dict]:
    alerts: list[dict] = []
    for item in items:
        signals = recent_signal_lookup(item.ticker)
        if len(signals) >= 2 and signals[0].signal != signals[1].signal:
            alerts.append(
                {
                    "alert_type": "signal_change",
                    "severity": "Medium",
                    "symbol": item.ticker,
                    "message": f"{item.ticker} research signal changed from {signals[1].signal} to {signals[0].signal}.",
                    "recommended_action": "Review the updated explanation and source data. This is not a trade instruction.",
                    "current_price_mad": None,
                }
            )

        prices = recent_price_lookup(item.ticker)
        daily_change = _daily_change_pct(prices)
        if daily_change is not None and abs(daily_change) > DAILY_MOVE_THRESHOLD:
            alerts.append(
                {
                    "alert_type": "daily_price_move",
                    "severity": "High" if abs(daily_change) >= 10 else "Medium",
                    "symbol": item.ticker,
                    "message": f"{item.ticker} moved {daily_change:.2f}% in the latest daily close.",
                    "recommended_action": "Review news, liquidity, and data quality before relying on this move.",
                    "current_price_mad": float(prices[0].close_mad),
                }
            )

        rankings = recent_ranking_lookup(item.ticker)
        if rankings:
            latest = rankings[0]
            previous = rankings[1] if len(rankings) >= 2 else None
            if latest.ai_score > RANKING_ALERT_THRESHOLD and (not previous or previous.ai_score <= RANKING_ALERT_THRESHOLD):
                alerts.append(
                    {
                        "alert_type": "ranking_threshold",
                        "severity": "Medium",
                        "symbol": item.ticker,
                        "message": f"{item.ticker} ranking score crossed above {RANKING_ALERT_THRESHOLD} and is now {latest.ai_score}.",
                        "recommended_action": "Review the ranking drivers and risk note; this is research only.",
                        "current_price_mad": None,
                    }
                )
            latest_risk = _risk_level(latest.risk_score)
            previous_risk = _risk_level(previous.risk_score) if previous else None
            if previous_risk and latest_risk and ["low", "medium", "high"].index(latest_risk) > ["low", "medium", "high"].index(previous_risk):
                alerts.append(
                    {
                        "alert_type": "risk_level_increase",
                        "severity": "High" if latest_risk == "high" else "Medium",
                        "symbol": item.ticker,
                        "message": f"{item.ticker} risk level increased from {previous_risk} to {latest_risk}.",
                        "recommended_action": "Review volatility, liquidity, and portfolio exposure before any manual decision.",
                        "current_price_mad": None,
                    }
                )
            if latest.liquidity_score < LOW_LIQUIDITY_SCORE:
                alerts.append(
                    {
                        "alert_type": "low_liquidity",
                        "severity": "High",
                        "symbol": item.ticker,
                        "message": f"{item.ticker} is now flagged as low liquidity with liquidity score {latest.liquidity_score}.",
                        "recommended_action": "Use conservative assumptions and verify trading value before relying on analysis.",
                        "current_price_mad": None,
                    }
                )

        snapshot = snapshot_lookup(item.ticker)
        volatility_30d = getattr(snapshot, "volatility_30d", None) if snapshot else None
        if snapshot and volatility_30d is not None and float(volatility_30d) > HIGH_VOLATILITY_30D:
            alerts.append(
                {
                    "alert_type": "high_volatility",
                    "severity": "Medium",
                    "symbol": item.ticker,
                    "message": f"{item.ticker} has elevated 30-day volatility.",
                    "recommended_action": "Review whether this volatility fits the user's risk profile.",
                    "current_price_mad": float(snapshot.price_mad),
                }
            )
    return alerts


def _persist_user_alerts(db: Session, watchlist: Watchlist, alert_payloads: list[dict]) -> list[RiskAlert]:
    rows = []
    for alert in alert_payloads:
        row = RiskAlert(
            user_id=watchlist.user_id,
            watchlist_id=watchlist.id,
            ticker=alert.get("symbol"),
            alert_type=alert["alert_type"],
            severity=alert["severity"].lower(),
            title=alert["alert_type"].replace("_", " ").title(),
            detail=alert["message"],
            trigger_payload={
                "recommended_action": alert["recommended_action"],
                "current_price_mad": alert.get("current_price_mad"),
            },
            is_read=False,
        )
        db.add(row)
        rows.append(row)
    if rows:
        db.commit()
        for row in rows:
            db.refresh(row)
    return rows


def get_watchlist_alerts(db: Session, watchlist_id: UUID) -> list[dict] | None:
    watchlist = get_watchlist(db, watchlist_id)
    if not watchlist:
        return None
    items = db.query(WatchlistItem).filter(WatchlistItem.watchlist_id == watchlist_id).all()
    return build_watchlist_user_alerts(watchlist, items, lambda ticker: _latest_snapshot(db, ticker), lambda ticker: _latest_signal(db, ticker))


def generate_and_store_watchlist_alerts(db: Session, watchlist_id: UUID) -> list[RiskAlert] | None:
    watchlist = get_watchlist(db, watchlist_id)
    if not watchlist:
        return None
    items = db.query(WatchlistItem).filter(WatchlistItem.watchlist_id == watchlist_id).all()
    threshold_alerts = build_watchlist_user_alerts(watchlist, items, lambda ticker: _latest_snapshot(db, ticker), lambda ticker: _latest_signal(db, ticker))
    trigger_alerts = build_watchlist_trigger_alerts(
        watchlist,
        items,
        lambda ticker: _recent_signals(db, ticker),
        lambda ticker: _recent_prices(db, ticker),
        lambda ticker: _recent_rankings(db, ticker),
        lambda ticker: _latest_snapshot(db, ticker),
    )
    return _persist_user_alerts(db, watchlist, threshold_alerts + trigger_alerts)
