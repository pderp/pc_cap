# Ongoing work, round 3 (rewritten 2026-09-10 after DEC-014): lanes for the other agent

Written by the orchestrating session. Rules from [ongoing.md](ongoing.md) §1–§4 and
[ongoing2.md](ongoing2.md) §4 apply unchanged, plus the commit policy: **no `git add`, commit,
merge or push by any agent; leave every change uncommitted; the lead commits.** Record each task
in `docs/tasks/<ID>.md` (§4.3 format) and claim it by editing your own row in
`manifests/tasks.json` (`python -m pccap.harness.status --set <ID> status=in_progress agent=<name>`).
State at writing: 40 tasks done (`docs/tasks/STATUS.md`); `logs/interim_report1.md` summarizes
everything so far; the delta plan is [updated_plan3.md](updated_plan3.md); decisions DEC-000…014
in [decisions.md](decisions.md); spec defects SD-1…18 in [spec_defects.md](spec_defects.md).

**Placeholder modules are yours to replace.** Every module named under "Owned" below currently
holds a one-line ENV-03 placeholder (`"... placeholder created by ENV-03; implemented by the owning
task."`). Replacing that placeholder is the task; it needs no further permission. Any *other*
existing file stays untouched (raise a `docs/tasks/<ID>-edit-request.md` as Lane F did).

## 1. Orchestrator lane (do not touch)

**Now:** ePC checkpoint regeneration under DEC-014 (PA-1 bound raised to 120 GPU-h):
REG-00 (JAX re-implementation of the sibling's homotopy distillation on FabricPC; `pccap.distill`,
`pccap.pc.kd_energy`, `pccap.pc.weight_phase`) → REG-01 (100-step pilot; s/step, projection) →
REG-02 (9,766 steps in resumable chunks under the lease; **the GPU lease will be held for long
stretches; short `-m gpu` tests still run without the lease, CPU work is unaffected**) → REG-03
preflight → S1-01 and the ePC rows of S1. Between chunks: Lane F review and arm registration
(B0/B1/B3 in `pccap.harness.runs` and the `pccap run` CLI), S2-06 baseline throughput rows,
S3-04 completion, S3-05, DATA-02 (after Lane H), S3-06 D2 memo, S4-01 freeze.

**Lane F (S2-03/S2-04) is implemented by codex and awaits orchestrator review** — do not modify
`src/pccap/baselines/{lora,lora_forward,b0,replay}.py` or `tests/baselines/` further; questions
to the orchestrator go into `docs/tasks/S2-04-completed.md` as an appended dated note only.

Owned by the orchestrator this round (in addition to ongoing.md §4 and ongoing2.md §1):
`src/pccap/distill/`, `src/pccap/pc/`, `tests/distill/`, `tests/pc/`, `results/REG/`,
`src/pccap/harness/`, `src/pccap/cap/`, `src/pccap/analysis/`, `manifests/datasets.json`,
`manifests/tasks.json` rows of the orchestrator's tasks, `assets/models/epc/`,
`assets/data/raw/openwebtext/`, `docs/decisions.md`, `docs/spec_defects.md`, `logs/`.

## 2. Lanes for the other agent (independent of the orchestrator lane and of each other)

Take them in this order unless one is blocked; one lane at a time; each is CPU-only unless stated.

### Lane D — GRACE reference: `S2-05a → S2-05b` (highest value; PC-10 and B4 depend on it)

Plan §6.4, PDF Baselines B4, PA-6; spec in ongoing.md Lane D. Summary of what is required:

- **S2-05a** — reference environment and smoke. The GRACE clone is at
  `assets/third_party/GRACE` (read-only; hash in `manifests/assets.json`). Build a CPU torch
  environment for it: reuse `assets/envs/ref-torch-cpu/` (torch CPU, transformers; used by REF-01)
  if GRACE's pins are compatible, otherwise create `assets/envs/grace/` (record the resolver
  output and the pinned versions in the task record). Run GRACE's own GPT-2 editing smoke on
  ≤ 5 zsRE items from `manifests/dev/zsre_dev.json` (item ids recorded); write
  `results/S2/grace_reference_smoke.txt` (command, versions, per-item outputs) and
  `docs/baselines/grace_reference.md`: the algorithm as implemented in the clone (key = hidden
  state at the edited layer, codebook of (key, value, ε-radius) entries, deferral/expansion/split
  rules, the layer and ε defaults for GPT-2), and the **eviction adaptation design** required by
  SD-8 (GRACE has no byte ceiling; describe how B4 will be bounded to `B_cap` = the cap's ceiling
  with least-recently-used eviction, and which of GRACE's behaviours that changes).
- **S2-05b** — parity cases. From `manifests/dev/zsre_dev.json` choose 10 single-token-answer and
  10 multi-token-answer items (ids recorded; exclude any id in `manifests/dev/s0_sample.json`);
  run the reference GRACE editor on each in isolation and after the full sequence of 20; save
  the edited outputs (greedy continuation ≤ 32 tokens, teacher-forced answer NLL) and the
  codebook contents (keys, values, radii as `.npz`, hashes) to `assets/reference/grace/`;
  write `manifests/dev/grace_parity_cases.json` (ids, hashes of the reference files, the exact
  command and environment hash). No adapter code yet: S2-05 proper (the JAX adapter
  `src/pccap/baselines/grace_adapter.py` + PC-10) is the orchestrator's after these inputs exist.
- Owned: `assets/envs/grace/` (if needed), `assets/reference/grace/`, `docs/baselines/`,
  `results/S2/grace_reference_smoke.txt`, `manifests/dev/grace_parity_cases.json`,
  `docs/tasks/S2-05a.md`, `docs/tasks/S2-05b.md`.
- Verify: the smoke file lists ≥ 1 successful edit (post-edit greedy answer equals the target
  for at least one item) and the parity manifest validates (every referenced file exists, hashes
  match). Cost: 3 h + 3 h. GPU: none (CPU torch).

### Lane H — DATA-02a sealed-confirmation loader

Spec: ongoing2.md Lane H (restated): `src/pccap/data/confirm.py` with
`load(manifest_path, frozen=ROOT/"manifests/frozen.json")` that raises unless `frozen.json` exists,
validates as `manifest_frozen` (`pccap.harness.schema`) and its `dataset_ids[<dataset>]` equals the
SHA-256 of the manifest file; manifest = JSON `{name, mode: "confirm", dataset, realization, seed,
items: [EditItem-like dicts]}` listed in `manifests/confirm/SHA256SUMS`; `scripts/seal_confirm.py`
writes the sums file and a metadata-only sidecar (`*.meta.json`: counts, answer-length strata,
subject count; no prompts/answers); `tests/data/test_confirm_seal.py`; `manifests/confirm/README.md`.
This module is the only file under `pccap/` allowed to mention `manifests/confirm`
(`tests/test_package_layout.py` enforces it). The source pools it will later read are
`assets/data/prepared/editing/{zsre,counterfact}_eligible.jsonl` (hashes in
`manifests/dev/pools.json`); the realization/order sampling (DATA-02) stays with the orchestrator.
Owned: the four paths above + `docs/tasks/DATA-02a.md`. Cost: 2 h.

### Lane G′ — GRAM-01 grammar generator (pure NumPy), then GRAM-02 code (no GPU yet)

Spec: ongoing2.md Lane G. GRAM-01: `src/pccap/fixtures/grammar_generator.py` implementing the
plan §6.5 / PDF E.1 generator (vocab 64, length 64, agreement/dependency families, seeded,
deterministic; `manifests/grammar/` holds the generator parameters, seeds and counts, and a
SHA-256 of a 1,000-sentence sample); `tests/fixtures/test_grammar_generator.py` (determinism,
grammaticality checker agreement, family coverage). GRAM-02 *code* may be written now:
`src/pccap/fixtures/grammar_model.py` — pre-norm transformer d = 128, 4 heads, 6 blocks, vocab 64,
length 64, following `pccap.bases.gpt2_jax` conventions (functional params dict, `block`,
`embed`, `head`, bank sites at blocks 1, 3, 5) and the `Base` protocol of `pccap.contracts` so the
cap runs on it (`forward(ids, writes, retain_sites, phase, last_only)`, `forward_from`, `adjoint`,
`checksum`; copy the shape of `tests/cap/mock_base.py` / `pccap.bases.bp.BPBase`). The GPU
training itself (≤ 30 GPU-min under `pccap.harness.lease.gpu_lease("GRAM-02", ...)`) waits for
the PA-2 clock (2026-09-11 23:59 ET) **and** for a lease window the orchestrator will announce in
`docs/lead_queue.md` (REG-02 holds the lease in chunks). Label everything "replacement fixture,
no continuity with R8/R9". Owned: the two modules, `tests/fixtures/test_grammar_*.py`,
`manifests/grammar/`, `assets/models/grammar/`, `docs/tasks/GRAM-01.md`, `docs/tasks/GRAM-02.md`.
Cost: 6 h + 4 h.

### Lane F′ — optional, after the three above: B1 learning-rate screening inputs

Not a task-board item. If time remains: a CPU-only script `scripts/lora_lr_screen_inputs.py`
that, for the candidate learning rates {3e-5, 1e-4, 3e-4} (PDF Baselines), writes the exact
`LoRALearner` configuration dicts and the item ids of 30 zsRE development items
(`manifests/dev/zsre_dev.json`, excluding `s0_sample` ids) to `manifests/dev/lora_lr_screen.json`.
The GPU screening run is the orchestrator's (needs the lease).

## 3. Interfaces (all in the working tree; see interim_report1.md §6 for paths)

`pccap.contracts` (EditItem, ItemOutcome, CostRecord, MemoryReport, LearnerState via
`pccap.harness.snapshot`), `pccap.bases.gpt2_jax` (functional GPT-2; `load_params_numpy`,
`block`, `embed`, `head`, `bucket_len`, `pad_ids`, `save_params_npz`/`load_params_npz`),
`pccap.bases.bp.BPBase`, `pccap.data.tokenize.GPT2Tokenizer/tokenize_pair`,
`pccap.data.decode.greedy_decode/score_generation/teacher_forced_nll`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`,
`pccap.harness.stage_s0.load_items` (EditItems from the S0 sample) and
`pccap.harness.stage_s2.load_dev_items(ds, n)` (EditItems + unrelated prompts from the dev pools).
Test markers: `gpu` (short CUDA test, no lease), `lease` (harness only), `slow`.

## 4. Coordination

- The lease file `results/.gpu_lease` shows the holder; do not wait on it for CPU work.
- Do not edit `manifests/tasks.json` rows other than your own; never regenerate
  `docs/tasks/STATUS.md` by hand (the status tool does it).
- Questions for the orchestrator: append a dated line to `docs/lead_queue.md` under
  "## Agent questions" (create the heading if absent); the orchestrator reads it between chunks.
