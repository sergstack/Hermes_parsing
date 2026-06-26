"""Deterministic run metrics containers for exporter observability."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StageTiming:
    stage: str
    duration_sec: float
    status: str
    error_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "duration_sec": self.duration_sec,
            "status": self.status,
            "error_code": self.error_code,
        }


@dataclass(frozen=True)
class AttemptTiming:
    report_code: str
    period: str
    attempt: int
    status: str
    stages: list[StageTiming] = field(default_factory=list)
    error_code: str | None = None
    duration_sec: float = 0.0
    output_path: str | None = None
    file_size: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_code": self.report_code,
            "period": self.period,
            "attempt": self.attempt,
            "status": self.status,
            "error_code": self.error_code,
            "duration_sec": self.duration_sec,
            "output_path": self.output_path,
            "file_size": self.file_size,
            "stages": [stage.to_dict() for stage in self.stages],
        }


@dataclass(frozen=True)
class RunMetrics:
    run_id: str = ""
    schema_version: int = 1
    status: str = "unknown"
    dry_run: bool = False
    attempts: list[AttemptTiming] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "schema_version": self.schema_version,
            "status": self.status,
            "dry_run": self.dry_run,
            "attempts": [attempt.to_dict() for attempt in self.attempts],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)


def write_run_metrics(log_dir: Path, metrics: RunMetrics) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = log_dir / "run_metrics.json"
    metrics_path.write_text(metrics.to_json() + "\n", encoding="utf-8")
    return metrics_path
