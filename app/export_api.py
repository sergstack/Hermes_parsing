"""API helpers for export polling and downloads."""

from __future__ import annotations

import base64
import json
import logging
from pathlib import Path
from time import sleep

from .browser import BrowserSession

logger = logging.getLogger(__name__)


def request_json(
    session: BrowserSession, method: str, url: str, payload: dict | None = None
) -> dict:
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
            return { status: response.status, text: await response.text() };
        }""",
        {"method": method, "url": url, "payload": payload},
    )
    if body["status"] >= 400:
        raise RuntimeError(f"{method} {url} -> {body['status']}: {body['text'][:200]}")
    try:
        return json.loads(body["text"]) if body["text"] else {}
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"{method} {url} did not return JSON") from exc


def request_bytes(
    session: BrowserSession, method: str, url: str
) -> tuple[bytes, dict[str, str]]:
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
        raise RuntimeError(
            f"{method} {url} -> {body['status']}: {body.get('text', '')[:200]}"
        )
    headers = {k.lower(): v for k, v in body["headers"].items()}
    return base64.b64decode(body["data"]), headers


def trigger_async_export(
    session: BrowserSession, export_url: str, file_name: str
) -> None:
    logger.info("download | trigger export -> %s (%s)", export_url, file_name)
    request_json(session, "POST", export_url, {"userData": {"fileName": file_name}})


def load_export_rows(session: BrowserSession, base_url: str) -> list[dict]:
    payload = request_json(
        session, "POST", f"{base_url}/api/resources/export-file/all", {}
    )
    return payload.get("data", [])


def step(label: str) -> None:
    message = f"download | step | {label}"
    print(message, flush=True)
    logger.info(message)


def candidate_export_names(file_name: str, extra_name: str | None = None) -> list[str]:
    stem = Path(file_name).stem
    names: list[str] = []
    if extra_name:
        names.append(extra_name)
    parts = stem.rsplit("_", 1)
    if len(parts) == 2 and len(parts[1]) == 7 and parts[1][4] == "-":
        period = parts[1]
        names.extend([file_name, f"{period}-01.xlsx", f"{period}.xlsx"])
        return names
    if len(parts) == 2 and len(parts[1]) == 10 and parts[1][4] == "-" and parts[1][7] == "-":
        names.extend([file_name, f"{parts[1]}.xlsx"])
        return names
    names.append(file_name)
    return names


def poll_ready_export_row(
    session: BrowserSession,
    base_url: str,
    file_name: str,
    timeout_ms: int,
    min_row_id: int | None = None,
    extra_name: str | None = None,
) -> dict:
    candidates = set(candidate_export_names(file_name, extra_name))
    deadline = timeout_ms / 1000
    waited = 0.0
    while waited <= deadline:
        step("fetch export rows start")
        rows = load_export_rows(session, base_url)
        step("fetch export rows done")
        ready_rows = [
            row
            for row in rows
            if row.get("status_id") == "ready"
            and (min_row_id is None or int(row.get("id", 0)) > min_row_id)
            and (
                row.get("original_file_name") in candidates
                or row.get("file_name") in candidates
            )
        ]
        if ready_rows:
            ready_rows.sort(key=lambda row: row.get("id", 0), reverse=True)
            step("row selected")
            return ready_rows[0]
        step("no row")
        sleep(1)
        waited += 1
    raise RuntimeError(f"Ready export row not found for {file_name}")


def download_export_file(
    session: BrowserSession, base_url: str, file_id: str | int
) -> tuple[bytes, str]:
    body, headers = request_bytes(
        session, "POST", f"{base_url}/api/export_files/download/{file_id}"
    )
    return body, headers.get("content-disposition", "")
