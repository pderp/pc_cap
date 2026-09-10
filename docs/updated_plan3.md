# Updated Plan 3: course corrections after D0–D1 (delta to updated_plan2.md)

Prepared 2026-09-10 from the execution record (`docs/tasks/*.md`, `docs/decisions.md`,
`docs/spec_defects.md`, `results/S{0,1,2}/report.md`, `logs/interim_report1.md`). This file
**amends** [updated_plan2.md](updated_plan2.md); it does not replace it. Everything not listed
here stands as written there. The PDF remains the scientific contract: no threshold, endpoint,
arm definition or budget changes below.

## 0. Why a delta is needed

Execution exposed five kinds of change relative to updated_plan2.md: (1) lead directives at
D0 that replace the planned PyTorch stack and the agent protocol; (2) assets that the plan
assumed and that do not exist; (3) measured facts that resolve open choices (radii, A, the
zsRE baseline behaviour); (4) specification gaps found while implementing (SD-13…SD-17); and
(5) new tasks that the new stack requires (REF-01, REG-00, DATA-02a, ANA-01, S0-07b). Each is
listed with its consequence for the remaining weeks.

## 1. Directives that override updated_plan2.md (already in force)

| ID | Directive | Effect on the plan text |
| --- | --- | --- |
| DEC-001 | All GPU code is JAX in the pre-existing venv (`/home/derp/cap/venv`, Python 3.12, jax 0.11.1, fabricpc 0.5.2). No PyTorch. | ENV-01 §6.1: the 3.11 + torch recipe is void. S0-04/S0-09 "equal to HF" assertions become stored-oracle comparisons (SD-14, REF-01). PDF App. B's "PyTorch handles the cap" is a logged deviation (SD-13). |
| DEC-002 | Predictive-coding functionality is built on FabricPC plus pc_cap infrastructure. | S0-06 implements `GPT2BlockNode`/`TokenCrossEntropyEnergy`/`EPCInference` in `pccap.pc`; FabricPC 0.5.2 has no error-optimization solver of its own. |
| DEC-003 | The sibling and FabricPC are read-only reference material; no runtime import, no copied files. | ENV-04 is a reference recorder; PA-1 regeneration needs a JAX distillation driver (REG-00, SD-15); the plan's "sibling fast tests" line is `unsupported`. |
| DEC-004 | Only code, logs and docs in `pc_cap/`; every other resource under `/home/derp/cap/assets/`. | `data/raw`, `data/models`, `third_party`, learner checkpoints and large prepared arrays live under `assets/` with hashes in `manifests/`. |
| DEC-005 + commit policy (2026-09-10) | Worktrees under `pc_cap/.worktrees/`; **no agent commits, merges or pushes** — the lead commits. | §4.2 steps 5–8 of updated_plan2.md (commit on branch, orchestrator merges) are replaced by: record in `docs/tasks/<ID>.md`, leave changes uncommitted, orchestrator reviews and applies; the lead commits. PA-8 is withdrawn. |

## 2. Assets: what exists, what does not, and what replaces it

| Asset (PDF §3.1) | Status (S0-01, 2026-09-09) | Course |
| --- | --- | --- |
| ePC production checkpoint `4f0c23aa…` + resume state | absent everywhere reachable | T1 filed; PA-1 clock ends 2026-09-11 23:59 ET. Regeneration requires **REG-00** (JAX re-implementation of the sibling's homotopy distillation; DEC-006 corrects the regime: T ∈ {1,2,4,8,16,32,64}, not one step) → REG-01 pilot → REG-02 within the **120 local GPU-h bound of DEC-014** (2026-09-10 lead decision; superseding the ≤ 10 h line of this table's first version). The pilot's timing probe projects ≈ 11 h at micro-batch 5 on the RTX 5070 (results/REG/timing_probe.json); the regeneration runs on the orchestrator lane in resumable chunks and Thread 1's ePC rows are re-measured on the new checkpoint (S1-01, ePC rows of P3/P5/P6, S5). |
| BP teacher GPT-2 small | verified | unchanged |
| R8/R9 six-layer grammar | absent | PA-2 replacement (GRAM-01/02), labelled "replacement fixture, no continuity" |
| causal-fibres v0.3, comcrit, RelaLeap | absent | optional; `unavailable`; S7-04 uses S0-07b's own small-matrix controls |
| refs [2], [5] | no link | unavailable |
| WikiText-103 validation | 247,289 tokens | drift set = whole split (SD-3, PA-5) |
| HF PyTorch reference | not in the project env | **REF-01** (new task, Lane A): CPU torch env under `assets/envs/`, stored oracle fixtures `assets/reference/gpt2/` |

## 3. Measured facts that fix development choices

