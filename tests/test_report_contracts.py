from datetime import date
from pathlib import Path

import pytest

from app import main as app_main
from app.dates import MonthPeriod
from app.paths import build_output_path
from app.reports import (
    REPORT_DEFINITIONS,
    ReportDefinition,
    validate_report_definition,
)


def strategy_name(report):
    if report.export_endpoint:
        return "api"
    if report.use_export_marker:
        return "marker_history"
    if report.export_via_history:
        return "history"
    return "direct"


EXPECTED_STRATEGIES = {
    "applications": "marker_history",
    "dds_expenses": "history",
    "p-fact": "history",
    "dds": "marker_history",
    "budget_rows": "marker_history",
    "contractors": "marker_history",
    "account_balances": "direct",
    "cons_budget": "direct",
}


EXPECTED_OUTPUT_PATHS = {
    "applications": Path("demands/demands_2026-03.xlsx"),
    "dds_expenses": Path("dds/dds_2026-03.xlsx"),
    "p-fact": Path("p-fact/p-fact_2026-03.xlsx"),
    "dds": Path("dds/dds_2026-03.xlsx"),
    "budget_rows": Path("budget_rows/raw_2026-03.xlsx"),
    "contractors": Path("contractors/contractors.xlsx"),
    "account_balances": Path("account_balances/acc_balance_2026-03-31.xlsx"),
    "cons_budget": Path("cons_budget/cons_budget.xlsx"),
}


def _output_contract_path(
    report: ReportDefinition,
    period: MonthPeriod,
    download_dir: Path = Path("/tmp/exports"),
) -> Path:
    use_end_date = (
        not report.append_month_to_filename
        and report.payment_date_filter
        and report.single_date_filter
    )
    output_path = build_output_path(
        download_dir,
        report.export_dir,
        period,
        ".xlsx",
        report.file_prefix,
        use_end_date=use_end_date,
    )
    if not report.append_month_to_filename and not use_end_date:
        output_path = output_path.with_name(f"{report.file_prefix}.xlsx")
    return output_path.relative_to(download_dir)


def test_all_reports_have_explicit_strategy_expectations():
    assert set(REPORT_DEFINITIONS) == set(EXPECTED_STRATEGIES)
    assert {
        code: strategy_name(report) for code, report in REPORT_DEFINITIONS.items()
    } == EXPECTED_STRATEGIES


def test_report_strategies_do_not_use_conflicting_flags():
    for report in REPORT_DEFINITIONS.values():
        enabled_strategies = [
            bool(report.export_endpoint),
            report.use_export_marker,
            report.export_via_history,
        ]
        assert sum(enabled_strategies) <= 1, report.code


def test_report_definition_invariants(sample_period):
    base_url = "https://herm.finance"

    for code, report in REPORT_DEFINITIONS.items():
        assert report.code == code
        assert report.url_path.startswith("/")
        assert report.export_dir
        assert report.file_prefix
        assert report.build_url(base_url, sample_period).startswith(f"{base_url}/")
        validate_report_definition(report)


@pytest.mark.parametrize(
    "overrides",
    [
        {"export_endpoint": "/api/export", "use_export_marker": True},
        {"export_endpoint": "/api/export", "export_via_history": True},
        {"use_export_marker": True, "export_via_history": True},
    ],
)
def test_invalid_report_strategy_combinations_are_rejected(overrides):
    report = ReportDefinition(
        code="invalid",
        url_path="/invalid",
        build_url=lambda base_url, period: f"{base_url}/invalid",
        export_dir="invalid",
        **overrides,
    )

    with pytest.raises(ValueError):
        validate_report_definition(report)


@pytest.mark.parametrize("report_code", EXPECTED_OUTPUT_PATHS)
def test_report_output_path_contracts(report_code, sample_period):
    assert (
        _output_contract_path(REPORT_DEFINITIONS[report_code], sample_period)
        == EXPECTED_OUTPUT_PATHS[report_code]
    )


def test_one_shot_reports_do_not_repeat_or_append_month():
    for report_code in ("contractors", "cons_budget"):
        report = REPORT_DEFINITIONS[report_code]
        assert report.repeat_each_month is False
        assert report.append_month_to_filename is False


def test_applications_clear_request_id_before_export():
    assert REPORT_DEFINITIONS["applications"].clear_text_input_labels == ("ID заявки",)


def test_account_balances_applies_required_ui_filters():
    report = REPORT_DEFINITIONS["account_balances"]

    assert report.single_date_filter is True
    assert report.date_filter_label == "Дата"
    assert report.select_filters == (
        ("Отчетная валюта", "EUR"),
        ("Нулевые остатки", "--"),
        ("Заблокированные", "--"),
        ("Закрытые счета", "--"),
        ("Счета-копилки", "--"),
        ("Архивные счета", "Исключить"),
    )


def test_budget_rows_periods_run_until_current_year_end():
    periods = app_main._periods_for_report(
        "budget_rows", "2026-03-01", today=date(2026, 4, 17)
    )

    assert [period.label for period in periods] == [
        "2026-03",
        "2026-04",
        "2026-05",
        "2026-06",
        "2026-07",
        "2026-08",
        "2026-09",
        "2026-10",
        "2026-11",
        "2026-12",
    ]


def test_cons_budget_periods_use_single_fixed_start_to_last_completed_month():
    periods = app_main._periods_for_report(
        "cons_budget", "2026-01-01", today=date(2026, 5, 4)
    )

    assert len(periods) == 1
    assert periods[0].start == date(2025, 1, 1)
    assert periods[0].end == date(2026, 4, 30)


def test_default_report_periods_use_completed_months_only():
    periods = app_main._periods_for_report("dds", "2026-03-01", today=date(2026, 5, 4))

    assert [period.label for period in periods] == ["2026-03", "2026-04"]


def test_readme_supported_reports_mentions_every_report_code():
    readme = Path("README.md").read_text(encoding="utf-8")

    for report_code in REPORT_DEFINITIONS:
        assert f"`{report_code}`" in readme
