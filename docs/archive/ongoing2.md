# Ongoing work, round 2 (after CP-C): parallel lanes for other agents

Written 2026-09-10 by the orchestrating session before starting the S1/S2 development work.
Read [ongoing.md](ongoing.md) first: its §1 (lead directives DEC-001…005), §2 (asset
hierarchy) and §3 (how to claim, worktrees, records, lease) apply unchanged. The plan
([updated_plan2.md](updated_plan2.md)) stays the task specification; the PDF text is at
`docs/pdf_text/plan.txt`. Nothing here changes a threshold, endpoint, arm or budget.

State at writing: S0 complete (CP-C, DEC-011; `results/S0/report.md`), 24 tasks done, board in
`docs/tasks/STATUS.md`. Test suites: `make test-fast` (CPU, 215 tests) and `make test-gpu`.

> **Commit policy (lead directive, 2026-09-10):** do **not** commit or push. Leave your changes uncommitted in your worktree (or in the main tree if you are the only agent there) and list the changed files in your task record. The lead commits when they choose; the orchestrator does not commit either.

## 1. What the orchestrator lane is doing now (do not touch these paths)

**DATA-01 → S2-01 → S2-02 → S1-02 / S1-03 / S1-06 (BP rows)**, in that order.

Owned by the orchestrator for this round, in addition to the paths listed in ongoing.md §4:
`src/pccap/data/streams.py`, `src/pccap/data/splits.py`, `src/pccap/cap/calibrate.py` (new),
`src/pccap/harness/stage_s1.py`, `src/pccap/harness/stage_s2.py`, `src/pccap/analysis/s1_*.py`
(new), `src/pccap/analysis/report.py`, `manifests/dev/{zsre,counterfact}_dev.json`,
`manifests/dev/s1.json`, `manifests/dev/s2*.json`, `results/S1/`, `results/S2/`,
`results/DATA/`, `data/prepared/`. The GPU lease will be held by DATA-01's teacher generations
for roughly an hour and then intermittently; other lanes below need the GPU only for short
tests or for one bounded run (GRAM-02) that queues on the lease.

## 2. Lanes open now (independent of the orchestrator lane and of each other)

Claim by setting your row in `manifests/tasks.json` to `in_progress` with your agent name,
then `git worktree add .worktrees/<ID> -b task/<ID> master`. Record in `docs/tasks/<ID>.md`; leave the changes uncommitted; the orchestrator reviews and applies them.

### Lane F — BASELINES (one agent): `S2-03 → S2-04`

**S2-03 — LoRA baselines B1 (and B0)** · plan §6.8 · PDF §8 "Baselines", S2 "Baselines".
- Owned: `src/pccap/baselines/{lora,b0,__init__}.py`, `tests/baselines/`.
- Build on `pccap.bases.gpt2_jax` (functional GPT-2; params are the nested dict from
  `load_params_numpy`) and `pccap.bases.bp.BPBase`. Own implementation (HF GPT-2 has the fused
  `c_attn` Conv1D `[d, 3d]`): rank-8 LoRA on the **Q and V column slices** of every block's
  `c_attn` (columns `0:d` and `2d:3d`), K untouched, all 12 layers; `optax.adam` lr 1e-4
  (screen {3e-5, 1e-4, 3e-4} on development later, S2-02-style, log every configuration);
  10 optimizer steps per complete edit, teacher-forced over the whole answer
  (`EditItem.prompt_ids` / `answer_ids` from `pccap.data.tokenize.tokenize_pair`); one epoch per
  synthetic task; the shared decoder is `pccap.data.decode.greedy_decode` with a `predict`
  closure over the LoRA-merged forward; optimizer state and A/B matrices counted in the memory
  report (`MemoryReport` in contracts); B0 = frozen model with evaluation cost recorded.
  Expose `LoRALearner` with `export_state()/import_state()` returning
  `pccap.harness.snapshot.LearnerState` (arrays = A/B + Adam moments, scalars = step counts)
  so the harness snapshot/rollback works unchanged, and a `predict(ids) -> logits` that charges
  the ledger (`Ledger.call`).
- Verify: `pytest tests/baselines/test_lora.py -m gpu`: trainable tensor list is exactly the
  LoRA A/B for Q and V; original weights unchanged (checksum); K-slice gradient is zero; a
  10-step edit on an s0-sample item reduces teacher-forced NLL.
