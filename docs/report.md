# Integrated report — cap v0 on BP and regenerated-ePC substrates (S8-03, draft 1)

This report preserves the v2 results reviewed at snapshot `170fad3`. During P2/X2, DEC-029/030 authorized and froze the grammar-only v3 rerun (`frozen-confirmatory-v3-163d04e2`); zsRE, CounterFact and S5 retain their v2 identities. V3 outcomes are not included here. See `logs/p2_x2_v3_transition/review.md` for the transition checks and the residual seven-item paraphrase coverage finding.

Drafted 2026-09-13 ≈ 05:30 EDT by the orchestrator. Contract: `docs/pc_cap_month_plan_readable.pdf` (sha256 `9a2b6468…`) as
executed under `docs/updated_plan2.md` and its deltas (plans 3–8). Reviewed v2 protocol: `manifests/archive/frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json`
(`frozen-confirmatory-v2`, DEC-027). Decisions DEC-000…028 (`docs/decisions.md`); spec defects SD-1…22 (`docs/spec_defects.md`).
Every number below is read from a results file named in the section; reproduction commands are in `docs/REPRODUCE.md`.
P2's final-tree CPU reproduction audit and X2's counter-review are in `logs/reproduce_final.md` and `logs/review_report_draft1.md`. These reviews do not constitute the lead's T4 / CP-F approval.

## 1. Summary

The month asked one confirmatory question: does the radius-gated cap with probe-and-choose routing (C2: one bank per round, chosen by the best positive probe) retain paraphrase
generalization (RET-GS) at least 0.02 better than the fixed three-site schedule (C1: writes at all three banks every round, the aggregate bound divided among them) and than random bank choice (CR), on sealed editing
streams, without losing acquisition or locality? **The primary claim is not supported on any dataset.** On zsRE, C2 retains about three points *less* than C1 in
every realization (Δ = −0.030, 97.5% interval [−0.041, −0.019]) and its difference from random routing has an interval spanning zero (+0.000
[−0.013, +0.018]); equivalence is not established. On CounterFact and on the replacement grammar the primary endpoint sits at a floor for every cap arm
because those streams run with exact keys (SD-18, SD-20), so they cannot discriminate; the grammar's frozen classification is
reported from the version-3 rerun after the evaluation-seed defect (SD-22) was fixed: complete, negative, with the same floor; the v2
grammar row (`incomplete`, with its labelled supplement) is archived for the record. Under adjoint credit, SE-A's RET-GS is 0.002 below SB, but locality non-inferiority is not established; this is not a general equivalence result. Settled-error credit reduces acquisition by 0.336 for a RET-GS point gain of 0.0189, whose interval spans the 0.02 margin; the contrast is negative because acquisition fails. On the tested S7 checkpoints, zsRE near-neighbour update directions cause 2.4 nats mean damage; CounterFact and grammar show zero damage on the evaluated prefixes, while all complete endpoint states differ between orders. The B4 (GRACE) contrast was not run: element-wise value
parity across frameworks failed and the pre-registered sensitivity control did not qualify the output-level form (DEC-020/
SD-21). The saved confirmatory configurations retain the frozen thresholds, endpoints, arms, contrasts and allowances. Post-confirmatory ablations and source changes are disclosed separately in §8–§9.

## 2. What was built (S0–S3, GRAM, REG)

- A JAX functional GPT-2 small base with deterministic settings (DEC-001/007; TF32 off; `pccap.assert_determinism()` at every
  run), reference-checked against stored PyTorch outputs (SD-14; max |Δlogit| ≤ 1e-3, argmax agreement).
- The cap (three radius-gated banks at blocks 3/7/11; routers C0/C1/C2/CR; byte ceiling B_cap = 6144·(8d+128); transactional
  candidate search; SD-16/17/18) with known-answer metric tests and process controls PC-1…PC-10 (`docs/controls.md`, S3-01); PC-10 remains unqualified. The historical count of 33 refers to the original known-answer test run, not 33 distinct process controls.
- Predictive-coding infrastructure on FabricPC (DEC-002): ePC inference with an error-optimizing solver, the KD energy and
  weight phase of the sibling's recipe, re-implemented line by line (DEC-003, SD-15), and the JAX distillation driver.
