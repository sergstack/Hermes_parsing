# Acceptance Criteria — Hermes Refactor Foundation

The task is complete only if all applicable criteria are satisfied or explicitly blocked.

## Required File

- [ ] `REFACTOR_PLAN.md` exists.
- [ ] `REFACTOR_PLAN.md` is actionable.
- [ ] `REFACTOR_PLAN.md` is based on safe repository inspection.

## Required Sections in `REFACTOR_PLAN.md`

- [ ] Purpose
- [ ] Non-Negotiable Safety Rules
- [ ] Current Repository Map
- [ ] Functional Baseline
- [ ] Sensitive and Runtime Files Policy
- [ ] Current Architecture Diagnosis
- [ ] Target Architecture
- [ ] Refactor Principles
- [ ] Phased Migration Plan
- [ ] Test and Validation Strategy
- [ ] Batch Checklist
- [ ] Rollback Strategy
- [ ] Risk Register
- [ ] Acceptance Criteria
- [ ] Open Questions

## Safety Criteria

- [ ] Live exporter was not run.
- [ ] `state/herm_session.json` was not opened.
- [ ] `state/herm_session.json` was not modified.
- [ ] `config/config.txt` was not opened.
- [ ] `config/config.txt` was not modified.
- [ ] Runtime/generated paths were not modified:
  - `exports`
  - `logs`
  - `output`
  - `state`
  - `config/config.txt`

## Validation Criteria

- [ ] `git status --short` was run before changes.
- [ ] `git diff --name-only` was run before changes.
- [ ] `.venv/bin/python -m pytest --collect-only -q` was run after changes.
- [ ] `git status --short exports logs output state config/config.txt` was run after changes.
- [ ] Any additional test command was run only if confirmed safe.
- [ ] Any skipped validation is explained.

## Documentation Criteria

- [ ] Current repository map is documented.
- [ ] Safe and unsafe commands are documented.
- [ ] Target architecture or architecture options are documented.
- [ ] Refactor phases are documented.
- [ ] Rollback strategy is documented.
- [ ] Risks and controls are documented.
- [ ] Missing data and assumptions are documented.

## Final Report Criteria

Final report must include:

- [ ] Summary
- [ ] Files changed
- [ ] Repository areas inspected
- [ ] Key decisions
- [ ] Commands run
- [ ] Validation results
- [ ] Acceptance criteria check
- [ ] Safety confirmation
- [ ] Assumptions
- [ ] Residual risks
- [ ] Blockers
- [ ] Next safe step
