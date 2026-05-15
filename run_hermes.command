#!/bin/zsh
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Fresh virtualenv not found: .venv/bin/python"
  echo "Create it first: python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt"
  exit 1
fi

exec .venv/bin/python -m app.main