| Quantity | Plan expectation | Measured | Consequence |
| --- | --- | --- | --- |
| GPU matmul precision | fp32 | JAX default is TF32 on Blackwell | `pccap` forces `highest` (DEC-007) |
| Shared workload | unknown | 19.7k tokens/s fwd+bwd (B 8×128); 1.6–2.1 ms batch-1 forward; κ = 1 provisional | ENV-02; throughput projection (S2-06) will be cheap |
| b_m (median residual norms) | S2-01 | 70.7 / 106.6 / 425.6 | frozen input for S4 |
| Radii (R-h) | one per bank per base/read | zsRE 0.28/0.41/0.19 (87% coverage, 0% false-fire); **CounterFact none admissible** → exact-key pilot | **SD-17**: radii per (base, read, dataset), shared across arms. CounterFact paraphrase generalization via retrieval is 0 by construction; CR-4 interpretation; RET-GS still scores paraphrases. |
| Aggregate step A | screen {0.03, 0.1, 0.3} | 0.3 (ES 1.00/1.00; 0.1: 0.97/1.00; 0.03: never reaches τ) | **DEC-012: A = 0.3** for every confirmatory cap arm |
| zsRE teacher baseline | "real edits" filter | GPT-2 small emits an immediate newline on 294/300 dev questions | every zsRE item is a "real edit"; immediate ES on zsRE is acquisition from an empty answer; retention/paraphrase/locality carry the weight (S3/S4) |
| CounterFact teacher | — | 0 teacher-correct (counterfactual targets) | filter has no effect there |
| S0 cost | 8 A100-h ceiling | 0.41 local GPU-h | large headroom; the 300-edit confirmatory scope is very likely affordable (S2-06/S2-07 will confirm) |
| ePC solver on BP weights | "settled" at 8 steps? | r₈ ≈ 0.40, r₆₄ ≈ 0.10 | label "finite-iteration error credit" (D.6) |

## 4. Specification defects added (all committed, to be frozen at S4-01)

SD-13 framework line vs lead directive; SD-14 HF equality → stored oracle (≤ 1e-3 abs, argmax
agreement); SD-15 PA-1 via a JAX re-implementation; SD-16 C2 tie rule = smallest bank index;
SD-17 radii per dataset. DEC-008 (zero-matrix rank encoding) and DEC-009 (ANA-01
classification policy incl. `negative`, to be copied verbatim into `frozen.json`) are rulings
on Lane B's deliverables.

## 5. Revised task queue for the remaining weeks

Tasks done at writing: ENV-01..04, DATA-00, DATA-01, DATA-04, S0-01, S0-03..S0-11, CAP-01..07,
S0-07, S0-07b, ANA-01, S1-02, S1-03, S1-05, S1-06, S2-01, S2-02; S1-07 partial; REF-01 fixtures
generated (pending integration). Board: `docs/tasks/STATUS.md`.

**Added tasks** (specs in `docs/ongoing.md` / `docs/ongoing2.md`):
REF-01 (HF oracle fixtures), REG-00 (JAX distillation driver), ANA-01 (frozen analysis code,
brought forward), S0-07b (HVP small-matrix controls), DATA-02a (sealed-confirmation loader
before the data exists), S2-05a/b (GRACE reference env and parity cases).

**Re-sequenced critical path** (BP programme; ePC rows attach only if REG-03 happens):

```
S3 harness: C2 probe binding in pccap run (orchestrator, now)
  → S2-03 LoRA B1/B0, S2-04 replay B3 (BASELINES lane)       → S2-05 GRACE B4 (PA-6 bound)
  → DATA-03 MODULAR-CONTROL + PC-1 (FIXTURES lane)            → S3-01 controls + dev matrix
  → GRAM-01/02 + DATA-06/07 (PA-2 clock 2026-09-11)           → S3-02/03/04 → S3-05 CR distribution → S3-06 D2
  → S2-06 throughput (exclusive lease) → S2-07 D1 memo (needs S1-07, ENV-02)
  → DATA-08 challenge sets → DATA-02 sealed manifests (DATA-02a code first)
  → S4-01 freeze (frozen.json with DEC-009 text, SD-13..17) → S4-02 scope → S4-03/04 runs → S4-05/06 → S7 → S8
```

**Dropped or deferred unless REG-03 lands:** S1-01 (P1), ePC rows of S1-03/05/06, S5 in full,
S6. D1 will record "ePC unavailable, not failed" and S5's allocation becomes reassignable to
core replication by logged amendment (plan §9). If the T1 answer locates the checkpoint, REG-03
runs immediately and the ePC rows rejoin without code changes (`EPCBase.from_npz` / `params_np`).

**Schedule effect.** D1 (S2-07) slips from D6–D8 to whenever S2-06 and the baselines exist
(the baseline lane has not been claimed); everything else on the BP critical path is ahead of
the §8 windows. The freeze (S4-01) still targets week 2–3; no compression of realizations,
orders or contrasts.

## 6. Agent protocol changes (effective)

- No commits by agents (lead directive). Records + uncommitted worktrees. `docs/ongoing2.md` §2
  is the live lane list; claim by editing your own row of `manifests/tasks.json`.
- Reviewer pass remains required for `review: yes` tasks before the orchestrator applies them.
- GPU lease unchanged (`results/.gpu_lease`); bulk jobs queue on it with `flock` semantics.

## 7. Open risks added to the §11 register

| Risk | Evidence | Containment |
| --- | --- | --- |
| CounterFact exact-key gate gives GS = 0 from retrieval | S2-01 | Report per CR-4; R-h0/R-g ablations (CAP-08) may be motivated as development diagnostics, never as confirmatory tuning |
| Baselines lane unclaimed → D1 waits | board | orchestrator takes S2-03/04 after the C2 harness binding if still unclaimed |
| REG-01 projection > 120 h (DEC-014 bound) | timing probe projects ≈ 11 h | BP-only month; S5 allocation reassigned by amendment. Not triggered. |
| zsRE empty-baseline inflates immediate ES | DATA-01 | immediate ES reported with the baseline note; endpoints are RET-GS and locality |
