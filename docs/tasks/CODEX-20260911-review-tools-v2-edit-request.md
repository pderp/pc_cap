# Review-tool edit request, final proposed patch

Apply only `docs/tasks/CODEX-20260911-review-tools-v2.patch`. It supersedes the one-line V2 request and the earlier combined patch. Nothing has been applied.

The two targets were created by Codex this turn. The patch removes a schema-invalid synthetic checkpoint override from `scripts/review_repairs_r2b_study.py`, tidies imports, and binds per-case diagnostic closures in `scripts/grace_numerical_trace.py`. An explicit import-sort boundary preserves pccap initialization before JAX (the first combined proposal did not preserve that order after sorting). No production model, adapter algorithm, tolerance or reference artifact is changed.

The proposed text compiles and passes Ruff through stdin without rewriting the files. Permission is required by the user's new-files-only rule. Existing failed logs will remain; the rerun will use a fresh fixture/evidence path.
