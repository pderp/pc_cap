# X16 — independent review of the Stage 4 signature package

2026-09-17, Codex, round 27. **Verdict: not ready for lead signature or launch.**
The CPU preparation is substantial, but remaining work includes technical evidence
and protocol repairs, not merely signatures. No GPU/model calls, actual draw,
seal, freeze or signature were performed by this review.

## Scope and provenance

Reviewed final protocol v5.2-D and incorporated v5.1 definitions, matrix DEC061,
queue policy v2, execution plan v2, candidate v9/forms v4, the unsigned cost
receipt v1, both allocation modes and eight corrected MQuAKE profiles. Then
checked the replacement unsigned operator package v11/forms v6 after the draw
hook and DEC-062 binding. Exact source hashes and raw-result references are in
`r1-x16-audit.json`; current package verification is in
`r1-x16-DEC062-addendum.json`. All paths here are relative to this log directory
unless stated otherwise.

Incoming v9 verified **744 bindings**, not the 728 stated in the lead queue.
The first replacement v10 verified 759; current v11 verifies **772**, with 17
open gate identifiers. A verified candidate is an internally bound draft, not a
production freeze. Its `launch_authorized` remains false. Old producer hashes
are preserved in `source_snapshot/`; v9/v10 now have intentional code/form drift
and must not be reused for current signatures. New request digests are required.

**Status correction:** the initial audit and real-pool diagnostic metadata
incorrectly called DEC-062 pending. The accepted DEC-062 row already selects B.
The addendum corrects that statement without rewriting the initial evidence.
The current unsigned forms select `family_coordinated`. The outstanding question
is whether the planned 100 means pairs or distinct families: this implementation
allows multiple disjoint pairs per family. No final allocation-contract approval
has been invented.

## Findings and required repairs

| ID | Finding | Consequence / next action |
|---|---|---|
| X16-01 | Final protocol incorporates normative v5.1 text, but neither incoming v9 nor current v11 binds that file. | Bind the complete normative dependency closure in a successor candidate and refreshed requests before signing. |
| X16-02 | Cost receipt v1 is unsigned and lacks the typed admission schema. | Even an in-memory `lead_approved=true` fails: `receipt register identity differs from v6`. Produce a fully bound typed successor; a flag edit is insufficient. |
| X16-03 | Explicit shared process-hour budget, admitted peak host/device ceilings and complete final-endpoint/full-validation cost basis are missing. | Obtain or identify measured evidence and admit exact ceilings. Padding partial development times does not establish full costs. |
| X16-04 | DEC-062 B is accepted, but the phrase “fewer than 100 families” is ambiguous. | Confirm whether repeated-family pairs are allowed; the diagnostic below uses that interpretation. Review the exact algorithm in the unsigned contract before admission. |
| X16-05 | Authorized hook/operator changes invalidate old request identities. | Use the successor unsigned package and re-dry at each step. No historical signatures are portable. |
| X16-06 | No production final-freeze/recipe publication bundle exists. | The owner must build all admitted final recipes and dependency bindings from the actual sealed population; the new CLI validates/publishes a supplied bundle. |
| X16-07 | Chain Q notes quote 206/125/+16 hours. | Current declared table reproduces 209.4 solo core, 126.91 projected wall, +12.15 solo extension. Proposed notes patch supplied separately. |
| X16-08 | Candidate exposes 17 open gates plus actual population operations. | Audit their real receipt evidence; do not describe the package as awaiting only a few signatures. Corrected comparator profiles are complete, but completion of those profiles is not closure of every gate. |
| X16-09 | Six v0/S1 corrected profiles have unavailable firing telemetry, while Chain Q notes show zero unseen false fires. | Report unavailable, 0 scored/100 planned; retain valid locality and retention results. Proposed notes patch supplied separately. |
| X16-10 | Final protocol expressly says “No family-coordinated allocation ... is authorized.” | Version/amend that normative paragraph to implement DEC-062, then rebind downstream requests. Current RNG mode and protocol text conflict. |

The independent-review lane permits new findings and edit requests only. No
reviewed protocol, cost receipt, notes, decision row or execution plan was changed.
The authorized D9/operator implementation and unsigned-mode binding are the
separate implementation lanes. Exact proposals are in
`../../docs/tasks/X16-edit-requests.md`.

