import json

from app.metrics import AttemptTiming, RunMetrics, StageTiming, write_run_metrics


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
        run_id="test-run",
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
        "run_id": "test-run",
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
                "duration_sec": 0.0,
                "output_path": None,
                "file_size": None,
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


def test_write_run_metrics_writes_json_file(tmp_path):
    metrics = RunMetrics(run_id="test-run", status="planned", dry_run=True)

    metrics_path = write_run_metrics(tmp_path / "logs", metrics)

    assert metrics_path == tmp_path / "logs" / "run_metrics.json"
    assert json.loads(metrics_path.read_text(encoding="utf-8")) == {
        "run_id": "test-run",
        "schema_version": 1,
        "status": "planned",
        "dry_run": True,
        "attempts": [],
    }
