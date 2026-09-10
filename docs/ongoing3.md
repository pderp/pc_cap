# Ongoing work, round 3 (after D1 inputs): lanes for the other agent

Written 2026-09-10 by the orchestrating session after [updated_plan3.md](updated_plan3.md).
Rules from [ongoing.md](ongoing.md) §1–§3 and the commit policy (no commits, merges or pushes
by agents; leave changes uncommitted; record in `docs/tasks/<ID>.md`) apply unchanged. Task
specs referenced below live in [ongoing2.md](ongoing2.md) unless restated here. Claim a task by
editing your own row in `manifests/tasks.json`. State at writing: 33 tasks done
(`docs/tasks/STATUS.md`), `logs/interim_report1.md` summarizes everything so far.

## 1. Orchestrator lane (do not touch)

Progress 2026-09-10: HARN-C2, HARN-BATCH, DATA-03, DATA-08, S3-02, S2-06, S2-07 (D1 memo: `docs/D1_decision.md`) done; S3-04 partial (needs baselines, Lane F). Original order: **HARN-C2** (C2/CR/C0 through `pccap run`: probe binding in `harness/stage_s0.py` →
a general `harness/runs.py`) → **DATA-03** (MODULAR-CONTROL fixture + PC-1; the orchestrator
takes it because it needs the cap internals) → **DATA-08** (challenge sets) → **S3-01**
(control suite, development matrix) → **S2-06** (throughput; cap arms first, baselines added when
Lane F lands) → **S2-07** (D1 memo) → **S3-02/03/04**.

Owned paths this round (in addition to those in ongoing.md §4 and ongoing2.md §1):
`src/pccap/harness/runs.py`, `src/pccap/harness/stage_s3.py`, `src/pccap/fixtures/modular_control.py`,
`tests/fixtures/test_modular_control.py`, `tests/controls/test_pc1_planted.py`,
`manifests/fixtures/`, `src/pccap/data/challenges.py`, `tests/data/test_challenges.py`,
`manifests/dev/challenges*.json`, `results/S3/`, `docs/D1_decision.md`.

## 2. Lanes for the other agent (independent of the orchestrator lane and of each other)

### Lane F — BASELINES: `S2-03 → S2-04` (highest value; D1 waits on it)

Spec: ongoing2.md Lane F. Additional integration requirements so the harness can drive B1/B3
like a cap arm:

- Provide `pccap.baselines.lora.LoRALearner(base: BPBase, rank=8, lr=1e-4, steps=10, seed=0)` with
  `update_item(item: EditItem) -> ItemOutcome` (10 Adam steps, teacher-forced over
  `answer_ids`; `ItemOutcome.code` = `accepted`, `rounds_used` = steps, `cost` = a `CostRecord`
  with `full_forwards`/`reverses` = steps and `tokens`), `predict(ids) -> logits [T, V]`
  (LoRA-merged forward, charged as `query`), `export_state()/import_state()` (`LearnerState`;
  arrays = A/B per layer + Adam moments; scalars = steps, lr, rank), `state_hash()`,
  `memory_bytes() -> MemoryReport` (A/B + optimizer state bytes; `ceiling_bytes` = the same
  `B_cap` for reporting, `allocated_bytes` may exceed it — B1 is not byte-bounded, report the
  actual total), `base_checksum()`.
- Implement the LoRA forward by adding `ΔW_q = B_q A_q`, `ΔW_v = B_v A_v` to the Q and V column
  slices of each block's `c_attn.w` inside a jitted copy of `gpt2_jax.forward`-style code (do not
  modify `gpt2_jax.py`; write `baselines/lora_forward.py`). Base weights stay immutable arrays;
  the checksum must be unchanged after training.
- `pccap.baselines.b0.B0(base)` = frozen model with the same `predict`/`update_item` (no-op,
  code `accepted`, zero cost beyond evaluation) interface.
- Verify: `pytest tests/baselines/test_lora.py -m gpu` (trainable tensors exactly A/B for Q and V;
  K slice gradient zero; base checksum unchanged; a 10-step edit on an s0-sample item reduces
  teacher-forced NLL and — report, do not assert — changes the greedy answer).
- S2-04 replay B3 (ongoing2.md): `ReplayLearner(lora_learner, seed, ceiling_items_fraction=0.05,
  ceiling_bytes=B_cap)` with reservoir sampling and one replay item per new item per step;
  snapshot includes the buffer (token ids only) and optimizer state; `tests/baselines/test_replay.py`.
- Cost: 4 h + 3 h; GPU short tests only.

### Lane D — GRACE reference: `S2-05a → S2-05b`

Spec: ongoing.md Lane D. You already have a CPU torch environment
(`assets/envs/ref-torch-cpu/`); create a separate `assets/envs/grace/` only if GRACE's pins
conflict. Outputs: `docs/baselines/grace_reference.md` (algorithm summary, eviction adaptation
design per SD-8), `results/S2/grace_reference_smoke.txt`, `manifests/dev/grace_parity_cases.json`
(10 single-token + 10 multi-token cases chosen from `manifests/dev/zsre_dev.json` items, ids
recorded), `assets/reference/grace/` (reference edited outputs and memory contents, hashed).
No adapter code yet (S2-05 proper is the orchestrator's after PC-10 inputs exist).

### Lane H — DATA-02a sealed-confirmation loader

Spec: ongoing2.md Lane H (`src/pccap/data/confirm.py`, `tests/data/test_confirm_seal.py`,
`scripts/seal_confirm.py`, `manifests/confirm/README.md`). The confirmation source pools now
exist at `assets/data/prepared/editing/{zsre,counterfact}_eligible.jsonl` (hashes in
`manifests/dev/pools.json`); the realization/order sampling itself (DATA-02) stays with the
orchestrator after DATA-08.

### Lane G′ — GRAM-01 generator (pure NumPy)

Spec: ongoing2.md Lane G, GRAM-01 only (the six-layer training GRAM-02 and DATA-06/07 follow
under the same lane once GRAM-01 is verified; GPU training waits for the PA-2 clock,
2026-09-11 23:59 ET, unless T1 answers earlier). Owned: `src/pccap/fixtures/grammar_generator.py`,
`manifests/grammar/`, `tests/fixtures/test_grammar_generator.py`.

### Lane E — withdrawn (2026-09-10)

REG-00/01/02/03 are now on the orchestrator lane (DEC-014: PA-1 bound raised to 120 GPU-h). Do not claim.

## 3. Interfaces (all in the working tree; see interim_report1.md §6 for paths)

`pccap.contracts` (EditItem, ItemOutcome, CostRecord, MemoryReport, LearnerState via
`pccap.harness.snapshot`), `pccap.bases.gpt2_jax` (functional GPT-2; `load_params_numpy`,
`block`, `embed`, `head`, `bucket_len`, `pad_ids`), `pccap.bases.bp.BPBase`,
`pccap.data.tokenize.GPT2Tokenizer/tokenize_pair`, `pccap.data.decode.greedy_decode/
score_generation/teacher_forced_nll`, `pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`,
`pccap.harness.stage_s0.load_items` (EditItems from the S0 sample) and
`pccap.harness.stage_s2.load_dev_items(ds, n)` (EditItems + unrelated prompts from the dev pools).
