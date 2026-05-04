"""Logging helpers."""

from __future__ import annotations

import logging
from pathlib import Path


class _BracketFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):  # noqa: N802
        return super().formatTime(record, datefmt or "%Y-%m-%d %H:%M:%S")

    def format(self, record):
        timestamp = self.formatTime(record)
        message = record.getMessage()
        return f"[{timestamp}] {message}"


def setup_logging(log_dir: Path) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "herm_export.log"

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()

    formatter = _BracketFormatter()
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    root.addHandler(stream)
    root.addHandler(file_handler)
    return log_file


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
