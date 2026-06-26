"""Report download routines."""

from __future__ import annotations

import logging
import json
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
from .export_history import (
    candidate_export_names as _candidate_export_names,
    poll_ready_export_row,
    wait_for_export_ready_by_name,
)
from .export_flows import (
    click_export,
    download_first_exported_file,
    enter_export_marker,
)
from .output_writer import (
    determine_extension as _determine_extension,
    move_download as _move_download,
    repair_xlsx_dimension as _repair_xlsx_dimension,
    save_export_bytes as _save_export_bytes,
)
from .paths import build_output_path, ensure_dir, existing_output_paths, normalize_download_name
from .reports import REPORT_DEFINITIONS

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DownloadResult:
    success: bool
    output_path: Path | None
    error: str | None = None


@dataclass(frozen=True)
class ReportOutputTarget:
    export_file_name: str
    output_path: Path
    export_marker: str | None


def resolve_report_output_target(
    download_dir: Path,
    report_code: str,
    month_period: MonthPeriod,
) -> ReportOutputTarget:
    report = REPORT_DEFINITIONS[report_code]
    target_dir = download_dir / report.export_dir
    if report.repeat_each_month:
        export_file_name = f"{report.file_prefix}_{month_period.label}.xlsx"
        output_path = build_output_path(download_dir, report.export_dir, month_period, ".xlsx", report.file_prefix)
    else:
        export_file_name = f"{report.file_prefix}.xlsx"
        output_path = target_dir / export_file_name

    if report_code == "account_balances":
        export_file_name = f"acc_balance_{month_period.end:%Y-%m-%d}.xlsx"
        output_path = target_dir / export_file_name
    if report_code == "cons_budget":
        export_file_name = "cons_budget.xlsx"
        output_path = target_dir / export_file_name

    export_marker = f"{report.file_prefix}_{month_period.label}" if report.use_export_marker else None
    return ReportOutputTarget(export_file_name, output_path, export_marker)


def _click_export(page: Page) -> None:
    click_export(page)


def _enter_export_marker(page: Page, marker: str) -> None:
    enter_export_marker(page, marker)


def _set_reserves_filter(page: Page, value: str) -> None:
    page.locator(".el-select").nth(8).click(timeout=5000)
    page.wait_for_timeout(500)
    page.locator(".el-select-dropdown__item").filter(has_text=value).last.click(timeout=5000)
    page.wait_for_timeout(300)


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
    inputs.first.wait_for(state="visible", timeout=10000)

    for index, value in ((0, start), (1, end)):
        field = inputs.nth(index)
        field.click(timeout=10000)
        field.fill(value, timeout=3000)
        field.evaluate(
            """(el, value) => {
                const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                setter.call(el, value);
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.blur();
            }""",
            value,
        )
        page.wait_for_timeout(200)

    # Close the calendar popup before clicking «Показать».
    # Escape alone is unreliable — combine with a mouse click far from the picker.
    page.keyboard.press("Escape")
    page.wait_for_timeout(150)
    # Click top-left corner (outside any panel) to blur the picker and dismiss the calendar.
    page.mouse.click(4, 4)
    page.wait_for_timeout(300)

    actual_start = inputs.nth(0).input_value(timeout=3000)
    actual_end = inputs.nth(1).input_value(timeout=3000)
    if actual_start != start or actual_end != end:
        raise RuntimeError(
            f"Date filter '{label_text}' was not applied: "
            f"expected {start} - {end}, got {actual_start!r} - {actual_end!r}"
        )


def _set_single_date_by_label(page: Page, label_text: str, date_str: str) -> None:
    """Fill a single Element-UI date input next to a label containing *label_text*."""
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:  # noqa: BLE001
        pass
    form_item = page.locator(".el-form-item").filter(has_text=label_text).first
    field = form_item.locator("input.el-input__inner").first
    field.wait_for(state="visible", timeout=10000)
    field.click(timeout=10000)
    field.fill(date_str, timeout=3000)
    field.evaluate(
        """(el, value) => {
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
            setter.call(el, value);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            el.blur();
        }""",
        date_str,
    )
    page.wait_for_timeout(200)
    page.keyboard.press("Escape")
    page.wait_for_timeout(150)
    page.mouse.click(4, 4)
    page.wait_for_timeout(300)

    actual = field.input_value(timeout=3000)
    if actual != date_str:
        raise RuntimeError(
            f"Date filter '{label_text}' was not applied: expected {date_str}, got {actual!r}"
        )


