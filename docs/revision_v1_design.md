# Revision v1 — design note (Stage 1 interfaces; coding-agent guide §1)

Written 2026-09-13 17:20 EDT by the orchestrator before any Stage 1 code exists. Everything here is a proposal to be
implemented under `src/pccap/revision_v1/` after the v0 close-out (the v3 freeze still hashes the package until then).
v0 contracts (`pccap.contracts`) are adapted, never edited.

## Modules and ownership

| module | responsibility | owner |
| --- | --- | --- |
| `contracts.py` | `Observation`, `MemoryRecord`, `CapState`, `Episode`, `PredictResult`, `AdaptResult`, `OuterResult`; adapters from `pccap.contracts.EditItem` | O |
| `observations.py` | one unedited base pass per prefix; tapped features at blocks 3/7/11 (last position + masked prompt-span summary); causal masks; `encoder_version` | O |
| `memory.py` | bounded records; retrieval (top-k, deterministic ties); explicit revisions (supersede, never overwrite); serialization; index rebuild on key-version change; byte accounting | O |
| `reader.py` | query encoder (per tap: last-position + span summary → 256 → MLP), key/value encoders, applicability with an explicit null, threshold calibration | O |
| `controller.py` | query + weighted value code → three 768-d writes jointly; × non-null mass; hard-null → exact zeros; aggregate bound Σ‖w_m‖/b_m ≤ A | O |
| `adapt.py` | support-only fast update of a record's fact code (1/3/5 steps; lr screen; accepted-step check; rollback on non-finite; norm bound) | O |
| `episodes.py` | episode generator (synthetic first, then development pools); splits/families/seeds explicit; labels only in containers | C |
| `evaluate.py` | paired streams (reuses `pccap.harness.runs.run_stream` through an adapter learner), phase costs incl. the extra unedited pass, traces | O |
| `audit.py` | data-separation and update-path audits | C |
| `train.py` (Stage 2) | differentiable reference; alternating BP surrogate | O |
| `epc_train.py` (Stage 2) | alternating ePC surrogate on the existing energy + query term | O |
| `pc_cap.py` (Stage 3) | latent energy and bounded state solver | O |

## Records (minimum fields)

- `Observation`: `ids` (int32 [T]), `mask` (bool [T]), `last` {tap: float32 [768]}, `span` {tap: float32 [768]} (masked mean over the prompt span), `base_hash`, `encoder_version`.
- `MemoryRecord`: `record_id` (immutable), `fact_id`, `revision_id`, `created_order`, `active`, `key` (float32 [256]), `code` (float32 [d_code], initialized from support text), `provenance` (support ids), `source_tokens` (optional, counted).
- `CapState`: `records`, `index_version`, `encoder_version`, `rng`, byte totals (keys, codes, metadata, tokens, index); snapshot = `pccap.harness.snapshot.LearnerState` via adapter (arrays + scalars) so the v0 harness can checkpoint it.
- `Episode`: `history` (support examples of 2–8 earlier facts), `support_new`, `queries_new` (≥ 2 unseen paraphrases), `queries_old`, `near_miss`, `unrelated`, `composition` (optional), `split_id`, `entity_ids`, `family_ids`, `seed`. Query labels live only in the episode's `labels` container, which `predict` never receives.

## API (guide p.3)

```
predict(prefix, state) -> logits, trace, cost        # read-only; no target argument exists
adapt(support, state, budget) -> new_state, trace, cost   # may change only declared fast state (record codes, new records)
outer_step(training_episode, params) -> params, metrics   # reusable weights; Stage 2 only
```

Trace: per tap the candidates, scores, null mass, chosen record, write norms; cost = `pccap.contracts.CostRecord` plus a
revision extension (`extra_pass_forwards`, `reader_flops`, `records_touched`, `rebuild_seconds`).

Harness adapter: `RevisionLearner` exposes the v0 learner surface (`update_item`, `predict`, `last_logits_batch`,
`export_state/import_state/state_hash/memory_bytes/base_checksum`, `decode_key_positions=False`) so `run_stream`,
the evaluator, the queue and the S7 machinery work unchanged; the reader/controller weights are frozen during evaluation
and hashed before/after (gate "frozen evaluation components").

## Capacity and cost

