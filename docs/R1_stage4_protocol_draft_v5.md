# Revision v1 — Stage 4 protocol draft v5 (R1-49e)

**Development draft, 2026-09-16. Experimental work stops October 9; presentation October 15.**
DEC-050–053 are accepted. This document grants no draw, seal, freeze or launch authority.
Scope remains **360 core cells plus 45 separately admitted extension cells**. The development reference is
**primary v5**, selected under DEC-049/050. Final protocol, population, costs and scientific admission remain open.

Sources: [primary v5](../manifests/revision_v1/primary_condition_v5.json),
[selection audit](../logs/r1_round16/selection_audit.json),
[register v6](../manifests/revision_v1/exclusions_frozen_v6.json),
[matrix v5](../manifests/revision_v1/run_matrix_v5.json),
[DEC-050–053](decisions.md), and [R1-75 cell analysis](../logs/r1_round17/R1-75-development.md).
The predecessor is [draft v4](R1_stage4_protocol_draft_v4.md); its earlier evidence remains historical.

## 1. Question and scope

Can a small editing memory retain requested facts and their paraphrases, reject unrelated requests and preserve
ordinary language modeling while the base and reusable reader/controller weights remain fixed? Within each stream,
only declared support-driven episodic state changes. A low average language-model loss change can coexist with
substantial harm on a small number of token positions; both quantities are research outcomes.

DEC-043 accepts the rare-token gate. DEC-044 retains full scope and supersedes the 15-hour envelope.
DEC-045 retains CounterFact and adds MQuAKE-CF. The operational MQuAKE slices are self-contained training v3
(500 items) and development v3b (100); historical exposure is not erased by shrinking today's slices.
DEC-047 binds the fidelity-passing S1_LM continuation at weight learning rate 1e-8.
DEC-048 accepts the query-role exemption with the caveat in §4. DEC-049 admits run/checkpoint candidate selection;
DEC-050 fixes its common-population criterion. DEC-051 fixes block order, DEC-052 permits honest incomplete reporting,
and DEC-053 fixes bounded text equality for locality and near-miss endpoints.

Episodically trained bases, alternating BP/ePC on matched episodes, settled/feedforward inference and the retrained-cap
2×2 remain separately admitted plan-9 branches. Absence of these experiments is not a negative result.
The learned/random contrast compares deployed packages with different architecture, features and gates.
It does not isolate a causal effect of learning alone.

## 2. Conditions and selected reference

Eight conditions × three datasets × three fresh realizations × five orders give **360 core cells**.
Datasets: zsRE, CounterFact and MQuAKE-CF. Checkpoints: **100, 300 and 1,000 attempted edits**.
Record actual retained occupancy separately. Draft realization seeds are 0/1/2 and order seeds 100–104.
The constructor seed remains 0; **selected reader training seed is 2**, not the constructor seed.
Training seeds on the same development split are not independent data realizations.

| Condition | Fixed deployment |
| --- | --- |
| R1_learned_ff | Original base; selected question-null v5 reader, seed 2, uniform average of training checkpoints 150/200/250/300 |
| R1_nonlearned | Random tied cosine reader; lexical and pairwise-null off, cosine floor .93, null threshold 1.01 |
| v0_stable | Original base; StableCap C1 under DEC-035 |
| matched_update | Original base; MatchedUpdateCap C1, five normalized adjoint steps at lr .1 |
| v0_live_C1 | Original base; live C1 observations and registered search |
| v0_live_C2 | Original base; live C2 observations and registered site/search probes |
| S1_literal | Literal-continued base plus StableCap C1, no cap retraining |
| S1_LM | Fidelity-passing LM-continued base, weight lr 1e-8, plus StableCap C1, no cap retraining |

**DEC-050 selection rule:** maximize the equal-weight three-dataset mean development RET-GS subject to
zsRE unseen fires / 100 ≤ .10 at **100 actual records**, and locality preservation / 50 ≥ .98 **in every dataset**.
Candidates must use the same ordered development items per dataset and complete required assays.
A 300/1,000-record result or another outside population cannot substitute for the 100-record constraint.
Missing endpoints never pass the gate. DEC-053 reads the LS constraint under bounded equality.