def _clear_checked_boxes_by_label(page: Page, labels: tuple[str, ...]) -> None:
    for label in labels:
        form_item = page.locator(".el-form-item").filter(has_text=label).first
        checked_box = form_item.locator(".el-checkbox__input.is-checked").first
        if checked_box.count() > 0:
            checked_box.click(timeout=5000)
            page.wait_for_timeout(100)


def _clear_text_inputs_by_label(page: Page, labels: tuple[str, ...]) -> None:
    for label in labels:
        form_item = page.locator(".el-form-item").filter(has_text=label).first
        inputs = form_item.locator("input.el-input__inner")
        for index in range(inputs.count()):
            field = inputs.nth(index)
            field.fill("", timeout=3000)
            field.evaluate(
                """(el) => {
                    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                    setter.call(el, '');
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.blur();
                }"""
            )
            page.wait_for_timeout(100)


def _set_select_filters_by_label(page: Page, filters: tuple[tuple[str, str], ...]) -> None:
    for label, value in filters:
        form_item = page.locator(".el-form-item").filter(has_text=label).first
        form_item.locator(".el-select").first.click(timeout=5000)
        page.wait_for_timeout(500)
        page.locator(".el-select-dropdown__item").filter(has_text=value).last.click(timeout=5000)
        page.wait_for_timeout(300)


def _apply_search(
    page: Page,
    timeout_ms: int,
    done_selector: str | None = ".dx-loadpanel-content",
    pre_wait_ms: int = 0,
    reserves_filter_value: str | None = None,
    payment_date: tuple[str, str] | None = None,
    date_filter_label: str = "Дата оплаты",
    clear_checkbox_labels: tuple[str, ...] = (),
    clear_text_input_labels: tuple[str, ...] = (),
    select_filters: tuple[tuple[str, str], ...] = (),
    single_date: str | None = None,
) -> None:
    if pre_wait_ms:
        page.wait_for_timeout(pre_wait_ms)
    if single_date:
        _set_single_date_by_label(page, date_filter_label, single_date)
    if payment_date:
        _set_date_range_by_label(page, date_filter_label, payment_date[0], payment_date[1])
    if clear_checkbox_labels:
        _clear_checked_boxes_by_label(page, clear_checkbox_labels)
    if clear_text_input_labels:
        _clear_text_inputs_by_label(page, clear_text_input_labels)
    if select_filters:
        _set_select_filters_by_label(page, select_filters)
    if reserves_filter_value:
        _set_reserves_filter(page, reserves_filter_value)
    show_button = page.locator("button:has-text('Показать')")
    if show_button.count() == 0:
        show_button = page.locator("button.el-button--primary.el-button--small").filter(has_text="Показать")
    if show_button.count() == 0:
        show_button = page.locator(
            "button.el-button--primary.el-button--small:not(.input-button):has(i.el-icon-search)"
        )
    if show_button.count() == 0:
        show_button = page.locator("button.el-button--primary.el-button--small")
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
    return download_first_exported_file(page, timeout_ms, _step)


def _request_json(session: BrowserSession, method: str, url: str, payload: dict | None = None) -> dict:
    body = session.page.evaluate(
        """async ({ method, url, payload }) => {
            const headers = { 'X-Requested-With': 'XMLHttpRequest' };
            const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            const xsrf = decodeURIComponent((document.cookie.match(/XSRF-TOKEN=([^;]+)/) || [])[1] || '');
            if (token) headers['X-CSRF-TOKEN'] = token;
            if (xsrf) headers['X-XSRF-TOKEN'] = xsrf;
            if (method === 'POST') headers['Content-Type'] = 'application/json';
            const response = await fetch(url, {
                method,
                credentials: 'include',
                headers,
                body: method === 'POST' ? JSON.stringify(payload ?? {}) : undefined,
            });
            return {
                status: response.status,
                text: await response.text(),
            };
        }""",
        {"method": method, "url": url, "payload": payload},
    )
    if body["status"] >= 400:
        raise RuntimeError(f"{method} {url} -> {body['status']}: {body['text'][:200]}")
    try:
        return json.loads(body["text"]) if body["text"] else {}
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"{method} {url} did not return JSON") from exc


