# Ongoing work (the single current log; older rounds are archived under `docs/archive/`)

Written 2026-09-10 (evening) by the orchestrating session, in response to `docs/derp_review1.md`
R1 ("consolidate ongoing logs"). Everything an agent needs is restated here; the archived files are
history only. State: 48 tasks done, REG-02 (ePC regeneration) running on the GPU for ≈ 9 more
hours; freeze decision pending with the lead (`docs/lead_queue.md` T-CP-E).

## 1. Ground rules (unchanged; DEC-001…005 and the commit policy)

1. **All GPU code is JAX** through `/home/derp/cap/venv` (Python 3.12, `jax 0.11.1`, `fabricpc 0.5.2`,
   `optax`); no PyTorch in the project environment. Predictive-coding functionality is built on
   FabricPC plus infrastructure in `pc_cap` (`docs/epc_energy.md`).
2. `llm-by-neural-predictive-coding` (sibling, commit `298fc719…`) and `FabricPC` are **read-only**
   references: no runtime import, no copied code; re-implemented formulas carry
   `# reproduces hdpc/<file>:<lines>` headers.
3. **Only code, logs and documentation go into `pc_cap/`**; datasets, weights, checkpoints, clones,
   caches and auxiliary environments live under `/home/derp/cap/assets/`.
4. **No `git add`/commit/merge/push by any agent; leave changes uncommitted; the lead commits.**
5. **Task protocol:** claim by `python -m pccap.harness.status --set <ID> status=in_progress agent=<name>`
   (your own row only); record the task in `docs/tasks/<ID>.md` (format: status / agent / inputs /
   outputs / verify command / verify output / done-when check / cost / deviations / unresolved /
   questions); charge GPU time with `pccap.harness.ledger.append_task_cost`. Never regenerate
   `docs/tasks/STATUS.md` by hand.
6. **GPU:** any CUDA use > 60 s takes the lease `results/.gpu_lease` via
   `pccap.harness.lease.gpu_lease(task, stage, projected_seconds)`; short `-m gpu` tests need no
   lease. REG-02 holds the lease in ≤ 90-minute chunks; touching `results/REG/reg02.pause` makes
   it wait between chunks (remove it afterwards). While REG-02 runs the device has ≈ 2.5 GiB free:
   run GPU tests in a pause window, not concurrently.
7. **Placeholder modules named under "Owned" are yours to replace** (the one-line ENV-03 stubs);
   any *other* existing file needs a `docs/tasks/<ID>-edit-request.md` first — the lead answers.
8. Spec defects/decisions: append to `docs/spec_defects.md` (SD-n) or `docs/decisions.md` (DEC-n)
   only through the orchestrator; never change thresholds, endpoints, arms or budgets (the PDF
   `docs/pc_cap_month_plan_readable.pdf` is the contract).
9. Tests: `make test-fast` (CPU), `make test-gpu` (short GPU), `make lint`; markers `gpu`, `slow`,
   `lease`. `tests/test_package_layout.py` enforces the confirm-manifest firewall: only
   `pccap/data/confirm.py` may contain the string `manifests/confirm`.

## 1b. Interim report 2 (Codex) — accepted; repairs applied (see `logs/review_interim_report2.md`)

The integration findings R2-01…R2-08 are repaired in the orchestrator's paths and covered by
`tests/harness/test_confirm_cli.py`; the freeze waits for the gate in `docs/updated_plan4.md` §2
(DEC-019); `docs/updated_plan5.md` adds the REG-02 evidence, the S6 closure and the review-2 items. Consequences for the lanes below: Lane D resumes now (permission done); Lane G′ must
declare `bank_blocks`/`d` on its base (R2-09); Lane R covers the lock's editable line; new Lane V.

## 2. Orchestrator lane (do not touch)

Running: **REG-02** (`results/REG/epc-50m.log`; checkpoints `assets/models/epc/epc-50m/checkpoints/`)
with an automatic chain afterwards (`results/REG/chain_after_reg02.sh`): REG-03 preflight → S1-01
(P1) → ePC rows of P2/P3/P5/P6 → S1 report. Then: S5 eligibility/arm definition, S2-05 GRACE
adapter + PC-10 (after Lane D delivers), S3-01/S3-03 (after GRAM-02), S4-04 execution after the
lead's freeze, S4-05/S4-06 analysis, S7. Owned paths: `src/pccap/{distill,pc,harness,cap,analysis,
routers,transport,bases}/`, `tests/{distill,pc,harness,cap,controls,bases,analysis}/`, `results/`,
`manifests/{tasks,datasets,assets,cr_distribution}.json`, `manifests/{confirm,frozen*}`,
`docs/{decisions,spec_defects,lead_queue,D1_decision,D2_decision,epc_energy}.md`, `logs/`,
`assets/models/epc/`, `assets/data/raw/openwebtext/`, `README.md`, `CONTRIBUTING.md`.

## 3. Lanes for the other agent (independent of §2 and of each other; take in this order)

### Lane D — GRACE reference (S2-05a → S2-05b), in progress by codex

State: environment `assets/envs/grace` built (Python 3.10, torch 2.0.0+cpu, transformers 4.20.1);
runner `scripts/grace_reference_oracle.py`, tests `tests/reference/test_grace_reference.py`,
selection `manifests/dev/grace_parity_selection.json`, design `docs/baselines/grace_reference.md`.
**Unblocked (2026-09-10):** the lead approved the `setuptools==78.1.0` pin and the orchestrator applied
it (`results/grace_lane_d/setuptools_pin_install.txt`; `import wandb` now works in `assets/envs/grace`).
Resume with the commands in `docs/tasks/S2-05a.md` and finish: source-import check, the six
controls, the five-case smoke gate → `results/S2/grace_reference_smoke.txt`, then the twenty parity
cases (isolated and sequential) → `assets/reference/grace/` and `manifests/dev/grace_parity_cases.json`
(hashes of every artifact), completion records, and set your board rows (`--set S2-05a status=done`).
SD-8 note: the reference is unbounded; the byte-bounded eviction is the adapter's (orchestrator,
S2-05) — record both wordings as you did. Cost remaining: ≈ 2 h CPU.

### Lane H — DATA-02a sealed-confirmation loader

Owned: `src/pccap/data/confirm.py` (placeholder), `tests/data/test_confirm_seal.py`,
`scripts/seal_confirm.py`, `manifests/confirm/README.md`.
`pccap.data.confirm.load(manifest_path, frozen=ROOT/"manifests/frozen.json")` raises unless
`frozen.json` exists, validates it as `manifest_frozen` (`pccap.harness.schema`), and checks that
`frozen["dataset_ids"][<dataset>]` — a mapping `{file_name: sha256}` because DATA-02 wrote one file
per realization (`manifests/confirm/{zsre,counterfact}_r{0,1,2}.json`, hashes in
`manifests/confirm/SHA256SUMS`; layout `{name, mode:"confirm", dataset, realization, seed,
order_seeds, orders{seed: [item_id…]}, named_seeds, n_items, items[…]}`) — contains the SHA-256 of
the file being loaded; returns the manifest dict. `scripts/seal_confirm.py` (re)writes `SHA256SUMS`
and a metadata-only sidecar per file (`*.meta.json`: counts, answer-length strata, subject count;
no prompts/answers) — DATA-02 already wrote `SHA256SUMS` and `DATA-02.meta.json`; keep those
formats. The S4 runner (`pccap.harness.stage_s4`, orchestrator) already calls
`load(Path(cfg["manifest"]), frozen=…)` and reads `dataset`, `realization`, `orders`, `named_seeds`,
`items`. Verify: `pytest tests/data/test_confirm_seal.py tests/test_package_layout.py` (loading
without `frozen.json` raises; hash mismatch raises; sidecar has no prompt/answer text; firewall
holds — use `manifests/frozen.draft.json` copied to a temp dir as the fixture, never the real
`frozen.json`). Cost 2 h, CPU only.

### Lane G′ — grammar (GRAM-01 → GRAM-02 code → GRAM-02 training after PA-2 → DATA-06/07)

PA-2 clock: 2026-09-11 23:59 America/New_York (T1 unanswered → the replacement grammar is
authorized after that; the generator and model *code* may be written now).
- **GRAM-01** (owned: `src/pccap/fixtures/grammar_generator.py`, `tests/fixtures/test_grammar_generator.py`,
  `manifests/grammar/`): PDF E.1 LATENT-GRAMMAR — a seeded pure-NumPy generator, vocab 64, length 64,
  agreement/dependency families with a grammaticality checker, labelled mechanism strata, held-out
  combinations; `manifests/grammar/generator.json` (parameters, seeds, counts, SHA-256 of a
  1,000-sentence sample). Tests: determinism, checker agreement, family coverage. 6 h.
- **Interface (R2-09, required):** the grammar base declares `d = 128` and `bank_blocks = {1: 1, 2: 3, 3: 5}`
  (the cap and the credit code read `base.bank_blocks` when present; `make_learner` passes `d = base.d`);
  its `forward`/`forward_from`/`adjoint` return sites keyed by those blocks. Add a CPU control that runs
  the real `Cap` (`make_learner("C1", grammar_base, ledger)`) on the grammar base: forward_from equals a
  full forward with the same writes, adjoint shapes `[3, 128]`, byte accounting at d = 128.
- **GRAM-02 code** (owned: `src/pccap/fixtures/grammar_model.py`, `tests/fixtures/test_grammar_model.py`):
  pre-norm transformer d = 128, 4 heads, 6 blocks, vocab 64, length 64, following
  `pccap.bases.gpt2_jax` conventions (functional params dict; `embed`/`block`/`head`; bank sites at
  blocks 1, 3, 5) and the `Base` protocol of `pccap.contracts` so `pccap.cap.cap.Cap` runs on it
  (`forward(ids, writes, retain_sites, phase, last_only)`, `forward_from`, `adjoint`, `checksum`;
  model `tests/cap/mock_base.py` and `pccap.bases.bp.BPBase`). Training (≤ 30 GPU-min, optax, under
  `gpu_lease("GRAM-02", …)` in a REG-02 pause window — touch `results/REG/reg02.pause`, wait for the
  lease, remove it afterwards) writes `assets/models/grammar/grammar_base.npz` via
  `gpt2_jax.save_params_npz`-style code and its hash into `manifests/assets.json` under
  `assets.grammar_replacement` with `status: replacement`; label everything "replacement fixture,
  no continuity with R8/R9". 4 h + GPU.
- **DATA-06/07** (owned: `src/pccap/data/grammar_streams.py`, `src/pccap/fixtures/tracing.py`,
  `manifests/grammar/streams.json`): task streams (10,000 training items per the D1 scope) and
  causal-tracing pairs on the grammar. After GRAM-02.

### Lane V — independent review of the repaired confirmatory path (CPU, ≈ 2 h)

Re-run the two reproducers from `logs/interim_report2.md` §7 against the repaired tree (expect 150/150
paths and zero payload reads on denied access), read `tests/harness/test_confirm_cli.py` and
`pccap.data.selection`, and write `logs/review_repairs_r2.md` with any remaining gap (especially:
resume semantics, the per-run allowance, the S5 confirm path, and whether the synthetic study should
also drive a fake learner through `run_stream` from the CLI). New files only.

### Lane R — review response R2/R4 (environment setup; small, CPU only)

From `docs/derp_review1.md`: add `scripts/setup_venv.sh` that recreates the project venv from
`requirements.lock` on a fresh machine (Python 3.12; `pip install -r requirements.lock`; the CUDA 13
JAX plugin wheels are in the lock; print `pccap.determinism_report()` at the end) and a
"Recreating the environment" section in `docs/environment.md` (what the script does, the
`HF_HOME`/assets layout, how `make test-fast` verifies it). Do **not** run it against
`/home/derp/cap/venv`; verify with `python -m venv /home/derp/cap/assets/envs/venv-check` +
`pip install --dry-run -r requirements.lock` (or a real install there if disk/time allow) and record
the output in `docs/tasks/ENV-05.md` (new task id ENV-05; add your row with the status tool).
The lock contains a private editable line (`-e git+ssh://…pc_cap.git@e381c9e8…#egg=pccap`): the script
must install the package from the local checkout (`pip install -e .` from the working tree) and skip
that line, recording the revision it installed; never rewrite the lock. Owned: `scripts/setup_venv.sh`,
the new section of `docs/environment.md`, `docs/tasks/ENV-05.md`, `assets/envs/venv-check/`. 1 h.

