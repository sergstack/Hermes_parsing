"""Entry point for Herm Finance monthly report export."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date

from .auth import ensure_logged_in, save_session_state
from .browser import close_browser_session
from .config import read_config
from .dates import MonthPeriod, build_months_range, build_months_range_until_year_end
from .downloaders import download_report_for_month
from .logging_utils import setup_logging
from .paths import resolve_project_path
from .reports import REPORT_DEFINITIONS

logger = logging.getLogger(__name__)


@dataclass
class RunSummary:
    success_count: int = 0
    error_count: int = 0
    failed_reports: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.failed_reports is None:
            self.failed_reports = []


def build_cons_budget_period(today: date | None = None) -> MonthPeriod:
    today = today or date.today()
    return MonthPeriod(date(today.year - 1, 1, 1), date(today.year, 12, 31))


def main() -> int:
    config = read_config().resolved()
    setup_logging(resolve_project_path("logs"))

    summary = RunSummary()
    session = ensure_logged_in(config)
    periods = build_months_range(config.start_date)
    # budget_rows covers planned (future) payments — extend to December of the current year.
    budget_rows_periods = build_months_range_until_year_end(config.start_date)

    try:
        for report_code in REPORT_DEFINITIONS:
            if report_code == "budget_rows":
                active_periods = budget_rows_periods
            elif report_code == "cons_budget":
                active_periods = [build_cons_budget_period()]
            else:
                active_periods = periods
            for period in active_periods:
                if report_code == "contractors" and not config.repeat_each_month and period != active_periods[0]:
                    continue
                result = download_report_for_month(session, config, report_code, period)
                if result.success:
                    summary.success_count += 1
                else:
                    summary.error_count += 1
                    summary.failed_reports.append(f"{report_code}:{period.label}")
        logger.info(
            "summary | success=%s | error=%s | failed=%s",
            summary.success_count,
            summary.error_count,
            ", ".join(summary.failed_reports) if summary.failed_reports else "none",
        )
        save_session_state(session, config.session_file)
        return 0 if summary.error_count == 0 else 1
    finally:
        close_browser_session(session)


if __name__ == "__main__":
    raise SystemExit(main())
