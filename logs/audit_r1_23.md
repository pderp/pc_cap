# R1-23 — installed data-separation and update-path audit

The public read API and support/query separation pass the checks below, but **the installed Stage 1–2 implementation does not yet pass the full plan-9 scientific gates**. CPU controls reproduce loss-normalization, rejected-update, query-boundary, snapshot and byte-accounting defects. The current pilots train a zero-fast-step reader/controller over a frozen base; they do not implement the guide's differentiable adaptation reference or alternating base-update pair.

Scope: read-only audit of `src/pccap/revision_v1/`, the pilot, loss-source table, plan 9/DEC-034, and coding-agent guide pp. 3–6. Core code and GPU pilots remain the orchestrator's lane. This report proposes changes; it applies none. Source identities are recorded in [r1_23_controls.json](r1_round2/r1_23_controls.json) and [r1_23_boundaries.json](r1_round2/r1_23_boundaries.json). Controls use a random 12-block, width-16, vocabulary-64 GPT-2-shaped **CPU** base, not a performance benchmark.

## What passes

| Assigned boundary | Result and limit |
| --- | --- |
| `RevisionCap.predict` / `selection_for` have no target input | Signatures accept IDs and, for predict, `full`. No target/label data-flow into these methods was found. Poisoning all held-out label fields while preserving prediction inputs leaves predictions bit-identical and persistent state unchanged when query boundaries are explicitly reset. |
| Fast teaching uses supplied support | `support_from_edit_item` carries supplied prompt/answer, not held-out paraphrases or scoring aliases. `adapt_record` differentiates only the taught code; unrelated record arrays and reusable/base weights stay fixed in the tested accepted updates. Rejected-update transaction semantics fail separately below. |
| Outer labels remain in the outer container | `featurize` indexes `LabeledEpisode.query_labels` by query ID. L1 uses new-paraphrase/old-fact targets; L3 uses cap-off logits only for near-miss/unrelated roles; composition is counted as skipped. No revised answer is scored against the teacher in the normal generated role assignments. |
| Observation passes are unedited | `ObservationEncoder.observe`, learner selection/read observations, support observations and training features call `base.forward(..., ())`. The spy observes zero writes; actual base arrays remain unchanged. `observation_from_pass` itself trusts its caller; preserve this invariant at new call sites. |
| Default parameter count | Independently initialized default reader/controller have **3,282,689** float32 parameters, under 5 million. They occupy **13,130,756 bytes** before records, indices or caches. The current byte report omits those weights. |

The API check is stronger than a signature-only assertion but remains bounded: it does not prove every future evaluator respects the boundary. Generated labels supply the provenance contract; `train.py` has role dispatch, not a separate runtime assertion validating every target-source label against the loss-source table.

## Findings and concrete checkpoints

### R23-01 — High: reported means and optimized gradients disagree

Sources: `train.py:166` (`episode_grads`), `epc_train.py:113` (`episode_grads_epc`), loss-source table L1/L3; guide p. 5. Both accumulators sum prefix gradients with the configured coefficient, then divide **metrics only** by each term's count. Retrieval is already a per-query mean. The existing finite-difference test explicitly reconstructs the summed objective, so passing it does not validate the declared mean objective.

Controlled duplication of one identical prefix gives:

| Term | Reported mean, one / duplicated | Gradient norm, one / duplicated |
| --- | ---: | ---: |
| Answer | 3.636373 / 3.636373 | .427263 / .854526 |
| Preservation | .002278315 / .002278315 | .005743832 / .011487665 |

The duplicated gradient equals twice the original exactly at stored precision. A deterministic stand-in for ePC write gradients reproduces the same accumulator defect; this control does not test ePC convergence. Longer answers/more preservation prefixes change the effective weighting against retrieval and across episodes. Global clipping/Adam does not generally remove a relative-loss-weight error.

**Owner change:** compute each term's evaluated prefix count before accumulation and divide that term's gradients by its own nonzero count; retain separate counts and means. Apply the same definition to BP/ePC. **Checkpoint:** duplication invariance for each term; a finite-difference check against the weighted *mean* objective; zero-count and unequal-length episodes. Reinterpret current pilots as using the summed objective until a versioned rerun exists.

### R23-02 — High scientific gap: support answers do not enter zero-step record construction

