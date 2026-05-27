import json
from unittest.mock import MagicMock

from app.failure_artifacts import failure_artifact_dir, write_failure_artifacts


def test_failure_artifact_dir_is_deterministic(tmp_path):
    assert failure_artifact_dir(tmp_path / "logs", "run-1", "p/fact", "2026/03") == (
        tmp_path / "logs" / "failures" / "run-1" / "p_fact_2026_03"
    )


def test_write_failure_artifacts_writes_summary_and_metrics(tmp_path):
    artifact_dir = write_failure_artifacts(
        tmp_path / "logs",
        "run-1",
        "dds",
        "2026-03",
        {"error_code": "download_timeout"},
        {"status": "failed"},
    )

    assert json.loads((artifact_dir / "summary.json").read_text(encoding="utf-8")) == {
        "error_code": "download_timeout"
    }
    assert json.loads((artifact_dir / "metrics.json").read_text(encoding="utf-8")) == {
        "status": "failed"
    }


def test_write_failure_artifacts_captures_page_when_available(tmp_path):
    page = MagicMock()
    page.content.return_value = "<html>failure</html>"

    artifact_dir = write_failure_artifacts(
        tmp_path / "logs",
        "run-1",
        "dds",
        "2026-03",
        {"error_code": "download_timeout"},
        page=page,
    )

    assert (artifact_dir / "page.html").read_text(encoding="utf-8") == (
        "<html>failure</html>"
    )
    page.screenshot.assert_called_once_with(path=str(artifact_dir / "screenshot.png"))


def test_write_failure_artifacts_ignores_page_capture_errors(tmp_path):
    page = MagicMock()
    page.content.side_effect = RuntimeError("content failed")
    page.screenshot.side_effect = RuntimeError("screenshot failed")

    artifact_dir = write_failure_artifacts(
        tmp_path / "logs",
        "run-1",
        "dds",
        "2026-03",
        {"error_code": "download_timeout"},
        page=page,
    )

    assert (artifact_dir / "summary.json").exists()
    assert not (artifact_dir / "page.html").exists()
    assert not (artifact_dir / "screenshot.png").exists()
