# Requested edits to new review scripts

This combined patch supersedes the one-line V2 fixture request. Both files were created by Codex this turn, but the user requires permission for every existing-file edit. The patch has not been applied.

- `scripts/review_repairs_r2b_study.py`: preserve the schema-required checkpoint schedule; organize one import block. This permits the independent synthetic study to proceed past its fixture error.
- `scripts/grace_numerical_trace.py`: import pccap before JAX, organize imports, and bind per-case arrays in synchronous diagnostic closures explicitly. No model, optimizer, tolerance or reference artifact changes.

The proposed versions compile and pass Ruff via stdin, without writing them over the originals. The failed study and lint logs remain preserved.

Patch: `docs/tasks/CODEX-20260911-review-tools-edit.patch`.
