from datetime import date

import pytest

from app.dates import build_months_range_until_year_end, MonthPeriod
from app.orchestration import build_cons_budget_period
from app.reports import (
    REPORT_DEFINITIONS,
    _build_account_balances_url,
    _build_applications_url,
    _build_bank_cashbox_url,
    _build_budget_rows_url,
    _build_cons_budget_url,
    _build_contractors_url,
    _build_dds_expenses_url,
)


@pytest.mark.parametrize(
    ("builder", "expected"),
    [
        (
            _build_applications_url,
            "https://herm.finance/new_demand?date_of_create%5B0%5D=2026-03-01&date_of_create%5B1%5D=2026-03-31&all=false&archived=0&deleted=0",
        ),
        (
            _build_dds_expenses_url,
            "https://herm.finance/budgeting/reports/plan_fact_bdds_report?statuses%5B0%5D=2&statuses%5B1%5D=6&statuses%5B2%5D=7&statuses%5B3%5D=5&statuses%5B4%5D=3&interval%5B0%5D=2026-03-01&interval%5B1%5D=2026-03-31&level=3&reportType=by_month&excludeIntraCompany=1&excludeFounder=1&excludeBilling=1&excludeFinancialAgent=1&excludeReserve=1&isGroupsCollapsed=false&reportCurrencyId=5",
        ),
        (
            _build_bank_cashbox_url,
            "https://herm.finance/bank_and_cashbox/operations?date_of_document%5B0%5D=2026-03-01&date_of_document%5B1%5D=2026-03-31&all=false&archived=0&deleted=0&reportCurrencyId=5",
        ),
        (
            # Дата оплаты = month, Тип строки = Расход, все статусы кроме Отклонено (4), EUR
            _build_budget_rows_url,
            "https://herm.finance/rows?"
            "date_of_payment%5B0%5D=2026-03-01&date_of_payment%5B1%5D=2026-03-31"
            "&row_type%5B0%5D=expense"
            "&statuses%5B0%5D=1&statuses%5B1%5D=2&statuses%5B2%5D=3"
            "&statuses%5B3%5D=5&statuses%5B4%5D=6&statuses%5B5%5D=7"
            "&all=false&archived=0&deleted=0&reportCurrencyId=5",
        ),
        (
            _build_cons_budget_url,
            "https://herm.finance/budgeting/reports/consolidated_plan_fact_monthly_report?"
            "statuses%5B0%5D=7&statuses%5B1%5D=2&statuses%5B2%5D=6&statuses%5B3%5D=5&statuses%5B4%5D=3"
            "&level=3&excludeIntraCompany=1&reportCurrencyId=5&reportType=by_month",
        ),
        (
            _build_contractors_url,
            "https://herm.finance/dictionary/contractors?all=false&archived=0&deleted=0&group_id=0",
        ),
        (
            _build_account_balances_url,
            "https://herm.finance/ledger/reports/account_balance_report?date=2026-03-31&exclude_zero_balances=0&exclude_blocked=0&exclude_closed=0&exclude_moneyboxes=0&exclude_archived=1&is_holder=false&reportCurrencyId=5",
        ),
    ],
)
def test_build_urls(sample_period, builder, expected):
    assert builder("https://herm.finance", sample_period) == expected


def test_budget_rows_range_includes_future_months():
    """budget_rows must be downloaded for all months up to December of the current year."""
    periods = build_months_range_until_year_end("2026-03-01", today=date(2026, 4, 17))
    labels = [p.label for p in periods]
    assert "2026-03" in labels
    assert "2026-12" in labels
    # Must NOT include January of next year
    assert "2027-01" not in labels


def test_budget_rows_uses_export_marker():
    """budget_rows must use the filename-popover flow (use_export_marker=True)."""
    assert REPORT_DEFINITIONS["budget_rows"].use_export_marker is True


def test_budget_rows_no_api_endpoint():
    """budget_rows must NOT use the broken API endpoint."""
    assert REPORT_DEFINITIONS["budget_rows"].export_endpoint is None


def test_cons_budget_filters():
    rd = REPORT_DEFINITIONS["cons_budget"]
    assert rd.repeat_each_month is False
    assert rd.date_filter_label == "Период"
    assert rd.clear_checkbox_labels == (
        "Отображать отклонения",
        "План|факт / IN-OUT(текущий)",
        "План|факт / IN-OUT(предыдущий)",
    )
    assert rd.select_filters == (("Проекты", "Azp_admin"), ("ВГО", "исключить"))


def test_cons_budget_period_uses_config_start_date_until_current_year_end():
    period = build_cons_budget_period(date(2024, 1, 1), today=date(2026, 5, 14))

    assert period.start == date(2024, 1, 1)
    assert period.end == date(2026, 12, 31)


def test_applications_uses_export_marker():
    """applications must still use the filename-popover flow after refactor."""
    assert REPORT_DEFINITIONS["applications"].use_export_marker is True


def test_dds_uses_export_marker():
    """dds must use the filename-popover flow."""
    assert REPORT_DEFINITIONS["dds"].use_export_marker is True


def test_dds_date_filter_label():
    """dds date picker label must be 'Дата начисления'."""
    assert REPORT_DEFINITIONS["dds"].date_filter_label == "Дата начисления"


def test_dds_file_prefix():
    """dds files must be named dds_YYYY-MM."""
    assert REPORT_DEFINITIONS["dds"].file_prefix == "dds"


def test_dds_expenses_exports_to_p_fact():
    """dds_expenses export must go to 'p-fact' folder with 'p-fact' prefix."""
    rd = REPORT_DEFINITIONS["dds_expenses"]
    assert rd.export_dir == "p-fact"
    assert rd.file_prefix == "p-fact"
    assert rd.export_via_history is False


def test_dds_reserves_removed():
    """dds_reserves report must no longer exist."""
    assert "dds_reserves" not in REPORT_DEFINITIONS
