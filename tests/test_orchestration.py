from datetime import date
from dataclasses import dataclass

from app.dates import MonthPeriod
from app.main import build_cons_budget_period
from app.orchestration import periods_for_report
from app.run_summary import RunSummary


@dataclass(frozen=True)
class ResultStub:
    success: bool


def test_run_summary_initializes_failed_reports_list():
    summary = RunSummary()

    assert summary.success_count == 0
    assert summary.error_count == 0
    assert summary.failed_reports == []


def test_run_summary_records_success_and_failure_results():
    period = MonthPeriod(date(2026, 3, 1), date(2026, 3, 31))
    summary = RunSummary()

    summary.record_result("dds", period, ResultStub(success=True))
    summary.record_result("budget_rows", period, ResultStub(success=False))

    assert summary.success_count == 1
    assert summary.error_count == 1
    assert summary.failed_reports == ["budget_rows:2026-03"]
    assert summary.failed_label == "budget_rows:2026-03"
    assert summary.has_errors is True
    assert summary.exit_code() == 1


def test_periods_for_regular_report_uses_completed_month_periods():
    periods = [MonthPeriod(date(2026, 1, 1), date(2026, 1, 31))]
    budget_rows_periods = [MonthPeriod(date(2026, 12, 1), date(2026, 12, 31))]

    assert periods_for_report("dds", periods, budget_rows_periods) == periods


def test_periods_for_budget_rows_uses_extended_periods():
    periods = [MonthPeriod(date(2026, 1, 1), date(2026, 1, 31))]
    budget_rows_periods = [MonthPeriod(date(2026, 12, 1), date(2026, 12, 31))]

    assert periods_for_report("budget_rows", periods, budget_rows_periods) == budget_rows_periods


def test_periods_for_cons_budget_uses_previous_and_current_year():
    periods = [MonthPeriod(date(2026, 1, 1), date(2026, 1, 31))]
    budget_rows_periods = [MonthPeriod(date(2026, 12, 1), date(2026, 12, 31))]

    selected = periods_for_report("cons_budget", periods, budget_rows_periods, today=date(2026, 5, 15))

    assert selected == [MonthPeriod(date(2025, 1, 1), date(2026, 12, 31))]
    assert build_cons_budget_period(today=date(2026, 5, 15)) == selected[0]
