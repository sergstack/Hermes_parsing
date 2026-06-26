# Offline Smoke

Safe command:

```bash
bash scripts/smoke_offline_pipeline.sh
```

## What It Checks

- Python tests collect successfully.
- Full offline pytest suite passes.
- Git diff has no whitespace errors.
- Protected runtime paths show no Git changes.

## Safety Boundary

The smoke command does not:

- run `python -m app.main`;
- run `./run_hermes.command`;
- open `state/herm_session.json`;
- open `config/config.txt`;
- contact Herm Finance;
- write to `exports/`, `logs/`, `output/`, `downloads/`, `state/`, `.auth/`, or `config/config.txt`.

## Node Classification

Node validation is not applicable for the current repository state because no root `package.json` exists.
