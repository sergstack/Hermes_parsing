from unittest.mock import MagicMock, patch

from app.downloaders import (
    _apply_search,
    _download_first_exported_file,
    _enter_export_marker,
    _trigger_export_with_marker,
    _wait_for_export_ready_by_name,
)
from app.export_files import move_latest_download
from app.export_files import move_latest_download_since
from app.export_api import candidate_export_names


class _DownloadContext:
    def __init__(self, download):
        self.value = download

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_applications_download_helpers_use_expected_selectors(mock_page):
    popover_candidates = MagicMock()
    popover = MagicMock()
    input_locator = MagicMock()
    upload_button = MagicMock()
    files_button = MagicMock()
    download_button = MagicMock()
    tooltip_candidates = MagicMock()
    tooltip = MagicMock()
    visible_downloads = MagicMock()
    download = MagicMock()

    popover_candidates.filter.return_value.first = popover
    popover.locator.side_effect = lambda selector: {
        "input.el-input__inner": input_locator,
        "button.el-button:has-text('Загрузить')": upload_button,
    }[selector]

    tooltip_candidates.filter.return_value.first = tooltip
    tooltip.locator.return_value = visible_downloads
    visible_downloads.first = download_button
    mock_page.expect_download.return_value = _DownloadContext(download)

    def locator_side_effect(selector):
        mapping = {
            ".el-popover.export-popper-class": popover_candidates,
            "button.files-button": files_button,
            "div[role='tooltip'].el-popover.el-popper[aria-hidden='false']": tooltip_candidates,
            "button.download-button": MagicMock(),
        }
        return mapping[selector]

    mock_page.locator.side_effect = locator_side_effect

    _enter_export_marker(mock_page, "demands_2026-03")
    _download_first_exported_file(mock_page, 15000)

    popover.wait_for.assert_called_once_with(state="visible", timeout=5000)
    input_locator.first.fill.assert_called_once_with("demands_2026-03", timeout=3000)
    upload_button.first.click.assert_called_once_with(timeout=3000)
    files_button.click.assert_called_once_with(timeout=5000)
    tooltip.locator.assert_called_once_with(
        "td:not(.dx-hidden-cell) button.download-button"
    )
    download_button.wait_for.assert_called_once_with(state="visible", timeout=15000)
    download_button.click.assert_called_once_with(timeout=5000)


def test_apply_search_for_applications_clicks_show(mock_page):
    show_button = MagicMock()
    done_locator = MagicMock()
    primary_buttons = MagicMock()
    primary_buttons.filter.return_value = show_button
    show_button.count.return_value = 1

    def locator_side_effect(selector):
        if selector == "button.el-button--primary.el-button--small":
            return primary_buttons
        if selector == "button:has-text('Показать')":
            return primary_buttons
        if selector == ".dx-loadpanel-content":
            return done_locator
        raise AssertionError(selector)

    mock_page.locator.side_effect = locator_side_effect

    _apply_search(mock_page, 15000)

    show_button.first.click.assert_called_once_with(timeout=15000)
    done_locator.wait_for.assert_called_once_with(state="hidden", timeout=15000)


def test_apply_search_for_dds_expenses_sets_exclude_reserve_before_show(mock_page):
    events = []
    show_button = MagicMock()
    primary_buttons = MagicMock()
    primary_buttons.filter.return_value = show_button
    show_button.count.return_value = 1

    def click_show(*args, **kwargs):
        events.append("show")

    show_button.first.click.side_effect = click_show
    mock_page.locator.side_effect = lambda selector: (
        primary_buttons
        if selector == "button.el-button--primary.el-button--small"
        else MagicMock()
    )

    with patch(
        "app.downloaders._set_reserves_filter",
        side_effect=lambda page, value: events.append(f"reserve:{value}"),
    ) as set_filter:
        _apply_search(
            mock_page, 15000, done_selector=None, reserves_filter_value="исключить"
        )

    set_filter.assert_called_once_with(mock_page, "исключить")
    assert events == ["reserve:исключить", "show"]


def test_trigger_export_with_marker_calls_click_and_enter(mock_page):
    """_trigger_export_with_marker must click the export button then fill the popover."""
    with (
        patch("app.downloaders._click_export") as mock_click_export,
        patch("app.downloaders._enter_export_marker") as mock_enter_marker,
    ):
        _trigger_export_with_marker(mock_page, "demands_2026-03")

    mock_click_export.assert_called_once_with(mock_page)
    mock_enter_marker.assert_called_once_with(mock_page, "demands_2026-03")


