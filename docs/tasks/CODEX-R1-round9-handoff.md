# Codex round 9 handoff — 2026-09-14

## Delivered

Completed the CPU/new-file scope of **R1-57, R1-58, R1-59, R1-X8**, and **R1-D4**, which was added with DEC-045
while this round was active. The [protocol v2](../R1_stage4_protocol_draft_v2.md) reflects the adopted gate and
full **360-cell** scope. The [counter-review](../../logs/review_r1_56.md) contains findings and owner repairs.
Each lane has its own task record in this directory; claims remain unchanged and completion is additive.

- R1-57: independent-inventory analysis, pairing/missingness checks, revision margins/bootstrap, 16 tests and
  development dry run. Seed-0 v3−v2 RET-GS: zsRE 0, CounterFact −.01; no confirmatory interpretation.
- R1-58: verified register/candidate recipe, 16 tests, strict/exception count-only reports; DEC-045 companion
  adds three-dataset capacity with 5 further tests. No real RNG selection, final payload or seal.
- R1-D4: deterministic MQuAKE preparation, 15 tests, source/subject/conflict/composition inventories and independent
  complete token/source recount. Manifest: [mquake_items_v1.json](../../manifests/revision_v1/mquake_items_v1.json).
- R1-59: results, costs, accepted scope and all U01–U18 reconciled without closing owner/lead gates.
- R1-X8: 100-source numerical audit and cache-state reproduction; proposed repair compiled/tested in memory only.

Resources are under **/home/derp/cap/assets/data/prepared/revision_v1/r1_d4_v1/**.
Code, manifests, logs and documentation are in pc_cap. No base/teacher/model execution, GPU use, sealed-payload
access, source edits, staging or commits were performed. Sibling repositories and the shared environment were
not changed. Temporary test resources stayed under assets/test_tmp.

## Results that affect the next round

1. **Cache defect:** same-count state import and remove/add can retain stale rarity DF. Ordinary appended
   supersession and the tested rollback work. [Unapplied patch](R1-X8-cache-repair.patch) and
   [proof](../../logs/r1_round9/x8_cache_review.json) are ready for the owner.
2. **P1 scope:** stored P1 measures ungated v2 and a random surrogate with the wrong registered settings.
   It does not certify v3/all-control/MQuAKE full-cell costs or cache-state equivalence.
3. **Report qualifications:** cross-size outside IDs change (100→300 overlap 80% zsRE / 62% CF; 300→1,000 zero).
   Within-size gate comparisons are paired. The report reverses 67 complete versus 33 truncated CF pairs;
   locality firing is not measured LS loss. The +.012407 v2 CF drift residual exceeds the provisional .01 ceiling;
   exact-v3 drift is unavailable. Propagate the R1-X7 continuation qualifications.
4. **MQuAKE:** 6,043 remaining rewrites on 5,577 subjects; 924 excluded subjects correspond to 1,193 excluded
   rewrites. Nineteen target conflicts are retained. All items have two locality and two separate near candidates;
   these are per-item proposals, not globally disjoint final reserves.
5. **Composition:** 27,654 source questions; 4,981 cases retain all dependencies, 2,391 also avoid exact excluded
   path-subject hits. Semantic/teacher/final-stream compatibility remains open.
6. **Yield risk:** zsRE overlap removes 159 MQuAKE subjects, leaving 5,418. A proposed 1,000-subject training pool
   leaves only 368 surplus over 4,050 confirmation-role reservations before eligibility/context losses.
7. **Scope/cost:** retain all 360 cells; homogeneous 1,150 s/cell with .20 reserve gives 138 h, not an exact
   all-condition ceiling. A full v2 comparison is 45 additional cells; its allocation needs explicit resolution.
   Full-validation, composition, MQuAKE and exact control/shared-training costs remain unpriced.

## Validation and pending permission

The installed revision CPU suite returned **318 passed, 8 skipped, 2 failures** in 47 s.
All **52 newly added tests passed** within it. [Full log](../../logs/r1_round9/revision_tests_cpu.txt).
Package-layout checks: **59 passed**. [Log](../../logs/r1_round9/package_layout_tests_cpu.txt).
All eleven new Python files pass formatting; 49 new-document links resolve.
Ruff identifies one import-group blank line in the new analysis test. No other lint errors were found.

Three small test-file repairs remain unapplied:

| File | Repair | Preview |
| --- | --- | --- |
| tests/revision_v1/test_r1_27_superseding_cpu.py | Remove obsolete strict xfail: the orphan-root defect is already repaired | Direct target test passes with the marker removed in memory |
| tests/revision_v1/test_round4_data_matrix_cpu.py | Check live source bindings against a freshly built matrix; retain the historical stored draft | Full target test passes with the candidate change in memory |
| tests/revision_v1/test_analysis.py | Insert one blank line separating third-party and first-party imports | Ruff check of the proposed content passes |

The first two are [R1-round9-test-maintenance.patch](R1-round9-test-maintenance.patch);
the third is [R1-57-import-spacing.patch](R1-57-import-spacing.patch).
Both patches are concrete and do not touch manifests, implementation code or the cache-owner lane.
The first request was sent while independent report writing continued. **User permission is still required before
applying any of these existing-file edits**, including the now-created analysis test. No permission is inferred
from elapsed time. The current full-suite/lint state must not be reported as all green.

After approval, apply only the authorized patch scope, run the affected tests/lint and then the required CPU suite.
Record the result in a new validation addendum so existing handoff/task records need not be edited.
Do not alter historical logs or hide the initial failures.

## Safe owner sequencing

CPU context/dependency review, final analysis/query inventories and comparator loader/observer work can proceed
in separate files. The GPU owner handles teacher eligibility, any MQuAKE retrain, adopted-v3 drift and exact
all-condition profiles. Cache/metadata/report repairs and the new register/matrix belong to the orchestrator.
Source/training/analysis decisions precede final draw; payload compatibility precedes seal; measured costs and
counter-review disposition precede lead freeze and launch. No reduction of the retained scope is proposed.

Initial HEAD was 32b1ff3; Claude committed decision updates during this work through 85127c5.
The final working tree has no tracked-file diff from those owner commits; this round's work is additive/untracked.
The pre-existing untracked logs/r1_round8/pytest_tmp directory is not part of this handoff.
