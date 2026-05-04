"""Date helpers for month-based report iteration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta


@dataclass(frozen=True)
class MonthPeriod:
    """A monthly period identified by its first and last calendar day."""

    start: date
    end: date

    @property
    def label(self) -> str:
        return self.start.strftime("%Y-%m")


def month_bounds(any_date: date) -> MonthPeriod:
    """Return the first and last day of the month containing any_date."""
    start = any_date.replace(day=1)
    if start.month == 12:
        next_month = start.replace(year=start.year + 1, month=1, day=1)
    else:
        next_month = start.replace(month=start.month + 1, day=1)
    end = next_month - timedelta(days=1)
    return MonthPeriod(start=start, end=end)


def build_months_range_until_year_end(start_date: str, today: date | None = None) -> list[MonthPeriod]:
    """Build inclusive month periods from start_date to December of the current year.

    Used for budget rows, which contain planned (future) payments — so we need
    months beyond the last completed month, up to the end of the current calendar year.
    """
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    current = today or date.today()
    year_end = month_bounds(date(current.year, 12, 1))

    cursor = start.replace(day=1)
    periods: list[MonthPeriod] = []
    while cursor <= year_end.start:
        periods.append(month_bounds(cursor))
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year + 1, month=1, day=1)
        else:
            cursor = cursor.replace(month=cursor.month + 1, day=1)
    return periods


def build_months_range(start_date: str, today: date | None = None) -> list[MonthPeriod]:
    """Build inclusive month periods from start_date to the last completed month."""
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    current = today or date.today()
    last_completed_month = month_bounds(current.replace(day=1) - timedelta(days=1))

    cursor = start.replace(day=1)
    periods: list[MonthPeriod] = []
    while cursor <= last_completed_month.start:
        periods.append(month_bounds(cursor))
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year + 1, month=1, day=1)
        else:
            cursor = cursor.replace(month=cursor.month + 1, day=1)
    return periods

