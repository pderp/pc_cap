# Interim report 1 — pc_cap execution, D0 to D1 (2026-09-09 → 2026-09-10)

Scope: everything done so far by the orchestrating Claude session and by the second agent
("codex") under [docs/updated_plan2.md](../docs/updated_plan2.md), with the lead's directives
of D0 and D1. Sources: `docs/tasks/*.md` (38 task records), `docs/decisions.md` (DEC-000…012),
`docs/spec_defects.md` (SD-1…17), `results/S{0,1,2}/report.md`, `manifests/tasks.json`,
`results/ledger/`. Companion: [docs/updated_plan3.md](../docs/updated_plan3.md) (course
corrections). Nothing in this report is a confirmatory finding: every number below is a
development measurement or an implementation control.

---

## 1. Headline status

| Item | State |
| --- | --- |
| Tasks done / partial / pending (of 85 on the board) | 33 / 1 / 51 |
| Stage checkpoints | CP-A (assets, T1 filed), CP-C (S0 complete) recorded; D1 memo not yet (needs S2-06 throughput and baselines) |
| Tests | 226 CPU tests pass (3 skipped: GPU-dependent variants), 36 GPU tests pass (1 skipped slow), plus 8 reference-env tests (codex) |
| Code | 81 Python modules under `src/pccap` (≈7,500 lines), 47 test files (≈3,200 lines) |
| GPU used | 0.92 local RTX 5070 hours total (S0 0.41, S1 0.18, S2 0.33) against 32 A100-eq hours allotted to S0–S2 (κ = 1 provisional) |
| Human touchpoints open | T1 (locate the ePC checkpoint, grammar, causal-fibres, comcrit, RelaLeap, refs [2]/[5]); PA-1/PA-2 clocks end 2026-09-11 23:59 ET |
| Commit state | all work since the lead's instruction of 2026-09-10 is uncommitted in the working tree; earlier commits by the orchestrator were pushed by the lead (`origin/master`) |

---

## 2. Lead directives and how they changed the plan

| Decision | Content | Consequence |
| --- | --- | --- |
| DEC-001 | All GPU code in JAX via the existing venv (Python 3.12.14, jax 0.11.1 + CUDA 13, fabricpc 0.5.2, optax, orbax, tokenizers, huggingface_hub); no PyTorch | GPT-2 small re-implemented in JAX; HF "exact equality" checks became stored-oracle comparisons (SD-14, REF-01); baselines will be JAX/optax |
| DEC-002 | PC functionality on FabricPC plus pc_cap infrastructure | FabricPC 0.5.2 has no error-optimization solver (its `NodeState.error` is derived); `pccap.pc` adds `GPT2BlockNode`, `TokenCrossEntropyEnergy`, `EPCInference` on FabricPC's node/graph/energy abstractions |
| DEC-003 | Sibling repo and FabricPC read-only; no runtime import, no copying | `pccap.vendor_hdpc` records the sibling commit `298fc719…` (clean, licence unknown); all re-implemented formulas cite sibling file/lines; PA-1 needs a JAX distillation driver (REG-00, SD-15) |
| DEC-004 | Only code/logs/docs in `pc_cap/`; all resources under `/home/derp/cap/assets/` | datasets, model snapshot, HF cache, GRACE clone, reference env and fixtures, learner checkpoints, prepared arrays live under `assets/` with hashes in `manifests/` |
| DEC-005 | worktrees at `pc_cap/.worktrees/<ID>` | used by codex for Lane B |
| Commit policy (2026-09-10) | agents do not commit/merge/push; the lead commits | PA-8 withdrawn; `docs/ongoing*.md` updated |
| DEC-006 | correction: the sibling's distillation ran a homotopy of relaxation horizons T ∈ {1,2,4,8,16,32,64} (τ = 0.1·T), not one step | SD-6's 8-step credit is inside the training regime but not its terminal horizon; S1-06 measures |
| DEC-007 | JAX determinism: `--xla_gpu_deterministic_ops`, autotune off, matmul precision `highest` (TF32 off), x64 off, OMP 16 | measured default-precision error 5.1e-2 vs 9.3e-5 at `highest` |
| DEC-008 / DEC-009 | rulings on Lane B deliverables: zero-matrix rank encoding; ANA-01 classification policy to be frozen verbatim at S4-01 | — |
| DEC-010 / DEC-011 | CP-A with T1 and the PA clocks; CP-C (S0 complete) | — |
| DEC-012 | shared aggregate step A = 0.3 (S2-02) | used by every confirmatory cap arm |