def test_export_via_history_snapshots_then_clicks_export_before_download(
    tmp_path, mock_session
):
    from datetime import date
    from pathlib import Path

    from app.config import AppConfig
    from app.dates import MonthPeriod
    from app.downloaders import download_report_for_month

    events = []
    config = AppConfig(
        start_date="2025-01-01",
        base_url="https://herm.finance",
        download_dir=tmp_path / "exports",
        session_file=Path("/tmp/session.json"),
        headless=True,
        overwrite=True,
        timeout_ms=15000,
        slow_mo=0,
        repeat_each_month=False,
    )
    period = MonthPeriod(start=date(2025, 1, 1), end=date(2025, 1, 31))

    def record_wait(page, baseline, timeout_ms):
        events.append(f"wait:{baseline}")

    with (
        patch(
            "app.downloaders._apply_search",
            side_effect=lambda *args, **kwargs: events.append("apply_search"),
        ),
        patch(
            "app.downloaders._snapshot_history_top_row",
            side_effect=lambda *args, **kwargs: events.append("snapshot") or "old-row",
        ),
        patch(
            "app.downloaders._click_export",
            side_effect=lambda page: events.append("click_export"),
        ) as click_export,
        patch("app.downloaders._wait_for_history_refresh", side_effect=record_wait),
        patch(
            "app.downloaders._download_from_history",
            side_effect=lambda *args, **kwargs: (
                events.append("download")
                or tmp_path / "exports" / "dds" / "dds_2025-01.xlsx"
            ),
        ),
    ):
        result = download_report_for_month(mock_session, config, "dds_expenses", period)

    assert result.success is True
    click_export.assert_called_once_with(mock_session.page)
    assert events == [
        "apply_search",
        "snapshot",
        "click_export",
        "wait:old-row",
        "download",
    ]


def test_wait_for_export_ready_returns_when_status_ready(mock_session):
    """_wait_for_export_ready_by_name must return as soon as it finds a ready row."""
    ready_row = {
        "id": 999,
        "status_id": "ready",
        "original_file_name": "demands_2026-03.xlsx",
    }
    with patch("app.downloaders._load_export_rows", return_value=[ready_row]):
        # Should not raise, should return immediately
        _wait_for_export_ready_by_name(
            mock_session,
            "https://herm.finance",
            "demands_2026-03",
            timeout_ms=10000,
            min_id=0,
        )


def test_wait_for_export_ready_raises_on_fail_status(mock_session):
    """_wait_for_export_ready_by_name must raise RuntimeError if server reports fail."""
    import pytest

    fail_row = {
        "id": 999,
        "status_id": "fail",
        "original_file_name": "demands_2026-03.xlsx",
    }
    with patch("app.downloaders._load_export_rows", return_value=[fail_row]):
        with pytest.raises(RuntimeError, match="failed on server"):
            _wait_for_export_ready_by_name(
                mock_session,
                "https://herm.finance",
                "demands_2026-03",
                timeout_ms=10000,
                min_id=0,
            )


def test_wait_for_export_ready_ignores_rows_below_min_id(mock_session):
    """_wait_for_export_ready_by_name must skip rows with id <= min_id (old exports)."""
    import pytest

    old_row = {
        "id": 100,
        "status_id": "ready",
        "original_file_name": "demands_2026-03.xlsx",
    }
    # Only the old row exists — function must timeout, not return early.
    mock_session.page.wait_for_timeout = MagicMock()
    with patch("app.downloaders._load_export_rows", return_value=[old_row]):
        with pytest.raises(RuntimeError, match="did not become ready"):
            _wait_for_export_ready_by_name(
                mock_session,
                "https://herm.finance",
                "demands_2026-03",
                timeout_ms=100,
                min_id=100,
            )


def test_apply_search_for_dds_reserves_sets_only_reserve_before_show(mock_page):
    events = []
    show_button = MagicMock()
    primary_buttons = MagicMock()
    primary_buttons.filter.return_value = show_button
    show_button.count.return_value = 1

    def click_show(*args, **kwargs):
        events.append("show")

    show_button.first.click.side_effect = click_show
    mock_page.locator.side_effect = lambda selector: (
        primary_buttons
        if selector == "button.el-button--primary.el-button--small"
        else MagicMock()
    )

    with patch(
        "app.downloaders._set_reserves_filter",
        side_effect=lambda page, value: events.append(f"reserve:{value}"),
    ) as set_filter:
        _apply_search(
            mock_page, 15000, done_selector=None, reserves_filter_value="только"
        )

    set_filter.assert_called_once_with(mock_page, "только")
    assert events == ["reserve:только", "show"]


