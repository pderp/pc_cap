# Week 1 Plan (v1): Correctness and Feasibility

**Programme:** A One-Month Programme for Continual-Learning Predictive-Coding Caps on GPT-2-Scale Transformers (Goertzel and Claude Fable, revised readable edition, 7 September 2026). Source: [`pc_cap_month_plan_readable.pdf`](pc_cap_month_plan_readable.pdf). Plain-language summary: [`pc_cap_month_plan_summary.md`](pc_cap_month_plan_summary.md). References: [`footnotes.md`](footnotes.md).

**Week 1 window:** Tuesday 8 September 2026 (today) through Monday 14 September 2026. Five working days (WD1–WD5) with the weekend as an explicit, optional buffer. Decision point **D1 (validity and feasibility)** closes the week at end of day Monday 14 September. Week 2 (mechanism screening, S3) starts Tuesday 15 September.

**Stages covered:** S0 (harness and invariant tests), S1 (substrate report card), S2 (shared calibration, baseline validation, throughput). Combined accelerator ceiling: **32 A100-equivalent hours** (S0 = 8, S1 = 12, S2 = 12) out of the month's 154. These are spending ceilings, not runtime predictions (Appendix B).

**What this document is.** A day-by-day execution plan for week 1 with checkpoints, deliverables, an unknowns register, and named revision points. It does not change any number, threshold, or procedure in the PDF; where the PDF fixes a rule, this plan cites the section and follows it. Where this plan makes an assumption the PDF does not settle, it says so and records it in the unknowns register (Section 7). This file is version 1 and is expected to be revised at every checkpoint; revisions are logged in Section 10.

---

## 0. Definition of done for week 1

Week 1 is done when all of the following are true and written down in stage reports following the Appendix G template:

1. **S0 exit:** every S0 known-answer test passes, and the four pre-run invariants (cap-off identity, memory accounting, transactional rollback, complete-state cloning) pass on the BP base. No experimental run has been started before this.
2. **S1 exit:** a validity/eligibility table exists stating, for each available base, which claims it is eligible for (matched-fidelity substrate claim, synthetic-only substrate claim, BP-only editing) and which report-card alerts fired. If the ePC base is unavailable, the table says "unavailable, not failed" with the reason.
3. **S2 exit:** one shared aggregate step `A` is frozen from the three candidates; per-bank radii are calibrated (or exact-key fallback recorded); B1/B3/B4 baselines run end to end on development data with parity evidence; and a throughput profile with projected costs for every candidate stream length exists.
4. **D1 memo:** a short decision memo recording base eligibility, the compute conversion factor, the affordable stream-length candidates, and the week-2 plan, with every open unknown either resolved or assigned an owner and deadline.
5. **No confirmatory data touched.** Development and confirmation manifests are disjoint and the confirmation manifest has been hashed but never read by any tuning code (Operating rule 3).

---

## 1. Starting position as of Tuesday 8 September 2026

### 1.1 What exists in this repository

| Item | Status |
| --- | --- |
| The plan PDF, its summary, and the reference list | Present (`docs/`) |
| Source code, `pccap` package, tests | **Absent.** Week 1 starts from an empty tree. |
| Base checkpoints (BASE-BP teacher, BASE-EPC conversion) | **Absent from repo.** Location unknown (U1). |
| Causal-fibres v0.3, comcrit HVP code, six-layer grammar fixture, RelaLeap harnesses, FabricPC/JAX | **Absent from repo.** Location unknown (U5). |
| Public datasets (GPT-2 small weights, zsRE, CounterFact, WikiText-103, POS-tagged corpus) | Not downloaded. All are public and can be fetched on WD1 (U7 covers provenance). |
| Development/confirmation manifests | Not created. |

### 1.2 Local environment (measured today)

| Resource | Value |
| --- | --- |
| GPU | NVIDIA GeForce RTX 5070, 12,227 MiB |
| CPU / RAM / disk | 16 cores / 30 GiB / 875 GiB free |
| OS | Fedora, kernel 7.1.12 |
| Python | 3.x present; **PyTorch not installed** |
| Git | Clean tree on `master`, three commits, docs only |

Implications:

- A 12 GiB Blackwell-generation GPU is sufficient for GPT-2 small (124M, `D = 12`, `d = 768`) with a cap, LoRA baselines, and GRACE, in fp32, at batch size 1 to 8. It is **not** an A100. The plan's hour ceilings need a measured conversion factor (Appendix B: "hardware conversion based on a measured shared workload"). This is U4 and a WD1 task.
- The RTX 5070 requires a recent PyTorch build with Blackwell (`sm_120`) kernels. Older wheels will fail at the first CUDA kernel launch. Environment setup is therefore a real task, not a formality.
- The "existing production environment" named in Appendix B is not this machine. Whether it exists elsewhere and whether the user has access is U1/U4.

### 1.3 Who decides what

The plan routes "unresolved changes to task scope" to the human lead (Operating rule 5). The lead is assumed to be Ben Goertzel (U12 confirms). This plan's revision points distinguish decisions the executor can make alone (development choices, logged) from decisions that go to the lead (scope, thresholds, primary endpoint, dropping arms).

---

## 2. Week 1 at a glance

| Day | Date | Theme | Stage | Checkpoint |
| --- | --- | --- | --- | --- |
| WD1 | Tue 8 Sep | Locate, verify, decide. Environment, assets, datasets, scaffold, compute conversion. | S0 (setup) | CP-1 |
| WD2 | Wed 9 Sep | Measurement before the thing measured: BP base wrapper, known-answer metric tests, cost ledger, memory accounting, stream readers, decoder. | S0 | CP-2 |
| WD3 | Thu 10 Sep | The cap core: slots, banks, transactional updates, routers, F.3 learning loop, clone/restore, positive controls PC-2/4/5/6/9. S0 stage report. | S0 exit | CP-3 |
| WD4 | Fri 11 Sep | Report card on BP (P2, P3, P5), development data manifest, residual scales, radius calibration. ePC wrapper if assets exist. | S1 + S2 | CP-4 |
| Sat/Sun | 12–13 Sep | Optional buffer. Absorbs slips from WD1–WD4 or pulls WD5 work forward. | — | — |
| WD5 | Mon 14 Sep | Step-budget screening, baselines (B1/B3/B4) with parity, throughput profile and projections, ePC report card (P1, P6) if available. S1/S2 stage reports. D1 memo. | S1/S2 exit | CP-5 = D1 |

Dependency order (Appendix C): S0 → S1 and S2 in parallel; S2 → S3 (week 2); S1 and S3 → S4 freeze. Nothing in S1 or S2 may run on a real base before the S0 pre-run invariants pass.

---

## 3. Day-by-day plan

Each day lists tasks, the deliverable each produces, the plan section it satisfies, and the checkpoint criteria. Task IDs are `W1-<day>.<n>`. A ⚠ marks a place where progress may force a revision (details in Section 8).

### WD1 — Tuesday 8 September: locate, verify, decide