Specification defects resolved during execution (beyond SD-1…12 seeded from the plan):
SD-13 framework line vs directive; SD-14 HF oracle tolerance (≤ 1e-3 abs, argmax agreement);
SD-15 PA-1 via JAX re-implementation; SD-16 C2 tie → smallest bank index; SD-17 radii per
(base, read, dataset), shared across arms.

---

## 3. Work by the orchestrating session (Claude)

### 3.1 Environment and scaffold (ENV-01…04)
- Verified the JAX venv on the RTX 5070 (cc 12.0, driver 610.57.04, CUDA 13.4 runtime, cuDNN 9.25); added pytest 9.1.1, ruff, safetensors, jsonschema, conllu, hypothesis; `requirements.lock` (pip freeze). Determinism probe: two runs bit-identical (SHA-256 `ce30cc0e…`). Sibling fast tests `unsupported` (no torch).
- Package scaffold per plan §5: `pyproject.toml` (src layout), `Makefile` (`test-fast`, `test`, `test-gpu`, `lint`, `status`), `contracts.py` v0 (SiteId, Write, CostRecord, ForwardResult, ErrorResult, DirectionResult, RouteDecision, RevisionEvent, EditItem, Budget, RoundContext, ItemOutcome, MemoryReport, Metric/metric, Base/EPCBase/Transport/Router/Cap protocols), `pccap/__init__.py` determinism, `harness/status.py` board renderer, `manifests/tasks.json` (85 tasks), `docs/{spec_defects,decisions,lead_queue,environment}.md`, `docs/pdf_text/plan.txt`, layout/firewall test.
- ENV-02 benchmark under the exclusive lease: fp32 forward+backward at batch 8×128 = 19,747 tokens/s (0.052 s/step); batch-1 forward median 1.60/1.75/2.12 ms at 16/32/64 tokens; peak 2.6 GiB; desktop processes (kwin, Chrome, swipl ≈ 1.8 GiB) resident throughout and recorded; κ = 1.0, band [0.5, 2.0], provisional.

### 3.2 Data (DATA-00, DATA-01, DATA-04, S0-01, S0-09)
- DATA-00: GPT-2 snapshot `607a30d7…` (`model.safetensors` `248dfc39…`), zsRE MEND eval/train, CounterFact, WikiText-103-raw-v1 (HF rev `b08601e0…`), UD-EWT r2.18, GRACE clone `f674183f…`; 15/15 files hash-verified; WikiText GPT-2 token counts train 117,920,140 / validation 247,289 / test 283,287 (SD-3 exact).
- S0-01 inventory: ePC checkpoint, resume state, R8/R9 grammar, causal-fibres, comcrit, RelaLeap all absent on this host, in `~/repos` and in the sibling (its three `.pt` files are flowmap endpoints); Drive links [1],[3],[4] resolve; refs [2],[5] have no link. T1 filed with the 2026-09-11 deadline.
- S0-09: S0 development sample (40 zsRE + 40 CounterFact, seed 7, hashed), tokenization helper (answer = `" " + answer + "\n"` tokenized separately, round-trip asserted, > 32 tokens excluded), reference greedy decoder (no KV cache, full recompute, stop at newline/EOS, read-only, no answer argument), PC-7 tests.
- DATA-01: readers and pools. zsRE 19,086 → 10,720 eligible after subject dedup (8,366 duplicates) → dev 300 (incl. the S0 sample) + 1,000 unrelated, confirm pool 10,420. CounterFact 21,919 → 20,391 eligible → dev 300 + 2,777 unrelated, confirm pool 20,091. Dev ∩ confirm subjects = ∅. Teacher filter: 0 teacher-correct in either set; GPT-2 small answers 294/300 zsRE dev questions with an immediate newline (empty answer). Teacher generations used a batched cap-off decoder with tested token-level parity to the reference decoder; access logged.
- DATA-04: H (2×10⁶ train tokens by document, seed 11), drift (whole validation), P2 (256×128 sequences, 4,096 positions), P3 (1,000×128), UD-EWT POS (204,578 labelled first sub-tokens train; dev ≥ 5,000); document-disjoint; E.4 domains `unsupported`.