def _request_bytes(session: BrowserSession, method: str, url: str) -> tuple[bytes, dict[str, str]]:
    body = session.page.evaluate(
        """async ({ method, url }) => {
            const headers = { 'X-Requested-With': 'XMLHttpRequest' };
            const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            const xsrf = decodeURIComponent((document.cookie.match(/XSRF-TOKEN=([^;]+)/) || [])[1] || '');
            if (token) headers['X-CSRF-TOKEN'] = token;
            if (xsrf) headers['X-XSRF-TOKEN'] = xsrf;
            const response = await fetch(url, {
                method,
                credentials: 'include',
                headers,
            });
            const buffer = await response.arrayBuffer();
            let binary = '';
            const bytes = new Uint8Array(buffer);
            const chunkSize = 0x8000;
            for (let i = 0; i < bytes.length; i += chunkSize) {
                binary += String.fromCharCode(...bytes.subarray(i, i + chunkSize));
            }
            return {
                status: response.status,
                headers: Object.fromEntries(response.headers.entries()),
                data: btoa(binary),
                text: bytes.length < 1024 ? new TextDecoder().decode(buffer) : '',
            };
        }""",
        {"method": method, "url": url},
    )
    if body["status"] >= 400:
        raise RuntimeError(f"{method} {url} -> {body['status']}: {body.get('text', '')[:200]}")
    import base64

    headers = {k.lower(): v for k, v in body["headers"].items()}
    return base64.b64decode(body["data"]), headers


def _trigger_async_export(session: BrowserSession, export_url: str, file_name: str) -> None:
    logger.info("download | trigger export -> %s (%s)", export_url, file_name)
    _request_json(session, "POST", export_url, {"userData": {"fileName": file_name}})


def _load_export_rows(session: BrowserSession, base_url: str) -> list[dict]:
    payload = _request_json(session, "POST", f"{base_url}/api/resources/export-file/all", {})
    return payload.get("data", [])


def _step(label: str) -> None:
    message = f"download | step | {label}"
    print(message, flush=True)
    logger.info(message)


def _wait_for_export_ready_by_name(
    session: BrowserSession,
    base_url: str,
    expected_name: str,
    timeout_ms: int,
    min_id: int = 0,
) -> None:
    """Poll export history until the named newly created export is ready."""
    wait_for_export_ready_by_name(
        session,
        base_url,
        expected_name,
        timeout_ms,
        _load_export_rows,
        session.page.wait_for_timeout,
        min_id,
        logger.info,
        _step,
    )


class _StageTimeout(Exception):
    def __init__(self, stage: str) -> None:
        super().__init__(stage)
        self.stage = stage


def _run_with_timeout(stage: str, timeout_ms: int, fn: Callable[[], Path | dict | tuple[bytes, str] | None]):
    def handler(signum, frame):  # noqa: ARG001
        raise _StageTimeout(stage)

    previous = signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, max(timeout_ms / 1000, 0.001))
    try:
        return fn()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def _poll_ready_export_row(
    session: BrowserSession,
    base_url: str,
    file_name: str,
    timeout_ms: int,
    min_row_id: int | None = None,
    extra_name: str | None = None,
    load_rows: Callable[[BrowserSession, str], list[dict]] = _load_export_rows,
) -> dict:
    return poll_ready_export_row(
        session,
        base_url,
        file_name,
        timeout_ms,
        load_rows,
        min_row_id,
        extra_name,
        _step,
    )


def _download_export_file(session: BrowserSession, base_url: str, file_id: str | int) -> tuple[bytes, str]:
    body, headers = _request_bytes(session, "POST", f"{base_url}/api/export_files/download/{file_id}")
    return body, headers.get("content-disposition", "")


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


def _download_from_history(page: Page, target_dir: Path, output_path: Path, timeout_ms: int) -> Path:
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