def test_apply_search_for_account_balances_applies_selects_and_checkbox(mock_page):
    events = []
    show_button = MagicMock()
    primary_buttons = MagicMock()
    primary_buttons.filter.return_value = show_button
    show_button.count.return_value = 1

    def click_show(*args, **kwargs):
        events.append("show")

    show_button.first.click.side_effect = click_show
    mock_page.locator.side_effect = lambda selector: (
        primary_buttons
        if selector == "button.el-button--primary.el-button--small"
        else MagicMock()
    )

    with (
        patch(
            "app.downloaders._set_single_date_by_label",
            side_effect=lambda page, label, value: events.append(
                f"date:{label}:{value}"
            ),
        ) as set_date,
        patch(
            "app.downloaders._set_select_value_by_label",
            side_effect=lambda page, label, value: events.append(
                f"select:{label}:{value}"
            ),
        ),
        patch(
            "app.downloaders._set_checkbox_by_label",
            side_effect=lambda page, label, checked: events.append(
                f"checkbox:{label}:{checked}"
            ),
        ),
    ):
        _apply_search(
            mock_page,
            15000,
            done_selector=None,
            payment_date=("31.05.26", "31.05.26"),
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
        )

    set_date.assert_called_once()
    assert events == [
        "date:Дата:31.05.26",
        "select:Отчетная валюта:EUR",
        "select:Нулевые остатки:--",
        "select:Заблокированные:--",
        "select:Закрытые счета:--",
        "select:Счета-копилки:--",
        "select:Архивные счета:Исключить",
        "checkbox:Мои счета:False",
        "show",
    ]


def test_set_single_date_by_label_fills_input(mock_page):
    from app.downloaders import _set_single_date_by_label

    form_item = MagicMock()
    input_locators = MagicMock()
    input_locators.count.return_value = 1
    input_locators.first = MagicMock()
    form_item.locator.return_value = input_locators
    mock_page.locator.return_value.filter.return_value.first = form_item

    _set_single_date_by_label(mock_page, "Дата", "31.05.26")

    input_locators.first.focus.assert_called_once_with(timeout=10000)
    input_locators.first.fill.assert_called_once_with("31.05.26", timeout=3000)


def test_candidate_export_names_supports_month_end_date():
    assert candidate_export_names("acc_balance_2025-01-31.xlsx") == [
        "acc_balance_2025-01-31.xlsx",
        "2025-01-31.xlsx",
    ]


def test_move_latest_download_moves_newest_xlsx(tmp_path):
    downloads_dir = tmp_path / "Downloads"
    downloads_dir.mkdir()
    old_file = downloads_dir / "old.xlsx"
    new_file = downloads_dir / "new.xlsx"
    old_file.write_text("old", encoding="utf-8")
    new_file.write_text("new", encoding="utf-8")
    old_mtime = old_file.stat().st_mtime
    new_file.touch()
    new_file.write_text("newer", encoding="utf-8")
    assert old_mtime <= new_file.stat().st_mtime

    output_path = (
        tmp_path / "exports" / "account_balances" / "acc_balance_2025-01-31.xlsx"
    )
    moved = move_latest_download(downloads_dir, output_path)

    assert moved == output_path
    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8") == "newer"


def test_move_latest_download_since_uses_only_new_files(tmp_path):
    downloads_dir = tmp_path / "Downloads"
    downloads_dir.mkdir()
    old_file = downloads_dir / "old.xlsx"
    new_file = downloads_dir / "new.xlsx"
    old_file.write_text("old", encoding="utf-8")
    new_file.write_text("new", encoding="utf-8")
    known_files = {old_file}

    output_path = (
        tmp_path / "exports" / "account_balances" / "acc_balance_2025-01-31.xlsx"
    )
    moved = move_latest_download_since(downloads_dir, output_path, known_files)

    assert moved == output_path
    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8") == "new"


def test_account_balances_uses_direct_download_after_search(mock_page):
    from app.downloaders import download_report_for_month
    from app.config import AppConfig
    from app.dates import MonthPeriod
    from datetime import date
    from pathlib import Path
    from unittest.mock import MagicMock, patch

    session = MagicMock()
    session.page = mock_page
    config = AppConfig(
        start_date="2025-01-01",
        base_url="https://herm.finance",
        download_dir=Path("/tmp/exports"),
        session_file=Path("/tmp/session.json"),
        headless=True,
        overwrite=True,
        timeout_ms=15000,
        slow_mo=0,
        repeat_each_month=False,
    )
    period = MonthPeriod(start=date(2025, 1, 1), end=date(2025, 1, 31))

    with (
        patch("app.downloaders._apply_search") as apply_search,
        patch(
            "app.downloaders._save_download",
            return_value=Path(
                "/tmp/exports/account_balances/acc_balance_2025-01-31.xlsx"
            ),
        ) as save_download,
        patch(
            "app.downloaders.ensure_dir",
            return_value=Path("/tmp/exports/account_balances"),
        ),
    ):
        download_report_for_month(session, config, "account_balances", period)

    assert apply_search.call_count >= 1
    save_download.assert_called_once()
    # account_balances is a direct browser download — via_history must be False
    call_args = save_download.call_args[0]
    assert call_args[5] is False


