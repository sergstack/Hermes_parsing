"""Autonomous download CLI — assumes a valid session already exists.

Exit codes:
  0  all reports downloaded successfully
  1  one or more downloads failed
  2  session invalid / unexpected error

Usage:
  python -m app.cmd_download [--config PATH]

Intended to be called by Kestra (or any orchestrator) after cmd_auth has
already refreshed / validated the session.
"""

from __future__ import annotations

import argparse
import logging
import sys

from .auth import ensure_logged_in, save_session_state
from .browser import close_browser_session
from .config import read_config
from .dates import build_months_range, build_months_range_until_year_end
from .downloaders import download_report_for_month
from .logging_utils import setup_logging
from .orchestration import periods_for_report
from .paths import resolve_project_path
from .reports import REPORT_DEFINITIONS
from .run_summary import RunSummary

logger = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Download monthly reports from herm.finance")
    p.add_argument("--config", default="config/config.txt", help="Path to config file")
    return p.parse_args()


def download_main(config_path: str = "config/config.txt") -> int:
    """Return 0 on full success, 1 on partial failure, 2 on fatal error."""
    setup_logging(resolve_project_path("logs"))
    try:
        config = read_config(config_path).resolved()
        summary = RunSummary()
        session = ensure_logged_in(config)
        periods = build_months_range(config.start_date)
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

    except Exception as exc:
        logger.exception("cmd_download | fatal error: %s", exc)
        return 2


def main() -> None:
    args = _parse_args()
    sys.exit(download_main(config_path=args.config))


if __name__ == "__main__":
    main()