## Reproduced inventory, budget arithmetic and uncertainty

There are **360 core cells plus 45 optional extension cells**, three datasets,
three realizations and five paired orders (100–104). Blocks contain 45, 45, 90,
90, 90 and 45 cells. All 27 declared condition/dataset wall ceilings equal the
listed solo cost times 3,600 times 1.5; this reproduces their arithmetic, not the
missing full-endpoint measurements.

| Block | zsRE solo h | CounterFact solo h | MQuAKE solo h | Total solo h |
|---|---:|---:|---:|---:|
| 1 | 5.90 | 9.60 | 2.75 | 18.25 |
| 2 | 7.20 | 18.30 | 4.95 | 30.45 |
| 3 | 13.10 | 27.90 | 7.70 | 48.70 |
| 4 | 13.10 | 27.90 | 7.70 | 48.70 |
| 5 | 15.00 | 38.40 | 9.90 | 63.30 |
| 6 | 5.25 | 5.25 | 1.65 | 12.15 |

Core sum: **209.40 h**; extension: **12.15 h** (12.2 rounded); combined: **221.55 h**.
At the assumed 1.65 throughput factor, projected elapsed time is 126.91 h core or
134.27 h with the extension. These are schedule projections; no whole-matrix
throughput measurement was reproduced. Initialization, complete endpoint costs,
full validation, contention, retries and host failures can erode the margin.

With two workers, effective per-attempt ceilings apply 1.15 once to the stored
1.5-padded solo ceilings. Summing those ceilings gives 361.215 core process-hours
or 382.17375 including extension. If every cell consumed two whole ceilings, the
bounds would be 722.43 / 764.3475 process-hours. These are derived bounding sums,
**not** newly requested/admitted budgets or predictions of actual consumption.
Overlapping process time adds to the budget; elapsed wall time does not replace it.

The primary family remains 7 comparisons × 3 datasets × 3 metrics = **63
intervals**, nominal confidence `1 - .05/63 = .9992063492063492` per interval.
All **21 MQuAKE 1,000-edit intervals remain unavailable**; no alpha is redistributed
and no 300-to-1,000 claim is extrapolated. The adopted bootstrap remains float64,
seed 0, 10,000 draws, linear quantiles and three realization clusters with five
paired orders retained inside each. With only three clusters, simultaneous
coverage is nominal/approximate, not established by these arithmetic checks.
Classifier margins and strict inequalities trace to DEC-057/058; adopted secondary
benchmarks trace to DEC-059 and remain descriptive.

Population certification is 6,084 / 6,121 / 2,161 distinct subjects versus demands
4,050 / 4,050 / 1,950, margins 2,034 / 2,071 / 211. All 93 Hall subset checks pass.
MQuAKE has 2,214 eligible items but only 2,161 subjects and 2,158
first-representative revision-compatible subjects. These distinctions must remain
visible. Of 6,084 zsRE teacher baselines, **6,036 are empty**; most zsRE results
therefore measure acquisition against an empty base answer. E.2 passes do not
prove that the original base knew those facts.

## Raw-result check: corrected development MQuAKE profiles

Each row was matched to its exact recipe, result, checkpoint and receipt; bounded
locality was recomputed from baseline/query traces. These are development
profiles, not confirmatory cells. Attempt wall times below exclude any outer
startup envelope. ES is the reported terminal retention ES, 1.00 in all eight.
The primary selected reader is not an extra ninth row in this comparator table.

| Condition | Attempt s | RET-GS | Bounded locality | Unseen firing |
|---|---:|---:|---|---|
| R1_nonlearned | 331.32 | 0.000000 | 0.0/50 | 100/100 |
| v0_stable | 1168.38 | 0.000000 | 50.0/50 | unavailable (0 scored/100 planned) |
| matched_update | 1002.25 | 0.000000 | 50.0/50 | unavailable (0 scored/100 planned) |
| v0_live_C1 | 1147.95 | 0.000000 | 50.0/50 | unavailable (0 scored/100 planned) |
| v0_live_C2 | 989.27 | 0.000000 | 50.0/50 | unavailable (0 scored/100 planned) |
| S1_LM | 1162.69 | 0.000000 | 39.0/50 | unavailable (0 scored/100 planned) |
| S1_literal | 1164.91 | 0.000000 | 49.0/50 | unavailable (0 scored/100 planned) |
| R1_learned_ff_v2 | 383.34 | 0.176667 | 47.0/50 | 7/100 |

