"""Playwright UI primitives for Herm Finance export flows."""

from __future__ import annotations

from typing import Callable

from playwright.sync_api import Page


def click_export(page: Page) -> None:
    try:
        page.get_by_role("button", name="Экспортировать всё").click(timeout=5000)
        return
    except Exception:  # noqa: BLE001
        pass
    candidates = [
        "div.dx-datagrid-export-button[aria-label='Экспортировать всё']",
        ".dx-datagrid-export-button",
        "[aria-label='Экспортировать всё']",
        "[title='Экспортировать всё']",
        "button:has-text('Скачать')",
        "button:has-text('Export')",
        "button:has-text('Экспорт')",
        "[data-testid*='export']",
        "a:has-text('Export')",
        "a:has-text('Экспорт')",
        "a:has-text('Скачать')",
    ]
    last_error: Exception | None = None
    for selector in candidates:
        try:
            page.locator(selector).first.click(timeout=5000)
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError("Export button not found") from last_error


def enter_export_marker(page: Page, marker: str) -> None:
    popover = page.locator(".el-popover.export-popper-class").filter(has_text="Имя файла можно изменить").first
    popover.wait_for(state="visible", timeout=5000)
    popover.locator("input.el-input__inner").first.fill(marker, timeout=3000)
    popover.locator("button.el-button:has-text('Загрузить')").first.click(timeout=3000)


def download_first_exported_file(page: Page, timeout_ms: int, step: Callable[[str], None]):
    """Open the export history panel and click the first ready download button."""
    step("files list start")
    page.locator("button.files-button").click(timeout=5000)
    files_popover = page.locator(
        "div[role='tooltip'].el-popover.el-popper[aria-hidden='false']"
    ).filter(has=page.locator("button.download-button")).first
    # DevExtreme renders each row twice: once in the scrollable area (dx-hidden-cell, hidden)
    # and once in the fixed-column overlay (visible). Select only the visible copy.
    btn = files_popover.locator("td:not(.dx-hidden-cell) button.download-button").first
    btn.wait_for(state="visible", timeout=timeout_ms)
    step("files list done")
    with page.expect_download(timeout=timeout_ms) as download_info:
        step("file download start")
        btn.click(timeout=5000)
    step("file download done")
    return download_info.value
