"""Pure experiment scoring models for parameter tuning."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExperimentResult:
    experiment_id: str
    report_code: str
    period: str
    variant: str
    success: bool
    duration_sec: float
    retry_count: int = 0
    failure_count: int = 0

    @property
    def success_rate(self) -> float:
        return 1.0 if self.success else 0.0

    def score(
        self,
        retry_penalty_weight: float = 5.0,
        failure_penalty_weight: float = 50.0,
    ) -> float:
        return (
            self.success_rate * 100
            - self.duration_sec
            - (self.retry_count * retry_penalty_weight)
            - (self.failure_count * failure_penalty_weight)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "report_code": self.report_code,
            "period": self.period,
            "variant": self.variant,
            "success": self.success,
            "duration_sec": self.duration_sec,
            "retry_count": self.retry_count,
            "failure_count": self.failure_count,
            "score": self.score(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)


def candidate_beats_baseline(
    baseline: ExperimentResult, candidate: ExperimentResult
) -> bool:
    if candidate.success_rate < baseline.success_rate:
        return False
    if candidate.failure_count > baseline.failure_count:
        return False
    return candidate.score() > baseline.score()