def _save_download(
    page: Page,
    target_dir: Path,
    output_path: Path,
    timeout_ms: int,
    wait_after_export_ms: int = 5000,
    via_history: bool = False,
) -> Path:
    """Trigger export via UI and save the file.

    via_history=True  — click export → fixed wait → history panel → first button.
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


def log_result(report_code: str, period: MonthPeriod | str, status: str, details: str = "") -> None:
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
    output_target = resolve_report_output_target(config.download_dir, report_code, month_period)
    export_file_name = output_target.export_file_name
    output_path = output_target.output_path
    # Reports with use_export_marker=True open a filename popover after clicking export.
    export_marker = output_target.export_marker

    for attempt in range(1, 4):
        try:
            log_result(report_code, month_period, "started")
            existing = (
                existing_output_paths(config.download_dir, report.export_dir, month_period)
                if report.repeat_each_month
                else ([output_path] if output_path.exists() else [])
            )
            if existing and not config.overwrite:
                if report_code != "cons_budget":
                    log_result(report_code, month_period, "skipped", f"exists -> {existing[0]}")
                    return DownloadResult(True, existing[0])
            logger.info("%s | %s | opening -> %s", report_code, month_period.label, url)
            _step("page open start")
            page.goto(url, wait_until="domcontentloaded")
            _step("page open done")
            if report.apply_search_before_export:
                _step("apply search start")
                # herm.finance date-range picker uses DD.MM.YY (two-digit year).
                payment_date = (
                    month_period.start.strftime("%d.%m.%y"),
                    month_period.end.strftime("%d.%m.%y"),
                ) if report.payment_date_filter else None
                single_date = (
                    month_period.end.strftime("%d.%m.%y")
                ) if report.single_date_filter else None
                _apply_search(
                    page,
                    config.timeout_ms,
                    report.search_done_selector,
                    report.pre_search_wait_ms,
                    report.reserves_filter_value,
                    payment_date=payment_date,
                    date_filter_label=report.date_filter_label,
                    clear_checkbox_labels=report.clear_checkbox_labels,
                    clear_text_input_labels=report.clear_text_input_labels,
                    select_filters=report.select_filters,
                    single_date=single_date,
                )
                _step("apply search done")
            if report.export_endpoint:
                base_url = config.base_url.rstrip("/")
                if not page.url.startswith(base_url):
                    page.goto(base_url, wait_until="domcontentloaded")
                _step("fetch export rows before trigger start")
                before_rows = _load_export_rows(session, base_url)
                _step("fetch export rows before trigger done")
                before_max_id = max((int(row.get("id", 0)) for row in before_rows), default=0)
                try:
                    _step("trigger start")
                    _run_with_timeout(
                        "trigger",
                        config.timeout_ms,
                        lambda: _trigger_async_export(session, f"{base_url}{report.export_endpoint}", export_file_name),
                    )
                    _step("trigger done")
                except Exception as exc:  # noqa: BLE001
                    # Known behavior: some Herm Finance reports return 500 on trigger, but the export row
                    # still appears in /api/resources/export-file/all and can be downloaded from there.
                    logger.warning("%s | %s | trigger failed -> %s", report_code, month_period.label, exc)
                _step("fetch status start")
                _run_with_timeout("status", config.timeout_ms, lambda: _request_json(session, "GET", f"{base_url}/api/export_files/status"))
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
                body, disposition = _run_with_timeout("download", config.timeout_ms, lambda: _download_export_file(session, base_url, row["id"]))
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
                    before_max_id = max((int(r.get("id", 0)) for r in before_rows), default=0)
                    _trigger_export_with_marker(page, export_marker)
                    _wait_for_export_ready_by_name(
                        session, base_url, export_marker, config.timeout_ms, min_id=before_max_id,
                    )
                    saved_path = _download_from_history(page, target_dir, output_path, config.timeout_ms)
                else:
                    saved_path = _save_download(page, target_dir, output_path, config.timeout_ms, report.wait_after_export_ms, report.export_via_history)
            log_result(report_code, month_period, "saved", str(saved_path))
            if report_code == "account_balances" and saved_path.suffix == ".xlsx":
                _repair_xlsx_dimension(saved_path)
            return DownloadResult(True, saved_path)
        except PlaywrightTimeoutError as exc:
            logger.warning("%s | %s | timeout attempt %s", report_code, month_period.label, attempt)
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
        log_result(report_code, month_period, "error", last_error)
        return DownloadResult(False, None, last_error)

    return DownloadResult(False, None, "unknown error")