- **REG-02:** the ePC checkpoint regenerated on 50M tokens in 12.2 GPU-h (DEC-014/015; stage boundaries identical to the
  sibling's run), preflighted (REG-03) and **eligible for matched-fidelity claims** (S1-01: mean KL 2.9231e-5 nats/token over 1,999,872 scored H positions, archived at `git show 25c988b:results/S1/P1_epc.json`;
  rule ≤ 1e-3). The current P1 filename is a 199,680-position follow-up (2.8746e-5). P2/P3/P5/P6 are broadly similar but do not equal the BP rows to three decimals; for example P5 bank-1 target reach is 0.950 BP versus 0.945 ePC. P6 labels the
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

210 runs, all complete, 11.49 accelerator hours (42.6% of the S4 ceiling after headroom), no correctness failure, no resource
stop, no rerun; every run carries the frozen identities of the base, tokenizer and (for the grammar) weights, and the base
hash unchanged before and after (`results/S4/queue_summary.json`, `results/S4/frozen-confirmatory-v2-84126123/`). The
confirmatory path had been reviewed four times before it ran (R2, V, V2/V3, V4) with controls for the execution defects identified in those rounds. The drift-coverage limitation and later reporting findings remain disclosed below.

## 5. Frozen paired analysis (S4-05/06; `docs/D3_decision.md`)

| dataset | C2 − C1 Δ RET-GS [97.5%] | C2 − CR | ES non-inf. | LS non-inf. | classification |
| --- | --- | --- | --- | --- | --- |
| zsRE | −0.030 [−0.041, −0.019] | +0.000 [−0.013, +0.018] | yes / yes | no / not established | negative |
| CounterFact | 0.000 (floor) | 0.000 (floor) | yes | yes | negative (uninformative) |
| grammar (v3 rerun, DEC-029/030/032) | 0.000 [0, 0] (floor) | 0.000 [0, 0] (floor) | yes (C2 acquires +0.301 over C1, +0.100 over CR) | yes | **negative (complete: 2044/2047/2046 of 2,048 items per realization; 4/1/2 paraphrase-less items excluded by the disclosed inventory rule)** |

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

Readings (descriptive, D3 §3): at 1,000 zsRE edits, C1 retains ES 0.524, C2 0.302 and CR 0.344. C0's 0.992 uses a shorter 300-edit stream. These endpoint means do not identify eviction as the cause: accepted-event logs contain mean eviction counts 2,801 for C1 and 1,085 for C2, and counts of slot events do not identify forgotten edits. On the grammar, the RET-ES routing pattern matches development, while the RET-GS means all round to 0.286 under differing paraphrases (SD-22).

B3 has poor locality, and its editing drift ratios are 1.75/6.47. The editing drift assay recorded with every run covers 4,064 scored positions, not the full validation split SD-3 asks for; a labelled full-split supplement on the zsRE realization-0 endpoints (`results/S4/drift_supplement.md`, 245,110 positions) gives perplexity ratios C0 1.0010, C1 1.0019, C2 1.0036, CR 1.0030 and B3 1.884, so the cap arms' drift is below 0.4% on the whole split and the recorded assay's band holds. Near-one cap means do not establish zero drift; zsRE C2's maximum per-run ratio is 1.00929. The grammar ratio uses a separate 4,032-position base-grammar assay. A versioned full-validation remedy remains unresolved.

C2−CR locality non-inferiority is not established: Δ LS −0.007 [−0.026, +0.013], versus the −0.01 margin. The primary classifications are unchanged. Comparable-compute ratios are tabulated in D3 §4: no comparator lies within 20% of C2. Lower update cost plus worse equal-exposure retention does not rule out a different equal-time tradeoff; the current resource views do not establish paired RET-GS superiority at equal cost. Order variation across the five committed orders (S7-03): maximum RET-GS standard deviation is 0.0277543 on zsRE, 0 on CounterFact and 0.00440532 on the grammar.

## 6. Substrate comparison (S5; `results/S5/report.md`)

SB reuses the S4 C1 runs; SE-A uses the regenerated ePC base with adjoint credit, and SE-E uses that base with eight-iteration finite-error credit. The 60 S5 confirmatory runs consume 8.88985 recorded accelerator hours. On zsRE, SE-A−SB RET-GS is −0.0020 [−0.0040, −0.0002], ES +0.000067, and LS −0.02133 [−0.041, +0.004]. Acquisition non-inferiority passes; locality non-inferiority is not established. A small RET-GS difference is not a general equivalence result.

