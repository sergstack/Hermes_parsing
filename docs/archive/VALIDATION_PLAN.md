# Validation Plan — Hermes Refactor Foundation

## Goal

Validate that the refactor planning work did not damage functionality, sensitive state, runtime files, or generated outputs.

## Safe Baseline Commands

Run before changes:

```bash
pwd
git status --short
git diff --name-only
```

## Safe Repository Inspection

```bash
find . -maxdepth 3 \
  -not -path './.git/*' \
  -not -path './exports/*' \
  -not -path './logs/*' \
  -not -path './output/*' \
  -not -path './state/*' \
  -not -path './config/config.txt' \
  -print
```

## Safe Documentation Reads

Run only if files exist:

```bash
sed -n '1,240p' README.md
sed -n '1,240p' SPEC.md
sed -n '1,240p' plan.md
sed -n '1,240p' tasks.md
```

If a file is missing, document it and continue.

## Safe Metadata Discovery

```bash
find . -maxdepth 2 -type f \( \
  -name 'pyproject.toml' -o \
  -name 'requirements*.txt' -o \
  -name 'setup.cfg' -o \
  -name 'setup.py' -o \
  -name 'pytest.ini' -o \
  -name 'tox.ini' -o \
  -name 'Makefile' \
\) -print
```

## Safe Source/Test Discovery

```bash
find . -maxdepth 4 -type f \( -name '*.py' -o -name '*.md' \) \
  -not -path './.git/*' \
  -not -path './exports/*' \
  -not -path './logs/*' \
  -not -path './output/*' \
  -not -path './state/*' \
  -not -path './config/config.txt' \
  -print
```

## Risk Boundary Search

```bash
rg -n "export|exporter|live|session|cookie|token|password|secret|config.txt|herm_session|requests|selenium|playwright|write|open\(|Path\(|mkdir|logs|output|state" \
  --glob '!exports/**' \
  --glob '!logs/**' \
  --glob '!output/**' \
  --glob '!state/**' \
  --glob '!config/config.txt'
```

## Required Test Collection

```bash
.venv/bin/python -m pytest --collect-only -q
```

## Post-Change Validation

Run after creating `REFACTOR_PLAN.md`:

```bash
git diff --name-only
git status --short
.venv/bin/python -m pytest --collect-only -q
git status --short exports logs output state config/config.txt
```

## Optional Additional Tests

Additional tests may be run only if inspection proves they do not:

* run live exporter;
* contact live systems;
* require credentials;
* require session files;
* write to runtime/generated paths;
* mutate `exports`, `logs`, `output`, `state`, or `config/config.txt`.

## Validation Failure Handling

If a command fails:

1. Do not hide the failure.
2. Document the command.
3. Document the result.
4. Explain whether the failure blocks completion.
5. Do not claim full completion if acceptance criteria are not satisfied.