Goal: by end of day, know what assets and compute exist, have a working environment, and have a repository scaffold that matches Appendix F.7.

| ID | Task | Deliverable | Satisfies |
| --- | --- | --- | --- |
| W1-1.1 | **Asset triage.** For every asset in §3.1 (ePC checkpoint + BP teacher + distillation pipeline; causal-fibres v0.3; comcrit; six-layer grammar fixture; RelaLeap harnesses; FabricPC/JAX) record path or URL, owner, version or commit, licence, hash, and framework. Record "MISSING" explicitly where nothing is found. Send the lead the list of missing items today. | `manifests/assets.json` + `docs/assets_status.md` | §3.1, Op. rule 1 |
| W1-1.2 | **Environment.** Create a Python 3.11 virtual environment; install a PyTorch build with Blackwell support and verify a CUDA matmul runs on the RTX 5070; install `transformers`, `numpy`, `scipy`, `pytest`; produce a lock file. Record the driver, CUDA, and torch versions. Set deterministic flags globally (`torch.use_deterministic_algorithms(True)`, fixed seeds, dropout off). | `pyproject.toml`, lock file, `docs/environment.md` | App. B "Software and paths", Op. rule 9 |
| W1-1.3 | **Compute conversion.** Run a shared workload micro-benchmark (GPT-2 small forward+backward, batch 8 × 128 tokens, fp32, 60 s steady state after warmup) and record tokens/s. If an A100 is reachable, run the identical script there and compute the ratio. If not, record a **provisional** factor from published A100 figures, label it provisional, and schedule a real measurement (U4). Convert the week-1 ceilings (8/12/12 h) into local GPU hours. ⚠ | `results/S0/compute_conversion.json` | App. B "Stage ceilings" |
| W1-1.4 | **Public datasets.** Download and hash: GPT-2 small weights and tokenizer (record HF revision); zsRE editing data in the preprocessing used by GRACE [7] (record which release, U7); CounterFact with paraphrase and neighbourhood sets [9]; WikiText-103 validation; a POS-tagged English corpus with ≥ 25,000 tagged tokens for the P2 probe (Universal Dependencies English EWT is the default choice; record licence). Store under `data/raw/` with a `SHA256SUMS` file. | `data/raw/`, `manifests/datasets.json` | E.2, D.2, D.8 |
| W1-1.5 | **Repository scaffold** matching F.7: `pccap/{bases,cap,routers,harness,fixtures,metrics,cli}`, `tests/`, `manifests/{dev,test}/`, `results/<stage>/<arm>/<base>/<realization>/<perm>/`, `docs/`. Add `make test` and `make lint`. Commit. | Package skeleton, first commit of code | F.7, App. B "Results live under…" |
| W1-1.6 | **Read the internal references** available via the Drive links in `footnotes.md`: [1] Causally Designed Error Highways, [3] The Coupling Dilemma, [4] The Shadow Calculus. These are context for the routing hypothesis and the order-effect diagnostics, not sources of numbers. [2] and [5] have no links; ask the lead (U5). | Notes in `docs/reading_notes.md` (optional) | §2.5, §3.1 |
| W1-1.7 | **Open the unknowns register** (Section 7 of this file becomes the living copy, or move it to `docs/unknowns.md`). Assign an owner and a resolve-by date to each. Send the lead the questions that only they can answer (U1, U2, U3, U5, U6, U12). | Updated Section 7 | Op. rule 1 |
| W1-1.8 | **Spec-defect log.** Create `docs/spec_defects.md` for any contradiction found between the main text and the appendix. The appendix preamble requires these to be recorded and resolved in development, never silently. Seed it with the candidates in Section 9. | `docs/spec_defects.md` | App. preamble |

**CP-1 (end of WD1) passes when:** environment runs a CUDA matmul; asset status is recorded for all six asset lines; datasets are hashed on disk; scaffold is committed; the lead has received the missing-asset list and the U-questions; a provisional or measured conversion factor exists.

⚠ **Revision trigger at CP-1:** if the ePC checkpoint and BP teacher are not located today, WD4/WD5 ePC tasks become conditional and the BP-only path in Section 8 (RV-1) is activated tomorrow morning, not at the end of the week.

### WD2 — Wednesday 9 September: measurement before the thing measured

Goal: the base wrapper, every metric with a known-answer test, the cost ledger, memory accounting, stream readers, and the reference decoder. No cap yet.

| ID | Task | Deliverable | Satisfies |
| --- | --- | --- | --- |
| W1-2.1 | **`BPBase` wrapper** over HF GPT-2 small. Expose `forward`, hidden hooks at the three bank sites, `adjoint`, parameter/buffer checksum, and a per-call cost record. Hook definition per F.1: block output before the next block; for the final block, the output **before** `ln_f` and the LM head. With `D = 12`, banks attach at `l = 4, 8, 12` (block indices 3, 7, 11 in 0-based HF `h[]`). **Trap:** HF's `output_hidden_states[-1]` is post-`ln_f`; use forward hooks on the block modules, not the returned tuple. One reverse pass exposes adjoints at all three sites (F.3 step 2); do not charge three. Dropout off. | `pccap/bases/bp.py`, `tests/test_bp_base.py` | F.1, F.7, Op. rules 9–10 |
| W1-2.2 | **Frozen-base guard.** Hash all parameters and persistent buffers before and after every run; fail loudly on mismatch. | `pccap/bases/checksum.py` | Op. rule 10 |
| W1-2.3 | **Known-answer metric tests** (all required by S0): (a) effective rank: uniform rank-`r` spectrum → `r`; unequal nonzero singular values → below algebraic rank; all-zero matrix → rank 0 with its own outcome code, no division; (b) participation ratio: uniform positive mass over `N` cells → `N`; zero mass → outcome code; (c) subspace overlap `O_ab`: orthogonal → 0, identical → 1; (d) JS divergence: identical distributions → 0, bounded by `log 2`; (e) scalar quadratic order effect of §2.5: `L1 = θ²/2`, `L2 = (θ−1)²/2`, displacement exactly `η²` with zero Hessian commutator; (f) structured undefined/unreachable/not-supported outcome codes are distinct from NaN and carry operands. | `pccap/metrics/*.py`, `tests/test_metrics_known_answer.py` | S0, D.2–D.4, D.7, D.9, Op. rule 8 |
| W1-2.4 | **Cost ledger.** Counters for full and partial forwards, reverse/VJP calls, settle iterations, token-prefix microsteps, router probes, memory-search time, wall time, accelerator time, peak memory. Query costs and learning costs are separate columns. Every wrapper call increments it; nothing is free. | `pccap/harness/ledger.py`, tests | App. B "Cost ledger", Op. rule 7 |
| W1-2.5 | **Memory accounting.** Implement `B_cap = 6144(8d + 128)` and the per-bank slot formula `S_m = floor(B_m / (4 d_k + 4d + b_meta))`. At `d = 768`: `B_cap = 38,535,168` bytes (36.75 MiB); three-bank arms get 12,845,056 bytes per bank → **2,048 slots per bank** for R-h (`d_k = d`) and **1,374** for `d_k = 2d`; C0 gets all 6,144 slots in the last bank. Count keys, values, metadata (fixed 128 bytes), indices, caches, alignment. Assert no unbounded text in metadata. Report allocated vs occupied bytes separately. | `pccap/cap/memory.py`, `tests/test_memory_accounting.py` | App. B "Memory ceiling", F.2, PC-6 |
| W1-2.6 | **Stream readers and tokenization helper.** zsRE and CounterFact readers producing (prompt, canonical answer + fixed terminating newline, aliases, paraphrases, locality prompts, subject id). One tested helper tokenizes prompt/answer boundaries and asserts the target decodes to the intended answer and delimiter. Exclude and count answers exceeding 32 tokens with delimiter. | `pccap/harness/streams.py`, tests | E.2 |
| W1-2.7 | **Reference decoder and scoring.** Greedy generation, max 32 new tokens, stop at newline or EOS, **full-prefix recompute with no KV cache**, cap writes only at the current prediction position. Fixed normalization: Unicode NFKC, case-fold, whitespace collapse, trim. Exact complete-answer match against aliases. Truncation is failure unless the full accepted answer was already emitted. Also teacher-forced NLL for diagnosis. | `pccap/harness/decode.py`, `pccap/metrics/editing.py`, `tests/test_pc7_complete_answers.py` | E.2, D.8, PC-7 |
| W1-2.8 | **Decision-record and outcome-code schema.** JSON schema for per-decision records (item digest, prefix, round, candidate banks, signed scores, chosen route, accepted increment, before/after loss, allocation/conflict/eviction codes, cost counters) and the closed list of outcome codes (accepted, rejected-no-improvement, no-direction, ambiguous-key-conflict, evicted, unreachable, undefined, not-supported, acquisition-failure, …). | `pccap/harness/records.py`, `docs/outcome_codes.md` | F.7, Op. rule 8 |

