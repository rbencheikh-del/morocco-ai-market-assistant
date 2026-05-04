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
                    "unrealized_pl_pct": 0.0,
                    "market_value_mad": 26_000.0,
                    "avg_daily_traded_value_mad": 2_000_000.0,
                    "volatility_30d": 0.10,
                },
                {
                    "ticker": "IAM",
                    "allocation_pct": 74.0,
                    "unrealized_pl_mad": 0.0,
                    "unrealized_pl_pct": 0.0,
                    "market_value_mad": 74_000.0,
                    "avg_daily_traded_value_mad": 2_000_000.0,
                    "volatility_30d": 0.10,
                },
            ]
        },
    )
    monkeypatch.setattr(risk_service, "_latest_signal", lambda _db, _ticker: None)

    alerts = risk_service.generate_portfolio_alerts(db, portfolio_id)

    concentration_alerts = [alert for alert in alerts if alert.alert_type == "single_stock_exposure"]
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


def test_portfolio_valuation_and_unrealized_pnl_are_calculated():
    portfolio = SimpleNamespace(id=uuid4(), name="Test portfolio", base_currency="MAD")
    holdings = [
        SimpleNamespace(id=uuid4(), ticker="ATW", quantity=10, average_cost_mad=400, manual_note=None),
        SimpleNamespace(id=uuid4(), ticker="IAM", quantity=20, average_cost_mad=100, manual_note=None),
    ]
    prices = {
        "ATW": {
            "current_price_mad": 450,
            "price_status": "live",
            "price_as_of": None,
            "avg_daily_traded_value_mad": 3_000_000,
            "volatility_30d": 0.10,
            "data_quality_note": None,
        },
        "IAM": {
            "current_price_mad": 90,
            "price_status": "live",
            "price_as_of": None,
            "avg_daily_traded_value_mad": 3_000_000,
            "volatility_30d": 0.10,
            "data_quality_note": None,
        },
    }

    summary = portfolio_service.build_portfolio_summary(
        portfolio,
        holdings,
        lambda ticker, _fallback: prices[ticker],
        lambda ticker: "Banking" if ticker == "ATW" else "Telecoms",
    )

    assert summary["total_value_mad"] == 6_300
    assert summary["cost_basis_mad"] == 6_000
    assert summary["unrealized_pl_mad"] == 300
    assert summary["unrealized_pl_pct"] == 5.0
    assert summary["holdings"][0]["unrealized_pl_mad"] == 500
    assert summary["sector_allocations"]["Banking"] == 71.43


def test_missing_price_data_generates_data_quality_alert():
    portfolio = SimpleNamespace(id=uuid4(), user_id=uuid4())
    pnl = {
        "sector_allocations": {},
        "holdings": [
            {
                "ticker": "ATW",
                "allocation_pct": 10.0,
                "unrealized_pl_mad": 0.0,
                "unrealized_pl_pct": 0.0,
                "market_value_mad": 10_000.0,
                "price_status": "missing",
                "avg_daily_traded_value_mad": 0.0,
                "volatility_30d": None,
            }
        ],
    }

    alerts = risk_service.build_portfolio_risk_alerts(portfolio, pnl, lambda _ticker: None)

    assert alerts[0]["alert_type"] == "missing_market_price"
    assert alerts[0]["severity"] == "medium"
    assert "average cost" in alerts[0]["detail"]
    assert "Refresh or verify" in alerts[0]["trigger_payload"]["recommended_action"]


def test_sector_concentration_generates_alert():
    portfolio = SimpleNamespace(id=uuid4(), user_id=uuid4())
    pnl = {
        "sector_allocations": {"Banking": 52.0},
        "holdings": [],
    }

    alerts = risk_service.build_portfolio_risk_alerts(portfolio, pnl, lambda _ticker: None)

    assert alerts[0]["alert_type"] == "sector_exposure"
    assert alerts[0]["severity"] == "medium"
    assert "Banking" in alerts[0]["detail"]


def test_drawdown_generates_alert():
    portfolio = SimpleNamespace(id=uuid4(), user_id=uuid4())
    pnl = {
        "sector_allocations": {},
        "holdings": [
            {
                "ticker": "LHM",
                "allocation_pct": 12.0,
                "unrealized_pl_mad": -1_400.0,
                "unrealized_pl_pct": -14.0,
                "market_value_mad": 8_600.0,
                "price_status": "live",
                "avg_daily_traded_value_mad": 2_000_000.0,
                "volatility_30d": 0.10,
            }
        ],
    }

    alerts = risk_service.build_portfolio_risk_alerts(portfolio, pnl, lambda _ticker: None)

    assert alerts[0]["alert_type"] == "drawdown"
    assert alerts[0]["severity"] == "medium"
    assert "down 14.0%" in alerts[0]["detail"]


def test_low_liquidity_generates_alert():
    portfolio = SimpleNamespace(id=uuid4(), user_id=uuid4())
    pnl = {
        "sector_allocations": {},
        "holdings": [
            {
                "ticker": "DHO",
                "allocation_pct": 8.0,
                "unrealized_pl_mad": 0.0,
                "unrealized_pl_pct": 0.0,
                "market_value_mad": 8_000.0,
                "price_status": "live",
                "avg_daily_traded_value_mad": 400_000.0,
                "volatility_30d": 0.10,
            }
        ],
    }

    alerts = risk_service.build_portfolio_risk_alerts(portfolio, pnl, lambda _ticker: None)

    assert alerts[0]["alert_type"] == "low_liquidity"
    assert alerts[0]["severity"] == "high"


def test_large_gain_and_high_volatility_generate_alerts():
    portfolio = SimpleNamespace(id=uuid4(), user_id=uuid4())
    pnl = {
        "sector_allocations": {},
        "holdings": [
            {
                "ticker": "MNG",
                "allocation_pct": 12.0,
                "unrealized_pl_mad": 2_200.0,
                "unrealized_pl_pct": 22.0,
                "market_value_mad": 12_200.0,
                "price_status": "live",
                "avg_daily_traded_value_mad": 2_000_000.0,
                "volatility_30d": 0.26,
            }
        ],
    }

    alert_types = {
        alert["alert_type"] for alert in risk_service.build_portfolio_risk_alerts(portfolio, pnl, lambda _ticker: None)
    }

    assert "large_unrealized_gain" in alert_types
    assert "high_volatility" in alert_types


def test_sell_signal_conflict_generates_alert():
    portfolio = SimpleNamespace(id=uuid4(), user_id=uuid4())
    sell_signal = SimpleNamespace(signal="SELL", confidence=74)
    pnl = {
        "sector_allocations": {},
        "holdings": [
            {
                "ticker": "LHM",
                "allocation_pct": 12.0,
                "unrealized_pl_mad": 0.0,
                "unrealized_pl_pct": 0.0,
                "market_value_mad": 12_000.0,
                "price_status": "live",
                "avg_daily_traded_value_mad": 2_000_000.0,
                "volatility_30d": 0.10,
            }
        ],
    }

    alerts = risk_service.build_portfolio_risk_alerts(portfolio, pnl, lambda _ticker: sell_signal)

    assert alerts[0]["alert_type"] == "signal_conflict"
    assert alerts[0]["severity"] == "high"
    assert "SELL/AVOID" in alerts[0]["detail"]
