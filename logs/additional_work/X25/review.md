# X25 — supplemental evidence and reporting review

**PASS for the October 1 snapshot**, with the qualifications below. This is a source/receipt audit, not a scientific efficacy or fidelity verdict. No experiment was rerun.

The independent scan checked **25 report/profile/variant groups**, **13,112 declared file bindings** and **4,583 unique files**. It inventories **652 distinct cost/finish receipts**, including historical inputs shared by multiple reports; these counts are not independent experimental cells. All 47 ledger rows name an existing source. See [audit JSON](round58-reviewed/audit.json), [table](round58-reviewed/table.csv) and [ledger coverage](claim-source-coverage.json).

| Evidence group | Check | Sources | Receipt entries (overlap across groups) |
| --- | --- | --- | --- |
| PC-v0 | PASS | 1123 | 196 |
| PC-v0 harm | PASS | 1088 | 189 |
| PC-v1 | PASS | 1112 | 194 |
| PC-v1 harm | PASS | 1105 | 194 |
| depth/random controls | PASS | 1433 | 260 |
| matched control | PASS | 137 | 18 |
| AW-B | PASS | 366 | 2 |
| PC-reader | PASS | 163 | 34 |
| Option R | PASS | 827 | 6 |
| AW-L | PASS | 132 | 21 |
| HT-17 | PASS | 2290 | 295 |
| rehearsal deck | PASS | 2599 | 302 |
| results/additional_work/PC-reader/profile-bp-s0 | PASS | 52 | 1 |
| results/additional_work/PC-reader/profile-epc-s0 | PASS | 52 | 1 |
| results/additional_work/PC-v0/dev-profile-20260927 | PASS | 15 | 8 |
| results/additional_work/PC-v0/dev-profile-k1-20260928 | PASS | 16 | 8 |
| results/additional_work/PC-v0/dev-profile-k32-20260928 | PASS | 16 | 8 |
| results/additional_work/PC-v1/profile-20260927 | PASS | 65 | 8 |
| results/additional_work/PC-v1/profile-k32-20260929 | PASS | 66 | 8 |
| results/additional_work/PC-v1/profile-lr0.05-20260929 | PASS | 66 | 8 |
| results/additional_work/PC-v1/profile-lr0.2-20260929 | PASS | 66 | 8 |
| results/additional_work/PC-v1/replication-4-20260927 | PASS | 80 | 12 |
| results/additional_work/PC-v1/replication-4-k32-20260929 | PASS | 81 | 12 |
| results/additional_work/PC-v1/replication-4-lr0.05-20260929 | PASS | 81 | 12 |
| results/additional_work/PC-v1/replication-4-lr0.2-20260929 | PASS | 81 | 12 |

## What the PASS does and does not mean

- Original PC-v0 and fixed-v5 report/harm copies use the explicitly preserved pre-PC-9/10 source versions. They are the canonical reporting copies, not substitutes for raw results. The fixed-v5 original harm process ended with a final-table KeyError; the four arm vectors/two pairs and explicit repair are retained. That original cost receipt remains failed and its work remains charged. No successful terminal receipt is invented.
- Random-direction credit remains resource-stopped at 993 items, with 3 immediate successes. The controls container is complete as a report of the declared experiments, not evidence that all random cells completed. The matched-adjoint arm offered additional updates but underspent the PC allowance; it is not actual compute matching. Depth comparisons use order100; the default v0 result uses all five orders.
- AW-B has complete calibration/evaluation receipts. Its ten-memory result is the selected mixture at exp(-1); severity falls to about one-third with nearly unchanged frequency. The positive result does not establish a tail family or remove CounterFact KL breaches.
- PC-reader currently contains eight of twelve evaluations; only seed0 is paired. BP/ePC profiles are separate from full training receipts. The actual seed0 ePC/BP training ratio is 102.106×, not the old 37× forecast. Active seed1 metrics are not cited as a final result. AW-L contains six reused controls and eighteen missing evaluations; the latter are not zero-valued effects.
- Option R has four successful cells, one ceiling-stopped cell, nine deferred and sixteen pending. Independent sums of the five enclosing process receipts reproduce **20,418.39597792551 seconds** and exactly the four reported successful cell IDs. Session wall-time is separate and not added again. The stopped session and repaired torn cost journal stay explicit; four-realization sensitivity is still withheld.
- HT-17 uses the canonical v2 299-cell snapshot, whose sources.json digest and saved vector bindings pass. Earlier profile/first-snapshot outputs are historical. The prior 4,064-position κ pilot and v0 harm populations are not relabeled as the 245,237-position Stage-4 assay. Invalid/sparse fits and conditional interval assumptions remain visible.
- The current rehearsal pack binds the canonical partial reader/Option R/AW-L reports as well as default PC/control/mixture sources. All 47 ledger rows name sources; this syntactic check is supplemented by reading the reports, Q&A and numerical prompts. It is not an automatic semantic proof of every sentence or an independent rerun of model outputs. The default-PC numerical replay and X24 remain the separate source for arm/vector reconstruction.

## Discrepancies investigated

The initial Option R mismatch was a genuine current-path difference: five original cell plans bind `aw/r_run.py` before the R-2 resume/deferral repair. Its recorded SHA256 exactly matches `bbb7336:aw/r_run.py`. Those bytes are now preserved under `docs/tasks/round58-source-archive/`, with Git identities and reasons. The reporting-only resolver accepts precisely that hash; current runtime resolution and original plans/results are unchanged. [Version evidence](option-r-source-version.json).

S4-LIM necessarily changes publication producers. Their original versions are preserved by the same manifest so historical analysis checks still require the original bytes. No saved analysis hash was rewritten to pretend current code produced the old experiment. Intermediate audit directories document work in progress; **round58-reviewed is the delivered result**. An attempted common-resolver extension was removed before delivery; runtime `aw/pc_historical.py` is unchanged.

No unresolved byte/receipt discrepancy remains in this snapshot. Outstanding scientific limitations and incomplete GPU work are listed above and in the [freeze checklist](../../../docs/freeze_checklist_20261009.md). Rerun this audit after the final GPU results and regenerated reports; use `--reports` overrides for new canonical paths and `--deck` for the final export. This pass does not pre-approve future outputs.

Numerical provenance review: default-PC arm differences and harm source slots; depth/random/matched populations and stopping; AW-B per-memory efficacy/harm; PC-reader seed0 pairing/cost ratio; Option R coverage/cost; HT-17 phase/threshold conditioning; and rehearsal rounded values all agree with their named current records. The Stage-4 tables are unchanged by this round.