SE-E−SE-A RET-GS is +0.01887 [+0.0120, +0.0248]: the point is below the 0.02 margin, but the interval extends above it. ES is −0.3362 [−0.344, −0.324], so the frozen negative classification is driven by lost acquisition. RET-GS is measured over the endpoint inventory, not only acquired edits. CounterFact's paired differences are zero on RET-GS/ES/LS; absolute RET-GS is zero and ES/LS are one. Both substrate contrasts remain negative by the frozen rule.

## 7. Order effects on committed checkpoints (S7-01/02; `results/S7/summary.md`)

The fixed inventory supplies 100 pairs per checkpoint, or 75 for CounterFact (DEC-023), stratified shared/private/near-neighbour and separate from the confirmatory streams. Each reversal starts from a clone of the same complete state. At zsRE C2's 300-edit checkpoint, mean damage over both update directions is +2.41365 nats for near-neighbours, +0.69152 shared and +0.15958 private; mean D_ij is 0.03962/0.04063/0.00350, respectively.

The reported harmful fractions use **ordered directions**, not pairs: 22/66 (33.3%), 11/68 (16.2%) and 2/66 (3.0%). Counting pairs harmed in either direction gives 16/33, 9/34 and 2/33 instead. CounterFact endpoint and grammar checkpoints at 1,000 and 2,048 sequences have zero damage and JS divergence on their evaluated Q sets. Complete endpoint states differ in all 375 pairs across the four checkpoints, so these results do not establish commuting updates. Natural-language strata are operational proxies (`manifests/dev/s7_pairs.json`), not established latent mechanisms.

## 8. Exploratory ablations (S8-02; `results/S8/ablations.json`; development data, 3 realizations × 2 orders; not confirmatory)

**(b) Byte ceiling at 0.5×, 1× and 2× (zsRE, 280 available development edits per run, C1 and C2; 300 requested).** Every metric is identical across the three
factors (C1: ES 0.999, RET-ES 0.849, RET-GS 0.257, LS 0.983, 17.3 MB occupied; C2: 0.999 / 0.548 / 0.191 / 0.983, 6.1 MB):
at the 280 completed edits the ceiling (38.5 MB; 19 MB at half) never binds, so this ablation cannot attribute the confirmatory C1 > C2
retention gap at 1,000 edits to capacity. What it does show is that the gap is already present with no ceiling pressure at
all — C2 retains 0.55 of its edits against C1's 0.85 with a third of C1's occupancy — so ceiling pressure is not necessary for this development gap. The exact mechanism and its contribution at 1,000 confirmatory edits remain unresolved. Smaller ceilings or a larger development pool would be needed for an informative capacity intervention; it was not added post hoc.

**(c) Grammar with paraphrase keys at a 5% false-fire radius (C1, C2, CR; 128 sequences per run).** The 5% calibration
finds no admissible positive radius among its tested grid candidates, so the "5% radius" runs reproduce the exact-key runs to the third decimal (C1 ES 0.719 /
RET-GS 0.294; C2 1.000 / 0.294; CR 0.906 / 0.294; LS 1.000 throughout). On the grammar the paraphrase-to-edit and
unrelated-to-edit key distances overlap almost completely (bank 1: paraphrase quantiles 0.09 / 0.20 / 1.05 vs unrelated
0.06 / 0.30 / 0.71), and the smallest grid radius fires on 5.4% of unrelated prefixes while covering 4.4% of paraphrases.
This grid search does not lift the grammar's RET-GS limitation when its criterion is relaxed from 1% to 5%. It does not prove that every smaller positive radius, key definition or calibration procedure is ineffective. The zero-radius runs agree with the exact-key comparator in the reported metrics.

**(a) Stable keys versus edited keys:** not run (needs the optional read variant R-h0, CAP-08). The D3 list was fixed before ablation execution but after confirmation; the grammar 5% test was not in the S4-frozen exploratory list, which also included difficulty weighting. These 72 development runs are explicitly post-confirmatory exploration, not a completion of every frozen optional ablation.

## 9. Deviations, unscheduled and failed work (Appendix G §8)

