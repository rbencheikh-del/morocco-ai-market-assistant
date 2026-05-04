import csv
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from io import StringIO
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.db.models import DailyOHLCVPrice, MarketDataImportLog, Security

REQUIRED_COLUMNS = ("symbol", "date", "open", "high", "low", "close", "volume")
STALE_PRICE_DAYS = 7
LARGE_MOVE_THRESHOLD = 0.15


@dataclass
class RowIssue:
    row_number: int
    symbol: str | None
    price_date: str | None
    reason: str


@dataclass
class CleanPriceRow:
    security_id: object
    ticker: str
    price_date: date
    open_mad: float
    high_mad: float
    low_mad: float
    close_mad: float
    volume: float
    adjusted_close_mad: float | None = None
    traded_value_mad: float | None = None
    market_cap_mad: float | None = None


@dataclass
class ImportResult:
    status: str
    rows_received: int = 0
    rows_inserted: int = 0
    rows_rejected: int = 0
    rows_duplicate: int = 0
    warnings: list[RowIssue] = field(default_factory=list)
    rejected_rows: list[RowIssue] = field(default_factory=list)
    batch_id: UUID = field(default_factory=uuid4)

    def as_dict(self) -> dict:
        return {
            "status": self.status,
            "batch_id": str(self.batch_id),
            "rows_received": self.rows_received,
            "rows_inserted": self.rows_inserted,
            "rows_rejected": self.rows_rejected,
            "rows_duplicate": self.rows_duplicate,
            "warning_count": len(self.warnings),
            "warnings": [issue.__dict__ for issue in self.warnings],
            "rejected_rows": [issue.__dict__ for issue in self.rejected_rows],
        }


def _parse_float(value: str | None, field_name: str) -> float:
    if value is None or str(value).strip() == "":
        raise ValueError(f"missing {field_name}")
    return float(str(value).replace(",", "").strip())


def _parse_optional_float(value: str | None) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    return float(str(value).replace(",", "").strip())


def _validate_row(
    raw: dict,
    row_number: int,
    securities_by_symbol: dict[str, Security],
    seen_in_file: set[tuple[str, date]],
) -> tuple[CleanPriceRow | None, list[RowIssue], RowIssue | None]:
    symbol = (raw.get("symbol") or raw.get("ticker") or "").strip().upper()
    price_date_text = (raw.get("date") or raw.get("price_date") or "").strip()
    warnings: list[RowIssue] = []

    if not symbol:
        return None, warnings, RowIssue(row_number, None, price_date_text, "missing symbol")
    security = securities_by_symbol.get(symbol)
    if not security:
        return None, warnings, RowIssue(row_number, symbol, price_date_text, "unknown symbol")
    try:
        price_date = date.fromisoformat(price_date_text)
    except ValueError:
        return None, warnings, RowIssue(row_number, symbol, price_date_text, "invalid date")

    if (symbol, price_date) in seen_in_file:
        return None, warnings, RowIssue(row_number, symbol, price_date_text, "duplicate date in CSV")
    seen_in_file.add((symbol, price_date))

    try:
        open_mad = _parse_float(raw.get("open"), "open")
        high_mad = _parse_float(raw.get("high"), "high")
        low_mad = _parse_float(raw.get("low"), "low")
        close_mad = _parse_float(raw.get("close"), "close")
        volume = _parse_float(raw.get("volume"), "volume")
    except ValueError as exc:
        return None, warnings, RowIssue(row_number, symbol, price_date_text, str(exc))

    prices = [open_mad, high_mad, low_mad, close_mad]
    if any(price < 0 for price in prices):
        return None, warnings, RowIssue(row_number, symbol, price_date_text, "negative prices are not allowed")
    if high_mad < low_mad or high_mad < max(open_mad, close_mad) or low_mad > min(open_mad, close_mad):
        return None, warnings, RowIssue(row_number, symbol, price_date_text, "OHLC values are inconsistent")
    if volume < 0:
        return None, warnings, RowIssue(row_number, symbol, price_date_text, "negative volume is not allowed")
    if volume == 0:
        warnings.append(RowIssue(row_number, symbol, price_date_text, "zero volume"))

    return (
        CleanPriceRow(
            security_id=security.id,
            ticker=symbol,
            price_date=price_date,
            open_mad=open_mad,
            high_mad=high_mad,
            low_mad=low_mad,
            close_mad=close_mad,
            volume=volume,
            adjusted_close_mad=_parse_optional_float(raw.get("adjusted_close") or raw.get("adjusted_close_mad")),
            traded_value_mad=_parse_optional_float(raw.get("traded_value") or raw.get("traded_value_mad")),
            market_cap_mad=_parse_optional_float(raw.get("market_cap") or raw.get("market_cap_mad")),
        ),
        warnings,
        None,
    )


