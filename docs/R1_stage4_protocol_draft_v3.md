# Revision v1 — Stage 4 protocol draft v3 (R1-49c)

**Draft for owner implementation and lead admission, 2026-09-15. No draw, seal, freeze or launch authorization.**
This replaces draft v2's current-state statements. The nominal scope remains **360 core cells**. MQuAKE capacity
does not support that scope under the current cumulative exclusions; [R1-D7](tasks/R1-D7.md) presents choices
without making a decision. The [new matrix](../manifests/revision_v1/run_matrix_draft_v4.json) binds available
identities and keeps execution flags false. The historical v0 freeze is not a revision-v1 launch receipt.

Evidence: [round-12 population counts](../logs/r1_round12/population_options.json),
[development recount](../logs/r1_round12/mquake_review_evidence.json),
[counter-review](../logs/review_r1_mquake.md), and [source snapshot](../logs/r1_round12/source_evidence.json).
The GPU owner's concurrent tri3 retraining and cell profile are separate work; their incomplete or newly arriving
outputs are not substituted for the registered v4 reference by this draft.

## 1. Question, decisions and scope

Can a small editing memory retain requested facts and paraphrases, reject unrelated requests and preserve
ordinary language modeling while the base and reusable cap weights remain fixed? Only declared support-driven
episodic state changes during each stream.

DEC-043 accepts the rare-token overlap gate; DEC-044 retains full scope and supersedes the old 15-hour envelope;
DEC-045 adds MQuAKE-CF while retaining CounterFact. DEC-046 proposed training/development slices and three-pool
training; its historical 500/200 split and approximate remaining-capacity claim are superseded operationally by
the self-contained v3 500/100 slices and cumulative exposure accounting. The original decision row remains a
historical record and needs a dated qualification. DEC-047 supplies the fidelity-passing S1_LM at weight
learning rate 1e-8; the failed 1e-6 run remains historical evidence.

This matrix does not implement every plan-9 branch. Episodically trained bases, alternating BP versus ePC on
matched episodes, settled versus feedforward inference and the retrained-cap 2×2 need separate admitted
implementations and allocations. Their absence is not a negative result. The learned/random comparison is
between deployed packages with different architecture/features/gates, not a pure effect of learning.

## 2. Conditions and immutable identities

Use 8 conditions × 3 datasets × 3 independent fresh realizations × 5 orders = **360 core cells**.
Datasets: zsRE, CounterFact and MQuAKE-CF. There are 120 cells per dataset and 45 per condition.
Checkpoints follow **attempted edits 100, 300, 1,000**; record actual retained occupancy separately.
Proposed data realization seeds are 0/1/2, order seeds 100–104 and fixed reader/model seed 0.
Three reader training seeds on the same development split are not independent fresh-data realizations.

| Condition | Substrate and behavior |
| --- | --- |
| R1_learned_ff | Original base; proposed primary v4, three-pool text-null learned reader, plain lexical feature, rare-overlap minimum 1 / active-record DF maximum 2 |
| R1_nonlearned | Original base; random tied cosine reader, lexical and pairwise-null off, cosine floor .93, null threshold 1.01 |
| v0_stable | Original base; StableCap C1, DEC-035 |
| matched_update | Original base; MatchedUpdateCap C1, five normalized adjoint steps at learning rate .1 |
| v0_live_C1 | Original base; live C1 observations and declared v0 search |
| v0_live_C2 | Original base; live C2 observations and declared v0 site/search probes |
| S1_literal | Literal-continued base plus StableCap C1, no cap retraining |
| S1_LM | Fidelity-passing LM-continued base at weight lr 1e-8 plus StableCap C1, no cap retraining |

[Primary v4](../manifests/revision_v1/primary_condition_v4.json) seed-0 weights have SHA-256
`d42cd97a761ee7c56c041694f57c0f8ff31798ae45b99cf714728798ebb0f7ce`.
They were trained using **MQuAKE pool v2, 1,000 items**, not the self-contained v3 500-item pool.
The active tri3 retraining needs a new reader/reference identity and development evaluation before substitution.

