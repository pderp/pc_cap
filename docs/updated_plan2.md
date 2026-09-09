# Updated Plan 2 (v2): an agent-executable month plan for pc_cap

Prepared 2026-09-09 from a full read of [the readable month-plan PDF](pc_cap_month_plan_readable.pdf) (SHA-256 `9a2b6468…3359080`, 37 pages, revised 7 September 2026), [plan2.md](plan2.md), the [week-one plan](week1/week1plan1.md), its [review](week1/review_plan1.md) and [counter-review](week1/counter_review_week1plan1.md), and a fresh inspection of this machine and the sibling repository. This document **supersedes plan2.md as the execution baseline**. The PDF remains the scientific and implementation contract; nothing here changes a PDF threshold, endpoint, arm definition, or budget. Section references like F.3, S2, D.11, PC-4 refer to the PDF.

The purpose of this revision is stated by the lead: every task must be explicit enough that this session and other coding agents can execute the whole programme with no or minimal supervision. That requires three things plan2 did not fully provide: (1) every task carries inputs, outputs, a verification command and a mechanically checkable "done when"; (2) every decision the PDF leaves open is either pre-resolved here or listed as a one-time pre-authorization the lead grants by accepting this plan; (3) the agent workflow (claiming, worktrees, GPU serialization, evidence, merge) is specified so agents do not have to invent it.

---

## 0. What changed from plan2.md

| Area | plan2.md | This version | Why |
| --- | --- | --- | --- |
| GPU availability | "nvidia-smi cannot communicate with the driver"; RTX 5070 assumption "unverified" | **Measured today:** NVIDIA GeForce RTX 5070, 12,227 MiB, driver 610.57.04, CUDA 13.3 UMD; ~2.2 GiB in use by desktop processes | plan2's audit ran in a sandbox without device access; the physical host does have the GPU |
| Python | 3.14.7 active, no deps | Same, plus `uv` at `~/.local/bin/uv`, system 3.12 present (no torch), 3.11 installable via `uv python install 3.11` | Establishes an executable environment recipe (ENV-01) |
| ePC checkpoint | "Weights absent; do not spend 50M tokens recreating by default" | Still absent. **Pre-authorized regeneration** (PA-1) from the sibling's pinned recipe after a 100-step cost pilot, capped at 10 local GPU-hours, charged to the conditional S6 allocation by logged amendment | Without a checkpoint, Thread 1, S5, and half the report card are unavailable; the recipe, teacher revision and data pipeline exist and the projected cost is small |
| ePC training regime | Not noted | The sibling's 50M-token production run used `relaxation_steps = 1`, `error_lr = 0.1`, fp32 (its `summary.json`). The PDF's nominal eight-step credit is therefore **out of the checkpoint's training regime**; S1-06 measures it, nothing assumes it | Prevents "settled" language and makes S0-06's solver declaration concrete |
| ePC wrapper blocked on weights | S0-06 waits for "available ePC assets" | **Unblocked:** the ePC wrapper is the same GPT-2 architecture plus error variables; it is built and tested on the BP teacher weights first. Only S1 ePC rows and S5 wait for the distilled checkpoint | Removes a false dependency from the critical path |
| Grammar fixture | "Recovery first; else document replacement" | Not found anywhere on this host or in the sibling. **Pre-authorized replacement** (PA-2): build and train a new six-layer, vocab-64, length-64 grammar transformer per E.1, labelled as a replacement with no continuity to R8/R9 | Required test bed; recovery has no known source |
| WikiText drift sample | Assumed available | **Spec defect SD-3:** WikiText-103 validation is roughly 0.28M GPT-2 tokens (estimated from its ~218k words; DATA-00 records the exact count), below the 10⁶ the PDF prescribes. Pre-resolved: use the whole validation split, no repetition, log the shortfall | Counter-review CR-8 anticipated this; the count settles it |
| FabricPC/JAX | "only if the checkpoint requires it" | Present at `~/repos/fpc4/FabricPC` but **not needed**: the sibling checkpoint is PyTorch. Recorded and excluded | Avoids cross-framework gradient work |
| Second clone | Not mentioned | `/home/derp/pc_cap` is a second, docs-only clone of the same remote. **Do not work there.** The working clone is `/home/derp/cap/pc_cap` | Two agents editing two clones would fork the history |
| Task specification | Subtask + acceptance prose | Every task has Inputs / Steps / Outputs / Verify / Done-when / Cost | Mechanically checkable completion |
| Open decisions | Routed to the lead at various gates | Pre-authorizations PA-1…PA-9 and pre-resolved spec defects SD-1…SD-12; only four human touchpoints remain | Minimal supervision |
| Agent protocol | Four-worker waves, prose rules | Orchestrator + task agents, worktree-per-task, task record format, status board, GPU lease file, prompt template | Executable by Claude agents without direction |
| Data sources | "Pin zsRE/CounterFact release" | Concrete default URLs, revisions, licences and field mappings (DATA-00) | Agents cannot pin what is not named |
| Scope realism | "No throughput yet" | Prior per-run cost estimate and a pre-committed scope-selection algorithm; expectation stated that 300-edit prefixes fit and 3,000 do not on this GPU | Lets the D1 memo be produced without a human deciding what "affordable" means |

Everything in plan2 that is not listed above is retained: the reuse decision (sibling as a pinned dependency behind an adapter), the component disposition table (plan2 §2.1), the contracts (plan2 §3), the task IDs (S0-01…S8-04, CAP-01…09, DATA-01…08), the control register, the frozen analysis details (plan2 §8), and the reconciliation of earlier plans (plan2 §9). Where a plan2 task is restated below it is the restated version that governs.

---

## 1. Authority, pre-authorizations, and human touchpoints

**Authority.** The PDF is the contract. If the PDF contradicts itself, record both readings in `docs/spec_defects.md`, apply the resolution listed in Section 3 if one exists, otherwise apply the reading that changes no threshold, endpoint or arm and log it. Freeze all resolutions at S4.

**Working clone.** `/home/derp/cap/pc_cap` (remote `git@github.com:pderp/pc_cap.git`, branch `master`). Sibling dependency: `/home/derp/cap/llm-by-neural-predictive-coding` at `298fc719a0bb3e50a2b818990dd61ccca438ee62` (relative path from this file: `../../llm-by-neural-predictive-coding`).

**Pre-authorizations.** By accepting this plan the lead grants the following once. Agents act on them without asking again. Each is logged in `docs/decisions.md` when first exercised.

| ID | Pre-authorization | Bound |
| --- | --- | --- |
| PA-1 | Regenerate the ePC checkpoint with the sibling's reproduction recipe (teacher snapshot `607a30d783dfa663caf39e06633721c8d4cfcd7e`, 50M tokens, the run settings in `results/distillation/50m-tokens/summary.json`) if the original artifact (SHA-256 `4f0c23aa…84eb5`) is not located by CP-A + 2 working days. Run REG-01 (100-step pilot) first; proceed only if the projection is ≤ 10 local GPU-hours. Charge to S6's 20-hour allocation by logged amendment. The result is a **new** checkpoint: report its own hash; make no identity claim to the original; all inherited claims are re-measured. | ≤ 10 local GPU-h |
| PA-2 | Build a replacement LATENT-GRAMMAR base (six layers, vocab 64, length 64, E.1 generator) if the R8/R9 fixture is not located by CP-A + 2 working days. Label it a replacement with no continuity. Competence criterion in GRAM-02. | ≤ 2 local GPU-h |
| PA-3 | Use a provisional conversion factor κ = 1.0 (one local RTX 5070 hour = one A100-equivalent hour) with a reported sensitivity band [0.5, 2.0] until an A100 measurement of the shared workload exists. All ledgers store local seconds; reports show both. | Until measured |
| PA-4 | Pre-resolve the specification defects in Section 3 as stated there. | — |
| PA-5 | Where the PDF names a data volume the named source cannot supply (SD-3, and any found by DATA-04), use the whole available unique source, log the shortfall, and do not repeat or substitute a different corpus without a further logged decision. | — |
| PA-6 | Run baseline reference code (GRACE) under a separate pinned environment if it cannot run under the project environment; parity (PC-10) may be established on CPU. If parity cannot be established after ENV + 4 working days of effort, B4 is reported as "comparison unavailable" and the programme continues. | ≤ 4 working days |
| PA-7 | Choose the confirmatory scope by the algorithm in Section 9 without asking, as long as at least the smallest complete core comparison fits. Only if it does not fit is the lead asked (touchpoint T2). | — |
| PA-8 | Create branches, worktrees, commits and merges to `master` in the working clone, and push to `origin` at stage boundaries. No force-pushes, no history rewriting. | — |
| PA-9 | Download the public assets in DATA-00 (GPT-2 weights, zsRE, CounterFact, WikiText-103, UD English EWT, GRACE source, OpenWebText shards via the sibling recipe) and store them under `data/raw/` with hashes. | ~15 GB disk |

**Human touchpoints.** Exactly four, all asynchronous. The orchestrator writes to `docs/lead_queue.md` and continues with all work that does not depend on the answer.

| ID | When | Question | Default if no answer |
| --- | --- | --- | --- |
| T1 | Now | Accept this plan and its PA list; state the locations of the ePC checkpoint, the R8/R9 grammar, causal-fibres v0.3, comcrit, RelaLeap, and documents [2] and [5]. | After 2 working days: PA-1 and PA-2 fire; optional assets are marked unavailable. |
| T2 | D1, only if the smallest complete core comparison does not fit the S4 ceiling | Obtain more compute, accept a feasibility result for editing, or drop optional arms. | Report the feasibility result; run the core routing contrast on the synthetic beds; do not shrink realizations/orders or change the endpoint. |
| T3 | D3, only if a required paired core comparison must be dropped after optional work is already dropped | Which core pair to mark incomplete. | Mark the pair with the least completed prefix incomplete; preserve every finished pair. |
| T4 | CP-F | Review the integrated report before any external release. | No release; the report and artifacts remain in the repository. |

Anything else the PDF's Operating rule 5 would route to the lead ("unresolved changes to task scope") is by construction not needed: thresholds, endpoints and arm definitions are never changed by agents. If an agent believes one must change, it files `docs/lead_queue.md` and continues the rest of the plan.

---

## 2. Measured starting position (9 September 2026)

| Resource | Measured value |
| --- | --- |
| GPU | NVIDIA GeForce RTX 5070, 12,227 MiB, Blackwell (`sm_120`); driver 610.57.04; CUDA UMD 13.3; ~2.2 GiB used by `kwin`, Chrome and a `swipl` process at inspection |
| CPU / RAM / disk | 16 threads; 30 GiB RAM (22 available); 875 GiB free on `/home` |
| Python | 3.14.7 default (no torch); 3.12 present (no torch); `uv` available; 3.11 downloadable |
| PyTorch | Not installed in any interpreter |
| HF cache | Only `intfloat/e5-large-v2`; **no GPT-2 weights cached** |
| Datasets | None of zsRE, CounterFact, WikiText-103, UD-EWT present |
| Sibling repo | Present; pins `torch==2.11.0` (+cu128), `transformers==5.13.1`, `numpy==2.4.4`, `pytest==9.1.1`; no `.venv`, no `artifacts/`, tests present (19 files); source ~6.5k lines |
| ePC checkpoint | **Absent.** Sibling records SHA-256 `4f0c23aa…84eb5`, teacher snapshot `607a30d7…`, run config: 50,001,920 tokens, batch 10 × 512, fp32, `error_lr 0.1`, `relaxation_steps 1`, `weight_lr 1e-6`, seed 1729, 9,766 steps |
| Sibling fidelity record | `terminal-fidelity.json`: OWT-unseen mean KL 1.24e-4 (its own scaling; plan2 notes temperature-2 and ×4 factors) at 409,600 positions. This is an inherited claim, re-measured in S1-01 |
| Grammar fixture, causal-fibres, comcrit, RelaLeap | **Absent** from this host, `~/repos`, and the sibling |
| FabricPC | Present at `~/repos/fpc4/FabricPC` (JAX). Not required (checkpoint is PyTorch). Excluded |
| Other clones | `/home/derp/pc_cap` (docs-only, same remote). Not used |

Implications carried into the tasks: a 12 GiB GPU runs GPT-2 small fp32 with a cap, LoRA, GRACE and teacher/student pairs at small batch; the RTX 5070 needs a CUDA ≥ 12.8 PyTorch wheel with `sm_120` kernels; all GPU jobs on one device are serialized through a lease (Section 4.5).

---

## 3. Pre-resolved specification defects and defaults

Each row is applied by agents without further discussion, recorded in `docs/spec_defects.md` at ENV-03, and frozen at S4-01.

