"""Deterministic run metrics containers for exporter observability."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_code": self.report_code,
            "period": self.period,
            "attempt": self.attempt,
            "status": self.status,
            "error_code": self.error_code,
            "stages": [stage.to_dict() for stage in self.stages],
        }


@dataclass(frozen=True)
class RunMetrics:
    schema_version: int = 1
    status: str = "unknown"
    dry_run: bool = False
    attempts: list[AttemptTiming] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "dry_run": self.dry_run,
            "attempts": [attempt.to_dict() for attempt in self.attempts],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)