Preserve stable observations, tied cosine, pairwise/query null, plain lexical overlap (`lex_idf=false`),
top-k 4, hard top-1, binary mass, null threshold .5, no cosine floor, zero fast-code steps, five per-position
delta steps at learning rate .1, tau .1 and A .3. Bind exact bank scales, radii, stop list, tokenizer,
answer masks, dimensions, constructor defaults, encoder/taps, serialization and byte accounting.

[Gated v3](../manifests/revision_v1/primary_condition_v3.json) is the two-pool fallback. Its seed-0 weight SHA is
`c5777b5bf0df754766463737f53f641f624de8bc98ac0420fd99bec8850730db`.
A fallback choice requires a versioned matrix/profile and an explicitly transfer-based MQuAKE interpretation.

The requested **45-cell v2 extension** is a separate block, making 405 if admitted. It binds the v3 two-pool
weights with an explicit `rare_overlap_min=None` deployment override. The v3 manifest itself describes a
gated condition. Against v4, this extension changes both training pools and gating; it is **not a gate-only
ablation**. A pure gate comparison requires the same weights, training, edits, queries and settings other than
the gate. Either rebind the extension to v4 weights or separately allocate a gated v3 comparator through a lead
decision. Neither change occurs here; the eight accepted conditions remain intact.

Continuation identities are bound by the matrix to:
`r1_24_control_v3.json` / `r1_24_literal_v3b` and
`r1_24_control_lm_v3_lr1e-8.json` / its same-named result.
The LM checkpoint SHA is `6ef32487c4f4e2641ee0b5aba966651741788a98549c27292e6d40fa583992c6`;
literal is `7591cfd1209f01c1d9877be6b596da56e3a3b45c2fa3e693cdb31407bbf59ef5`.
LM fidelity KL is **.0004736076008384771 nats**, NLL change **−.008859649300575256**, passing the .001 KL gate.
Literal KL is .000029332460329101195, NLL change −.00006179139018058777.
It is a numerical negative control, not exactly unchanged weights. Both controls' historical forward-token
matching basis is 771,581; final v4 total-cost equivalence is not established.

## 3. Development evidence and limits

The following values are stored 100-edit development stream summaries, reader seeds 0/1/2, stream seed 21.
They provide no independent-data confidence interval.

| v4 dataset | RET-GS seeds 0 / 1 / 2 | Immediate ES and RET-ES | Bounded LS |
| --- | --- | --- | --- |
| zsRE | .98 / .96 / .95 | 1 / 1 / 1 | 1 / 1 / 1 |
| CounterFact | .76 / .83 / .785 | 1 / 1 / 1 | 1 / 1 / 1 |
| MQuAKE | .79 / .68 / .56 | .92 / 1 / 1 for both metrics | 1 / 1 / 1 |

The .47–.82 MQuAKE range pools six readers across two training-pool sizes; v4's own three-seed range is .56–.79.
The earlier 500-MQuAKE readers obtain .80/.47/.82; the two-pool transfer reader obtains .16.
These comparisons support further same-source training investigation, not a universal claim that it is necessary.
Lexical/null diagnostics and threshold tradeoffs do not establish that the lexical feature is the sole cause.

IDF-weighted readers obtain MQuAKE GS .62/.74/.80 with ES .85/.99/.99. Plain lexical remains the reference.
IDF uses the same weighting definition in training and deployment, but training's episode memory is usually
64 supports and deployment's population is the current active store, often 100–1,000 records.
CPU tests establish equality given identical support populations and show the expected size/frequency dependence.

The often cited MQ outside result 0/100 at 100 records and drift approximately +.005 nats belong to the earlier
pool-v1 reader assay. CounterFact +.012 nats and zsRE unseen 10–11% likewise come from older reference identities.
They must not be silently pooled into a v4 all-endpoint certificate. Final-reference high-occupancy, full-text and
all-comparator profiles remain required. Pair outside IDs across checkpoints; older cross-size development
curves changed outside populations and do not isolate memory-size causation.

## 4. Population, role allocation and sealing