| ID | Issue | Committed resolution |
| --- | --- | --- |
| SD-1 | S1 uses a 2×10⁶-token held-out set H for P1; D.8 uses a 10⁶-token WikiText-103 validation sample for LM drift. | Two distinct committed sets. H = 2×10⁶ tokens sampled **by document** from WikiText-103 *train* (document ids recorded; disjoint from validation by split). Drift = WikiText-103 validation (SD-3). |
| SD-2 | S2 names 300 development edits and ≥1,000 unrelated prompts; D.5 names 200 Q and 200 U. | Q and U are manifest-fixed subsets of the S2 development pool (`manifests/dev/p5_subsets.json`). |
| SD-3 | WikiText-103 validation has roughly 0.28M GPT-2 tokens (estimate from word count; exact count recorded by DATA-00), not 10⁶. | Drift set = entire validation split, tokenized once, unique tokens only. Shortfall logged as a source-specification issue (PA-5). The test split is **not** added (keeps a clean held-out for any later use). |
| SD-4 | The correction-track slot-retirement rule reads the owner-edit digest; E.2 forbids routers from receiving fact identity in main runs. | The router API has no access to slot metadata. Retirement is a `Cap.update(..., revision=RevisionEvent)` path enabled only when the stream item carries a revision record, and only on the correction challenge track. A test asserts the router's inputs contain no digest. |
| SD-5 | "25% headroom" is ambiguous. | Reserve 25% of the ceiling: a scope is affordable when projected cost ≤ 0.75 × ceiling (plan2's convention, now committed). |
| SD-6 | F.6 leaves the ePC solver, step size and stopping to S0. The production run used one relaxation step. | Declared nominal procedure: the sibling's `relax_errors` simultaneous gradient descent on all error variables, `error_lr = 0.1`, exactly 8 iterations, errors zero-initialized per call, γ = 1, energy `½Σ‖e‖² + CE(current target only, summed not averaged)`, fp32, retrieval choices frozen within a call, no stopping rule (fixed iteration count). 64 iterations is the reference horizon. The label is "finite-iteration error credit" unless D.6's convergence test passes. |
| SD-7 | Bank hook indices. | `l_m = round(m·12/3) = 4, 8, 12` → HF `transformer.h[3]`, `h[7]`, `h[11]` block outputs, the last taken **before** `ln_f`. Verified by test in S0-04. |
| SD-8 | GRACE reference has no byte budget; PDF says run under the ceiling "when supported". | Add a documented eviction adaptation (lowest use count, then oldest) bounded by the same byte accounting; disclose in PC-10 and the report. B4 without the adaptation is also run once on development as a parity reference. |
| SD-9 | zsRE has no explicit "aliases" beyond its answer list; CounterFact has a single `target_new`. | Aliases = zsRE `answers` list (deduplicated after normalization); CounterFact aliases = `[target_new.str]`. No augmentation policy is frozen; aliases are scoring-only. |
| SD-10 | PC-2 "match the base reference": bitwise or tolerance? | The cap-off path is the same wrapper code with zero writes, so exact equality (max |Δlogit| = 0) is the expected result and the assertion. A nonzero difference is reported with the kernel identified; ≤ 1e-6 relative is tolerated only with that record (Op. rule 9). |
| SD-11 | Uniform provisional CR distribution for S2 profiling versus S3-estimated probabilities. | Profiling uses uniform (1/3 each) labelled `cr_profile_uniform`; S3-05 estimates the confirmatory distribution from development C2 routes; if C2 never routes in development, CR is uniform and that is logged as the development resolution. |
| SD-12 | "Successful training-item use count" per slot with multiple prefixes and rounds. | Increment at most once per (slot, item digest); enforced with a bounded per-item set cleared at item end. Inference never increments. Test in CAP-02. |

---

## 4. Agent execution protocol

### 4.1 Roles

| Role | Held by | Does |
| --- | --- | --- |
| ORCHESTRATOR | The interactive Claude session (or its resumed successor) | Owns `master`, `manifests/`, `docs/tasks/STATUS.md`, the GPU lease, stage reports, gates and merges. Spawns task agents. Never edits code owned by an in-flight task. |
| Task agent | A subagent per task ID (general-purpose or fork), in its own worktree | Implements exactly one task block from Section 6, runs its Verify command, writes its task record, commits on its branch. |
| REVIEWER | A separate subagent | Before a merge that touches a contract or a control, reads the task record and the cited PDF section and answers: does the artifact satisfy the Done-when? Reports discrepancies; does not edit. |
| Run owner | A task agent with the GPU lease | Executes manifest-driven runs; never modifies configuration; only appends results. |

The plan2 workstream roles (INTEGRATOR, BASE, MEMORY, DATA, METRICS, BASELINES) survive as **path ownership labels** on tasks, so two concurrent agents never edit the same directory.

| Label | Owned paths |
| --- | --- |
| INTEGRATOR | `pyproject.toml`, `requirements.lock`, `Makefile`, `src/pccap/contracts.py`, `src/pccap/harness/`, `src/pccap/cli.py`, `manifests/`, `docs/tasks/` |
| BASE | `src/pccap/bases/`, `src/pccap/transport/`, `tests/bases/` |
| MEMORY | `src/pccap/cap/`, `src/pccap/routers/`, `tests/cap/` |
| DATA | `src/pccap/data/`, `src/pccap/fixtures/`, `data/`, `tests/data/` |
| METRICS | `src/pccap/metrics/`, `src/pccap/analysis/`, `tests/metrics/`, report generators |
| BASELINES | `src/pccap/baselines/`, `tests/baselines/`, `third_party/` |

### 4.2 Task lifecycle

1. **Claim.** The orchestrator sets the task's row in `manifests/tasks.json` to `in_progress` with the agent name and start time, then creates a worktree: `git worktree add ../pc_cap-wt/<ID> -b task/<ID> master`.
2. **Brief.** The agent receives the prompt in 4.6, which embeds the task block verbatim, the PDF sections it cites, and the paths it owns.
3. **Implement** only within owned paths. If a change outside them is unavoidable, the agent writes a patch to `docs/tasks/<ID>.patch` and states it in the record; the orchestrator applies it.
4. **Verify.** Run the task's Verify command. Paste its full output (or the last 50 lines and the path of the full log) into the task record.
5. **Record.** Write `docs/tasks/<ID>.md` in the 4.3 format. Commit with message `<ID>: <one line>` plus the session attribution trailer.
6. **Review** (only for tasks marked `review: yes`). The orchestrator spawns REVIEWER with the record.
7. **Merge.** Orchestrator: `git merge --no-ff task/<ID>` into `master`, then `make test-fast`; if red, revert the merge and reopen the task. Remove the worktree.
8. **Ledger.** The orchestrator appends the task's cost to `results/ledger/tasks.jsonl`.

### 4.3 Task record format (`docs/tasks/<ID>.md`)

```
# <ID> <title>
status: done | partial | blocked | failed
agent: <name>   started: <ISO>   finished: <ISO>
commit: <hash on task/<ID>>
inputs used: <paths, hashes, upstream task IDs>
outputs: <paths>
verify command: <exact command>
verify output: <pasted or path to log>
done-when check: <each Done-when clause with pass/fail and evidence>
cost: gpu_seconds=<n> wall_seconds=<n> peak_mem_mib=<n> (0 if CPU only)
deviations: <anything done differently from the task block, and why>
unresolved: <defects found; ≤3 diagnoses and cheapest discriminating test for each>
questions for lead: <none | text also appended to docs/lead_queue.md>
```

### 4.4 Status board

`manifests/tasks.json` is the machine-readable queue: `{id, title, stage, role, deps:[ids], status, agent, worktree, commit, evidence:[paths], gpu_seconds, wall_seconds}`. `docs/tasks/STATUS.md` is regenerated from it by `python -m pccap.harness.status` and is the only file a human needs to read to know where the programme is. A task is `ready` when every dependency is `done`. The orchestrator always dispatches every `ready` task whose owned paths are not held by an in-flight task, up to the concurrency limit (default 4 agents; GPU-bearing tasks additionally limited by the lease).

### 4.5 Rules for safe concurrency

1. **One writer per path.** Enforced by the ownership table and worktrees. Never `git reset`, `checkout --`, or `stash` on another agent's branch.
2. **GPU lease.** Any process that will use CUDA for more than 60 seconds first acquires `results/.gpu_lease` (`fcntl` lock, JSON: pid, task ID, stage, projected seconds, started). One lease at a time. Throughput profiles (S2-06), resource-matched runs, and anything used for κ run with **no other GPU process**. Short tests (< 60 s) may run without the lease but must set `CUDA_VISIBLE_DEVICES` as usual.
3. **Never two learners on one cap.** Each run owns its own `Cap` instance and results directory `results/<stage>/<arm>/<base>/<read>/<realization>/<perm>/`. Parallel runs come only from immutable manifests and clean initial snapshots.
4. **Development/confirmation separation in code.** `manifests/confirm/*.json` are written once by DATA-02, hashed into `manifests/confirm/SHA256SUMS`, and loadable only through `pccap.data.confirm.load(manifest, frozen=manifests/frozen.json)`, which raises unless `frozen.json` exists and its hash matches. Development code paths never import that module (a test greps for it).
5. **Ledger outside rollback.** `results/ledger/*.jsonl` is append-only and is never part of learner state.
6. **No silent fallback** (Op. rule 8). Any exception in a run writes `error.json` with traceback and item id; the run's status becomes `correctness_failure`; nothing is retried with different numerics.
7. **Determinism settings** are set once in `pccap/__init__.py`: `torch.use_deterministic_algorithms(True)`, `CUBLAS_WORKSPACE_CONFIG=:4096:8`, TF32 off, dropout off, `torch.manual_seed` from the manifest, fixed `OMP_NUM_THREADS=16`.
8. **Push** to `origin master` at every stage boundary and at least daily; never force.

### 4.6 Task-agent prompt template

```
You are executing task <ID> of docs/updated_plan2.md in /home/derp/cap/pc_cap (worktree: <path>, branch task/<ID>).
Contract: docs/pc_cap_month_plan_readable.pdf (text extract at docs/pdf_text/plan.txt), sections <refs>.
Interface contracts: src/pccap/contracts.py (do not change; propose changes as docs/tasks/<ID>.patch).
Owned paths: <list>. Do not edit anything else.
Task block (verbatim):
<block>
Rules: no threshold or endpoint changes; log every configuration tried; no confirmatory data; every ratio carries operands and status; charge every forward/backward/settle to the ledger; determinism per Section 4.5.
When finished: run the Verify command, write docs/tasks/<ID>.md in the Section 4.3 format, commit on your branch with the trailer, and reply with the record's contents.
If blocked, write status: blocked with the exact blocker and stop; do not work around it by changing scope.
```

### 4.7 Cost recording

Every run directory contains `cost.json` from the harness ledger: full/partial forward counts, reverse/VJP counts, settle iterations, token-prefix microsteps, router probes, memory-search seconds, wall seconds, CUDA-event accelerator seconds, peak memory; query and learning columns separate. Stage totals are summed by `python -m pccap.analysis.budget` into `results/ledger/stages.json` and compared with the ceilings in Section 9 using κ from PA-3.

---

## 5. Repository layout and interface contracts (v0)

```
pc_cap/
  pyproject.toml            # package pccap, src layout, python 3.11
  requirements.lock         # uv pip compile output, exact transitive pins
  Makefile                  # test-fast, test, lint, status
  src/pccap/
    __init__.py             # determinism settings
    contracts.py            # dataclasses/Protocols below; frozen at ENV-03 (v0)
    vendor_hdpc.py          # sibling path + commit/dirty-diff recording
    bases/   bp.py epc.py checksum.py hooks.py
    transport/ transport.py  # signal -> unit direction, subspace projection
    cap/     features.py bank.py transaction.py cap.py learn.py memory.py
    routers/ last.py full.py measured.py random_.py supplied.py
    baselines/ lora.py replay.py grace_adapter.py b0.py
    data/    fetch.py streams.py tokenize.py decode.py splits.py confirm.py lm_sets.py
    fixtures/ modular_control.py grammar_model.py grammar_generator.py tracing.py
    metrics/ rank.py participation.py overlap.py divergence.py editing.py cl_matrix.py order.py hvp.py
    harness/ ledger.py records.py snapshot.py runner.py lease.py status.py schema.py
    analysis/ paired.py bootstrap.py frontier.py budget.py report.py
    cli.py
  tests/  (mirrors src; tests/controls/test_pc{1..10}_*.py; tests/known_answer/)
  manifests/ assets.json datasets.json dev/ confirm/ frozen.json tasks.json
  data/raw/ (gitignored; SHA256SUMS committed)   data/prepared/
  results/<stage>/<arm>/<base>/<read>/<realization>/<perm>/{config.json,decisions.jsonl,metrics.json,cost.json,learner.ckpt}
  results/S0/controls/  results/ledger/  results/lease
  docs/tasks/  docs/spec_defects.md  docs/decisions.md  docs/lead_queue.md  docs/environment.md  docs/epc_energy.md  docs/pdf_text/plan.txt
  third_party/GRACE (git submodule or vendored snapshot with commit and licence)
```

Contract signatures (from plan2 §3, made concrete; `contracts.py` holds these and nothing else):

```python
class SiteId(NamedTuple): bank: int; block: int; position: int      # bank m in {1,2,3}; block 3/7/11

@dataclass(frozen=True)
class Write: site: SiteId; vector: Tensor                            # additive, position p only

@dataclass
class ForwardResult: logits: Tensor; sites: dict[SiteId, Tensor]; cost: CostRecord

class Base(Protocol):
    D: int; d: int; sites: list[SiteId]
    def forward(self, ids: Tensor, writes: Sequence[Write] = (), retain_sites: bool = False) -> ForwardResult
    def forward_from(self, bank: int, hidden: Tensor, ids: Tensor, writes: Sequence[Write] = ()) -> ForwardResult  # partial, counted as partial
    def adjoint(self, ids: Tensor, target: int, writes: Sequence[Write]) -> dict[SiteId, Tensor]   # one reverse pass, all sites
    def checksum(self) -> str                                          # params + persistent buffers

class EPCBase(Base):
    def infer_errors(self, ids: Tensor, target: int | None, iters: int, writes=()) -> ErrorResult   # E_0..E_k, r_k, cost

class Transport(Protocol):
    def direction(self, signal: Tensor, site: SiteId, allowed_subspace: Tensor | None) -> DirectionResult  # unit or no-direction

class Router(Protocol):
    def schedule(self, ctx: RoundContext) -> RouteDecision              # banks, scores, abstain, cost

class Cap(Protocol):
    def predict(self, ids: Tensor) -> ForwardResult                    # read-only, asserts state hash unchanged
    def update_item(self, item: EditItem, router: Router, budget: Budget) -> ItemOutcome  # transactional, F.3
    def serialize(self) -> bytes;  def restore(self, blob: bytes) -> None;  def clone(self) -> "Cap"
    def memory_bytes(self) -> MemoryReport                              # allocated, occupied, per bank, indices

class Metric(TypedDict): value: float | None; status: Literal["ok","undefined","unreachable","unsupported","unavailable"]
                        units: str; numerator: float | None; denominator: float | None; n: int; strata: dict; exclusions: list
```

`RoundContext` carries only: prefix ids, current loss, candidate directions, bank scales `b_m`, item-keyed RNG seed material (seed, item digest, prefix index, round), and for CO the supplied permitted banks. It never carries slot metadata or answers (SD-4, PC-8).

---

## 6. Task queue

Format of every task:

**ID — title** · role · deps · review: yes/no · GPU: none/short/lease
- **Inputs:** what must exist first.
- **Steps:** what to do, in order.
- **Outputs:** paths.
- **Verify:** the command whose success is the evidence.
- **Done when:** clauses checked in the task record.
- **Cost:** budget for the task (engineering time is an estimate; GPU is a ceiling).

Tasks are listed in dependency order within each stage. "PDF" citations are the sections the agent must read. Anything marked *conditional* has its condition in the Inputs line.

### 6.1 ENV — environment and scaffold (before S0; ~1 working day)

**ENV-01 — Python 3.11 environment with Blackwell PyTorch** · INTEGRATOR · deps none · review no · GPU short
- **Inputs:** `uv`; network access.
- **Steps:** `uv python install 3.11`; `uv venv --python 3.11 .venv`; install `torch==2.11.0` from `https://download.pytorch.org/whl/cu128` (if the wheel lacks `sm_120` in `torch.cuda.get_arch_list()`, take the newest cu128/cu130 stable wheel that has it and record the deviation); `transformers==5.13.1`, `numpy==2.4.4`, `safetensors==0.8.0`, `tokenizers==0.22.2`, `huggingface-hub==1.23.0`, `scipy`, `pytest==9.1.1`, `ruff==0.15.21`, `conllu`, `requests`, `jsonschema`. `uv pip compile` → `requirements.lock`. Write `docs/environment.md` with driver, CUDA, torch, arch list, CPU, RAM, thread count, determinism flags. Run the sibling's fast tests from its directory with `PYTHONPATH=src`: `pytest tests -m "not slow and not mork" -x`, record pass/fail/skip counts.
- **Outputs:** `.venv/`, `requirements.lock`, `docs/environment.md`, `results/ENV/sibling_tests.txt`.
- **Verify:** `.venv/bin/python -c "import torch;assert torch.cuda.is_available();assert 'sm_120' in torch.cuda.get_arch_list();x=torch.randn(1024,1024,device='cuda');print((x@x).sum().item())"` and the sibling test run.
- **Done when:** CUDA matmul runs; arch list includes `sm_120`; lock file committed; sibling fast tests ran (failures recorded, not necessarily fixed); two runs of `python -m pccap.harness.determinism_probe` (written here: 100 GPT-2-shaped matmuls + a softmax) produce identical bytes.
- **Cost:** 2 h; GPU < 5 min.

**ENV-02 — Shared-workload benchmark and κ** · INTEGRATOR · deps ENV-01, DATA-00 (GPT-2 weights) · review no · GPU lease
- **Steps:** `scripts/bench_shared_workload.py`: (a) GPT-2 small fp32, TF32 off, batch 8 × 128 tokens, forward+backward, 30 s warmup then 60 s steady state → tokens/s; (b) batch-1 forward latency for prefixes of 16/32/64 tokens, 500 calls each, median and p95; (c) peak memory. Record with the ENV-01 environment hash. Set `kappa = 1.0`, `kappa_band = [0.5, 2.0]`, `status = provisional` (PA-3). If an A100 becomes reachable, rerun the same script there and replace.
- **Outputs:** `results/ENV/bench.json`, `results/ENV/kappa.json`.
- **Verify:** `python scripts/bench_shared_workload.py --check` reloads and prints both files.
- **Done when:** both files exist; the bench ran with the GPU lease held and no other CUDA process (`nvidia-smi --query-compute-apps` captured before and after).
- **Cost:** 30 min; GPU 5 min.

**ENV-03 — Package scaffold, contracts v0, Makefile, docs skeleton** · INTEGRATOR · deps ENV-01 · review yes · GPU none
- **Steps:** create the tree in Section 5 with empty modules and `contracts.py` exactly as Section 5 (plus `CostRecord`, `ErrorResult`, `DirectionResult`, `RouteDecision`, `ItemOutcome`, `MemoryReport`, `EditItem`, `Budget`, `RevisionEvent` dataclasses with documented fields). `Makefile`: `test-fast` (`pytest -m "not gpu and not slow"`), `test`, `lint` (ruff), `status`. Write `docs/spec_defects.md` seeded with SD-1…SD-12, `docs/decisions.md`, `docs/lead_queue.md` (with T1 text), `docs/pdf_text/plan.txt` (via `pdftotext -layout`), `manifests/tasks.json` with every task in this section as `pending`, and `src/pccap/harness/status.py` that renders `docs/tasks/STATUS.md`. Add `pccap/__init__.py` determinism settings (4.5 rule 7). Add `tests/test_package_layout.py` asserting the tree and that no module under `pccap/` except `data/confirm.py` mentions `manifests/confirm`.
- **Outputs:** everything above; first commit on `master`.
- **Verify:** `make test-fast && make lint && make status`.
- **Done when:** the tree matches Section 5; `contracts.py` imports; `STATUS.md` renders with all tasks pending; the PDF text extract exists.
- **Cost:** 3 h.

**ENV-04 — Sibling dependency adapter** · INTEGRATOR · deps ENV-03 · review no · GPU none
- **Steps:** `vendor_hdpc.py`: resolve `PCCAP_HDPC_PATH` (default `../llm-by-neural-predictive-coding`), verify it is a git checkout, record `commit`, `dirty` (diff hash) into `manifests/assets.json` under `sibling`, and add `src` to `sys.path` lazily. Provide `import_hdpc(name)` that raises a structured `unavailable` error if absent. Note the sibling has no top-level licence file: record `licence: unknown` and do not copy files; adaptation happens by import or by clearly headed re-implementation.
- **Verify:** `pytest tests/test_vendor_hdpc.py` (imports `hdpc.wrap`, `hdpc.relax`, `hdpc.energy`, `hdpc.checkpoint`; asserts the recorded commit is `298fc719…`).
- **Done when:** import works from a clean shell; assets.json records commit and dirty state.
- **Cost:** 1 h.

### 6.2 DATA-00 and S0-01 — assets

**DATA-00 — Fetch and hash public assets** · DATA · deps ENV-01 · review no · GPU none
- **Steps (each with URL, revision, licence recorded in `manifests/datasets.json` and file hashes in `data/raw/SHA256SUMS`):**
  1. GPT-2 small: `huggingface_hub.snapshot_download("openai-community/gpt2", revision="607a30d783dfa663caf39e06633721c8d4cfcd7e")` (the sibling's pinned snapshot). Licence: MIT (modified).
  2. zsRE (MEND format, used by ROME/GRACE): `https://rome.baulab.info/data/dsets/zsre_mend_eval.json` and `zsre_mend_train.json`. Fields: `src`, `rephrase`, `answers`, `alt`, `loc`, `loc_ans`, `subject`. Licence: as distributed by ROME (MIT repo); record.
  3. CounterFact: `https://rome.baulab.info/data/dsets/counterfact.json`. Fields: `case_id`, `requested_rewrite{prompt,subject,target_new,target_true}`, `paraphrase_prompts`, `neighborhood_prompts`, `attribute_prompts`, `generation_prompts`. Licence: MIT (ROME).
  4. WikiText-103 raw: HF dataset `Salesforce/wikitext`, config `wikitext-103-raw-v1`, parquet for `train`, `validation`, `test`; record the HF revision. Licence: CC BY-SA 3.0.
  5. UD English EWT: `https://github.com/UniversalDependencies/UD_English-EWT` at the latest release tag; `en_ewt-ud-{train,dev,test}.conllu`. Licence: CC BY-SA 4.0.
  6. GRACE source: `git clone https://github.com/Thartvigsen/GRACE third_party/GRACE`; record HEAD commit and licence file.
  7. OpenWebText shards for REG only: through the sibling's `hdpc-prepare` recipe (deferred to REG-01; not fetched here).
  If any URL fails, record `unavailable` with the HTTP status and continue with the others; do not substitute a different source.
- **Outputs:** `data/raw/…`, `data/raw/SHA256SUMS`, `manifests/datasets.json`.
- **Verify:** `python -m pccap.data.fetch --verify` (re-hashes every file and compares).
- **Done when:** every listed asset is `present` with hash or `unavailable` with reason; token counts for WikiText splits are recorded (this feeds SD-3 and DATA-04).
- **Cost:** 1 h; ~2 GB disk.

**S0-01 — Asset inventory and lead queue** · INTEGRATOR+BASE · deps ENV-04, DATA-00 · review no · GPU none
- **Steps:** search this host (`locate`/`find` on `*.pt`, `*.safetensors`, names containing `pc`, `epc`, `grammar`, `fibre`, `comcrit`, `relaleap`), the Drive links in `footnotes.md` (record only whether they resolve; do not download private documents into the repo), and the sibling for: the ePC checkpoint (`4f0c23aa…`), its full resume state, the R8/R9 grammar model/tokenizer/generator, causal-fibres v0.3, comcrit, RelaLeap, references [2] and [5]. Inspect the teacher config and tokenizer. Write `manifests/assets.json` with `status ∈ {verified, absent, regenerable, unavailable}` and provenance; write T1 into `docs/lead_queue.md` with the absent list; start the two-working-day PA-1/PA-2 clocks (`docs/decisions.md`).
- **Verify:** `python -m pccap.harness.schema validate manifests/assets.json`.
- **Done when:** every PDF §3.1 asset line has a status; three bundled sibling `.pt` files are recorded as flowmap tensors, not weights; the T1 entry exists with a dated deadline.
- **Cost:** 1 h.

### 6.3 S0 — harness, invariants, minimal cap (8 A100-h ceiling; week 1)

**S0-03 — Schemas, outcome codes, CLI skeleton, ledger, records** · INTEGRATOR · deps ENV-03 · review yes · GPU none
- **Steps:** `harness/schema.py` with JSON schemas for `config`, `decision record` (F.7 fields: item digest, prefix, round, candidate banks, signed scores, chosen route, accepted increment, before/after loss, allocation/conflict/eviction codes, cost counters), `metrics` (Section 5 `Metric`), `cost`, `manifest` (development and frozen variants; frozen requires every field in S4-01). `harness/records.py` with the closed outcome-code enum: `accepted, rejected_no_improvement, no_direction, abstain, ambiguous_key_conflict, evicted, acquisition_failure, unreachable, undefined, unsupported, unavailable, resource_stop, nonfinite_failure, revision_replaced, revision_replayed`. `harness/ledger.py` counters (4.7) with context managers around every base call. `cli.py`: `pccap run --stage --arm --base --read --realization --perm --manifest [--mode dev|confirm]`; `pccap report --stage`; `pccap status`. The CLI validates the manifest against the schema for its mode and exits non-zero listing missing fields.
- **Verify:** `pytest tests/harness/test_schema.py tests/harness/test_ledger.py tests/harness/test_cli.py` (includes: a manifest missing one frozen field fails; ledger counts survive a simulated rollback; outcome codes are distinct from NaN).
- **Done when:** tests pass; `docs/outcome_codes.md` lists every code with meaning and where it is emitted.
- **Cost:** 4 h.

**S0-04 — BP base wrapper** · BASE · deps ENV-01, ENV-03, DATA-00 · review yes · GPU short · PDF F.1, F.7, Op. rules 9–10
- **Steps:** `bases/bp.py`: load GPT-2 small from the pinned snapshot; `requires_grad=False` on all parameters; `eval()`; dropout modules replaced by identity; `use_cache=False`. Implement the forward as an explicit block loop (embedding → `h[0..11]` → `ln_f` → head) so that `forward_from(bank, hidden)` can resume at block 4/8/12 (SD-7) and so writes are applied by adding `Write.vector` to the residual at position p immediately after the block output and before the next block (for bank 3, before `ln_f`). Sites returned in `ForwardResult.sites` are the pre-write residuals. `checksum()` hashes parameters and persistent buffers. Every call records full/partial forward counts, wall and CUDA-event time.
- **Verify:** `pytest tests/bases/test_bp_base.py -m gpu`: (a) no-write logits equal HF `GPT2LMHeadModel` logits exactly on 256 development prompts (SD-10); (b) site tensors equal `output_hidden_states[l]` for l = 4, 8 and equal the pre-`ln_f` residual for l = 12 (HF's last hidden state is post-`ln_f`, so compare against a hook on `h[11]`); (c) a write at bank 1 changes sites 2 and 3 and the logits; a write at bank 3 changes only logits; writes at position p ≠ last do not occur; (d) `forward_from` equals a full forward with the same writes; (e) checksum unchanged after 100 forwards; (f) padding and prompt lengths 1…128 behave.
- **Done when:** all six assertions pass; cost counters increment per call.
- **Cost:** 5 h; GPU 10 min.

**S0-05 — Hidden-site adjoints and forced interventions** · BASE · deps S0-04 · review yes · GPU short · PDF F.3 step 2–3
- **Steps:** `Base.adjoint`: run the block loop with `.detach().requires_grad_()` leaves inserted at the three sites (after applying writes), compute `CE(logits[p], target)`, one `backward`, return `∂L/∂h` at each site; assert no parameter received a gradient; count one reverse. `transport/transport.py`: `direction = -g/‖g‖` (adjoint) with `no_direction` when `‖g‖ < 1e-12`; optional projection onto an allowed subspace **before** normalization (fixture use). Sign-convention control: on a 1-D differentiable toy (`loss = (w·h − y)²`) the returned direction reduces the loss; recorded once in `results/S0/controls/sign_convention.json`; never flipped per example.
- **Verify:** `pytest tests/bases/test_adjoint.py tests/transport/test_transport.py -m gpu`: finite-difference agreement (relative error < 1e-3 in fp32 with step 1e-2 along the direction) at each site on 8 prompts; one reverse per call in the ledger; frozen-parameter assertion; zero-vector → `no_direction`.
- **Done when:** tests pass; sign-convention record exists.
- **Cost:** 3 h; GPU 5 min.

**S0-06 — ePC base wrapper and declared energy (built on BP weights first)** · BASE · deps S0-04, ENV-04 · review yes · GPU short · PDF D.6, F.6, §2.2, SD-6
- **Inputs:** BP weights (always available). The distilled checkpoint is **not** required for this task.
- **Steps:** `bases/epc.py`: wrap the sibling's `PCGPT2.forward_states` idea in our own block loop with error variables `e_l` added at each post-block site (all 12 blocks, matching the sibling's error sites; record which). Energy per SD-6: `E(e;x,y) = ½Σ_{l,t}‖e_{l,t}‖² + CE(f(x;e)[p], y)` with the CE summed over the single current target for credit calls and over declared positions for report-card calls. `infer_errors`: zero-init errors each call; `iters` steps of simultaneous gradient descent with `error_lr = 0.1`; record `E_0…E_k`, `r_k = ‖∇_e E_k‖ / max(1, ‖∇_e E_0‖)` computed explicitly at the terminal iterate (not from the pre-update norm); count each iteration as one forward and one reverse; retrieval/writes frozen within a call; no state carried between calls; `target=None` gives the unclamped variant (with zero-init this equals the feedforward computation; report as a consistency check, D.1). Expose `error_at_site(bank)` and the documented descent sign (the error variable's negative, verified on the toy as in S0-05). Write `docs/epc_energy.md` recording: energy, γ, solver, step size, iteration count, dtypes, no precision matrices, reset, no stopping rule, and the note that the production checkpoint was trained with one relaxation step.
- **Verify:** `pytest tests/bases/test_epc_base.py -m gpu`: (a) with zero errors, logits equal BP wrapper logits exactly; (b) `E_k` is non-increasing over 8 iterations on 16 prompts at `error_lr 0.1` (if not, record the fact; it is a measurement, not a test failure, and the test then only checks finiteness); (c) no parameter gradient accumulates; (d) two calls with the same inputs give identical errors (fresh state); (e) ledger counts 8 forwards and 8 reverses for `iters=8`; (f) sign control passes.
- **Done when:** tests pass on BP weights; `docs/epc_energy.md` exists; the wrapper loads a state dict by path so REG-03 can swap in the distilled weights without code changes.
- **Cost:** 6 h; GPU 10 min.

**S0-07 — Metric library with known-answer tests** · METRICS · deps ENV-03 · review yes · GPU none · PDF S0, D.2, D.3, D.4, D.7, D.9
- **Steps:** implement `rank.effective_rank` (centre, SVD, `exp(−Σ p log p)`, zero-matrix → rank 0 with status), `participation.pr` and `active_fraction`, `overlap.subspace_overlap` (`‖UaᵀUb‖²_F / r`), `divergence.kl` and `js` (natural logs; JS ∈ [0, log 2]), `cl_matrix` (ACC/BWT/FWT/F per D.7, plus late-acquisition gain), `order.scalar_quadratic_reversal` (two gradient steps, η, returns displacement and Hessian commutator), `editing.normalize_answer` and `exact_match_aliases`, structured `Metric` builders with operands.
- **Verify:** `pytest tests/known_answer/`: uniform rank-r spectrum → r; unequal nonzero singular values → below algebraic rank; zero matrix → rank 0 and status `undefined`; uniform mass over N cells → PR = N; zero mass → status code; overlap 0/1 for orthogonal/identical; JS of identical distributions = 0 and ≤ log 2; scalar quadratic `L1=θ²/2, L2=(θ−1)²/2` gives displacement exactly η² (to 1e-12) with zero commutator; D.7 matrix on a hand-built 3-task table gives the hand-computed ACC/BWT/FWT/F; two-token wrong-second-token answer fails exact match.
- **Done when:** every listed case passes; each function returns a `Metric` with operands.
- **Cost:** 4 h.

**S0-08 — Snapshot, clone, strict resume, resource-stop rollback** · INTEGRATOR · deps S0-03, CAP-02 (schema) · review yes · GPU none · PDF Op. rule 9, App. B, F.2, CR-6
- **Steps:** `harness/snapshot.py`: `LearnerState` = all cap arrays, radii, ids, metadata, correction index, use counters, per-item use set, RNG states (Python, NumPy, Torch CPU and CUDA), replay/optimizer state when present, and a content hash. `serialize/restore/clone` byte-exact. Atomic file writes (temp + rename). Resume refuses on any hash or schema mismatch (stricter than the sibling's relaxed resume). Resource-stop semantics: a run interrupted mid-item restores the pre-item snapshot (including accepted earlier prefixes) and marks `resource_stop`; the ledger keeps every cost incurred.
- **Verify:** `pytest tests/harness/test_snapshot.py`: clone → mutate → original unchanged; serialize/restore round-trip equals clone hash; kill-and-resume on a mock learner reproduces the same decisions as an uninterrupted run; resource stop after an accepted prefix restores the item boundary and the ledger total is unchanged by the rollback.
- **Done when:** tests pass; the hash covers every field listed.
- **Cost:** 4 h.

**S0-09 — Development reservation, tokenization helper, reference decoder** · DATA · deps DATA-00, S0-03 · review yes · GPU short · PDF E.2, D.8, PC-7
- **Steps:** `data/splits.py`: reserve a **small S0 development sample** now (40 zsRE + 40 CounterFact items chosen by seed 7 from `zsre_mend_eval` and `counterfact`), write `manifests/dev/s0_sample.json` with hashes, and record their subjects/facts in `manifests/dev/reserved_subjects.json` so DATA-02 excludes them from confirmation. `data/tokenize.py`: one helper that tokenizes prompt and `answer + "\n"` separately, asserts `decode(answer_ids) == answer + "\n"`, and excludes answers whose tokens with delimiter exceed 32 (counted). `data/decode.py`: greedy, max 32 new tokens, stop at `\n` or EOS, **full prefix recompute, no KV cache**, cap writes only at the current prediction position, read-only (asserts learner hash unchanged). Normalization: NFKC, casefold, whitespace collapse, trim. Exact match against aliases (SD-9). Truncation is failure unless the full accepted answer was already emitted. Teacher-forced NLL reported alongside.
- **Verify:** `pytest tests/data/test_tokenize.py tests/data/test_decode.py tests/controls/test_pc7_complete_answers.py -m gpu`: round-trip; the 32-token exclusion counted; PC-7 (correct first, wrong second token fails; teacher-forced success does not override); decode of 8 s0-sample prompts with the BP base matches HF `generate(do_sample=False, use_cache=False)` token for token; hidden answer is not reachable from the decode path (the function signature has no answer argument).
- **Done when:** tests pass; `s0_sample.json` and `reserved_subjects.json` exist and are hashed.
- **Cost:** 4 h; GPU 5 min.

**CAP-01 — Key features and deterministic retrieval** · MEMORY · deps ENV-03 · review no · GPU none · PDF F.1
- **Steps:** `cap/features.py`: `LN0` (centre, divide by sqrt(var + 1e-5)), `z(h) = LN0(h)/√d`. `cap/bank.py`: fixed-capacity FP32 key `[S, dk]` and value `[S, d]` arrays, immutable slot ids, active mask; `retrieve(q)`: among active slots with `‖q − k‖₂ ≤ ρ` (inclusive) choose the nearest, ties → smallest id; zero radius requires exact equality; implemented with sorted tensors, never with dict/set iteration order.
- **Verify:** `pytest tests/cap/test_features.py tests/cap/test_retrieve.py`: unit-scale keys at three widths; boundary inclusive; tie → smallest id; zero radius exact only; zero vector handled; retrieval identical across 100 shuffles of insertion order.
- **Cost:** 3 h.

**CAP-02 — Slot metadata, use-count semantics, byte layout** · MEMORY · deps CAP-01 · review no · GPU none · PDF F.2, SD-12
- **Steps:** packed metadata per slot in a structured NumPy array padded to exactly 128 bytes: `radius f32, use_count u32, created u64, last_use u64, last_target i32, owner_digest 16B, version u32, loss_ema f32, active u8, flags u8` (document the padding). Per-item bounded set `used_slots_this_item` cleared at item end; `use_count` increments once per (slot, item). `predict` paths cannot call the mutator (separate class with no public setter). Persistent memory report counts keys, values, metadata, indices, the correction index and any caches.
- **Verify:** `pytest tests/cap/test_metadata.py`: multi-prefix, multi-round item increments once; inference never increments; layout is 128 bytes; memory report equals `S·(4dk + 4d + 128) + index bytes`.
- **Cost:** 3 h.

**CAP-03 — Byte ceiling and capacity** · MEMORY · deps CAP-02 · review no · GPU none · PDF App. B "Memory ceiling", PC-6
- **Steps:** `cap/memory.py`: `B_cap = 6144·(8d + 128)` (= 38,535,168 bytes at d = 768); C0 → all to bank 3; three-bank arms → equal thirds (12,845,056); `S_m = floor((B_m − fixed_overhead_m) / (4dk + 4d + 128))`, where `fixed_overhead_m` is the measured bytes of indices and bookkeeping for an empty bank. Report allocated and occupied bytes, key/value dims, occupancy, and training peak memory separately.
- **Verify:** `pytest tests/cap/test_memory.py`: nominal upper bounds 6,144 / 2,048 / 1,374 (dk = 2d) reproduced when overhead is zero; actual capacities are ≤ nominal and reported; wide keys reduce capacity; sum of bank ceilings equals `B_cap` for every arm.
- **Cost:** 2 h.

**CAP-04 — Transactions, conflicts, eviction, revisions** · MEMORY · deps CAP-03, S0-08 · review yes · GPU none · PDF F.2, PC-4, SD-4
- **Steps:** `cap/transaction.py`: `begin()` snapshots bank arrays, metadata, ids, indices and RNG; `commit()`/`rollback()`. Conflict on firing slot with different last target: distinct keys at distance `d_qs > 0` → old radius `min(ρ_s, 0.49·d_qs)`, new slot radius `min(ρ_0, 0.49·d_qs)`, old key/value intact, retrieval recomputed; identical keys with incompatible targets → if the item carries a `RevisionEvent` for the same fact digest, retire the older fact/version slots inside the same transaction and attempt replacement (`revision_replaced`), replay of the same version is idempotent (`revision_replayed`); otherwise `ambiguous_key_conflict`, reject this bank, preserve old memory. Full bank → evict lowest `use_count`, then oldest `last_use`, then smallest id; eviction commits only with a successful write. Bounded correction index of active digests counted in memory.
- **Verify:** `pytest tests/controls/test_pc4_conflict.py`: distinct-key conflict preserves old key/value and keeps radii ≥ 0; identical-key ambiguity rejects and logs; newer version replaces; same version replays idempotently; a failed replacement rolls back values, metadata, radii, ids, index and RNG byte-exactly; deterministic eviction order at full capacity; the router never receives digests (grep-based test on `RoundContext` fields).
- **Cost:** 6 h.

**CAP-05 — Routers** · MEMORY+BASE · deps CAP-04, S0-05 · review yes · GPU short · PDF F.3 steps 3–4, PC-5
- **Steps:** `routers/`: `Last` (bank 3), `Full` (all three), `Measured` (C2): for each bank with a direction, apply a temporary forced write `ε·b_m·d_m` (ε = 0.01), recompute the downstream forward **with live discrete retrieval** via `forward_from`, score `r_m = (L − L_probe)/ε`, select the largest positive score with improvement `> max(1e-8, 1e-6·L)`, ties by depth, else abstain; nothing is committed; probe cost charged. `Random` (CR): one bank from a fixed distribution with RNG keyed by `(seed, item digest, prefix index, round)`. `Supplied` (CO): the permitted banks in depth order. Every rule logs zero-direction and conflict cases.
- **Verify:** `pytest tests/controls/test_pc5_probe.py tests/routers/`: on an analytic 1-D loss a helpful probe scores positive and a harmful one negative; abstention below threshold; CR reproduces the same choice for the same key across reversed-order replays; no learner state changes after a probe (hash equal); ledger records the probe forwards.
- **Cost:** 5 h; GPU 5 min.

**CAP-06 — Transactional candidate search and budget** · MEMORY · deps CAP-05 · review yes · GPU short · PDF F.3 steps 5–6, PC-5/6
- **Steps:** `cap/learn.py::round_update`: for `b` scheduled banks reserve `A/b` each with no redistribution; process by depth; after each accepted earlier write recompute features, gates, loss and credit; candidates `Δv = w·a·b_m·d_m` for `a ∈ {A/b, A/2b, A/4b, A/8b}` plus no-op, each evaluated from the same original snapshot with ordinary retrieval (new slots start at zero value); choose the smallest loss, tie → smaller increment; commit only if improvement `> max(1e-8, 1e-6·L)`, else restore. Aggregate `Σ‖Δv_m‖/b_m ≤ A` asserted. Up to four forward candidates per bank per round recorded.
- **Verify:** `pytest tests/controls/test_pc5_search.py tests/controls/test_pc6_budget.py`: non-monotone analytic loss does not crash and does not assume bracketing; accepted state equals the evaluated candidate byte-for-byte; rejected search restores exactly and is charged; aggregate increment ≤ A on 100 random rounds; C0/C1/C2/CR share the byte ceiling.
- **Cost:** 5 h; GPU 5 min.

**CAP-07 — Complete-edit learning loop** · MEMORY+DATA · deps CAP-06, S0-09 · review yes · GPU short · PDF F.3, E.2, PC-3
- **Steps:** `cap/learn.py::update_item`: visit each gold prefix `(x, y_<t)` including the terminating newline; at most R = 5 rounds per prefix; stop at `CE ≤ 0.1`; record threshold attainment per prefix separately from end-of-item free-generation ES/GS; metadata updated on commit (target token, digest, version, use count once per item, last use, optional loss EMA at rate 0.2 from the pre-update loss); item-level `ItemOutcome` with codes; every decision record written.
- **Verify:** `pytest tests/controls/test_pc3_idempotence.py tests/cap/test_update_item.py -m gpu`: on 20 s0-sample items that reach threshold, an immediate repeat allocates no new slots; per-prefix and per-item outcomes are both present; the ledger sums every prefix microstep.
- **Cost:** 5 h; GPU 15 min.

**S0-10 — Minimal cap integration smoke and the four pre-run invariants** · MEMORY · deps CAP-07, S0-08, S0-04 · review yes · GPU short · PDF S0, PC-2, PC-6, PC-8, PC-9
- **Steps:** `cap/cap.py` assembling three banks over the BP base; one complete development smoke edit (s0-sample item 0, C1, A = 0.1, uniform radius placeholder 0.0 → exact key) run through `pccap run --stage S0 --mode dev`. Controls: PC-2 (cap-off logits equal base on 256 probes; oracle-false gate identity), PC-6, PC-8 read-only evaluation (learner hash unchanged after `predict` and `decode`), PC-9 (clone equality, identical replay, reversed-sequence start equality, scalar order effect), reproducibility (two full replays: identical decisions, metrics within 1e-6 rel / 1e-8 abs).
- **Verify:** `pytest tests/controls/test_pc2_identity.py tests/controls/test_pc8_readonly.py tests/controls/test_pc9_cloning.py tests/test_reproducibility.py -m gpu` and `pccap run --stage S0 --arm C1 --base BP --read h --realization 0 --perm 0 --manifest manifests/dev/s0_smoke.json`.
- **Done when:** the four invariants (cap-off identity, memory accounting, transactional rollback, complete-state cloning) pass and their evidence is under `results/S0/controls/`; the smoke run wrote `decisions.jsonl`, `metrics.json`, `cost.json`, `learner.ckpt`; the base checksum is unchanged; acquisition may have failed.
- **Cost:** 4 h; GPU 15 min.

**S0-11 — S0 stage report and CP-C** · INTEGRATOR · deps S0-10, S0-06, S0-07, S0-09 · review yes · GPU none · PDF App. G
- **Steps:** `pccap report --stage S0` renders `results/S0/report.md` with the ten Appendix G sections, the control table (expected/observed/pass), the dependency table naming which later measurement each still-failing control blocks, cost against 8 A100-h (κ per PA-3), and the ePC status (wrapper built on BP weights; distilled checkpoint status).
- **Done when:** report filed; `manifests/tasks.json` shows every S0/CAP task `done` or a named blocker; CP-C recorded in `docs/decisions.md`.
- **Cost:** 2 h.

### 6.4 REG — ePC checkpoint regeneration (conditional on PA-1)

**REG-01 — Cost pilot** · BASE · deps ENV-04, S0-01 clock expired without a located artifact · review no · GPU lease
- **Steps:** run the sibling's `hdpc-prepare` for the pilot inputs and then `hdpc-distill` for **100 steps** with the production settings from `results/distillation/50m-tokens/summary.json` (batch 10 × 512, fp32, `error_lr 0.1`, `relaxation_steps 1`, `weight_lr 1e-6`, seed 1729, the same schedule file), measuring steady-state seconds/step after 20 warmup steps. Project `9766 × s/step` plus data preparation time. Record in `results/REG/pilot.json`.
- **Done when:** projection recorded; decision `proceed` if ≤ 10 local GPU-h else `escalate` (lead queue) written to `docs/decisions.md`.
- **Cost:** 2 h; GPU ≤ 30 min.

**REG-02 — Full regeneration** · BASE · deps REG-01 = proceed · review no · GPU lease
- **Steps:** prepare the 50M-token shards per the sibling reproduction guide (record every URL and hash it reports); run the full recipe to completion with checkpoints every 1,000 steps under `artifacts/runs/…`; copy the final `model_state` to `data/models/epc_regen.pt`; hash it; record the run summary. Never exceed 10 GPU-h: if the projection was wrong, stop at the ceiling, keep the checkpoint, and record `resource_stop`.
- **Done when:** `manifests/assets.json` has `epc_checkpoint: {status: regenerated, sha256, run_summary, tokens_seen}`; budget amendment logged against S6.
- **Cost:** GPU ≤ 10 h (projected 3–5 h).

**REG-03 — Load and preflight** · BASE · deps REG-02 or a located original, S0-06 · review yes · GPU short
- **Steps:** load into `EPCBase`; cap-off identity of the ePC wrapper against its own vanilla forward; quick KL to the teacher on 50k tokens (a smoke figure, not S1-01); record dtype, config equality with the teacher, and tokenizer equality.
- **Done when:** `results/REG/preflight.json` exists; S1 ePC rows become `ready`.
- **Cost:** 1 h; GPU 10 min.

### 6.5 GRAM — replacement learned grammar (conditional on PA-2)

**GRAM-01 — Grammar generator per E.1** · DATA · deps ENV-03 · review yes · GPU none · PDF E.1 LATENT-GRAMMAR
- **Steps:** `fixtures/grammar_generator.py`: vocabulary 64 (2 reserved: BOS, PAD; 8 context tokens; 54 content tokens); sequence length 64; eight observable contexts (context token at position 0 and re-emitted every 16 tokens); two shared switches and one private switch per context; deterministic generative rules where a switch changes a token-transition rule (private: only inside its context; shared: the same rule family in all contexts); one designated evaluated position per sequence (position 48–63, sampled by seed) with one supplied causal label `(kind ∈ {private, shared_1, shared_2}, context)`; manifests for development, training, evaluation (2,000 per task) and held-out switch combinations; five balanced eight-task orders with every task at least once in the first and last quarter.
- **Verify:** `pytest tests/fixtures/test_grammar_generator.py`: flipping a private switch changes only sequences of its context; flipping a shared switch changes the designated mechanism in all contexts; context is always observable; the five orders satisfy the balance property; regenerating from a manifest is byte-identical.
- **Cost:** 6 h.

**GRAM-02 — Train the six-layer base** · DATA+BASE · deps GRAM-01 · review no · GPU lease
- **Steps:** `fixtures/grammar_model.py`: six-layer pre-norm transformer, d = 128, 4 heads, vocab 64, length 64, same block/hook conventions as GPT-2 (bank sites `round(m·6/3)` = 2, 4, 6 → blocks 1, 3, 5, last before final norm). Train on the **base grammar** (all contexts; all switches at their default value) with AdamW until held-out next-token accuracy at the designated positions ≥ 0.98 or 30 minutes of GPU, whichever first. The continual tasks are the eight contexts with their private switch flipped and the two shared switches set to their non-default values consistently. Record frozen-base accuracy `b_i` on every task (expected low by construction) and joint-training reference accuracy (same total examples).
- **Done when:** `data/models/grammar_base.pt` with hash and training log; competence table in `results/GRAM/competence.json`; labelled "replacement fixture, no continuity with R8/R9".
- **Cost:** 3 h; GPU ≤ 1 h.

**DATA-07 — Causal tracing pairs on the grammar** · DATA+METRICS · deps GRAM-02 · review no · GPU short · PDF D.10, E.1
- **Steps:** manifest of clean/corrupt pairs that change one latent; patch depths and positions fixed **before** any tracing result is seen; restoration score `R = (p_restore − p_corrupt)/(p_clean − p_corrupt)` with clean–corrupt gap ≥ 0.1; keep every site ≥ 0.5, continuous scores, overshoot, weak, no-site and multi-site cases.
- **Verify:** `pytest tests/fixtures/test_tracing.py` (score on a hand-built 3-outcome example; weak pairs excluded and counted).
- **Cost:** 3 h; GPU 10 min.

### 6.6 DATA — editing data, fixtures, LM sets (parallel with S0)

**DATA-01 — Editing pools** · DATA · deps S0-09 · review yes · GPU lease · PDF E.2, D.1
- **Steps:** `data/streams.py` readers for both sources (field mapping in DATA-00; zsRE locality prompt = `loc`/`loc_ans`; CounterFact locality = `neighborhood_prompts`, paraphrases = `paraphrase_prompts`). Canonical answer + `\n`; exclude > 32 tokens (count). Deduplicate facts and subjects. Run the BP teacher's complete greedy generation on every candidate prompt and **keep only items whose normalized answer is outside the aliases** (E.2). Build the development pool: ≥ 300 edits with paraphrases per dataset (including the S0 sample), ≥ 1,000 unrelated/near-neighbour prompts per dataset; the remaining eligible items form the sealed confirmation source pool (not yet split). Log the teacher-generation access under `results/DATA/selection_access.log`.
- **Outputs:** `manifests/dev/{zsre,counterfact}_dev.json`, `data/prepared/{zsre,counterfact}_eligible.jsonl` (hashed), exclusion counts.
- **Verify:** `pytest tests/data/test_streams.py` and `python -m pccap.data.splits --audit` (prints counts: candidates, excluded by length, teacher-correct, eligible, dev, confirm-pool; asserts dev ∩ confirm-pool subjects = ∅).
- **Cost:** 4 h; GPU ~1 h (teacher generations over ~40k prompts at 32 tokens, no cache).

**DATA-02 — Realizations, orders, sealed confirmation manifests** · DATA · deps DATA-01, DATA-08 · review yes · GPU none · PDF App. B "Randomization"
- **Steps:** from the confirmation pool, three subject-disjoint realizations (seeds 0, 1, 2) of up to 3,000 zsRE and 1,000 CounterFact edits each (fewer if the pool is short: record); five orders per realization with seeds 100–104; separate named seeds for cap init, router and replay. Write `manifests/confirm/*.json`, `SHA256SUMS`, and a metadata-only sidecar (counts, length strata) readable by tuning code. Enforce 4.5 rule 4.
- **Verify:** `pytest tests/data/test_confirm_seal.py`: loading without `frozen.json` raises; metadata sidecar has no prompts or answers; realizations are subject-disjoint (overlaps logged if unavoidable).
- **Cost:** 3 h.

**DATA-03 — MODULAR-CONTROL fixture** · DATA+MEMORY · deps ENV-03, CAP-05 · review yes · GPU none · PDF E.1 MODULAR-CONTROL, PC-1
- **Steps:** `fixtures/modular_control.py`: a small residual computation graph (width 32, three module groups at the three write depths) with fixed masks routing each private latent through its designated path and shared latents through an explicit shared path; output coordinates partitioned so a permitted write at one site cannot directly overwrite other sites' outputs; fixed allowed write subspace per bank supplied to **every** arm (projection before normalization in `Transport`); oracle routes supplied only to CO. ≥ 100 private, ≥ 100 shared, ≥ 100 mixed-cause items plus held-out combinations; no-sharing, useful-sharing and wrong-router variants. Record masks, sites and `R*`.
- **Verify:** `pytest tests/controls/test_pc1_planted.py tests/fixtures/test_modular_control.py`: the supplied router recovers ≥ 19/20 planted targets within the round budget with unrelated outputs unchanged within 1e-6; the full fixture oracle reaches ≥ 95% of planted deterministic targets; wrong-router variant fails as designed.
- **Cost:** 8 h.

**DATA-04 — LM, probe and property sets with inventory** · DATA+METRICS · deps DATA-00 · review no · GPU none · PDF S1, D.2, D.3, D.8, E.4, SD-1, SD-3
- **Steps:** tokenize WikiText-103 splits once with the GPT-2 tokenizer; record unique document and token counts. H = 2×10⁶ tokens by document from train (seed 11); drift = entire validation (SD-3; log shortfall); P2 = 4,096 held-out positions from H's complement in train; P3 = 1,000 teacher-forced sequences of 128 tokens from the same complement; POS = UD-EWT train (≥ 20,000 tokens) and dev (≥ 5,000) mapped to GPT-2 tokens by first-subtoken labelling (documented). E.4 domain manifests: eight "domains" = eight WikiText-103 topic clusters are **not** available; record E.4 natural-language domains as `unsupported` for GPT-2 small this month and use the grammar's labelled mechanisms for P4 (PDF E.4 permits this substitution; state it). Document-level deduplication across all sets.
- **Verify:** `python -m pccap.data.lm_sets --audit` (prints counts and shortfalls; asserts disjointness by document id).
- **Cost:** 3 h.

**DATA-06 — Grammar task streams** · DATA · deps GRAM-02 · review no · GPU none
- **Steps:** eight tasks (one per context), three realizations, five committed orders; training count per task chosen at S4 from {256, 1024, 10000}; evaluation 2,000 per task; held-out switch combinations; joint-training reference manifest with the same total examples; one sequence/target pair per item at the designated position.
- **Verify:** `pytest tests/data/test_grammar_streams.py` (balance property; item count equals sequence count; no 64-way expansion).
- **Cost:** 2 h.

**DATA-08 — Challenge sets** · DATA+BASELINES · deps DATA-01 · review no · GPU short · PDF E.2 challenge paragraph
- **Steps:** ≥ 100 near-neighbour pairs requiring different answers (CounterFact neighbourhood prompts whose true answer differs from the edited target; zsRE items sharing a subject with different relations); ≥ 100 compositions where the reference supports unambiguous evaluation (zsRE pairs `(s, r1) → o1`, `(o1, r2) → o2` present in the pool; if fewer than 100 exist, report the count as `unsupported` for the remainder); ≥ 100 explicit temporal corrections built from CounterFact items by supplying `target_true` then `target_new` as versions 1 and 2 of the same fact id. All disjoint from development.
- **Verify:** `python -m pccap.data.challenges --audit`.
- **Cost:** 4 h; GPU 15 min.

### 6.7 S1 — substrate report card (12 A100-h; week 1–2, parallel with S2)

Common rule: every row is computed for BP adjoints; ePC adjoints and ePC finite-iteration errors are added when REG-03 is done. A coverage matrix `results/S1/coverage.json` with `complete/pending/unsupported/unavailable` per (property, base, signal) is maintained by every S1 task.

**S1-01 — P1 fidelity** · METRICS+BASE · deps REG-03, DATA-04, S0-11 · review yes · GPU lease · PDF D.1
- **Steps:** ordinary `KL(p_T‖p_S)` per token on H at matched teacher-forced positions, feedforward and unclamped-after-8 (with zero-init the second equals the first: label the consistency check); mean, p95, p99, max finite; base task accuracy; argmax agreement on the development edit-prompt pool; initially-correct fraction per base on the BP-selected stream (no reselection); common initially-incorrect subset recorded as secondary. Reconcile with the sibling's 1.24e-4 figure and the PDF's inherited 3e-5 claim (state scalings).
- **Verify:** `pccap run --stage S1 --task P1 --manifest manifests/dev/s1.json` produces `results/S1/P1_{bp,epc}.json` validating against the metric schema.
- **Done when:** eligibility line written: both means ≤ 1e-3 → eligible for matched-fidelity claims, else ineligible (SE-A/SE-E still interpretable).
- **Cost:** 3 h; GPU ≤ 1 h.

**S1-02 — P2 geometry** · METRICS · deps S0-07, DATA-04, S0-04 (and REG-03 for ePC rows) · GPU short · PDF D.2
- **Steps:** per-layer effective rank on 4,096 centred positions with full spectra and seeds; POS linear probe (fixed, matched, disjoint train/eval); grammar latent probe for the grammar base; ratios to teacher when ePC exists; alert flags (rank ratio < 0.9; probe drop > 0.02) as alerts only.
- **Verify:** outputs `results/S1/P2_*.json` schema-valid; known-answer tests still green.
- **Cost:** 2 h; GPU 15 min.

**S1-03 — P3 localization and coverage** · METRICS+BASE · deps S0-05, S0-06, DATA-04 · GPU short · PDF D.3
- **Steps:** 1,000 sequences; mass per (layer, token) = squared adjoint norm (BP, ePC adjoint) or squared error norm (ePC finite errors) under the summed sequence loss; PR, nPR, distribution, final-block share, active fraction above 1% of the sequence max, zero fields, raw and layer-scale-normalized; dataset layer shares stratified by mechanism on the grammar. Final-block share > 0.4 → alert.
- **Cost:** 2 h; GPU 20 min.

**S1-04 — P4 separability** · METRICS · deps DATA-04, GRAM-02 · GPU short · PDF D.4
- **Steps:** per mechanism and layer, 8,192 centred vectors, top-r basis with r = 16 only if supported (else insufficient-rank case or common lower rank, labelled); overlap matrix, captured variance, eigen gaps, resampling stability; on the grammar: private/private overlap, shared retention, held-out compositional transfer (intervention checks come from S3). Natural-language domain PCA `unsupported` (DATA-04).
- **Cost:** 2 h; GPU 15 min.

**S1-05 — P5 write locality** · BASE+METRICS · deps S0-10, S2-01 (b_m), DATA-01 · GPU lease · PDF D.5
- **Steps:** Q = 200 edit prompts and U = 200 unrelated/near-neighbour prompts from the development pool (SD-2); at each site, unit direction under each credit rule; bounded geometric search (the CAP-06 grid at A = 0.1 scaled up to 8 doublings) for a 50% current-token loss reduction; achieved improvement, normalized write norm, unreachable cases; unconditional collateral `C_q` (mean KL over U under the same write) and actual gated-cap behaviour (firing rate, complete-answer changes) separately; ratio undefined at 0/0 and right-unbounded at positive/0. Retrieval-drift tracking: keys and firing slots on a fixed prompt set at saved checkpoints.
- **Cost:** 3 h; GPU ≤ 1 h.

**S1-06 — P6 finite settling and informativeness** · BASE+METRICS · deps S0-06 (BP weights suffice for the procedure; ePC rows need REG-03) · GPU lease · PDF D.6
- **Steps:** `E_0…E_64`, `r_8`, `r_64`, first iteration reaching 95% of `E_0 − E_64` (only when positive); 16-step optional; "settled" label only if `r_64 ≤ 1e-3` and terminal changes small, else "finite-iteration error credit"; error–loss Spearman (constant vectors undefined); actual reverse counts, runtime and query cost; cosine between settled errors and adjoints at the three sites (reproduces the inherited > 0.998 claim or not).
- **Cost:** 2 h; GPU ≤ 1 h.

**S1-07 — S1 report and D1 input** · INTEGRATOR+METRICS · deps S1-01…06 · review yes
- **Steps:** report per Appendix G with the validity/eligibility table (matched-fidelity claim, synthetic-only claim, BP-only editing), alerts separated from correctness, the coverage matrix, and the reconciliation of inherited claims.
- **Cost:** 2 h.

### 6.8 S2 — calibration, baselines, throughput (12 A100-h; week 1–2)

**S2-01 — Residual scales and radius calibration** · BASE+MEMORY · deps S0-10, DATA-01 · review yes · GPU lease · PDF S2 "Radius calibration", F.6
- **Steps:** `b_m` = median raw residual norm per site over cap-disabled development prefixes (floor 1e-8). For each bank (R-h): observed key distances between the 300 dev edit prompts and their paraphrases (coverage) and between edit prompts and the ≥ 1,000 unrelated prompts (false fire); 20-quantile grid; pick the largest radius with unrelated false-fire ≤ 1%, ties by paraphrase coverage; store every candidate. No positive radius → exact-key pilot with the limitation recorded and CR-4's interpretation (RET-GS still scores paraphrases).
- **Outputs:** `results/S2/residual_scales.json`, `results/S2/radius_calibration.json`.
- **Cost:** 2 h; GPU 20 min.

**S2-02 — Aggregate step screening** · MEMORY+METRICS · deps S2-01 · review yes · GPU lease · PDF S2 "Update numerics"
- **Steps:** A ∈ {0.03, 0.1, 0.3} only; C1, calibrated radii, ε = 0.01, R = 5, stop 0.1; on 100 development edits per dataset score immediate free-generation ES and the ≤ 1% false-fire locality criterion; choose one shared A (highest ES among candidates meeting locality; tie → 0.1); log every configuration. If none functions: ≤ 3 diagnoses with the cheapest discriminating test, no new sweep, no confirmatory data.
- **Outputs:** `results/S2/A_screening.json`, `docs/decisions.md` entry.
- **Cost:** 2 h; GPU ≤ 1 h.

**S2-03 — LoRA baselines B1 (and B0)** · BASELINES · deps S0-09, S0-04 · review yes · GPU short · PDF §8 Baselines, S2 "Baselines"
- **Steps:** own implementation (HF GPT-2 uses a fused `c_attn` Conv1D): rank-8 LoRA on the Q and V slices only, K untouched, all 12 layers; Adam lr 1e-4 (screen {3e-5, 1e-4, 3e-4} on development); 10 optimizer steps per complete edit (teacher-forced over the whole answer); one epoch per synthetic task; shared decoder; optimizer state counted in memory; B0 = frozen model with evaluation cost recorded.
- **Verify:** `pytest tests/baselines/test_lora.py -m gpu`: trainable tensor list is exactly the LoRA A/B for Q and V; original weights unchanged (checksum); K slice gradient is zero; a 10-step edit reduces teacher-forced NLL.
- **Cost:** 4 h; GPU 15 min.

**S2-04 — Replay baseline B3** · BASELINES · deps S2-03, S0-08 · review no · GPU short
- **Steps:** reservoir sampling over seen edits with ceiling min(5% of seen edits, `B_cap` bytes of stored items); one replay item per new item per step; rounding, RNG and item storage defined; replay buffer and optimizer state cloned in the snapshot and reported as total state.
- **Verify:** `pytest tests/baselines/test_replay.py` (reservoir statistics; restore equality; byte ceiling).
- **Cost:** 3 h; GPU 10 min.

**S2-05 — GRACE baseline B4 with parity** · BASELINES · deps DATA-00 (GRACE source), S0-09 · review yes · GPU short · PDF Op. rule 11, PC-10, SD-8, PA-6
- **Steps:** pin the GRACE commit; try to run its own smoke test in the project environment, else in a separate `uv` environment with its pinned torch (CPU acceptable); write `baselines/grace_adapter.py` for GPT-2 small (layer and radius chosen on development; 100 value steps initially; byte-bounded eviction adaptation per SD-8); PC-10: on 10 single-token and 10 multi-token shared development cases, the adapter and the reference produce the same edited outputs and memory contents within fp32 tolerance when the adaptation is disabled; document every intentional change.
- **Verify:** `pytest tests/controls/test_pc10_parity.py`.
- **Done when:** parity evidence exists, or after the PA-6 bound the record says `B4 comparison unavailable` with the reason.
- **Cost:** 6 h; GPU 20 min.

**S2-06 — Throughput profile** · INTEGRATOR · deps S2-01, S2-02, S2-03…05, CAP-08 optional · review yes · GPU lease (exclusive) · PDF S2 "Throughput"
- **Steps:** 100 complete development edits per dataset under C0, C1, C2, CR (uniform per SD-11), B1, B3, B4, and ePC credit when available; each including immediate ES/GS/LS evaluation, memory search, checkpoint save and a checkpoint rescoring pass; warmup/compile reported separately; operation counts and CUDA-event seconds per edit stratified by answer length; peak memory. Grammar: 100 items per router on the GRAM base.
- **Outputs:** `results/S2/throughput.json`.
- **Cost:** 2 h; GPU ≤ 2 h.

**S2-07 — Full cost projection and D1 memo** · INTEGRATOR+METRICS · deps S2-06, S1-07, ENV-02 · review yes · GPU none · PDF App. B "Stage ceilings", SD-5, PA-7
- **Steps:** `analysis/budget.py --project`: for each candidate scope (zsRE {300, 1000, 3000} × CounterFact {300, 1000} × grammar {256, 1024, 10000}), sum measured per-item learning cost × items × arms × 15 (realization × order), plus checkpoint rescoring at 100/300/1000/3000, endpoint retention, locality, LM drift, challenge evaluation, serialization; count shared teacher-reference production once; include the C0 initial scope (300) and mark its extension optional; add S5/S7 to their own ceilings. Select by the Section 9 algorithm. Write `docs/D1_decision.md`: eligibility, κ status, affordable scopes with the chosen one, open items with owners, and the week-2 queue.
- **Done when:** D1 memo filed; `manifests/tasks.json` updated; if no scope fits, T2 filed and the synthetic-only core continues.
- **Cost:** 2 h.

**CAP-08 — Read variants R-h0, R-g, R-e** · BASE+MEMORY · deps S0-10, S0-06 · review yes · GPU short · PDF F.4, PC-8 (optional, needed only for S5-03/S8-02)
- **Steps:** R-h0 from a cap-disabled pass; R-g = `[z(h⁰); z(g⁰)]/√2` with `g⁰` the adjoint of `CE(p⁰, argmax p⁰)`; R-e on ePC with the label-free pseudo-target and the query budget; identical key computation in learning and inference; zero auxiliary vectors normalized by the declared epsilon; every extra pass charged to the query; separate radius calibration per variant.
- **Verify:** `pytest tests/controls/test_pc8_labels.py -m gpu` (hidden-answer substitution leaves keys and predictions unchanged; state reset between queries; wide-key PC-6).
- **Cost:** 4 h; GPU 10 min.

**CAP-09 — Optional difficulty weight** · MEMORY · deps CAP-07 · review no · GPU none
- **Steps:** `w = max(0.1, 1/(1 + L̄_s/L_ref))`, `L_ref` fixed on development, new slots w = 1, weight inside every tested increment; off by default.
- **Verify:** PC-5 weighted-candidate identity test.
- **Cost:** 2 h.

### 6.9 S3 — BP mechanism screening (16 A100-h; week 2)

**S3-01 — Full control suite and development run matrix** · INTEGRATOR · deps S0-11, DATA-03, CAP-07, S2-05, DATA-06 · review yes · GPU short
- **Steps:** run every applicable PC-1…PC-10 test; write `results/S3/controls.md` (expected/observed/pass; applicability for optional keys); freeze the development matrix: one realization (dev), two orders; CR uniform (SD-11) for this stage's first pass.
- **Done when:** CP-D recorded; any failing control names the measurements it blocks.
- **Cost:** 2 h; GPU 20 min.

**S3-02 — Constructed fixture runs** · MEMORY+DATA · deps S3-01 · GPU short · PDF S3, D.10
- **Steps:** C0/C1/C2/CR/CO on MODULAR-CONTROL (all three variants); oracle success (gate), private/shared/mixed transfer and harm, wrong-router control, C2 delivery precision/recall against `R*` with bootstrap intervals, majority-bank baseline, per-latent confusion matrices; multi-cause coverage.
- **Cost:** 2 h; GPU 15 min.

**S3-03 — Learned grammar runs and tracing** · DATA+METRICS · deps S3-01, DATA-07 · GPU lease
- **Steps:** C0/C1/C2/CR on the grammar (dev realization, two orders, training count 1024 provisional); joint-training reference; D.7 matrix, held-out combinations; tracing scores with all site cases retained.
- **Cost:** 3 h; GPU ≤ 2 h.

**S3-04 — Short editing checks** · BASELINES+MEMORY · deps S3-01 · GPU lease
- **Steps:** 100-edit development streams per dataset for C0/C1/C2/CR/B1/B3/B4 under the common decoder; routes, probes/searches, collisions, drift, evictions, abstentions and allocations logged; proposed routes, accepted writes and acquired complete answers reported separately.
- **Cost:** 2 h; GPU ≤ 2 h.

**S3-05 — CR distribution and re-profile** · METRICS+INTEGRATOR · deps S3-02…04 · review yes
- **Steps:** estimate CR bank probabilities from development C2 accepted routes only (counts per bank over accepted deliveries; abstentions excluded from the normalizer but reported); if C2 never routes, uniform (SD-11); record in `manifests/cr_distribution.json`; re-run the S2-06 CR profile if the bank mix changes projected cost by > 10%.
- **Cost:** 1 h; GPU ≤ 30 min.

**S3-06 — D2 memo** · INTEGRATOR · deps S3-05, S1-07 · review yes
- **Steps:** `docs/D2_decision.md`: correctness versus science for every failure (≤ 3 diagnoses, cheapest test), core feasibility, S6 deficit recommendation (yes/no with the deficit statement draft), freeze readiness checklist.
- **Cost:** 2 h.

### 6.10 S4 — freeze and confirmatory BP runs (36 A100-h; weeks 2–3)

**S4-01 — Frozen manifest** · INTEGRATOR · deps S3-06, DATA-02, DATA-08, S2-07 · review yes · GPU none · PDF Op. rule 4, S4
- **Required fields (schema-enforced):** `code_commit, env_lock_sha, pdf_sha, base_checkpoints{bp,epc?}, tokenizer_rev, bank_sites, radii{bank,read}, b_m, A, epsilon, R, tau_edit, byte_ceiling, slot_capacities, cr_distribution, dataset_ids{zsre,counterfact,grammar}, realizations, order_seeds, cap_seed, router_seed, replay_seed, stream_lengths{zsre,counterfact,grammar_train_count}, arms[], contrasts[] (ordered), primary_endpoint=RET-GS, margins{ret_gs:0.02, es:-0.02, ls:-0.01}, interval{method:paired-cluster-bootstrap, draws:10000, level:0.975}, checkpoints[100,300,1000,3000], challenge_policy, resource_rules{headroom:0.25, kappa, stop_boundary}, analysis_code_commit, negative_case_interpretation, spec_defect_resolutions[]`.
- **Verify:** `pccap run --mode confirm --manifest manifests/frozen.json --dry-run` succeeds and `pytest tests/analysis/` (frozen analysis code tested on synthetic tables) passes.
- **Done when:** CP-E logged; `manifests/frozen.json` hash committed; the analysis module hash matches.
- **Cost:** 3 h.

**S4-02 — Scope selection** · INTEGRATOR · deps S4-01 inputs · review yes
- **Steps:** apply Section 9's algorithm with the S2-06/S3-05 measurements; write the chosen scope into the frozen manifest before any confirmatory access; C0 initial editing scope = 300 with the extension optional.
- **Cost:** 1 h.

**S4-03 / S4-04 — Confirmatory run schedule and execution** · run owner · deps S4-01 · GPU lease (serialized queue)
- **Steps:** generate the job list: grammar C0/C1/C2/CR × 15; zsRE and CounterFact C1/C2/CR/B3/B4 × 15 each, C0 × 15 at the initial scope; B0/B1 curves where already available. Execute via `pccap run --mode confirm` in a fixed order (realization-major, arm-minor) independent of observed results; hash the base before and after each run; save learner checkpoints at 100/300/1000/3000 and the endpoint; record immediate ES/GS, retention (unconditional and conditional survival), LS (complete-answer agreement, first token, fixed-prefix KL), LM drift (perplexity ratio and mean loss difference), strata, memory and cost; on a resource stop roll back the incomplete item and charge it. `pccap status` shows completed pairs.
- **Done when:** every scheduled job has a result directory with `status ∈ {complete, resource_stop, correctness_failure}`; no imputation.
- **Cost:** GPU ≤ 36 A100-h ÷ κ.

**S4-05 — Resource views** · METRICS · deps completed pairs
- **Steps:** exposure-matched and time-matched tables; retention versus items and versus accelerator seconds; longest common completed prefix per contrast; comparable-compute eligibility (update time within 20% or resource-matched support).
- **Cost:** 2 h.

**S4-06 — Frozen paired analysis and D3 audit** · METRICS+INTEGRATOR · deps S4-05 · review yes · PDF D.11
- **Steps:** `analysis/paired.py` from the frozen commit: per realization/order paired differences for C2−C1 and C2−CR on endpoint RET-GS, averaged over orders within realization; 10,000-draw paired cluster bootstrap over the three realizations keeping their five orders together; 97.5% two-sided intervals; constraints (ΔRET-GS ≥ 0.02 and lower bound > 0; ES lower bound > −0.02; LS lower bound > −0.01) reported even after a failure; classification positive / qualified / inconclusive / negative; per-item lost sets. D3 coverage and cost audit; any post-freeze bugfix creates a manifest version and reruns affected pairs or marks them incomplete.
- **Cost:** 3 h.

### 6.11 S5 — representation and credit (24 A100-h; week 3; conditional on REG-03)

**S5-01 — Eligibility and arm definition** · BASE+INTEGRATOR · deps S4-01, S1-07, REG-03
- **Steps:** SB (BP, adjoint), SE-A (ePC, adjoint), SE-E (ePC, 8-iteration error credit), all with C1, R-h, identical radii calibration per base/read, matched streams, byte ceilings and write policy; natural-language eligibility from S1-01; else synthetic-only with BP editing separate.
- **S5-02 — Execution:** paired streams on the frozen scope; reuse of the S4 SB/C1 run only when every frozen field matches (record provenance; charge shared production once).
- **S5-03 — Optional (only if D3 budget allows):** C2 substrate repeats; R-h0; R-e versus R-h and same-dimensional ePC R-g; BP R-g if a cross-base claim is made.
- **S5-04 — Report:** all paired outcomes, eligibility limits, cost frontiers; no independent-replicate language.
- **Cost:** GPU ≤ 24 A100-h ÷ κ.

### 6.12 S6 — conditional matched re-distillation (20 A100-h minus REG amendment)

Runs only if S3-06 recommends a deficit **and** the remaining S6 allocation covers both arms plus evaluation. Tasks S6-01…S6-05 are as in plan2 with these additions: S6-03 must replace the sibling's detaching `relax_errors` with a `create_graph=True` path for regularizers through error features and pass a finite-difference test showing the regularizer changes parameter gradients; S6-04 runs EPC-CONT and EPC-REG from the same state, tokens, schedule and KD mass; S6-05 evaluates P1–P6 on both and keeps cap tests exploratory. If REG-02 consumed part of the allocation, the remaining hours bound both arms; if insufficient, S6 is skipped with the reason logged.

### 6.13 S7 — order effects (10 A100-h; weeks 3–4)

**S7-01/02 — Cloned-state reversals and damage matrix** · METRICS · deps S4-04 checkpoints, frozen probe manifest · GPU lease
- **Steps:** at selected immutable checkpoints (300-edit endpoint per dataset; grammar end of task 4 and 8), 100 fixed pairs stratified shared/private/near-neighbour from independent data; clone complete state; run `U_j(U_i(s))` and `U_i(U_j(s))` with item-keyed randomness; `D_ij` mean JS over the fixed evaluation set Q; per-item accuracy changes, update counts, allocations, evictions; `I_ij` damage matrix in both orders with strata.
- **S7-03 — Order variation from permutations:** ACC std across orders, pairwise JS and disagreement at identical prefixes, lost-item sets; PR-E descriptive table.
- **S7-04 — Optional HVP diagnostics:** only after exact small-matrix tests (Gram PSD/sign, loop `I − η²C`, full block sum) pass; frozen topology; 16 Rademacher probes; not the sibling's error-energy HVP.
- **Cost:** GPU ≤ 10 A100-h ÷ κ.

### 6.14 S8 — replication, ablations, report (16 A100-h; week 4)

**S8-01 — Core completion and reproduction audit** · INTEGRATOR+METRICS: finish missing preregistered pairs first; reproduce two completed runs from clean state (identical decisions); audit exclusions, ledger totals, base hashes, failed controls, post-freeze changes.
**S8-02 — Fixed exploratory ablations** (list frozen at S4-01 from development failure mechanisms; 3 realizations × 2 orders; labelled exploratory): R-h0 vs R-h; half and double `B_cap`; difficulty weight; R-e vs R-g if built. Dropped before any core pair.
**S8-03 — Integrated report** via `pccap report --final`: P1–P6, routing, representation/credit, acquisition/retention/locality, transfer/order, frontiers, uncertainty, failure and deviation tables; every claim mapped to its contrast; no cap-level PC, causal-origin or independent-replicate claims.
**S8-04 — Handoff package:** `docs/REPRODUCE.md` with tested commands (environment, controls, asset verification, stage runs, resume, report), artifact index, licences and provenance, remaining work in priority order; a small end-to-end run reproduced from the package. Push; T4 filed.
- **Cost:** GPU ≤ 16 A100-h ÷ κ; two working days reserved for overruns.

---

## 7. Control register

All evidence lives under `results/S0/controls/` (later stages reference it). Each row names the test file that is the evidence.

| Control | Test file(s) | Cases | Due gate | Blocks if failing |
| --- | --- | --- | --- | --- |
| Numerical known answers | `tests/known_answer/*` | rank, PR, overlap, JS, D.7 table, scalar η² order effect | CP-B | every S1 measurement using the metric |
| PC-1 planted acquisition | `tests/controls/test_pc1_planted.py` | ≥ 19/20 targets; full fixture ≥ 95%; unrelated ≤ 1e-6 | CP-D | S3-02 |
| PC-2 identity | `tests/controls/test_pc2_identity.py` | 256-probe cap-off equality; oracle-false gate | CP-C | everything |
| PC-3 idempotence | `tests/controls/test_pc3_idempotence.py` | 20 repeated threshold-fitted edits, no new slots | CP-D | S3-04, S4 |
| PC-4 conflicts/revisions | `tests/controls/test_pc4_conflict.py` | distinct, identical, newer version, replay, failed rollback | basic at CP-C, full at CP-D | S3-04, correction track |
| PC-5 probe/search | `tests/controls/test_pc5_probe.py`, `test_pc5_search.py` | signed scores, nonmonotone, exact candidate, rollback, weighted identity | CP-C | C2 and all cap learning |
| PC-6 budgets | `tests/controls/test_pc6_budget.py`, `tests/cap/test_memory.py` | equal ceilings, overhead, wide keys, aggregate increment, eviction, use-count once | CP-C; repeat per variant | all arms |
| PC-7 complete answers | `tests/controls/test_pc7_complete_answers.py` | wrong second token; teacher-forced vs generation; terminators | CP-B | all editing metrics |
| PC-8 isolation/read-only | `tests/controls/test_pc8_readonly.py`, `test_pc8_labels.py` | state hash after predict/decode; hidden-answer substitution for R-g/R-e | CP-C (R-h); before CAP-08 use | evaluation validity; optional keys |
| PC-9 cloning/randomness | `tests/controls/test_pc9_cloning.py`, `tests/test_reproducibility.py` | clone equality, replay, reversal start, item-keyed CR, scalar order effect, resource-stop rollback | CP-C; full before S7 | S7, all confirmatory |
| PC-10 parity | `tests/controls/test_pc10_parity.py` | GRACE single/multi-token parity, documented deviations | CP-D | B4 comparison |
| Sign convention | `results/S0/controls/sign_convention.json` | analytic descent direction, recorded once | CP-C | all credit |
| Frozen base | every run's `base_hash_{before,after}` | equality | every run | that run |

---

## 8. Schedule and critical path

Working days are counted from D0 = the first day this plan is executed (not a calendar date; record D0 in `docs/decisions.md`). Five working days per week; no weekend labour assumed. Agent concurrency: up to four task agents; one GPU lease.

| Window | Parallel lanes (one agent each) | Join |
| --- | --- | --- |
| D0 | ENV-01 → ENV-03 → ENV-04 (INTEGRATOR) · DATA-00 (DATA) · S0-01 after both · ENV-02 after DATA-00 | CP-A: environment, assets, lead queue T1 |
| D1–D2 | S0-03, S0-08 (INTEGRATOR) · S0-04 → S0-05 → S0-06 (BASE) · CAP-01 → CAP-02 → CAP-03 → CAP-04 (MEMORY) · S0-07, S0-09 (METRICS/DATA) | CP-B: contracts, wrapper, metrics, decoder |
| D3–D4 | CAP-05 → CAP-06 → CAP-07 → S0-10 (MEMORY+BASE) · DATA-01, DATA-04 (DATA) · GRAM-01 (DATA, second agent) · S2-03/S2-05 reference smoke (BASELINES) | CP-C: four invariants, S0-11 report |
| D4–D6 | S2-01 → S2-02 (MEMORY) · S1-02/03/04/06 on BP (METRICS) · GRAM-02, DATA-06, DATA-07 (DATA) · S2-04, S2-05 parity (BASELINES) · REG-01 → REG-02 when PA-1 fires (BASE, GPU overnight) | — |
| D6–D8 | DATA-03, DATA-08, DATA-02 (DATA) · S1-05 (BASE) · S2-06 exclusive GPU · REG-03 → S1-01, ePC rows of S1-03/S1-06 (BASE/METRICS) · CAP-08 (optional) | CP-D / D1: S1-07, S2-07 memos |
| D8–D10 | S3-01 → S3-02/03/04 → S3-05 → S3-06 | D2 |
| D10–D11 | S4-01, S4-02 (INTEGRATOR) · S5-01, S6-01 decision (BASE) · analysis code tests (METRICS) | CP-E freeze |
| D11–D16 | S4-03/04 job queue on the GPU lease (run owner) · S5-02 interleaved when eligible · S6 only if authorized and affordable · S7-01/02 on committed checkpoints as they appear (METRICS) · S4-05 incremental | D3 at D16 |
| D16–D19 | S4-06, S5-04, S7-03/04 (METRICS) · S8-01 core completion, S8-02 ablations (run owner) · S8-03 report drafting | — |
| D19–D20 | S8-03 final, S8-04 handoff, push, T4 | CP-F |
| D21–D22 | Reserved buffer (PDF: two working days) | — |

**Critical path:** ENV-01 → S0-04 → S0-05 → CAP-05 → CAP-06 → CAP-07 → S0-10 → S2-01 → S2-02 → S2-06 → S2-07 (D1) → S3-01 → S3-05 → S4-01 → S4-04 → S4-06 → S8-03. Everything else has slack of at least one day. The GPU is the binding resource from D11 onward; all CPU-side analysis and report drafting proceeds in parallel.

**Slip rule.** If a gate slips, the orchestrator re-dates the downstream windows in `docs/tasks/STATUS.md` and states the effect on freeze and confirmation; it never compresses realizations, orders or contrasts to recover time.

---

## 9. Budget, conversion, and the scope-selection algorithm

| Stage | A100-eq ceiling | Local ceiling at κ = 1 (PA-3) | Reassignable |
| --- | ---: | ---: | --- |
| S0 | 8 | 8 h | no |
| S1 | 12 | 12 h | no |
| S2 | 12 | 12 h | no |
| S3 | 16 | 16 h | no |
| S4 | 36 | 36 h | no |
| S5 | 24 | 24 h | to core replication by logged amendment if ePC ineligible |
| S6 | 20 | 20 h minus REG-02 (≤ 10 h) | unused → core replication by logged amendment |
| S7 | 10 | 10 h | no |
| S8 | 16 | 16 h | no |
| Total | 154 | 154 h | never increases silently |

`results/ledger/stages.json` holds local CUDA-event seconds per stage; the report shows local hours, κ, and the band.

**Prior per-run estimate (to be replaced by S2-06; used only to set expectations).** With C2 on GPT-2 small: per token prefix about one forward, one reverse, three probe partial forwards and up to four candidate partial forwards per round, five rounds, average six prefixes per edit → roughly 250 forward-equivalents per edit for learning; plus immediate evaluation by greedy 32-token no-cache decoding over the edit prompt, its paraphrases and locality prompts. At a few milliseconds per short-prefix forward this is seconds per edit, so a 300-edit run including endpoint rescoring is on the order of 10–20 minutes, and the ~150 confirmatory editing runs plus 60 grammar runs are on the order of 40–60 local GPU-hours. Expectation: the 300-edit prefixes fit S4 (possibly with the C0 extension dropped), 1,000 is marginal, 3,000 does not fit. This is not a measurement.

**Scope-selection algorithm (S4-02; PA-7).** Inputs: `throughput.json` (per-item learning seconds by arm and dataset, evaluation seconds per prompt, checkpoint save/rescore seconds), the frozen arm list, κ.

```
for zs in [3000, 1000, 300]:
  for cf in [1000, 300]:
    for gr in [10000, 1024, 256]:
      cost = Σ_arms Σ_datasets 15 × [items × learn_s + rescoring(checkpoints ≤ items) + endpoint_eval + drift_eval + challenge_eval + save]
             + grammar: 4 arms × 15 × gr × learn_s + evals
             + C0 initial 300 on both datasets × 15
      if cost ≤ 0.75 × (36 h × 3600 / κ): select (zs, cf, gr); stop
if nothing selected:
  if grammar-only core (4 arms × 15 at gr=256) ≤ 0.75 × ceiling: select grammar-only; file T2 with the editing feasibility result
  else: file T2; run nothing confirmatory
```

The selected scope is written into `manifests/frozen.json` before any confirmatory access. Optional work (C0 extension, R-e/R-g, S6, HVP, S8-02) is funded only from remaining allocation after the core is complete (D3).

---

## 10. Decision points with pre-committed outcomes

| Decision | Inputs | Pre-committed outcome |
| --- | --- | --- |
| D1 validity/feasibility (S2-07) | S1-07 eligibility, S2-06 throughput, κ | Base eligibility recorded per claim type. If ePC absent: "unavailable, not failed"; S5 pending REG. Scope by Section 9. Alerts trigger their named diagnostic, no number changes. |
| D2 implementation vs science (S3-06) | control suite, S3 runs | Failed control → affected mechanism paused, ≤ 3 diagnoses, cheapest test, repair within development budget. Correct C2 that routes poorly → proceeds to the frozen bounded negative-result evaluation. Beating LoRA is not a gate. S6 deficit statement written only if a reproducible deficit and an affordable pair exist. |
| CP-E freeze (S4-01) | everything above | No confirmatory access before the manifest hash is committed. Missing required field → the CLI refuses to run. |
| D3 scope audit (S4-06) | completed pairs, ledger | Drop order: HVP → R-e/R-g → S6 → S8-02 ablations → C0 extension → (T3) a core pair. Never the endpoint, margins, realizations or orders. |
| Post-freeze bugfix | any | New manifest version; old results retained; affected pairs rerun if affordable, else marked incomplete. |
| Near-threshold result | S4-06 | No added seeds. Classify as inconclusive if the interval spans benefit and harm; recommend a planned independent replication. |

---

## 11. Risk register

| Risk | Evidence now | Contained consequence and owner |
| --- | --- | --- |
| No `sm_120` wheel at the pinned torch version | Blackwell needs cu128+; sibling pinned 2.11.0+cu128 | ENV-01 records the actual wheel; a newer cu128/cu130 stable wheel is a logged deviation; CPU fallback for S0 tests. INTEGRATOR |
| ePC checkpoint never located and regeneration exceeds 10 h | Recipe exists; pilot projects | PA-1 bound; if projection > 10 h, ePC stays unavailable and the month is BP-only for Thread 1 rows; report says so. BASE |
| Regenerated checkpoint fails P1 | Sibling reported 1.2e-4 with its scaling | Ineligible for matched-fidelity claims; SE-A/SE-E still run; matched-fidelity superiority not claimed. METRICS |
| Eight-step credit is uninformative for a one-step-trained model | Production `relaxation_steps=1` | Measured in S1-06; label "finite-iteration error credit"; a low error–loss association is a result. BASE |
| No positive radius meets 1% false-fire | Unknown until S2-01 | Exact-key pilot; CR-4 interpretation; per-bank diagnosis; no per-arm tuning. MEMORY |
| No A candidate acquires | Unknown until S2-02 | Diagnosis with decision records; no new sweep; lead queue only if a protocol change is proposed. MEMORY |
| GRACE reference incompatible with torch 2.11/transformers 5 | Likely (older code) | PA-6 separate environment; CPU parity; after 4 days, B4 unavailable. BASELINES |
| transformers 5.13 GPT-2 internals differ from expectations | Sibling pins it; not tested here | S0-04 tests compare against HF outputs and hooks rather than assuming the tuple layout. BASE |
| Scope does not fit S4 | Prior estimate says 300 fits, 3,000 does not | Section 9 algorithm; T2 only if nothing fits. INTEGRATOR |
| zsRE composition challenge cannot reach 100 unambiguous cases | Dataset structure | Report the count as `unsupported` beyond what exists; other challenge sets unaffected. DATA |
| E.4 natural-language domain sets | Not available for GPT-2 small this month | `unsupported`; grammar mechanisms substitute per PDF E.4. DATA |
| Two clones / concurrent agents diverge | `/home/derp/pc_cap` exists | Working clone fixed; worktrees; path ownership; orchestrator merges. INTEGRATOR |
| GPU contention corrupts throughput | Desktop processes use ~2 GiB | Lease with exclusivity for profiles; `nvidia-smi` capture before/after; other jobs serialized. INTEGRATOR |
| Desktop process OOM at 12 GiB | teacher + student + LoRA/optimizer at batch ≤ 8 | Batch sizes fixed small; peak memory recorded; any OOM is `resource_stop`, never a silent batch change. run owner |
| Licensing for release | Sibling has no root licence | Record; no redistribution of sibling code; T4 before any release. INTEGRATOR |

---

## 12. Deliverables and handoff

Stage reports `results/S{0..8}/report.md` follow Appendix G's ten sections (plan2 §11 lists them). The final deliverable set:

1. `results/S8/integrated_report.md` (and PDF) with the substrate report card, controlled routing results, representation/credit results, resource frontiers, order-effect diagnostics, all deviations and failures, and per-claim contrast mapping.
2. `docs/REPRODUCE.md` with tested commands: environment (`uv`), `make test`, `python -m pccap.data.fetch --verify`, every stage's `pccap run` invocation, resume, `pccap report`.
3. `manifests/` (assets, datasets, dev, confirm with hashes, frozen, cr_distribution, tasks) and `docs/{spec_defects,decisions,lead_queue,environment,epc_energy,D1_decision,D2_decision}.md`.
4. `results/ledger/` totals against ceilings with κ and its band.
5. `docs/tasks/STATUS.md` showing every task `done`, `partial` (with what is missing), or `blocked` (with the blocker), including unscheduled and failed work.

Final acceptance is reproducible controlled evidence with explicit limitations, including a useful negative or feasibility answer. It does not require that C2 or ePC wins.

---

## Appendix: first commands for the orchestrator

```bash
cd /home/derp/cap/pc_cap
# ENV-01
uv python install 3.11 && uv venv --python 3.11 .venv
.venv/bin/python -m pip install --index-url https://download.pytorch.org/whl/cu128 torch==2.11.0
.venv/bin/python -c "import torch;print(torch.__version__, torch.cuda.get_arch_list())"
# then the remaining pins, uv pip compile, docs/environment.md
# ENV-03
mkdir -p src/pccap tests manifests results docs/tasks docs/pdf_text data/raw
pdftotext -layout docs/pc_cap_month_plan_readable.pdf docs/pdf_text/plan.txt
# dispatch: for each task with status ready in manifests/tasks.json → worktree → agent (Section 4.6)
```
