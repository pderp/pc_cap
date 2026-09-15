# Revision v1 — Stage 4 protocol draft v4 (R1-49d)

**Development draft, 2026-09-15. DEC-048 is accepted; this document authorizes no draw, seal, freeze or launch.**
This supersedes draft v3's current population, reader-selection and profile statements. The scope remains
**360 core cells**, with **45 separately allocated extension cells** only if admitted. The final primary reader
is **unselected**. A nominally sufficient exclusion register is not a certificate of eligible capacity.

Evidence: [register v5](../manifests/revision_v1/exclusions_frozen_v5.json),
[training and result recount](../logs/r1_round13/training_review_evidence.json),
[population comparison](../logs/r1_round13/population_and_checkpoint_recount.json),
[clean-profile recount](../logs/r1_round13/clean_profile_recount.json),
[counter-review](../logs/review_r1_65_66.md). The historical v0 freeze is not a revision-v1 launch receipt.
The existing [matrix v4](../manifests/revision_v1/run_matrix_draft_v4.json) still binds older exclusions/reference;
the owner must produce a new version after final selection and clearance.

## 1. Question, decisions and scope

Can a small editing memory retain requested facts and paraphrases, reject unrelated requests and preserve ordinary
language modeling while the base and reusable cap weights remain fixed? Only declared support-driven episodic
state changes during each stream.

DEC-043 accepts the rare-token gate; DEC-044 retains full scope and supersedes the old 15-hour envelope;
DEC-045 adds MQuAKE-CF while retaining CounterFact. DEC-046's historical 500/200 split is superseded operationally
by the self-contained v3 500/100 slices and development v3b's corrected unrelated inventory. Historic exposure
remains reserved except for DEC-048's explicit query-role exemption. DEC-047 supplies the fidelity-passing S1_LM
at weight learning rate 1e-8. DEC-048 chooses option C; its policy and objection are declared in §4.

Episodically trained bases, alternating BP/ePC on matched episodes, settled/feedforward inference and the retrained-cap
2×2 remain separately admitted plan-9 branches. Their absence is not a negative result. The learned/random contrast
compares deployed packages with different architecture/features/gates, not an isolated causal effect of learning.

## 2. Conditions and final-primary selection

Use 8 conditions × 3 datasets × 3 fresh realizations × 5 orders = **360 core cells**: 120 per dataset, 45 per condition.
Datasets are zsRE, CounterFact and MQuAKE-CF. Checkpoints are **100, 300 and 1,000 attempted edits**; report actual
retained occupancy separately. Proposed realization seeds 0/1/2, order seeds 100–104, reader/model seed 0 remain
subject to final binding. Reader-training seeds on one development split are not independent data realizations.

| Condition | Substrate and behavior |
| --- | --- |
| R1_learned_ff | Original base; final reader slot OPEN among historical v4, fixed-locality tri4, and question-null candidates tri5/tri6 |
| R1_nonlearned | Original base; random tied cosine reader, lexical and pairwise-null off; cosine floor .93, null threshold 1.01 |
| v0_stable | Original base; StableCap C1, DEC-035 |
| matched_update | Original base; MatchedUpdateCap C1, five normalized adjoint steps at lr .1 |
| v0_live_C1 | Original base; live C1 observations and declared v0 search |
| v0_live_C2 | Original base; live C2 observations and declared v0 site/search probes |
| S1_literal | Literal-continued base plus StableCap C1, no cap retraining |
| S1_LM | Fidelity-passing LM-continued base, weight lr 1e-8, plus StableCap C1, no cap retraining |

**Selection rule required by the current lane:** choose one deployment rule for all three datasets, maximizing the
development mean RET-GS subject to **zsRE unseen false fires ≤ .10 at 100 records** and **LS ≥ .98**, before any draw.
The mean is the equal-weight mean of the three dataset RET-GS values, not a query-count-weighted pooled mean.
Conservative draft interpretation: LS must meet .98 in each dataset. The owner must bind that interpretation,
candidate roster/cutoff, training-seed selection or aggregation, tie-break and exact ordered populations before
writing the selection receipt. Thresholds are inclusive. Missing endpoints or incomplete runs do not pass.

