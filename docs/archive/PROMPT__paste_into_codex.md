# START PROMPT FOR CODEX

You are Codex, an autonomous coding agent working inside this repository:

```text
/Users/sst/prod/Парсинг Hermes_2
```

Your mission is to safely analyze the project and create a deep refactoring foundation without damaging existing functionality, sensitive runtime state, generated outputs, or live/exporter behavior.

Do not stop at a plan.
Do not stop after analysis.
Do not return only recommendations.
Implement the full safe scope and validate against acceptance criteria.

You are done only when the final report proves every acceptance criterion is satisfied or explicitly blocked.

## Read These Files First

Read these execution package files in order:

1. `README__START_HERE.md`
2. `CODEX_EXECUTION_BRIEF.md`
3. `ACCEPTANCE_CRITERIA.md`
4. `VALIDATION_PLAN.md`
5. `RISK_REGISTER.md`
6. `FINAL_REPORT_TEMPLATE.md`

Treat them as the task contract.

## Context

Known from the previous work summary:

* Changed file: `README.md`.
* README now includes sections for project scope, runtime/sensitive files, safe operating rules, and future Mart/analytics boundaries.
* `.venv/bin/python -m pytest --collect-only -q` passed previously.
* 32 tests were collected in 0.04s.
* Full tests were not run.
* Live exporter was not run.
* `state/herm_session.json` was not opened.
* `config/config.txt` was not opened.
* `git status --short exports logs output state config/config.txt` previously showed no runtime/generated file changes.

## Hard Safety Rules

Do not open:

* `state/herm_session.json`
* `config/config.txt`
* any file that appears to contain tokens, cookies, credentials, session state, auth state, or personal sensitive data.

Do not run:

* live exporter;
* production exporter;
* commands that contact live systems;
* commands that require credentials/session;
* commands that write to runtime/generated paths.

Do not modify:

* `exports`
* `logs`
* `output`
* `state`
* `config/config.txt`

Do not:

* delete user data;
* delete generated outputs;
* change secrets or credentials;
* introduce new dependencies;
* perform unrelated refactoring;
* perform broad code movement;
* reformat the whole repository;
* change parser/exporter behavior;
* change output schemas.

## Required Output

Create a repository file:

```text
REFACTOR_PLAN.md
```

It must include:

1. Purpose
2. Non-Negotiable Safety Rules
3. Current Repository Map
4. Functional Baseline
5. Sensitive and Runtime Files Policy
6. Current Architecture Diagnosis
7. Target Architecture
8. Refactor Principles
9. Phased Migration Plan
10. Test and Validation Strategy
11. Batch Checklist
12. Rollback Strategy
13. Risk Register
14. Acceptance Criteria
15. Open Questions

Optionally add a minimal README link to `REFACTOR_PLAN.md` only if it fits the existing README structure.

## Work Order

1. Confirm repository location and git status:

```bash
pwd
git status --short
git diff --name-only
```

2. Safely inspect repository structure, excluding sensitive/runtime/generated paths:

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

3. Read safe documentation files if present:

```bash
sed -n '1,240p' README.md
sed -n '1,240p' SPEC.md
sed -n '1,240p' plan.md
sed -n '1,240p' tasks.md
```

If any file is missing, document it and continue.

4. Inspect safe metadata files if present:

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

5. Inspect source and test files safely:

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

6. Search for risky boundaries without opening excluded files:

```bash
rg -n "export|exporter|live|session|cookie|token|password|secret|config.txt|herm_session|requests|selenium|playwright|write|open\(|Path\(|mkdir|logs|output|state" \
  --glob '!exports/**' \
  --glob '!logs/**' \
  --glob '!output/**' \
  --glob '!state/**' \
  --glob '!config/config.txt'
```

7. Re-run safe test collection:

```bash
.venv/bin/python -m pytest --collect-only -q
```

8. Create `REFACTOR_PLAN.md`.

9. Optionally make a minimal README link to `REFACTOR_PLAN.md`.

10. Validate after changes:

```bash
git diff --name-only
git status --short
.venv/bin/python -m pytest --collect-only -q
git status --short exports logs output state config/config.txt
```

11. Run additional tests only if inspection proves they are safe and do not trigger live/exporter/runtime writes.

## Acceptance Criteria

The task is complete only if:

1. `REFACTOR_PLAN.md` exists and is actionable.
2. The plan contains a current repository map based on safe inspection.
3. The plan contains explicit safety rules.
4. The plan contains target architecture or architecture options.
5. The plan contains phased refactor roadmap.
6. The plan contains validation strategy.
7. The plan contains rollback strategy.
8. The plan contains risk register.
9. No live exporter was run.
10. `state/herm_session.json` was not opened or modified.
11. `config/config.txt` was not opened or modified.
12. Runtime/generated paths were not modified:

    * `exports`
    * `logs`
    * `output`
    * `state`
    * `config/config.txt`
13. `pytest --collect-only -q` was run after changes and passed, or any blocker is documented.
14. `git status --short exports logs output state config/config.txt` was run after changes and showed no new runtime/generated modifications, or any pre-existing changes are documented.
15. Final report lists files changed, commands run, validation results, assumptions, residual risks, blockers, and next safe step.

## Final Report Format

Use the structure from `FINAL_REPORT_TEMPLATE.md`.

Return the final report after implementation and validation.