def test_apply_search_falls_back_when_show_button_not_found(mock_page):
    search_button = MagicMock()
    done_locator = MagicMock()
    primary_buttons = MagicMock()
    filtered_buttons = MagicMock()
    search_candidates = MagicMock()
    search_candidates.first = search_button.first

    primary_buttons.filter.return_value = filtered_buttons
    filtered_buttons.count.return_value = 0
    search_candidates.count.return_value = 1

    def locator_side_effect(selector):
        if selector == "button.el-button--primary.el-button--small":
            return primary_buttons
        if (
            selector
            == "button.el-button--primary.el-button--small:not(.input-button):has(i.el-icon-search)"
        ):
            return search_candidates
        if selector == ".dx-loadpanel-content":
            return done_locator
        raise AssertionError(selector)

    mock_page.locator.side_effect = locator_side_effect

    _apply_search(mock_page, 15000)

    search_button.first.click.assert_called_once_with(timeout=15000)
    done_locator.wait_for.assert_called_once_with(state="hidden", timeout=15000)


def _test_config(tmp_path):
    from pathlib import Path

    from app.config import AppConfig

    return AppConfig(
        start_date="2025-01-01",
        base_url="https://herm.finance",
        download_dir=tmp_path / "exports",
        session_file=Path("/tmp/session.json"),
        headless=True,
        overwrite=True,
        timeout_ms=15000,
        slow_mo=0,
        repeat_each_month=False,
    )


def _test_period():
    from datetime import date

    from app.dates import MonthPeriod

    return MonthPeriod(start=date(2025, 1, 1), end=date(2025, 1, 31))


def test_api_report_dispatches_to_api_helper(tmp_path, mock_session, monkeypatch):
    from app.downloaders import download_report_for_month
    from app.reports import REPORT_DEFINITIONS, ReportDefinition

    report = ReportDefinition(
        code="api_test",
        url_path="/api-test",
        build_url=lambda base_url, period: f"{base_url}/api-test",
        export_dir="api_test",
        export_endpoint="/api/export",
        file_prefix="api_test",
    )
    monkeypatch.setitem(REPORT_DEFINITIONS, "api_test", report)
    output_path = tmp_path / "exports" / "api_test" / "api_test_2025-01.xlsx"

    with patch(
        "app.downloaders._download_via_api_export", return_value=output_path
    ) as helper:
        result = download_report_for_month(
            mock_session, _test_config(tmp_path), "api_test", _test_period()
        )

    assert result.success is True
    helper.assert_called_once()


def test_marker_report_dispatches_to_marker_history_helper(tmp_path, mock_session):
    from app.downloaders import download_report_for_month

    output_path = tmp_path / "exports" / "demands" / "demands_2025-01.xlsx"

    with (
        patch("app.downloaders._apply_search"),
        patch(
            "app.downloaders._download_via_marker_history", return_value=output_path
        ) as helper,
    ):
        result = download_report_for_month(
            mock_session, _test_config(tmp_path), "applications", _test_period()
        )

    assert result.success is True
    helper.assert_called_once()


def test_history_report_dispatches_to_history_helper(tmp_path, mock_session):
    from app.downloaders import download_report_for_month

    output_path = tmp_path / "exports" / "dds" / "dds_2025-01.xlsx"

    with (
        patch("app.downloaders._apply_search"),
        patch(
            "app.downloaders._download_via_history", return_value=output_path
        ) as helper,
    ):
        result = download_report_for_month(
            mock_session, _test_config(tmp_path), "dds_expenses", _test_period()
        )

    assert result.success is True
    helper.assert_called_once()


def test_direct_report_dispatches_to_direct_browser_helper(tmp_path, mock_session):
    from app.downloaders import download_report_for_month

    output_path = (
        tmp_path / "exports" / "account_balances" / "acc_balance_2025-01-31.xlsx"
    )

    with (
        patch("app.downloaders._apply_search"),
        patch(
            "app.downloaders._download_via_direct_browser", return_value=output_path
        ) as helper,
    ):
        result = download_report_for_month(
            mock_session, _test_config(tmp_path), "account_balances", _test_period()
        )

    assert result.success is True
    helper.assert_called_once()