Use the same 100-edit development streams, paraphrase inventories, decode convention and fixed unrelated inventory
for each candidate. Use a separate zsRE outside development population disjoint from all 100 attempted edits,
with 100 actual records and 100 planned/scored queries. A training-pool outside assay or a 1,000-record result cannot
substitute for this constraint. Keep observed gate acceptance, changed answers and terminated-pair preservation
separate. Selection uses the declared LS statistic; final confirmatory LS interpretation still needs §5 binding.

Historical v4's MQuAKE development stream shares only **47/100 items** with the new tri4/tri5 stream and uses a
different unrelated inventory. Its old value cannot be ranked as a paired rerun. Obtain a common-population receipt
for every candidate still under consideration. Within-run best-checkpoint choice uses held-out episode retrieval
loss; that is a different, earlier decision from the final stream-based selection rule. Record both decisions.

Preserve stable observations, tied cosine, pairwise/query null, plain lexical overlap, top-k 4, hard top-1,
binary mass, null threshold .5, no cosine floor, rare-overlap minimum 1 / active-record DF maximum 2,
zero fast-code steps and five per-position delta steps at lr .1, tau .1, A .3 unless a versioned candidate declares
otherwise. Bind scales, radii, stop list, tokenizer, masks, dimensions, taps, constructor defaults and byte accounting.

Historical [v4](../manifests/revision_v1/primary_condition_v4.json) seed-0 weights
SHA-256 `d42cd97a761ee7c56c041694f57c0f8ff31798ae45b99cf714728798ebb0f7ce` used MQuAKE v2's 1,000 items.
Tri4/tri5/tri6 use v3's 500-item pool; none inherits v4's reader identity.
The two-pool [v3](../manifests/revision_v1/primary_condition_v3.json) remains historical fallback evidence,
not an automatic selection-rule exception.

The **45-cell v2 extension** remains separate, total 405 if admitted. Its current recipe uses two-pool v3 weights
with the gate off; against three-pool candidates this changes both training and gating. A gate-only interpretation
requires the same selected weights and all other settings. The owner must version the extension or explicitly retain
the package-comparison interpretation; no allocation change is made here.

Continuation bindings remain `r1_24_control_v3.json` / `r1_24_literal_v3b` and
`r1_24_control_lm_v3_lr1e-8.json`. LM checkpoint SHA
`6ef32487c4f4e2641ee0b5aba966651741788a98549c27292e6d40fa583992c6`;
literal SHA `7591cfd1209f01c1d9877be6b596da56e3a3b45c2fa3e693cdb31407bbf59ef5`.
LM fidelity KL .0004736076008384771 nats, NLL change −.008859649300575256; literal KL .000029332460329101195,
NLL change −.00006179139018058777. Literal is a numerical negative control, not exactly unchanged weights.
Historical forward-token matching at 771,581 does not establish final-reference total-cost equivalence.

## 3. Development evidence and limits

The following nine completed streams use 100 items, stream seed 21, paired ordered items within each dataset
for the three recent candidates. RET-GS is recomputed from 100 checkpoint rows per stream; LS uses the stored
50-query aggregate, whose individual generation traces are not present in those checkpoint files.

| Reader | zsRE RET-GS | CF RET-GS | MQ RET-GS | Mean | LS zsRE / CF / MQ | zsRE unseen fires |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| tri4 seed 0, fixed locality | .98 | .86 | .79 | .876667 | 1 / 1 / .98 | 30/100 |
| tri4 seed 2, fixed locality | .98 | .86 | .79 | .876667 | 1 / .98 / 1 | 52/100 |
| tri5 seed 0, question null probability 1 | .91 | .81 | .55 | .756667 | 1 / .98 / 1 | 5/100 |
| tri6 seed 0, probability .35 | null | null | null | null | null | null |

