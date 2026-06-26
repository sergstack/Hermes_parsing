# Codex Refactor Validation

## Initial

```bash
git status --short
git diff --name-only
git diff --stat
.venv/bin/python -m pytest --collect-only -q
git status --short .auth downloads state logs exports output config/config.txt
```

## Per Batch

```bash
.venv/bin/python -m pytest -q
git diff --check
git status --short .auth downloads state logs exports output config/config.txt
```

## Node

Not applicable in the current repository state: no root `package.json` was found. If Node project files are added later, run:

```bash
npm test
node --check scripts/*.mjs
```

## Offline Smoke

Run:

```bash
bash scripts/smoke_offline_pipeline.sh
```

This command is offline-only and does not run the live exporter.

## Final

```bash
git status --short
git diff --name-only
git diff --stat
git diff --check
.venv/bin/python -m pytest -q
.venv/bin/python -m pytest --collect-only -q
git status --short .auth downloads state logs exports output config/config.txt
```
