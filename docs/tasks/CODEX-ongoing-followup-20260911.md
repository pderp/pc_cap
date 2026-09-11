# CODEX ongoing follow-up, 11 September 2026

status: done for the independent CPU audit and diagnostic; existing-document edits await permission
agent: Codex
inputs used: ongoing.md; round-four completion records and hashes; current REPRODUCE.md and its diff since 0d6e8d0; source snapshot 6b4b769; frozen v2 metadata; SD-3 and LM inventory; completed aggregate run records.

outputs: `logs/ongoing_followup_20260911/review.md`, `drift_remediation.md`, `summary.json`, `drift_coverage.json`, exact logs and copied generated audit outputs; `scripts/reproduce_ongoing_followup{,_v2}.py`, `scripts/review_drift_coverage{,_v2}.py`; `docs/tasks/ONGOING-followup-documentation.patch` and its edit-request JSON.

verify commands: original follow-up driver in the existing venv, launching twelve fresh CPU shells in ENV-05; original model-free drift driver; Ruff on the v2 scripts; syntax-tree comparison of v1/v2; `git apply --check docs/tasks/ONGOING-followup-documentation.patch`.

verify output: 12/12 subprocess invocations returned zero; five affected regressions passed in 5.02 s; no copied input changed; no corresponding live source changed during the audit. The existing evaluator reproduced 4,064 positions despite a full supplied array until its separate count argument was explicit. Explicit full-window coverage yields 245,237 scored positions and a 121-token dropped tail. All ten captured completed runs report 4,064 drift positions.

done-when check: prior Codex lane completion reconciled with stale board labels; changed CPU reproduction paths exercised without running confirmation; coverage defect has a runnable counterexample and concrete remedy requirements; two documentation edits prepared but not applied.

cost: gpu_seconds=0; summed fresh-shell subprocess wall_seconds=16.53. No model weights loaded by the drift diagnostic. Copies/temp files are isolated from active results and assets.

deviations: none to the frozen scientific programme. Diagnostic NLL is stubbed only to exercise window selection and count reporting; it is never a research NLL result. CLI analyses use empty isolated input roots and are correctly reported incomplete. V2 script cleanup changes no execution behavior.

unresolved: Claude's S4/S5/S7 and final S8 work; whole-validation drift remediation and versioning decision; mirroring completed lanes into the shared board. B4 remains unavailable; S6 stays closed for the month.

questions for lead: permission to apply the prepared existing-document edits to `docs/REPRODUCE.md` and `logs/grace_gradient_localization.md`. No source-tree edit or GPU action is included in that request.