Tri5 meets the observed numerical constraint among these completed assays; it is **not declared the winner**.
Tri4 seed 1 and tri6 were incomplete at the evidence snapshot. Future results require an additive selection receipt.
The paired unseen reports have 100 planned/scored queries, 100 records and 100 terminated reference/cap pairs.
The seed-0 tradeoff is −25 percentage points in firing, −7 in zsRE GS and −24 in MQ GS. This is development
evidence on one population, not a confirmatory treatment effect or independent-data uncertainty estimate.

R1-65 removes exact token collisions between a locality query and any in-memory own prompt, including the
mixed-builder domain-repair branch. A metadata rehearsal of the actual mixed recipe finds historical collisions
of 23/1,004 and 21/996 MQ locality queries (seeds 0/2), versus 0 in the repaired rehearsals. The ≈13% heuristic
assumes a homogeneous 500-item memory pool; it is not the rate in these mixed runs. This repair alone did not
resolve unseen firing. R1-66 changes the null subclasses; balanced L2 still allocates .5 total mass to each of
null and record classes. See the review for RNG, validation and causal-interpretation limitations.

Older v4 three-seed RET-GS ranges are zsRE .95–.98, CF .76–.83 and MQ .56–.79. Older unseen/drift results
must retain their exact reader/pool/query identities. The completed zsRE driver profile is historical v4,
development source order at 100/300 edits; it is not a certificate for the as-yet unselected final primary.

## 4. Population, DEC-048 and sealing

**Declared rule:** for MQuAKE only, presentation of a true-fact locality, unrelated or verified near-miss candidate
query does not count as exposure to the later counterfactual edit. DEC-048 accepts this because such a presentation
does not teach the requested replacement answer as an edit. It does not assert that the model never encountered
the subject, template or true answer.

**Reviewer objection:** exposure to the entity, query form, cap-off logits or true-fact neighborhood can still change
retrieval and rejection. Exempting it weakens a strict unseen-subject claim, and the policy was chosen after a
capacity shortfall became visible. Disclose that chronology and label the target population “unexposed to primary
counterfactual editing under DEC-048”; do not call it wholly unexposed. Preserve historical query evidence and report
the 2,100-subject conservative population as a sensitivity inventory, without drawing extra data here.

[Register v5](../manifests/revision_v1/exclusions_frozen_v5.json) binds 43 sources, including v3 slices, v3b lineage,
the cumulative exposure register and the split R1-X9 audit. It removes only the three recorded MQuAKE query
reason codes. Other reasons remain independently effective: historical primary training/development, drawn/sealed
roles, conflicts, contexts, cross-dataset exclusions and zsRE priority. Unknown or counterfactual near-miss reasons
are never waived by name similarity. In v3 the true near-candidate inventory coincides with its locality
neighborhood and stays primary-reserved; no additional historical near-miss release is inferred.

| Dataset | Candidate items | Distinct candidate subjects | Demand | Subject headroom | First clearance loss causing shortfall |
| --- | ---: | ---: | ---: | ---: | ---: |
| zsRE | 52,411 | 52,411 | 4,050 | 48,361 | 48,362 |
| CounterFact, DEC-042 reason-specific exception | 12,246 | 12,246 | 4,050 | 8,196 | 8,197 |
| MQuAKE-CF, DEC-048 | 4,489 | 4,218 | 4,050 | 168 | 169 |

MQuAKE releases 2,118 distinct subjects relative to cumulative v4: 5,577 source subjects minus 159 under zsRE
priority minus 1,200 historically primary-exposed subjects = 4,218. This does not release primary exposures simply
because they are absent from today's 500/100 slices. CounterFact's strict policy remains zero; its final exception
source receipt remains the lead's responsibility.

