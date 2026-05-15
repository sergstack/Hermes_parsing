# Acceptance Criteria — Deep Safe Offline Refactor

The task is accepted only if all applicable criteria are satisfied or explicitly blocked.

## Package Criteria

- [ ] Execution package files exist.
- [ ] `REFACTOR_PLAN.md` exists or was created from safe inspection.
- [ ] `REFACTOR_PLAN.md` lists safe offline batches.
- [ ] Progress/completion status is documented.

## Refactor Criteria

- [ ] All executable safe offline batches are completed.
- [ ] Any skipped batch has a specific blocker.
- [ ] At least one source/test refactor is performed if safe batches exist.
- [ ] Characterization tests are added or improved for changed behavior.
- [ ] Behavior is intended to remain unchanged.
- [ ] No output schema changes were made unless explicitly approved.

## Validation Criteria

- [ ] Initial validation was run.
- [ ] Validation was run after each batch.
- [ ] Final validation was run.
- [ ] Failed validation was fixed or the batch was reverted.
- [ ] Full pytest was run if safe.
- [ ] If full pytest was not run, the safest relevant subset was run and the reason was documented.
- [ ] `git diff --check` passed.
- [ ] Protected paths check passed.

## Safety Criteria

- [ ] Live exporter was not run.
- [ ] `state/herm_session.json` was not opened.
- [ ] `state/herm_session.json` was not modified.
- [ ] `config/config.txt` was not opened.
- [ ] `config/config.txt` was not modified.
- [ ] Protected paths were not modified:
  - `exports`
  - `logs`
  - `output`
  - `state`
  - `config/config.txt`

## Final Report Criteria

- [ ] Definition of Done A or B is stated.
- [ ] Completed batches are listed.
- [ ] Blocked batches are listed with reasons.
- [ ] Files changed are listed.
- [ ] Tests added/updated are listed.
- [ ] Commands run are listed.
- [ ] Validation results are listed.
- [ ] Safety confirmation is included.
- [ ] Residual risks are listed.