Sources: `train.py:78–125`, `_records`; `adapt.py:59`; `scripts/r1_21_pilot.py:92`, `:130`; guide pp. 4–5. Support features are computed from `s.prompt_ids` only. Initial keys **and fact codes** use those features. Support answers enter `adapt_record` only through code optimization, while the current pilot evaluates with `FastConfig(steps=0)` and featurizes training episodes without fast updates.

Changing all five support answers, with prompt observations and outer query labels fixed, leaves support features, initial keys and codes **bit-identical**. This deliberately inconsistent-label intervention tests input dependence; it is not an efficacy score. Training query targets do influence the reusable weights, which is permitted outer supervision. It does not establish that an arbitrary *new support answer* can be stored by this zero-step mechanism. A revised answer swap cannot change its initial code.

`LossConfig.fast_steps` does not run an unroll. `_records` accepts manually populated `fast_delta` as a stopped constant, and the pilot never supplies one. The local loss table openly declares zero steps and a possible first-order approximation, but that is not the guide's reference, which differentiates through a fixed short adaptation unroll and derives values from supplied facts/question-answer pairs.

**Owner change:** keep the existing treatment under a precise name such as “frozen-base, zero-step cap training.” Implement a support-answer-sensitive value path and/or actual support-code adaptation in training and evaluation. Implement the differentiable fixed-unroll reference separately from a stopped-delta alternative, or seek an explicit plan amendment. Reject unsupported nonzero `fast_steps` rather than silently ignoring it. **Checkpoint:** hold prompt fixed, swap taught answer, keep query text fixed, and verify memory/prediction sensitivity; old/new revision discrimination; finite-difference gradient through a tiny smooth fast unroll.

### R23-03 — High scientific gap: the named alternating ePC surrogate does not update base weights

Sources: `epc_train.py:1–9`, `EPCTrainer`, `train.Trainer`, pilot estimator setup; guide p. 6 and plan 9 R1-22. The installed ePC path extracts settled site errors as an estimator of the write gradient, then backpropagates locally through controller/reader. Both optimizers receive only `theta = {reader, controller}`. There is no alternating base phase, no trainable base mask, and no local block weight update. The base is frozen throughout these pilots.

This is a useful **cap-gradient-estimator comparison over a frozen base**, but cannot establish that local ePC *base weight learning* improves editability. Ordinary-text fidelity/base co-training terms and the paired BP base-update schedule remain work to do. Exact BP of the current cap-only prefix loss is real; calling it exact differentiation through adaptation would be incorrect.

During this audit the orchestrator landed **SD-24 / DEC-036 (`67700f7`)** and launched a corrected ePC pilot. `surrogate_check_fixed.json` reports one-iteration site-gradient cosine approximately 1, with magnitude ratio approximately .1; at 8 iterations its mean ratio is approximately .554. That repair addresses the error-energy implementation. It does not supply the absent base phase or fast unroll, nor does aligned direction imply matched update magnitude. The pre-SD-24 negative pilot must remain separately identified; this review draws no conclusion from the active corrected run.

**Owner change:** name and preserve current pilot conditions accurately; implement the matched alternating cap/base phases with identical examples, masks, losses and schedules. Rebuild observations/keys after encoder/base changes. **Checkpoint:** hash every parameter group before/after each phase, assert the declared leaf-change mask, and compare BP/ePC base updates on the same frozen-memory fixture. Fidelity and held-out editability gates then apply to the resulting trained base.

### R23-04 — High: a rejected revision still supersedes the valid old record

Sources: `adapt.py:64–77`, `:116–143`; guide p. 4 rollback requirement. `adapt_record` adds/supersedes the record before optimization. On rejection it keeps the new initial code but does not restore the old active record or remove the new one.

A revision with `lr=NaN` is rejected with `non_finite_code`, yet persistent state changes: **old inactive, new active**. Unrelated code and reusable parameters stay unchanged. An ordinary no-improvement update likewise leaves the inserted record. The guide permits declared fast-state changes, but the current “rollback” is only a code-step rollback, not rollback of the rejected edit. The caller reports rejection while later predictions can use the replacement.

**Owner change:** establish a transactional acceptance boundary around code, insertion and supersession; restore the previous valid state on nonfinite/error rejection, or explicitly distinguish “record accepted at initial code, code step rejected” from a rejected edit. Set and disclose the intended code-norm bound (current default is `None`). **Checkpoint:** compare full state hashes/active IDs on rejected new records, revisions, nonfinite steps, exceptions and capacity failures; accepted revision preserves unrelated keys/codes and retires exactly one old record. Two small accepted support updates in the positive controls do preserve unrelated arrays and frozen weights.

### R23-05 — High: independent queries can inherit another query's selection

Sources: `learner.py:117–129`, `last_logits_batch`; pilot `:148`; `data/decode.py` and `harness/runs.py`. `selection_for` treats any cached prefix as the beginning of the same query. The pilot resets once per episode, and the shared decode/run paths have no explicit per-query reset call.

After query `[5,6]`, an independent query `[5,6,7]` inherits a selection with `prompt_len=2`; after reset it correctly selects with `prompt_len=3`. The controlled logits differ by **0.00096428394**. This is an order dependence in query interpretation, distinct from holding the selected fact across answer tokens *within* one query. Caches also accumulate prompt forward results until reset.

**Owner change:** supply a query identity/begin-query boundary in the adapter and reset exactly there, including batch decoding and every evaluation role. Do not reset on each generated token. **Checkpoint:** independent queries where one prefixes another are order-invariant; later answer tokens still hold the original query's record/null decision; cache lifetime is bounded to the query.

### R23-06 — High: snapshot identity omits behavior-changing configuration

Sources: `learner.py:188–207`. `export_state` omits `single_site`; `import_state` checks only reusable weight hash and ignores the serialized configuration. Importing a three-site snapshot into the same-parameter single-site learner succeeds, produces the **same state hash**, and changes controlled logits by **0.08882046**. A different null threshold is also accepted, although it changes the re-exported state hash.

**Owner change:** bind all semantic read/update settings, base identity and encoder identity to the checkpoint; validate compatible settings on import. Explicitly declare which runtime/cost-only settings may differ. `base_checksum()` returns an initialization-time cached encoder hash; use an actual before/after parameter hash or recomputed base checksum for frozen-base verification. **Checkpoint:** same snapshot/config reproduces predictions; changed single-site/null/read settings are refused or require an explicit versioned conversion; deliberate base mutation is detected.

### R23-07 — High: the claimed total persistent-byte ceiling is not enforced

Sources: `memory.py:20–60`, `RecordStore.export/from_state`, `learner.py:79–85`, `memory_bytes`; guide p. 4. The store counts keys/codes/tokens plus a nominal 128 bytes per record, reports zero index bytes, and excludes reader/controller weights. Python metadata strings and `_by_id` are unbounded; unlike v0, these are not packed 128-byte records.

Two counterexamples:

- An empty tiny cap with **7,356 reusable-weight bytes** accepts a **one-byte** ceiling and reports zero occupied bytes.
- A record with a 10,000-character ID fits a declared **256-byte** store ceiling and reports **192 bytes**, while its arrays plus serialized metadata alone require at least **20,154 bytes**. This lower bound excludes Python object overhead.

The default 13,130,756 weight bytes must be deducted from a 64-MiB total allowance before capacity is allocated to records. Merely reporting a parameter count does not enforce the 5-million maximum for arbitrary configurations. Optimizer state, replay and temporary query caches need separate reporting; caches should also have a bounded lifecycle.

**Owner change:** adopt a precise packed/serialized accounting contract, count real metadata/index/source/weight payloads, enforce total capacity and the parameter ceiling, validate imported state capacity, and report working/optimizer memory separately. **Checkpoint:** measured packed size agrees with the report, oversized metadata and oversized models fail, imported over-budget state fails, and the matched-total-memory comparator uses the same convention.

### R23-08 — High for compute comparisons: returned costs omit work and BP bypasses the ledger

Sources: `learner._select/predict`; `train.prefix_loss`, `episode_grads`; `adapt.losses_and_grad`; guide pp. 2, 4, 6. On the first empty-cap query, one actual full forward executes, but the returned cost has **zero full forwards and zero tokens** because the selection pass precedes the returned accumulator. A real base's global ledger can still charge that pass, so this is a returned-record/ledger discrepancy, not evidence that it vanished from every log.

BP outer losses call `g.forward_jit` and JAX differentiation directly, outside the base's ledger wrappers. The CPU counter records zero base-API calls while those actual forward/backward computations occur. ePC's estimator explicitly enters ledger contexts. Therefore the current ledger cannot provide a matched BP/ePC training-cost comparison; pilot wall time is a separate available measurement. Adaptation manually increments reverse/full counts but does not propagate each adjoint's elapsed time/token cost into the returned extension. `reader_flops` and `rebuild_seconds` have no populated path here.

