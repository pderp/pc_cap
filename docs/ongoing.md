# Ongoing work and parallelizable tasks

Written 2026-09-09 (D0) by the orchestrating session before starting execution of
[updated_plan2.md](updated_plan2.md). This file tells a second (or third) agent what it can
work on **right now** without touching anything the orchestrator lane is editing. It is kept
current: when a lane finishes or a dependency clears, this file and `manifests/tasks.json`
are updated. The plan (updated_plan2.md) stays the task specification; the PDF
(`docs/pc_cap_month_plan_readable.pdf`, text extract at `docs/pdf_text/plan.txt`) stays the
scientific contract. Nothing below changes a threshold, endpoint, arm, or budget.

## 1. Ground rules that differ from updated_plan2.md (lead directives, 2026-09-09)

These were given by the lead when execution started and override the corresponding lines of
the plan. They are logged in `docs/decisions.md` as DEC-001…DEC-005.

| # | Directive | Consequence |
| --- | --- | --- |
| DEC-001 | **All GPU code uses JAX**, through the venv at `/home/derp/cap/venv` (Python 3.12.14, `jax 0.11.1` + CUDA 13 plugin, `fabricpc 0.5.2`, `optax`, `orbax-checkpoint`, `tokenizers`, `huggingface_hub`). No PyTorch in the project environment. | ENV-01 is "verify and complete the existing venv", not "build a 3.11 + torch env". GPT-2 small is re-implemented in JAX (`pccap.bases.bp`) and loaded from the pinned HF safetensors. LoRA/replay baselines are written in JAX/optax. |
| DEC-002 | **Predictive-coding functionality is built on FabricPC** (`/home/derp/cap/FabricPC`, read-only, MIT) plus infrastructure written directly in `pc_cap`. | `pccap.bases.epc` implements the ePC energy/relaxation of PDF D.6/F.6 in JAX, using FabricPC where its abstractions fit and our own code where they do not; which parts are which is recorded in `docs/epc_energy.md`. |
| DEC-003 | `llm-by-neural-predictive-coding` (the PyTorch sibling, commit `298fc719…`) and `FabricPC` are **read-only reference material**. Nothing is imported from the sibling at runtime (its `torch` dependency is absent by DEC-001). | ENV-04 becomes a *reference recorder*: it pins the sibling commit and dirty hash in `manifests/assets.json` and every re-implemented formula cites the sibling file/line it reproduces. The ePC checkpoint regeneration (REG-01/02) cannot run the sibling's `hdpc-distill`; it needs a JAX distillation driver (see Lane E). |
| DEC-004 | **Only code, logs and documentation go into `pc_cap/`.** Every other resource (datasets, model weights, checkpoints, third-party clones, HF cache, auxiliary environments) lives under `/home/derp/cap/assets/` in the hierarchy of §2. | Plan paths `data/raw/`, `data/models/`, `third_party/` are relocated to `assets/…`; `pc_cap/data/` holds only manifests and `SHA256SUMS` files. Small derived JSON/JSONL under `pc_cap/results/` and `pc_cap/data/prepared/` is allowed when it is a log or a manifest; anything ≥ 50 MB or binary goes to `assets/`. |
| DEC-005 | Working clone is `/home/derp/cap/pc_cap` (branch `master`). Task branches are `task/<ID>`; worktrees live at `pc_cap/.worktrees/<ID>` (gitignored) so they stay inside `pc_cap`. | Same protocol as plan §4.2 with the worktree path changed. |

Everything else in updated_plan2.md (task IDs, Done-when clauses, SD-1…SD-12, PA-1…PA-9,
ownership labels, record format §4.3, ledger, lease) stands.

## 2. Resource hierarchy under `/home/derp/cap/assets/`

```
assets/
  data/raw/<source>/…              DATA-00 downloads (gpt2 snapshot, zsre, counterfact, wikitext103, ud_ewt)
  data/prepared/…                  tokenized/prepared large artifacts (parquet, npy) if ≥ 50 MB
  models/gpt2/                     symlink or copy of the pinned GPT-2 safetensors snapshot
  models/epc/                      regenerated ePC checkpoint(s) (orbax) when REG runs
  models/grammar/                  GRAM-02 replacement grammar base
  third_party/GRACE/               git clone, pinned commit (never modified)
  envs/ref-torch-cpu/              optional CPU-only torch+transformers venv used ONLY to produce
                                   reference fixtures and to run GRACE's own tests (PA-6)
  reference/gpt2/                  reference logits / hidden states / greedy decodes produced by
                                   the CPU torch env, consumed by pc_cap tests as an oracle
  hf_cache/                        HF_HOME for snapshot_download
  runs/<stage>/…                   learner checkpoints and any large run outputs
```

