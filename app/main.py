"""Entry point for Herm Finance monthly report export."""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass, replace
from pathlib import Path

from .auth import ensure_logged_in, save_session_state
from .browser import close_browser_session
from .config import normalize_config, read_config
from .dates import build_months_range, build_months_range_until_year_end
from .downloaders import download_report_for_month
from .logging_utils import setup_logging
from .paths import build_output_path
from .reports import REPORT_DEFINITIONS

logger = logging.getLogger(__name__)


@dataclass
class RunSummary:
    success_count: int = 0
    error_count: int = 0
    failed_reports: list[str] = None  # type: ignore[assignment]
    planned_reports: list[dict] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.failed_reports is None:
            self.failed_reports = []
        if self.planned_reports is None:
            self.planned_reports = []


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Herm Finance monthly report exporter")
    parser.add_argument("--config", default="config/config.txt")
    parser.add_argument("--reports", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--headless", choices=["true", "false"], default=None)
    parser.add_argument("--overwrite", choices=["true", "false"], default=None)
    return parser.parse_args()


def _selected_reports(raw: str) -> list[str]:
    if not raw:
        return list(REPORT_DEFINITIONS.keys())
    selected = [item.strip() for item in raw.split(",") if item.strip()]
    unknown = [item for item in selected if item not in REPORT_DEFINITIONS]
    if unknown:
        raise ValueError(f"Unknown report codes: {', '.join(unknown)}")
    return selected


def _apply_overrides(config, args: argparse.Namespace):
    if args.headless is not None:
        config = replace(config, headless=args.headless == "true")
    if args.overwrite is not None:
        config = replace(config, overwrite=args.overwrite == "true")
    return config


def _build_planned_reports(config, report_codes: list[str]) -> list[dict]:
    periods = build_months_range(config.start_date)
    budget_rows_periods = build_months_range_until_year_end(config.start_date)
    planned: list[dict] = []
    for report_code in report_codes:
        active_periods = (
            budget_rows_periods if report_code == "budget_rows" else periods
        )
        report = REPORT_DEFINITIONS[report_code]
        for period in active_periods:
            if report_code == "contractors" and not config.repeat_each_month:
                if period != active_periods[0]:
                    continue
            planned.append(
                {
                    "report_code": report_code,
                    "period": period.label,
                    "url": report.build_url(config.base_url.rstrip("/"), period),
                    "output_path": str(
                        build_output_path(
                            config.download_dir,
                            report.export_dir,
                            period,
                            ".xlsx",
                            report.file_prefix,
                            use_end_date=report_code == "account_balances",
                        )
                    ),
                }
            )
    return planned


def _write_summary(log_dir: Path, summary: RunSummary) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    summary_path = log_dir / "summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "success_count": summary.success_count,
                "error_count": summary.error_count,
                "failed_reports": summary.failed_reports,
                "planned_reports": summary.planned_reports,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return summary_path


def _run_dry_run(config, report_codes: list[str]) -> int:
    summary = RunSummary()
    summary.planned_reports = _build_planned_reports(config, report_codes)
    for item in summary.planned_reports:
        logger.info(
            "dry-run | %s | %s | %s",
            item["report_code"],
            item["period"],
            item["output_path"],
        )
    _write_summary(Path("logs"), summary)
    return 0


def main() -> int:
    args = _parse_args()
    config = normalize_config(read_config(args.config), Path.cwd())
    config = _apply_overrides(config, args)
    setup_logging(Path("logs"))
    report_codes = _selected_reports(args.reports)

    if args.dry_run:
        return _run_dry_run(config, report_codes)

    summary = RunSummary()
    session = ensure_logged_in(config)
    periods = build_months_range(config.start_date)
    budget_rows_periods = build_months_range_until_year_end(config.start_date)

    try:
        for report_code in report_codes:
            active_periods = (
                budget_rows_periods if report_code == "budget_rows" else periods
            )
            for period in active_periods:
                if (
                    report_code == "contractors"
                    and not config.repeat_each_month
                    and period != active_periods[0]
                ):
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
        _write_summary(Path("logs"), summary)
        save_session_state(session, config.session_file)
        return 0 if summary.error_count == 0 else 1
    finally:
        close_browser_session(session)


if __name__ == "__main__":
    raise SystemExit(main())