R1-X12 independently reviewed 42 complete candidate definitions, 15 admissible, and a unique winner.
The selected reader has mean RET-GS .803333 (zsRE .98, CounterFact .82, MQuAKE .61).
Its averaged weight-file SHA256 is
`b38fb851e5ebf66de6700aa2a68dbdee23bf093f56f2c0897e3bb275b5af19e6`.
The selected training recipe uses the first 1,000 CounterFact and zsRE training-pool rows and the self-contained
500-item MQuAKE training pool. Ordinary-text nulls and question-form out-of-memory nulls remain distinct.

Preserve stable observations, tied cosine, pairwise/query null, plain lexical overlap, top-k 4, hard top-1,
binary mass, null threshold .5, no cosine floor, rare-overlap minimum 1 / active-record DF maximum 2,
zero fast-code steps and five per-position delta steps at lr .1, tau .1, A .3. Bind stop tokens,
scales, radii, tokenizer, masks, dimensions, taps, constructor defaults and byte accounting.
The selection manifest and complete audit carry the run/checkpoint roster and its provenance;
a future candidate is a versioned selection decision, not an unrecorded replacement.

The separate **45-cell R1_learned_ff_v2 extension** currently follows the R1-64b recipes:
historical two-pool v2 weights with rare gate disabled. Against v5, training and gating both differ.
Matrix v5 preserves that package-comparison interpretation. A same-v5-weights gate-only ablation requires
a new explicit identity; this draft does not silently switch weights or authorize extra cells.

Continuation identities remain `r1_24_literal_v3b` and `r1_24_lm_v3_lr1e-8`.
LM checkpoint SHA256: `6ef32487c4f4e2641ee0b5aba966651741788a98549c27292e6d40fa583992c6`.
Literal SHA256: `7591cfd1209f01c1d9877be6b596da56e3a3b45c2fa3e693cdb31407bbf59ef5`.
LM fidelity KL .0004736076 nats, loss change −.0088596493; literal KL .0000293325, loss change −.0000617914.
The literal continuation is not exactly unchanged weights. Historical forward-token matching at 771,581
does not establish final-v5 total-cost equivalence. MQuAKE v0-style radii need the R1-73 owner receipt;
continued-base calibration transfer remains explicitly subject to admission.

## 3. Development evidence and interpretation limits

The selected development stream results above come from the selection population. Driver profiles use
different 300-edit populations and must keep their own identities. R1-75 reproduces these saved cells:

| Bound driver cell | Checkpoint | ES | RET-GS | LS bounded / terminated | Unseen fires | Near-miss bounded / terminated |
| --- | ---: | ---: | ---: | --- | --- | --- |
| zsRE v5, d22ce680… | 100 | 1.00 | .99 | 50/50 / 50/50 | 9/100 | not run |
| zsRE v5, d22ce680… | 300 | 1.00 | .986667 | 50/50 / 50/50 | 8/100 | unavailable: 0 of 100 planned rows |
| CounterFact v5, bc285b69… | 100 | 1.00 | .765 | 49/50 / 36/50 | 0/100 | not run |
| CounterFact v5, bc285b69… | 300 | 1.00 | .753333 | 49/50 / 36/50 | 0/100 | 100/100 / 63/100 |

The zsRE cell also has zero revision rows against 50 planned IDs; it cannot certify a 50/50 revision result.
Standalone challenge reports are separate evidence. The task-list expectation of 100/100 zsRE near-miss
preservation is not supported by these driver files. CounterFact's driver reports 50/50 latest-answer revisions.
The newer R1-68c re-profile records immediate ES 299/300; it is a separate source/code-bound run, not a
replacement of the older cell's 300/300. Do not erase that difference when discussing runtime parity.

| Final-cell drift against original base, 16,256 positions | Mean signed nats | Maximum positive nats | Positions > .1 nats | Positive-harm ES99 |
| --- | ---: | ---: | ---: | ---: |
| zsRE v5, d22ce680… | .002197557 | 8.685941 | 17 | .219768 |
| CounterFact v5, bc285b69… | .006286152 | 7.314826 | 52 | .638480 |

