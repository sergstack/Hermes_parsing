"""Tests for session state loading and cookie expiry detection."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from app.auth import load_session_state, _session_cookies_valid, _remember_token_valid


def _write_session(tmp_path: Path, cookies: list[dict]) -> Path:
    p = tmp_path / "session.json"
    p.write_text(json.dumps({"cookies": cookies, "origins": []}), encoding="utf-8")
    return p


def _session_cookie(name: str = "hermes_session", expires: float = -1) -> dict:
    return {"name": name, "value": "x", "domain": "herm.finance", "expires": expires}


# ── load_session_state ────────────────────────────────────────────────────────

def test_load_session_state_missing_file(tmp_path: Path) -> None:
    assert load_session_state(tmp_path / "no_such_file.json") is False


def test_load_session_state_empty_file(tmp_path: Path) -> None:
    p = tmp_path / "empty.json"
    p.write_bytes(b"")
    assert load_session_state(p) is False


def test_load_session_state_valid_session(tmp_path: Path) -> None:
    future = time.time() + 3600
    p = _write_session(tmp_path, [_session_cookie("hermes_session", future)])
    assert load_session_state(p) is True


def test_load_session_state_expired_session(tmp_path: Path) -> None:
    past = time.time() - 1
    p = _write_session(tmp_path, [_session_cookie("hermes_session", past)])
    assert load_session_state(p) is False


def test_load_session_state_no_expiry_cookies_treated_as_valid(tmp_path: Path) -> None:
    p = _write_session(tmp_path, [_session_cookie("app_version", -1)])
    assert load_session_state(p) is True


# ── _session_cookies_valid ────────────────────────────────────────────────────

def test_session_cookies_valid_expired(tmp_path: Path) -> None:
    past = time.time() - 60
    p = _write_session(tmp_path, [_session_cookie("hermes_session", past)])
    assert _session_cookies_valid(p) is False


def test_session_cookies_valid_future(tmp_path: Path) -> None:
    future = time.time() + 3600
    p = _write_session(tmp_path, [_session_cookie("hermes_session", future)])
    assert _session_cookies_valid(p) is True


def test_session_cookies_valid_malformed_json_treated_as_valid(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("not json {{{", encoding="utf-8")
    assert _session_cookies_valid(p) is True


def test_session_cookies_valid_no_cookies(tmp_path: Path) -> None:
    p = tmp_path / "empty_cookies.json"
    p.write_text(json.dumps({"cookies": [], "origins": []}), encoding="utf-8")
    assert _session_cookies_valid(p) is True


def test_session_cookies_valid_non_session_cookie_expired_ignored(tmp_path: Path) -> None:
    past = time.time() - 60
    p = _write_session(tmp_path, [{"name": "XSRF-TOKEN", "value": "y", "domain": "herm.finance", "expires": past}])
    # XSRF-TOKEN doesn't contain "session" in its name — not checked by this function
    assert _session_cookies_valid(p) is True


def test_session_cookies_valid_multiple_cookies_one_expired(tmp_path: Path) -> None:
    past = time.time() - 60
    future = time.time() + 3600
    p = _write_session(tmp_path, [
        _session_cookie("hermes_session", past),
        {"name": "remember_web_abc", "value": "z", "domain": "herm.finance", "expires": future},
    ])
    assert _session_cookies_valid(p) is False


# ── _remember_token_valid ─────────────────────────────────────────────────────

def _remember_cookie(expires: float) -> dict:
    return {"name": "remember_web_abc123", "value": "tok", "domain": "herm.finance", "expires": expires}


def test_remember_token_valid_future_expiry(tmp_path: Path) -> None:
    future = time.time() + 86400
    p = _write_session(tmp_path, [_remember_cookie(future)])
    assert _remember_token_valid(p) is True


def test_remember_token_valid_no_expiry(tmp_path: Path) -> None:
    p = _write_session(tmp_path, [_remember_cookie(-1)])
    assert _remember_token_valid(p) is True


def test_remember_token_valid_expired(tmp_path: Path) -> None:
    past = time.time() - 60
    p = _write_session(tmp_path, [_remember_cookie(past)])
    assert _remember_token_valid(p) is False


def test_remember_token_valid_missing_file(tmp_path: Path) -> None:
    assert _remember_token_valid(tmp_path / "none.json") is False


def test_remember_token_valid_no_remember_cookie(tmp_path: Path) -> None:
    future = time.time() + 3600
    p = _write_session(tmp_path, [_session_cookie("hermes_session", future)])
    assert _remember_token_valid(p) is False