Use register v4, its rebound v1 exposure supplement and cumulative v2 supplement. The current capacities are
**zsRE 52,411; CounterFact 12,246 under the reason-specific exception; MQuAKE 2,100 distinct subjects**.
CounterFact strict policy remains zero. The DEC-042 final source receipt belongs to the lead.

R1-D7 distinguishes four policies: cumulative exclusions with scope amendment; executed-only clearance
(conditional MQ ceiling 2,829); query-role exemption retaining historical primary exposure (4,218);
and additional sources. The prospective 4,818 figure assumes away history and is not the query-only exemption.
Local MQuAKE-T has 1,868 cases but only 96 distinct edits / 86 subjects and is temporal, not automatically
admissible to MQuAKE-CF. No option is activated in this draft.

The nominal disjoint subject allocation per realization remains 1,000 edits + 100 outside + 100 near supports
+ 100 near neighbours + 50 explicit revision = **1,350**, or **4,050 per dataset**.
Composition closures may consume additional capacity. Containment within new training/dev slices does not
release historically exposed subjects. A reduced MQuAKE proposal must version both checkpoints and analysis
inventory, not silently truncate streams.

Canonicalization is NFKC, casefold and collapsed whitespace plus verified aliases only. Preserve independent
exclusion reasons, cross-dataset priority and all later exposure. Teacher eligibility is bounded base-wrong-new-
answer evidence, not proof of old-fact correctness. Teacher truncation policy and complete provenance need binding.

Before any allocation, measure joint eligible capacity with alias/context and role/dependency constraints.
Abort globally on shortfall before RNG or partial outputs. The R1-58 proposal retains proportional answer-token
length strata (1–2, 3–4, 5–8, 9+ including terminal), largest-remainder allocation with lexical tie-breaks,
realization/role order and separately derived PCG64 streams. Seed 158 remains a proposal; freeze exact source
order, NumPy version and seed derivation before use. Do not draw until the lead approves the final recipe.

Serial checkpoints: choose population/reference policy; complete eligibility/context review; freeze independent
expected inventories and RNG rules; allocate all roles once; construct locality/revision/composition cases and
verify token/schema round trips; write immutable payloads in assets and bind their hashes; lead freezes protocol,
code, models, environment, costs and inventory together. Existing development payloads are not final seals.

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

Every matrix cell names a future owner evidence directory:
`results/R1/stage4_dev_cells/pending_r1_40d_<condition>_<dataset>/`.
These names are requested profile receipts, not claims that those runs exist. Each of the 24 core condition/dataset
combinations (and three extension combinations if admitted) requires representative evidence at the exact identity.

| Field for each condition/dataset | Current value | Required receipt |
| --- | --- | --- |
| Cold initialization and compilation | null | One-time versus reusable setup separated |
| Edit work to 100/300/1,000 | null | Incremental edits, answer-length buckets and actual occupancy |
| Checkpoint 100 / 300 / 1,000 costs | null / null / null | Retention, LS, outside, drift, challenges, clone/restore separately |
| Serialization/restart and peak state | null | Exact restore, logical/physical bytes and memory peaks |
| Full-cell wall and watchdog seconds | null / null | Measured components plus explicit accepted headroom |
| Failure reserve and profile hash | null / null | Bounded retries, failed work charged, immutable profile identity |

The current owner development recipe checks only 100/300 on zsRE; completion alone cannot price 1,000 edits,
MQuAKE or every comparator. Never fill missing fields with zero or borrow learned timings as admitted limits.
The matrix is descriptive and not directly a final driver recipe; its nulls deliberately prevent admission.

Accounting: initialization + all edits + checkpoint retention/LS/outside/drift/challenge work + restore and final
serialization, charging each phase once. Reuse cap-off references only with identical base/tokenizer/window and
reference policy. Charge reader/continuation training, banks and failed jobs once per executed job, not per cell
or contrast. Reconcile forward tokens, reverse positions, padded/JIT work and measured wall/device time.
Historical continuation token matching does not prove v4 compute matching.