≤ 5 M trainable cap parameters; persistent-state ceiling 64 MiB counted in full (weights, keys, codes, metadata, tokens,
index); optimizer and replay reported separately; a matched-total-memory comparison or cost frontier against v0's
36.75 MiB. The unedited observation pass plus the corrected pass are both charged; a cached-observation variant is a
separate condition.

## Gates (tests under `tests/revision_v1/`)

1. no hidden target access: changing held-out labels leaves predictions and state hashes unchanged; `predict` has no
   target parameter (asserted by signature); support/query containers are distinct types;
2. frozen evaluation components: base and reusable weights hashed before/after a stream; only declared fast state changes;
3. memory: snapshot round-trip; key-version checks; deterministic ties; explicit supersession; ceiling enforcement;
4. causality and null: future tokens cannot alter earlier predictions; empty/rejected memory → writes exactly zero and
   logits equal the cap-off base within tolerance;
5. learning mathematics (Stage 2): finite-difference check of the tiny smooth adaptation reference; ePC block-gradient
   locality and stop-gradient boundaries;
6. resource accounting: phase counters reconcile with actual base/solver calls; warm-up separated; failed work included;
7. behavioural sanity: learn a planted fact, answer an unseen formulation, preserve a near-miss, revise the fact, retain an
   older unrelated correction.

## First development configuration (to be profiled on 10 edits before any stream)

query width 256; reader MLP 2 × 256; top-k = 4; controller 2 × 512 → 3 × 768; fact code d_code = 256; A = 0.3;
fast steps ∈ {1, 3, 5}; lr ∈ {1e-3, 1e-2}; ceiling 64 MiB; base frozen; reader/controller pre-trained on synthetic
episodes (Stage 2) then frozen for the first evaluation. Parameter count reported exactly at construction.

## As built (2026-09-13 evening; Stage 1–2 code under `src/pccap/revision_v1/`)

- `contracts.py` re-exports the installed episode containers (Codex R1-20) instead of defining a separate `Episode`;
  adds `Observation`, `MemoryRecord`, `RevisionCost`, `Predict/Adapt/OuterResult`, an `EditItem → SupportExample`
  adapter and the signature gate `assert_no_target_parameter`.
- `observations.py`: `ObservationEncoder.observe` (one write-free pass) and `observation_from_pass` so the read path
  reuses the same pass for the corrected partial forward (one full + one partial pass per position, as in v0).
- `memory.py`: `RecordStore` (immutable ids, supersession, deterministic ties, key-version refusal + `rebuild_keys`, full
  byte ceiling, `LearnerState` round-trip).
- `reader.py` / `controller.py`: JAX pytrees; siamese tap encoder (LN[last; span] per tap → 256), query/key/code heads,
  applicability softmax with a learned null logit; controller MLP 512×2 → 3×768, scaled by non-null mass, aggregate
  bound Σ‖w_m‖/b_m ≤ A with a safe norm (finite gradient at zero writes); 3.28 M parameters at the first configuration.
- `adapt.py`: support-only fast rule on the record code (base adjoint → controller VJP; accepted-step / rollback / norm
  bound). With untrained weights it barely moves the support loss (lr screen 1e-2…10): the fast rule's usefulness is a
  Stage 2 outcome, so the reference trainer runs with `fast_steps = 0` first.
- `learner.py`: `RevisionCap` behind the v0 harness surface. Selection (records + null) happens once per query from the
  prompt and is held for every answer position (cache keyed by the longest cached prompt that prefixes the query; reset
  on every update). Hard null returns the cap-off logits exactly. R1-16 variants: `cache_prompt_pass` (reuse the
  selection pass for the prompt-position read) and `single_site` (writes at site 3 only; partial pass from block 11).
- `train.py`: differentiable reference (featurize once; L1/L2/L3 as pure functions of θ through the base's jitted
  forward; optax); `epc_train.py`: the alternating ePC surrogate (settled site errors as write gradients; CE head for
  answers, KD head for preservation; θ through a controller/reader VJP). Loss table: `docs/revision_v1_losses.md`.
- `v0_stable.py`: `StableCap` (DEC-035 control).
- Gates: 1/3/4 (CPU tests), 2/3/4/6 on the real base (`scripts/r1_12_profile.py`), 5 (finite differences on a tiny
  CPU base; ePC/BP equivalence when write gradients coincide), X0-12 mechanics (`scripts/r1_21_overfit_check.py`);
  gate 7 waits for trained weights (`scripts/r1_21_pilot.py`).