`pc_cap/results/` keeps `metrics.json`, `cost.json`, `decisions.jsonl`, reports and ledgers
(small text). `pc_cap/data/raw/SHA256SUMS` and `pc_cap/manifests/*.json` record what is in
`assets/` by hash.

## 3. How a second agent works here

1. Environment: `source /home/derp/cap/venv/bin/activate` (or call `/home/derp/cap/venv/bin/python`).
   `pytest`, `ruff`, `safetensors`, `jsonschema`, `conllu`, `hypothesis` are installed there
   (ENV-01). Set `HF_HOME=/home/derp/cap/assets/hf_cache` when downloading.
2. Claim a task: set its row in `manifests/tasks.json` to `in_progress` with your agent name
   (edit that one row only; it is the only shared file two agents may both touch, and only
   their own rows). Create a worktree:
   `cd /home/derp/cap/pc_cap && git worktree add .worktrees/<ID> -b task/<ID> master`.
3. Edit only the owned paths listed for the task. Anything else → write a patch to
   `docs/tasks/<ID>.patch` and say so in the task record.
4. Run the Verify command; write `docs/tasks/<ID>.md` in the §4.3 format of updated_plan2.md;
   commit on your branch as `<ID>: <one line>`; do **not** merge to `master` (the
   orchestrator merges) and do not push.
5. GPU use > 60 s requires the lease file `results/.gpu_lease` (`pccap.harness.lease`,
   available after S0-03; until then use `flock results/.gpu_lease <cmd>` and write a JSON
   line with pid, task ID and projected seconds). The lanes below are chosen so that none of
   them needs the GPU for more than short tests while the orchestrator lane holds it.
6. Interface contracts: `src/pccap/contracts.py` (committed at ENV-03, within the first hours
   of D0). Until that commit lands, code against the signatures in §5 of this file, which are
   exactly what ENV-03 writes. Do not edit `contracts.py`; propose changes as a patch.

## 4. Lanes available now (no cross-dependencies with the orchestrator lane or each other)

The orchestrator lane (this session, INTEGRATOR+BASE) is doing, in order:
**ENV-01 → ENV-03 → ENV-04 → S0-03 → S0-04 (JAX GPT-2 BP base) → S0-05 → S0-06 (FabricPC ePC
base) → S0-08 → ENV-02.** It owns `pyproject.toml`, `Makefile`, `requirements.lock`,
`src/pccap/{__init__,contracts,vendor_hdpc,cli}.py`, `src/pccap/harness/`, `src/pccap/bases/`,
`src/pccap/transport/`, `tests/harness/`, `tests/bases/`, `tests/transport/`, `manifests/tasks.json`
(whole-file edits), `docs/tasks/STATUS.md`, `docs/{decisions,spec_defects,lead_queue,environment,epc_energy}.md`.
Do not edit those.

### Lane A — DATA (one agent). `DATA-00 → REF-01 → S0-01 → DATA-04 → GRAM-01`

**DATA-00 — Fetch and hash public assets** (plan §6.2, with DEC-004 paths).
- Owned: `assets/**`, `pc_cap/scripts/fetch_assets.py`, `pc_cap/src/pccap/data/fetch.py`,
  `pc_cap/manifests/datasets.json`, `pc_cap/data/raw/SHA256SUMS`, `pc_cap/tests/data/test_fetch.py`.
- Steps exactly as the plan's DATA-00 list 1–6 (GPT-2 snapshot revision
  `607a30d783dfa663caf39e06633721c8d4cfcd7e` via `huggingface_hub.snapshot_download` with
  `HF_HOME=assets/hf_cache`, then copy/symlink into `assets/models/gpt2/`; zsRE MEND eval+train
  and CounterFact from `rome.baulab.info`; WikiText-103-raw-v1 parquet from
  `Salesforce/wikitext` with the HF revision recorded; UD English EWT latest release tag;
  GRACE clone into `assets/third_party/GRACE` with HEAD commit and licence file recorded).
  Item 7 (OpenWebText) is deferred to REG. Failures → `unavailable` with HTTP status; no substitutes.
