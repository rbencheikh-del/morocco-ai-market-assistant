from types import SimpleNamespace
from uuid import uuid4

from app.services.watchlists import build_watchlist_user_alerts


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
