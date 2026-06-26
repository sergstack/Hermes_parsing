"""Autonomous authentication CLI.

Exit codes:
  0  session is valid (or was successfully refreshed / re-authenticated)
  1  all automatic paths failed — manual login aborted or timed out
  2  unexpected error

Usage:
  python -m app.cmd_auth [--headless] [--config PATH]

  --headless  Skip the manual-login fallback; fail with exit 1 if the
              remember_web headless refresh also fails.  Suitable for
              Kestra / cron environments where no human is present.
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import replace

from .auth import (
    _remember_token_valid,
    _session_cookies_valid,
    ensure_logged_in,
    load_session_state,
    refresh_session_headless,
)
from .browser import close_browser_session
from .config import read_config
from .logging_utils import setup_logging
from .paths import resolve_project_path

logger = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Authenticate against herm.finance")
    p.add_argument("--headless", action="store_true", help="No interactive login; fail if headless refresh fails")
    p.add_argument("--config", default="config/config.txt", help="Path to config file")
    return p.parse_args()


def auth_main(headless_override: bool | None = None, config_path: str = "config/config.txt") -> int:
    """Return 0 on success, 1 on auth failure, 2 on unexpected error."""
    setup_logging(resolve_project_path("logs"))
    try:
        config = read_config(config_path).resolved()
        if headless_override is not None:
            config = replace(config, headless=headless_override)

        # Already valid — nothing to do.
        if load_session_state(config.session_file):
            logger.info("cmd_auth | session already valid")
            return 0

        # Session expired — try headless refresh via remember_web.
        if (
            config.session_file.exists()
            and _remember_token_valid(config.session_file)
            and not _session_cookies_valid(config.session_file)
        ):
            if refresh_session_headless(config):
                logger.info("cmd_auth | headless refresh succeeded")
                return 0
            logger.warning("cmd_auth | headless refresh failed")

        # Headless-only mode stops here.
        if config.headless:
            logger.error("cmd_auth | running headless but no valid session — exit 1")
            return 1

        # Manual login via visible browser.
        session = ensure_logged_in(config)
        close_browser_session(session)
        logger.info("cmd_auth | manual login succeeded")
        return 0

    except RuntimeError as exc:
        logger.error("cmd_auth | auth failed: %s", exc)
        return 1
    except Exception as exc:
        logger.exception("cmd_auth | unexpected error: %s", exc)
        return 2


def main() -> None:
    args = _parse_args()
    sys.exit(auth_main(headless_override=args.headless or None, config_path=args.config))


if __name__ == "__main__":
    main()