### 3.3 Harness (S0-03, S0-08, S0-10 runner, S0-11)
- JSON schemas (config, decision, metric, cost, dev/frozen manifests with the D.11 constants pinned as `const`, assets, tasks, datasets); closed outcome-code enum (15 codes, `docs/outcome_codes.md`); ledger with query/learning columns and device time measured as wall around `block_until_ready` (documented); GPU lease with `fcntl` and `nvidia-smi` capture; `pccap run/report/status` CLI that refuses a frozen manifest missing any S4-01 field.
- Byte-exact learner snapshots (arrays, metadata, correction index, per-item use set, Python/NumPy RNG, JAX keys) with content hash, strict resume, atomic writes, item-boundary resource-stop rollback with the ledger untouched.
- Stage S0 runner and smoke manifest; stage reports (`pccap report --stage S0|S1|S2`) with the Appendix G sections; `pccap.analysis.budget` stage totals vs ceilings.

### 3.4 Bases (S0-04, S0-05, S0-06)
- `bases/gpt2_jax.py`: functional GPT-2 small (HF eager semantics; gelu_new; tied head), explicit block loop with sites at blocks 3/7/11 (SD-7), writes as a dense `[3, d]` array at position p (zero rows exact no-ops → cap-off identity by construction), `forward_from` partial resume, adjoint as one `value_and_grad` over the write array (all three sites in one reverse pass), batched last-row and all-layer kernels, sequence-adjoint kernel. Bucketed sequence lengths {16…1024}.
- S0-04 evidence: vs an independent float64 NumPy GPT-2 max |Δlogit| 2.1e-4; vs the HF PyTorch oracle (REF-01) max |Δlogit| 4.0e-4 with argmax agreement 2,802/2,802 and site rows 2.5e-4; `forward_from` bit-exact vs full forward; checksum stable over 100 forwards; lengths 1…128; cost counters per call.
- S0-05: transport (−g/‖g‖, projection before normalization, `no_direction` below 1e-12, non-finite raises); adjoint vs float64 finite differences at step 1e-2: worst relative error 1.4e-5 (an fp32-internal finite difference cannot certify 1e-3 at that step: noise floor ≈ 1e-4/2·step; both recorded); sign-convention control recorded.
- S0-06 ePC on FabricPC: GPT-2 graph (`ids → embed → block_0..11 → logits`), errors at all 12 block outputs (sibling `wrap.py`), energy ½Σ‖e‖² + CE (FabricPC `GaussianEnergy` + custom token-CE energy via `graph_energy`), solver = simultaneous SGD on errors, lr 0.1, zero init, fixed iterations, explicit terminal residual (counted: k+1 forwards/reverses), descent sign +e verified (cos(e, −adjoint) = 0.99999994 on the toy). Zero-error identity: sites bit-exact; logits differ 8.4e-5 in the head GEMM (kernel identified, SD-10 record). Energy monotone over 8 iterations on 16/16 prompts. `docs/epc_energy.md` records everything; `EPCBase.from_npz` loads any distilled checkpoint without code changes.

### 3.5 Cap v0 (CAP-01…07, S0-10)
- Features `z(h) = LN0(h)/√d`; banks with 128-byte packed metadata (documented offsets) as the single source of truth for radius/active; deterministic inclusive-radius nearest retrieval with smallest-id ties; `B_cap = 6144·(8d+128)` = 38,535,168 B, capacities 6,144/2,048/1,374 reproduced, per-bank ceilings sum to `B_cap` for every arm.
- Transactions (begin/rollback/commit over arrays, metadata, correction index, use set, RNG), F.2 conflict handling (0.49 radius shrink; identical-key ambiguity; revision replace/replay only on the correction track), deterministic eviction (lowest use count, oldest last use, smallest id) committed only with a successful write.
- Routers Last/Full/Measured/Random/Supplied; Measured probes through the cap's live sequential retrieval (`Cap.edited_forward(extra=...)`), threshold `max(1e-8, 1e-6·L)`, abstention; CR keyed by (seed, digest, prefix, round).
- `round_update` (reserve A/b, geometric candidates from the same snapshot, smallest loss, commit only on improvement, aggregate ≤ A asserted) and `update_item` (every gold prefix incl. the terminator, R = 5, τ = 0.1, use count once per item, decision records per round).
- Controls with evidence under `results/S0/controls/`: PC-2 exact on 256 probes (0.0) and oracle-false gate exact; PC-3 20/20 development items idempotent on repeat; PC-4, PC-5 (probe and search), PC-6, PC-7, PC-8, PC-9, reproducibility (two replays identical). Smoke edit (C1, A = 0.1): acquired, ES 0 → 1, NLL 23.7 → 0.16, base hash unchanged.

