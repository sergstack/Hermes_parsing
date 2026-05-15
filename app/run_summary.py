"""Run summary accounting for exporter executions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RunSummary:
    success_count: int = 0
    error_count: int = 0
    failed_reports: list[str] | None = None

    def __post_init__(self) -> None:
        if self.failed_reports is None:
            self.failed_reports = []
