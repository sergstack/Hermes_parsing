from app.errors import ExportError, ExportErrorCode, is_retryable_error
from app.metrics import AttemptTiming, StageTiming


def test_export_error_code_values_are_stable_strings():
    assert ExportErrorCode.EXPORT_HISTORY_STALE == "export_history_stale"
    assert ExportErrorCode.LOGIN_EXPIRED == "login_expired"
    assert ExportErrorCode.UNKNOWN == "unknown"


def test_export_error_serializes_to_dict():
    err = ExportError(
        code=ExportErrorCode.EXPORT_HISTORY_STALE,
        stage="history_refresh",
        message="Export history did not refresh",
        retryable=True,
    )

    assert err.to_dict() == {
        "code": "export_history_stale",
        "stage": "history_refresh",
        "message": "Export history did not refresh",
        "retryable": True,
    }


def test_retryable_error_map_returns_expected_values():
    retryable_codes = {
        ExportErrorCode.PAGE_OPEN_TIMEOUT,
        ExportErrorCode.SEARCH_APPLY_FAILED,
        ExportErrorCode.EXPORT_TRIGGER_FAILED,
        ExportErrorCode.EXPORT_HISTORY_STALE,
        ExportErrorCode.EXPORT_ROW_TIMEOUT,
        ExportErrorCode.DOWNLOAD_TIMEOUT,
        ExportErrorCode.EMPTY_FILE,
        ExportErrorCode.PLAYWRIGHT_ERROR,
    }

    for code in retryable_codes:
        assert is_retryable_error(code) is True


def test_non_retryable_errors_remain_non_retryable():
    non_retryable_codes = {
        ExportErrorCode.LOGIN_EXPIRED,
        ExportErrorCode.OUTPUT_EXISTS_SKIP,
        ExportErrorCode.INVALID_CONFIG,
        ExportErrorCode.UNKNOWN,
        ExportErrorCode.EXPORT_BUTTON_NOT_FOUND,
    }

    for code in non_retryable_codes:
        assert is_retryable_error(code) is False


def test_error_taxonomy_can_be_used_as_metrics_error_code_string():
    attempt = AttemptTiming(
        report_code="dds",
        period="2026-03",
        attempt=1,
        status="failed",
        error_code=ExportErrorCode.DOWNLOAD_TIMEOUT.value,
        stages=[
            StageTiming(
                stage="download",
                duration_sec=60.0,
                status="failed",
                error_code=ExportErrorCode.DOWNLOAD_TIMEOUT.value,
            )
        ],
    )

    payload = attempt.to_dict()

    assert payload["error_code"] == "download_timeout"
    assert payload["stages"][0]["error_code"] == "download_timeout"