For the six v0/S1 rows, every firing field is `null` with status `unavailable`.
That cannot be converted into zero firing. S1 locality compares its continued
base against the original-base reference, so the 39/50 and 49/50 values should
not be described as a cap-only failure rate. The random reader's locality floor
and the ungated reader's 7/100 firing are observed values. All these comparisons
remain tied to their development population and specific attempt identities.

## Allocation diagnostic and interpretation

Both modes use one predeclared diagnostic seed (20260917); no selection of a
favourable seed occurred. Non-near reservations are byte-identical between modes.
The diagnostic files under assets explicitly authorize nothing.

| Dataset | Independent matched, r0/r1/r2 | Coordinated matched, r0/r1/r2 | Planned each |
|---|---|---|---:|
| zsRE | 21/16/18 | 100/100/100 | 100 |
| CounterFact | 63/72/68 | 100/100/100 | 100 |
| MQuAKE | 77/79/79 | 100/100/100 | 100 |

The coordinated algorithm selects disjoint same-family pair units from the pool
remaining after the exact independent edit/outside/revision backbone. Multiple
pairs can share a family. It records RNG states and missing slots, retains Hall
checks and global disjointness, and uses no outcomes. Endpoint ordering still
uses DEC-061 lexical pairing within reserved roles. Family coordination changes
membership and thus the assay population; its count improvement is not a model
performance improvement. It tests exact relation/template specificity, not
semantic nearest-neighbour robustness. Requiring distinct families would change
this contract and these feasibility results.

## Decision trace DEC-033–061

The table covers all 29 requested identifiers, including the withdrawn 038
proposal. Sources and exact accepted-row hashes are in the audit JSON. A text
trace is not evidence that all associated execution gates have been completed.

