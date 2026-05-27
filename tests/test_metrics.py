import json

from app.metrics import AttemptTiming, RunMetrics, StageTiming


def test_stage_timing_serializes_required_fields():
    stage = StageTiming(
        stage="apply_search",
        duration_sec=1.25,
        status="success",
        error_code=None,
    )

    assert stage.to_dict() == {
        "stage": "apply_search",
        "duration_sec": 1.25,
        "status": "success",
        "error_code": None,
    }


def test_run_metrics_json_is_deterministic_and_json_serializable():
    metrics = RunMetrics(
        status="success",
        dry_run=True,
        attempts=[
            AttemptTiming(
                report_code="dds",
                period="2026-03",
                attempt=1,
                status="success",
                stages=[
                    StageTiming(
                        stage="page_open",
                        duration_sec=0.5,
                        status="success",
                    )
                ],
            )
        ],
    )

    payload = metrics.to_json()

    assert payload == metrics.to_json()
    assert json.loads(payload) == {
        "schema_version": 1,
        "status": "success",
        "dry_run": True,
        "attempts": [
            {
                "report_code": "dds",
                "period": "2026-03",
                "attempt": 1,
                "status": "success",
                "error_code": None,
                "stages": [
                    {
                        "stage": "page_open",
                        "duration_sec": 0.5,
                        "status": "success",
                        "error_code": None,
                    }
                ],
            }
        ],
    }


def test_attempt_timing_can_represent_failure_code():
    attempt = AttemptTiming(
        report_code="p-fact",
        period="2026-04",
        attempt=2,
        status="failed",
        error_code="history_timeout",
    )

    assert attempt.to_dict()["error_code"] == "history_timeout"
    assert attempt.to_dict()["stages"] == []
