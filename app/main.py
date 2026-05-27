"""Entry point for Herm Finance monthly report export."""

from __future__ import annotations

import argparse
import json
import logging
import time
from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from .auth import ensure_logged_in, save_session_state
from .browser import close_browser_session
from .config import normalize_config, read_config
from .dates import MonthPeriod, build_months_range, build_months_range_until_year_end
from .downloaders import download_report_for_month
from .failure_artifacts import write_failure_artifacts
from .logging_utils import setup_logging
from .metrics import AttemptTiming, RunMetrics, StageTiming, write_run_metrics
from .paths import build_output_path
from .reports import REPORT_DEFINITIONS

logger = logging.getLogger(__name__)


@dataclass
class RunSummary:
    success_count: int = 0
    error_count: int = 0
    failed_reports: list[str] = field(default_factory=list)
    planned_reports: list[dict] = field(default_factory=list)


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


def _cons_budget_periods(today: date | None = None) -> list[MonthPeriod]:
    current = today or date.today()
    last_completed_month_end = current.replace(day=1) - timedelta(days=1)
    return [
        MonthPeriod(start=date(2025, 1, 1), end=last_completed_month_end),
    ]


def _periods_for_report(report_code: str, start_date: str, today: date | None = None):
    if report_code == "budget_rows":
        return build_months_range_until_year_end(start_date)
    if report_code == "cons_budget":
        return _cons_budget_periods(today)
    return build_months_range(start_date)


def _build_planned_reports(config, report_codes: list[str]) -> list[dict]:
    planned: list[dict] = []
    for report_code in report_codes:
        active_periods = _periods_for_report(report_code, config.start_date)
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
                            use_end_date=report_code
                            in {
                                "account_balances",
                                "cons_budget",
                            },
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


def _new_run_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _planned_reports_to_metrics(run_id: str, planned_reports: list[dict]) -> RunMetrics:
    return RunMetrics(
        run_id=run_id,
        status="planned",
        dry_run=True,
        attempts=[
            AttemptTiming(
                report_code=item["report_code"],
                period=item["period"],
                attempt=0,
                status="planned",
                output_path=item["output_path"],
            )
            for item in planned_reports
        ],
    )


def _result_file_size(output_path: Path | None) -> int | None:
    if output_path and output_path.exists():
        return output_path.stat().st_size
    return None


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
    log_dir = Path("logs")
    _write_summary(log_dir, summary)
    write_run_metrics(
        log_dir, _planned_reports_to_metrics(_new_run_id(), summary.planned_reports)
    )
    return 0


def main() -> int:
    args = _parse_args()
    config = normalize_config(read_config(args.config))
    config = _apply_overrides(config, args)
    setup_logging(Path("logs"))
    report_codes = _selected_reports(args.reports)

    if args.dry_run:
        return _run_dry_run(config, report_codes)

    summary = RunSummary()
    metrics_attempts: list[AttemptTiming] = []
    run_id = _new_run_id()
    session = ensure_logged_in(config)

    try:
        for report_code in report_codes:
            active_periods = _periods_for_report(report_code, config.start_date)
            for period in active_periods:
                if (
                    report_code == "contractors"
                    and not config.repeat_each_month
                    and period != active_periods[0]
                ):
                    continue
                started = time.perf_counter()
                result = download_report_for_month(session, config, report_code, period)
                duration_sec = round(time.perf_counter() - started, 6)
                status = "success" if result.success else "failed"
                metrics_attempts.append(
                    AttemptTiming(
                        report_code=report_code,
                        period=period.label,
                        attempt=result.attempts,
                        status=status,
                        error_code=result.error_code,
                        duration_sec=duration_sec,
                        output_path=str(result.output_path)
                        if result.output_path
                        else None,
                        file_size=_result_file_size(result.output_path),
                        stages=[
                            StageTiming(
                                stage="download_report",
                                duration_sec=duration_sec,
                                status=status,
                                error_code=result.error_code,
                            )
                        ],
                    )
                )
                if result.success:
                    summary.success_count += 1
                else:
                    summary.error_count += 1
                    summary.failed_reports.append(f"{report_code}:{period.label}")
                    write_failure_artifacts(
                        Path("logs"),
                        run_id,
                        report_code,
                        period.label,
                        {
                            "report_code": report_code,
                            "period": period.label,
                            "error": result.error,
                            "error_code": result.error_code,
                            "error_stage": result.error_stage,
                            "error_message": result.error_message,
                        },
                        metrics_attempts[-1].to_dict(),
                        getattr(session, "page", None),
                    )
        logger.info(
            "summary | success=%s | error=%s | failed=%s",
            summary.success_count,
            summary.error_count,
            ", ".join(summary.failed_reports) if summary.failed_reports else "none",
        )
        log_dir = Path("logs")
        _write_summary(log_dir, summary)
        write_run_metrics(
            log_dir,
            RunMetrics(
                run_id=run_id,
                status="success" if summary.error_count == 0 else "failed",
                dry_run=False,
                attempts=metrics_attempts,
            ),
        )
        save_session_state(session, config.session_file)
        return 0 if summary.error_count == 0 else 1
    finally:
        close_browser_session(session)


if __name__ == "__main__":
    raise SystemExit(main())
