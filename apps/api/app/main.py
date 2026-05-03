from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import alerts, assistant, market, portfolio, rankings, signals, stocks, watchlists

settings = get_settings()

app = FastAPI(
    title="Morocco AI Market Assistant API",
    description="AI Moroccan stock market assistant with ranked stocks, explainable signals, manual portfolios, and risk alerts.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router)
app.include_router(stocks.router)
app.include_router(rankings.router)
app.include_router(signals.router)
app.include_router(portfolio.router)
app.include_router(alerts.router)
app.include_router(watchlists.router)
app.include_router(assistant.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name, "env": settings.app_env}
