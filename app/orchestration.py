"""Pure orchestration helpers for report period selection."""

from __future__ import annotations

from datetime import date

from .dates import MonthPeriod


def build_cons_budget_period(start: date, today: date | None = None) -> MonthPeriod:
    today = today or date.today()
    return MonthPeriod(start, date(today.year, 12, 31))


def periods_for_report(
    report_code: str,
    periods: list[MonthPeriod],
    budget_rows_periods: list[MonthPeriod],
    today: date | None = None,
) -> list[MonthPeriod]:
    if report_code == "budget_rows":
        return budget_rows_periods
    if report_code == "cons_budget":
        return [build_cons_budget_period(periods[0].start, today)]
    return periods
