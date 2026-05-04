from datetime import date
from types import SimpleNamespace
from uuid import uuid4

from app.db.models import DailyOHLCVPrice
from app.services import market_ingestion


def security(ticker="ATW"):
    return SimpleNamespace(id=uuid4(), ticker=ticker, is_active=True)


def price_row(ticker="ATW", price_date=date(2026, 5, 1), close=100, volume=10_000):
    return SimpleNamespace(
        ticker=ticker,
        price_date=price_date,
        open_mad=close,
        high_mad=close + 2,
        low_mad=close - 2,
        close_mad=close,
        volume=volume,
    )


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, *_args, **_kwargs):
        return self

    def order_by(self, *_args, **_kwargs):
        return self

    def all(self):
        return self.rows

    def first(self):
        return self.rows[0] if self.rows else None


class FakeDb:
    def __init__(self, securities=None, prices=None):
        self.securities = securities or [security()]
        self.prices = prices or []
        self.added = []
        self.committed = False

    def query(self, model):
        if model.__name__ == "Security":
            return FakeQuery(self.securities)
        if model.__name__ == "DailyOHLCVPrice":
            return FakeQuery(self.prices)
        return FakeQuery([])

    def add(self, row):
        self.added.append(row)

    def commit(self):
        self.committed = True


def test_valid_csv_import_inserts_clean_daily_prices():
    csv_text = """symbol,date,open,high,low,close,volume
ATW,2026-05-01,100,104,99,103,12000
"""
    db = FakeDb()

    result = market_ingestion.import_prices_from_csv(db, csv_text)

    inserted_prices = [row for row in db.added if isinstance(row, DailyOHLCVPrice)]
    assert result["status"] == "success"
    assert result["rows_inserted"] == 1
    assert result["rows_rejected"] == 0
    assert inserted_prices[0].ticker == "ATW"
    assert db.committed is True


def test_invalid_rows_are_rejected_safely():
    csv_text = """symbol,date,open,high,low,close,volume
ATW,2026-05-01,-100,104,99,103,12000
XXX,2026-05-02,100,104,99,103,12000
"""

    clean_rows, result = market_ingestion.validate_csv_prices(csv_text, [security()])

    assert clean_rows == []
    assert result.status == "failed"
    assert result.rows_rejected == 2
    assert "negative prices" in result.rejected_rows[0].reason
    assert result.rejected_rows[1].reason == "unknown symbol"


def test_duplicate_price_records_are_not_inserted(monkeypatch):
    csv_text = """symbol,date,open,high,low,close,volume
ATW,2026-05-01,100,104,99,103,12000
"""
    db = FakeDb()
    monkeypatch.setattr(market_ingestion, "_existing_price", lambda *_args: object())

    result = market_ingestion.import_prices_from_csv(db, csv_text)

    inserted_prices = [row for row in db.added if isinstance(row, DailyOHLCVPrice)]
    assert result["rows_inserted"] == 0
    assert result["rows_duplicate"] == 1
    assert inserted_prices == []


def test_stale_price_detection():
    report = market_ingestion.build_data_quality_report_from_rows(
        [price_row(price_date=date(2026, 4, 1))],
        as_of=date(2026, 5, 4),
    )

    assert any(issue["issue_type"] == "stale_prices" for issue in report["issues"])


def test_missing_close_data_is_rejected_and_reported():
    csv_text = """symbol,date,open,high,low,close,volume
ATW,2026-05-01,100,104,99,,12000
"""

    clean_rows, result = market_ingestion.validate_csv_prices(csv_text, [security()])

    assert clean_rows == []
    assert result.rows_rejected == 1
    assert result.rejected_rows[0].reason == "missing close"


def test_zero_volume_duplicate_dates_and_large_moves_are_flagged():
    report = market_ingestion.build_data_quality_report_from_rows(
        [
            price_row(price_date=date(2026, 5, 1), close=100, volume=0),
            price_row(price_date=date(2026, 5, 1), close=100, volume=10_000),
            price_row(price_date=date(2026, 5, 2), close=130, volume=10_000),
        ],
        as_of=date(2026, 5, 4),
    )
    issue_types = {issue["issue_type"] for issue in report["issues"]}

    assert "zero_volume" in issue_types
    assert "duplicate_date" in issue_types
    assert "large_unexplained_price_move" in issue_types
