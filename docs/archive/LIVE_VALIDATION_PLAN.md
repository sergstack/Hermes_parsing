# Live Validation Plan

Status: prepared, not run by Codex.

## Preconditions

- Operator explicitly approves live validation in a separate command.
- Operator confirms `config/config.txt` and `state/herm_session.json` are valid without printing their contents.
- Operator confirms exported files may be written to configured runtime output paths.
- Current safe validation passes:

```bash
.venv/bin/python -m pytest -q
bash scripts/smoke_offline_pipeline.sh
```

## Forbidden Without Explicit Approval

Do not run:

```bash
python -m app.main
./run_hermes.command
```

Do not open or print:

```text
state/herm_session.json
config/config.txt
```

## Live Validation Steps

After explicit approval only:

1. Record `git status --short`.
2. Run the operator-approved exporter command.
3. Capture exit code.
4. Inspect only metadata needed for evidence:
   - log tail without secrets;
   - generated file names and sizes only;
   - summary line if present.
5. Run protected path Git status check.

## Abort Criteria

- Unexpected credential prompt.
- Auth/session values are printed.
- Exporter writes outside configured runtime paths.
- Report filenames, periods, or output folders differ from documented contracts.
- Any test fails before live validation starts.

## Evidence To Collect

- Command used.
- Exit code.
- Summary counts.
- Generated file names and sizes only.
- Any failed report codes and periods.

## Recovery

If live validation fails, preserve logs and outputs for operator review. Do not delete, rewrite, or move runtime files from Codex without a separate explicit instruction.
