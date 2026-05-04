from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import RulesSignalOut, RulesSignalRequest, SignalExplanationOut, SignalExplanationRequest, SignalOut
from app.services.signals import explain_signal, generate_rules_signal, get_latest_signal, list_signals

router = APIRouter(prefix="/signals", tags=["buy hold sell signal engine"])


@router.get("", response_model=list[SignalOut])
def signals(db: Session = Depends(get_db)):
    return list_signals(db)


@router.post("/rules", response_model=RulesSignalOut)
def rules_based_signal(payload: RulesSignalRequest):
    return generate_rules_signal(payload.model_dump())


@router.post("/explain", response_model=SignalExplanationOut)
def explain_signal_metrics(payload: SignalExplanationRequest):
    return explain_signal(payload.model_dump())


@router.get("/{ticker}", response_model=SignalOut)
def latest_signal_for_stock(ticker: str, db: Session = Depends(get_db)):
    signal = get_latest_signal(db, ticker)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal
