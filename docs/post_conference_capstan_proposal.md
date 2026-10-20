# Capstan's response to the post-conference plan: what to do now that there is no deadline

Capstan, for charlie derr and collaborators · 20 October 2026

Inputs: Capex's [post-conference plan](post_conference_research_plan.md) (19 Oct), the Derp Peoples / Omega [review](post_conference_research_plan_review.md) (20 Oct), the [cap-value supplement](../results/extremes_analysis/ext-20261009/reports/cap_value_report.md) and its `tables/cap_value/` CSVs, the [PC-reader](additional_work/PC-reader.md) specification and [report](additional_work/PC-reader_report.md), [PC-v1](additional_work/PC-v1_report.md), [HT-17](additional_work/HT-17_report.md), the [H3 distillation results](gen-trans/H3_distillation_results.md), the [coupled-objective note](additional_work/coupled_objective_note.md), the cap source under `src/pccap/cap/` and the ePC solver `src/pccap/pc/epc_inference.py`. This is a proposal for discussion, not a launch record. Nothing is scheduled and no GPU work has been started.

The lead's two goals are the ones I organise around: **(G1) decent cap behaviour** and **(G2) a demonstrable value of predictive coding that backprop does not provide**. My recommendation in one paragraph:

> Keep Capex's A (selection) and the B×C intersection (online learning with a small, genuinely local PC reader). Narrow everything else. Before any new training, spend one week on cheap analyses of saved results and forward-only reruns that answer three questions we have never asked: are the BP and PC readers merely at different operating points on the same gate frontier; how much of the remaining error is payload rather than gating, per dataset; and how far does frozen GPT-2 get when the taught fact is simply placed in its context. Then build one shared artefact, a cached-feature small-reader harness, and use it to test the two hypotheses where PC has a structural mechanism BP lacks: iterative query-time inference as the abstain/commit decision, and low-interference online learning. Defer singular learning theory, NESS and distributed execution until that harness exists and has produced one result.

## 1. What I agree with in the plan and the review

Capex's plan is careful and I would not reopen its foundations: frozen GPT-2 small as substrate, local JAX only, exposed streams for development and reserved populations for confirmation, paired seeds, equal-updates separated from equal-compute, the checkpoint structure, the effect-size screens in §11, the new `aw/post_conference/` namespace, and the instrumentation list in §3.3 (per-prefix NLL, H(base), H(cap), both KL directions, record/null mass, write norms; energy, residual and settling count for PC). The review's nine suggestions are all sound and cheap; I would adopt them, in particular the oracle selection rate (3.1), cross-checking any activation-state PC against the error-state reference (3.3), reporting step-matched and loss-matched LLC comparisons (3.4), and the request to cite or set aside the one-month plan's routing results (§4).

## 2. Where I differ

### 2.1 The plan is too wide for two agents and one 12 GB GPU

Experiments A–F plus §9 open seven lanes in two weeks and 32 process-hours. The review endorses that breadth ("proceed as written"). The conference programme showed what happens with many parallel lanes: most of our wall-clock went to reconciliation, receipts and reports rather than to the mechanism. With no deadline the right move is the opposite: fewer, deeper experiments and one shared piece of infrastructure. I would run A and the B×C intersection, keep D1 as a by-product of the same runs, and make D3, E and F conditional on a result from the first two.

### 2.2 The ePC estimator we have is not a test of predictive coding's merits

The "PC-CAP" in all our figures is a reader trained with a *global* error-state solver: eight settling iterations of gradient descent on the error variables of the full twelve-block GPT-2 graph, each iteration itself an autodiff pass (`epc_inference.py`). Only the base-dependent answer/preservation gradient estimator differed between arms; retrieval and the reader VJP were exact autodiff in both. So the completed BP/PC contrast is "exact gradient versus an eight-step approximate gradient at 96–102× the cost". It cannot show locality, because nothing in it is local, and it cannot show a learning-dynamics advantage, because the reader update rule was the same AdamW step on a noisier gradient. The 2.4-nat CounterFact paraphrase gap and the cost ratio are facts about that estimator, not about PC. I would state this plainly in whatever we publish next and retire the through-GPT-2 ePC solver as the instrument for *reader* training. It stays as a historical result and as the error-state reference the review asks for in C3.

### 2.3 The BP and PC readers may be the same frontier at two thresholds

The supplement's gating table shows the PC readers abstain far more (CounterFact paraphrases: PC 19–41 % versus BP 12–16 %) and fire far less on things they should not (zsRE near-miss neighbours: PC 3–8 % versus BP 8–21 %; unseen prompts: PC 2–5 % versus BP 4–14 %). Lower retention with fewer false fires is what one gets by raising a threshold. Nobody has drawn the two readers' risk–coverage curves. If they coincide, "PC is more conservative" is an operating-point artefact and the honest statement is that the two training rules produced the same gate. If PC's curve dominates at low coverage, that is a real result in PC's favour that we have been under-reporting. The saved `null_mass`, `best_score` and `selected_own_record` fields allow the decision side of this on CPU; the loss side needs forward-only reruns at new thresholds (acquisition was done at the fixed threshold, so only read-time decisions change). This is the single cheapest informative experiment available and should come first.

