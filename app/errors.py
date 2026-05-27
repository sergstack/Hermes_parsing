"""Stable exporter error codes for metrics and retry planning."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ExportErrorCode(StrEnum):
    PAGE_OPEN_TIMEOUT = "page_open_timeout"
    LOGIN_EXPIRED = "login_expired"
    SEARCH_APPLY_FAILED = "search_apply_failed"
    EXPORT_BUTTON_NOT_FOUND = "export_button_not_found"
    EXPORT_TRIGGER_FAILED = "export_trigger_failed"
    EXPORT_HISTORY_STALE = "export_history_stale"
    EXPORT_ROW_TIMEOUT = "export_row_timeout"
    DOWNLOAD_TIMEOUT = "download_timeout"
    EMPTY_FILE = "empty_file"
    OUTPUT_EXISTS_SKIP = "output_exists_skip"
    INVALID_CONFIG = "invalid_config"
    PLAYWRIGHT_ERROR = "playwright_error"
    UNKNOWN = "unknown"


_RETRYABLE_CODES = frozenset(
    {
        ExportErrorCode.PAGE_OPEN_TIMEOUT,
        ExportErrorCode.SEARCH_APPLY_FAILED,
        ExportErrorCode.EXPORT_TRIGGER_FAILED,
        ExportErrorCode.EXPORT_HISTORY_STALE,
        ExportErrorCode.EXPORT_ROW_TIMEOUT,
        ExportErrorCode.DOWNLOAD_TIMEOUT,
        ExportErrorCode.EMPTY_FILE,
        ExportErrorCode.PLAYWRIGHT_ERROR,
    }
)


def is_retryable_error(code: ExportErrorCode) -> bool:
    return code in _RETRYABLE_CODES


@dataclass(frozen=True)
class ExportError:
    code: ExportErrorCode
    stage: str
    message: str
    retryable: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "code": str(self.code),
            "stage": self.stage,
            "message": self.message,
            "retryable": self.retryable,
        }
