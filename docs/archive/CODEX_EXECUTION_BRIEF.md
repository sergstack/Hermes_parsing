# Codex Execution Brief — Hermes Refactor Foundation

## 1. Role

You are Codex, an autonomous coding agent working inside this repository:

```text
/Users/sst/prod/Парсинг Hermes_2
```

## 2. Mission

Safely analyze the project and create a deep refactoring foundation without damaging current functionality.

Do not stop at a plan.
Do not stop after analysis.
Do not return only recommendations.

The required repository output is:

```text
REFACTOR_PLAN.md
```

## 3. Context

Known from previous work summary:

* Changed file: `README.md`.
* README now includes project scope, runtime/sensitive files, safe operating rules, and future Mart/analytics boundaries.
* `.venv/bin/python -m pytest --collect-only -q` passed previously.
* 32 tests were collected in 0.04s.
* Full tests were not run.
* Live exporter was not run.
* `state/herm_session.json` was not opened.
* `config/config.txt` was not opened.
* `git status --short exports logs output state config/config.txt` previously showed no runtime/generated file changes.

## 4. Current State

Known facts:

* Repository exists locally.
* README has been updated.
* Test collection passed previously.
* Full behavior validation has not been performed.
* Runtime/generated files must be protected.
* Sensitive files must not be opened.

Known risks:

* Test collection does not prove behavior correctness.
* Live/exporter side effects may exist.
* Runtime/generated files may be modified by unsafe commands.
* Sensitive files may contain session data or credentials.
* Deep refactoring without characterization tests can break behavior.

## 5. Target State

After completion:

* `REFACTOR_PLAN.md` exists.
* Repository structure has been safely inspected.
* Runtime/sensitive safety rules are explicit.
* A safe validation baseline is documented.
* A staged refactor roadmap is documented.
* No live exporter was run.
* Sensitive files were not opened.
* Runtime/generated files were not modified.
* Final report proves acceptance criteria.

## 6. Scope

### Must Do

* Inspect repository safely.
* Build a repository map.
* Identify source modules, tests, docs, scripts, configs, and entrypoints.
* Identify runtime/generated/sensitive boundaries.
* Re-run safe pytest collection.
* Create `REFACTOR_PLAN.md`.
* Validate after changes.
* Report changed files, commands, validation, risks, and next step.

### Should Do

* Identify high-coupling modules.
* Identify filesystem/network/config/session/exporter boundaries.
* Identify missing characterization tests.
* Suggest safe phased migration.
* Suggest target architecture based on existing project conventions.

### Out of Scope

* Do not perform the full refactor now.
* Do not move large parts of code.
* Do not change parser/exporter behavior.
* Do not change output schemas.
* Do not change credentials or sessions.
* Do not delete generated data.
* Do not introduce dependencies.
* Do not reformat the whole repository.

## 7. Execution Mode

Work autonomously until the full safe scope is completed.

If information is missing:

* inspect the repository safely;
* infer only from safe files;
* document assumptions;
* continue.

Stop only if continuing would violate safety rules.

## 8. Implementation Phases

### Phase 1 — Safety Baseline

* Confirm current directory.
* Check git status.
* Check changed files.
* Re-run safe pytest collection.

### Phase 2 — Repository Inventory

* Inspect docs.
* Inspect source tree.
* Inspect tests.
* Inspect safe config metadata.
* Exclude sensitive/runtime/generated files.

### Phase 3 — Architecture Diagnosis

Identify:

* domain/core logic;
* parsing logic;
* exporter/output logic;
* config loading;
* state/session handling;
* filesystem writes;
* network/live integrations;
* analytics/Mart boundaries.

### Phase 4 — Refactor Plan

Create `REFACTOR_PLAN.md` with actionable staged roadmap.

### Phase 5 — Validation

Run safe validation commands and confirm runtime/generated paths were not modified.

### Phase 6 — Final Report

Return final implementation report using `FINAL_REPORT_TEMPLATE.md`.
