# Judge Checklist — Deep Safe Offline Refactor

## Verdict

accept / revise / reject

## Scope Check

- [ ] Codex did not stop at planning.
- [ ] Codex executed safe offline batches.
- [ ] All remaining batches are completed or blocked.
- [ ] Live validation was not performed without approval.

## Evidence Check

- [ ] `git status --short` included.
- [ ] `git diff --stat` included.
- [ ] Files changed listed.
- [ ] Tests added/updated listed.
- [ ] Commands run listed.
- [ ] Validation results listed.

## Safety Check

- [ ] Live exporter was not run.
- [ ] `state/herm_session.json` was not opened.
- [ ] `config/config.txt` was not opened.
- [ ] Protected paths are clean.

## Test Check

- [ ] Pytest passed or blocked with reason.
- [ ] `git diff --check` passed.
- [ ] Characterization tests protect changed behavior.

## Acceptance Criteria Review

- [ ] Definition of Done A or B reached.
- [ ] Completed batches listed.
- [ ] Blocked batches have specific blockers.
- [ ] Residual risks documented.

## Final Recommendation

Accept only if the final report proves completion or explicit blockers.