No positive lower bound on final alias/context/role clearance is certified. The defensible pending-removal upper
bound is the whole candidate population: 52,411 / 12,246 / 4,218 subjects, respectively (and all candidate items).
MQ can lose at most 168 subjects while retaining nominal demand; 169 losses abort. Additional disjoint composition
support allocations, if required, increase demand and must be accounted for before capacity admission.

The nominal allocation per realization is 1,000 edits + 100 outside + 100 near supports + 100 near neighbors
+ 50 explicit revision = 1,350 disjoint subjects, or **3 × 1,350 = 4,050 per dataset**.
Canonicalization is NFKC, casefold, collapsed whitespace plus verified aliases. Teacher eligibility is bounded
base-wrong-new-answer evidence; it does not prove old-fact correctness. Preserve source/teacher truncation policy.

**Abort before RNG or any draw output if usable, jointly cleared distinct subjects in any dataset are below demand.**
R1-D1h's `require_usable_capacity` rejects missing datasets, unknown or duplicate subjects and insufficient counts.
It requires an explicit clearance inventory; supplying all candidates without actual clearance is not a certificate.
R1-58 must call this policy-aware guard and additionally check joint role/dependency feasibility; never reuse the
conservative parent removals as if DEC-048 had not happened, or treat the register alone as launch admission.

Freeze exact ordered sources, answer-token strata (1–2 / 3–4 / 5–8 / 9+ including terminal), largest-remainder ties,
NumPy version, independent role/realization RNG derivation and seed before allocating. Seed 158 remains proposed.
Serial boundaries: final reference/eligibility -> independent expected inventories/RNG -> one role allocation ->
payload/schema/token/alias validation -> immutable assets and hash bindings -> joint lead freeze of protocol,
code, models, environment, costs and inventory. This work performs none of those draws or seals.

## 5. Endpoints and inference

At each checkpoint retain unconditional immediate ES, RET-ES and item-averaged RET-GS, including behavioral
acquisition failures and all planned paraphrases. Resource failures are explicitly unavailable, not dropped.
Report attempted edits, active records, bytes, peak memory, candidate/selection/null outcomes and truncation.
Missing target occupancy is an unavailable exact-size point.

Outside inventory is fixed at 100 distinct facts per realization, disjoint from the entire attempted edit
history across realizations and all other roles, including failed/evicted/superseded facts. Reuse its IDs across
conditions, orders and checkpoints. Report actual post-gate firing, bounded changes and complete-answer preservation
separately; missing observer data is unavailable. The comparator adapter honestly distinguishes v0 slots from
RevisionCap records and does not invent unsupported firing observations.

LS's primary convention still requires an explicit lead binding: current bounded normalized text equality versus
termination-qualified equality. Always report complete pairs and truncation. S1 primary locality compares against
the original base; incremental cap effects also compare with its own continued cap-off base.

Near-miss and revision challenges use isolated clones and pre/post restoration identity checks. Denominators include
all planned cases, without own-answer-success filtering. Revision reports old acquisition, latest answer, old-alias
reappearance and version activity separately.

**Composition remains descriptive.** The source provides three direct questions per case; attach only when all
required edits belong to the appropriate realization, preserving unavailable/conflicting cases and source identity.
Dependency count is the number of edited facts, not total path hops. Select cases without reference to outcomes.

R1-60 selected 300 of 484 cases attached to the exposed MQ training pool. It scored 299 cases / 897 questions;
one case was unavailable because pre/post aliases overlap. All-three success is **1/299 scored**, question exact
is **8/897**; cap-off exact against old/new answers is **0/897 each**. Full planned-inventory fractions remain
null (300 cases / 900 questions planned), not automatically 1/300 or 8/900. Seven reference and seven cap outputs
hit the decode bound and count as non-exact. This is a floor under the tested prompting/reference, not proof of
a composition capability ceiling or “no headroom.” The 369 null-mass-below-.5 traces do not establish actual
post-rare-gate firing because that trace omits the gate result.