### 2.4 "Selection first" is right on CounterFact and only half right on MQuAKE

On CounterFact, 90–100 % of each reader's own worst 5 % of paraphrases are abstentions and the fired paraphrases succeed 95–97 % of the time; gating is the bottleneck. On MQuAKE, 28–45 of 300 BP paraphrases (32–36 for PC) *fired and still failed*, and fired-paraphrase success is only 82–87 %. That is a payload or generation failure of roughly the same size as the gating failure. Experiment A2's oracle will expose it, but the plan should expect it and budget for the acquisition diagnostic: per-prefix threshold attainment is already recorded by `cap.learn.update_item`, so we can read off on CPU how often the five-round, A = 0.3 acquisition stopped short on MQuAKE targets before touching the GPU.

### 2.5 The equal-information baseline should be a full arm, not a subset

The strongest competitor to a cap is not a frozen model. It is the same frozen model with the retrieved fact placed in its context. That arm is forward-only on GPT-2 and costs minutes for 300 edits. If in-context retrieval reaches 90 % CounterFact paraphrases, then the cap's value is latency, memory bytes, locality and tail harm, not accuracy, and our figures should say so. If it reaches 60 %, the cap's write mechanism is genuinely adding something. Either answer changes what "decent cap behaviour" means. GRACE (`src/pccap/baselines/grace_jax.py`) exists as a second key-value adapter reference and can be loaded read-only.

### 2.6 Test chaining inside the cap before building a symbolic executor

Banks act sequentially; a bank-1 write changes what bank 2 reads, and the code already logs this as "retrieval drift". That is a primitive for two-hop composition we have never examined: for MQuAKE cases where both hop facts are in memory, does bank 2 or 3 ever select the hop-2 record after bank 1 fires on hop 1? If never, composition needs an explicit mechanism and Capex's E2 join is justified. If sometimes, the cheapest composition experiment is to train for it. This is a CPU read of saved logs if the drift records survived, otherwise a short forward-only rerun on the 80 cases.

### 2.7 The locality failure on MQuAKE is a hard-negative problem

Both caps got worse than frozen on 7.7 % of MQuAKE item-locality prompts, with about 33 deteriorations above 2 nats per seed, while the registered 50-prompt locality endpoint read 100 %. Those prompts share a subject with a taught fact and ask a different relation. The reader training recipe's negatives were other items' paraphrases and ordinary text; same-subject different-relation prompts were absent. Any selection change in A4 should train on exactly those negatives, which the datasets supply for free. This is a rule-agnostic fix and part of G1 regardless of PC.

## 3. Where PC could add value that BP cannot, and how to test it honestly

For a three-layer reader on cached features, BP is cheap and exact. PC can only win where BP's assumptions hurt. Two such regimes are reachable on this machine; one is not.

**H1 — iterative query-time inference as the gate.** A feedforward reader decides fire/abstain from one pass. A PC reader can settle latent "which record, or none" states against the evidence (the three tap features and the memory) with no label, and its terminal energy or residual is a confidence signal with a definition, not a learned logit. Hypothesis: at equal parameters and equal test-time operations, energy-based abstention gives a better risk–coverage frontier on CounterFact and MQuAKE paraphrases, near-miss neighbours and same-subject locality prompts than the feedforward null probability. Controls: the same architecture trained by BP with a feedforward gate; the same architecture with an *unrolled k-step refinement* trained by BP at equal test-time cost, to separate "iteration helps" from "PC helps". This is Capex's C3.4 made primary instead of optional. It uses cached features and never differentiates through GPT-2.

**H2 — online learning with less interference.** The published case for PC in continual learning (prospective configuration: infer activity first, then change weights; reported to reduce interference relative to BP in sequential tasks) applies exactly to a reader that must keep learning as the memory grows and facts are revised. The conference readers were frozen after 300 updates; this regime was never tested. Hypothesis: in B1b streams with block structure and revisions, the small PC reader loses less earlier-block paraphrase retention per unit of new-block acquisition than the same architecture under BP, at equal updates, equal data and no replay; and the gap closes when BP gets a replay buffer, which quantifies what PC's locality is worth in replay bytes. Endpoint: the forgetting matrix Capex defines in B2. Secondary: sensitivity to learning rate and to update-order shuffles, where PC is claimed to be more forgiving.

**Not reachable here: a measured distributed advantage.** With one GPU, locality can be verified as a code property and simulated with stale messages, but a speed or scaling claim needs hardware we do not have. I would keep F as Capex wrote it and not spend first-tranche hours on it.

**Expected nulls.** On a small reader H1 may lose to the unrolled-refinement control, and H2's effect may vanish under modest replay. Both are publishable and both are more informative than another ePC-through-GPT-2 run. If both fail, PC's remaining case in this testbed is systems-level, and we should say so.

## 4. What "decent cap behaviour" should mean

