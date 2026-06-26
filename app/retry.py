"""Retry policy primitives for exporter attempts."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import ExportErrorCode, is_retryable_error


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_sleep_sec: float = 2.0
    backoff_multiplier: float = 1.0
    jitter_sec: float = 0.0

    def sleep_seconds(self, attempt: int) -> float:
        return (
            self.base_sleep_sec
            * attempt
            * (self.backoff_multiplier ** max(attempt - 1, 0))
            + self.jitter_sec
        )

    def should_retry(self, error_code: str | None, attempt: int) -> bool:
        if attempt >= self.max_attempts:
            return False
        try:
            code = ExportErrorCode(error_code or "")
        except ValueError:
            return False
        return is_retryable_error(code)
