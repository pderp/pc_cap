# Ongoing work (the single current log; previous versions are dated under `docs/archive/`)

Rewritten 2026-09-10 ≈ 19:45 EDT by the orchestrating session, after REG-02 completed and the S5
preparation ran. Rules §1 are unchanged from the archived version (`docs/archive/ongoing-2026-09-10-1400.md`)
and are restated in `CONTRIBUTING.md`: JAX only, sibling/FabricPC read-only, resources under `assets/`,
**no commits by agents**, task records in `docs/tasks/<ID>.md`, claim rows with the status tool, lease
for any GPU use > 60 s, placeholder modules are the lane's to replace, other existing files need an
edit request. Board: `docs/tasks/STATUS.md`.

## 1. State (2026-09-10 evening)

- **REG-02 done** (12.2 GPU-h, 9,766 steps); **REG-03 preflight valid**, checkpoint promoted; **S1-01: eligible**
  for matched-fidelity claims (mean KL 2.9e-5 on H); ePC rows of P2/P3/P5/P6 equal the BP rows to three
  decimals; **S5-01 done** (ePC calibration = BP calibration; SB/SE-A/SE-E smoke through the CLI).
  Narrative: `logs/reg02_report.md`.
- **Lane D done** (S2-05a/b, codex): GRACE CPU reference environment, oracle, 20 parity cases with 63
  hashed artifacts under `assets/reference/grace/`, `manifests/dev/grace_parity_cases.json`.
- **Lane V done** (codex): `logs/review_repairs_r2.md` — the R2 repairs hold on the main S4 path (150/150
  synthetic jobs through the real CLI, loader, stream and collectors); six further findings V-01…V-06
  (lease ordering, S5 frozen authority/allowance, archived-run discovery and checkpoint preservation,
  stage-ceiling enforcement, update-vs-total cost naming, provenance negative controls) — **repaired with tests**
  (`logs/review_repairs_r2_response.md`); Lane V2 re-checks them.
- **Lane G′ done** (orchestrator): grammar generator, CPU-trained replacement base (provisional until PA-2),
  streams, tracing pairs; the grammar now runs through the shared harness (S3-03 development matrix running on
  the CPU; SD-20: latent paraphrases, exact keys).
- **GPU:** the S5-prep + window-1 chain is finishing (re-profile with reconcilable costs, ≈ 30 min);
  after it the device is free. Short `-m gpu` tests need no lease.

## 2. Orchestrator lane (do not touch)

V-01…V-06 repairs with tests (CPU) → rerun Lane V's study driver → freeze gate (`updated_plan4.md` §2)
→ CP-E request to the lead → S4-02 allowance → S4-03/04. In parallel: S4 runner/evaluator generalization
for grammar streams (S3-03), P1 complete-answer initially-correct check (GPU short), arm registration of
B4 when Lane B4 delivers, S5-02 after the freeze. Owned paths as before (`src/pccap/{distill,pc,harness,
cap,analysis,routers,transport,bases,fixtures,data}/`, `results/`, `manifests/`, `docs/decisions.md`,
`docs/spec_defects.md`, `docs/lead_queue.md`, `logs/`).

## 3. Lanes for the other agent (independent of §2 and of each other; none needs the GPU chain)

### Lane B4 — S2-05: the JAX GRACE adapter with PC-10 parity (highest value; CPU, one GPU-short test)

Owned: `src/pccap/baselines/grace_adapter.py` (placeholder — yours), `tests/controls/test_pc10_parity.py`,
`docs/tasks/S2-05.md`, `docs/baselines/grace_adapter.md`. Spec: plan §6.8 S2-05; PDF Op. rule 11, PC-10,
SD-8, PA-6; your own reference (`docs/baselines/grace_reference.md`, `assets/reference/grace/`).
- `GraceLearner(base: BPBase, block=8, radius=1.0, value_steps=100, value_lr=1.0, seed=0, ceiling_bytes=None,
  eviction="none")` with the Lane F interface: `update_item(EditItem) -> ItemOutcome` (code `accepted`;
  `cost` = value-optimization forwards/reverses and tokens, charged through `base.ledger` in
  `ledger.call("learning", ...)` blocks), `predict(ids) -> logits [T, V]` (query phase, codebook lookup
  active), `export_state/import_state` (`LearnerState`: keys, values, radii, labels, use counts, RNG),
  `state_hash`, `memory_bytes` (`MemoryReport`; `ceiling_bytes = B_cap`), `base_checksum`. Optional but
  welcome: `last_logits_batch(seqs, phase)` (vmapped forward with the codebook lookup) — otherwise the
  orchestrator's adapter in `harness.arms` wraps `predict`.
- Forward: a functional copy of the GPT-2 block loop (use `pccap.bases.gpt2_jax.block/embed/head`; do not
  modify `gpt2_jax.py`) with the GRACE hook at the input of block 8's MLP (`h[8].mlp.c_fc`, your
  binding): the codebook key is the residual at the hook for the last position, Euclidean distance,
  radius-gated replacement of the activation by the stored value, radius expansion/split per the source
  (`coverage`), cold-init values, Adam at lr 1.0 for 100 steps on the answer NLL (the shared newline
  terminator convention of your reference).
- SD-8 adaptation: `eviction="use_count_then_age"` bounded by `ceiling_bytes` (lowest use count, then
  oldest); disabled (`"none"`) for parity; every intentional difference from the source listed in the doc.
