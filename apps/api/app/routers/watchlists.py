from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import AddWatchlistItemRequest, CreateWatchlistRequest, UpdateWatchlistItemRequest, UserAlertOut, WatchlistOut
from app.services.watchlists import (
    add_watchlist_item,
    create_watchlist,
    get_watchlist,
    get_watchlist_alerts,
    list_watchlists,
    remove_watchlist_item,
    update_watchlist_item,
)

router = APIRouter(prefix="/watchlists", tags=["watchlists"])


@router.get("", response_model=list[WatchlistOut])
def watchlists(db: Session = Depends(get_db)):
    return list_watchlists(db)


@router.post("", response_model=WatchlistOut, status_code=201)
def create_user_watchlist(payload: CreateWatchlistRequest, db: Session = Depends(get_db)):
    watchlist = create_watchlist(
        db,
        name=payload.name,
        description=payload.description,
        user_id=payload.user_id,
        is_default=payload.is_default,
    )
    if not watchlist:
        raise HTTPException(status_code=404, detail="User not found")
    return watchlist


@router.get("/{watchlist_id}", response_model=WatchlistOut)
def watchlist_detail(watchlist_id: UUID, db: Session = Depends(get_db)):
    watchlist = get_watchlist(db, watchlist_id)
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return watchlist


@router.post("/{watchlist_id}/items", response_model=WatchlistOut)
def add_item(watchlist_id: UUID, payload: AddWatchlistItemRequest, db: Session = Depends(get_db)):
    watchlist = add_watchlist_item(
        db,
        watchlist_id=watchlist_id,
        ticker=payload.ticker,
        user_note=payload.user_note,
        alert_above_mad=payload.alert_above_mad,
        alert_below_mad=payload.alert_below_mad,
    )
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist or stock not found")
    return watchlist


@router.put("/{watchlist_id}/items/{item_id}", response_model=WatchlistOut)
def update_item(watchlist_id: UUID, item_id: UUID, payload: UpdateWatchlistItemRequest, db: Session = Depends(get_db)):
    watchlist = update_watchlist_item(
        db,
        watchlist_id=watchlist_id,
        item_id=item_id,
        user_note=payload.user_note,
        alert_above_mad=payload.alert_above_mad,
        alert_below_mad=payload.alert_below_mad,
    )
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    return watchlist


@router.delete("/{watchlist_id}/items/{item_id}", status_code=204)
def delete_item(watchlist_id: UUID, item_id: UUID, db: Session = Depends(get_db)):
    deleted = remove_watchlist_item(db, watchlist_id, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    return Response(status_code=204)


@router.get("/{watchlist_id}/alerts", response_model=list[UserAlertOut])
def watchlist_alerts(watchlist_id: UUID, db: Session = Depends(get_db)):
    alerts = get_watchlist_alerts(db, watchlist_id)
    if alerts is None:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return alerts