- Cost: 4 h; GPU 15 min (short tests, no lease needed).

**S2-04 — Replay baseline B3** · plan §6.8 · after S2-03.
- Owned: `src/pccap/baselines/replay.py`, `tests/baselines/test_replay.py`.
- Reservoir sampling over seen edits with ceiling `min(5% of seen edits, B_cap bytes of stored
  items)` (`pccap.cap.memory.b_cap(768)`); one replay item per new item per step; rounding, RNG
  (`numpy.random.Generator`, state captured in `LearnerState.rng`) and item storage defined;
  buffer + optimizer state in the snapshot and reported as total state.
- Verify: `pytest tests/baselines/test_replay.py` (reservoir statistics; restore equality; byte
  ceiling). CPU only.

### Lane G — FIXTURES (one agent): `DATA-03 → GRAM-01 → GRAM-02 → DATA-06 → DATA-07`

**DATA-03 — MODULAR-CONTROL fixture** · plan §6.6 · PDF E.1 MODULAR-CONTROL, PC-1.
- Owned: `src/pccap/fixtures/modular_control.py`, `tests/fixtures/test_modular_control.py`,
  `tests/controls/test_pc1_planted.py`, `manifests/fixtures/modular_control.json`.
- Implement a fixture "base" satisfying the `Base` protocol exactly like
  `tests/cap/mock_base.py` (copy its structure: `forward`, `forward_from`, `adjoint` by
  `jax.grad` w.r.t. the `[3, d]` write array, `checksum`, ledger charging), width 32, three
  module groups at the three write depths, fixed masks routing each private latent through its
  designated path and shared latents through an explicit shared path, output coordinates
  partitioned so a permitted write at one site cannot directly overwrite other sites' outputs;
  per-bank allowed write subspace (`allowed_subspace[m]`, orthonormal `[d, r]`) supplied to
  **every** arm through `Transport.direction(..., allowed_subspace=...)`; oracle routes
  (`permitted_banks`) supplied only to CO via `RoundContext.permitted_banks`. ≥ 100 private,
  ≥ 100 shared, ≥ 100 mixed-cause items plus held-out combinations; no-sharing, useful-sharing
  and wrong-router variants; record masks, sites and `R*(m, j)`.
- The cap runs unchanged on the fixture: `Cap(fixture_base, CapConfig(arm=..., d=32, ...))`
  from `pccap.cap.cap`, `update_item` from `pccap.cap.learn` (pass `permitted_banks=` for CO,
  and a `Transport` whose `direction` projects — wrap `Transport` so the projection is applied
  per site; a small subclass in the fixture module is fine).
- Verify: `pytest tests/controls/test_pc1_planted.py tests/fixtures/test_modular_control.py`:
  the supplied router (CO) recovers ≥ 19/20 planted targets within the round budget with
  unrelated outputs unchanged within 1e-6; the full fixture oracle reaches ≥ 95% of planted
  deterministic targets; the wrong-router variant fails as designed. CPU only.
- Cost: 8 h.

**GRAM-01 / GRAM-02 / DATA-06 / DATA-07** — if Lane A (ongoing.md) has not claimed GRAM-01 by
the time DATA-03 is done, take the chain: GRAM-01 generator (plan §6.5, pure NumPy), GRAM-02
six-layer base trained in JAX/optax (`fixtures/grammar_model.py`: pre-norm transformer d = 128,
4 heads, vocab 64, length 64, block/hook conventions of `pccap.bases.gpt2_jax` with bank sites
at blocks 1, 3, 5 per `pccap.bases.hooks.bank_blocks(6)`; implement the `Base` protocol so the
cap runs on it; ≤ 30 GPU-min under `pccap.harness.lease.gpu_lease("GRAM-02", ...)`; weights
to `assets/models/grammar/grammar_base.npz` via `gpt2_jax.save_params_npz`-style code, hash in
`manifests/assets.json` under `assets.grammar_replacement` with `status: replacement`),
DATA-06 task streams, DATA-07 tracing pairs. All labelled "replacement fixture, no continuity
with R8/R9" (PA-2; the clock ends 2026-09-11 23:59 ET — the generator and model code may be
written before, the GPU training waits for the clock unless T1 answers earlier).

### Lane H — DATA (one agent): `DATA-02a` (DATA-04 has been taken by the orchestrator)