- PC-10: `tests/controls/test_pc10_parity.py` (GPU short, no lease): on the 20 cases, edited greedy
  outputs and teacher-forced NLL equal the reference within fp32 tolerance (state the tolerance), and the
  codebook keys/values/radii match the reference NPZ within tolerance after the isolated edits and after
  the 20-edit sequence. If any case cannot match, report it as a parity failure with the cause — never
  tune to the reference. Cost 6 h; GPU 20 min (run after the chain in §1 finishes; the device is then free).

### Lane P4 — S1-04 P4 separability on the grammar base (CPU)

Owned: `src/pccap/analysis/s1_p4.py`, `tests/analysis/test_s1_p4.py`, `docs/tasks/S1-04.md`; output
`results/S1/P4_gram.json` and a row in `results/S1/coverage.json` via `pccap.analysis.s1_p6.update_coverage`.
Spec: plan §6.7 S1-04, PDF D.4. Inputs: `pccap.fixtures.grammar_model.GrammarBase(weights=WEIGHTS)` (CPU:
`JAX_PLATFORMS=cpu`), `pccap.fixtures.grammar_generator` (kinds private/shared_1/shared_2, eight contexts,
held-out switch combinations via `pccap.data.grammar_streams.{eval_items,heldout_items}`), residuals at
the six block outputs via `base.forward(ids, retain_sites=True)` (sites 1/3/5) — for the other layers add a
small functional helper in your module reusing `grammar_model.run_blocks`.
- Per mechanism (the three kinds; and per context for the private mechanism) and per layer: 8,192 centred
  residual vectors at the designated positions; top-r basis with r = 16 only if the spectrum supports it
  (report the captured variance and eigen gaps; otherwise the insufficient-rank case or a common lower
  rank, labelled); overlap matrix between mechanisms (`pccap.metrics.overlap.subspace_overlap`), resampling
  stability (two disjoint halves, overlap of their bases); private/private overlap across contexts, shared
  retention (the shared subspace measured in a task-flipped stream vs the base grammar), held-out
  compositional transfer (does the private/shared basis from base-grammar data capture the held-out
  combinations' variance). Natural-language domain PCA: `unsupported` (DATA-04, recorded as such).
- Tests on synthetic Gaussian data with planted subspaces (known overlaps). Cost 3 h.

### Lane S7-prep — reversal pairs and the S7-01/02 harness (CPU; GPU later on committed checkpoints)

Owned: `src/pccap/analysis/s7_01.py`, `manifests/dev/s7_pairs.json`, `tests/analysis/test_s7_01.py`,
`docs/tasks/S7-01.md` (partial: design + CPU controls). Spec: plan §6.13 S7-01/02, PDF S7.
- Pair inventory: 100 fixed pairs from development data, stratified *shared* (two zsRE items with the
  same subject and different relations, or CounterFact items sharing a subject), *private* (unrelated
  items), *near-neighbour* (`manifests/dev/challenges.json` near-neighbour pairs); ids, strata and seeds
  in the manifest, fixed before any result.
- Protocol functions: `reversal(learner_factory, state, item_i, item_j, Q)` clones the complete state
  (`export_state`/`import_state`), runs `U_j(U_i(s))` and `U_i(U_j(s))` with item-keyed randomness
  (the router's `rng_material` already keys on the item digest), returns `D_ij` = mean JS
  (`pccap.metrics.divergence.js`) over the fixed evaluation set Q, per-item accuracy changes, update
  counts, allocations, evictions; `damage_matrix(...)` = `I_ij` in both orders with strata.
- CPU controls with the mock base (`tests/cap/mock_base.py`) and a fake learner: cloning leaves the
  original untouched; commuting updates give D = 0; a planted non-commuting pair gives D > 0; strata
  bookkeeping. The GPU run on the S4 300-edit checkpoints is the orchestrator's later. Cost 4 h.

### Lane R — ENV-05 environment recreation script (CPU/network; unchanged spec)

`scripts/setup_venv.sh` from `requirements.lock` into a scratch venv under `assets/envs/venv-check/`
(skip the private editable line; install the package from the local checkout; record the revision),
a "Recreating the environment" section for `docs/environment.md` (as a proposed patch if you prefer not
to edit), `docs/tasks/ENV-05.md`. 1 h.

### Lane V2 — **ready now**: the V-01…V-06 repairs landed (2026-09-10 ≈ 20:20 EDT; `logs/review_repairs_r2_response.md`)

Rerun your study driver against the repaired tree from a fresh fixture root, extend it with the negative
controls you listed (changed code/checkpoint/tokenizer, missing substrate definitions, invalid order
index, conflicting CLI base/read, two experiment ids, a forced rerun with different state hashes), and
write `logs/review_repairs_r2b.md`. New files only.

## 4. Interfaces and coordination

As in the archived version §4–§5: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`,
`pccap.harness.arms.make_learner/router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`,
`pccap.data.tokenize`, `pccap.data.decode`, `pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`,
`pccap.fixtures.grammar_generator/grammar_model`, `pccap.data.grammar_streams`. Questions for the
orchestrator: a dated line under "## Agent questions" in `docs/lead_queue.md`; board rows: your own only
(the orchestrator mirrors completion records it finds, as done for S2-05a/b and DATA-02a).
