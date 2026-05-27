"""Playwright browser bootstrap and context management."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)

from .config import AppConfig


@dataclass
class BrowserSession:
    playwright: Playwright
    browser: Browser
    context: BrowserContext
    page: Page


def safe_base_url(base_url: str) -> str:
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Invalid base_url: {base_url!r}")
    return base_url.rstrip("/")


def create_browser_session(config: AppConfig) -> BrowserSession:
    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        headless=config.headless,
        slow_mo=config.slow_mo,
        args=["--deny-permission-prompts"],
    )
    context = browser.new_context(accept_downloads=True)
    context.set_default_timeout(config.timeout_ms)
    page = context.new_page()
    return BrowserSession(playwright=pw, browser=browser, context=context, page=page)


def close_browser_session(session: BrowserSession) -> None:
    session.context.close()
    session.browser.close()
    session.playwright.stop()


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
