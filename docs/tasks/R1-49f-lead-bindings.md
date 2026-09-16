# R1-49f — proposed Q11–Q13 bindings for the lead

Status: proposals ready for orchestrator review; **no new decision has been accepted here**.
Agent: Codex, 2026-09-16. Inputs: protocol draft v5, matrix v5, primary condition v5,
DEC-033/048/050/052/053/054/056 and freeze candidate v5. Outputs: this document.
Verification: checked the actual seven primary contrasts, three datasets, 360 core cells and 45
unadmitted historical-v2 extension cells against matrix v5. GPU cost: zero. No protocol, decision
log, source module or lead queue was changed. The orchestrator posts the questions.

The experiment deadline is **October 9**, with September 20 the cost/scope admission checkpoint.
These decisions must be fixed before confirmation outcomes are inspected. The numerical secondary
proposals below are informed by development results; they are not pre-existing accepted thresholds.

## Q11 / U12 — comparisons and multiplicity

**Proposed default:** retain all seven registered primary-vs-control comparisons separately in each
of zsRE, CounterFact and MQuAKE: 21 contrast/dataset claims at checkpoint 1,000. Controls are
R1_nonlearned, v0_stable, matched_update, v0_live_C1, v0_live_C2, S1_LM and S1_literal.
Use one family of 63 metric intervals (21 comparisons × RET-GS, ES, LS), with a nominal Bonferroni
family error budget 0.05. Each two-sided interval has confidence `1 − .05/63 = .9992063492063492`,
with equal tail probabilities `.05/(2*63) = .0003968253968253968`.
Keep the existing resampling procedure: float64; seed 0; 10,000 bootstrap draws; NumPy linear
percentiles; sample the three fresh realization means with replacement and keep all five paired
orders together inside each realization. Only complete independently declared paired populations
enter a contrast. No imputation, order-level pseudoreplication or denominator repair.

This is a **nominal multiplicity adjustment of approximate bootstrap intervals**, not an exact
finite-sample familywise guarantee. There are only three independent realization clusters: the
bootstrap has very little independent information, and these extreme quantiles will be unstable
or close to the observed extremes. Report all three realization estimates, the unadjusted 97.5%
interval, and the adjusted interval. A narrow interval with three clusters is not strong validation
of its coverage. Any choice to increase realizations is a new scope and resource decision.

Alternatives for the lead:

- Retain pointwise 97.5% intervals and explicitly decline any familywise-confirmatory positive
  claim. This preserves the current implementation but changes the strength of the conclusion.
- Name a smaller primary family (for example the learned-vs-nonlearned contrast in three datasets),
  with the other controls secondary. This improves precision but changes the approved comparison
  hierarchy; it requires an explicit decision, never a retrospective choice of favorable controls.

The historical-v2 contrast is a secondary **package** comparison, not a same-weights gate ablation.
Its 45 cells remain separately subject to allocation approval. Any κ comparison is outside this
primary family and requires its own final secondary admission. No extra contrast enters by adding a
recipe to a queue. Checkpoints 100 and 300 are descriptive trajectories, not further primary tests.

Downstream: set the final matrix's multiplicity status/family/confidence; update the protocol;
make the analysis output distinguish adjusted and unadjusted intervals; test the selected quantiles
and exact contrast inventory; rebind analysis code and gate U12 in the final freeze. The existing
analysis has a configurable confidence but does not by itself create a validated multiple-testing
procedure. This document does not apply that implementation change.

**Exact proposed insertion into §5.3:**

> The primary family consists of the seven prespecified primary/control contrasts separately in
> each of three datasets at 1,000 attempted edits (21 contrast/dataset claims). RET-GS, ES and
> bounded-text LS yield 63 component intervals. The family uses a nominal Bonferroni allocation
> of 0.05 across these intervals: each two-sided percentile interval has confidence
> 0.9992063492063492 and equal tails 0.0003968253968253968. Resampling uses seed 0, 10,000 draws,
> float64 and linear quantiles, with the three independently drawn realization means as clusters
> and all five paired orders retained within each cluster. Classifications use these adjusted
> bounds. Pointwise 97.5% intervals are also shown and never substituted for adjusted bounds.
> This is approximate bootstrap inference with only three independent clusters; exact familywise
> coverage is not claimed. Missing planned paired populations make that comparison unavailable.
> Earlier checkpoints and the separately admitted historical-v2 package contrast are secondary.