Ordinary text selects at every prefix. K complete 128-token windows give 127K scored positions; report mean
delta NLL in nats, exp(delta NLL), per-position fires and bound source/window identities. 128 windows give
16,256 positions but are not the full validation split required by plan 9. Bind full-split/tail policy, references
and measured cost separately; 3K sampled prefixes are a separate diagnostic denominator.

Independent expected dataset/condition/realization/order/role inventories govern the analysis. Missing cells,
items and required endpoints stay visible; fully unavailable metrics are null. For paired contrasts, average
item differences per realization/order and keep five orders together within each realization. Bootstrap three
realization means, proposed 10,000 draws, seed 0, float64, confidence .975 and linear percentile bounds
.0125/.9875. Three clusters give preliminary uncertainty; overlapping development data or reader seeds do not
increase independent sample size. No CI is available from a single realization.

Proposed complete/admitted classifier: positive if delta GS ≥ .05 with lower bound > 0, ES lower bound > −.02
and LS lower bound > −.01; negative if GS upper bound < .05 or ES upper bound < −.02 or LS upper bound < −.01;
qualified if not negative, GS meets the positive test and ES/LS points meet margins but their lower-bound tests
are unresolved; otherwise inconclusive. Admission/missingness/insufficient-cluster statuses precede classification.
Lead must bind inequalities, primary contrasts and multiplicity across datasets/controls. Bootstrap confidence
alone is not multiplicity control. No numerical secondary composition success margin is registered.

## 6. Profiles, watchdogs and schedule

Fill versioned receipts from `results/R1/stage4_dev_cells/R1_learned_ff-zsre-development_profile-*/`.
The completed current directory ends `source-8a5edf8cea14e816ace0/attempt-0000`; its result and checkpoint
receipts are bound in the [CPU recount](../logs/r1_round13/clean_profile_recount.json). It profiles historical v4
on zsRE at 100/300; final-primary, 1,000-edit, other-dataset and comparator values remain **null**.

| Measured phase | Count | Sum of recorded phase seconds |
| --- | ---: | ---: |
| Edit | 300 | 177.147 |
| Immediate check | 300 | 153.506 |
| Retention | 2 | 30.040 |
| LS | 2 | 6.299 |
| Unseen | 2 | 99.438 |
| Near-miss / revision / composition | 1 each, zero available rows | .463 / .466 / .464 |
| Drift | 1, 16,256 positions | 508.487 |

The recorded timers sum to **976.310 seconds**. They begin **after** input verification, the initial state hash and
snapshot clone. Owner notes report **1,252 seconds total** and roughly 1 second per edit/check including those
boundaries; these are different timing scopes. Neither the JSON timers nor their difference isolate individual
hashing, I/O, cloning or model costs. The metadata recount has no independent process-elapsed measurement.
Zero-case challenge timings do not price 100 actual challenges.

| Required per condition/dataset field | Current admission value |
| --- | --- |
| Final reader/base/config and exact profile identity | null |
| Cold initialization/compilation vs reusable setup | null |
| Edit and checkpoint components at 100 / 300 / 1,000 | partial historical zsRE / partial historical zsRE / null |
| Alias/context and answer-length coverage; full validation drift | null |
| Restore/restart, state peaks, full wall and watchdog | null |
| Failure reserve, shared training costs, total schedule | null |
| R1-68 incremental driver profile | null |

The R1-68 proposal adds record-digest indexing, immutable batched phase journals and a checked immediate assay
that can omit cloning for exact RevisionCap. Full immutable-input/parameter and checkpoint checks remain required.
Existing driver wiring, mutation inventories and all-endpoint resume parity still need owner work and a real-base
profile. No speedup or cheaper admitted ceiling is claimed from CPU component tests.

