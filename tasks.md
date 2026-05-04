# Tasks

## 1. Preparation
- [x] Inspect current source formatting and identify files that need formatting-only cleanup.
- [x] Add dev dependencies for test and lint workflows.
- [x] Create or update repo instructions so safe edit zones and verification commands are explicit.
- [x] Keep scope limited to `SPEC.md`, `plan.md`, and `tasks.md` until execution is approved.

## 2. Tests and smoke
- [x] Add tests for config parsing and validation.
- [x] Add tests for date boundary handling.
- [x] Add tests for report flow validation.
- [x] Add tests for file/path helpers.
- [x] Define the behavior of `--dry-run` before implementation.

## 3. Refactor
- [x] Split `app/downloaders.py` into smaller modules while preserving behavior.
- [x] Keep existing public entrypoints working during the migration.
- [x] Move brittle selectors and magic waits into a dedicated, documented layer.
- [x] Improve error context only where it does not broaden behavior risk.

## 4. Documentation
- [x] Update README with test and dry-run commands.
- [x] Document live smoke expectations and known brittle points.
- [x] Record residual risks after each refactor step.

## 5. Validation
- [x] Run the smallest relevant checks after each change.
- [x] Verify that the documented commands still match the codebase.
- [x] Confirm that the final plan preserves current Herm Finance flows.