- Also record WikiText token counts with the GPT-2 tokenizer (`tokenizers` library, the
  `tokenizer.json` from the snapshot): unique documents and tokens per split. This feeds SD-3.
- Verify: `python -m pccap.data.fetch --verify` re-hashes everything against
  `pc_cap/data/raw/SHA256SUMS` (the module may simply import `scripts/fetch_assets.py`
  logic; keep it free of any import from `pccap.bases`/`pccap.harness`).
- Cost: ~1 h, ~2 GB disk, no GPU.

**REF-01 — Reference oracle fixtures from the HF PyTorch implementation** (new task; supports
S0-04(a,b), S0-09 PC-7 decode parity, and PC-10 under PA-6). Reason: with no torch in the
project env (DEC-001) the plan's "equal to HF `GPT2LMHeadModel`" assertions need a stored oracle.
- Owned: `assets/envs/ref-torch-cpu/`, `assets/reference/gpt2/`, `pc_cap/scripts/make_reference_fixtures.py`,
  `pc_cap/manifests/reference.json`.
- Steps: `uv venv --python 3.12 assets/envs/ref-torch-cpu`; install CPU-only torch (from
  `https://download.pytorch.org/whl/cpu`) and `transformers` (try `5.13.1`, else newest that
  installs; record). Load GPT-2 from the DATA-00 snapshot in **fp32**, `eval()`, `use_cache=False`,
  attention implementation `eager`. Produce, with `torch.use_deterministic_algorithms(True)`:
  1. `logits_256.npz`: 256 prompts = the first 256 `src` prompts of `zsre_mend_eval.json`
     (record the ids); per prompt: token ids, full logits `[T, 50257]` fp32, hidden states
     after blocks 3, 7, 11 (**pre-`ln_f`**: hook `transformer.h[11]` output, do not use
     `output_hidden_states[-1]` for the last one), and the post-`ln_f` last hidden state.
  2. `greedy_8.json`: for 8 of those prompts, `generate(do_sample=False, max_new_tokens=32,
     use_cache=False)` token ids, plus the same for `use_cache=True` (to document whether they agree).
  3. `lengths.npz`: logits for synthetic prompts of length 1, 2, 3, 5, 8, 16, 64, 128 (fixed
     random token ids from seed 0) — for S0-04(f).
  4. `ref_env.json`: torch/transformers versions, thread count, CPU model, and SHA-256 of
     every produced file.
- Verify: `python scripts/make_reference_fixtures.py --check` reloads and re-hashes.
- Cost: 1–2 h CPU. **No GPU.**

**S0-01 — Asset inventory and lead queue** (plan §6.2) — searches this host for the ePC
checkpoint (`4f0c23aa…`), grammar R8/R9, causal-fibres, comcrit, RelaLeap; notes whether the
Drive links in `docs/footnotes.md` resolve (do not download); writes `manifests/assets.json`
statuses. Owned: `manifests/assets.json` (the DATA/assets section; the orchestrator adds the
`sibling` section in ENV-04 — put yours under top-level key `"assets"` and leave `"sibling"` alone),
`docs/lead_queue.md` **append-only** (add the T1 absent list under a `## T1 (S0-01)` heading).
Verify: `python -m pccap.harness.schema validate manifests/assets.json` once S0-03 lands; until
then `python -c "import json;json.load(open('manifests/assets.json'))"`.

**DATA-04 — LM, probe and property sets** (plan §6.6; needs DATA-00 only). Owned:
`src/pccap/data/lm_sets.py`, `manifests/dev/lm_sets.json`, `assets/data/prepared/lm/`,
`tests/data/test_lm_sets.py`. Tokenize with `tokenizers` (GPT-2 `tokenizer.json`); H = 2×10⁶
tokens by document from train (seed 11); drift = whole validation (SD-3, log the shortfall);
P2 = 4,096 held-out positions from H's complement; P3 = 1,000 × 128-token sequences from the
complement; POS from UD-EWT with first-subtoken labelling; E.4 domains recorded `unsupported`.
Verify: `python -m pccap.data.lm_sets --audit`.

**GRAM-01 — Grammar generator per E.1** (plan §6.5; pure NumPy). Owned:
`src/pccap/fixtures/grammar_generator.py`, `manifests/grammar/`, `tests/fixtures/test_grammar_generator.py`.
Verify: `pytest tests/fixtures/test_grammar_generator.py`.

### Lane B — METRICS (one agent). `S0-07 → ANA-01 → S0-07b`

