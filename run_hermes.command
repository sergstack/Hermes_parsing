#!/bin/zsh
set -uo pipefail

cd -- "${0:A:h}"

PYTHON=".venv/bin/python"

if [[ ! -x "$PYTHON" ]]; then
  echo "Virtualenv not found; creating .venv"
  python3 -m venv .venv
fi

if [[ ! -x "$PYTHON" ]]; then
  echo "Cannot find Python executable: $PYTHON"
  exit 1
fi

if ! "$PYTHON" -c "import playwright" >/dev/null 2>&1; then
  echo "Installing Python dependencies"
  "$PYTHON" -m pip install -r requirements.txt
fi

if ! "$PYTHON" -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); p.chromium.launch(headless=True).close(); p.stop()" >/dev/null 2>&1; then
  echo "Installing Playwright Chromium browser"
  "$PYTHON" -m playwright install chromium
fi

exec "$PYTHON" -m app.main "$@"
