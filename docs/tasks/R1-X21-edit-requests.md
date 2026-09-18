# R1-X21 — report/protocol coverage edit requests

Review complete; **requests only, none applied**. September 18, 2026. The current report correctly preserves the primary 63-interval family, MQuAKE unavailability and prospective omissions, but is not yet a complete final scientific report under D.4's inherited reporting obligations. Successful placeholder filling establishes document wiring, not exhaustive protocol coverage.

Use [the machine-readable coverage audit](../../logs/r1_round40/x21-coverage.json) and [table/figure crosswalk](../../logs/r1_round40/x21-review.md). The review follows D.4 → D.3 → D.2 → D.1 and the incorporated v5.1/plan/PDF closure; later amendments take precedence. D.2's withdrawn cap-fidelity veto is not revived.

## X21-G1 — carry the remaining declared tail fields into the report

**Scope:** `scripts/r1_d14_report.py`, template Table 9; new tests. Formatter change; measured results remain unchanged.

v5.1 §5.2 requires `exp(mean ΔNLL)`, maximum **and position**, as well as signed/positive means and ES99; D.2/D.3 retain these and add ES95 and zero-mass summaries. Current `tails` rows omit fields already in the analysis JSON:

- `/cells/i/checkpoints/n/secondary/full_validation/references/ref/loss/{exp_mean_signed,exp_mean_signed_overflow,maximum_signed,maximum_location,maximum_tie_count,atom_zero_signed,atom_zero_positive}`. Keep corresponding KL maximum/location and zero-mass summaries under their own metric/reference label.
- `/cells/i/checkpoints/n/secondary/sampled_drift/references/ref/{maximum_position,zero_positive_n}`. The sample's `exp(mean_signed_nats)` is a derived display value; bind its input, declare the operation and handle overflow explicitly. Do not invent full-population zero counts from the sample.

Add columns or an indexed tail-detail appendix, retain JSON-pointer provenance and update the template's field inventory. Keep signed maximum distinct from positive-part maximum, and document first-location/tie conventions from the producer. **Acceptance:** nonzero maximum/location, tied maxima, all-negative loss changes, all-zero KL and overflowing exponential fixtures; full/sample references remain separate; every output field binds or declares a checked derivation. Existing 63 primary rows and classifiers identical before/after.

## X21-G2 — expose the joint cap-fidelity benchmark flag

**Scope:** report formatter, Table 7 and tests.

D.3 explicitly requests the joint numeric benchmark pass flag separately from evidence completeness and primary scientific admission. The current table has four per-reference labels across two rows, plus `admission_veto=False`, but omits `/cells/i/cap_fidelity_benchmark/passes`.

Add `joint_cap_benchmark_passes` using that existing field (repeat by reference if convenient), `scientific_admission` and appropriate completeness status. A missing joint flag is unavailable, not false or true. **Acceptance:** all four labels pass, either KL fails, either NLL fails, incomplete evidence, and equality at both bounds; primary classifier and admission remain unchanged by numeric label changes.

## X21-G3 — render the admitted historical-v2 package comparison

**Scope:** report formatter, a clearly secondary table, template and tests.

v5.1 §5.3 retains the separately admitted historical-v2 comparison; D.4 keeps the optional extension. The complete rehearsal's `/historical_pointwise_contrasts` contains **eight** `contrast.role == "secondary"` package comparisons: zsRE/CounterFact at 100/300/1000 and MQuAKE at 100/300, **24 metric rows**. No output binding currently references this collection. Per-arm trajectories do not replace paired contrasts.

Select these secondary-role rows explicitly; show dataset, checkpoint, comparison, planned/observed pairs, estimate, three realization means, existing pointwise interval and availability. Keep `classification="secondary_descriptive"`; do not present `draft_margin_classification` as an adopted confirmatory verdict. Do not promote the other legacy pointwise rows over the current adjusted primary family. **Acceptance:** extension admitted and not admitted, missing pair, absent MQuAKE1000; the nominal primary family remains exactly63 and optional descriptive rows cannot change its alpha or classifier.

## X21-G4 — join execution accounting and distinguish endpoint completeness

**Scope:** report composition with existing D11/D13 output, formatter/template and tests. No queue-policy change.

D.1 DEC-052 requires declared/complete/partial/failed cells, missing checkpoints/endpoints, known charged costs and unknown-cost records, including retries. The skeleton defers accounting to D11/D13 but has no supplied report binding or table for it. A reader cannot recover charged process time or exhausted retries from the filled report alone.

Accept an explicit independently verified D11/D13 report binding with matching matrix/receipt-root identity; include known process spend, unknown-cost records, retry/host-failure status and block reconciliation. If absent, retain an explicit unavailable accounting section. Do not derive process cost from summed checkpoint timings or silently treat missing time as zero.

Also expose `/cells/i/{primary_metrics_complete,full_validation_complete,sampled_drift_complete,unreceipted_checkpoints}` alongside existing fields when supplied. The installed `endpoint_complete` combines **full-validation and sampled-drift completeness only**; it does not establish completion of every near-miss/revision/composition case. Label its scope accurately and retain each challenge's independent planned/scored/missing inventory. Do not widen scientific admission predicates while fixing the report.