**S0-07 — Metric library with known-answer tests** (plan §6.3). Pure NumPy (float64) — no JAX
needed, no GPU. Owned: `src/pccap/metrics/{rank,participation,overlap,divergence,cl_matrix,order,editing,__init__}.py`,
`tests/known_answer/`. Every function returns a `Metric` (signature in §5) with operands.
Verify: `pytest tests/known_answer/`. Note `editing.normalize_answer` = NFKC → casefold →
whitespace collapse → strip; `exact_match_aliases` compares the normalized generated text
before the terminator against normalized aliases (SD-9). Cost 4 h.

**ANA-01 — Frozen analysis code on synthetic tables** (from plan S4-01/S4-06, brought forward
because it has no dependency on runs). Owned: `src/pccap/analysis/{paired,bootstrap,__init__}.py`,
`tests/analysis/`. Implements D.11: per-realization/order paired differences (C2−C1, C2−CR) on
RET-GS, means over orders within realization, 10,000-draw paired cluster bootstrap over the
three realizations keeping five orders together, 97.5% two-sided intervals, constraint checks
(ΔRET-GS ≥ 0.02 with lower bound > 0; ES lower bound > −0.02; LS lower bound > −0.01),
classification positive/qualified/inconclusive/negative, per-item lost sets. Input format: a
long table (JSONL or list of dicts) with fields `arm, realization, order, item_id, ret_gs, es,
ls`. Tests: hand-built tables with known answers (e.g. constant shift → interval excludes 0;
zero effect → classified negative/inconclusive as specified; missing pair → marked incomplete,
never imputed). Verify: `pytest tests/analysis/`. Cost 4 h.

**S0-07b — HVP small-matrix controls** (from plan S7-04 pre-tests; optional, do last). Owned:
`src/pccap/metrics/hvp.py`, `tests/known_answer/test_hvp_controls.py`: Gram sign (`Tr(CaᵀCb)`
PSD), loop sign `I − η²C`, block-sum identity `‖C‖²_F = Σ‖P_m C P_n‖²_F` on exact 4×4 matrices.

### Lane C — MEMORY (one agent). `CAP-01 → CAP-02 → CAP-03`

Pure NumPy/JAX-CPU; no base model needed. Owned: `src/pccap/cap/{features,bank,metadata,memory,__init__}.py`,
`tests/cap/`. Follow plan §6.3 CAP-01/02/03 verbatim (unit-scale `z(h)=LN0(h)/√d`; sorted-tensor
retrieval with inclusive radius and smallest-id ties; 128-byte packed metadata dtype with the
documented padding; `B_cap = 6144·(8d+128)`; capacities 6,144 / 2,048 / 1,374 reproduced at
zero overhead). Use NumPy arrays for bank storage (the cap is CPU-side state; values are
transferred to the device only inside the base call) so that snapshots are byte-exact. Verify:
`pytest tests/cap/`. Do **not** start CAP-04 (needs `harness/snapshot.py` from the orchestrator).

### Lane D — BASELINES (one agent). `S2-05a → S2-05b`

