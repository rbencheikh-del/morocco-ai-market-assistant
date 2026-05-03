from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import AskRequest, AskResponse
from app.services.assistant import answer_question

router = APIRouter(prefix="/assistant", tags=["AI assistant"])


@router.post("/ask", response_model=AskResponse)
def ask_stocks(payload: AskRequest, db: Session = Depends(get_db)):
    return answer_question(db, payload.question, payload.risk_profile, payload.tickers)
