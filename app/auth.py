"""Session reuse and manual login flow."""

from __future__ import annotations

import logging
import json
import time
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

from .browser import (
    BrowserSession,
    close_browser_session,
    create_browser_session,
    safe_base_url,
)
from .config import AppConfig

logger = logging.getLogger(__name__)


def _read_cookies(session_file: Path) -> list[dict]:
    try:
        return json.loads(session_file.read_text(encoding="utf-8")).get("cookies", [])
    except Exception:
        return []


def _session_cookies_valid(session_file: Path) -> bool:
    now = time.time()
    for cookie in _read_cookies(session_file):
        name: str = cookie.get("name", "")
        exp: float = cookie.get("expires", -1)
        if "session" in name and exp > 0 and exp < now:
            logger.info(
                "auth | session cookie '%s' expired at %s, re-authentication required",
                name,
                exp,
            )
            return False
    return True


def _remember_token_valid(session_file: Path) -> bool:
    now = time.time()
    for cookie in _read_cookies(session_file):
        name: str = cookie.get("name", "")
        exp: float = cookie.get("expires", -1)
        if name.startswith("remember_web") and (exp < 0 or exp > now):
            return True
    return False


def load_session_state(session_file: Path) -> bool:
    return (
        session_file.exists()
        and session_file.stat().st_size > 0
        and _session_cookies_valid(session_file)
    )



def save_session_state(session: BrowserSession, session_file: Path) -> None:
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session.context.storage_state(path=str(session_file))


def _is_logged_in(page: Page, base_url: str) -> bool:
    page.goto(base_url, wait_until="domcontentloaded")
    content = page.content().lower()
    url = page.url.lower()
    if "/login" in url or page.locator("input[name='email']").count() > 0:
        return False
    if any(marker in content for marker in ("logout", "выход")):
        return True
    return urljoin(base_url, "/") in page.url or "herm.finance" in page.url


def ensure_logged_in(config: AppConfig) -> BrowserSession:
    base_url = safe_base_url(config.base_url)
    stored_state = (
        config.session_file if load_session_state(config.session_file) else None
    )

    if stored_state is not None:
        session = create_browser_session(config)
        try:
            # Recreate the context with persisted state if available.
            session.context.close()
            session.context = session.browser.new_context(
                accept_downloads=True, storage_state=str(stored_state)
            )
            session.context.set_default_timeout(config.timeout_ms)
            session.page = session.context.new_page()
            if _is_logged_in(session.page, base_url):
                logger.info("auth | session loaded")
                return session
            logger.info("auth | saved session invalid, falling back to manual login")
        except PlaywrightError:
            close_browser_session(session)
            raise
        except Exception:
            close_browser_session(session)
            raise
        close_browser_session(session)

    manual_config = AppConfig(
        start_date=config.start_date,
        base_url=config.base_url,
        download_dir=config.download_dir,
        session_file=config.session_file,
        headless=False,
        overwrite=config.overwrite,
        timeout_ms=config.timeout_ms,
        slow_mo=config.slow_mo,
        repeat_each_month=config.repeat_each_month,
        config_path=config.config_path,
    )
    session = create_browser_session(manual_config)
    session.page.goto(base_url, wait_until="domcontentloaded")
    logger.info("auth | please login manually in the opened browser")
    session.page.bring_to_front()
    input("After completing login in the browser, press Enter here to continue...")
    if not _is_logged_in(session.page, base_url):
        close_browser_session(session)
        raise RuntimeError("Login was not detected after manual sign-in.")
    save_session_state(session, config.session_file)
    logger.info("auth | session saved")
    return session