### 3.6 Calibration and screening (S2-01, S2-02)
- b_m = 70.70 / 106.58 / 425.57. zsRE radii 0.281 / 0.414 / 0.189 (coverage 0.87, false-fire 0.000). CounterFact: no positive radius admissible — its neighbourhood prompts (same relation, other subject) are closer in key space (median 0.14–0.18) than paraphrases (0.30–0.64) → exact-key pilot (radius 0), CR-4 interpretation; SD-17 radii per dataset.
- A screening (C1, 100 dev edits per dataset): A = 0.03 ES 0.39/0.33, threshold never reached; A = 0.1 ES 0.97/1.00; A = 0.3 ES 1.00/1.00; deployed-gate false-fire 0.0000 everywhere → **A = 0.3** (DEC-012).

### 3.7 S1 report card, BP rows (S1-02, S1-03, S1-05, S1-06; S1-07 partial)
| Property | Result (BP base) |
| --- | --- |
| P2 geometry | effective rank by layer boundary 0…12: 103, 154, 181, 225, 266, 294, 315, 332, 345, 349, 346, 317, 104; POS probe accuracy 0.87–0.92 at every layer |
| P3 localization | adjoint mass PR 266 of 1,524 cells (nPR 0.17), final-block share 0.011 (no alert), active fraction 0.50, zero fields 0; layer-normalized PR 177 |
| P5 write locality | 50% loss reduction reached at bank 1/2/3 on 0.95/1.00/1.00 of 200 prompts; median normalized write norm 0.80/0.20/0.05; unconditional collateral KL over 200 unrelated prompts 1.09/0.14/0.20 nats; deployed gate false-fire 0 |
| P6 finite settling (declared solver on BP weights) | r₈ 0.40, r₆₄ 0.10 (max 1.54); E₀−E₆₄ 2.42 nats; 95% of the 64-step reduction at median iteration 17.5; cos(e₈, −adjoint) 0.971/0.979/0.998 at banks 1/2/3, cos(e₆₄, −adjoint) 0.75/–/0.98; error–loss Spearman 0.35 (bank 1), 0.61 (bank 3); 0.147 s per 8-iteration call; label **finite-iteration error credit** |
| P1, P4 | pending (need a second base / the grammar) |

Eligibility table (D1 input): BP-only editing programme **eligible**; matched-fidelity
substrate claims **unavailable, not failed**; synthetic-only claims pending the grammar.
Inherited claims: cos > 0.998 partly reproduced (bank 3, e₈, BP weights); teacher KL 3e-5
unavailable; "less concentrated in the last block" consistent on BP adjoints.

---

## 4. Work by the second agent (codex)

| Task | Deliverable | Verification | Integration |
| --- | --- | --- | --- |
| S0-07 metric library | `src/pccap/metrics/{rank,participation,overlap,divergence,cl_matrix,order,editing}.py`, 33 known-answer tests | reviewer confirmed every formula against PDF D.2/D.3/D.4/D.7/D.8/§2.5 literally; all functions return `Metric` with operands; one ruling needed (DEC-008) | merged to `master` after review (orchestrator, 2026-09-09) |
| S0-07b HVP controls | `metrics/hvp.py`, 6 exact small-matrix tests (Gram sign PSD, loop sign I − η²C, full block accounting: total 20, cross-block 16) | pass | merged |
| ANA-01 frozen paired analysis | `analysis/{paired,bootstrap}.py`, 19 tests: per-realization/order pairing, 10,000-draw cluster bootstrap keeping five orders together, 97.5% intervals, D.11 constraints, positive/negative/qualified/inconclusive/incomplete, no imputation | reviewer: matches D.11; `negative` and `qualified` operationalizations must be frozen verbatim (DEC-009) | merged |
| REF-01 reference fixtures | `assets/envs/ref-torch-cpu/` (torch 2.11.0+cpu, transformers 5.13.1), `scripts/make_reference_fixtures.py`, `assets/reference/gpt2/{logits_256.npz, lengths.npz, greedy_8.json, ref_env.json}`, `manifests/reference.json`, `tests/reference/` (8 tests pass in the reference env) | orchestrator ran the consumer tests: logits parity 4.0e-4, argmax 2,802/2,802, decode 8/8 token-for-token | verified 2026-09-10; the HF-oracle rows of S0-04 and S0-09 are now closed; its proposed test patch was superseded by its own later fix |

