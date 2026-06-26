"""Entry point for Herm Finance monthly report export."""

from __future__ import annotations

from .cmd_download import download_main


def main() -> int:
    return download_main()


if __name__ == "__main__":
    raise SystemExit(main())