**Owner change:** reconcile returned costs with ledger phase deltas, instrument synchronized BP outer computation, and include selection, observations, corrections, adjoints, teacher passes, rebuilds and warm-up under a declared convention. **Checkpoint:** independently counted calls match returned records and ledger deltas for empty/non-null first queries, continuations, support adaptation and one BP/ePC outer batch. Do not infer relative speed from the uninstrumented ledger totals.

### R23-09 — Medium: optional loss configuration differs between trainers

`episode_grads_epc` never implements `w_code_norm`, while BP does. With every other coefficient zero and no queries, the same nonzero-code fixture yields BP code loss **1.07653749**, gradient norm **8.858816**, versus ePC **zero/zero**. The default coefficient is zero, so this does not explain the current default pilots. It breaks the stated “only the estimator differs” contract if enabled.

**Owner change/checkpoint:** implement the identical exact code penalty in ePC or reject a nonzero coefficient. Test nondefault loss settings and fail explicitly on unsupported combinations. Separately, support adaptation reports a token-mean loss but sums the code gradient; declare that sum objective or normalize the gradient if the intended learning-rate screen is per-token comparable.

### R23-10 — Medium: training and retrieval geometry differ beyond the declared top-k restriction

`reader.query_embedding` and `record_key` return unnormalized MLP outputs. `RecordStore.retrieve` chooses top-k by Euclidean distance; training `_selection` and inference applicability score dot products. Without equal key norms these rankings need not agree: for query `(1,0)`, keys `(10,0)` and `(1,0)`, dot product prefers the former, distance the latter. This is an algebraic counterexample, not a measurement of the active pilot's embeddings.

The guide asks for normalized queries, and the loss table declares a top-k/hard-null approximation, but neither explains this norm-dependent rank difference. **Owner checkpoint:** decide and document a common metric/normalization; measure recall of training-relevant records under deployed top-k; retain the full-record retrieval gradient test. Also measure how the aggregate write projection interacts with non-null mass: when already saturated, rescaling after gating can cancel a positive scalar gate, so preservation cannot be assumed to improve smoothly with that mass.

## Recommended continuation and division of work

1. **CPU core repair lane, orchestrator-owned:** R23-01, -04 through -09; add focused counterexample tests and a written response. R23-05 and -06 should land together because query state and snapshot semantics interact. Memory/accounting can proceed independently until integration.
2. **CPU design/reference lane:** specify the support-answer value path and fixed fast unroll (R23-02), then numerical checks. Decide the common selection geometry (R23-10). Keep zero-step/stopped-delta pilots as named controls rather than replacing their history.
3. **GPU owner:** preserve active corrected-SD-24 outputs as exploratory evidence. After objective/phase semantics are fixed, run the bounded paired pilot and genuine support-answer-swap/revision controls. More optimizer sweeps alone cannot repair a missing input path or loss denominator.
4. **Data lane:** use the new development corpus/exclusions; finish canonical entity review and a new synthetic final namespace before sealing. Teacher prefix diagnostics are optional for installed on-the-fly preservation KL.
5. **Later gate:** implement the matched BP/ePC base-update phases before claims about base co-training; hold Stage 3 settling and confirmatory freeze until a functioning, audited feedforward cap and valid comparative objectives exist.

The observed defects are not evidence against predictive coding as a method. They limit what the current named experiments test. SD-24 is a separate, already owner-handled energy correction; no source change or GPU restart was made by this audit.

## Reproduction

Use distinct new output paths on reruns; both scripts refuse overwrites:

```bash
env JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /home/derp/cap/venv/bin/python scripts/r1_23_audit.py --output logs/r1_round2/r1_23_controls_rerun.json
env JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /home/derp/cap/venv/bin/python scripts/r1_23_boundaries.py logs/r1_round2/r1_23_boundaries_rerun.json
```

The positive boundary control uses explicit query resets and two accepted three-step support updates at learning rate .001. The rejection/control script also records an ordinary nonaccepted update; that single small-step rejection is not classified as a gradient-sign defect. Supplemental fixed-fixture results are in `r1_round2/r1_23_support_steps.json`. Source hash checks report whether installed revision files changed during the controls.
