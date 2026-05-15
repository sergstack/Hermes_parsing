# Codex Execution Brief — Deep Safe Offline Refactor

## 1. Role

You are Codex, an autonomous coding agent working inside this repository.

## 2. Mission

Complete the deep safe offline refactor end-to-end.

Do not stop at a plan.
Do not stop after analysis.
Do not stop after one batch.
Do not return only recommendations.

## 3. Context

Known context:

- The project is a Hermes parsing/exporting project.
- `REFACTOR_PLAN.md` may already exist.
- Safe offline work has previously emphasized:
  - not opening `state/herm_session.json`;
  - not opening `config/config.txt`;
  - not running live exporter;
  - not modifying `exports`, `logs`, `output`, `state`, or `config/config.txt`.
- Live validation against Herm Finance is outside safe offline scope.

## 4. Current State

Before implementation, inspect the repository safely and establish:

- current git status;
- existing source files;
- existing tests;
- existing docs;
- whether `REFACTOR_PLAN.md` exists;
- whether previous safe batches are already marked completed;
- what remaining safe offline batches exist.

## 5. Target State

After completion:

- all safe offline refactor batches are completed or explicitly blocked;
- behavior-preserving refactor changes are implemented where safe;
- characterization tests are added or improved for changed behavior;
- tests pass;
- protected paths are clean;
- live exporter was not run;
- sensitive files were not opened;
- final report proves Definition of Done A or B.

## 6. Scope

### Must Do

- Create or update the execution package files.
- Read `REFACTOR_PLAN.md` if it exists.
- If `REFACTOR_PLAN.md` does not exist, create one from safe inspection.
- Identify all safe offline refactor batches.
- Execute all safe batches iteratively.
- Add or improve characterization tests before or with behavior-preserving refactors.
- Validate after each batch.
- Check protected paths after each batch.
- Update progress in `REFACTOR_PLAN.md`.
- Return final report.

### Should Do

- Prefer small, reviewable batches.
- Extract pure helper functions.
- Reduce duplication.
- Isolate IO/path/config/output boundaries without touching sensitive files.
- Improve names and type hints when behavior remains unchanged.
- Keep existing project conventions.

### Out of Scope

- Live exporter execution.
- Real Herm Finance login.
- API polling against live service.
- Real downloads.
- Runtime/generated output mutation.
- Credentials/session handling changes.
- Output schema changes without approval.
- Large risky restructuring without tests.
- New dependencies unless absolutely necessary.

## 7. Execution Mode

Work autonomously until Definition of Done A or B is reached.

If information is missing:

- inspect safe files;
- infer conservatively;
- document assumptions;
- continue.

Do not ask for confirmation between safe batches.

## 8. Execution Loop

Repeat until no executable safe batch remains:

1. Read or update `REFACTOR_PLAN.md`.
2. Select next safe offline batch.
3. Add or update characterization tests for affected behavior.
4. Implement behavior-preserving refactor.
5. Run validation.
6. Check protected paths.
7. If validation fails, fix or revert the batch.
8. Mark completed batch in `REFACTOR_PLAN.md`.
9. Continue to the next batch.

## 9. Completion Rule

Before returning final report, verify:

- Is there any remaining safe batch in `REFACTOR_PLAN.md`?
- Is there any safe source/test refactor still possible?
- Does final report contain “next step: continue refactor” or “add tests”?

If yes, do not return final report. Continue executing.