def validate_csv_prices(csv_text: str, securities: list[Security]) -> tuple[list[CleanPriceRow], ImportResult]:
    reader = csv.DictReader(StringIO(csv_text.strip()))
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
    result = ImportResult(status="failed")
    if missing_columns:
        result.rejected_rows.append(RowIssue(0, None, None, f"missing required columns: {', '.join(missing_columns)}"))
        result.rows_rejected = 1
        return [], result

    securities_by_symbol = {security.ticker.upper(): security for security in securities}
    clean_rows: list[CleanPriceRow] = []
    seen_in_file: set[tuple[str, date]] = set()

    for row_number, raw in enumerate(reader, start=2):
        result.rows_received += 1
        clean, warnings, rejection = _validate_row(raw, row_number, securities_by_symbol, seen_in_file)
        result.warnings.extend(warnings)
        if rejection:
            result.rejected_rows.append(rejection)
            result.rows_rejected += 1
            continue
        if clean:
            clean_rows.append(clean)

    result.status = "success" if clean_rows and not result.rejected_rows else "partial_success" if clean_rows else "failed"
    return clean_rows, result


def _existing_price(db: Session, ticker: str, price_date: date) -> DailyOHLCVPrice | None:
    return (
        db.query(DailyOHLCVPrice)
        .filter(DailyOHLCVPrice.ticker == ticker, DailyOHLCVPrice.price_date == price_date)
        .first()
    )


def _write_import_log(db: Session, result: ImportResult, source_name: str, error_message: str | None = None) -> None:
    log = MarketDataImportLog(
        source_name=source_name,
        status=result.status,
        rows_received=result.rows_received,
        rows_inserted=result.rows_inserted,
        rows_rejected=result.rows_rejected,
        rows_duplicate=result.rows_duplicate,
        warning_count=len(result.warnings),
        error_message=error_message,
        import_summary=result.as_dict(),
        completed_at=datetime.now(UTC),
    )
    db.add(log)


def import_prices_from_csv(db: Session, csv_text: str, source_name: str = "csv_upload") -> dict:
    securities = db.query(Security).filter(Security.is_active.is_(True)).all()
    clean_rows, result = validate_csv_prices(csv_text, securities)

    for clean in clean_rows:
        if _existing_price(db, clean.ticker, clean.price_date):
            result.rows_duplicate += 1
            continue
        db.add(
            DailyOHLCVPrice(
                security_id=clean.security_id,
                ticker=clean.ticker,
                price_date=clean.price_date,
                open_mad=clean.open_mad,
                high_mad=clean.high_mad,
                low_mad=clean.low_mad,
                close_mad=clean.close_mad,
                adjusted_close_mad=clean.adjusted_close_mad,
                volume=clean.volume,
                traded_value_mad=clean.traded_value_mad,
                market_cap_mad=clean.market_cap_mad,
                data_source=source_name,
                ingestion_batch_id=result.batch_id,
            )
        )
        result.rows_inserted += 1

    if result.rows_inserted == 0 and (result.rows_rejected or result.rows_duplicate):
        result.status = "failed" if result.rows_rejected and not result.rows_duplicate else "partial_success"
    elif result.rows_rejected or result.rows_duplicate or result.warnings:
        result.status = "partial_success"
    else:
        result.status = "success"

    _write_import_log(db, result, source_name)
    db.commit()
    return result.as_dict()