def test_existing_output_skip_happens_before_page_open(tmp_path, mock_session):
    from app.downloaders import download_report_for_month

    config = _test_config(tmp_path)
    config = type(config)(
        start_date=config.start_date,
        base_url=config.base_url,
        download_dir=config.download_dir,
        session_file=config.session_file,
        headless=config.headless,
        overwrite=False,
        timeout_ms=config.timeout_ms,
        slow_mo=config.slow_mo,
        repeat_each_month=config.repeat_each_month,
    )
    existing = config.download_dir / "dds" / "dds_2025-01.xlsx"
    existing.parent.mkdir(parents=True)
    existing.write_text("old", encoding="utf-8")

    with patch("app.downloaders._download_via_history") as helper:
        result = download_report_for_month(
            mock_session, config, "dds_expenses", _test_period()
        )

    assert result.success is True
    assert result.output_path == existing
    mock_session.page.goto.assert_not_called()
    helper.assert_not_called()


def test_contractors_stale_monthly_file_cleanup_is_preserved(tmp_path, mock_session):
    from app.downloaders import download_report_for_month

    config = _test_config(tmp_path)
    stale = config.download_dir / "contractors" / "contractors_2025-01.xlsx"
    stale.parent.mkdir(parents=True)
    stale.write_text("stale", encoding="utf-8")
    output_path = config.download_dir / "contractors" / "contractors.xlsx"

    with patch(
        "app.downloaders._download_via_marker_history", return_value=output_path
    ) as helper:
        result = download_report_for_month(
            mock_session, config, "contractors", _test_period()
        )

    assert result.success is True
    assert not stale.exists()
    helper.assert_called_once()


def test_stage_timeout_maps_to_stable_error_code(tmp_path, mock_session):
    from app.downloaders import _StageTimeout, download_report_for_month

    with (
        patch("app.downloaders._apply_search"),
        patch("app.downloaders.sleep"),
        patch(
            "app.downloaders._download_via_history",
            side_effect=_StageTimeout("export_rows"),
        ),
    ):
        result = download_report_for_month(
            mock_session, _test_config(tmp_path), "dds_expenses", _test_period()
        )

    assert result.success is False
    assert result.error is not None
    assert result.error_code == "export_row_timeout"
    assert result.error_stage == "export_rows"
    assert result.error_message == "timeout stage: export_rows"


def test_playwright_error_maps_to_stable_error_code(tmp_path, mock_session):
    from playwright.sync_api import Error as PlaywrightError

    from app.downloaders import download_report_for_month

    with (
        patch("app.downloaders._apply_search"),
        patch("app.downloaders.sleep"),
        patch(
            "app.downloaders._download_via_history",
            side_effect=PlaywrightError("browser closed"),
        ),
    ):
        result = download_report_for_month(
            mock_session, _test_config(tmp_path), "dds_expenses", _test_period()
        )

    assert result.success is False
    assert result.error is not None
    assert result.error_code == "playwright_error"
    assert result.error_stage == "history"
    assert result.error_message == "playwright error: browser closed"


def test_unknown_exception_maps_to_unknown_error_code(tmp_path, mock_session):
    from app.downloaders import download_report_for_month

    with (
        patch("app.downloaders._apply_search"),
        patch("app.downloaders.sleep"),
        patch(
            "app.downloaders._download_via_history",
            side_effect=ValueError("unexpected failure"),
        ),
    ):
        result = download_report_for_month(
            mock_session, _test_config(tmp_path), "dds_expenses", _test_period()
        )

    assert result.success is False
    assert result.error is not None
    assert result.error_code == "unknown"
    assert result.error_stage == "history"
    assert result.error_message == "unexpected failure"


def test_download_result_keeps_backward_compatible_error_string(tmp_path, mock_session):
    from app.downloaders import download_report_for_month

    with (
        patch("app.downloaders._apply_search"),
        patch("app.downloaders.sleep"),
        patch(
            "app.downloaders._download_via_history",
            side_effect=RuntimeError("Downloaded file is empty"),
        ),
    ):
        result = download_report_for_month(
            mock_session, _test_config(tmp_path), "dds_expenses", _test_period()
        )

    assert result.success is False
    assert result.error == "dds_expenses:2025-01:Downloaded file is empty"
    assert result.error_code == "empty_file"
    assert result.error_message == "Downloaded file is empty"
