from pathlib import Path

import pytest

from app.config import AppConfig, normalize_config, read_config


def test_read_config_parses_required_and_optional_fields(tmp_path):
    config_file = tmp_path / "config.txt"
    config_file.write_text(
        "\n".join(
            [
                "start_date=2026-03-01",
                "base_url=https://herm.finance",
                "download_dir=./exports",
                "session_file=./state/session.json",
                "headless=true",
                "overwrite=false",
                "timeout_ms=12345",
                "slow_mo=10",
                "repeat_each_month=yes",
            ]
        ),
        encoding="utf-8",
    )

    config = read_config(config_file)

    assert config.start_date == "2026-03-01"
    assert config.base_url == "https://herm.finance"
    assert config.download_dir == Path("exports")
    assert config.session_file == Path("state/session.json")
    assert config.headless is True
    assert config.overwrite is False
    assert config.timeout_ms == 12345
    assert config.slow_mo == 10
    assert config.repeat_each_month is True


def test_read_config_rejects_invalid_line(tmp_path):
    config_file = tmp_path / "config.txt"
    config_file.write_text(
        "\n".join(
            [
                "start_date=2026-03-01",
                "base_url=https://herm.finance",
                "download_dir=./exports",
                "session_file=./state/session.json",
                "invalid-line",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid config line"):
        read_config(config_file)


def test_normalize_config_resolves_relative_paths(tmp_path):
    config = AppConfig(
        start_date="2026-03-01",
        base_url="https://herm.finance",
        download_dir=Path("exports"),
        session_file=Path("state/session.json"),
        headless=False,
        overwrite=True,
        timeout_ms=60000,
        slow_mo=0,
    )

    normalized = normalize_config(config, tmp_path)

    assert normalized.download_dir == (tmp_path / "exports").resolve()
    assert normalized.session_file == (tmp_path / "state/session.json").resolve()


def test_normalize_config_infers_root_from_config_folder(tmp_path):
    config = AppConfig(
        start_date="2026-03-01",
        base_url="https://herm.finance",
        download_dir=Path("exports"),
        session_file=Path("state/session.json"),
        headless=False,
        overwrite=True,
        timeout_ms=60000,
        slow_mo=0,
        config_path=tmp_path / "config" / "config.txt",
    )

    normalized = normalize_config(config)

    assert normalized.download_dir == (tmp_path / "exports").resolve()
    assert normalized.session_file == (tmp_path / "state/session.json").resolve()