Owner notes extrapolate **49–66 minutes per learned 1,000-edit cell** under the current driver, with assumptions about
drift cadence and challenge counts. For 360 homogeneous cells that is roughly **294–396 hours before reserve**,
or **353–475 hours with 20% reserve**. This is a planning scenario, not a measured heterogeneous matrix budget.
The optional 45 cells, training, failed attempts, initialization, complete-validation drift and queue contention add
work. The earlier 115-hour proxy is superseded as a planning basis, not silently retained as a ceiling.

Charge initialization, edits, checkpoints, restore/serialization and failed work once at their actual boundaries.
Shared banks/training are charged once per execution. Reference reuse requires identical base/tokenizer/windows
and policy; count forward tokens, reverse positions, padded/JIT work, wall and device time separately.
Refresh calendar dates from actual charged spend and the final profiles; no current finish-date claim is justified.
Population policy is resolved, but clearance, common-population reader selection, driver integration and final
cost admission remain serial dependencies.

## 7. Gate register U01–U18

“Complete artifact” is not automatic final admission.

| Gate | Status and next checkpoint |
| --- | --- |
| U01 scientific comparisons | 360 core retained; declare deferred plan-9 branches and package-comparison claims |
| U02 reference | OPEN: §2 common-population constrained development selection, then exact reader identity and assays |
| U03 continuation | Fidelity component supported; final-reference budget/config/profile match remains |
| U04 zsRE freshness | 52,411 candidates; final alias/context/teacher and later-exposure clearance pending |
| U05 CounterFact source | 12,246 under DEC-042 exception; final source receipt pending; strict zero retained |
| U06 draw/RNG/splits | DEC-048 accepted and v5 written; MQ 4,218 nominal; usable clearance, joint feasibility and RNG receipt pending |
| U07 payload/seal | Development builder exists; final role payloads and seals unwritten |
| U08 endpoint cadence | 100/300/1,000 attempted edits retained; full-validation/tail and challenge cadence must bind |
| U09 challenge semantics | Modules exist; compatible aliases, dependencies and independent inventories remain |
| U10 LS convention | §2 development criterion declared; final bounded/termination-qualified primary convention and references pending |
| U11 implementation | R1-67 new loader/trace delivered; owner wiring outstanding. R1-68 components and broader integration gates remain |
| U12 contrasts/multiplicity | Lead family across three datasets/eight conditions open; separate 45-cell extension interpretation pending |
| U13 classifier/fidelity | Existing .05/−.02/−.01 CPU machinery; final applicability, inequalities and fidelity/drift binding pending |
| U14 secondary thresholds | Composition descriptive; no numeric success margin; unseen/revision/scale decision rules need final binding |
| U15 analysis adapter | CPU inventory machinery complete; independent final expected IDs and admission pending |
| U16 budget | Historical zsRE clean profile complete; final all-condition/dataset/checkpoint ceilings remain unadmitted |
| U17 execution controls | Matrix v4 and dry freeze are stale for final reference/v5/code; versioned queue/retry/resume/environment binding required |
| U18 schedule | Refresh actual spend and critical path; no admitted calendar promise |

## 8. Freeze contents and concurrent work

The lead's joint freeze must bind the protocol/decisions; matrix/contrasts; complete code/environment/hardware and
determinism; base/reader checkpoints; tokenizer/calibration/gates; cumulative exclusions plus accepted DEC-048;
cleared ordered roles/challenges; training/development separation and caches; denominators/references; byte limits,
eviction and restore; per-job/total ceilings, retry/overshoot/shared costs; analysis settings and approval identity.

CPU lanes can proceed independently on alias/context clearance, source inventories, final loader/trace wiring,
mutation audit, journal/resume integration and analysis inventories. The owner can complete tri6 and missing
common-population development assays on the GPU. Reader selection precedes final pricing; both selection and
cleared capacity precede draw. New code changes the whole-tree identity, so future recipes must be rebound.
No source-tree changes were made while the completed clean profile was running. Existing-file edits remain
permission-gated under the lead's new-files-only instruction; this round creates additions and proposed edits only.
