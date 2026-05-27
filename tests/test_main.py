from pathlib import Path
from datetime import date

from app import main as app_main


def test_run_summary_uses_independent_lists():
    first = app_main.RunSummary()
    second = app_main.RunSummary()

    first.failed_reports.append("dds:2026-03")
    first.planned_reports.append({"report_code": "dds"})

    assert second.failed_reports == []
    assert second.planned_reports == []


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


def test_main_dry_run_plans_cons_budget_for_full_year(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.txt"
    config_file.write_text(
        "\n".join(
            [
                "start_date=2026-01-01",
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
                "reports": "cons_budget",
                "dry_run": True,
                "headless": None,
                "overwrite": None,
            },
        )(),
    )

    exit_code = app_main.main()

    assert exit_code == 0
    summary_path = Path("logs/summary.json")
    assert summary_path.exists()
    summary_text = summary_path.read_text(encoding="utf-8")
    assert '"report_code": "cons_budget"' in summary_text
    assert '"period": "2025-01"' in summary_text
    assert (
        str(tmp_path / "exports" / "cons_budget" / "cons_budget_2026-04-30.xlsx")
        in summary_text
    )


def test_periods_for_cons_budget_use_fixed_start_and_last_completed_month():
    periods = app_main._periods_for_report(
        "cons_budget", "2026-01-01", today=date(2026, 5, 4)
    )
    assert len(periods) == 1
    assert periods[0].start == date(2025, 1, 1)
    assert periods[0].end == date(2026, 4, 30)
