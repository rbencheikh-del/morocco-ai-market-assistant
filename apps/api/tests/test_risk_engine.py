from types import SimpleNamespace
from uuid import uuid4

from app.services import portfolio as portfolio_service
from app.services import risk as risk_service


class FakeDb:
    def __init__(self):
        self.added = []
        self.committed = False

    def add_all(self, rows):
        self.added.extend(rows)

    def commit(self):
        self.committed = True

    def refresh(self, row):
        if getattr(row, "id", None) is None:
            row.id = uuid4()


def test_portfolio_concentration_above_25_percent_triggers_alert(monkeypatch):
    portfolio_id = uuid4()
    user_id = uuid4()
    portfolio = SimpleNamespace(id=portfolio_id, user_id=user_id)
    db = FakeDb()

    monkeypatch.setattr(risk_service, "get_portfolio", lambda _db, _portfolio_id: portfolio)
    monkeypatch.setattr(
        risk_service,
        "calculate_portfolio_pnl",
        lambda _db, _portfolio_id: {
            "holdings": [
                {
                    "ticker": "ATW",
                    "allocation_pct": 26.0,
                    "unrealized_pl_mad": 0.0,
                    "market_value_mad": 26_000.0,
                },
                {
                    "ticker": "IAM",
                    "allocation_pct": 74.0,
                    "unrealized_pl_mad": 0.0,
                    "market_value_mad": 74_000.0,
                },
            ]
        },
    )
    monkeypatch.setattr(risk_service, "_latest_signal", lambda _db, _ticker: None)

    alerts = risk_service.generate_portfolio_alerts(db, portfolio_id)

    concentration_alerts = [alert for alert in alerts if alert.alert_type == "concentration"]
    assert concentration_alerts
    assert any(alert.ticker == "ATW" for alert in concentration_alerts)
    assert db.committed is True


class NoSnapshotQuery:
    def filter(self, *_args, **_kwargs):
        return self

    def order_by(self, *_args, **_kwargs):
        return self

    def first(self):
        return None


class NoSnapshotDb:
    def query(self, *_args, **_kwargs):
        return NoSnapshotQuery()


def test_missing_price_data_fails_safely_with_average_cost_fallback():
    fallback_price = portfolio_service._latest_price(NoSnapshotDb(), "ATW", fallback=462.0)

    assert fallback_price == 462.0