These are empirical finite-sample tails, not fitted power-law evidence. Positive-harm ES99 averages the worst
1% of all scored positions, retaining zero-harm positions in the denominator and fractionally weighting
the boundary order statistic. A small mean does not exclude rare localized harm. Prefixes within windows
are dependent; do not treat 16,256 positions as 16,256 independent experimental replications.

**Occupancy caveat (R1-X12):** the reported zsRE rates 10/100, 12/100 and 9/100 at 100/300/1,000 records used
different outside populations. They do not establish flatness or an effect of memory size. Selection's 10/100
also sits exactly at its gate: descriptive Wilson 95% interval ≈ 5.52–17.44%, with post-selection limitations.
R1-76 fixes one outside set disjoint from the largest edit inventory and reuses it at all three checkpoints;
only that design supports a paired occupancy comparison. It is unexecuted at this draft.
MQuAKE beyond 100 remains unavailable pending a legitimate reader-unseen filler population; §6 does not budget
a nonexistent completed assay.

Earlier tri4/tri5/tri6 and v4 results remain in draft v4 and the Stage-2 notes as developmental history.
They neither replace the common-population selection receipt nor add independent realizations.
The R1-65 collision repair and R1-66 null-class change remain part of the selected training provenance.

## 4. Population, DEC-048 and sealing

For MQuAKE only, a true-fact locality, unrelated or verified near-miss query presentation does not count as
exposure to the later counterfactual edit. This does not assert that the model never encountered the subject,
query form, cap-off logits or true answer. Such exposure can still affect retrieval/rejection.
The exemption was adopted after a capacity shortfall was found; disclose that chronology.
Use “unexposed to primary counterfactual editing under DEC-048,” not “wholly unseen subjects.”

Register v6 rebinds the v5 policy without an additional policy release. It retains historical primary
training/development, drawn/sealed roles, conflicts, contexts, cross-dataset exclusions and zsRE priority.
No release is inferred from an absent row in today's smaller slices or from a similar reason-code name.

| Dataset | Candidate items | Candidate subjects | Required subjects | Nominal slack | First clearance loss causing shortfall |
| --- | ---: | ---: | ---: | ---: | ---: |
| zsRE | 52,411 | 52,411 | 4,050 | 48,361 | 48,362 |
| CounterFact, DEC-042 exception | 12,246 | 12,246 | 4,050 | 8,196 | 8,197 |
| MQuAKE-CF, DEC-048 | 4,489 | 4,218 | 4,050 | 168 | 169 |

MQuAKE accounting: 5,577 source subjects − 159 under zsRE priority − 1,200 historically primary-exposed = 4,218.
The full item pool has 6,043 entries; items and distinct subjects are different denominators.
The nominal per-realization allocation is 1,000 edits + 100 outside + 100 near supports + 100 near neighbors
+ 50 revisions = 1,350 distinct subjects, or 4,050 across three realizations.
Additional disjoint composition dependencies, if needed, increase demand.

**No positive lower bound on usable clearance is certified.** MQuAKE's 168 subjects are nominal headroom,
not a free development pool. A loss of 169 subjects already defeats nominal demand. Using candidates as
new development fillers creates primary exposure and must be debited before any later allocation.
The R1-76 memo supplies options for lead Q10; this draft allocates none.

Canonicalize NFKC, casefold and collapsed whitespace with independently verified aliases.
Teacher eligibility is bounded base-wrong-new-answer evidence, not proof of old-fact correctness.
Bind source/teacher truncation rules and alias/context/role compatibility.
Abort before RNG or draw output if any dataset lacks jointly cleared distinct subjects for all required roles.
R1-D1h's capacity guard must consume a real clearance inventory, not all nominal candidates.
Joint dependency feasibility remains additional to scalar count checks.

