# Plan

## Phase 1: Safe preparation
1. Normalize formatting without changing logic.
2. Add dev dependencies and document check commands.
3. Add project instructions and planning artifacts.

## Phase 2: Test foundation
1. Expand unit coverage for config, dates, paths, and report validation.
2. Add a `--dry-run` mode that reads config, builds periods and paths, and does not open a browser.
3. Document the dry-run and live-smoke expectations.

## Phase 3: Behavior-preserving refactor
1. Split `app/downloaders.py` into smaller modules for UI actions, API actions, file handling, and orchestration.
2. Keep the public entrypoint compatible while moving internals.
3. Run the smallest relevant checks after each step.

## Phase 4: Reliability improvements
1. Replace only the most fragile waits with condition-based waits where the condition is reliable.
2. Move selectors into a dedicated module or section with comments about purpose and failure mode.
3. Improve error reporting with structured context when practical.

## Phase 5: Operational quality
1. Add CLI flags for config path, report selection, date range, dry-run, headless mode, and overwrite behavior if they fit the current design.
2. Add machine-readable summary output if it can be done without widening scope too much.
3. Update README with developer workflow and troubleshooting notes.
