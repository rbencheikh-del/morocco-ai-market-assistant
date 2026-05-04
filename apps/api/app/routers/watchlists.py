from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import (
    AddWatchlistItemRequest,
    CreateWatchlistRequest,
    RenameWatchlistRequest,
    RiskAlertOut,
    UpdateWatchlistItemRequest,
    UserAlertOut,
    WatchlistDetailOut,
    WatchlistOut,
)
from app.services.watchlists import (
    add_watchlist_item,
    create_watchlist,
    delete_watchlist,
    generate_and_store_watchlist_alerts,
    get_watchlist,
    get_watchlist_alerts,
    list_watchlists,
    remove_watchlist_item,
    remove_watchlist_stock,
    rename_watchlist,
    update_watchlist_item,
    watchlist_detail as get_watchlist_detail,
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


@router.get("/{watchlist_id}", response_model=WatchlistDetailOut)
def watchlist_detail(watchlist_id: UUID, db: Session = Depends(get_db)):
    detail = get_watchlist_detail(db, watchlist_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return detail


@router.put("/{watchlist_id}", response_model=WatchlistOut)
def rename_user_watchlist(watchlist_id: UUID, payload: RenameWatchlistRequest, db: Session = Depends(get_db)):
    watchlist = rename_watchlist(db, watchlist_id, payload.name, payload.description)
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return watchlist


@router.delete("/{watchlist_id}", status_code=204)
def delete_user_watchlist(watchlist_id: UUID, db: Session = Depends(get_db)):
    deleted = delete_watchlist(db, watchlist_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return Response(status_code=204)


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


@router.post("/{watchlist_id}/stocks", response_model=WatchlistOut)
def add_stock(watchlist_id: UUID, payload: AddWatchlistItemRequest, db: Session = Depends(get_db)):
    return add_item(watchlist_id, payload, db)


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


@router.delete("/{watchlist_id}/stocks/{symbol}", status_code=204)
def delete_stock(watchlist_id: UUID, symbol: str, db: Session = Depends(get_db)):
    deleted = remove_watchlist_stock(db, watchlist_id, symbol)
    if not deleted:
        raise HTTPException(status_code=404, detail="Watchlist stock not found")
    return Response(status_code=204)


@router.get("/{watchlist_id}/alerts", response_model=list[UserAlertOut])
def watchlist_alerts(watchlist_id: UUID, db: Session = Depends(get_db)):
    alerts = get_watchlist_alerts(db, watchlist_id)
    if alerts is None:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return alerts


@router.post("/{watchlist_id}/alerts/generate", response_model=list[RiskAlertOut])
def generate_watchlist_alerts(watchlist_id: UUID, db: Session = Depends(get_db)):
    alerts = generate_and_store_watchlist_alerts(db, watchlist_id)
    if alerts is None:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return alerts
