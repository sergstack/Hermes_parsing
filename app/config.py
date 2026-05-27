"""Configuration loading and typed application settings."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration loaded from a key=value text file."""

    start_date: str
    base_url: str
    download_dir: Path
    session_file: Path
    headless: bool
    overwrite: bool
    timeout_ms: int
    slow_mo: int
    repeat_each_month: bool = False
    config_path: Path | None = None

    def resolved(self, project_root: Path) -> "AppConfig":
        """Resolve relative paths against the project root."""
        return AppConfig(
            start_date=self.start_date,
            base_url=self.base_url,
            download_dir=(project_root / self.download_dir).resolve()
            if not self.download_dir.is_absolute()
            else self.download_dir.resolve(),
            session_file=(project_root / self.session_file).resolve()
            if not self.session_file.is_absolute()
            else self.session_file.resolve(),
            headless=self.headless,
            overwrite=self.overwrite,
            timeout_ms=self.timeout_ms,
            slow_mo=self.slow_mo,
            repeat_each_month=self.repeat_each_month,
            config_path=self.config_path,
        )


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")


def _parse_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if "=" not in stripped:
        raise ValueError(f"Invalid config line: {line!r}")
    key, value = stripped.split("=", 1)
    return key.strip(), value.strip()


def normalize_config(config: AppConfig, project_root: Path | None = None) -> AppConfig:
    """Resolve relative config paths against project_root or the current working tree."""
    return config.resolved(project_root or Path.cwd())


def read_config(config_path: str | Path = "config/config.txt") -> AppConfig:
    """Read a minimal key=value config file."""

    path = Path(config_path)
    raw: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parsed = _parse_line(line)
        if parsed is None:
            continue
        key, value = parsed
        raw[key] = value

    required = ["start_date", "base_url", "download_dir", "session_file"]
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(missing)}")

    return AppConfig(
        start_date=raw["start_date"],
        base_url=raw["base_url"],
        download_dir=Path(raw["download_dir"]),
        session_file=Path(raw["session_file"]),
        headless=_parse_bool(raw.get("headless", "false")),
        overwrite=_parse_bool(raw.get("overwrite", "true")),
        timeout_ms=int(raw.get("timeout_ms", "60000")),
        slow_mo=int(raw.get("slow_mo", "0")),
        repeat_each_month=_parse_bool(raw.get("repeat_each_month", "false")),
        config_path=path.resolve(),
    )
