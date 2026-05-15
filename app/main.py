"""Entry point for Herm Finance monthly report export."""

from __future__ import annotations

import logging

from .auth import ensure_logged_in, save_session_state
from .browser import close_browser_session
from .config import read_config
from .dates import build_months_range, build_months_range_until_year_end
from .downloaders import download_report_for_month
from .logging_utils import setup_logging
from .orchestration import build_cons_budget_period, periods_for_report
from .paths import resolve_project_path
from .reports import REPORT_DEFINITIONS
from .run_summary import RunSummary

logger = logging.getLogger(__name__)


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
            active_periods = periods_for_report(report_code, periods, budget_rows_periods)
            for period in active_periods:
                if report_code == "contractors" and not config.repeat_each_month and period != active_periods[0]:
                    continue
                result = download_report_for_month(session, config, report_code, period)
                summary.record_result(report_code, period, result)
        logger.info(
            "summary | success=%s | error=%s | failed=%s",
            summary.success_count,
            summary.error_count,
            summary.failed_label,
        )
        save_session_state(session, config.session_file)
        return summary.exit_code()
    finally:
        close_browser_session(session)


if __name__ == "__main__":
    raise SystemExit(main())