**DATA-02a — Sealed confirmation loader and seal test** (the code half of DATA-02; the data
half waits for DATA-01/DATA-08). Plan §4.5 rule 4, §6.6 DATA-02.
- Owned: `src/pccap/data/confirm.py`, `tests/data/test_confirm_seal.py`,
  `scripts/seal_confirm.py`, `manifests/confirm/README.md`.
- `pccap.data.confirm.load(manifest_path, frozen=ROOT/"manifests/frozen.json")` raises unless
  `frozen.json` exists, validates as `manifest_frozen` (`pccap.harness.schema`), and its
  `dataset_ids[<dataset>]` equals the SHA-256 of the manifest file; the manifest itself is a
  JSON `{name, mode: "confirm", dataset, realization, seed, items: [EditItem-like dicts with
  item_id, digest, prompt, answer, aliases, paraphrases, locality_prompts, subject, fact_id]}`
  and `manifests/confirm/SHA256SUMS` must list it. `scripts/seal_confirm.py` writes the sums file
  and a metadata-only sidecar (`*.meta.json`: counts, answer-length strata, subject count; no
  prompts/answers). This module is the **only** file under `pccap/` allowed to mention
  `manifests/confirm` (`tests/test_package_layout.py` enforces it).
- Verify: `pytest tests/data/test_confirm_seal.py`: loading without `frozen.json` raises; a
  hash mismatch raises; the sidecar contains no prompt or answer text; the layout firewall test
  still passes. CPU only.
- Cost: 2 h.

**DATA-04 — LM, probe and property sets** — listed in ongoing.md Lane A; **the orchestrator
needs it for S1-02/S1-03/S1-06**. If it is still `pending` in `manifests/tasks.json` when you
start, claim it (spec in ongoing.md Lane A). Inputs are all present (`assets/data/raw/wikitext103`
parquet, `assets/data/raw/ud_ewt/*.conllu`, GPT-2 `tokenizer.json`); write large token arrays
to `assets/data/prepared/lm/` and only manifests (document ids, seeds, counts, hashes) to
`manifests/dev/lm_sets.json`. If nobody has claimed it by the time S2-02 finishes, the
orchestrator takes it.

### Still open from ongoing.md (unchanged specs there)

REF-01 (HF oracle fixtures via a CPU torch env under `assets/envs/`; unblocks the pending
HF-parity rows of S0-04 and S0-09), S2-05a/S2-05b (GRACE reference environment and parity
cases, PA-6), REG-00 (JAX distillation driver for PA-1; the sibling's exact math is
summarized in `docs/epc_energy.md` "Production checkpoint regime" and DEC-006).

## 3. Interfaces these lanes rely on (all on `master` at e18caa4)

- `pccap.contracts`: `Base`, `Write`, `SiteId`, `EditItem`, `Budget`, `RoundContext`,
  `MemoryReport`, `Metric`/`metric`.
- `pccap.bases.gpt2_jax`: `load_params_numpy`, `block`, `embed`, `head`, `run_blocks`,
  `forward_jit`, `BANK_BLOCK`, `bucket_len`, `save_params_npz`/`load_params_npz`.
- `pccap.bases.hooks.bank_blocks(n_layer)`; `pccap.cap.cap.Cap/CapConfig`;
  `pccap.cap.learn.update_item/round_update`; `pccap.routers.make_router`;
  `pccap.transport.transport.Transport`; `pccap.harness.snapshot.LearnerState`;
  `pccap.harness.ledger.Ledger`; `pccap.harness.lease.gpu_lease`;
  `pccap.data.tokenize.GPT2Tokenizer/tokenize_pair`; `pccap.data.decode.greedy_decode/
  score_generation/teacher_forced_nll`; `pccap.metrics.*` (Lane B).
- A CPU mock of the `Base` contract to copy from: `tests/cap/mock_base.py`.

## 4. Coordination notes

- The GPU lease (`results/.gpu_lease`) serializes runs > 60 s; short tests may run without it.
- `manifests/tasks.json`: edit only your own rows. `docs/tasks/STATUS.md` is regenerated by the
  orchestrator.
- Contract changes go through `docs/tasks/<ID>.patch`, never direct edits to `contracts.py`.
- When a lane finishes, leave the worktree in place; the orchestrator merges with `--no-ff`
  after a reviewer pass for `review: yes` tasks and removes the worktree.
