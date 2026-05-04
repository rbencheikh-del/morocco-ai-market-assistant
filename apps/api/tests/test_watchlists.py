from types import SimpleNamespace
from uuid import uuid4

from app.services import risk as risk_service
from app.services import watchlists as watchlist_service
from app.services.watchlists import build_watchlist_trigger_alerts, build_watchlist_user_alerts


def item(ticker="ATW", above=None, below=None):
    return SimpleNamespace(
        id=uuid4(),
        ticker=ticker,
        user_note=None,
        alert_above_mad=above,
        alert_below_mad=below,
    )


def snapshot(price):
    return SimpleNamespace(price_mad=price)


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, *_args, **_kwargs):
        return self

    def order_by(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.rows[0] if self.rows else None

    def all(self):
        return self.rows


class FakeDb:
    def __init__(self):
        self.user = SimpleNamespace(id=uuid4(), created_at=None)
        self.security = SimpleNamespace(ticker="ATW", is_active=True)
        self.watchlist = SimpleNamespace(id=uuid4(), user_id=self.user.id, name="Core", description=None, is_default=False, items=[])
        self.item = SimpleNamespace(id=uuid4(), watchlist_id=self.watchlist.id, ticker="ATW")
        self.alert = SimpleNamespace(id=uuid4(), is_read=False)
        self.added = []
        self.deleted = []
        self.committed = False

    def query(self, model):
        name = model.__name__
        if name == "User":
            return FakeQuery([self.user])
        if name == "Security":
            return FakeQuery([self.security])
        if name == "Watchlist":
            return FakeQuery([self.watchlist])
        if name == "WatchlistItem":
            return FakeQuery([self.item])
        if name == "RiskAlert":
            return FakeQuery([self.alert])
        return FakeQuery([])

    def add(self, row):
        self.added.append(row)

    def delete(self, row):
        self.deleted.append(row)

    def commit(self):
        self.committed = True

    def refresh(self, row):
        if getattr(row, "id", None) is None:
            row.id = uuid4()


def test_watchlist_price_above_threshold_generates_user_alert():
    watchlist = SimpleNamespace(id=uuid4(), user_id=uuid4())

    alerts = build_watchlist_user_alerts(
        watchlist,
        [item("ATW", above=480)],
        lambda _ticker: snapshot(482),
        lambda _ticker: None,
    )

    assert alerts[0]["alert_type"] == "price_above_threshold"
    assert alerts[0]["severity"] == "Medium"
    assert alerts[0]["symbol"] == "ATW"
    assert "not a trade instruction" in alerts[0]["recommended_action"]


def test_watchlist_price_below_threshold_generates_user_alert():
    watchlist = SimpleNamespace(id=uuid4(), user_id=uuid4())

    alerts = build_watchlist_user_alerts(
        watchlist,
        [item("IAM", below=90)],
        lambda _ticker: snapshot(88),
        lambda _ticker: None,
    )

    assert alerts[0]["alert_type"] == "price_below_threshold"
    assert alerts[0]["severity"] == "Medium"
    assert alerts[0]["symbol"] == "IAM"


def test_watchlist_missing_market_price_generates_data_quality_alert():
    watchlist = SimpleNamespace(id=uuid4(), user_id=uuid4())

    alerts = build_watchlist_user_alerts(
        watchlist,
        [item("LHM", above=1800)],
        lambda _ticker: None,
        lambda _ticker: None,
    )

    assert alerts[0]["alert_type"] == "missing_market_price"
    assert alerts[0]["severity"] == "Medium"
    assert alerts[0]["current_price_mad"] is None


def test_watchlist_sell_signal_generates_high_alert():
    watchlist = SimpleNamespace(id=uuid4(), user_id=uuid4())
    sell_signal = SimpleNamespace(signal="SELL", confidence=76)

    alerts = build_watchlist_user_alerts(
        watchlist,
        [item("MNG")],
        lambda _ticker: snapshot(1820),
        lambda _ticker: sell_signal,
    )

    assert alerts[0]["alert_type"] == "signal_watch"
    assert alerts[0]["severity"] == "High"
    assert "SELL/AVOID" in alerts[0]["message"]


def test_watchlist_creation():
    db = FakeDb()

    created = watchlist_service.create_watchlist(db, name="Banks", description="Banking names")

    assert created.name == "Banks"
    assert created.description == "Banking names"
    assert db.committed is True


def test_adding_and_removing_watchlist_stock():
    db = FakeDb()

    updated = watchlist_service.add_watchlist_item(db, db.watchlist.id, "ATW", user_note="Core bank")
    deleted = watchlist_service.remove_watchlist_stock(db, db.watchlist.id, "ATW")

    assert updated is db.watchlist
    assert deleted is True
    assert db.deleted == [db.item]


def test_signal_change_and_price_move_alert_triggers_are_explainable():
    watchlist = SimpleNamespace(id=uuid4(), user_id=uuid4())
    signals = [SimpleNamespace(signal="BUY"), SimpleNamespace(signal="HOLD")]
    prices = [SimpleNamespace(close_mad=106), SimpleNamespace(close_mad=100)]
    rankings = [SimpleNamespace(ai_score=78, risk_score=42, liquidity_score=70)]

    alerts = build_watchlist_trigger_alerts(
        watchlist,
        [item("ATW")],
        lambda _ticker: signals,
        lambda _ticker: prices,
        lambda _ticker: rankings,
        lambda _ticker: snapshot(106),
    )
    alert_types = {alert["alert_type"] for alert in alerts}

    assert "signal_change" in alert_types
    assert "daily_price_move" in alert_types
    assert all("trade instruction" in alert["recommended_action"] or "Review" in alert["recommended_action"] for alert in alerts)


def test_unread_and_mark_read_logic():
    db = FakeDb()

    unread = risk_service.list_unread_alerts(db)
    read = risk_service.mark_alert_read(db, db.alert.id)

    assert unread == [db.alert]
    assert read.is_read is True
    assert db.committed is True
