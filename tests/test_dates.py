from datetime import date

from app.dates import (
    build_months_range,
    build_months_range_until_year_end,
    month_bounds,
)


def test_month_bounds_handles_year_end():
    bounds = month_bounds(date(2026, 12, 15))
    assert bounds.start.isoformat() == "2026-12-01"
    assert bounds.end.isoformat() == "2026-12-31"


def test_build_months_range_handles_year_boundary():
    periods = build_months_range("2025-11-01", today=date(2026, 2, 10))
    assert [p.label for p in periods] == ["2025-11", "2025-12", "2026-01"]


def test_build_months_range_until_year_end_includes_current_year_tail():
    periods = build_months_range_until_year_end("2026-11-01", today=date(2026, 11, 10))
    assert [p.label for p in periods] == ["2026-11", "2026-12"]
