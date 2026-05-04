from pathlib import Path

from app import main as app_main


def test_main_dry_run_writes_summary_without_browser(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.txt"
    config_file.write_text(
        "\n".join(
            [
                "start_date=2026-03-01",
                "base_url=https://herm.finance",
                "download_dir=./exports",
                "session_file=./state/session.json",
                "headless=true",
                "overwrite=false",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        app_main,
        "_parse_args",
        lambda: type(
            "Args",
            (),
            {
                "config": str(config_file),
                "reports": "dds",
                "dry_run": True,
                "headless": None,
                "overwrite": None,
            },
        )(),
    )

    calls = []
    monkeypatch.setattr(
        app_main, "ensure_logged_in", lambda config: calls.append(config)
    )

    exit_code = app_main.main()

    assert exit_code == 0
    assert calls == []
    summary_path = Path("logs/summary.json")
    assert summary_path.exists()
    assert '"report_code": "dds"' in summary_path.read_text(encoding="utf-8")