def latest_import_status(db: Session) -> dict:
    latest = db.query(MarketDataImportLog).order_by(MarketDataImportLog.started_at.desc()).first()
    if not latest:
        return {"status": "not_started", "message": "No import has been run yet."}
    return {
        "id": latest.id,
        "source_name": latest.source_name,
        "status": latest.status,
        "rows_received": latest.rows_received,
        "rows_inserted": latest.rows_inserted,
        "rows_rejected": latest.rows_rejected,
        "rows_duplicate": latest.rows_duplicate,
        "warning_count": latest.warning_count,
        "error_message": latest.error_message,
        "started_at": latest.started_at,
        "completed_at": latest.completed_at,
    }


def build_data_quality_report_from_rows(prices: list[DailyOHLCVPrice], as_of: date | None = None) -> dict:
    as_of = as_of or date.today()
    issues: list[dict] = []
    rows_by_ticker: dict[str, list[DailyOHLCVPrice]] = defaultdict(list)
    duplicate_counter = Counter((row.ticker, row.price_date) for row in prices)

    for row in prices:
        rows_by_ticker[row.ticker].append(row)
        if row.close_mad is None:
            issues.append({"symbol": row.ticker, "date": row.price_date, "issue_type": "missing_close_price"})
        if any(float(value) < 0 for value in [row.open_mad, row.high_mad, row.low_mad, row.close_mad] if value is not None):
            issues.append({"symbol": row.ticker, "date": row.price_date, "issue_type": "negative_prices"})
        if float(row.volume) == 0:
            issues.append({"symbol": row.ticker, "date": row.price_date, "issue_type": "zero_volume"})

    for (ticker, price_date), count in duplicate_counter.items():
        if count > 1:
            issues.append({"symbol": ticker, "date": price_date, "issue_type": "duplicate_date", "count": count})

    for ticker, rows in rows_by_ticker.items():
        ordered = sorted(rows, key=lambda row: row.price_date)
        latest = ordered[-1]
        stale_days = (as_of - latest.price_date).days
        if stale_days > STALE_PRICE_DAYS:
            issues.append({"symbol": ticker, "date": latest.price_date, "issue_type": "stale_prices", "stale_days": stale_days})
        for previous, current in zip(ordered, ordered[1:]):
            previous_close = float(previous.close_mad or 0)
            current_close = float(current.close_mad or 0)
            if previous_close and abs(current_close - previous_close) / previous_close > LARGE_MOVE_THRESHOLD:
                issues.append(
                    {
                        "symbol": ticker,
                        "date": current.price_date,
                        "issue_type": "large_unexplained_price_move",
                        "move_pct": round(((current_close - previous_close) / previous_close) * 100, 2),
                    }
                )

    return {
        "as_of": as_of,
        "rows_checked": len(prices),
        "issue_count": len(issues),
        "issues": issues,
        "rules": {
            "stale_price_days": STALE_PRICE_DAYS,
            "large_move_threshold_pct": LARGE_MOVE_THRESHOLD * 100,
        },
    }


def data_quality_report(db: Session) -> dict:
    prices = db.query(DailyOHLCVPrice).all()
    report = build_data_quality_report_from_rows(prices)
    latest = db.query(MarketDataImportLog).order_by(MarketDataImportLog.started_at.desc()).first()
    if latest:
        rejected = latest.import_summary.get("rejected_rows", []) if latest.import_summary else []
        report["latest_import_rejections"] = rejected
    return report


def run_daily_refresh(db: Session) -> dict:
    result = ImportResult(status="success")
    result.warnings.append(RowIssue(0, None, None, "scheduled refresh structure is configured; no external data provider is connected"))
    result.status = "partial_success"
    _write_import_log(db, result, "scheduled_daily_refresh")
    db.commit()
    return {
        "status": result.status,
        "message": "Daily refresh job structure ran. Connect a provider adapter to import live CSE data.",
        "warning_count": len(result.warnings),
    }