## 4. Interfaces

`pccap.contracts` (Base, EditItem, ItemOutcome, CostRecord, MemoryReport, Metric/metric; `LearnerState`
in `pccap.harness.snapshot`); `pccap.bases.gpt2_jax` (functional GPT-2: `load_params_numpy`, `embed`,
`block`, `head`, `bucket_len`, `pad_ids`, `save_params_npz`/`load_params_npz`); `pccap.bases.bp.BPBase`,
`pccap.bases.epc.EPCBase`; `pccap.harness.arms.make_learner/router_for` (arm registry incl. B0/B1/B3);
`pccap.harness.runs.Evaluator/run_stream`; `pccap.harness.stage_s2.load_dev_items(ds, n)`;
`pccap.data.tokenize.GPT2Tokenizer/tokenize_pair`; `pccap.data.decode`; `pccap.harness.ledger.Ledger`;
`pccap.harness.lease.gpu_lease`. Reports: `pccap report --stage S0|S1|S2|S3`.

## 5. Coordination

- Questions for the orchestrator: append a dated line under "## Agent questions" in
  `docs/lead_queue.md`; the orchestrator reads it between REG-02 chunks.
- Questions for the lead (permissions on existing files, environment changes): a
  `docs/tasks/<ID>-edit-request.md` plus a line in `docs/lead_queue.md`.
- The board (`manifests/tasks.json`) is the source of truth for claims; the orchestrator mirrors
  records it finds without a board row (as done for S2-05a/b today).