## Q12 / U13 — classifier and fidelity boundary conventions

**Proposed default:** retain DEC-033's accepted effect margins and the current proposed four-way
classifier, but bind every inequality and use Q11's chosen interval family. Let Δ denote primary
minus control, with ΔG = RET-GS, ΔE = ES, ΔL = LS; L and U are the corresponding lower/upper bounds.

| Classification | Exact test, evaluated in this order |
| --- | --- |
| unavailable | Any required planned paired primary population or admissibility input is incomplete |
| negative | `U_G < .05 OR U_E < −.02 OR U_L < −.01` |
| positive | `ΔG >= .05 AND L_G > 0 AND L_E > −.02 AND L_L > −.01` |
| qualified | Not negative; `ΔG >= .05 AND L_G > 0 AND ΔE >= −.02 AND ΔL >= −.01`, while at least one preservation lower-bound test does not pass |
| inconclusive | Every other complete, admitted case |

Negative has priority because interval/point combinations should not produce conflicting labels.
A lower bound exactly on a preservation margin does not pass its strict test; an upper bound exactly
on a negative margin does not meet the strict negative test. A point ΔG exactly .05 meets the point
effect-size requirement. These conventions are proposals for final binding, not newly accepted margins.

For continued-base fidelity, retain the accepted upper limits: mean KL at most .001 nats and mean
signed loss increase at most .01 nats on the frozen validation population. Equality **passes** these
upper-bound checks. Both complete measurements are required; missing/nonfinite values fail admission.
Do not compare maximum loss or ES99 against these mean limits, and do not replace signed mean loss
with positive-part mean harm. Fidelity failure does not justify silently removing a required comparator.
The owner records an admission failure and returns to the lead's matrix/scope decision.

DEC-053 applies to both LS margins and near-miss preservation: compare the bounded decoded texts;
retain termination, truncation and terminated-match diagnostics separately. Equal bounded strings
can count as preserved even when both generations truncate. Do not substitute the older
termination-required LS numbers in the classifier.

Alternatives: classify qualified cases as inconclusive (simpler reporting, fewer positive-sounding
labels), or require `L_G >= .05` for a positive effect-size claim (substantially stronger than the
current proposal, likely harder with three clusters). Either needs an explicit protocol change.

Downstream: boundary-value classifier tests; confirmed assay convention; final fidelity receipts
for S1 conditions and exact continued-NPZ identities; U13 closure. Draft v5's stale descriptions of
LS/κ status must be reconciled in the owner-approved final protocol.

**Exact proposed insertion into §5.3 and fidelity subsection:**

> With complete admitted populations, classify negative first when U_G < 0.05 or U_E < −0.02 or
> U_L < −0.01. Otherwise classify positive when ΔG ≥ 0.05, L_G > 0, L_E > −0.02 and L_L > −0.01.
> Otherwise classify qualified when ΔG ≥ 0.05, L_G > 0, ΔE ≥ −0.02 and ΔL ≥ −0.01 and at least one
> preservation lower-bound test is unresolved; classify remaining complete comparisons inconclusive.
> Missing required planned paired populations produce unavailable, not a classification. All bounds
> use the multiplicity procedure above. LS is bounded-text equality under DEC-053; termination and
> truncation remain reported diagnostics. Fidelity admission requires complete finite mean KL ≤ .001
> nats and mean signed loss increase ≤ .01 nats on the fixed validation population. Equality passes
> those upper bounds. These are mean constraints and imply no bound on tail harm.

## Q13 / U14 — unseen, revision and scaling benchmarks

**Proposed default:** bind the following as **secondary descriptive pass/fail benchmarks**, with
complete fixed denominators and uncertainty reported, without extending the primary classifier or
claiming a simultaneous secondary error guarantee. Their distinct purpose must remain visible:

