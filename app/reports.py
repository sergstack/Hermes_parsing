"""Report definitions and UI parameter mappings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .dates import MonthPeriod


@dataclass(frozen=True)
class ReportDefinition:
    code: str
    url_path: str
    build_url: Callable[[str, MonthPeriod], str]
    export_dir: str
    export_endpoint: str | None = None
    export_ready_name: str | None = None
    apply_search_before_export: bool = False
    pre_search_wait_ms: int = 0
    search_done_selector: str | None = ".dx-loadpanel-content"
    reserves_filter_value: str | None = None
    export_via_history: bool = False
    # If True, after clicking the export button the script enters report.file_prefix_YYYY-MM
    # into the filename popover ("Имя файла можно изменить") and then downloads via history.
    # This is the flow used by "applications" and "budget_rows".
    use_export_marker: bool = False
    # If True, _apply_search will explicitly fill a date-range picker via UI.
    # The label of the picker is given by date_filter_label.
    payment_date_filter: bool = False
    # If True, payment_date_filter uses a single date input instead of a date range.
    single_date_filter: bool = False
    # Label of the date-range form item to fill when payment_date_filter=True.
    date_filter_label: str = "Дата оплаты"
    # Explicit UI select filters to apply before export.
    select_filters: tuple[tuple[str, str], ...] = ()
    # Explicit UI checkbox filters to apply before export.
    checkbox_filters: tuple[tuple[str, bool], ...] = ()
    clear_text_input_labels: tuple[str, ...] = ()
    repeat_each_month: bool = True
    file_prefix: str = "raw"
    append_month_to_filename: bool = True
    wait_after_export_ms: int = 5000


def validate_report_definition(report: ReportDefinition) -> None:
    if report.export_endpoint and report.use_export_marker:
        raise ValueError(
            f"{report.code}: export_endpoint cannot be combined with use_export_marker"
        )
    if report.export_endpoint and report.export_via_history:
        raise ValueError(
            f"{report.code}: export_endpoint cannot be combined with export_via_history"
        )
    if report.use_export_marker and report.export_via_history:
        raise ValueError(
            f"{report.code}: use_export_marker cannot be combined with export_via_history"
        )


def validate_report_definitions() -> None:
    for report in REPORT_DEFINITIONS.values():
        validate_report_definition(report)


def month_start_end(period: MonthPeriod) -> tuple[str, str]:
    return period.start.strftime("%Y-%m-%d"), period.end.strftime("%Y-%m-%d")


def _build_applications_url(base_url: str, period: MonthPeriod) -> str:
    start, end = month_start_end(period)
    return (
        f"{base_url}/new_demand?"
        f"date_of_create%5B0%5D={start}&date_of_create%5B1%5D={end}"
        "&all=false&archived=0&deleted=0"
    )


def _build_dds_expenses_url(base_url: str, period: MonthPeriod) -> str:
    start, end = month_start_end(period)
    return (
        f"{base_url}/budgeting/reports/plan_fact_bdds_report?"
        "statuses%5B0%5D=2&statuses%5B1%5D=6&statuses%5B2%5D=7&statuses%5B3%5D=5&statuses%5B4%5D=3"
        f"&interval%5B0%5D={start}&interval%5B1%5D={end}"
        "&level=3&reportType=by_month"
        "&excludeIntraCompany=1&excludeFounder=1&excludeBilling=1&excludeFinancialAgent=1"
        "&excludeReserve=2&isGroupsCollapsed=false&reportCurrencyId=5"
    )


def _build_bank_cashbox_url(base_url: str, period: MonthPeriod) -> str:
    start, end = month_start_end(period)
    return (
        f"{base_url}/bank_and_cashbox/operations?"
        f"date_of_document%5B0%5D={start}&date_of_document%5B1%5D={end}"
        "&all=false&archived=0&deleted=0&reportCurrencyId=5"
    )


def _build_budget_rows_url(base_url: str, period: MonthPeriod) -> str:
    start, end = month_start_end(period)
    # Filters:
    #   date_of_payment  — Дата оплаты = month range  (date_of_document = Дата отражения stays empty)
    #   reportCurrencyId=5 — EUR
    #   row_type[0]=expense — Тип строки: Расход
    #   Statuses: all except "Отклонено".
    #     Known IDs from herm.finance: 1=Черновик, 2=Отправлено, 3=Возвращено,
    #     5=Бюджет принят, 6=Проверено, 7=На согласовании; 4=Отклонено (excluded).
    #   Verify these param names against the live URL bar on first run.
    return (
        f"{base_url}/rows?"
        f"date_of_payment%5B0%5D={start}&date_of_payment%5B1%5D={end}"
        "&row_type%5B0%5D=expense"
        "&statuses%5B0%5D=1&statuses%5B1%5D=2&statuses%5B2%5D=3"
        "&statuses%5B3%5D=5&statuses%5B4%5D=6&statuses%5B5%5D=7"
        "&all=false&archived=0&deleted=0&reportCurrencyId=5"
    )


def _build_contractors_url(base_url: str, period: MonthPeriod) -> str:
    return (
        f"{base_url}/dictionary/contractors?all=false&archived=0&deleted=0&group_id=0"
    )


def _build_account_balances_url(base_url: str, period: MonthPeriod) -> str:
    end = period.end.strftime("%Y-%m-%d")
    return (
        f"{base_url}/ledger/reports/account_balance_report?"
        f"date={end}&exclude_zero_balances=0&exclude_blocked=0"
        "&exclude_closed=0&exclude_moneyboxes=0&exclude_archived=1&is_holder=false"
        "&reportCurrencyId=5"
    )


def _build_cons_budget_url(base_url: str, period: MonthPeriod) -> str:
    start, end = month_start_end(period)
    return (
        f"{base_url}/budgeting/reports/consolidated_plan_fact_monthly_report?"
        f"dates_period%5B0%5D={start}&dates_period%5B1%5D={end}"
        "&projects%5B0%5D=5"
        "&statuses%5B0%5D=7&statuses%5B1%5D=6&statuses%5B2%5D=5"
        "&statuses%5B3%5D=2&statuses%5B4%5D=3"
        "&level=3"
        "&excludeIntraCompany=1"
        "&showDiff=false"
        "&showCurrentInOutDiff=false"
        "&showPrevInOutDiff=false"
        "&planFactDisplayOption=planAndFact"
        "&reportCurrencyId=5"
    )


REPORT_DEFINITIONS: dict[str, ReportDefinition] = {
    "applications": ReportDefinition(
        "applications",
        "/new_demand",
        _build_applications_url,
        "demands",
        apply_search_before_export=True,
        use_export_marker=True,
        file_prefix="demands",
        clear_text_input_labels=("ID заявки",),
    ),
    "dds_expenses": ReportDefinition(
        "dds_expenses",
        "/budgeting/reports/plan_fact_bdds_report",
        _build_dds_expenses_url,
        "dds",
        apply_search_before_export=True,
        pre_search_wait_ms=2000,
        search_done_selector=None,
        export_via_history=True,
        reserves_filter_value="исключить",
        file_prefix="dds",
        wait_after_export_ms=3000,
    ),
    "p-fact": ReportDefinition(
        "p-fact",
        "/budgeting/reports/plan_fact_bdds_report",
        _build_dds_expenses_url,
        "p-fact",
        apply_search_before_export=True,
        pre_search_wait_ms=2000,
        search_done_selector=None,
        export_via_history=True,
        reserves_filter_value="исключить",
        file_prefix="p-fact",
        wait_after_export_ms=3000,
    ),
    "dds": ReportDefinition(
        "dds",
        "/bank_and_cashbox/operations",
        _build_bank_cashbox_url,
        "dds",
        apply_search_before_export=True,
        pre_search_wait_ms=2000,
        search_done_selector=None,
        payment_date_filter=True,
        date_filter_label="Дата начисления",
        use_export_marker=True,
        file_prefix="dds",
        wait_after_export_ms=5000,
    ),
    # budget_rows: UI flow — "Скачать .xlsx" → filename popover → download via history.
    # Date range extended to end of current year (planned payments are future months too).
    # payment_date_filter=True: "Дата оплаты" must be set via UI, not just URL params.
    "budget_rows": ReportDefinition(
        "budget_rows",
        "/rows",
        _build_budget_rows_url,
        "budget_rows",
        apply_search_before_export=True,
        payment_date_filter=True,
        date_filter_label="Дата оплаты",
        use_export_marker=True,
        file_prefix="raw",
        wait_after_export_ms=5000,
    ),
    "contractors": ReportDefinition(
        "contractors",
        "/dictionary/contractors",
        _build_contractors_url,
        "contractors",
        apply_search_before_export=False,
        use_export_marker=True,
        file_prefix="contractors",
        append_month_to_filename=False,
        repeat_each_month=False,
    ),
    "account_balances": ReportDefinition(
        "account_balances",
        "/ledger/reports/account_balance_report",
        _build_account_balances_url,
        "account_balances",
        apply_search_before_export=True,
        payment_date_filter=True,
        date_filter_label="Дата",
        single_date_filter=True,
        select_filters=(
            ("Отчетная валюта", "EUR"),
            ("Нулевые остатки", "--"),
            ("Заблокированные", "--"),
            ("Закрытые счета", "--"),
            ("Счета-копилки", "--"),
            ("Архивные счета", "Исключить"),
        ),
        checkbox_filters=(("Мои счета", False),),
        file_prefix="acc_balance",
        append_month_to_filename=False,
        wait_after_export_ms=8000,
    ),
    "cons_budget": ReportDefinition(
        "cons_budget",
        "/budgeting/reports/consolidated_plan_fact_monthly_report",
        _build_cons_budget_url,
        "cons_budget",
        apply_search_before_export=True,
        pre_search_wait_ms=2000,
        search_done_selector=None,
        file_prefix="cons_budget",
        append_month_to_filename=False,
        repeat_each_month=False,
        wait_after_export_ms=3000,
    ),
}


validate_report_definitions()