**Acceptance:** terminal artifacts with incomplete near/revision rows; complete validation but unavailable composition; exhausted retry; unknown process envelope; partially complete block; different matrix/accounting snapshot refused. Both workers and failures remain charged exactly once through the existing accounting source.

## X21-G5 — bind narrative interpretation evidence explicitly

**Scope:** report sources and S1 paragraph, template and tests.

The report links `docs/R1_U03_interpretation_memo.md`, but its `source_bindings_sha256` does not bind that file. The fixed zsRE6036/6084 statement likewise should bind `logs/r1_round25/r1-x15-independent.json`. Bind the applicable D.4 normative closure for narrative statements, not only the analysis implementation/fixture population.

Use the memo's precise qualification: **“U03 retains the DEC-047-certified S1_LM checkpoint and the fidelity-valid S1_literal checkpoint as historical continuation controls under DEC-040; their forward-token budgets were reconciled to reader v1, and their contrasts with primary v5 are interpreted as comparisons with these specified controls, not as exact-v5-compute-matched tests or as exclusion of all continued-base explanations.”**

The current abbreviated wording loosely attributes both controls to DEC-047. Preserve the correct original-base locality versus own-cap-off near-miss distinction already in the template. **Acceptance:** changed memo/characterization bytes force a new bound snapshot; no extra training run or compute-match assertion; historical base certification remains distinct from full-validation cap labels.

## X21-G6 — carry composition through analysis and explicitly inventory it

**Scope:** an additive receipt-bound composition reporting module is preferable during this freeze; any edit of the installed `scripts/r1_75_analysis_stage4_v1.py` requires the owner's versioned-source procedure. Report/template integration and focused tests needed.

This is an **analysis omission**, not just a missing template column. v5.1 §5.1 declares descriptive composition and D.1 retains dependency-closed, outcome-independent case membership. `scripts/r1_77b_sealed_backend.py` writes `checkpoint.endpoints.composition` at the terminal checkpoint; the present `summarize_checkpoint` ignores it, and R1-49g does not restore it. The X21 audit adds one valid-shaped synthetic case to a synthetic raw checkpoint and obtains an identical analysis summary: the field is lost. No real confirmatory payload was opened.

Read only receipt-verified checkpoint sections and an independently bound planned composition inventory; validate IDs, dependencies, case/question counts and source identities. Preserve evaluable/scored/unavailable/conflict counts, all-three-case success and question-level success. Missing planned cases retain their denominator; zero planned cases are explicitly not applicable rather than a perfect score. Label the assay as **isolated direct-question dependency composition, not in-stream retained-memory composition**. No success margin or primary hypothesis is added.

**Acceptance:** complete case, missing case, source/dependency conflict, all cases unavailable, zero planned cases, all-three versus question denominator, and altered checkpoint/expected-ID refusal. Ensure a real positive or negative composition result reaches the final report unchanged. If a draw yields no eligible cases, report that actual inventory rather than substituting historical development cases.

## X21-G7 — keep resource ratios unavailable until the measurement adapter exists

**Scope:** explicit engineering follow-up, not an instruction to manufacture measurements or change thresholds.

The renderer faithfully reports the installed analyzer's missing resource adapter. v5.1 §5.1 declares persistent-state, peak-memory and charged-time feasibility against separately admitted ceilings; current analysis returns all three ratios unavailable (`peak_budget_ratio`, `state_budget_ratio`, `wall_budget_ratio`). A signed cost receipt alone does not fill measured memory/time fields.

Provide a verified measurement/ceiling adapter with units, cell identity, process boundary and high-water-versus-phase semantics; or retain prominent unavailable status in the final report and discuss its limit. **Acceptance:** measured equality passes, actual exceedance fails, missing observation remains unavailable, lifetime high-water is not labelled phase-specific, and a transferred ceiling is not labelled a measured result. This is separate from scientific cap-fidelity labels.

## X21-G8 — correct the incomplete-block wording

**Scope:** one template sentence, no analysis change.

Current: “An interval unavailable because of an incomplete block or missing paired population remains unavailable; a synthetic positive label is never a research finding.”

Replacement: **“An interval remains unavailable when its own required paired population or admission is incomplete. An unrelated incomplete comparison or block does not invalidate an otherwise complete admitted comparison. A synthetic positive label is never a research finding.”**

v5.1 §5.3 allows a complete comparison to be analyzed while another is unavailable. The installed primary implementation checks its paired populations; the template should not imply a blanket complete-block gate. Preserve the complete-block inventory for its separate execution-reporting purpose.

## Order and coordination

G1/G2/G3/G5/G8 are report-layer changes and can share one tested formatter/template revision. G4 can proceed independently as a reporting join; G6 as an additive composition consumer; G7 needs measured resource/ceiling inputs. All can avoid editing the operator, queue, trainer or current signing-bound sources. Apply no bound-source change during the signing session. These requests do not invalidate measured tail/retention numbers, the fixed63 family, D.4 scope or current numeric fidelity interpretation; they identify reporting completeness and provenance work still needed before a final scientific release.