| item | what happened | record |
| --- | --- | --- |
| Framework | JAX only, FabricPC for PC, sibling read-only (lead directives) | DEC-001…004, SD-13/14/15 |
| ePC checkpoint absent | regenerated (PA-1; bound raised to 120 GPU-h; 12.2 h used) | DEC-014/015, REG-00…03 |
| R8/R9 grammar absent | replacement grammar (PA-2), provisional until the clock passed | GRAM-01/02, DATA-06/07, SD-20 |
| B4 | element-wise value parity failed; sensitivity control did not qualify form (b); localization: the reference's fp32 reductions | DEC-020, SD-21, `logs/grace_*` |
| Freeze v1 | superseded before any result: loader refused editing realizations because of the grammar's `.npz` binding | DEC-026 |
| Grammar paraphrase seeds | per-process hash salt in v2 → paraphrase sequences differed between runs, 0–5 undefined RET-GS per run, frozen classification `incomplete` (archived); fixed by a content-hash seed and rerun under manifest v3 (DEC-029/030): complete and negative with 4/1/2 paraphrase-less items per realization excluded by an outcome-independent, disclosed inventory rule (DEC-031/032) | SD-22; `results/S4/partial/s4_06_grammar_v3.json`; the v2 row and supplement remain in `results/S4/partial/` |
| (v2 grammar row, archived) | frozen classification `incomplete` | SD-22 |
| Post-freeze source changes | analysis tree v2 is recorded; later default-preserving ablation knobs also changed `cap/{cap,memory,calibrate}.py` in `b530baf`. Snapshot 170fad3 had full tree `9b1d9984c3d4…`; DEC-029/030 subsequently binds v3 tree `67787f49ec16…`. The 270 reviewed run configurations still bind the original v2 tree | DEC-028; X2 |
| Drift coverage | Editing assay scores 4,064 positions instead of all available validation tokens required by SD-3; full-validation evaluation remains unresolved | `logs/ongoing_followup_20260911/drift_remediation.md`; X2 |
| Exploratory list | Grammar 5% radius added after confirmation; difficulty weighting omitted; byte-ceiling runs have 280 available edits | S4 frozen list; S8-02; X2 |
| S6 | closed for the month (REG charged to its allocation) | DEC-022 |
| S7 CounterFact shared stratum | 9 pairs (only shared-subject records outside sealed pools) | DEC-023 |
| Selection rule | one subset per realization across orders | SD-19 |
| Key equality tolerance | 1e-4 (batched kernels) | SD-18 |

## 10. Budget (local RTX 5070 hours; κ = 1 provisional, PA-3)

The PDF Appendix B allocates **154 A100-equivalent hours**, not 144. With provisional κ = 1, the current cost-file/task-ledger sum is S0 0.412 · S1 0.181 · S2 0.845 · S3 0.062 · S4 11.492 · S5 8.937 · S6 (REG) 12.316 · S7 0 · S8 0.825 = 35.069 local ledger hours. S5 includes 8.88985 confirmatory hours plus development records; SB is reused from S4 and not charged twice. S7's four embedded reversal ledgers add 0.041715 h, giving **35.111 recorded local hours** for these sources. The budget collector misses those S7 ledgers because no `cost.json` files accompany them.

This is a source-reconciled recorded-cost subtotal, not a certified full physical GPU occupancy or A100 measurement. The cached `results/ledger/stages.json` is stale; some stage measurements keep embedded ledgers, and task estimates may overlap run records. κ remains unmeasured against an A100 (band 0.5–2), and `accel_seconds` measures synchronized call wall time. S4 and S5 confirmation consumed 11.49181/27 and 8.88985/18 h of their enforced allowances; the largest run was 1,067.24 s of 2,400. A final non-duplicated all-cost reconciliation remains for the owner before asserting a complete project spend or universal ceiling compliance.

## 11. Reproduction and artifacts

`docs/REPRODUCE.md` (final-tree CPU audit completed by P2; `logs/reproduce_final.md`, with a fresh-checkout S5 dry-run workaround and expected code-drift refusal; GPU reproduction not rerun); manifests in `manifests/`
(active v3 `frozen.json`, archived v2 freeze, `analysis_versions.json`, `dev/`, `confirm/` sealed, `grammar/`); results per stage in `results/`; task
records in `docs/tasks/`; reviews and responses in `docs/*_review*.md` and `logs/`.
