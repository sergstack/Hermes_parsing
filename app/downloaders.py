"""Report download routines."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from time import sleep
from typing import Callable
import signal

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from .browser import BrowserSession
from .config import AppConfig
from .dates import MonthPeriod
from .export_api import (
    load_export_rows as _load_export_rows,
    download_export_file as _download_export_file,
    poll_ready_export_row as _poll_ready_export_row,
    request_json as _request_json,
    step as _step,
    trigger_async_export as _trigger_async_export,
)
from .export_files import (
    determine_extension as _determine_extension,
    move_latest_download as _move_latest_download,
    move_download as _move_download,
    save_export_bytes as _save_export_bytes,
)
from .selectors import (
    DOWNLOAD_BUTTON_SELECTOR,
    EXPORT_BUTTON_SELECTORS,
    EXPORT_POPOVER_SELECTOR,
    EXPORT_POPUP_INPUT_SELECTOR,
    EXPORT_POPUP_UPLOAD_SELECTOR,
    FILES_BUTTON_SELECTOR,
    FILES_TOOLTIP_SELECTOR,
    LOAD_PANEL_SELECTOR,
    RESERVES_OPTION_SELECTOR,
    RESERVES_SELECT_SELECTOR,
    SHOW_BUTTON_SEARCH_SELECTOR,
    SHOW_BUTTON_SELECTOR,
    VISIBLE_DOWNLOAD_SELECTOR,
)
from .paths import (
    build_output_path,
    ensure_dir,
    existing_output_paths,
    normalize_download_name,
)
from .reports import REPORT_DEFINITIONS

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DownloadResult:
    success: bool
    output_path: Path | None
    error: str | None = None


def _click_export(page: Page) -> None:
    last_error: Exception | None = None
    for selector in EXPORT_BUTTON_SELECTORS:
        try:
            page.locator(selector).first.click(timeout=5000)
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError("Export button not found") from last_error


def _enter_export_marker(page: Page, marker: str) -> None:
    popover = (
        page.locator(EXPORT_POPOVER_SELECTOR)
        .filter(has_text="Имя файла можно изменить")
        .first
    )
    popover.wait_for(state="visible", timeout=5000)
    popover.locator(EXPORT_POPUP_INPUT_SELECTOR).first.fill(marker, timeout=3000)
    popover.locator(EXPORT_POPUP_UPLOAD_SELECTOR).first.click(timeout=3000)


def _set_reserves_filter(page: Page, value: str) -> None:
    page.locator(RESERVES_SELECT_SELECTOR).nth(8).click(timeout=5000)
    page.wait_for_timeout(500)
    page.locator(RESERVES_OPTION_SELECTOR).filter(has_text=value).last.click(
        timeout=5000
    )
    page.wait_for_timeout(300)


def _set_select_value_by_label(page: Page, label_text: str, value: str) -> None:
    form_item = page.locator(".el-form-item").filter(has_text=label_text).first
    form_item.locator(".el-select").first.click(timeout=5000)
    page.locator(RESERVES_OPTION_SELECTOR).filter(has_text=value).last.click(
        timeout=5000
    )
    page.wait_for_timeout(300)


def _set_checkbox_by_label(page: Page, label_text: str, checked: bool) -> None:
    form_item = page.locator(".el-form-item").filter(has_text=label_text).first
    checkbox = form_item.locator("input[type='checkbox']").first
    if checked:
        checkbox.check(timeout=5000)
    else:
        checkbox.uncheck(timeout=5000)
    page.wait_for_timeout(200)


def _set_single_date_by_label(page: Page, label_text: str, value: str) -> None:
    form_item = page.locator(".el-form-item").filter(has_text=label_text).first
    inputs = form_item.locator("input")
    inputs.first.focus(timeout=10000)
    page.keyboard.press("Control+A")
    inputs.first.fill(value, timeout=3000)
    page.wait_for_timeout(200)


def _set_date_range_by_label(page: Page, label_text: str, start: str, end: str) -> None:
    """Fill an Element-UI date-range picker that sits next to a label containing *label_text*.

    Strategy:
      1. Find the .el-form-item whose label contains *label_text*.
      2. Inside it, locate the two .el-range-input fields (start / end).
      3. Triple-click each field to select any existing value, then type the new date.
      4. Press Tab to confirm and close the calendar.

    Date strings must be in the format the UI expects, e.g. "DD.MM.YYYY" or "YYYY-MM-DD" —
    pass whichever format herm.finance accepts (verified on first live run).
    """
    # Wait for the page to settle before interacting with the date picker.
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:  # noqa: BLE001
        pass
    form_item = page.locator(".el-form-item").filter(has_text=label_text).first
    inputs = form_item.locator("input.el-range-input")
    # Start date — use focus() instead of click() to avoid triggering adjacent pickers
    inputs.nth(0).focus(timeout=10000)
    page.keyboard.press("Control+A")
    inputs.nth(0).fill(start, timeout=3000)
    page.wait_for_timeout(200)
    # End date
    inputs.nth(1).focus(timeout=10000)
    page.keyboard.press("Control+A")
    inputs.nth(1).fill(end, timeout=3000)
    page.wait_for_timeout(200)
    # Close the calendar popup before clicking «Показать».
    # Escape alone is unreliable — combine with a mouse click far from the picker.
    page.keyboard.press("Escape")
    page.wait_for_timeout(150)
    # Click top-left corner (outside any panel) to blur the picker and dismiss the calendar.
    page.mouse.click(4, 4)
    page.wait_for_timeout(300)


def _apply_search(
    page: Page,
    timeout_ms: int,
    done_selector: str | None = LOAD_PANEL_SELECTOR,
    pre_wait_ms: int = 0,
    reserves_filter_value: str | None = None,
    payment_date: tuple[str, str] | None = None,
    date_filter_label: str = "Дата оплаты",
    single_date_filter: bool = False,
    select_filters: tuple[tuple[str, str], ...] = (),
    checkbox_filters: tuple[tuple[str, bool], ...] = (),
) -> None:
    if pre_wait_ms:
        page.wait_for_timeout(pre_wait_ms)
    if payment_date:
        if single_date_filter:
            _set_single_date_by_label(page, date_filter_label, payment_date[1])
        else:
            _set_date_range_by_label(
                page, date_filter_label, payment_date[0], payment_date[1]
            )
    for label_text, value in select_filters:
        _set_select_value_by_label(page, label_text, value)
    for label_text, checked in checkbox_filters:
        _set_checkbox_by_label(page, label_text, checked)
    if reserves_filter_value:
        _set_reserves_filter(page, reserves_filter_value)
    show_button = page.locator("button.el-button--primary.el-button--small").filter(
        has_text="Показать"
    )
    if show_button.count() == 0:
        show_button = page.locator(SHOW_BUTTON_SEARCH_SELECTOR)
    if show_button.count() == 0:
        show_button = page.locator(SHOW_BUTTON_SELECTOR)
    show_button.first.click(timeout=15000)
    if done_selector:
        page.locator(done_selector).wait_for(state="hidden", timeout=timeout_ms)
    else:
        page.wait_for_timeout(5000)


def _download_first_exported_file(page: Page, timeout_ms: int):
    """Open the export history panel and click the first ready download-button.

    DevExtreme renders each row twice (hidden duplicate + visible overlay);
    :not(.dx-hidden-cell) selects only the visible copy.
    Call this only after the target file is confirmed ready (via API poll or
    sufficient wait), so the newest entry at the top is always the right one.
    """
    _step("files list start")
    page.locator(FILES_BUTTON_SELECTOR).click(timeout=5000)
    files_popover = (
        page.locator(FILES_TOOLTIP_SELECTOR)
        .filter(has=page.locator(DOWNLOAD_BUTTON_SELECTOR))
        .first
    )
    # DevExtreme renders each row twice: once in the scrollable area (dx-hidden-cell, hidden)
    # and once in the fixed-column overlay (visible). The first N buttons in DOM order are
    # always the hidden duplicates, so we must skip them with :not(.dx-hidden-cell).
    btn = files_popover.locator(VISIBLE_DOWNLOAD_SELECTOR).first
    btn.wait_for(state="visible", timeout=timeout_ms)
    _step("files list done")
    with page.expect_download(timeout=timeout_ms) as download_info:
        _step("file download start")
        btn.click(timeout=5000)
    _step("file download done")
    return download_info.value


def _wait_for_export_ready_by_name(
    session: BrowserSession,
    base_url: str,
    expected_name: str,
    timeout_ms: int,
    min_id: int = 0,
) -> None:
    """Poll /api/resources/export-file/all until a row whose name contains
    *expected_name* appears with status 'ready' and id > min_id.

    Raises RuntimeError on timeout.  Used before opening the history panel so we
    always click the correct (newly created) file and not a stale older one.
    """
    poll_interval_ms = 3000
    waited_ms = 0
    while waited_ms <= timeout_ms:
        rows = _load_export_rows(session, base_url)
        for row in rows:
            row_id = int(row.get("id", 0))
            if row_id <= min_id:
                continue
            name = row.get("original_file_name") or row.get("file_name") or ""
            status = row.get("status_id", "")
            if expected_name in name:
                logger.info(
                    "download | api-poll | '%s' status=%s id=%s", name, status, row_id
                )
                if status == "ready":
                    _step(f"api-poll ready: {name}")
                    return
                if status == "fail":
                    raise RuntimeError(
                        f"Export '{name}' failed on server (status=fail)"
                    )
        logger.info(
            "download | api-poll | '%s' not ready yet, waited %sms",
            expected_name,
            waited_ms,
        )
        session.page.wait_for_timeout(poll_interval_ms)
        waited_ms += poll_interval_ms
    raise RuntimeError(
        f"Export '{expected_name}' did not become ready within {timeout_ms}ms"
    )


class _StageTimeout(Exception):
    def __init__(self, stage: str) -> None:
        super().__init__(stage)
        self.stage = stage


def _run_with_timeout(
    stage: str,
    timeout_ms: int,
    fn: Callable[[], Path | dict | tuple[bytes, str] | None],
):
    def handler(signum, frame):  # noqa: ARG001
        raise _StageTimeout(stage)

    previous = signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, max(timeout_ms / 1000, 0.001))
    try:
        return fn()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def _trigger_export_with_marker(page: Page, marker: str) -> None:
    """Click the export button, fill the filename popover, and click «Загрузить».

    This only *triggers* the server-side export job — it does NOT wait for the
    file to be ready.  Use _wait_for_export_ready_by_name + _download_from_history
    afterwards to confirm readiness and pull the file.
    """
    _step("export click start")
    _click_export(page)
    _step("export click done")
    _step("export marker start")
    page.wait_for_timeout(300)
    _enter_export_marker(page, marker)
    _step("export marker done")


def _download_from_history(
    page: Page, target_dir: Path, output_path: Path, timeout_ms: int
) -> Path:
    """Open the history panel and download the first (newest) ready file."""
    download = _download_first_exported_file(page, timeout_ms)
    suggested = normalize_download_name(download.suggested_filename)
    ext = _determine_extension(suggested, download.url)
    final_path = output_path.with_suffix(ext)
    if final_path != output_path:
        output_path = final_path
    tmp_path = target_dir / f"_tmp_{suggested}"
    download.save_as(str(tmp_path))
    _move_download(tmp_path, output_path)
    if output_path.stat().st_size == 0:
        raise RuntimeError("Downloaded file is empty")
    return output_path


def _wait_for_new_export_row(
    session: "BrowserSession",
    base_url: str,
    before_max_id: int,
    timeout_ms: int,
) -> None:
    """Poll /api/resources/export-file/all until a new row with id > before_max_id has status 'ready'."""
    poll_interval_ms = 3000
    waited_ms = 0
    while waited_ms <= timeout_ms:
        rows = _load_export_rows(session, base_url)
        for row in rows:
            row_id = int(row.get("id", 0))
            if row_id <= before_max_id:
                continue
            status = row.get("status_id", "")
            name = row.get("original_file_name") or row.get("file_name") or ""
            if status == "ready":
                _step(f"api-poll ready: id={row_id} name={name}")
                return
            if status == "fail":
                raise RuntimeError(f"Export id={row_id} failed on server (status=fail)")
        logger.info("download | api-poll | no new ready row yet, waited %sms", waited_ms)
        session.page.wait_for_timeout(poll_interval_ms)
        waited_ms += poll_interval_ms
    raise RuntimeError(f"No new export row became ready within {timeout_ms}ms")


def _save_download(
    page: Page,
    target_dir: Path,
    output_path: Path,
    timeout_ms: int,
    wait_after_export_ms: int = 5000,
    via_history: bool = False,
    session: "BrowserSession | None" = None,
    base_url: str = "",
    before_max_id: int = 0,
) -> Path:
    """Trigger export via UI and save the file.

    via_history=True  — click export → wait for new export row via API → history panel → first button.
    via_history=False — click export → browser download dialog.

    For marker-based exports (applications, budget_rows) use
    _trigger_export_with_marker + _wait_for_export_ready_by_name +
    _download_from_history directly in download_report_for_month.
    """
    logger.info("download | waiting for export")
    if via_history:
        _step("export click start")
        _click_export(page)
        _step("export click done")
        if session and base_url:
            _wait_for_new_export_row(session, base_url, before_max_id, timeout_ms)
        else:
            page.wait_for_timeout(wait_after_export_ms)
        download = _download_first_exported_file(page, timeout_ms)
    else:
        with page.expect_download(timeout=timeout_ms) as download_info:
            _step("export click start")
            _click_export(page)
            _step("export click done")
        download = download_info.value
    suggested = normalize_download_name(download.suggested_filename)
    ext = _determine_extension(suggested, download.url)
    final_path = output_path.with_suffix(ext)
    if final_path != output_path:
        output_path = final_path
    tmp_path = target_dir / f"_tmp_{suggested}"
    download.save_as(str(tmp_path))
    _move_download(tmp_path, output_path)
    if output_path.stat().st_size == 0:
        raise RuntimeError("Downloaded file is empty")
    return output_path


def _save_latest_browser_download(output_path: Path) -> Path:
    downloads_dir = Path.home() / "Downloads"
    return _move_latest_download(downloads_dir, output_path, "*.xlsx")


def log_result(
    report_code: str, period: MonthPeriod | str, status: str, details: str = ""
) -> None:
    label = period.label if isinstance(period, MonthPeriod) else period
    suffix = f" -> {details}" if details else ""
    logger.info("%s | %s | %s%s", report_code, label, status, suffix)


def download_report_for_month(
    session: BrowserSession,
    config: AppConfig,
    report_code: str,
    month_period: MonthPeriod,
) -> DownloadResult:
    report = REPORT_DEFINITIONS[report_code]
    page = session.page
    target_dir = ensure_dir(config.download_dir / report.export_dir)
    url = report.build_url(config.base_url.rstrip("/"), month_period)
    use_end_date = not report.append_month_to_filename and report.export_via_history and report.payment_date_filter and report.single_date_filter
    export_file_name = (
        f"{report.file_prefix}_{month_period.label}.xlsx"
        if report.append_month_to_filename
        else f"{report.file_prefix}.xlsx"
    )
    output_path = build_output_path(
        config.download_dir,
        report.export_dir,
        month_period,
        ".xlsx",
        report.file_prefix,
        use_end_date=use_end_date,
    )
    if not report.append_month_to_filename and not use_end_date:
        output_path = output_path.with_name(f"{report.file_prefix}.xlsx")
    # Reports with use_export_marker=True open a filename popover after clicking export;
    # we fill it with "{file_prefix}_{YYYY-MM}" and then download via the history panel.
    export_marker = None
    if report.use_export_marker:
        export_marker = (
            f"{report.file_prefix}_{month_period.label}"
            if report.append_month_to_filename
            else report.file_prefix
        )

    for attempt in range(1, 4):
        try:
            log_result(report_code, month_period, "started")
            existing = existing_output_paths(
                config.download_dir, report.export_dir, month_period
            )
            if report.code == "contractors" and existing:
                for path in existing:
                    path.unlink()
                existing = []
            if existing and not config.overwrite:
                log_result(
                    report_code, month_period, "skipped", f"exists -> {existing[0]}"
                )
                return DownloadResult(True, existing[0])
            logger.info("%s | %s | opening -> %s", report_code, month_period.label, url)
            _step("page open start")
            page.goto(url, wait_until="domcontentloaded")
            _step("page open done")
            if report.apply_search_before_export:
                _step("apply search start")
                # herm.finance date-range picker uses DD.MM.YY (two-digit year).
                payment_date = (
                    (
                        month_period.start.strftime("%d.%m.%y"),
                        month_period.end.strftime("%d.%m.%y"),
                    )
                    if report.payment_date_filter
                    else None
                )
                _apply_search(
                    page,
                    config.timeout_ms,
                    report.search_done_selector,
                    report.pre_search_wait_ms,
                    report.reserves_filter_value,
                    payment_date=payment_date,
                    date_filter_label=report.date_filter_label,
                    single_date_filter=report.single_date_filter,
                    select_filters=report.select_filters,
                    checkbox_filters=report.checkbox_filters,
                )
                _step("apply search done")
            if report.export_endpoint:
                base_url = config.base_url.rstrip("/")
                if not page.url.startswith(base_url):
                    page.goto(base_url, wait_until="domcontentloaded")
                _step("fetch export rows before trigger start")
                before_rows = _load_export_rows(session, base_url)
                _step("fetch export rows before trigger done")
                before_max_id = max(
                    (int(row.get("id", 0)) for row in before_rows), default=0
                )
                try:
                    _step("trigger start")
                    _run_with_timeout(
                        "trigger",
                        config.timeout_ms,
                        lambda: _trigger_async_export(
                            session,
                            f"{base_url}{report.export_endpoint}",
                            export_file_name,
                        ),
                    )
                    _step("trigger done")
                except Exception as exc:  # noqa: BLE001
                    # Known behavior: some Herm Finance reports return 500 on trigger, but the export row
                    # still appears in /api/resources/export-file/all and can be downloaded from there.
                    logger.warning(
                        "%s | %s | trigger failed -> %s",
                        report_code,
                        month_period.label,
                        exc,
                    )
                _step("fetch status start")
                _run_with_timeout(
                    "status",
                    config.timeout_ms,
                    lambda: _request_json(
                        session, "GET", f"{base_url}/api/export_files/status"
                    ),
                )
                _step("fetch status done")
                _step("poll new row start")
                row = _run_with_timeout(
                    "export_rows",
                    config.timeout_ms,
                    lambda: _poll_ready_export_row(
                        session,
                        base_url,
                        export_file_name,
                        config.timeout_ms,
                        before_max_id,
                        report.export_ready_name,
                    ),
                )
                _step("poll new row done")
                _step("download start")
                body, disposition = _run_with_timeout(
                    "download",
                    config.timeout_ms,
                    lambda: _download_export_file(session, base_url, row["id"]),
                )
                _step("download done")
                _step("save file start")
                saved_path = _save_export_bytes(output_path, body, disposition)
                _step("save file done")
            else:
                if export_marker:
                    # Marker flow (applications, budget_rows):
                    #   1. Record max export ID before triggering.
                    #   2. Click export → enter filename in popover → «Загрузить».
                    #   3. API-poll until our specific file is ready (avoids clicking
                    #      a stale older file that was already in the history panel).
                    #   4. Open history panel → click first (newest) download button.
                    base_url = config.base_url.rstrip("/")
                    before_rows = _load_export_rows(session, base_url)
                    before_max_id = max(
                        (int(r.get("id", 0)) for r in before_rows), default=0
                    )
                    _trigger_export_with_marker(page, export_marker)
                    _wait_for_export_ready_by_name(
                        session,
                        base_url,
                        export_marker,
                        config.timeout_ms,
                        min_id=before_max_id,
                    )
                    saved_path = _download_from_history(
                        page, target_dir, output_path, config.timeout_ms
                    )
                else:
                    if report.export_via_history:
                        _via_base_url = config.base_url.rstrip("/")
                        _via_before_rows = _load_export_rows(session, _via_base_url)
                        _via_before_max_id = max(
                            (int(r.get("id", 0)) for r in _via_before_rows), default=0
                        )
                    else:
                        _via_base_url = ""
                        _via_before_max_id = 0
                    saved_path = _save_download(
                        page,
                        target_dir,
                        output_path,
                        config.timeout_ms,
                        report.wait_after_export_ms,
                        report.export_via_history,
                        session=session if report.export_via_history else None,
                        base_url=_via_base_url,
                        before_max_id=_via_before_max_id,
                    )
            log_result(report_code, month_period, "saved", str(saved_path))
            return DownloadResult(True, saved_path)
        except PlaywrightTimeoutError as exc:
            logger.warning(
                "%s | %s | timeout attempt %s", report_code, month_period.label, attempt
            )
            last_error = f"timeout: {exc}"
        except PlaywrightError as exc:
            last_error = f"playwright error: {exc}"
        except _StageTimeout as exc:
            last_error = f"timeout stage: {exc.stage}"
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)

        if attempt < 3:
            sleep(2 * attempt)
            continue
        contextual_error = f"{report_code}:{month_period.label}:{last_error}"
        log_result(report_code, month_period, "error", contextual_error)
        return DownloadResult(False, None, contextual_error)

    return DownloadResult(
        False, None, f"{report_code}:{month_period.label}:unknown error"
    )
