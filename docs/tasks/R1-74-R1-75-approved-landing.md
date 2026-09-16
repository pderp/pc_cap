# R1-74 / R1-75 — approved patches landed

Status: complete. Agent: Codex. Date: 2026-09-16.

The user approved both exact patches. The DEC-053 scoring change is installed in
src/pccap/revision_v1/stage4_assays.py; the drift-definition hash correction is installed in
scripts/r1_75_development_matrix.py. Both R1-68c profiles had completed at checkpoint 300, the host
showed no active pc_cap GPU experiment, and an exclusive nonblocking lock on the existing GPU lease
protected the patch operation without modifying the lease file contents.

This record supersedes the pending-approval/landing statements in R1-74.md, R1-75.md, R1-68d.md and
CODEX-R1-round17-completion.md. Those files remain historical records under the new-files-only rule.

## Validation

597 passed, 8 skipped, 11 subtests passed in 90.23s (0:01:30). The new test file tests/revision_v1/test_r1_74_75_landing.py runs the
existing scoring behavior cases against the installed module and verifies that the corrected inventory
builder reproduces the independently saved development matrix exactly. Ruff and git diff --check pass.

Both full and incremental R1-68d recipes were rebuilt in memory. Their serialized bytes match the
already prepared recipe files exactly, so no existing recipe needed rewriting. Both unmocked production
loaders now accept the installed code identity:

`51263d99ad957c58cd7ac5e56acc6ae904dbdbaec0c49e7ac203ffaf777beb8f`.

The scoring source SHA256 matches the reviewed preview:
`af4b050dfeaa165c8d4af9ab8893322a6e22421d32baec5f21cdd66f8a9b89b5`.

- [Applied patch receipts](../../logs/r1_round17/scoring_landing_20260916/applied.json)
- [Recipe and inventory verification](../../logs/r1_round17/scoring_landing_20260916/recipe-and-inventory-validation.json)
- [CPU test output](../../logs/r1_round17/scoring_landing_20260916/revision-tests.txt)
- [Current freeze audit](../../logs/r1_round17/scoring_landing_20260916/freeze-audit.json)

## Owner handoff

The two driver recipes are ready for the owner's real-base re-profile. The historical freeze candidate
correctly reports the driver and scoring source as stale bindings; it still needs a versioned successor
with final matrix/protocol/cost and scientific admission receipts. No frozen execution was authorized.

Only the two explicitly approved existing files were edited in this turn. The test module, logs and this
status record are new. No other existing documentation, task board, prior result or recipe was changed.
No GPU experiment or commit was performed. There are no remaining approvals for these two patches.
