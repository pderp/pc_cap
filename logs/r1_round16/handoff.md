# Codex round16 — handoff

All eight current CPU lanes in docs/ongoing.md are complete for their assigned scope. New files only; no GPU/real-base execution, sealed payloads, existing-file edits, staging or commits. The task board and ongoing.md are left for the owner to mirror. Claude's concurrent work is separate.

| Lane | Delivered | Next owner action |
| --- | --- | --- |
| R1-X12 | logs/review_r1_selection.md; independent42-candidate audit; retention–rejection PDF/SVG/PNG | Use the verified winner with boundary uncertainty; obtain shared outside populations before claiming occupancy flatness |
| R1-68c | New instrumented driver, true batched per-prefix drift, full/incremental recipes, TinyBase parity | Re-profile both new recipes on the real base; read measured timer categories before attributing overhead |
| R1-72 | Per-block/per-cell schedule JSON and memo; DEC-051/052 addendum | Retain approved full scope; remeasure September20; use explicit incomplete-cell inventory if needed |
| HT-1b | v5/v4 tail audits plus new CF supplement; mean/tail PDF/SVG/PNG | Preserve per-position outcomes and reference/history labels; carry tail results into final reporting |
| HT-4b | docs/talk_claim_ledger_v2.md with20 labelled rows and32 evidence bindings | Read with late_owner_results_review.md; keep κ/stress outcome rows empty until actually run |
| R1-64b |16 preflighted comparator recipes and additive S1 NPZ construction entry point | Profile eight comparator conditions on zsRE/CF using scripts.r1_64b_comparator_recipes |
| R1-73 | Bound MQuAKE v3b calibration spec, owner execution script and CPU parity tests | Run under the shared GPU lease, inspect all banks/fallbacks, then bind calibration v3 |
| R1-63c | manifests/revision_v1/freeze_candidate_v4.json;905 bindings,147 source files,18 gates | Supply final closure receipts and selected-primary successor matrix before any freeze/draw/launch |

## Findings that affect interpretation

Selection rule reproduction passes:42 complete candidates,15 admissible, unique winner mean RET-GS0.8033 and10/100 zsRE unseen false fires. Wilson95% is5.52–17.44%; selection and deterministic-development qualifications apply. Four source checkpoints exactly reproduce the uniform averaged weights. All selection populations match where raw IDs are available; locality requires reconstruction from the common loader.

Unseen occupancy “flatness” is unproved: zsRE100/300/1000 outside-ID sets do not overlap, and sources/history mixtures differ. The300/1000 MQuAKE attempts failed during filler collection; no completed higher-occupancy observations exist. Do not fill that gap with a zero rate.

Small signed mean drift coexists with substantial local harm. On shared128-window/16,256-position text/reference populations:
- v4 zsRE: mean+.000233nat; maximum3.790nat;1position above .1nat.
- v5 zsRE: mean+.002198nat; maximum8.686nat;17positions above .1nat.
- v5 CounterFact: mean+.006286nat; maximum7.315nat;52positions above .1nat.

Full/incremental v5 scientific drift observations are duplicates, not independent replication. Report expected shortfall/exceedances beside means; no power-law identification is claimed.

Q9 concerns a real scoring distinction: CounterFact locality36/50 and near-miss63/100 under termination-qualified equality versus49/50 and100/100 under bounded text equality. The saved rows reproduce both. No scoring convention was changed. Shorter ordinary-text prefixes do not explain the CF timing difference: the drift windows/reference vectors match exactly. Two measured learned-reader cells do not establish equal costs for all datasets/controls.

The full405-cell scenario plus conditional7h HT reservation needs331–452.5GPUh at48–66minutes/cell, versus306GPUh before October8 at75% availability from September21. The ~20-minute R1-68c target is unmeasured. DEC-051/052 now govern scope/order/incomplete reporting; Q4/Q5 and Q9 remain lead/owner work.

## Validation and provenance

Full CPU suite: **551 passed,8 skipped,4 subtests passed in87.43s**. The23 new tests plus four subtests also pass independently. Ruff lint/format checks pass for all13 new Python files. All16 comparator recipes pass metadata preflight without model construction; their identities match installed TinyBase adapters. MQuAKE calibration's grid/choice matches v0, including explicit detection of an exact-key fallback that still fails the false-fire criterion. The dry candidate rehashes905 distinct bindings and validates the installed tree.

See revision_cpu_tests.{json,txt}, comparator_recipe_inventory.json, freeze_candidate_v4_verification.json and task records under docs/tasks.

The ledger snapshot's E30 live-notes source changed when Claude committed62dd43f during this round. Its exact original bytes were recovered from8da0995 as stage2_notes_at_ledger_v2.md;31other evidence bindings stayed identical. late_owner_results_review.{md,json} binds the archive/current source and the reviewed CF/Q9/filler updates. No earlier output was overwritten.

The old driver already omitted outer clones for edit/immediate phases, so the previous attribution of about545seconds specifically to clone/restore is not established. The new timers split recipe checks, identity verification, state hashing, clone, restore, operation and file writing. The optimized drift path preserves a fresh selection for every prefix, charges physical padded forwards and keeps state/identity checks. Clone-free mutation failures abort the cell; discard that object and resume only a verified checkpoint.

## Owner workflow

1. Read R1-X12 and late_owner_results_review.md; mirror the eight completion records.
2. Use docs/tasks/R1-68c-zsre-v5-{full,incremental}.recipe.json for the real-base comparison under the owner's lease/supervision.
3. Use the16 recipes listed in comparator_recipe_inventory.json through the new comparator entry point. The historical snapshot-only constructor cannot load continued S1 NPZ weights. Full integrity profile is intentional for these comparator recipes.
4. Run R1-73's bound calibration spec; retain old zsRE/CF radii and BP scales unless the lead changes policy explicitly. Continued-base transfer/budget reconciliation remains open.
5. Resolve Q4/Q5 and numerical safeguards before κ/stress runs; resolve Q9 before final locality-margin interpretation.
6. Reprice September20, bind successor matrix/ceilings/populations and all gates, then let the owner perform any authorized final freeze and execution.

No permission to edit an existing file is needed for these delivered additive artifacts. Suggested corrections to live notes/protocol/boards are documented for the owner; none was applied. Work remains uncommitted.
