"""Centralized UI selectors for fragile Herm Finance flows."""

from __future__ import annotations

# These selectors are intentionally kept in one place because they are brittle
# contracts with the Herm Finance UI and should be reviewed together.
EXPORT_BUTTON_SELECTORS = [
    "button:has-text('Скачать')",
    ".dx-datagrid-export-button",
    "[aria-label='Экспортировать всё']",
    "button:has-text('Export')",
    "button:has-text('Экспорт')",
    "[data-testid*='export']",
    "a:has-text('Export')",
    "a:has-text('Экспорт')",
    "a:has-text('Скачать')",
]
EXPORT_POPOVER_SELECTOR = ".el-popover.export-popper-class"
EXPORT_POPUP_INPUT_SELECTOR = "input.el-input__inner"
EXPORT_POPUP_UPLOAD_SELECTOR = "button.el-button:has-text('Загрузить')"
RESERVES_SELECT_SELECTOR = ".el-select"
RESERVES_OPTION_SELECTOR = ".el-select-dropdown__item"
SHOW_BUTTON_SELECTOR = "button.el-button--primary.el-button--small"
SHOW_BUTTON_SEARCH_SELECTOR = "button.el-button--primary.el-button--small:not(.input-button):has(i.el-icon-search)"
SHOW_BUTTON_TEXT_SELECTOR = "button:has-text('Показать')"
LOAD_PANEL_SELECTOR = ".dx-loadpanel-content"
FILES_BUTTON_SELECTOR = "button.files-button"
FILES_TOOLTIP_SELECTOR = "div[role='tooltip'].el-popover.el-popper[aria-hidden='false']"
DOWNLOAD_BUTTON_SELECTOR = "button.download-button"
VISIBLE_DOWNLOAD_SELECTOR = "td:not(.dx-hidden-cell) button.download-button"
