from pathlib import Path

from app.paths import build_output_directory, build_output_path, normalize_download_name


def test_build_output_directory_returns_report_folder():
    assert build_output_directory(Path("/tmp/exports"), "dds") == Path(
        "/tmp/exports/dds"
    )


def test_build_output_path_uses_prefix_and_suffix(sample_period):
    path = build_output_path(Path("/tmp/exports"), "dds", sample_period, "xlsx", "raw")
    assert path == Path("/tmp/exports/dds/raw_2026-03.xlsx")


def test_build_output_path_can_be_relabeled_without_month():
    path = build_output_path(
        Path("/tmp/exports"), "contractors", type("P", (), {"label": "2026-03"})(), "xlsx", "contractors"
    )
    assert path == Path("/tmp/exports/contractors/contractors_2026-03.xlsx")


def test_build_output_path_can_use_month_end_date():
    path = build_output_path(
        Path("/tmp/exports"),
        "account_balances",
        type("P", (), {"label": "2026-03", "end": __import__("datetime").date(2026, 3, 31)})(),
        "xlsx",
        "acc_balance",
        use_end_date=True,
    )
    assert path == Path("/tmp/exports/account_balances/acc_balance_2026-03-31.xlsx")


def test_normalize_download_name_keeps_suffix():
    assert normalize_download_name("report.xlsx") == "report.xlsx"


def test_normalize_download_name_adds_fallback_extension():
    assert normalize_download_name("report", ".csv") == "report.csv"
