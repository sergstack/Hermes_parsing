import json

from app.experiments import ExperimentResult, candidate_beats_baseline


def test_score_calculation_is_deterministic():
    result = ExperimentResult(
        experiment_id="exp-1",
        report_code="dds",
        period="2026-03",
        variant="baseline",
        success=True,
        duration_sec=12.5,
        retry_count=1,
        failure_count=0,
    )

    assert result.score() == 82.5
    assert result.score() == result.score()


def test_failure_penalty_is_applied():
    result = ExperimentResult(
        experiment_id="exp-1",
        report_code="dds",
        period="2026-03",
        variant="candidate",
        success=False,
        duration_sec=12.5,
        retry_count=1,
        failure_count=1,
    )

    assert result.score() == -67.5


def test_candidate_beats_baseline_only_if_success_not_worse():
    baseline = ExperimentResult(
        experiment_id="exp-1",
        report_code="dds",
        period="2026-03",
        variant="baseline",
        success=True,
        duration_sec=20.0,
    )
    faster_success = ExperimentResult(
        experiment_id="exp-1",
        report_code="dds",
        period="2026-03",
        variant="candidate",
        success=True,
        duration_sec=10.0,
    )
    faster_failure = ExperimentResult(
        experiment_id="exp-1",
        report_code="dds",
        period="2026-03",
        variant="candidate",
        success=False,
        duration_sec=1.0,
        failure_count=1,
    )

    assert candidate_beats_baseline(baseline, faster_success) is True
    assert candidate_beats_baseline(baseline, faster_failure) is False


def test_candidate_with_more_failures_does_not_beat_baseline():
    baseline = ExperimentResult(
        experiment_id="exp-1",
        report_code="dds",
        period="2026-03",
        variant="baseline",
        success=False,
        duration_sec=20.0,
        failure_count=1,
    )
    candidate = ExperimentResult(
        experiment_id="exp-1",
        report_code="dds",
        period="2026-03",
        variant="candidate",
        success=False,
        duration_sec=1.0,
        failure_count=2,
    )

    assert candidate_beats_baseline(baseline, candidate) is False


def test_json_serialization_is_stable():
    result = ExperimentResult(
        experiment_id="exp-1",
        report_code="dds",
        period="2026-03",
        variant="baseline",
        success=True,
        duration_sec=12.5,
        retry_count=1,
    )

    assert result.to_json() == result.to_json()
    assert json.loads(result.to_json()) == {
        "experiment_id": "exp-1",
        "report_code": "dds",
        "period": "2026-03",
        "variant": "baseline",
        "success": True,
        "duration_sec": 12.5,
        "retry_count": 1,
        "failure_count": 0,
        "score": 82.5,
    }