Proposed development targets, to be frozen before the confirmation run and reported with the three-model convention (frozen, BP-CAP, PC-CAP) plus the in-context arm:

| Property | Now (300 edits, seed means) | Target |
|---|---|---|
| Own-prompt retention | 99–100 % | ≥ 99 % |
| CounterFact paraphrase retention | 81.5 % BP, 66.9 % PC | ≥ 90 % |
| MQuAKE single-hop paraphrase retention | 67.4 % BP, 59.6 % PC | ≥ 80 % |
| Near-miss / unseen false fires | 8–21 % / 4–14 % BP; 3–8 % / 2–5 % PC | ≤ 2 % |
| Same-subject locality deteriorations > 2 nats (MQuAKE, 600 prompts) | ≈ 33 per seed | ≤ 3 per seed |
| Ordinary-text ES99+ versus frozen | ≤ 0.02 nats (these readers) | unchanged |
| Relative to in-context retrieval | unknown | state which of accuracy, cost, harm the cap wins on |

The targets are judgment calls for discussion. The point is to have them written before we tune, so that "decent" is not whatever we reach.

## 5. Proposed sequence

**Phase 0 — one week, CPU plus forward-only GPU (≤ 4 process-hours).** Everything here uses saved results or GPT-2 forwards; no training.

1. Risk–coverage curves for the six existing readers from saved scores, then loss at swept thresholds by forward-only replay (§2.3).
2. Failure atlas (Capex A1) with the review's oracle selection rate, split into abstained / fired-but-failed / wrong-record / false-fire per dataset; acquisition-bound attainment from the per-prefix records (§2.4).
3. In-context retrieval arm on the same 300-edit streams for all three datasets (§2.5).
4. Same-subject audit of the MQuAKE locality deteriorations (§2.7).
5. Chaining diagnostic for the two-hop cases (§2.6).
6. Inventory of unexposed subjects per dataset; the 684 / 721 margins recorded on 2 October are dated.

Output: one table bundle and a ten-page note. Decision: which of §3's hypotheses to test first and what the in-context bar is.

**Phase 1 — two to three weeks (≤ 12 process-hours).** Build the shared artefact: a cache of the three tap features for the training episodes and probes, and a small-reader harness that trains and evaluates on the cache without GPT-2 in the loop, with the per-prefix log from §3.3 of Capex's plan. On it: C2/C3 (matched small reader, BP versus activation-state PC, finite-difference and error-state cross-checks, locality tests in code); H1 with its two controls; hard-negative training in every arm; oracle replay (A2). Full GPT-2 evaluation only for arms that clear the development frontier.

**Phase 2 — two to three weeks (≤ 12 process-hours).** H2: B1a/B1b streams, synthetic first then the 300-edit development stream, with the Phase-1 readers under BP, BP + replay and PC; bounded memory with a declared eviction rule; forgetting matrices and revision behaviour.

**Phase 3 — one continuation, chosen from evidence.** Explicit composition (if §2.6 shows no chaining), distributed simulation (if H2 or the locality tests give a reason), or the coupled objective (when the collaborators have answered the four questions in the proposal). GPT-2 medium as an external-validity check is feasible on 12 GB but is a separate study and should wait.

**Confirmation.** Fresh subject realizations, three paired seeds, pre-declared targets from §4 and Capex's §11 screens, three-model-plus-in-context reporting, negatives kept.

Total: about 30 accelerator process-hours over six to eight weeks, similar to Capex's ceiling but concentrated on two hypotheses instead of seven lanes.

## 6. Division of work and protocol

Capex: Phase 0 items 1, 2, 4, 6 and D1 diagnostics on the Phase-1 runs; Capstan: Phase 0 items 3 and 5, the feature cache and small-reader harness, the PC implementation and its tests, GPU dispatch; Derp Peoples and human collaborators: NESS specification and H3 reference fixtures in parallel, review of the Phase-0 note. For the review's cross-lane escalation (3.7): a result that moves a question between lanes is recorded as one dated line in a shared `docs/post_conference/decisions.md`, and the owning agent changes only when the lead says so. Otherwise Capex's light protocol stands: one config, one runner, one table bundle, one concise report, and tests for the failure modes that would invalidate a conclusion (target leakage, state restoration, gradient signs, unpaired examples, missing null mass).

## 7. Summary of recommendations

1. Run Phase 0 before any training; it costs a week and answers whether the BP/PC difference is a threshold artefact, where the payload problem is, and what in-context retrieval already achieves.
2. Retire the through-GPT-2 ePC solver as the reader-training instrument; keep it as the error-state reference.
3. Build the cached-feature small-reader harness as the one shared artefact.
4. Test H1 (energy-based abstention) and H2 (low-interference online learning) as the PC-specific hypotheses, each with a BP control that isolates the mechanism.
5. Make the in-context retrieval arm and same-subject hard negatives standard in every comparison.
6. Fix "decent cap behaviour" targets now (§4) and report the three models plus in-context in every figure.
7. Defer LLC, NESS and distributed execution until Phase 1 has produced a result.
