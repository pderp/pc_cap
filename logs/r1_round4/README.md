# Codex round 4 handoff

All three CPU lane deliverables from `docs/ongoing.md` are written. No GPU use, source/core edits, task-board edits, staging or commits. Claude's active pilot/evaluation artifacts remain his work.

| Lane | Entry point | Result |
| --- | --- | --- |
| R1-D1c | `docs/tasks/R1-D1c.md` | 87,857 unique representatives: 58,498 clear of automated checks and 29,359 flagged. Source/field/mapped hashes verified. E.2 and sealing remain with owners. |
| R1-40 | `docs/tasks/R1-40.md` | 180 core cells; 660 inclusive conditional cells; shared checkpoint/training registry; exactly two proposed profiling jobs. Core provisional cost 149.7 hours with reserves versus the old 15-hour envelope. No freeze or launch. |
| R1-X3 | `logs/audit_r1_26.md` | Main repairs confirmed. Remaining import-capacity, physical-byte, query/cost, configuration, output-admission and failure-reason issues documented. |

Validation: `pytest_cpu.txt` has 43 passes and 4 strict expected failures for open R1-X3 boundaries. `final_verification.json` confirms current source bindings and unchanged tracked/staged trees at HEAD `3ba95b5`. `lint_initial.json` has one pending I001 import-order finding.

## Pending permission, already requested

`docs/tasks/CODEX-R1-round4-edit-request.md` scopes five files: a legacy missing-tag compatibility fix to the new matrix builder, import ordering in the new candidate script, and source-hash/provenance refreshes in three new JSON artifacts. The exact script patch is `CODEX-R1-round4-repairs.patch`; `git apply --check` succeeds. `repair_preview.json` records successful in-memory generation of the requested matrix using the proposed one-line fix. `pre_repair_bindings.json` pins the five current files so a later approved repair must refuse concurrent changes.

No repair was applied. The ordinary matrix-builder invocation still needs the tag fallback; the existing draft accurately discloses its in-memory generation. The candidate script works; its pending change is formatting only. Do not mark the overall cleanup complete or silently update the bound hashes without approval. The new-files-only rule is the reason for this pause, including revisions to files just created in this round.

## Reverification after approval

Apply only the scoped changes, preserving candidate/data hashes and all cell definitions and budgets. Refresh source bindings explicitly; retain original generation provenance as history. Run Ruff on the six new Python files and the targeted tests listed below, using a fresh log/temp path. Write an additive verification/completion record rather than overwriting this audit history. Do not stage or commit unless the lead asks.

```bash
env JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 RAYON_NUM_THREADS=2 /home/derp/cap/venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=<new-path-under-logs> tests/revision_v1/test_round4_data_matrix_cpu.py tests/revision_v1/test_r1_26_boundary_audit_cpu.py tests/revision_v1/test_learner_cpu.py tests/revision_v1/test_contracts_memory.py tests/revision_v1/test_reader_controller.py
```

The four xfails should remain until the owning lane fixes their contracts. The public outcome control is separately recorded in `r1_26_outcome.json`; legacy edge exit 1 is explained in the audit, not counted as a test success. New `path_fixtures/` contains deliberate orphan/sentinel evidence; `pytest_tmp/` is disposable test output and need not be committed. Nothing was deleted under the creation-only rule.
