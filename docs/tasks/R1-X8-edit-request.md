# R1-X8 — concrete owner edit requests

These are requests for the orchestrator/Claude to review in their owned files. **Nothing below is applied.**
The user requires permission before editing existing files; this lane supplies new review/patch artifacts only.
The detailed evidence and source bindings are in [review_r1_56.md](../../logs/review_r1_56.md).

| Priority | Existing files | Requested change | Acceptance check |
| --- | --- | --- | --- |
| High | src/pccap/revision_v1/memory.py; learner.py | Apply/review R1-X8-cache-repair.patch: content mutation version plus store identity; clear DF cache on import | Same-count import and remove/add give overlap 0; ordinary supersession and rollback remain correct; installed regression tests |
| High | tests/revision_v1/test_learner_cpu.py | Add the actual restore/replacement and repeated-token cases | No real base needed; gate1 insertion described as predicate-only |
| High | scripts/r1_55_p1_profile.py | Instantiate/load the exact registered random and adopted-v3 conditions; save query IDs/results and gate/cache byte/timing receipts | Constructor/config/weights equality; independent count and answer recount; all comparator/three-dataset profiles |
| High | scripts/r1_54_drift_assay.py | Accept/persist rare gate and DF settings, exact code/state/window bindings; refuse unintended overwrite | Adopted-v3 assay; 127K scored positions and 3K probes separate; full-validation scope explicit |
| High | scripts/r1_43_endpoints_run.py; scripts/r1_44_unseen_run.py | Save exact semantic config, rare gate, DF maximum, source/hash/history and expected endpoint inventories | Same weights with different gates are distinguishable without relying on tag; fixed final outside population |
| High | owner matrix/freeze/loader and next exclusion-register files | Version for DEC-043/045, 360 retained cells, MQuAKE training/transfer/source/exposure, compatible dependencies and budget | Strict mismatch refusal; no old 240-cell or two-dataset writer admitted |
| Medium | docs/R1_stage2_report.md | Correct 67 complete/33 truncated; qualify v2 residual drift, locality firing, oracle/storage and learning claims; propagate R1-X7 continuation qualifications | Every stated observation links to the correct condition, population, denominator and artifact |
| Medium | docs/R1_stage2_report.md; notes/lead queue as needed | Label changing size populations, exact surrogate P1 settings and scope; remove withdrawn reduction; distinguish 138h scenario from measured ceilings | All 8×3×3×5 retained; explicit v2 allocation and unpriced work |
| Medium | primary_condition_v3.json, next version | Separate inherited v2 numbers from gated evidence; pin repaired runtime identity and any retrained MQuAKE checkpoint | v3 CF seed0 GS .715; gated drift not invented |

The cache patch is bound to learner SHA
`4bb7b848bd1e3d34249379fb5b840062e5f95082a403a8895f8cb6d7ae68b451` and memory SHA
`c214c2a74cd396936cc674befda13c79ad04e126759872eed1a3b55d70169f64`.
The in-memory proof is [x8_cache_review.json](../../logs/r1_round9/x8_cache_review.json).
The patch does not account for persistent Python cache memory; include that in the exact-v3 profile/accounting work.

Separate test-maintenance request:
[R1-round9-test-maintenance.patch](R1-round9-test-maintenance.patch) removes one obsolete strict xfail and checks
current source hashes against a newly built matrix while preserving the historical stored draft.
Both direct in-memory reproductions pass; [receipt](../../logs/r1_round9/test_maintenance_preview.json).
Only those two existing test files are covered by the pending user permission request, not the cache or owner edits.
