# Round 11 handoff — 2026-09-15

Codex addressed all four CPU lanes in `docs/ongoing.md`. R1-D4b's slices and R1-X9's qualified exposure audit are delivered. R1-64's development runner and R1-63's draft freeze package are implemented, with a tested five-file repair awaiting the user's required permission. No existing file was edited, no commit was made, and the pre-existing `logs/r1_round8/pytest_tmp/` was left alone. All execution was CPU; there were zero real-base/teacher calls, sealed-payload reads, draws, seals or protocol freezes.

This handoff and `docs/tasks/R1-round11-edit-request-v2.md` supersede the earlier import-only request and the recipe-readiness statements in the initial task records. Apply only `docs/tasks/R1-round11-snapshot-bindings-v2.patch` after approval. The earlier patch is historical and insufficient.

## Scientific findings

| Reading | MQuAKE candidate subjects | Interpretation |
| --- | ---: | --- |
| New 500-training/100-development slices, assuming prior MQuAKE work never happened | 4,818 | Counterfactual only; not a fresh population available now |
| Effective cumulative supplement v2 | 2,100 | Historical exclusions retained; 1,950 short of 4,050 |
| All eligible no-evidence review candidates cleared, counting bank observations as exposure | At most 2,829 | Optimistic review ceiling; not certified |
| Narrow reader/development-query screening, ignoring bank-only observations | At most 2,999 | Still below 4,050; memory-support/history gaps can reduce it further |

Shrinking the next training/development slices cannot undo prior exposure. Even the narrower screening does not supply three disjoint 1,000-edit streams plus endpoint reserves. Resolve the source/capacity strategy before treating another retraining cycle as a repair. Options for the lead are a new approved source or explicitly revised sampling/scope and statistical protocol. Reusing exposed data or overlapping realizations cannot silently retain an independent fresh-confirmation interpretation.

The audit checks four feature banks, reconstructs 14 completed training sessions, and inspects 139 development item traces. Eight earlier summaries lack sufficient bank receipts. Per-query evidence, per-subject lists and exact source hashes are retained. The main 66 MiB JSON is verbose by design; the two capacity-review JSONs and `docs/tasks/R1-X9.md` are compact entry points. No subject is released. Reader queries, cached frozen-base observations and inferred development schedules remain distinct evidence categories; memory-support use and other historical assays need further reconciliation before any release.

The installed matrix draft v3 still has 240 cells/two datasets and the old allowance, while protocol v2 retains 360 cells/three datasets. It also predates reader v4 and the revised MQuAKE exposure accounting. A new matrix, contrasts, reference version, measured budget and gate-admission receipts are needed. The dry candidate represents all twelve protocol §9 binding groups, leaves unavailable final identities null, and records all U01–U18 admission gates open.

## Delivered code and artifacts

- R1-D4b: `scripts/r1_d4b_self_contained.py`; new training/dev v3 manifests; cumulative supplement v2; capacity table. Exact old edit membership and certified support fields are preserved. Neighbours stay inside the slice with labelled fallbacks for scarce relations. The dev unrelated list contains 52 distinct in-slice prompts.
- R1-X9: `scripts/r1_x9_exposure_audit.py`; exact bank-query checks, deterministic RNG replay and conditional execution evidence; `exposure_audit.json`, `exposure_capacity_bounds.json`, `reader_only_capacity_review.json`.
- R1-64: new development payload/CLI modules and `src/pccap/revision_v1/development_cell.py`; immutable checkpoint/resume with development labels, admission refusal, labelled fillers, explicit missing challenge inventories and TinyBase tests. CounterFact 1,000-edit and MQuAKE 100-edit payloads validate on CPU. The latter has 48 source composition cases. Existing challenges supply no zsRE/MQuAKE near/revision rows, so those remain unavailable, not successes.
- R1-63: `scripts/r1_63_freeze_package.py`; `manifests/revision_v1/freeze_candidate_v1.json`; hash/path refusal tests and U-gate inventory. No lead freeze was performed.
- Integration helpers: `scripts/r1_64_materialize_base.py` copies the hash-bound Hugging Face snapshot into regular files under assets; `src/pccap/revision_v1/checkpoint_identity.py` correctly reconstructs list-indexed reader layers from NPZ key paths. Five regression tests cover these helpers.

## Permission-dependent repair

The final owner-factory metadata check exposed two defects in the new worked example: the default snapshot's symlinks escape its directory and are refused by the existing loader; the draft parameter-hash parser dropped numeric layer indices. The prepared repair uses an exact regular-file snapshot copy, corrects the metadata parser, fixes import ordering, binds the helper code, and refreshes the example/candidate identities. Actual model weights and research settings remain unchanged.

Exactly five existing files require edits: the two R1-64 scripts, `development_cell.py`, the worked recipe and the candidate freeze JSON. The new helpers, copied resources, reports and patch are already present. The proposed recipe's adapter identity now matches the owner factory using a metadata-only stand-in and the completed training summary. Base calls: zero. Current recipe/candidate generation and inspection logs are historical; do not execute the current unrepaired recipe.

Approval was requested asynchronously for the v2 five-file patch. Before applying, compare the expected before-hashes in `repair_v2_preview.json`. No task-board edits or commits are included. After approval, apply, run installed lint and the affected tests, inspect the repaired recipe, validate candidate bindings, and create a new completion receipt. The full proposed repair has already passed CPU tests in memory.

## Verification and cost

- Installed baseline plus first 16 new tests: **479 passed, 8 skipped in 54.59 s**, `installed_cpu.txt`.
- Final proposed repair, including five additional regression tests: **484 passed, 8 skipped in 54.12 s**, `proposed_repairs_cpu.txt`. The three edited Python modules were loaded only in memory; existing files were not changed.
- Proposed Python source passes Ruff; `git apply --check` passes. Installed Ruff still has the two import-order findings addressed by the pending patch.
- Exact candidate bindings were checked against current/proposed bytes; owner-factory configuration, reader hash and tokenizer match. Evidence: `repair_v2_preview.json`.
- GPU seconds: 0. No actual base construction/execution; real weights were read for NumPy hashes, and a metadata-only stand-in was used to test factory identities. Tests use TinyBase on CPU. The materialized snapshot uses about 0.5 GB under assets, and all snapshots/cache resources stay outside the repository.

New-file inventory and source hashes are in `completion.json`. Individual task records are `docs/tasks/R1-D4b.md`, `R1-X9.md`, `R1-64.md` and `R1-63.md`. Earlier readiness descriptions in those records precede the integration findings; this handoff and the v2 edit request govern current status.

## Suggested handoffs

The lead can decide population/scope, source precedence, multiplicity and the final reader version now. Another CPU lane can refresh the 360-cell matrix and reconcile memory-support/older-session/other-assay exposure. The GPU owner can profile development cells after the tested repair lands, then bind measured ceilings and retraining costs to whichever reader version is actually selected. Re-training v3 is still development work and does not by itself recover fresh population capacity. The inherited phase engine repeatedly recomputes full base identity hashes; include that overhead in the first real profile before relying on earlier per-cell estimates. Missing dataset-specific challenge inventories and MQuAKE comparator calibration also need explicit owner work.
