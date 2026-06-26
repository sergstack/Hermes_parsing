"""Export history polling and row selection helpers."""

from __future__ import annotations

from pathlib import Path
from time import sleep
from typing import Any, Callable


LoadRows = Callable[[Any, str], list[dict]]
StepLogger = Callable[[str], None]


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
    names.append(file_name)
    return names


def wait_for_export_ready_by_name(
    session: Any,
    base_url: str,
    expected_name: str,
    timeout_ms: int,
    load_rows: LoadRows,
    wait_for_timeout: Callable[[int], None],
    min_id: int = 0,
    log_info: Callable[..., None] | None = None,
    step: StepLogger | None = None,
) -> None:
    poll_interval_ms = 3000
    waited_ms = 0
    while waited_ms <= timeout_ms:
        rows = load_rows(session, base_url)
        for row in rows:
            row_id = int(row.get("id", 0))
            if row_id <= min_id:
                continue
            name = row.get("original_file_name") or row.get("file_name") or ""
            status = row.get("status_id", "")
            if expected_name in name:
                if log_info:
                    log_info("download | api-poll | '%s' status=%s id=%s", name, status, row_id)
                if status == "ready":
                    if step:
                        step(f"api-poll ready: {name}")
                    return
                if status == "fail":
                    raise RuntimeError(f"Export '{name}' failed on server (status=fail)")
        if log_info:
            log_info("download | api-poll | '%s' not ready yet, waited %sms", expected_name, waited_ms)
        wait_for_timeout(poll_interval_ms)
        waited_ms += poll_interval_ms
    raise RuntimeError(f"Export '{expected_name}' did not become ready within {timeout_ms}ms")


def poll_ready_export_row(
    session: Any,
    base_url: str,
    file_name: str,
    timeout_ms: int,
    load_rows: LoadRows,
    min_row_id: int | None = None,
    extra_name: str | None = None,
    step: StepLogger | None = None,
    sleep_fn: Callable[[float], None] = sleep,
) -> dict:
    candidates = set(candidate_export_names(file_name, extra_name))
    deadline = timeout_ms / 1000
    waited = 0.0
    while waited <= deadline:
        if step:
            step("fetch export rows start")
        rows = load_rows(session, base_url)
        if step:
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
            if step:
                step("row selected")
            return ready_rows[0]
        if step:
            step("no row")
        sleep_fn(1)
        waited += 1
    raise RuntimeError(f"Ready export row not found for {file_name}")