**S2-05a — GRACE reference environment and smoke** (PA-6, plan §6.8 first half). Owned:
`assets/envs/grace/` (separate `uv` venv with GRACE's pinned torch, CPU), `assets/third_party/GRACE`
(cloned by DATA-00; if Lane A has not run yet, clone it yourself with the same pinned HEAD and
tell Lane A), `docs/baselines/grace_reference.md`, `results/S2/grace_reference_smoke.txt`.
Run GRACE's own smallest test/example on CPU; record commit, licence, exact command, pass/fail.
Write the algorithm summary needed for the adapter: key layer, distance metric, radius init and
split rule, value optimization (steps, lr), what state is persisted. Design the SD-8 eviction
adaptation (lowest use count, then oldest) on paper in that document. **No adapter code yet**
(needs `pccap.bases.bp`).

**S2-05b — Reference parity cases**: from the DATA-00 zsRE eval file select 10 single-token
and 10 multi-token development cases (record ids; must be inside the S0 development reservation
once S0-09 exists — coordinate by listing them in `manifests/dev/grace_parity_cases.json`), run
reference GRACE on GPT-2 small (CPU, fp32) at its default layer/radius, and store edited outputs and
memory contents under `assets/reference/grace/` with hashes. These are the PC-10 oracle.

### Lane E — REG-JAX (one agent; only after Lane A's DATA-00; longer task)

**REG-00 — JAX distillation driver for the ePC checkpoint (PA-1 enabler).** The sibling's
`hdpc-distill` is PyTorch and cannot run under DEC-001. Regeneration therefore needs a JAX
implementation of the same recipe (teacher = pinned GPT-2, student = same architecture with
error variables, error-relaxation homotopy T ∈ {1,2,4,8,16,32,64} at `error_lr = 0.1` (DEC-006; the `relaxation_steps = 1` in its summary.json is an unused default), AdamW `weight_lr = 1e-6`, batch 10 × 512,
fp32, seed 1729, 9,766 steps, the sibling's KD/CE mixing and schedule file — copy the exact
formulas from `llm-by-neural-predictive-coding/src/hdpc/{energy,relax,train_distill}.py` with
file/line citations). Owned: `src/pccap/distill/`, `scripts/distill_epc.py`, `tests/distill/`,
`assets/data/raw/openwebtext/` (via the sibling's documented data recipe, URLs and hashes
recorded in `manifests/datasets.json` under `openwebtext`). It must consume the `EPCBase` from
`pccap.bases.epc` for the student forward once S0-06 lands; until then build the data pipeline,
the KD loss, the optimizer/schedule and a unit test on a 2-layer random model. REG-01 (100-step
cost pilot) and REG-02 (full run, ≤ 10 GPU-h under the lease) follow and are gated by the
S0-01 clock (CP-A + 2 working days).

## 5. Contract signatures to code against now (identical to ENV-03's `contracts.py`)

```python
from typing import NamedTuple, Protocol, Sequence, Literal, TypedDict, Any
import jax  # Array = jax.Array (device or host)

class SiteId(NamedTuple):
    bank: int      # 1, 2, 3
    block: int     # 3, 7, 11 for GPT-2 small (SD-7); 1, 3, 5 for the six-layer grammar
    position: int  # token position p (last input token in v0)

class Metric(TypedDict):
    value: float | None
    status: Literal["ok", "undefined", "unreachable", "unsupported", "unavailable"]
    units: str
    numerator: float | None
    denominator: float | None
    n: int
    strata: dict
    exclusions: list

def metric(value, *, units, numerator=None, denominator=None, n=0, strata=None,
           exclusions=None, status="ok") -> Metric: ...   # helper exported by contracts.py
```

`Write`, `ForwardResult`, `CostRecord`, `ErrorResult`, `DirectionResult`, `RouteDecision`,
`ItemOutcome`, `MemoryReport`, `EditItem`, `Budget`, `RevisionEvent`, `RoundContext`, and the
`Base`/`EPCBase`/`Transport`/`Router`/`Cap` protocols are as listed in updated_plan2.md §5
with `Tensor` = `jax.Array | numpy.ndarray`. Lane C needs only `SiteId` and `MemoryReport`
(`allocated_bytes: int, occupied_bytes: int, per_bank: dict[int, dict], index_bytes: int,
key_dim: int, value_dim: int, occupancy: dict[int, float]`).

## 6. Status (updated 2026-09-10, CP-C)

See `docs/tasks/STATUS.md` (regenerated from `manifests/tasks.json`) for the live board.

* **S0 is complete (CP-C, DEC-011):** ENV-01..04, DATA-00, S0-01, S0-03..S0-11, CAP-01..CAP-07
  on `master`; Lane B's S0-07/S0-07b/ANA-01 reviewed and merged. `results/S0/report.md`.
* **Open, no dependency on the orchestrator (claim by editing your row in `manifests/tasks.json`):**
  - Lane A: **REF-01** (HF oracle fixtures; unblocks the pending rows of S0-04/S0-09), **DATA-04**
    (LM/probe sets), **GRAM-01** (grammar generator).
  - Lane D: **S2-05a → S2-05b** (GRACE reference env and parity cases).
  - Lane E: **REG-00** (JAX distillation driver; PA-1 clock ends 2026-09-11 23:59 ET).
  - BASELINES: **S2-03** (LoRA B1/B0 in JAX/optax on `pccap.bases.bp`; owned paths
    `src/pccap/baselines/`, `tests/baselines/`) and then **S2-04** (replay B3).
* **Orchestrator lane next:** DATA-01 (editing pools; teacher generations under the GPU lease) →
  S2-01 (radius calibration) → S2-02 (A screening); S1-02/S1-03/S1-06 on BP as soon as DATA-04
  lands (or with a provisional LM sample if it does not).
