#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

.venv/bin/python -m pytest --collect-only -q >/tmp/hermes_offline_collect.txt
.venv/bin/python -m pytest -q
git diff --check
git status --short .auth downloads state logs exports output config/config.txt

echo "offline smoke passed"