The old learned-cell proxy of 1,150 seconds gives **115 hours nominal + 23 hours reserve = 138 hours**
for 360 cells, or **155.25 hours** for 405. These are homogeneous planning scenarios, excluding unpriced/shared
work, not measured bounds or approved ceilings. At 138 hours, 5.75 uninterrupted accelerator-days precede
queue contention and serial admission work. Full scope was retained; measured cost controls and GPU leases remain.

No current calendar completion claim is justified. Refresh the plan-9 relative-day schedule with actual charged
spend, remaining training, population decision, eligibility, final profiles and execution queues. The population
decision is on the critical path even while GPU development proceeds.

## 7. Gate register U01–U18

“Complete” below describes a named artifact or evidence result, not automatic final admission.

| Gate | Status and next checkpoint |
| --- | --- |
| U01 scientific comparisons | Open: 360-core scope retained; declare deferred plan-9 branches and exact stronger-control claims |
| U02 reference | Partial: gate accepted; v4 three-pool and v3 fallback identities exist; self-contained tri3 selection and exact final-reference assays pending |
| U03 continuation | Fidelity component closed by DEC-047 and measured LM result; literal qualified; final v4 budget/config/profile binding remains |
| U04 zsRE freshness | Partial: 52,411 cumulative candidates; teacher/alias/context and post-snapshot exposure clearance pending |
| U05 CounterFact source | Proposed DEC-042 exception gives 12,246; final lead source receipt pending; strict zero retained |
| U06 draw/RNG/splits | Blocked for full MQ scope: 2,100 versus 4,050; D7 policy/scope decision then joint yield and exact seeds/strata |
| U07 payload/seal | Development payload builder and execution recipe tested; final three-dataset role payloads/seals not written |
| U08 endpoint cadence | Nominal 100/300/1,000 retained; bind full-validation/tail and challenge cadence; version if MQ scope changes |
| U09 challenge semantics | Composition module and development assay implemented; final compatible dependencies/aliases/reservations remain |
| U10 LS convention | Open: bind primary bounded/complete-pair rule, decode limits and original/continued reference policy |
| U11 implementation | Prior cache/identity repairs completed; comparator adapters and development driver CPU-tested; X10 loader/trace/provenance requests remain before applicable final use |
| U12 contrasts/multiplicity | Open: lead family across three datasets and eight controls; 45 extension allocation and training/gate confound unresolved |
| U13 classifier/fidelity | CPU .05/−.02/−.01 machinery tested; bind final applicability, inequalities and full-reference fidelity/drift |
| U14 secondary thresholds | Composition descriptive at observed floor; no numerical success margin; unseen/revision/scale decision rules still open |
| U15 analysis adapter | Three-dataset CPU inventory/adapter complete; final independent expected IDs, reference endpoints and confirm admission pending |
| U16 budget | Full scope accepted; owner profiles active; all-condition/dataset/checkpoint ceilings and shared costs remain null |
| U17 execution controls | Draft matrix v4 binds 33 source identities; dry freeze candidate exists; final code/environment/queue/retry/resume receipts not admitted |
| U18 schedule | Open: refresh spend ledger, calendar anchor and critical path after population/reference/profile decisions |

Installed CPU verification for round 12: **507 passed, 8 skipped** across revision-v1 and package layout,
including 23 new tests; [log](../logs/r1_round12/installed_cpu.txt). This does not substitute for GPU profiles or
scientific admission. No active training or driver code was edited.

## 8. Freeze contents and concurrent work

The final lead freeze binds the accepted protocol and decisions; matrix and contrast inventory; full executable
code/environment/hardware/determinism; original/continued base and reader checkpoints; tokenizer/calibration,
masks and gates; cumulative exclusions; eligible ordered role payloads and challenges; training/validation
separation and caches; denominators and references; state accounting/eviction/restore; per-job/total ceilings,
retry/overshoot and shared costs; analysis settings and lead approval identity. A register freeze alone is insufficient.

CPU work can continue on subject-class clearance, aliases/contexts, independent endpoint inventories and the
X10 edit requests after permission. The owner can complete tri3 evaluation and exact development profiles in its
own files. Lead decisions on population scope, final reference, contrast interpretation and budget precede
draw/seal/freeze. Final preparation remains serial at those boundaries; extra agents cannot remove those decisions.