**CP-2 (end of WD2) passes when:** `make test` is green for every known-answer test; `BPBase` reproduces HF logits bit-for-bit on 256 probe prompts; the hook sites produce tensors whose shape and pre-`ln_f` identity are asserted; a zsRE and a CounterFact item round-trip through tokenization and decode; PC-7 passes (two-token answer with correct first and wrong second token fails ES).

⚠ **Revision trigger at CP-2:** if the metric tests are not all green, WD3 does not start the cap. Slip one day, use the weekend buffer, and note it (RV-4).

### WD3 — Thursday 10 September: the cap core and S0 exit

Goal: cap v0 exactly as F.1–F.3 specify, all five routers, positive controls that do not need a fixture, and the S0 stage report.

| ID | Task | Deliverable | Satisfies |
| --- | --- | --- | --- |
| W1-3.1 | **Key features.** `LN0` (parameter-free centring and variance normalization, eps `1e-5`), `z(h) = LN0(h)/√d`. Keys frozen after allocation; no EMA. | `pccap/cap/features.py` | F.1 |
| W1-3.2 | **Slot and Bank.** Slot fields per F.2 (key, value, radius ≥ 0, success-use count, creation and last-use indices, last target token, fixed-size owner-edit digest, version, optional loss EMA). Retrieval: among active slots with `‖q − k‖₂ ≤ ρ`, choose nearest; ties by smallest immutable slot ID; zero radius matches only an exact key; distance and tie logic must not depend on unordered containers. Read-only predict never mutates usage. | `pccap/cap/bank.py`, tests | F.1, F.2 |
| W1-3.3 | **Transactions.** Snapshot/commit/rollback covering values, keys, radii, metadata, allocation IDs, indices, and RNG state. Conflict rule for distinct keys: shrink old radius to `min(ρ_s, 0.49 d_qs)`, new radius `min(ρ_0, 0.49 d_qs)`, old key and value intact. Identical keys with incompatible targets: preserve old memory, log `ambiguous-key-conflict`, reject this bank (correction-track retirement is deferred to the week the correction challenge is built, but the code path and its label are stubbed now). Eviction: lowest success-use, then oldest last-use, then smallest ID; commits only with a successful write. | `pccap/cap/transaction.py`, `tests/test_pc4_conflict.py` | F.2, PC-4 |
| W1-3.4 | **Cap.** Three banks in depth order, read-before-write, only position `p` modified, cap-disabled path is the base's own forward. `predict` (read-only), `update` (transactional), `serialize`, `restore`, `clone` (includes RNG and counters), `memory_bytes`. | `pccap/cap/cap.py` | F.1, F.7 |
| W1-3.5 | **Routers.** `Last` (C0), `Full` (C1), `Measured` (C2: probe `ε b_m d_m` with `ε = 0.01`, signed score `r_m = (L − L_probe)/ε`, select largest positive, ties by depth, abstain unless improvement `> max(1e−8, 1e−6 L)`), `Random` (CR: fixed bank distribution, randomness keyed by seed, item ID, prefix index, round), `Supplied` (CO). | `pccap/routers/*.py` | F.3 steps 3–4 |
| W1-3.6 | **F.3 learning loop.** Per gold prefix, up to `R = 5` rounds, stop at `CE ≤ 0.1` nats. Adjoint directions `d_m = −g_m/‖g_m‖` with discrete retrieval held fixed; zero direction → `no-direction` outcome. Scheduled banks get `A/b` each, no redistribution, increasing depth, recompute features/gates/loss/credit after each accepted earlier write. Candidate grid `a ∈ {A/b, A/(2b), A/(4b), A/(8b)}` plus no-op, all from the same snapshot, choose smallest loss, tie → smaller increment, commit only if improvement `> max(1e−8, 1e−6 L)`. Aggregate normalized increments ≤ `A` per round. Metadata updates on commit. Difficulty weight off (`w_s = 1`). Every decision produces a record. | `pccap/cap/learn.py` | F.3, F.6 |
| W1-3.7 | **Positive controls without a fixture.** PC-2 cap-off identity on 256 probes (behavioural, not checksum-only) and oracle-false gate identity; PC-4 conflict transaction (distinct keys, identical-key ambiguity, rollback of failed replacement); PC-5 signed probe and search on an analytic 1-D loss (helpful → positive, harmful → negative, nonmonotone loss does not crash, rejection restores exact state, accepted update is the one evaluated); PC-6 byte ceiling respected by C0/C1/C2/CR, wide keys reduce slot count, deterministic eviction at full capacity; PC-9 cloned identical sequences agree, reversed sequences start from the same state with item-keyed random choices, scalar quadratic order effect recovered. **Reproducibility:** replay the same config, stream, and RNG twice → identical discrete decisions and metrics within `1e−6` relative / `1e−8` absolute. | `tests/test_pc2_identity.py`, `test_pc4…`, `test_pc5…`, `test_pc6…`, `test_pc9…`, `test_reproducibility.py` | F.5, Op. rule 9 |
| W1-3.8 | **Sign-convention control.** Verify the descent sign once on an analytic differentiable control; record it. It is never flipped per example. | Part of PC-5 test | F.3 step 2 |
| W1-3.9 | **CLI.** `pccap run --stage … --arm … --base … --read … --realization … --perm … --manifest …` that fails if a required frozen field is missing. Week 1 only needs `--stage S0/S1/S2` and development manifests. | `pccap/cli.py` | F.7 |
| W1-3.10 | **S0 stage report** per Appendix G: header (hashes, hardware, cost vs 8 h ceiling), status, controls table (expected invariant, observed, pass/fail), coverage, deviations, reproduction commands. | `results/S0/report.md` | App. G |

