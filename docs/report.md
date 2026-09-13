# Integrated report — cap v0 on BP and regenerated-ePC substrates (S8-03, draft 1)

Drafted 2026-09-13 ≈ 05:30 EDT by the orchestrator. Contract: `docs/pc_cap_month_plan_readable.pdf` (sha256 `9a2b6468…`) as
executed under `docs/updated_plan2.md` and its deltas (plans 3–8). Frozen protocol: `manifests/frozen.json`
(`frozen-confirmatory-v2`, DEC-027). Decisions DEC-000…028 (`docs/decisions.md`); spec defects SD-1…22 (`docs/spec_defects.md`).
Every number below is read from a results file named in the section; reproduction commands are in `docs/REPRODUCE.md`.
Sections marked *pending* are filled when the S8-02 ablations finish and the final-tree reproduction audit runs.

## 1. Summary

The month asked one confirmatory question: does the three-bank radius-gated cap with learned routing (C2) retain paraphrase
generalization (RET-GS) at least 0.02 better than the single-bank cap (C1) and than random routing (CR), on sealed editing
streams, without losing acquisition or locality? **It does not.** On zsRE, C2 retains about three points *less* than C1 in
every realization (Δ = −0.030, 97.5% interval [−0.041, −0.019]) and is indistinguishable from random routing (+0.000
[−0.013, +0.018]). On CounterFact and on the replacement grammar the primary endpoint sits at a floor for every cap arm
because those streams run with exact keys (SD-18, SD-20), so they cannot discriminate; the grammar's frozen classification is
additionally `incomplete` because of an evaluation-seed defect (SD-22), with a labelled supplement that agrees with the floor
reading. The matched-fidelity substrate comparison shows that converting the base to the regenerated ePC checkpoint changes
nothing under the adjoint credit (SE-A ≈ SB within 0.002), and that the settled-error credit trades a third of acquisition for
a two-point retention gain below the margin. Order effects are real where keys retrieve (zsRE near-neighbour pairs damage
each other by 2.4 nats on average) and absent where they do not. The B4 (GRACE) contrast was not run: element-wise value
parity across frameworks failed and the pre-registered sensitivity control did not qualify the output-level form (DEC-020/
SD-21). No threshold, endpoint, arm, contrast or budget was changed after the freeze; every deviation is listed in §9.

## 2. What was built (S0–S3, GRAM, REG)

- A JAX functional GPT-2 small base with deterministic settings (DEC-001/007; TF32 off; `pccap.assert_determinism()` at every
  run), reference-checked against stored PyTorch outputs (SD-14; max |Δlogit| ≤ 1e-3, argmax agreement).
- The cap (three radius-gated banks at blocks 3/7/11; routers C0/C1/C2/CR; byte ceiling B_cap = 6144·(8d+128); transactional
  candidate search; SD-16/17/18) with 33 metric and 10 process controls (`docs/controls.md`, S3-01).
- Predictive-coding infrastructure on FabricPC (DEC-002): ePC inference with an error-optimizing solver, the KD energy and
  weight phase of the sibling's recipe, re-implemented line by line (DEC-003, SD-15), and the JAX distillation driver.
- **REG-02:** the ePC checkpoint regenerated on 50M tokens in 12.2 GPU-h (DEC-014/015; stage boundaries identical to the
  sibling's run), preflighted (REG-03) and **eligible for matched-fidelity claims** (S1-01: mean KL 2.9e-5 nats/token on H,
  rule ≤ 1e-3). Substrate properties P2/P3/P5/P6 on the ePC weights equal the BP rows to three decimals; P6 labels the
  eight-iteration credit "finite-iteration error credit" (r₆₄ > 1e-3).
