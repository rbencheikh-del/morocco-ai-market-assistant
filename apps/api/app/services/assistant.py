import re
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import ModelAuditLog

KNOWN_TICKERS = {"ATW", "IAM", "LHM", "TQM", "BOA", "MNG", "BCP", "AKT"}
DISCLAIMER = "This assistant provides research support only. This is not financial advice and no trade execution is available."


def extract_tickers(question: str, requested: list[str]) -> list[str]:
    found = set(requested)
    tokens = set(re.findall(r"\b[A-Z]{2,5}\b", question.upper()))
    found.update(tokens.intersection(KNOWN_TICKERS))
    return sorted(found)


def answer_question(db: Session, question: str, risk_profile: str, tickers: list[str]) -> dict:
    scoped_tickers = extract_tickers(question, tickers)
    if scoped_tickers:
        subject = ", ".join(scoped_tickers)
        answer = (
            f"For {subject}, the assistant would review ranking score, latest signal, liquidity, sector exposure, "
            f"and fit with a {risk_profile} manual portfolio before showing buy/hold/sell research."
        )
    else:
        answer = (
            "The assistant can answer questions about Casablanca-listed stocks, ranked signals, manual portfolios, "
            "and risk alerts. Add a ticker such as ATW, IAM, LHM, TQM, or BOA."
        )

    output = {
        "answer": answer,
        "tickers": scoped_tickers,
        "citations": ["stock_rankings", "stock_signals", "market_snapshots"],
        "disclaimer": DISCLAIMER,
    }
    audit = ModelAuditLog(
        request_type="ask_stocks",
        prompt=question,
        input_payload={"question": question, "risk_profile": risk_profile, "tickers": tickers},
        output_payload=output,
        model_version="assistant-mock-v1",
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    output["audit_id"] = audit.id
    return output
