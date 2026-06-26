"""Session reuse and manual login flow."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import replace
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

from .browser import BrowserSession, close_browser_session, create_browser_session, safe_base_url
from .config import AppConfig

logger = logging.getLogger(__name__)


# ── Cookie inspection ─────────────────────────────────────────────────────────

def _read_cookies(session_file: Path) -> list[dict]:
    try:
        return json.loads(session_file.read_text(encoding="utf-8")).get("cookies", [])
    except Exception:
        return []


def _session_cookies_valid(session_file: Path) -> bool:
    """Return False if any session-identifying cookie is expired.

    Malformed JSON → True (let Playwright decide).
    """
    now = time.time()
    for cookie in _read_cookies(session_file):
        name: str = cookie.get("name", "")
        exp: float = cookie.get("expires", -1)
        if "session" in name and exp > 0 and exp < now:
            logger.info("auth | session cookie '%s' expired at %s, re-authentication required", name, exp)
            return False
    return True


def _remember_token_valid(session_file: Path) -> bool:
    """Return True if the long-lived remember_web cookie exists and is not expired."""
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


# ── Login detection ───────────────────────────────────────────────────────────

def _is_logged_in(page: Page, base_url: str) -> bool:
    page.goto(base_url, wait_until="domcontentloaded")
    content = page.content().lower()
    if "/login" in page.url.lower() or page.locator("input[name='email']").count() > 0:
        return False
    if any(marker in content for marker in ("logout", "выход")):
        return True
    return urljoin(base_url, "/") in page.url or "herm.finance" in page.url


# ── Headless remember_web refresh ────────────────────────────────────────────

def refresh_session_headless(config: AppConfig) -> bool:
    """Try to renew hermes_session using the long-lived remember_web cookie.

    herm.finance recognises the remember_web token and issues new session
    cookies on the first page load — no password entry needed.

    Returns True if refresh succeeded, False if the server still shows a
    login page (remember_web is invalid/expired — manual login required).
    """
    if not config.session_file.exists():
        return False
    base_url = safe_base_url(config.base_url)
    headless_config = replace(config, headless=True)
    session = create_browser_session(headless_config)
    try:
        session.context.close()
        session.context = session.browser.new_context(
            accept_downloads=True, storage_state=str(config.session_file)
        )
        session.context.set_default_timeout(config.timeout_ms)
        session.page = session.context.new_page()
        if _is_logged_in(session.page, base_url):
            save_session_state(session, config.session_file)
            logger.info("auth | session refreshed headless via remember_web token")
            return True
        logger.info("auth | headless refresh failed — remember_web token may be expired")
        return False
    except Exception as exc:
        logger.warning("auth | headless refresh error: %s", exc)
        return False
    finally:
        close_browser_session(session)


# ── Main auth entry point ─────────────────────────────────────────────────────

def ensure_logged_in(config: AppConfig) -> BrowserSession:
    base_url = safe_base_url(config.base_url)

    # 1. Session is fully valid — use it directly.
    if load_session_state(config.session_file):
        session = _load_stored_session(config, base_url)
        if session is not None:
            return session

    # 2. Session expired but remember_web is still valid — headless refresh.
    if (
        config.session_file.exists()
        and _remember_token_valid(config.session_file)
        and not _session_cookies_valid(config.session_file)
    ):
        if refresh_session_headless(config):
            session = _load_stored_session(config, base_url)
            if session is not None:
                return session

    # 3. Full manual login required (visible browser + polling).
    return _manual_login(config, base_url)


def _load_stored_session(config: AppConfig, base_url: str) -> BrowserSession | None:
    """Load the persisted session file and verify the browser is logged in."""
    session = create_browser_session(config)
    try:
        session.context.close()
        session.context = session.browser.new_context(
            accept_downloads=True, storage_state=str(config.session_file)
        )
        session.context.set_default_timeout(config.timeout_ms)
        session.page = session.context.new_page()
        if _is_logged_in(session.page, base_url):
            logger.info("auth | session loaded")
            return session
        logger.info("auth | saved session invalid, falling back")
    except PlaywrightError:
        close_browser_session(session)
        raise
    except Exception:
        close_browser_session(session)
        raise
    close_browser_session(session)
    return None


def _manual_login(config: AppConfig, base_url: str) -> BrowserSession:
    manual_config = replace(config, headless=False)
    session = create_browser_session(manual_config)
    session.page.goto(base_url, wait_until="domcontentloaded")
    logger.info("auth | please login manually in the opened browser")
    session.page.bring_to_front()
    _wait_for_login(session.page, base_url)
    save_session_state(session, config.session_file)
    logger.info("auth | session saved")
    return session


def _wait_for_login(page: Page, base_url: str, poll_interval_s: int = 3, timeout_s: int = 300) -> None:
    """Poll until the browser page shows a logged-in state."""
    print(">>> Войдите в браузер. Скрипт продолжится автоматически после входа...", flush=True)
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            if _is_logged_in(page, base_url):
                logger.info("auth | login detected automatically")
                return
        except Exception:
            pass
        remaining = int(deadline - time.time())
        print(f"    ожидание входа... (осталось {remaining}с)", flush=True)
        time.sleep(poll_interval_s)
    raise RuntimeError(f"Login not detected within {timeout_s}s — timed out.")