Codex's handoff note (`docs/tasks/CODEX-LANE-B.md`) and records are the primary sources; all
its work was CPU-only and touched only its owned paths.

---

## 5. Findings and deviations that matter for the month

1. **No ePC checkpoint exists** and regenerating it means re-implementing the sibling's
   homotopy distillation in JAX (REG-00) and then a pilot; the original run took 35.7 A100-h,
   so PA-1's 10-hour bound will probably not admit a full regeneration. The month should be
   planned as BP-only for Thread 1, with ePC rows attaching later if a checkpoint appears.
2. **CounterFact admits no positive retrieval radius** at R-h under the 1% false-fire rule,
   because near-neighbour prompts are closer than paraphrases. CounterFact therefore runs as
   the exact-key pilot; paraphrase generalization through retrieval is zero by construction
   there (CR-4). zsRE has comfortable radii.
3. **zsRE baseline answers are empty** (immediate newline) for GPT-2 small, so every zsRE item
   is a "real edit" and immediate ES measures acquisition from nothing; retention, paraphrase
   and locality endpoints carry the scientific weight.
4. **A = 0.3** is the shared step (A = 0.03 never reaches the per-prefix threshold within five
   rounds); all three candidates are logged.
5. **Compute is not the binding constraint so far**: S0–S2 used under one local GPU-hour.
   The plan's expectation that 300-edit prefixes fit S4 is very likely conservative.
6. **Deviations logged** (App. G §8 material): JAX-only stack (SD-13); HF oracle via fixtures
   (SD-14); PA-1 via re-implementation (SD-15); C2 tie rule (SD-16); per-dataset radii (SD-17);
   adjoint finite-difference oracle in float64 (S0-05); ePC ledger counts the terminal
   residual (docs/epc_energy.md); head-GEMM 8.4e-5 logit difference (SD-10 record); no agent
   commits.

---

## 6. Where everything is

| What | Path |
| --- | --- |
| Task records, board | `docs/tasks/*.md`, `docs/tasks/STATUS.md`, `manifests/tasks.json` |
| Decisions / defects / lead queue | `docs/decisions.md`, `docs/spec_defects.md`, `docs/lead_queue.md` |
| Environment, energy, outcome codes | `docs/environment.md`, `docs/epc_energy.md`, `docs/outcome_codes.md` |
| Stage reports | `results/S0/report.md`, `results/S1/report.md`, `results/S2/report.md` |
| Controls evidence | `results/S0/controls/*.json` |
| Calibration / screening | `results/S2/{residual_scales,radius_calibration,A_screening}.json`, `results/S2/screen/` |
| S1 rows | `results/S1/P{2,3,5,6}_bp.json`, `results/S1/coverage.json` |
| Ledgers | `results/ledger/{tasks.jsonl,stages.json}`, `results/ENV/{bench,kappa}.json` |
| Manifests | `manifests/{assets,datasets,reference}.json`, `manifests/dev/{s0_sample,reserved_subjects,zsre_dev,counterfact_dev,pools,lm_sets,p5_subsets}.json` |
| Resources | `/home/derp/cap/assets/{models,data,hf_cache,third_party,envs,reference,runs}` |
| Parallel-lane instructions | `docs/ongoing.md`, `docs/ongoing2.md` |

---

## 7. Immediately next

Orchestrator: C2 probe binding in the stage harness (all four routing arms through `pccap run`),
then S3-01 once DATA-03 exists; S2-03/S2-04 baselines if the lane stays unclaimed. Open lanes
for other agents: S2-03/S2-04, DATA-03 → GRAM chain, DATA-02a, S2-05a/b, REG-00.


---

## Addendum (2026-09-10, later): D1 reached

