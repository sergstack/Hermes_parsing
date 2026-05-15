"""Run summary accounting for exporter executions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ExportResult(Protocol):
    success: bool


class PeriodLabel(Protocol):
    label: str


@dataclass
class RunSummary:
    success_count: int = 0
    error_count: int = 0
    failed_reports: list[str] | None = None

    def __post_init__(self) -> None:
        if self.failed_reports is None:
            self.failed_reports = []

    def record_result(self, report_code: str, period: PeriodLabel, result: ExportResult) -> None:
        if result.success:
            self.success_count += 1
            return

        self.error_count += 1
        self.failed_reports.append(f"{report_code}:{period.label}")

    @property
    def has_errors(self) -> bool:
        return self.error_count > 0

    @property
    def failed_label(self) -> str:
        return ", ".join(self.failed_reports) if self.failed_reports else "none"

    def exit_code(self) -> int:
        return 1 if self.has_errors else 0
