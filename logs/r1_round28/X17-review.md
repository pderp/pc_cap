# X17 — review of candidate v12 after the round-28 repairs

Codex, round 28. **Verdict: not ready for signature or launch.** The protocol
contradiction, missing normative bindings and typed cost schema are repaired.
The remaining work includes measurements and production assembly, so the
requested “signatures only” description would be inaccurate.

This report summarizes `r1-x17-review.json`, produced by
`scripts/r1_x17_review.py`. That JSON binds the reviewed inputs and contains the
full DEC-033–061 trace, corrected MQuAKE result references and gate diagnostics.
The review used CPU metadata and existing results; it ran no model or GPU job,
signed nothing and performed no actual draw, seal, freeze or launch.

## Package and scope

Candidate v12 verifies **1,408 bindings**, including all six governing documents:
protocol D.1, incorporated v5.1, concurrency policy v2, plan 9, coding-agent guide
PDF and joint-redesign proposal PDF. Missing documents and altered bytes fail
verification. D.1 implements DEC-062 and the lead's explicit permission for
multiple disjoint pairs per family. Planned near-miss slots remain 100;
allocation uses no outcomes, preserves the exact non-near backbone and keeps
disjointness, Hall checks, missingness and final lexical endpoint pairing.

The 360 core and 45 optional cell definitions compare equal to the prior matrix.
Only the governing identity and amendment bindings changed. Candidate, inputs v7,
forms v7 and operator sheet v6 consistently identify D.1 and typed cost receipt v2.
The operator now preserves typed cost evidence and passes the signed 6 GiB host
free-memory floor into queue launch, including the first worker.

Current identities:

| Artifact | SHA-256 |
|---|---|
| Candidate v12 | `9c82471b025c987f7dfab625eebe269d3eda4fff67b0c4778ed1d92700e6c722` |
| Inputs v7 | `980fab497ab30d57ecece2c987d5718eef01928d41a0fd5bd3d17dc7f7bb73ba` |
| Typed cost draft v2 | `28786b2aa2557823c7b04b3c312f9dd0c4641b838b6196719d015bf48c33838a` |

The earlier unsigned v12 preview, before host-floor forwarding, is retained in
`source_snapshot/`. Use `r1-63i-verification.json` and
`operator-protocol-current-dry.json` for the current package. Old preview digests
and historical approvals cannot authorize this package.

## Disposition of X16 findings

| Finding | Status | Evidence or remaining work |
|---|---|---|
| X16-01 normative closure | Closed | Six recursive dependencies bound; omission and mutation tests pass. |
| X16-02 cost schema | Partly closed | Typed producer and validator work; evidence and lead approval remain pending. |
| X16-03 complete costs | Open | Missing host peaks, full-validation costs and zsRE/MQuAKE full-endpoint measurements. |
| X16-04 pair units | Closed | Lead clarification and D.1 explicitly allow repeated families with disjoint pairs. |
| X16-05 request identities | Current draft repaired | v12/v7 requests refreshed. Future measurements and code changes require another refresh. |
| X16-06 publication producer | Open | Exact interface documented; no whole production recipe/freeze assembler exists. |
| X16-07 notes arithmetic | Closed | Claude's notes correction matches the recomputed table. |
| X16-08 substantive gates | Open | 17 gate IDs plus real population operations remain; verification grants no authority. |
| X16-09 unavailable firing | Closed | Corrected notes and raw-result review preserve unavailable telemetry for six v0/S1 profiles. |
| X16-10 protocol contradiction | Closed | D.1 replaces the independent-only prohibition with DEC-062. |

## Cost evidence and schedule

The producer verifies recipe/result/checkpoint identities and ordinary or batched
phase journals. It selects profile sources by declared provenance priority, never
by favorable scores. The canonical receipt is unsigned and has **45 explicit
pending-evidence reasons**. Merely setting an approval flag still fails admission.

| Quantity | Reproduced value | Interpretation |
|---|---:|---|
| Condition × dataset cost rows | 27 | Exact ceiling-table coverage |
| Rows with measured JAX device peak | 26 | Primary MQuAKE has no completed profile yet |
| Rows with measured process host peak | 0 | Free host memory is a different metric |
| Full near/revision rows measured | 9 | CounterFact only |
| New R1-64f profiles completed | 0/4 | Recipes inspected; execution belongs to Claude |
| Core solo estimate | 209.4 h | Declared table, not whole-matrix observation |
| Optional extension solo estimate | 12.15 h | Same qualification |
| Core elapsed projection | 126.91 h | Assumed 1.65 throughput factor |
| Combined process-time projection | 254.7825 h | `(209.4 + 12.15) × 1.15` |
| Proposed shared process budget | 750 h | Two workers × 375 h; unsigned |
| All cells using two padded attempt ceilings | 764.3475 h | Exceeds budget; not an expected runtime |