**CP-3 = S0 exit (end of WD3) passes when:** every test in W1-2.3 and W1-3.7 is green; a first smoke edit (one development zsRE item, C1, `A = 0.1`) runs end to end on GPT-2 small, producing decision records and a ledger, regardless of whether it acquires the fact; the base checksum is unchanged after the run; the S0 report is filed.

⚠ **Revision trigger at CP-3:** if PC-4/PC-5/PC-9 are not green, S1 may still start (it does not use the cap's update path) but S2 calibration and throughput may not. Reorder WD4 to put P2/P3 first (RV-4).

Deferred from S0 to early week 2 with a hard date: the MODULAR-CONTROL fixture and PC-1 (planted acquisition ≥ 19/20 with the supplied router, unrelated outputs unchanged within `1e−6`). E.1 requires ≥ 100 independent-private, ≥ 100 shared, ≥ 100 mixed-cause items plus held-out combinations and three cases (no-sharing, useful-sharing, wrong-router). If the weekend buffer is used, build it Saturday (W1-B.1). It must exist before S3 starts on Tuesday 15 September.

### WD4 — Friday 11 September: report card on BP, development data, calibration

Goal: everything in S1 that needs only the BP base; the development manifest; residual scales; radius calibration. ePC work only if assets are in hand.

| ID | Task | Deliverable | Satisfies |
| --- | --- | --- | --- |
| W1-4.1 | **Development/confirmation split.** From zsRE and CounterFact, build a development manifest (≥ 300 edits with paraphrases, ≥ 1,000 unrelated or near-neighbour prompts) and, separately, the confirmation pools, subject-disjoint and deduplicated on facts and subjects. Edits are selected using the BP teacher only: keep only items whose complete generated answer is outside the accepted aliases. Hash both manifests. The confirmation manifest is written, hashed, and then not read by any development code. Log unavoidable overlaps. | `manifests/dev/{zsre,counterfact}.json`, `manifests/test/…` (hashed, sealed) | S2, E.2, D.1, Op. rule 3 |
| W1-4.2 | **Held-out LM sets.** `H`: 2 × 10⁶ tokens for P1 (disjoint from everything else). Drift set: a committed 10⁶-token sample of WikiText-103 validation under the GPT-2 tokenizer. 4,096 held-out token positions for P2. 1,000 teacher-forced sequences for P3. | `manifests/dev/lm_sets.json` | S1, D.2, D.3, D.8 |
| W1-4.3 | **Residual scales `b_m`.** Median raw residual norm at each bank site over cap-disabled development prefixes, floored at `1e−8`. | `results/S2/residual_scales.json` | F.6 |
| W1-4.4 | **P2 geometry on BP.** Effective rank per layer on 4,096 held-out positions (centre first; report full spectra and seeds). Linear POS probe: ≥ 20,000 training and 5,000 held-out tagged tokens, fixed, disjoint. For BP alone this is the reference row; ratios to teacher appear when ePC exists. | `results/S1/P2_bp.json` | D.2 |
| W1-4.5 | **P3 localization on BP adjoints.** For 1,000 sequences, squared adjoint norm per (layer, position) cell; PR, nPR = PR/N, final-block share, active fraction (cells above 1% of the sequence max), zero fields counted separately, raw and layer-scale-normalized variants, dataset-level layer shares. Alert if final-block share > 0.4 (alert, not exclusion). | `results/S1/P3_bp.json` | D.3 |
| W1-4.6 | **P5 write locality on BP.** 200 development edit prompts `Q`, 200 unrelated/near-neighbour prompts `U`. At each bank site, unit descent direction under adjoint credit; bounded geometric search for a 50% token-loss reduction; record achieved improvement, required normalized write norm, unreachable cases. Unconditional collateral `C_q` (mean KL on `U` under the same write) and gated behaviour separately. No epsilon inserted into ratios. | `results/S1/P5_bp.json` | D.5 |
| W1-4.7 | **Radius calibration.** For each bank and read variant (R-h only this week): 20-quantile grid of observed key distances on development prompts; choose the largest radius with unrelated false-fire rate ≤ 1%; ties by paraphrase coverage; store every candidate and its result. If no positive radius qualifies, record exact-key retrieval for the pilot and flag the limitation. ⚠ | `results/S2/radius_calibration.json` | S2 |
| W1-4.8 | **ePC wrapper, conditional on U1/U3/U6.** `EPCBase`: forward, hooks at identical sites, adjoint, finite error inference under the declared energy `E(e; x, y) = ½ Σ‖e‖² + CE(f(x; e), y)`, errors initialized at zero per call, retrieval fixed within a settle, recorded solver/step size/precision/reset/stopping. If the production energy differs, record the complete energy and use it consistently. Cross-framework gradients must be explicitly implemented and tested, not copied arrays. ⚠ | `pccap/bases/epc.py`, `docs/epc_energy.md` | F.6, D.6, App. B |

**CP-4 (end of WD4) passes when:** the development and confirmation manifests are sealed with hashes; `b_m` exists; P2/P3/P5 on BP are computed with their known-answer tests still green; the radius table exists for all three banks (or the exact-key fallback is recorded); the ePC wrapper either runs a forward pass with recorded energy conventions or U1/U3/U6 are marked blocking with the lead's answer status.

### Weekend buffer — Saturday 12 and Sunday 13 September (optional)

Not scheduled work. If used, in priority order:

| ID | Task | Why |
| --- | --- | --- |
| W1-B.1 | MODULAR-CONTROL fixture and PC-1 (E.1, F.5). | Required before S3 on Tuesday; otherwise consumes WD5 or Tuesday morning. |
| W1-B.2 | Absorb any slip from WD2–WD4. | Keeps D1 on Monday. |
| W1-B.3 | Pull W1-5.3 (throughput) forward. | Throughput is the input to S4's stream-length choice and the biggest feasibility unknown (U11). |
| W1-B.4 | LATENT-GRAMMAR loader for the six-layer model, if the fixture was located (U5). | Needed for S3 on the learned grammar. |

### WD5 — Monday 14 September: calibration, baselines, throughput, D1

Goal: finish S2, finish whatever of S1 the ePC assets allow, file both stage reports, and write the D1 memo.

| ID | Task | Deliverable | Satisfies |
| --- | --- | --- | --- |
| W1-5.1 | **Aggregate step screening.** Run `A ∈ {0.03, 0.1, 0.3}` on development edits (C1 router, calibrated radii), scoring immediate acquisition subject to the same ≤ 1% false-fire locality criterion. Freeze **one** shared `A` for all cap arms. Log every attempted configuration including failures. Do not tune per arm. ⚠ | `results/S2/A_screening.json` | S2 "Update numerics", Op. rule 3 |
| W1-5.2 | **Baselines.** B1: LoRA rank 8 on query and value projections of all layers, Adam, 10 steps per complete edit; screen learning rates `{3e−5, 1e−4, 3e−4}` under the same development allocation. B3: B1 plus reservoir replay, one replay item per new item per step, ceiling 5% of seen edits or `B_cap` bytes, whichever binds; charge all tokens and optimizer state. B4: GRACE from the official implementation [7]; record commit and local changes; initially 100 value steps; select layer and radius on development data; apply the byte ceiling if supported and disclose the eviction adaptation; run PC-10 parity on small shared single- and multi-token cases. B0 (frozen) is free. B2/B5 are not built this week. ⚠ | `pccap/baselines/{lora,replay,grace}.py`, `results/S2/baselines/`, `tests/test_pc10_parity.py` | S2 "Baselines", §8, PC-10, Op. rule 11 |
| W1-5.3 | **Throughput profile.** 100–300 complete development edits under each of C0, C1, C2, CR (and B3, B4), including immediate ES/GS/LS evaluation. Record operation counts, steady-state per-edit latency (compile/warmup reported separately), peak memory. Project the cost of each candidate confirmatory scope: zsRE `{300, 1000, 3000}` and CounterFact `{300, 1000}`, × 3 realizations × 5 orders, × required arms (C1, C2, CR, C0, B3, B4), plus checkpoint re-evaluations at 100/300/1000/3000, with 25% headroom, against the S4 ceiling of 36 A100-equivalent hours converted by W1-1.3. ⚠ | `results/S2/throughput.json`, `docs/throughput_projection.md` | S2 "Throughput", App. B "Stage ceilings" |
| W1-5.4 | **ePC report card, conditional.** P1: `KL(p_T ‖ p_S)` on `H` feedforward and unclamped-after-8-iterations, both ≤ 1e−3 nats for eligibility; 95th/99th percentiles and max finite; argmax agreement on the edit-prompt pool; initially-correct fraction per base on the BP-selected stream. P6: energy at `k = 8` and `64`, residual `r_k`, earliest iteration reaching 95% of the 64-step reduction (only when `E_0 > E_64`), "settled" label only if `r_64 ≤ 1e−3`, error–loss Spearman, reverse-mode call counts and runtime. Reproduce the inherited claims (KL near 3e−5, cosine > 0.998 between settled errors and adjoints) as starting claims. P2/P3/P4 on ePC and P4 on BP. ⚠ | `results/S1/P1_epc.json`, `P6_epc.json`, … | S1, D.1, D.6, §2.2 |
| W1-5.5 | **S1 stage report** including the validity/eligibility table (which base is eligible for which claim) and the alerts table, separate from scientific outcomes. | `results/S1/report.md` | App. G, D1 |
| W1-5.6 | **S2 stage report** including the frozen `A`, radii, baseline configurations and parity results, throughput and projections, and cost against the 12 h ceiling. | `results/S2/report.md` | App. G |
| W1-5.7 | **D1 memo.** One page: base eligibility; compute conversion and remaining budget; which confirmatory scopes are affordable; open unknowns with owners; changes to this plan; week-2 (S3) plan draft. Send to the lead. | `docs/D1_decision.md`, `docs/week2plan1.md` (draft) | §10 D1 |

**CP-5 = D1 (end of WD5) passes when:** the definition of done in Section 0 holds.

---

## 4. Deliverables checklist

| # | Deliverable | Path | Due |
| --- | --- | --- | --- |
| D-1 | Asset status with hashes/versions/licences or MISSING | `manifests/assets.json`, `docs/assets_status.md` | WD1 |
| D-2 | Pinned environment and lock file, hardware record | `pyproject.toml`, lock file, `docs/environment.md` | WD1 |
| D-3 | Compute conversion factor (measured or provisional) | `results/S0/compute_conversion.json` | WD1 (measured by WD5 if provisional) |
| D-4 | Hashed public datasets and manifest | `data/raw/SHA256SUMS`, `manifests/datasets.json` | WD1 |
| D-5 | `pccap` scaffold committed | `pccap/`, `tests/`, `Makefile` | WD1 |
| D-6 | Spec-defect log | `docs/spec_defects.md` | WD1, living |
| D-7 | `BPBase` with hooks, adjoint, checksum, ledger | `pccap/bases/bp.py` | WD2 |
| D-8 | Known-answer metric tests, all green | `tests/test_metrics_known_answer.py` | WD2 |
| D-9 | Cost ledger and memory accounting with tests | `pccap/harness/ledger.py`, `pccap/cap/memory.py` | WD2 |
| D-10 | Stream readers, tokenization helper, reference decoder, PC-7 | `pccap/harness/{streams,decode}.py` | WD2 |
| D-11 | Decision record schema and outcome codes | `pccap/harness/records.py`, `docs/outcome_codes.md` | WD2 |
| D-12 | Cap v0 (slots, banks, transactions, cap, five routers, F.3 loop) | `pccap/cap/`, `pccap/routers/` | WD3 |
| D-13 | PC-2, PC-4, PC-5, PC-6, PC-9, reproducibility tests green | `tests/test_pc*.py` | WD3 |
| D-14 | CLI that fails on missing frozen fields | `pccap/cli.py` | WD3 |
| D-15 | S0 stage report | `results/S0/report.md` | WD3 |
| D-16 | Sealed development and confirmation manifests | `manifests/dev/`, `manifests/test/` | WD4 |
| D-17 | Residual scales `b_m` | `results/S2/residual_scales.json` | WD4 |
| D-18 | P2, P3, P5 on BP | `results/S1/P{2,3,5}_bp.json` | WD4 |
| D-19 | Radius calibration table (or exact-key fallback record) | `results/S2/radius_calibration.json` | WD4 |
| D-20 | `EPCBase` with recorded energy/solver conventions (conditional) | `pccap/bases/epc.py`, `docs/epc_energy.md` | WD4/WD5 |
| D-21 | MODULAR-CONTROL fixture and PC-1 | `pccap/fixtures/modular_control.py`, `tests/test_pc1_planted.py` | Weekend or Tue 15 Sep AM |
| D-22 | Frozen shared `A` with screening log | `results/S2/A_screening.json` | WD5 |
| D-23 | B1/B3/B4 running with PC-10 parity | `pccap/baselines/`, `results/S2/baselines/` | WD5 |
| D-24 | Throughput profile and scope projections | `results/S2/throughput.json`, `docs/throughput_projection.md` | WD5 |
| D-25 | P1, P6 (and P2/P3/P4) on ePC (conditional) | `results/S1/P*_epc.json` | WD5 |
| D-26 | S1 and S2 stage reports with eligibility table | `results/S1/report.md`, `results/S2/report.md` | WD5 |
| D-27 | D1 decision memo and week-2 plan draft | `docs/D1_decision.md`, `docs/week2plan1.md` | WD5 |

---

## 5. Checkpoints and pass criteria (summary)

| Checkpoint | When | Pass criteria | If failed |
| --- | --- | --- | --- |
| CP-1 | Tue 8 Sep EOD | CUDA works; assets triaged; datasets hashed; scaffold committed; lead notified; conversion factor recorded | RV-1, RV-2, RV-3 as applicable |
| CP-2 | Wed 9 Sep EOD | All known-answer tests green; `BPBase` reproduces HF logits on 256 probes; PC-7 green | RV-4 |
| CP-3 = S0 exit | Thu 10 Sep EOD | All PC-2/4/5/6/9 and reproducibility tests green; smoke edit runs; base checksum unchanged; S0 report filed | RV-4 |
| CP-4 | Fri 11 Sep EOD | Manifests sealed; `b_m`; P2/P3/P5 on BP; radius table; ePC wrapper or blocking status | RV-5, RV-1 |
| CP-5 = D1 | Mon 14 Sep EOD | Section 0 definition of done | RV-6, RV-8, RV-9; D1 memo states what is incomplete and why |

---

## 6. Budget tracking

Ceilings are accelerator hours in A100-equivalents (Appendix B). Local hours = ceiling ÷ conversion factor `κ` (A100-equivalents per local GPU hour), measured in W1-1.3. Person time is not budgeted by the plan; this schedule assumes one primary executor with coding-agent support at roughly eight hours per working day.

| Stage | Ceiling (A100-h) | Local ceiling (÷ κ) | Spent (update daily) | Notes |
| --- | ---: | ---: | ---: | --- |
| S0 | 8 | TBD | 0 | Mostly CPU-bound tests; GPU use is smoke edits and identity checks |
| S1 | 12 | TBD | 0 | P1 on 2M tokens and P6 at 64 iterations dominate if ePC exists |
| S2 | 12 | TBD | 0 | Throughput profiling and baseline screening dominate |
| Week 1 total | 32 | TBD | 0 | |

Rules: stop at the ceiling and preserve checkpoints (Op. rule 12); unused S6 allocation may later fund core replication only under a logged amendment; the total never increases silently.

Back-of-envelope for U11 (to be replaced by measurement in W1-5.3): under C2 one token-prefix round costs about one forward, one backward, three partial probe forwards, and up to four candidate forwards, roughly nine forward-equivalents; with five rounds and an average answer of five tokens plus terminator that is on the order of 250 forward-equivalents per edit for learning, before immediate ES/GS/LS evaluation, which is greedy 32-token decoding without a KV cache over the edit prompt, its paraphrases, and its locality prompts. At a few milliseconds per short-prefix GPT-2 small forward on the local GPU, that is seconds per edit and hours per 3,000-edit run. Multiplied by 15 realization/order runs and four to six arms, the 3,000-edit zsRE scope is unlikely to fit in 36 A100-equivalent hours on this hardware. The plan's remedy is built in: choose the largest affordable prefix from the fixed candidate set, and if the smallest complete core comparison is unaffordable, report a feasibility result rather than an underpowered imitation (Appendix B). This is RV-8.

---

## 7. Unknowns register

Each unknown has an ID, why it matters, how it gets resolved, who resolves it, and the date by which it must be resolved or escalated. "Executor" is whoever runs the week; "Lead" is the human lead.

| ID | Unknown | Why it matters | Resolution path | Owner | Resolve by |
| --- | --- | --- | --- | --- | --- |
| U1 | Where are the production ePC checkpoint, its BP teacher, and the 5 × 10⁷-token distillation pipeline? Does the executor have access? | Without them Thread 1 (S1 ePC rows, S5, S6) cannot run. Thread 2 on GPT-2 small does not depend on them. | Ask the lead today; search any shared drives named in the reference documents. | Lead | CP-1; escalate at CP-4 |
| U2 | What architecture and size is the matched BP/ePC pair? GPT-2 small, or a smaller model (possibly the six-layer synthetic-grammar model)? | Appendix B: if the pair is smaller than GPT-2 small, the substrate comparison uses that pair and a **separate** BP-only GPT-2 small experiment tests the cap on a competent model; if the pair has no natural-language capability, the substrate comparison stays synthetic. This changes which S1 measurements are even defined (P1 on `H`, POS probe, LM drift). | Read the checkpoint config once located. | Lead / Executor | CP-1 |
| U3 | Framework of the ePC checkpoint: PyTorch, or FabricPC/JAX? | JAX means a JAX base wrapper with an explicitly implemented and tested cross-framework gradient path, and possibly no second derivatives (HVP diagnostics unavailable, which is allowed). | Inspect the checkpoint files. | Executor | CP-1; build decision by CP-3 (RV-2) |
| U4 | What compute is actually available beyond the local RTX 5070? What is the A100-equivalent conversion factor `κ`? | Every stage ceiling and the S4 scope choice depend on it. | W1-1.3 micro-benchmark; ask the lead about cluster or cloud access. | Executor / Lead | Provisional CP-1; measured by CP-5 |
| U5 | Location and state of causal-fibres v0.3 (joint block diagonalization, supplied-support sandbox), comcrit HVP code, the six-layer grammar fixture (R8/R9, E1–E2), RelaLeap harnesses, and the unlinked references [2] and [5]. | The grammar fixture is one of the three test beds (S3, S4); causal-fibres and comcrit are optional (P4 description, D.9 HVP). | Ask the lead; check Drive folders adjacent to [1], [3], [4]. | Lead | CP-1; grammar fixture is needed by Tue 15 Sep |
| U6 | The production ePC energy function, clamp convention, solver, step size, precision matrices, state reset, and stopping behaviour. | F.6: "a bare instruction to run eight unspecified settle steps is not executable." SE-E and every P6 number depend on this. | Read the implementation once located; document in `docs/epc_energy.md`; compare to the D.6 default and record any difference as an explicit choice. | Executor | CP-4 |
| U7 | Exact zsRE and CounterFact releases and preprocessing to commit (dataset IDs, target strings, aliases, prompt forms), and their licences. | E.2 requires committing source release and preprocessing revision; results are not reproducible otherwise. | Default: the zsRE editing split used by GRACE [7] (originating from Levy et al. [10]) and CounterFact from the ROME release [9]. Record whichever is used. | Executor | WD1 |
| U8 | Does the GRACE reference implementation run under Python 3.11 and a current PyTorch, and does it support a byte budget? | B4 must be a validated adaptation, not a reimplementation, for comparative claims (Op. rule 11). | Clone, pin commit, run its smoke test; if unsupported, adapt minimally and disclose (eviction adaptation is expected). | Executor | WD5 |
| U9 | Does any positive radius achieve ≤ 1% unrelated false-fire on GPT-2 small at each of the three bank sites? | If not, the pilot uses exact-key retrieval, which means paraphrases will not fire and GS is structurally near zero for the cap; that changes what the routing contrast can show. | W1-4.7 calibration. | Executor | CP-4 (RV-5) |
| U10 | Can any of `A ∈ {0.03, 0.1, 0.3}` achieve immediate acquisition (token CE ≤ 0.1 nats within five rounds) on real edits with GPT-2 small? | If none functions, S2 says: complete the diagnostic before proposing a changed protocol, and consume no confirmatory examples. | W1-5.1 screening with step-level decision records. | Executor | CP-5 (RV-6) |
| U11 | Actual cost per complete edit under each router, and per evaluation, on the available hardware. | Decides the affordable stream lengths at S4 and whether the smallest complete core comparison fits. | W1-5.3 throughput profile. | Executor | CP-5 (RV-8) |
| U12 | Who is the human lead for scope decisions, and what is the turnaround for questions? | Several revision points route to the lead. | Confirm on WD1. | Executor | WD1 |
| U13 | Does a PyTorch build with Blackwell (`sm_120`) kernels install cleanly on this Fedora system with the present driver? | Without it there is no local GPU work at all. | W1-1.2. Fallback: CPU for S0 tests (fine), and escalate compute (U4). | Executor | WD1 morning |
| U14 | Do the inherited claims reproduce (teacher KL near 3 × 10⁻⁵, cosine > 0.998 between settled errors and adjoints, error mass less concentrated in the last block than R8/R9)? | §2.2 and Appendix H: these are starting claims, not verified results; everything built on the ePC base is conditional on S0/S1 reproduction. | W1-5.4. | Executor | CP-5 or first day ePC assets are available |
| U15 | Is the HF GPT-2 residual-stream hook placement exactly F.1's convention, and do BP and ePC wrappers agree on it? | A one-off in hook placement silently changes every bank's site. | W1-2.1 asserts pre-`ln_f` identity and block indices; the ePC wrapper reuses the same assertion. | Executor | CP-2 |
| U16 | Near-neighbour, composition, and correction challenge sets (≥ 100 cases each, E.2): do usable sources exist, or must they be constructed? | Needed for S4 challenge evaluations and the correction-track slot-retirement path; not needed in week 1 but the construction cost should be known at D1. | Survey during W1-4.1; estimate in the D1 memo. | Executor | CP-5 (estimate only) |
| U17 | Do the answers of the selected dev edits fit within 32 tokens, and what fraction is excluded? | Exclusions must be counted before any arm runs. | W1-2.6 / W1-4.1. | Executor | CP-4 |

---

## 8. Revision points

Each revision point names the trigger, what changes, what does not change, and who decides. "Executor decides" means a logged development choice; "Lead decides" means a scope change per Operating rule 5.

### RV-1: ePC assets not located (trigger: CP-1, hard stop at CP-4)

- **Change:** WD4 task W1-4.8 and WD5 task W1-5.4 are dropped from week 1. The S1 report contains BP rows only and an explicit "ePC base: unavailable (reason), not failed" line in the eligibility table. Week-2 planning marks S5 at risk and S6 as not authorizable.
- **Does not change:** Thread 2 in full. The plan is explicit that the BP programme continues if ePC is unavailable (§4, §10 D1).
- **Decides:** Executor for week 1; Lead on whether to keep pursuing ePC into week 2 or to formally scope the month as BP-only.

### RV-2: ePC assets are JAX-only (trigger: U3 resolved at CP-1)

- **Change:** allocate at most one working day (WD4) to a JAX `EPCBase` wrapper with an explicitly implemented cross-framework gradient path and a test that the path is differentiable end to end. If not working by CP-4, ePC moves to week 2 with a fixed one-day cap there, and RV-1 applies for week 1.
- **Does not change:** no time is spent optimizing FabricPC/JAX (§3.1: not a deliverable).
- **Decides:** Executor.

### RV-3: local GPU is the only compute (trigger: U4 at CP-1)

- **Change:** record `κ` and convert all ceilings. Expect the affordable confirmatory scope to be the 300-edit prefix, possibly 1,000. Prioritize measuring throughput early (weekend W1-B.3). Note in the D1 memo that a 3,000-edit zsRE scope is likely infeasible, with the projection.
- **Does not change:** the candidate stream-length set, the number of realizations and orders, and the rule that scope is chosen from throughput with 25% headroom. Do not reduce realizations or permutations to fit; that is the lead's call and the plan prefers a feasibility result over an underpowered sweep (Appendix B).
- **Decides:** Lead, at D1, if even the smallest complete core comparison does not fit.

### RV-4: S0 tests not green on schedule (trigger: CP-2 or CP-3)

- **Change:** slip S0 by one day, consuming the weekend buffer. S1 measurements that do not use the cap's update path (P2, P3, P5 unit-direction search) may proceed on WD4 in parallel with cap fixes. S2 calibration and throughput wait for CP-3.
- **Does not change:** no experimental run starts before the four pre-run invariants pass (S0 text). No threshold or tolerance is relaxed to get a pass (Op. rule 5).
- **Decides:** Executor. If the slip exceeds two days, tell the lead: D1 moves to Wednesday 16 September and week 2 compresses.

### RV-5: no positive radius meets the 1% false-fire criterion (trigger: W1-4.7)

- **Change:** pilot with exact-key retrieval, record the limitation, store the whole candidate table. Add to the D1 memo that GS for cap arms is then structurally near zero on paraphrases, so the primary endpoint (endpoint RET-GS) would mostly measure exact-prompt retention. Investigate whether the false-fire rate is driven by a particular bank (late banks are more semantically specific) before proposing anything.
- **Does not change:** the 1% criterion, the tie-break rule, the grid. No per-arm radius tuning.
- **Decides:** Executor for the pilot; Lead if a protocol change (for example, a different key normalization) is proposed, and only after the diagnostic is complete and documented.

### RV-6: no step-budget candidate functions (trigger: W1-5.1)

- **Change:** complete the diagnostic first: per-round decision records showing whether failures are no-direction, probe-rejected, candidate-rejected, conflict, or eviction; check `b_m` scale and the acceptance threshold arithmetic. Report to the lead with at most three diagnoses and the cheapest test separating them (Op. rule 5).
- **Does not change:** the candidate set is not extended, `τ_edit` is not raised, and no confirmatory examples are consumed (S2).
- **Decides:** Lead on any protocol change.

### RV-7: GRACE reference does not run or cannot be validated (trigger: W1-5.2)

- **Change:** if minimal adaptation fixes it, disclose the changes and run PC-10. If a reimplementation is unavoidable, label it as such, test against the reference on shared inputs where any part of it runs, and mark comparative claims against B4 as provisional in the S2 report.
- **Does not change:** B4 remains a required S4 comparator; the plan forbids a hidden untuned comparator labelled state of the art.
- **Decides:** Executor for adaptation; Lead if B4 must be dropped or replaced.

### RV-8: throughput projection shows the smallest complete core comparison does not fit S4's ceiling (trigger: W1-5.3)

- **Change:** the D1 memo presents the projection per candidate scope and arm, and states which scopes fit with 25% headroom. Options for the lead, in the order the plan prefers: obtain more compute (U4); drop optional arms first (C0's long extension, B0/B1 curves, all optional experiments); accept the 300-edit prefix; or report a feasibility result for editing and concentrate the core routing comparison on the synthetic beds.
- **Does not change:** the executor does not shrink realizations or orders, switch the primary endpoint, or reduce the number of required contrasts.
- **Decides:** Lead at D1.

### RV-9: ePC fails P1 fidelity or a P2/P3 alert fires (trigger: W1-5.4)

- **Change:** fidelity failure → the base is ineligible for matched-fidelity claims; SE-A vs SE-E remains interpretable and is kept; the eligibility table says exactly this. A geometry or localization alert → run the fixed diagnostic named in D.2/D.3 and report it; do not exclude the base or change any number.
- **Does not change:** the thresholds (1e−3 nats, 0.9 rank ratio, 2-point probe drop, 0.4 final-block share).
- **Decides:** Executor records; Lead decides whether S6's deficit statement is written in week 2.

### RV-10: a specification defect is found (trigger: any day)

- **Change:** log it in `docs/spec_defects.md` with both readings and the chosen resolution; if the two readings would produce different runs, do not run either until resolved; ask the lead if the resolution affects a threshold, an endpoint, or an arm definition.
- **Decides:** Executor for resolutions that do not touch scientific thresholds; Lead otherwise.

### RV-11: the weekend is not worked (trigger: Saturday morning)

- **Change:** W1-B.1 (MODULAR-CONTROL fixture, PC-1) moves to Tuesday 15 September morning and S3 starts that afternoon. Any slip from WD2–WD4 pushes D1 to Tuesday 15 September EOD. Record the new dates in Section 10.
- **Decides:** Executor.

---

## 9. Scope guards and traps for week 1

These are rules from the plan that are easiest to violate during a fast development week.

1. **Development data only.** S0–S3 use development examples and at most the listed calibration candidates. The confirmation manifests are sealed on WD4 and not read (Op. rule 3).
2. **Log every configuration tried,** including failures. A configuration chosen by looking at test data is a result measured on its own training data.
3. **One shared learning rule.** `A`, radii, `b_m`, and the acceptance thresholds are common to C0/C1/C2/CR within a base and read variant. No per-arm tuning.
4. **No silent fallback.** Nonfinite values, undefined ratios, unreachable targets, and ambiguous conflicts get outcome codes with operands, never a substituted number (Op. rule 8).
5. **Evaluation is read-only.** Predict paths must not touch usage counts, radii, keys, replay, or RNG-dependent learning state (E.2, PC-8).
6. **No KV cache in the reference decoder.** A cache optimization may be reported separately only after parity is verified (E.2).
7. **Frozen base, behaviourally verified.** Checksums before and after every run, plus the 256-probe cap-off identity test (PC-2). A checksum alone is not an identity test.
8. **Charge everything.** Probes, rejected candidates, backward passes, settling, replay tokens, cap-disabled feature passes. Query cost and learning cost in separate columns.
9. **Do not call cap v0 a predictive-coding cap.** It is a PC-motivated gated activation memory (§2.3). Reports use that wording.
10. **Do not call eight settle iterations "settled"** unless `r_64 ≤ 1e−3` and terminal changes are small (D.6). Otherwise the label is "finite-iteration error credit".
11. **A disappointing result is not a bug.** Correctness controls test code; scientific outcomes test hypotheses (Op. rule 2). Router accuracy, beating LoRA, and PCA patterns are not implementation gates (F.5).
12. **Hook placement.** Block output before the next block; final block before `ln_f`. Assert it in a test rather than trusting a library's hidden-state tuple (U15).
13. **Slot counts follow from bytes,** not the other way round. 2,048 per bank for R-h three-bank arms, 6,144 for C0, 1,374 per bank for `d_k = 2d`, all derived from `B_cap` and the metadata allowance, recomputed if actual metadata exceeds 128 bytes.
14. **Realizations and orders are separate seeds.** Realizations 0, 1, 2 change the sampled items; orders use seeds 100–104; cap initialization, router, and replay seeds are named separately (Appendix B).

Candidate spec-defect entries to seed `docs/spec_defects.md` on WD1 (none confirmed; each needs a reading and a resolution):

- S1 uses a 2 × 10⁶-token held-out set `H` for P1, while D.8 uses a 10⁶-token WikiText-103 sample for LM drift. Resolution assumed here: two distinct committed sets. Confirm and record.
- S2 names 300 development edits and ≥ 1,000 unrelated prompts; D.5 uses 200 `Q` and 200 `U`. Resolution assumed: D.5's sets are subsets of the S2 development pool, fixed by manifest. Confirm.
- The correction-track slot-retirement rule (F.2) is the only metadata-assisted operation and is "available only on that track"; the main-run router must not receive fact identity (E.2). Confirm that the owner-edit digest stored in slots is never read by the router outside the correction track.

---

## 10. Revision log for this plan

| Version | Date | Change | Reason |
| --- | --- | --- | --- |
| v1 | Tue 8 Sep 2026 | Initial plan written from the 7 September revised PDF, its summary, and the reference list. | Start of week 1. |

Update this table at every checkpoint. If a revision point fires, add a row naming the RV, the trigger evidence, and the new dates.

---

## 11. Questions for the lead (send on WD1)

1. Where are the production ePC checkpoint, its BP teacher, and the distillation pipeline, and may this executor access them? (U1)
2. What is the architecture and size of that matched pair, and what framework is it in? (U2, U3)
3. Where are causal-fibres v0.3, comcrit, the six-layer grammar fixture, and the RelaLeap harnesses? Can the unlinked documents [2] and [5] be shared? (U5)
4. Is there compute beyond a local 12 GiB RTX 5070? If an A100 or equivalent is available, may the conversion benchmark be run there? (U4)
5. Confirm you are the decision-maker for scope changes, and the expected turnaround for questions raised at checkpoints. (U12)
6. Is the executor expected to work the weekend, or should D1 be planned for Tuesday 15 September? (RV-11)

---

## 12. References used in this plan

Numbers in brackets follow [`footnotes.md`](footnotes.md). Week 1 draws on: [6] for the ePC settling procedure and its reverse-mode cost; [7] for the GRACE reference implementation and the zsRE editing split; [9] for CounterFact and its paraphrase/neighbourhood sets; [10] for zsRE's origin; [11] for LoRA (B1/B3); [1], [3], [4] as background for the routing hypothesis and order-effect diagnostics. [12] (EWC) and [8] (WISE) are optional baselines not built in week 1. [13] motivates the late-acquisition metric, which is defined in the harness this week but measured in weeks 3–4.
