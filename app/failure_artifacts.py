"""Best-effort failure artifact capture."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def failure_artifact_dir(
    log_dir: Path, run_id: str, report_code: str, period: str
) -> Path:
    safe_report = report_code.replace("/", "_")
    safe_period = period.replace("/", "_")
    return log_dir / "failures" / run_id / f"{safe_report}_{safe_period}"


def write_failure_artifacts(
    log_dir: Path,
    run_id: str,
    report_code: str,
    period: str,
    summary: dict[str, Any],
    metrics: dict[str, Any] | None = None,
    page: Any | None = None,
) -> Path:
    artifact_dir = failure_artifact_dir(log_dir, run_id, report_code, period)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    if metrics is not None:
        (artifact_dir / "metrics.json").write_text(
            json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    if page is not None:
        try:
            content = page.content()
            (artifact_dir / "page.html").write_text(str(content), encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass
        try:
            page.screenshot(path=str(artifact_dir / "screenshot.png"))
        except Exception:  # noqa: BLE001
            pass

    return artifact_dir