| Decision | Disposition | Governing text / evidence |
|---|---|---|
| DEC-033 | adopted; budget superseded by044 | Final text opening + v5.1 §§2,5,6: margins, fidelity, fresh roles; plan9/guide remain specification. |
| DEC-034 | adopted delegated amendment | v5.1 §2 conditions/control table, §4 exclusion register, §§5–7 full-episode/cost/restoration requirements; Stage3 coupling remains conditional. |
| DEC-035 | adopted delegated control | v5.1 §2 v0_stable row; matrix includes45 cells of this condition. |
| DEC-036 | historical correction; outside eight core arms | spec_defects SD-24 and stage2 notes preserve ePC energy correction; historical v0 SE-E is not rerun or silently relabelled. |
| DEC-037 | training-only source decision | v5.1 §4/current evidence exclude CF training exposures; train_pool_counterfact_v1 records3000; no reuse as confirmatory observations. |
| DEC-038 | withdrawn proposal; no accepted decision row | lead_queue items11/recovery and stage2_report: dropping learned reader was withdrawn. Primary v5 remains learned. |
| DEC-039 | training-only source decision | v5.1 §4/current evidence reserve all6000 zsRE candidates, including the3000 training subset; E.2 is unchanged. |
| DEC-040 | adopted two S1 treatments | v5.1 §2 S1_LM/S1_literal and §3 fidelity; both conditions are in block5. Final-v5 budget matching still U03. |
| DEC-041 | adopted exclusion policy with later versions | v5.1 §4 + final Population and exposure; operative v6 policy includes all later declaration snapshots. |
| DEC-042 | accepted exception | Final population and v5.1 §4: CounterFact old-pool-membership-only exception; not a wholly fresh external source. |
| DEC-043 | accepted rare-token gate | v5.1 §1/2 and primary_condition_v5; ungatedv2 is the optional45-cell package contrast. |
| DEC-044 | accepted full scope | Final Receipt contract:360core+45optional; 15h envelope superseded, no scope cut. |
| DEC-045 | accepted third dataset | Final layout: zsRE, CounterFact, MQuAKE-CF; only MQ cadence later changed by060. |
| DEC-046 | training/split proposal superseded by operational v3 slices | v5.1 §1/4 and primaryv5 source bindings identify actual self-contained MQ train/dev versions; initial proposed counts not final capacity. |
| DEC-047 | accepted LM fidelity result | v5.1 §1/3 identifies lr1e-8 LM continuation, KL.0004736076 and loss-.0088596493; failed lr1e-6 remains historical. |
| DEC-048 | accepted source-query exemption; scope later060 | Final Population and exposure + v5.1 §4: true-fact query roles exempt for later counterfactual edits, other exclusions retained. |
| DEC-049 | accepted three-dataset selection | v5.1 §2 reference selection and primary_condition_v5; exact weight average is bound, not reselected. |
| DEC-050 | accepted selection gate | v5.1 §2: maximize mean RET-GS with zsRE unseen≤.10 at100 and LS≥.98; distinct from confirmatory unseen≤.15. |
| DEC-051 | accepted execution order | Final block inventory plus matrix queue fields:45,45,90,90,90 then optional45; all coordinates reproduced. |
| DEC-052 | accepted complete-or-explicitly-incomplete reporting | Final Costs/inventory: October9stop, DEC052 inventory and full scope; earlier cost review is delegated but future schedule receipt still needed. |
| DEC-053 | accepted bounded equality | Final near family/scoring + v5.1 §5; raw corrected MQ locality traces independently rescored, termination diagnostics retained. |
| DEC-054 | accepted exploratory κ pilot | v5.1 §6 side-panel scheduling + kappa_pilot_v3 + heavy_tail_counter_review §4; preliminary hints, not coupled free energy or one-κ test. |
| DEC-055 | accepted development stress panel | v5.1 §6 + ht_development_panel_v1: six cells,100edits,20/60/70/80/100 probes,4GPUh ceiling; never a confirmatory replacement. |
| DEC-056 | accepted MQ occupancy diagnostic | R1-76b artifacts and final actual300 caveat: historically exposed700-row review, common outside100/300, no1000claim. |
| DEC-057 | accepted63-interval family | Final analysis + incorporated v5.1 §5.3:7×3×3, .05/63, 10000draws, seed0, float64, linear quantiles, three realization clusters. |
| DEC-058 | accepted classifier | Incorporated v5.1 §5.3 + r1_49g_inference; strict bounds, negative priority, unchanged .05/-.02/-.01 margins. |
| DEC-059 | accepted secondary thresholds | Incorporated v5.1 §5.1 and matrix secondary_benchmarks; MQ1000 thresholds unavailable, no transferred300pass. |
| DEC-060 | accepted optionD | Final population/cadence:1000/1000/300, demands4050/4050/1950, three realizations; MQ21 primary intervals unavailable. |
| DEC-061 | accepted NM-template-v1 | Final adopted-family section and shared source validator: different subjects/exact family, neighbour baseline equality, planned100 fixed. Allocation is separately adopted by DEC-062; the current protocol text still needs amendment. |

DEC-062 is outside the originally requested 033–061 range but is now operative:
B is recorded in the decision ledger and selected in the unsigned RNG/operator
inputs. Its exact row is preserved in the addendum. No decision to change the
primary arm, shrink scope or move the October 9 stop is inferred.

## Readiness, schedule and handoff

The experimental stop is **October 9**, leaving October 10–14 for analysis and
presentation preparation before October 15. The 127-hour core projection appears
compatible with the stated launch window, but the supposed 2.7× buffer is not a
validated allowance for every unmeasured cost. Resolve the full-endpoint cost
basis before describing the schedule as admitted. A 128-window, 16,256-position
drift sample is not the required complete validation split. U08/U16 and typed
resource admission remain substantive work even though Chain Q finished.

Before a signing sitting: settle pair-unit semantics, publish the DEC-062 protocol
amendment and normative bindings, produce the complete typed cost evidence and
budget, prepare final publication/recipe machinery, and map every open gate to
its actual closure evidence. Then execute the lead-controlled sequence without
seed retries. After a valid cost signature, HT-4f can publish the final claim
ledger; it is correctly blocked now. Failure/incomplete reporting and shared
process accounting remain mandatory throughout execution.

This review independently reproduced source inventories, allocation feasibility,
corrected-profile locality and specified schedule arithmetic. It did **not**
remeasure full final-cell costs, peak memory, whole-matrix throughput or the full
validation split, and did not create confirmatory results. Those limitations are
part of the readiness verdict, not claims that the missing work has failed.