Device ceilings are measured JAX `peak_bytes_in_use` × 1.5, not total GPU driver
allocation. CounterFact stable v0 near/revision time is 344.44 s; other conditions
retain their own times instead of inheriting that one value. The approximately
30 s startup/validation allowance is an estimate. A 128-window development drift
assay is not full-validation evidence.

Four representative R1-64f profiles will fill useful gaps but do not measure
every other condition. Any transfer of their endpoint or host costs needs an
explicit reviewed assumption. The current producer also needs a source-bound
host-envelope/full-validation input extension when that evidence exists. Until
then, null measurements remain null. The launch floor of 6 GiB does not substitute
for a measured per-process host peak.

The 750 h proposal can stop execution before every permitted retry consumes its
maximum. This is compatible with DEC-052's explicit incomplete-inventory reporting;
it is not proof that all cells will finish. Keep the **October 9 experimental
stop**, leaving time before the October 15 presentation. The elapsed projections
do not establish a calendar completion date or include all outage risks.

## Development results independently checked

Eight corrected MQuAKE profiles were matched to their recipes, results and final
checkpoints. Bounded locality was recomputed from traces. These are development
results and do not represent the selected primary v5's pending new MQuAKE run.

| Condition | RET-GS | Bounded locality | Unseen firing |
|---|---:|---:|---|
| R1_nonlearned | 0 | 0/50 | 100/100 |
| v0_stable | 0 | 50/50 | unavailable; 0 scored/100 planned |
| matched_update | 0 | 50/50 | unavailable; 0 scored/100 planned |
| v0_live_C1 | 0 | 50/50 | unavailable; 0 scored/100 planned |
| v0_live_C2 | 0 | 50/50 | unavailable; 0 scored/100 planned |
| S1_LM | 0 | 39/50 | unavailable; 0 scored/100 planned |
| S1_literal | 0 | 49/50 | unavailable; 0 scored/100 planned |
| R1_learned_ff_v2 | 0.176667 | 47/50 | 7/100 |

S1 locality includes the continued base's difference from the original reference;
it is not a cap-only failure measure. Missing firing telemetry cannot establish
zero false fires. No result-based retuning or favorable seed search was performed.

The four new recipes share exact payloads between arms and include 300 edits,
checkpoints 100/300, near-miss 100, revision 50, locality 50 and outside 100. They
use historically exposed training/development sources, including older MQuAKE
sources needed for role capacity. They are not independent confirmation samples
or the separate DEC-056 occupancy diagnostic. Zero normalized-subject intersection
with certified confirmation pools was checked; their declarations still belong
in the next formal current-exposure attestation.

## Remaining scientific and operational limits

The primary family still has 63 intervals at nominal confidence
`1 - .05/63 = .9992063492063492`. All 21 MQuAKE 1,000-edit intervals remain
unavailable; 300-edit observations do not fill them and alpha is not redistributed.
Three realization clusters provide only nominal/approximate coverage. The empty
zsRE baselines remain material: 6,036/6,084 are empty, so acquisition against an
empty baseline dominates that population.

Open gate IDs are U01–U09 and U11–U18. The candidate reports 51 non-signature
blocker entries, including per-row cost gaps, the four development runs, missing
whole-bundle assembly and actual authorized population/gate operations. This is
a dependency inventory, not 51 independent experiments. The production interface
in `docs/tasks/R1-63i-production-bundle-interface.md` names available component
producers and the missing whole-package producer; a document is not an assembler.

Next: execute the four prepared development recipes with host-envelope telemetry;
obtain full-validation measurements and review any cross-condition extrapolation;
build and validate a complete typed cost successor; close the other scientific
gates and implement production assembly; refresh the candidate and all requests;
then conduct the actual approval/population workflow. HT-4f remains blocked until
a complete, valid signed cost receipt exists. Its eventual ledger must preserve
all development, unavailable-data and exploratory heavy-tail qualifications.

## Validation

The combined CPU regression suite passed **100 tests**. After forwarding the
signed host-memory floor, **18 focused operator/package/queue tests** passed
(ten overlap the regression set). Normative mutations, missing or tampered cost
evidence, endpoint construction and stale bindings are covered. X17 independently
reverified the current candidate and costs. These checks do not demonstrate GPU
runtime behavior, cost completeness, actual population construction or production
launch readiness.
