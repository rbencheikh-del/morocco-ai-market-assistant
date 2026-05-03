from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import RiskAlertGenerationOut, RiskAlertGenerationRequest, RiskAlertOut
from app.services.risk import generate_portfolio_alerts, list_risk_alerts

router = APIRouter(prefix="/alerts", tags=["risk alerts"])


@router.get("", response_model=list[RiskAlertOut])
def alerts(db: Session = Depends(get_db)):
    return list_risk_alerts(db)


@router.post("/generate", response_model=RiskAlertGenerationOut)
def generate_alerts(payload: RiskAlertGenerationRequest, db: Session = Depends(get_db)):
    generated = generate_portfolio_alerts(db, payload.portfolio_id)
    return {"generated": len(generated), "alerts": generated}