Bind ordered sources, answer-token strata (1–2 / 3–4 / 5–8 / 9+, including terminal), largest-remainder ties,
NumPy version, independent role/realization RNG derivation and seed. Seed 158 remains proposed.
Sequence: final eligibility → independently expected inventories/RNG → one role allocation →
payload/token/alias validation → immutable assets/hashes → lead's joint protocol/code/environment/cost freeze.
This round performs no allocation or sealing.

## 5. Endpoints, inequalities and inference

At each checkpoint n, ES = immediate exact successes / n and RET-ES = retained exact successes / n.
RET-GS = (1/n) Σ over attempted items of (successful planned paraphrases / that item's planned paraphrases).
Behavioral acquisition failures stay in those denominators. Required rows made unavailable by resource failures
produce an unavailable full-inventory metric; evaluated-only fractions are diagnostics, not substitutes.
Report attempted edits, active records, bytes/peak memory, selection/null outcomes and truncation.

**DEC-053:** for locality and near-miss pair i, let B_i = 1 if the two decoded 32-token-bounded greedy texts
are exactly equal; no additional normalization or termination requirement is applied.
Let T_i = B_i × 1[neither generation truncated]. Primary LS = ΣB_i / N_L, near-miss preservation = ΣB_i / N_N.
Always also report ΣT_i / N, either-side truncation counts, each side's truncation count,
planned/scored/unavailable counts and both raw generated texts. Historical cells can be rescored from their traces.
A truncated unequal pair remains a failure; missing text/flags never becomes preservation.
This convention governs DEC-050's LS gate and DEC-033's LS contrast margin.
S1 primary locality uses the original base; own continued cap-off reference is a separate incremental effect.

Outside inventory: 100 distinct facts per realization, disjoint from the entire largest attempted edit
population and all roles, including failed, evicted and superseded facts, across realizations.
Reuse outside IDs/prompts across conditions, orders and checkpoints. Actual post-gate firing, bounded
answer changes and terminated-pair equality are separate fields; an unsupported observer remains unavailable.
V0 memory slots are not mislabeled as RevisionCap records.

Near-miss and revision assays use isolated episodes/clones with checked restoration.
No filtering by old/own-answer acquisition is allowed. Revision denominators cover all 50 planned cases
per realization, with old acquisition, latest-answer success, old-alias reappearance and version activity separate.

### 5.1 U14: explicit secondary rules awaiting numerical admission

No numerical unseen/revision/scale pass rule is accepted in draft v4 or DEC-050–053.
The following specifies the inequalities and denominators so a later receipt can fill values without
silently redefining the metric. **All threshold symbols below are currently null/unadmitted.**
They cannot yield a passing or failing scientific verdict before U14 closes.

| Endpoint | Full-inventory quantity | Proposed decision form to bind before draw |
| --- | --- | --- |
| Unseen level | F_k = post-gate fires among the same 100 outside prompts / 100 at exact occupancy k | F_1000 ≤ u_max; optionally require a predeclared upper confidence bound ≤ u_max |
| Unseen occupancy change | D_F = (fires_1000 − fires_100) / 100, paired on the same prompts and realization | −δ_F ≤ D_F ≤ δ_F; an equivalence claim requires the entire registered paired interval inside [−δ_F, δ_F] |
| Revision latest answer | R_latest = latest-answer successes / 50 planned revision episodes | R_latest ≥ r_min |
| Old answer reappearance | A_old = episodes with any old alias reappearing / 50 | A_old ≤ a_max |
| Semantic revision | R_semantic = latest-answer success AND old record retired AND new record active, summed / 50 | R_semantic ≥ s_min, only for supported version observers |
| Scale retention | D_G = RET-GS_1000 − RET-GS_100, each item-averaged on its declared history (1,000 and 100 items) | D_G ≥ −δ_G; this is a descriptive stream-horizon contrast, not identical-history treatment pairing |
| Scale ES/LS | D_E = ES_1000 − ES_100; D_L = LS_1000 − LS_100 with fixed locality prompts | D_E ≥ −δ_E and D_L ≥ −δ_L |
| Resource feasibility | measured persistent bytes M_k, peak bytes P_k, charged cell time W | M_k ≤ B_k, P_k ≤ P_max and W ≤ W_max; equality passes only after ceilings are admitted |

These thresholds must be numbers plus a bound point/interval procedure and multiplicity role in the freeze.
DEC-050's .10 development selection gate is **not automatically a confirmatory unseen threshold**.
DEC-033's between-condition margins are **not automatically stream-size noninferiority margins**.
Failure to reach k actual records makes an exact-k point unavailable; do not relabel attempted edit count as size.
A single absent required case leaves the full rate unavailable, with missingness and evaluated counts reported.
Observed equality of rates or an interval that merely includes zero does not demonstrate equivalence.

Composition remains descriptive with no success margin. Attach a case only if all required edited facts
belong to the realization; retain conflict/unavailability and source identities. Dependency count is edited
facts, not total path hops. Cases are selected independently of outcomes. Historical R1-60 scored 299/300 cases:
all-three success 1/299, question exact 8/897; the full 300-case/900-question fractions remain unavailable.
That observed floor does not establish a capability ceiling or actual post-gate firing.

### 5.2 Ordinary text, tail and fidelity

Select afresh at every ordinary-text prefix. K complete 128-token windows yield 127K scored positions.
Report signed mean ΔNLL (nats), exp(mean ΔNLL), positive-part mean, maximum and position,
counts above .01/.1/1 nat, and **ES99 of positive ΔNLL**, against original and own cap-off references.
For x_i = max(0, NLL_cap,i − NLL_reference,i), sort x descending and let q = .01N.
ES99 = [Σ first floor(q) x + (q − floor(q)) × next x] / q.
A total of 128 windows means 16,256 positions; it is not the full validation split required by plan 9.
Full-split/cadence and its budget remain U08/U16, not silently satisfied by the sampled panel.

Fidelity remains DEC-033: mean KL ≤ .001 nats and mean loss increase ≤ .01 nats on its bound inventory.
These are fidelity constraints for the specified comparison, not a tail-harm guarantee.
Per-position tail statistics remain descriptive until a separate threshold/model is admitted.

### 5.3 Paired contrasts and classification

The matrix enumerates primary v5 versus each of seven controls, per dataset.
Keep the historical-v2 extension separate. Independently declared IDs/denominators govern every pairing.
Missing cells/rows/endpoints stay visible. Never use another condition, checkpoint or realization to fill them.
Average within each realization/order and keep all five orders together within a realization.
Bootstrap three fresh realization means; draft settings: 10,000 draws, seed 0, float64,
confidence .975 with linear percentile bounds .0125/.9875.
Three clusters give limited uncertainty; overlapping developmental data do not increase sample size.
No independent-cluster interval is produced from one realization or overlapping realization populations.

DEC-033 margins: ΔRET-GS +.05, ΔES −.02, ΔLS −.01 (all absolute fractions, primary minus control).
Proposed U13 classifier, only after completeness and admission:

- Positive: ΔGS ≥ .05 AND L_GS > 0 AND L_ES > −.02 AND L_LS > −.01.
- Negative: U_GS < .05 OR U_ES < −.02 OR U_LS < −.01.
- Qualified: not negative, ΔGS ≥ .05 and L_GS > 0, ΔES ≥ −.02 and ΔLS ≥ −.01,
  with one or both ES/LS lower-bound tests unresolved.
- Otherwise inconclusive. Equality at strict interval boundaries does not pass that strict test.

U12 remains open: the lead must bind the family across datasets/controls and its correction/gatekeeping procedure.
A .975 pointwise interval is not a registered familywise procedure. R1-75 emits draft margin diagnostics and an
unadmitted-multiplicity status, never a confirmatory positive claim merely because pointwise limits pass.
Development reports and checkpoint contrasts are descriptive; the final 1,000-edit comparison has primary timing.

## 6. DEC-050–053 execution, profiles and calendar

Execution uses the selected reference and DEC-053 scoring convention together.
R1-68d moves the expensive full immutable-input/parameter rehash to attempt start, resume after restore,
each checkpoint before its receipt, and completion. Each phase checks in-memory parameter structure/configuration
and retains its mutable-state checks. Replaced array leaves are detected within the phase; mutable NumPy
in-place corruption is detected at the next full checkpoint boundary, before a receipt.
Both profiles retain their registered clone/restore policies; incremental drift batches independent prefixes.

R1-68c owner measurements (same 300-edit zsRE population):

| Component | Incremental | Full |
| --- | ---: | ---: |
| Attempt wall | 837 s | 1,274 s |
| Immutable identity rehash | 534 s | 534 s |
| Ordinary-text drift | 83 s batched | 516 s scalar |

The earlier ≈545-second “clone/restore” attribution is superseded: measured identity verification explains it.
Seven R1-68d CPU driver tests pass, including legacy scientific parity, resume/receipt-chain checks and
corruption rejection. This does **not** measure its real-base speedup or price 1,000-edit heterogeneous cells.
The scoring source patch remains separately permission-gated until landed; recipes must bind the final source.

**U11 real-base batching tolerance requested by the owner:** absolute per-position NLL difference ≤ 1e-3 nats
for cap, original and cap-off vectors on identical IDs/order, with identical exceedance counts at .01/.1/1 nat
for each declared drift reference. Record complete vectors and source identities.
The recorded scalar/batch maximum cap-NLL difference is about 1.3e-4 nats, mean 2.9e-6;
this is not bitwise equality and exceeds the earlier TinyBase absolute tolerance of 2e-5.
Any violated vector/count criterion refuses admission; roundoff cannot be hidden by rounding aggregate means.

**DEC-051 block order** (within each block: declared dataset order, condition order, realization, order):

| Block | Cells | Contents | Cumulative cells |
| --- | ---: | --- | ---: |
| B1 | 45 | Primary, random, v0-stable; realization 0; all three datasets and five orders | 45 |
| B2 | 45 | Matched-update, live C1/C2; realization 0 | 90 |
| B3 | 90 | First six conditions; realization 1 | 180 |
| B4 | 90 | First six conditions; realization 2 | 270 |
| B5 | 90 | Both S1 conditions; all three realizations | 360 |
| B6 | 45 | Separately admitted historical-v2 no-gate extension | 405 |

An optional HT-7h slot between B3/B4 depends on separate decisions/budget. It adds no cells to this matrix.
**Q4 (κ pilot) and Q5 (stress panel) remain OPEN; neither is resolved by this draft.**

Matrix v5 gives stable four-coordinate IDs, explicit block slots, recipe families and null measured ceilings.
R1-64/R1-64b are constructor templates; MQuAKE v0-style families require R1-73 calibration receipts.
They are not executable confirmatory recipes until final roles, code, budget and approval are bound.
Use new attempt directories; verify the unique contiguous checkpoint chain and full snapshot/state identity
before resume. Torn/open incremental journal intents or unknown spend refuse automatic resume.
Identity mismatch stops the queue for owner reconciliation; it never triggers silent rebinding.
There is no automatic retry policy that grants extra spend. Completed-cell skipping requires a verified
terminal receipt plus matching completion result. Charge failed/partial attempts and shared training honestly.

**DEC-052 schedule:** retain scope, remeasure on September 20, and stop experiments October 9.
October 10–14 is reserved for analysis, figures, writing and rehearsal, not experiment completion.
If all cells cannot finish, report complete blocks plus every incomplete cell/checkpoint by stable identity,
in DEC-051 order. A terminal result is execution completeness; missing secondary rows remain endpoint incompleteness.
No complete-matrix claim may be made from a coherent subset.

The owner's post-repair 15–17-minute/1,000-edit estimate is a scenario, not a measured ceiling.
At 17 minutes × 405 it is 114.75 GPU hours before additional reserves. Earlier 331–452-hour scenarios retain
their historical driver assumptions. Neither is admitted. Recompute from actual condition/dataset profiles,
cold setup, all checkpoint/real challenge costs, full validation, restore, failures and shared training.
The current 300-edit zsRE profile has no actual near-miss/revision rows; zero-row phases cannot price those assays.
MQuAKE calibration, continuation transfer, byte/watchdog ceilings and calendar contention remain serial risks.

## 7. Gate register U01–U18

| Gate | Current state and next checkpoint |
| --- | --- |
| U01 comparisons | 360 core retained; deferred plan-9 branches and package contrasts explicitly labeled |
| U02 reference | DEC-049/050 selected v5; selection audit complete, final admission still required |
| U03 continuation | Historical fidelity supported; final-v5 budget/config/calibration/profile matching open |
| U04 zsRE freshness | 52,411 candidates; final alias/context/teacher/later-exposure clearance open |
| U05 CounterFact source | 12,246 under DEC-042 exception; final source receipt pending, strict policy remains zero |
| U06 draw/RNG/splits | DEC-048/register v6 retained; MQuAKE 4,218 nominal, usable joint capacity/RNG receipt open |
| U07 payload/seal | Development construction exists; final role payloads and seals absent |
| U08 cadence | 100/300/1,000 attempted-edit checkpoints; challenge/full-validation cadence and actual inventories need binding |
| U09 semantics | Explicit unavailable zsRE challenges; aliases, revision dependencies and observers remain audited |
| U10 LS convention | DEC-053 resolves primary bounded equality; terminated/truncation counts mandatory; source landing/recipe rebinding pending |
| U11 implementation | R1-68d CPU repair tested; owner real-base re-profile plus ≤1e-3-nat batching/count parity and integration receipts required |
| U12 multiplicity | Seven controls × three datasets and separate extension are enumerated; family/procedure remains lead-owned |
| U13 classifier/fidelity | DEC-033 margins and proposed strict/inclusive inequalities in §5.3; DEC-053 applies to LS; final classifier/fidelity admission open |
| U14 secondary | §5.1 quantities/inequalities explicit; numerical thresholds and interval/multiplicity roles null, no success declaration |
| U15 analysis | R1-75 saved-cell/TinyBase analysis tested; independent final populations and scientific admission pending |
| U16 budget | All v5 measured ceilings null; owner heterogeneous pricing due September 20 |
| U17 controls | Matrix v5 supplied; freeze candidate v4 must rebind final matrix/protocol/source/recipes and closed gates |
| U18 schedule | DEC-051/052 bind order, September 20 review, October 9 stop and explicit incomplete reporting; no completion promise |

## 8. Freeze and concurrent work

The joint freeze must bind protocol/decisions, contrasts/multiplicity, code/environment/hardware/determinism,
base/reader/tokenizer/calibration/gates, cumulative exclusions, cleared roles/challenges, training/development
separation, denominators/references, bytes/eviction/restore, costs/retries/shared training, analysis settings and lead approval.

CPU work can proceed on clearance accounting, independent analysis inventories, manifest/receipt validation and
the common-outside runner. The owner handles real-base profiles/calibration and any approved occupancy assay.
R1-74 scoring landing and R1-68d driver rebinding must be coordinated once after active profiles finish.
Any later source change requires another explicit recipe/freeze identity. No final draw, sealed payload,
experiment or cost admission is inferred from these development deliverables.

## 9. Change log against v4

- Replaced “primary unselected” with DEC-049/050 v5 and its exact averaged weight identity, training seed,
  common-population audit and selection uncertainty.
- Updated register to metadata-rebound v6; retained DEC-048 caveat, 4,050-subject demand and 168 nominal MQuAKE slack.
- Applied DEC-053 exact bounded equality throughout LS/near-miss, with terminated and truncation counts.
- Added audited driver rows, explicit absent zsRE challenges, drift ES99 and the occupancy-population caveat.
- Made unseen/revision/scale denominators and decision inequalities explicit without inventing accepted U14 numbers.
- Retained open U12 multiplicity and U13 admission; enumerated control contrasts without familywise claims.
- Replaced old runtime attribution with measured identity-check/batched-drift components and the R1-68d repair;
  added the owner's real-base numerical tolerance.
- Added DEC-051 block counts, matrix v5 bindings, queue/resume/refusal semantics and DEC-052 calendar/incomplete reporting.
- Kept Q4/Q5 open and historical-v2 extension interpretation separate from a same-weight gate-only ablation.
