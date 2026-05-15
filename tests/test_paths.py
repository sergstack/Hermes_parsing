from pathlib import Path

from app.paths import resolve_project_path


def test_resolve_project_path_uses_project_root_for_relative_paths(tmp_path):
    project_root = tmp_path / "project"

    assert resolve_project_path(Path("logs"), project_root) == project_root / "logs"


def test_resolve_project_path_preserves_absolute_paths(tmp_path):
    absolute_path = tmp_path / "runtime" / "logs"

    assert resolve_project_path(absolute_path, tmp_path / "project") == absolute_path
