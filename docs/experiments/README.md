# Experiments

This folder is reserved for safe parameter tuning notes and result summaries.

Default workflow:

1. Define a baseline and one candidate variant.
2. Use unit, contract, dry-run, or explicitly approved live-smoke metrics.
3. Serialize each result with `ExperimentResult`.
4. Accept a candidate only when success is not worse, failures do not increase,
   and score improves.

Do not store private configs, sessions, logs, exports, or live Herm Finance data
in this folder.
