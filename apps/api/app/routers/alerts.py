from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import AlertReadOut, RiskAlertGenerationOut, RiskAlertGenerationRequest, RiskAlertOut
from app.services.risk import generate_portfolio_alerts, list_risk_alerts, list_unread_alerts, mark_alert_read

router = APIRouter(prefix="/alerts", tags=["risk alerts"])


@router.get("", response_model=list[RiskAlertOut])
def alerts(db: Session = Depends(get_db)):
    return list_risk_alerts(db)


@router.get("/unread", response_model=list[RiskAlertOut])
def unread_alerts(db: Session = Depends(get_db)):
    return list_unread_alerts(db)


@router.put("/{alert_id}/read", response_model=AlertReadOut)
def read_alert(alert_id: UUID, db: Session = Depends(get_db)):
    alert = mark_alert_read(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"id": alert.id, "is_read": alert.is_read}


@router.post("/generate", response_model=RiskAlertGenerationOut)
def generate_alerts(payload: RiskAlertGenerationRequest, db: Session = Depends(get_db)):
    generated = generate_portfolio_alerts(db, payload.portfolio_id)
    return {"generated": len(generated), "alerts": generated}