- **The replacement grammar** (PA-2; GRAM-01/02, DATA-06/07): a 64-symbol generator with eight contexts, two shared and
  eight private mechanisms, a 6-block d = 128 base trained on the CPU (held-out accuracy 0.99), streams, tracing pairs and
  latent paraphrases (SD-20). P4 on it (S1-04, D.4 error space): mechanism kinds occupy distinct but overlapping error
  subspaces (cross-kind overlap 0.27–0.35 vs 0.125 chance; held-out transfer 0.96–0.99 by the own basis vs 0.21 by the other
  kind's); the eight private mechanisms share one error subspace (0.93), so error geometry distinguishes kinds, not contexts.
- Development editing pools with the E.2 teacher filter (DATA-01), sealed confirmation realizations and orders (DATA-02/02a),
  radius calibration at 1% false-fire (S2-01; per dataset, SD-17), the aggregate step A = 0.3 (DEC-012), throughput profiles
  with reconcilable ledger deltas (S2-06), the D1 scope (S2-07) and the D2 development memo (S3-06).

## 3. The frozen protocol (S4-01/02)

Scope zsRE 1000 / CounterFact 300 / grammar 256 sequences per task (8 tasks), three sealed realizations × five committed
orders, arms C0 (300-edit initial scope), C1, C2, CR(learned distribution, DEC-018), B3 (LoRA + replay at the prescribed
rate, DEC-017); B4 unavailable (DEC-020); B0/B1 development references. Budget A = 0.3, ε = 0.01, R = 5, τ = 0.1;
checkpoints 100/300/1000/end; primary endpoint RET-GS with margin 0.02, ES −0.02 and LS −0.01 non-inferiority; 97.5%
paired-cluster bootstrap over realizations with orders kept together (DEC-009). Allowances: 2,400 s per run, 97,200 s S4,
64,800 s S5 (S4-02). The freeze was written twice: v1 was superseded before any result by a loader defect (DEC-026); v2 ran.

## 4. Confirmatory execution (S4-03/04)

210 runs, all complete, 11.49 accelerator hours (42% of the S4 ceiling after headroom), no correctness failure, no resource
stop, no rerun; every run carries the frozen identities of the base, tokenizer and (for the grammar) weights, and the base
hash unchanged before and after (`results/S4/queue_summary.json`, `results/S4/frozen-confirmatory-v2-84126123/`). The
confirmatory path had been reviewed four times before it ran (R2, V, V2/V3, V4) and every finding repaired with a control.

## 5. Frozen paired analysis (S4-05/06; `docs/D3_decision.md`)

| dataset | C2 − C1 Δ RET-GS [97.5%] | C2 − CR | ES non-inf. | LS non-inf. | classification |
| --- | --- | --- | --- | --- | --- |
| zsRE | −0.030 [−0.041, −0.019] | +0.000 [−0.013, +0.018] | yes / yes | no / yes | negative |
| CounterFact | 0.000 (floor) | 0.000 (floor) | yes | yes | negative (uninformative) |
| grammar | — | — | — | — | incomplete (SD-22); supplement: −0.000 [−0.003, +0.002], negative |

Descriptive means over the 15 runs per cell:

| dataset | arm | ES | RET-ES | RET-GS | LS | drift ratio | accel s/run |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| zsRE | C0 (300) | 1.000 | 0.992 | 0.356 | 0.981 | 1.000 | 123 |
| zsRE | C1 | 0.998 | 0.524 | 0.139 | 0.985 | 1.001 | 503 |
| zsRE | C2 | 0.998 | 0.302 | 0.109 | 0.965 | 1.001 | 316 |
| zsRE | CR | 0.999 | 0.344 | 0.109 | 0.972 | 1.000 | 277 |
| zsRE | B3 | 0.209 | 0.171 | 0.120 | 0.009 | 1.750 | 208 |
| CounterFact | C0/C1/C2/CR | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 215–259 |
| CounterFact | B3 | 0.224 | 0.217 | 0.098 | 0.000 | 6.468 | 116 |
| grammar | C0 | 1.000 | 1.000 | 0.286 | 1.000 | 1.000 | 40 |
| grammar | C1 | 0.698 | 0.690 | 0.286 | 1.000 | 1.000 | 134 |
| grammar | C2 | 1.000 | 1.000 | 0.286 | 1.000 | 1.000 | 74 |
| grammar | CR | 0.900 | 0.895 | 0.286 | 1.000 | 1.000 | 58 |

Readings (descriptive, D3 §3): at 1,000 zsRE edits under the byte ceiling, retained ES falls with the number of banks
written (C0 0.99, C1 0.52, C2 0.30, CR 0.34): the three-bank cap evicts more of what it learned; on the grammar the routing
contrast appears in RET-ES (C2 = C0 = 1.00, CR 0.90, C1 0.69), the development matrix's pattern, while RET-GS is a floor;
B3 acquires a fifth of the edits, has no locality and drifts the language model; no cap arm drifts. Comparable compute:
C1 costs 2.7–2.8× C2's update time on the editing streams, CR and C0 0.7×; no arm is within the 20% band, and C2 loses on
zsRE while using less compute than C1, so the resource-matched view does not rescue the claim. Order variation across the
five committed orders (S7-03): RET-GS std ≤ 0.023 for every cap arm on zsRE, 0 on CounterFact, ≤ 0.008 on the grammar.

## 6. Substrate comparison (S5; `results/S5/report.md`)

SB (= the S4 C1 runs), SE-A (regenerated ePC base, adjoint credit), SE-E (ePC base, eight-iteration settled-error credit),
on the same streams; 60 runs, 8.9 accelerator hours. zsRE: SE-A − SB Δ RET-GS −0.002 [−0.004, −0.000], ES +0.000, LS −0.021
(no practical difference: the converted base reproduces BP under a common credit rule); SE-E − SE-A Δ RET-GS +0.019
[+0.012, +0.025] with ES −0.336 [−0.344, −0.324] (a real but sub-margin retention gain on the edits it holds, at the cost of
a third of acquisitions within the frozen round budget). CounterFact: identically zero (floor). Both negative by policy.

## 7. Order effects on committed checkpoints (S7-01/02; `results/S7/summary.md`)

100 fixed pairs (CounterFact 75; DEC-023) per checkpoint, stratified shared / private / near-neighbour, from data independent
of every confirmatory stream; cloned complete state; both orders. zsRE C2 at 300 edits: mean damage (nats, both orders)
near-neighbour +2.41 (harmful in 33% of pairs), shared +0.69 (16%), private +0.16 (3%); D_ij 0.040 / 0.041 / 0.004.
CounterFact C2 endpoint and grammar C2 at ≈ task 4 and task 8: zero damage and zero divergence in every stratum — with exact
keys, updates of distinct items commute. Natural-language strata are operational proxies (`manifests/dev/s7_pairs.json`).

## 8. Exploratory ablations (S8-02; `results/S8/ablations.json`; development data, 3 realizations × 2 orders; not confirmatory)

**(b) Byte ceiling at 0.5×, 1× and 2× (zsRE, 300 development edits, C1 and C2).** Every metric is identical across the three
factors (C1: ES 0.999, RET-ES 0.849, RET-GS 0.257, LS 0.983, 17.3 MB occupied; C2: 0.999 / 0.548 / 0.191 / 0.983, 6.1 MB):
at 300 edits the ceiling (38.5 MB; 19 MB at half) never binds, so this ablation cannot attribute the confirmatory C1 > C2
retention gap at 1,000 edits to capacity. What it does show is that the gap is already present with no ceiling pressure at
all — C2 retains 0.55 of its edits against C1's 0.85 with a third of C1's occupancy — so the loss is interference among
retrievals within the three banks, not eviction. A binding-ceiling ablation would need factors ≤ 0.25 or a larger
development pool; it was not added post hoc.

**(c) Grammar with paraphrase keys at a 5% false-fire radius (C1, C2, CR).** *pending the run.* The 5% calibration itself
already answers the question: no positive radius exists at 5% either. On the grammar the paraphrase-to-edit and
unrelated-to-edit key distances overlap almost completely (bank 1: paraphrase quantiles 0.09 / 0.20 / 1.05 vs unrelated
0.06 / 0.30 / 0.71), and the smallest grid radius fires on 5.4% of unrelated prefixes while covering 4.4% of paraphrases.
The grammar's RET-GS floor is therefore a property of the R-h key on this base — "same latent, different filler" is not a
neighbourhood in key space — not of the 1% criterion. The runs at "5% radius" are consequently identical to exact keys.

**(a) Stable keys versus edited keys:** not run (needs the optional read variant R-h0, CAP-08).

## 9. Deviations, unscheduled and failed work (Appendix G §8)

| item | what happened | record |
| --- | --- | --- |
| Framework | JAX only, FabricPC for PC, sibling read-only (lead directives) | DEC-001…004, SD-13/14/15 |
| ePC checkpoint absent | regenerated (PA-1; bound raised to 120 GPU-h; 12.2 h used) | DEC-014/015, REG-00…03 |
| R8/R9 grammar absent | replacement grammar (PA-2), provisional until the clock passed | GRAM-01/02, DATA-06/07, SD-20 |
| B4 | element-wise value parity failed; sensitivity control did not qualify form (b); localization: the reference's fp32 reductions | DEC-020, SD-21, `logs/grace_*` |
| Freeze v1 | superseded before any result: loader refused editing realizations because of the grammar's `.npz` binding | DEC-026 |
| Grammar paraphrase seeds | per-process hash salt → paraphrase sequences differ between runs; 0–3 undefined RET-GS per cell; frozen classification `incomplete` | SD-22 |
| Post-freeze source changes | analysis tree only (grammar expected inventory; S7 runner), versioned | DEC-028 |
| S6 | closed for the month (REG charged to its allocation) | DEC-022 |
| S7 CounterFact shared stratum | 9 pairs (only shared-subject records outside sealed pools) | DEC-023 |
| Selection rule | one subset per realization across orders | SD-19 |
| Key equality tolerance | 1e-4 (batched kernels) | SD-18 |

## 10. Budget (local RTX 5070 hours; κ = 1 provisional, PA-3)

S0 0.41 · S1 0.18 · S2 0.84 · S3 0.06 · S4 11.49 · S5 8.94 · S6 (REG) 12.32 · S7 0.04 · S8 0.34 (so far) — total ≈ 34.6 of 144
A100-h across stages; no stage exceeded its ceiling. Wall-clock ran 1.5–3.7× accelerator time on this host.

## 11. Reproduction and artifacts

`docs/REPRODUCE.md` (audited on the CPU by Lane P; final-tree audit pending, S8-01); manifests in `manifests/`
(`frozen.json`, `analysis_versions.json`, `dev/`, `confirm/` sealed, `grammar/`); results per stage in `results/`; task
records in `docs/tasks/`; reviews and responses in `docs/*_review*.md` and `logs/`.