- **HARN-C2 / HARN-BATCH:** all four routing arms run through `pccap run --stage S3`; the cap-on evaluation is batched with token-for-token parity to the sequential reference decoder on zsRE and CounterFact (`results/S0/controls/harn_batch_parity.json`). Doing so exposed that bit-exact keys are not a stable property across kernels; **SD-18** adds a 1e-4 float32 key-equality tolerance.
- **DATA-03 / S3-02 (MODULAR-CONTROL):** PC-1 passes (oracle 20/20 and 120/120, unrelated exact; wrong-router 1/30). C2 routing precision 0.88 [0.83, 0.93], recall 0.89 vs oracle 1.00, random 0.55, majority-bank 0.67; no-sharing makes shared items unfixable for every arm; C2 fixes bank-3 mixed items through the shared path (0/20 multi-cause coverage vs C1 20/20).
- **DATA-08:** near-neighbour 20,085 available (400 fixed), temporal corrections 100, compositions 54 (46 `unsupported`).
- **S2-06 throughput** (batched evaluator): 0.5–1.4 wall s/edit (accelerator 0.15–0.8 s/edit) for C0/C1/C2/CR on both datasets.
- **S2-07 / D1 (DEC-013):** scope zsRE 1000 / CounterFact 300 / grammar 10000 at 25.4 of 27.0 accelerator hours; ≈ 27 wall hours for the confirmatory core; fallback 300/300/256. BP-only programme eligible; substrate claims unavailable-not-failed.
- **S3-04 (cap arms, one order):** zsRE RET-GS(100) C0 0.43, C1 0.31, C2 0.30, CR 0.18; C2 routes to bank 3 in 97% of rounds on zsRE and 100% on CounterFact; no abstentions; LS 0.93–1.00; LM drift ratio 1.0000.
- Board: 40 tasks done, 2 partial (S1-07, S3-04). Nothing committed since the lead's instruction.

## Addendum 2 (2026-09-10, after DEC-014): ePC regeneration is on

