# Validation Plan — Deep Safe Offline Refactor

## Initial Validation

Run before implementation:

```bash
git status --short
git diff --name-only
.venv/bin/python -m pytest --collect-only -q
git status --short exports logs output state config/config.txt
```

## Safe Inventory

```bash
find . -maxdepth 4 \
  -not -path './.git/*' \
  -not -path './exports/*' \
  -not -path './logs/*' \
  -not -path './output/*' \
  -not -path './state/*' \
  -not -path './config/config.txt' \
  -print
```

## Safe Risk Search

```bash
rg -n "export|exporter|live|session|cookie|token|password|secret|config.txt|herm_session|requests|selenium|playwright|write|open\(|Path\(|mkdir|logs|output|state" \
  --glob '!exports/**' \
  --glob '!logs/**' \
  --glob '!output/**' \
  --glob '!state/**' \
  --glob '!config/config.txt'
```

## Per-Batch Validation

Run after every batch:

```bash
.venv/bin/python -m pytest -q
git diff --check
git status --short exports logs output state config/config.txt
```

If full pytest is unsafe or blocked, run the safest relevant subset and document why.

## Final Validation

Run at the end:

```bash
git status --short
git diff --name-only
git diff --stat
git diff --check
.venv/bin/python -m pytest -q
.venv/bin/python -m pytest --collect-only -q
git status --short exports logs output state config/config.txt
```

## Validation Failure Handling

If validation fails:

1. Diagnose using safe files only.
2. Fix the issue if safe.
3. Re-run validation.
4. If not fixable safely, revert the batch.
5. Document the blocker.