| Quantity | Proposed benchmark | Meaning / qualification |
| --- | --- | --- |
| Unseen false-fire rate F at actual occupancy 1,000 | `F <= .15` | Deployment-tolerance proposal; **not** DEC-050's .10 development selection gate |
| Common-outside occupancy change F1000−F100 | point difference inside ±.05; any equivalence claim additionally needs its entire paired 95% interval inside ±.05 | Exactly the same outside100; missing actual occupancy makes it unavailable |
| Latest revision success | `R_latest >= .95` | Complete 50-case inventory; a per-cell rate requires at least 48/50 |
| Reappearance of any older alias | `A_old <= .02` | At most 1/50 in a full cell, not a guarantee of zero future failures |
| Supported semantic revision observer | `R_semantic >= .95` | At least 48/50; unsupported internal semantics stay unavailable |
| RET-GS change from 100 to 1,000 edits | `D_G >= −.05` | Horizon comparison; histories differ, so this is not the same-item paired retention effect |
| ES / bounded-text LS change from 100 to 1,000 | `D_E >= −.02`, `D_L >= −.01` | New scale tolerances proposed here; DEC-033's between-condition margins do not automatically authorize them |
| State bytes, peak memory, wall time | `M <= B`, `P <= Pmax`, `W <= Wmax` | Numbers must come from September20's approved chain-I ceilings; none invented here |

Benchmark cells and dataset macro summaries must both be shown; do not use a passing macro to hide
an individual cell failure. A macro is the prespecified equal average of realization/order rates,
not a pooled count that changes weighting. For equivalence, report the exact aggregation and cluster
interval design; do not infer equivalence because a difference interval includes zero. The 50-case
integer resolution is explicit. Composition remains descriptive, with exact dependency coverage.

Alternatives: keep all secondary thresholds unbound/descriptive (least commitment); choose stricter
unseen .10, zero observed old-alias returns, or smaller scale losses (more demanding, possibly
inconsistent with intended deployment tolerance); or register secondary confirmatory claims with a
separate multiplicity family and adequacy/power review. The last option needs additional design work
before freeze and should not be assumed to fit the present schedule.

DEC-056's historically exposed MQuAKE diagnostic has only occupancies 100 and 300. Its 1,000 point
and the corresponding F1000−F100 benchmark stay unavailable; its reduced cadence does not waive
any confirmatory requirement. Historical teacher provenance and bounded alias-review limits travel
with that development diagnostic.

DEC-054 approves the pilot and its interpretation, not automatic admission of κ to the final matrix.
The final registered HT-3d verdict controls eligibility. Current coupled-arm retention fails the floor;
only a final passing verdict permits consideration of a separately declared secondary arm with exact
weights, κ, cost ceiling, contrast, and pilot provenance. A passing pilot still needs final lead admission.
The clip2 control is ceiling-matched only to κ=.5. There is no silent κ replacement of primary v5.

Downstream: record Q13's chosen numbers/status in the final protocol and matrix; implement separate
secondary benchmark reporting without changing the primary classifier; freeze complete endpoint
inventories and references; keep unknown resource ceilings and unsupported metrics unavailable.

**Exact proposed insertion into §5.1:**

> Secondary descriptive benchmarks are u_max=.15, δ_F=.05, r_min=.95, a_max=.02, s_min=.95,
> δ_G=.05, δ_E=.02 and δ_L=.01. These values are newly admitted secondary tolerances, not inherited
> from development selection or between-condition margins. Full-inventory rates require every planned
> case; unsupported semantic observers and missing actual occupancies remain unavailable. Report
> cell-level outcomes and equally weighted dataset macro summaries. An occupancy equivalence claim
> additionally requires the entire prespecified paired 95% interval to lie within [−.05,+.05] for
> the same outside100 at both occupancies. Different-history scale comparisons remain descriptive.
> Resource ceilings are the separately approved September20 chain-I values, with equality passing.
> The primary classifier is unaffected; no simultaneous secondary significance guarantee is asserted.

## Handoff / unresolved

The orchestrator should present each default and alternatives as a separate lead decision, then
apply approved wording in a versioned final protocol. Until those decisions and their tested analysis
implementation are bound, U12–U14 remain open. No live file is updated merely because a default appears
in this memo. Cost and protocol admission remain separate from the October9 hard experiment stop.