The lead raised the PA-1 bound to 120 local GPU-hours (DEC-014). REG-00 is implemented:
`pccap.distill` (recipe, data, schedule, train) on top of the FabricPC graph of S0-06 with two
additions (`pccap.pc.kd_energy.KDEnergy`, `pccap.pc.weight_phase.local_weight_energy`; see
`docs/epc_energy.md` "REG-00"). The OpenWebText shard was rebuilt byte-exactly (sha256
`ae5b795a…` = the sibling's pinned value; `manifests/datasets.json`). Tiny-model tests check the
FabricPC path against an independent implementation of the sibling's formulas, micro-batch
exactness, Adam parity with torch's update rule, checkpoint/resume equivalence, and the stage
boundaries (1396/2791/4186/5581/6976/8371, identical to the sibling's realized run). The timing
probe (`results/REG/timing_probe.json`) and the 100-step pilot (`results/REG/pilot-100/`) are the
REG-01 evidence; REG-02 then runs in resumable chunks under the lease. The "BP-only month"
framing of §7 and of `docs/updated_plan3.md` is superseded for the ePC rows: they are
re-measured on the regenerated checkpoint when REG-03 passes.

## Addendum 3 (2026-09-10, evening): REG-01/02 running, Lane F integrated, D2 and freeze draft

- **REG-01 (done, DEC-015):** timing probe s/step at micro-batch 5: T = 1/2/4/8/16/32/64 → 0.72/0.95/1.36/2.27/4.00/7.60/14.66; projection 12.2 h ≪ 120 h; peak 7.6 GiB. The 100-step pilot reproduces the sibling's logged trajectory statistically (median per-step ratios 0.93–1.02; tracking residual 0.999). Along the way the real-model dissection found a float32 cancellation in the FabricPC-path weight phase (the residual stream is O(10–10³), so `stop(z_mu+e) − z_mu` loses a 1e-8 error); fixed by writing the sibling's exact form and keeping node errors equal to the free variable (REG-00 record; `docs/epc_energy.md`). After the fix the local gradient equals the reference in every block (cosine 1.0000).
- **REG-02 (running):** `results/REG/epc-50m.log`, checkpoints under `assets/models/epc/epc-50m/checkpoints/`, chunks of ≤ 500 steps or 90 min under the lease with a pause file for interleaving other GPU work; milestones so far track the sibling's (prompt KL 2–5e-6, held-out ppl ≈ 93.3).
- **Lane F reviewed and integrated (DEC-016):** `pccap.harness.arms` registry (`make_learner`, `router_for`, batched-evaluation adapters, parity-tested); `pccap run --arm B0|B1|B3` and the throughput profile drive baselines unchanged. Development rows: B1/B3 at the prescribed defaults acquire little (ES 0.08–0.10) and lose locality (LS 0.00; drift 1.1–3.9) — diagnosed in `docs/D2_decision.md` F2; the PDF's learning-rate screen ran (DEC-017: 1e-4 stands by the endpoint rule; the table is in the frozen draft).
- **S3-05 (DEC-018):** CR distribution from development C2 routes (zsRE 0.013/0.013/0.974; CounterFact 0/0/1); re-profiled CR reaches zsRE RET-GS 0.38 in one order (uniform 0.18, C2 0.30) — the C2-vs-CR contrast is a real test.
- **DATA-02:** three subject-disjoint realizations × five orders per dataset sealed under `manifests/confirm/` (SHA256SUMS + metadata sidecar); the loader is Lane H's.
- **S3-06 D2 memo** (`docs/D2_decision.md`) and **S4-01 draft** (`manifests/frozen.draft.json`, schema-valid; pending only grammar dataset id and the ePC checkpoint, which S5 alone needs). The freeze itself (writing `manifests/frozen.json`) is the lead's CP-E act: `docs/lead_queue.md` T-CP-E.
- **Projection with measured B1/B3 and the re-profiled CR:** scope zsRE 1000 / CounterFact 300 / grammar 10000 at 25.1 of 27.0 local h (≈ 23 wall h on this host).
- Open for the other agent (ongoing3.md): Lane D GRACE (in progress: `assets/envs/grace` exists), Lane H DATA-02a, Lane G′ grammar.

## Addendum 4 (2026-09-10, late): review response and S5/S4/S7 preparation while REG-02 runs

- Review (`docs/derp_review1.md`) answered in `docs/derp_review1_response.md`: single current log `docs/ongoing.md` (older logs archived), README and CONTRIBUTING written, spec-defect register triaged (16 of 18 committed), environment-setup script assigned to Lane R; the "energy efficiency" reading of `epc_energy.md` corrected.
- Lane D unblocked: the lead approved the setuptools pin in the GRACE environment; applied and verified (`import wandb` works).
- S5-01 prepared: SE-E error-credit rule in the cap (`CapConfig.credit`, inference cost charged), ePC radius calibration option, `manifests/dev/s5_arms.json`, `pccap run --stage S5`, CPU test of the credit rule; GPU checks and the ePC calibration + 20-item SB/SE-A/SE-E smoke are queued behind the post-REG-02 chain (`results/REG/chain_s5_prep.sh`).
- S4-05 resource views (development dry run: only C0 is within 20% of C2's update cost), S4-06 wiring over ANA-01 with a synthetic 3 × 5 test, S7-03 order-variation analysis (JS part pending checkpoints), `docs/REPRODUCE.md` draft.
- Tree: 296 CPU tests pass, lint clean. REG-02 at step ≈ 3,100 (T = 4), ETA ≈ 19:40 EDT.

## Addendum 5 (2026-09-10, afternoon): Lane G′ done on the CPU while REG-02 runs

GRAM-01 generator (eight observable contexts, two shared and one private mechanism per context with
deterministic targets at a designated position; five balanced orders; byte-identical regeneration),
GRAM-02 six-layer base (d = 128, sites at blocks 1/3/5, `GrammarBase` with the BP API; trained on the
CPU to 0.986 held-out designated-position accuracy in 8 s; competence table: frozen base 0.24–0.31 on
the eight tasks by construction, joint reference 1.00), DATA-06 task streams (three realizations ×
five orders, 2,000 evaluation sequences per task, held-out combinations, joint reference; one
sequence/target pair per item), DATA-07 tracing pairs (consistent single-latent counterfactuals through
a generator override; 119 of 120 pairs strong; mechanisms localize as multi-site by cumulative
residual, the copy mechanism computed between blocks 1 and 3 at the prediction position). The
replacement base is recorded as provisional until the PA-2 clock. Remaining grammar work: the S4
runner/evaluator generalization for grammar streams (tokenizer-free single-token items) and S3-03.
