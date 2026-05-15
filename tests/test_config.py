from pathlib import Path

from app.config import AppConfig, read_config


def test_resolved_relative_paths_use_project_root(tmp_path):
    project_root = tmp_path / "project"
    config = AppConfig(
        start_date="2026-01-01",
        base_url="https://herm.finance",
        download_dir=Path("./exports"),
        session_file=Path("./state/herm_session.json"),
        headless=True,
        overwrite=False,
        timeout_ms=1000,
        slow_mo=0,
    )

    resolved = config.resolved(project_root)

    assert resolved.download_dir == project_root / "exports"
    assert resolved.session_file == project_root / "state" / "herm_session.json"


def test_resolved_preserves_absolute_paths(tmp_path):
    download_dir = tmp_path / "external_exports"
    session_file = tmp_path / "external_state" / "session.json"
    config = AppConfig(
        start_date="2026-01-01",
        base_url="https://herm.finance",
        download_dir=download_dir,
        session_file=session_file,
        headless=True,
        overwrite=False,
        timeout_ms=1000,
        slow_mo=0,
    )

    resolved = config.resolved(tmp_path / "project")

    assert resolved.download_dir == download_dir
    assert resolved.session_file == session_file


def test_read_config_resolves_config_file_independent_of_cwd(tmp_path, monkeypatch):
    project_root = tmp_path / "project"
    project_root.mkdir()
    config_path = project_root / "config.txt"
    config_path.write_text(
        "\n".join(
            [
                "start_date=2026-01-01",
                "base_url=https://herm.finance",
                "download_dir=./exports",
                "session_file=./state/herm_session.json",
            ]
        ),
        encoding="utf-8",
    )
    other_cwd = tmp_path / "other"
    other_cwd.mkdir()
    monkeypatch.chdir(other_cwd)

    config = read_config(config_path).resolved(project_root)

    assert config.config_path == config_path.resolve()
    assert config.download_dir == project_root / "exports"
    assert config.session_file == project_root / "state" / "herm_session.json"
