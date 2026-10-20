# Post-conference programme, version 2 (agreed direction after three reviews)

Capstan, 20 October 2026, for charlie derr, Capex and Derp Peoples. Supersedes the sequence in [Capstan's proposal](post_conference_capstan_proposal.md) where the two differ; incorporates [Capex's feedback](post_conference_capex_feedback.md) and [Derp Peoples' review](post_conference_capstan_review.md) of that proposal, and the parts of [Capex's original plan](post_conference_research_plan.md) and [its review](post_conference_research_plan_review.md) that both later documents asked to keep. Written while Phase 0 is running; §6 records what changed mid-stream.

**Aim (Capex's wording, adopted).** Establish where a local predictive-coding learning rule offers a measurable advantage under explicit information, memory and compute constraints. A well-controlled benefit, an explained trade-off, or a negative result that rules out the current mechanism each counts as progress. We do not require proof of something backprop "cannot provide".

## 1. Corrections to the record and to the proposal

These change what the later experiments are allowed to assume.

1. **MQuAKE item-locality is not a same-subject failure.** All 600 item-locality rows share the *relation template* of their parent edit with a different subject; 40 rows (39 distinct prompts) are exact prompts of other taught stream items, scored against their old answers. 93 of 97 (BP) and 93 of 101 (PC) severe events across the three seeds fall on those 40 rows, where every reader fires on its own record for that item. On the remaining 560 rows the counts are 0–4 severe events per seed. Both Capex and Phase 0 found this independently. Consequences: (a) the extremes study's assembler now labels those rows `locality_item_taught` and the supplement carries a corrigendum that keeps the historical all-row numbers beside the two strata, not a silent replacement; (b) hard negatives for any selection fix must be labelled against the **whole active memory at the evaluation horizon**: a prompt that should invoke another taught record is a positive for that record; (c) the "≤ 3 severe events per seed" target is already met on the valid stratum, so the preservation population must be defined before an improvement is demanded.
2. **"Selected own record" meant "own record among the four candidates".** New analyses use separate fields: own record retrieved (candidate recall), own record is the pre-veto winner, gate accepted, applied record correct/wrong. Phase 0's `selection_table.parquet` carries these; the legacy column keeps its meaning and name.
3. **The failure atlas separates retrieval, gate and payload.** On CounterFact, roughly a third of each reader's abstained paraphrase failures never had the own record among the four candidates; no threshold could have applied it. On MQuAKE, 27–43 BP (31–35 PC) paraphrase failures per seed fired the correct record and still failed. "Selection first" holds for CounterFact's gate failures, not for its retrieval misses nor for MQuAKE's payload failures.
4. **Chaining between banks is not a property of these readers.** The learned readers select once at the prompt from a write-free pass, cache the selection and apply one record's writes at the three sites; later banks never retrieve a different record because of earlier writes. 78 of the 80 composition cases have one taught dependency; the other hop is the frozen model's own knowledge. The registered composition endpoint evaluates fresh-start dependency-edit states, not a query into the 300-edit memory. Item 5 of Phase 0 is therefore an architecture and dependency audit plus a frozen-base ceiling, not a chaining search.
5. **The acquisition stopping trace is not in the saved artifacts.** The learned-reader evaluation runner serialises only outcome codes and costs; per-prefix losses and threshold flags are absent from all six MQuAKE streams. Forward-only forced-record scoring measures current payload adequacy; it cannot recreate the historical trace, and acquisition reruns are not part of the forward-only budget.
6. **Numbers corrected in the proposal.** The CounterFact paraphrase PC loss is 2.43 nats/token and the PC−BP gap 1.12, not 2.4. The ordinary-text ES99+ baseline "≤ 0.02 nats" describes zsRE only (BP 0.014, PC 0.0016); CounterFact is 0.29 / 0.33 and MQuAKE 0.23 / 0.23. The near-miss false-fire ranges 8–21 % (BP) and 3–8 % (PC) are zsRE observations. Targets are dataset-specific (§4).
7. **The completed ePC contrast stays as evidence about that estimator.** It is a finite-step error-state solver with global autodiff cost, retired as the next large reader-training instrument; it is not dismissed as "not PC" nor described as merely a noisier gradient. The new small implementation compares activation-state and error-state versions of the *same* small model and energy; equilibria should agree, finite-step trajectories need not.

## 2. Phase 0 (running): cheap analyses, forward-only GPU

Items and their status at the time of writing; the result note is `results/post_conference/phase0/phase0_report.{md,pdf}`.

| Item | Change from the proposal | Status |
|---|---|---|
| 1 Gate frontier | Threshold sweep composes candidate-on and cap-off outcomes once per probe (the one-selection, hard-top-1, binary-write rule makes this exact); **all gates respected**: the rare-token veto is evaluated on every forced acceptance, because the learner only evaluates it after the null gate passes. Selection risk (wrong record accepted) and answer risk (failed generation / higher NLL after application) reported separately against coverage. Validation against the registered operating point (replay reproduces saved losses exactly). Coincident curves mean similar trade-offs on this population, not identical gates or representations; arm-specific acquired payloads are a confound to name. | replay rerun with the rare-veto fix scheduled |
| 2 Failure atlas | Fields per §1.2; oracle selection rate (Derp Peoples §3.1) reported; difficulty and answer-length splits | done |
| 3 In-context arms | Kept as full comparators: oracle own fact, frozen-feature knn, lexical; plus a **matched arm** that places the record the cap actually applied, under the cap's own abstention decision, into the context (isolates how the supplied fact is used; Capex §6). Context format chosen on development examples and locked; only the common answer tokens are scored; NLL reported with and without the terminator because a one-shot context demonstrates the answer format; exact match reported strict and prefix; context tokens, per-query wall time and peak memory reported (Derp Peoples §3.8). | three arms done; matched arm and cost columns in the next forward-only slot |
| 4 Locality audit | Population and target-consistency audit per §1.1, with the all-row table and both strata; same principle applied to zsRE and CounterFact (no overlap found) | done; corrigendum applied to the extremes study |
| 5 Composition | Architecture/dependency audit (§1.4) and frozen-base ceiling: dependency retrieval and gate acceptance on multi-hop wordings; frozen GPT-2 small's knowledge of the unedited hop with the new entity; multi-hop loss with the taught fact in context | done |
| 6 Reserves | Certified-register replay for zsRE/CounterFact (684 / 721, no overlap with the reader-training pool); MQuAKE from population tables only (4,549, upper bound) | done |

Budget: profile before expanding; the four-hour ceiling is a limit, not a forecast. One concise result note, not a prescribed ten pages.

## 3. Phase 1: the small-reader harness and the first controlled comparison

**Objective made explicit (Capex §4).** The cached-feature harness trains **record/null selection on frozen observations** with fixed payloads and the same supervised labels for every rule. It does not reproduce the episodic trainer's answer-NLL and preservation-KL terms, which need GPT-2 with the current writes; a table of precomputed candidate-on outcomes can support a declared fixed-candidate cost-sensitive objective, labelled as such. Shortlisted readers are evaluated through GPT-2 for answer accuracy and collateral harm. Training cost includes feature extraction and final evaluation. Selection-classification metrics are kept distinct from output NLL, entropy and KL.

**Labels.** Positives and negatives are defined against the whole active memory (§1.1). Hard negatives are matched-template, different-subject prompts (the zsRE near-miss neighbours and MQuAKE's same-relation locality prompts are where the genuine false fires are); same-subject different-relation negatives would be a new, explicitly constructed development population.

**Deliverables.**

1. Feature cache (taps at blocks 4/8/12, last prompt position; key-rebuild policy recorded) and the harness, with tests for target leakage, state restoration, gradient signs, unpaired examples and missing null mass.
2. Matched small reader trained by BP and by activation-state PC; the error-state version of the same small model as the numerical reference (not the GPT-2 solver); finite-difference checks of energies and local partials; locality of updates verified in code (local autodiff primitives disclosed).
3. **D1 as a named deliverable** (Derp Peoples §3.1): paired representation diagnostics on the Phase-1 BP/PC checkpoints (embeddings, record/null margins, write directions, prediction changes; centered kernel alignment as a descriptive tool), with equal tuning allowances recorded.
4. Selection frontier of every arm on development data, with the in-context arms and frozen on the same axes.
5. Oracle replay (A2) on the Phase-1 readers.

**H1 (energy-based abstention) is gated by a feasibility fixture (Capex §4).** For the plain feedforward PC energy, setting each free state to its feedforward prediction zeroes every residual for familiar and unfamiliar inputs alike, so an unclamped settle gives no confidence signal by construction. Before any H1 investment: demonstrate nontrivial, label-free inference on a tiny fixture with relevant, irrelevant and ambiguous queries, with a generative model that reconstructs the observed query features conditional on each candidate record and an explicit null hypothesis, comparable candidate/null energies, and stated normalisation and calibration. The gold record and answer are unavailable to this inference. If the fixture passes, H1 proceeds with the BP unrolled-refinement control given the same information, energy architecture, inference budget, learning-rate sweep, early-stopping protocol and tuning allowance, and its development ceiling reported beside the comparison (Derp Peoples §3.2). If the fixture is not ready, **H2 runs first**.

## 4. Phase 2: H2, online learning with less interference

Design points added from Capex §4:

- **Keys.** The reader's tied query/key embedding makes stored keys stale when the reader updates. Either recompute keys from immutable cached base observations after each update, or freeze the key representation in both arms; charge rebuild time and retained observations to cost and memory.
- **Payloads and acquisition fixed** while reader learning is tested. Separate failure to retrieve an old record from forgetting caused by eviction or a deliberate revision.
- **Matched new-task learning.** Compare old-task retention at matched new-block acquisition as well as at equal updates and equal measured compute; a method that changes less can preserve old behaviour by failing to learn.
- **Replay.** BP and PC without replay first; if replay is used to interpret a difference, both rules get the same small replay budget. The value of locality is never inferred from BP+replay versus PC alone.
- **Memory accounting** counts feature caches, source tokens, optimizer state and replay data; a persistent record used for inference is distinguished from revisiting it as a training example.
- **Synthetic-to-real gate (Derp Peoples §3.5, as amended by Capex).** The real-data pilot proceeds when the synthetic streams show working learning, measurable interference and an interpretable BP/PC comparison, whatever its sign. A favourable PC gap is not the criterion; a clear null still justifies one bounded real-data transfer test.

## 5. Parallel and deferred work

- **E1 minimal (Derp Peoples §3.4, scoped by Capex §7).** An H3/NESS specification and a few synthetic two-hop fixtures may proceed in parallel if Derp Peoples or a human collaborator has capacity. A full JAX H3 port is not an immediate primary deliverable. E2 (explicit compositional operation) and any transfer to MQuAKE are conditional on Phase 0's ceiling: frozen GPT-2 small answers the unedited hop on about a tenth of cloze prompts, so composition on this base is bounded by base knowledge before any cap mechanism.
- **Deferred:** singular learning theory (D3), distributed execution (F), the coupled objective (until the collaborators answer the four questions in the proposal). Decision at the first results discussion.

## 6. Targets, by phase and dataset

Development targets written before tuning; the column says which phase is expected to deliver each, and which are conditional.

| Property | Now (300 edits, seed means) | Target | Phase / condition |
|---|---|---|---|
| Own-prompt retention | 99–100 % | ≥ 99 % | hold |
| CounterFact paraphrase retention | 81.5 % BP, 66.9 % PC | ≥ 90 % | Phase 1 selection + retrieval; bounded by the oracle-rescue ceiling measured in Phase 0 |
| MQuAKE single-hop paraphrase retention | 67.4 % BP, 59.6 % PC | ≥ 80 % | **conditional**: Phase 0 shows 9–14 % payload failures; needs a write-transfer change (deltas acquired on more than one wording, or a code-conditioned controller write), not selection alone |
| zsRE near-miss / unseen false fires | 8–21 % / 4–14 % BP; 3–8 % / 2–5 % PC | ≤ 2 % | Phase 1 hard negatives |
| MQuAKE genuinely unrelated locality, severe events (560 prompts) | 0–4 per seed | ≤ 3 per seed | met on the valid stratum; hold |
| Ordinary-text ES99+ (BP / PC) | zsRE 0.014 / 0.0016; CounterFact 0.29 / 0.33; MQuAKE 0.23 / 0.23 | no increase, paired by seed | every phase |
| Relative to in-context retrieval | caps beat the in-context oracle on paraphrase NLL on all three datasets (Phase 0) | state which of accuracy, context tokens, latency, memory, harm the cap wins on | every table |

## 7. Division of work and protocol

Capex: analysis modules, failure atlas extensions, D1 diagnostics, independent audits (as the 20 Oct audit script). Capstan: harness, feature cache, PC implementation and tests, GPU dispatch, result notes. Derp Peoples and human collaborators: H3/NESS specification and fixtures, conceptual review. Lane ownership changes only when the lead says so; disagreements between agents are escalated to the lead, not blocking (Derp Peoples §3.7). One dated line per cross-lane result in `docs/post_conference/decisions.md`. One config, one runner, one table bundle, one concise note per study.

## 8. Change log against the proposal

| Review point | Change |
|---|---|
| Capex §1 locality | §1.1 here; Phase 0 item 4 redefined; corrigendum in the extremes study; labels against the whole memory; target re-based on the valid stratum |
| Capex §2 selection fields and gates | §1.2; frontier replay re-run with the rare-token veto on forced acceptances; selection vs answer risk columns; wording on coincident curves |
| Capex §3 chaining | §1.4; Phase 0 item 5 redefined |
| Capex §4 harness objective, H1 fixture, H2 design | §3 objective paragraph; H1 gate; §4 bullets; H2 default if the fixture is not ready |
| Capex §5 numbers, acquisition trace, ePC wording | §1.5–1.7; §6 targets |
| Capex §6 in-context | matched-record arm; locked format; answer-only scoring; cost columns |
| Derp Peoples §3.1 D1 | named Phase-1 deliverable |
| Derp Peoples §3.2 control tuning | H1 paragraph |
| Derp Peoples §3.3 target phases | §6 column |
| Derp Peoples §3.4 E1 | §5, scoped as Capex suggested |
| Derp Peoples §3.5 transfer criterion | §4, with Capex's amendment |
| Derp Peoples §3.6 field audit | done inside Phase 0 (fields present; acquisition trace absent, §1.5) |
| Derp Peoples §3.7 escalation | §7 |
| Derp Peoples §3.8 in-context costs | Phase 0 item 3 |
