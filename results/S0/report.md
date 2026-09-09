# S0 stage report (Appendix G)

Rendered 2026-09-09 19:37 UTC by `pccap report --stage S0`.

## 1. Header

- Stage: S0 (harness, invariants, minimal cap). Code commit: `3e86acf17938ec14679ac382aeb4d682098e8798`.
- Configuration: `manifests/dev/s0_smoke.json`; base checkpoint: GPT-2 small snapshot `607a30d7…` (`model.safetensors` sha256 `248dfc39…`).
- Hardware: NVIDIA GeForce RTX 5070 (cc 12.0), JAX 0.11.1, fp32, TF32 off.
- Realizations/orders: development only (s0 sample, seed 7); no confirmatory access.
- Elapsed cost: 0.32 local GPU-h = 0.32 A100-eq h (κ = 1.0, band [0.5, 2.0], provisional) against the 8 h ceiling (4.0%).

## 2. Status

Development. Completed: ENV-01..04, DATA-00, S0-03..S0-10, CAP-01..CAP-07, S0-07/S0-07b/ANA-01 (Lane B). Pending inside S0: REF-01 (HF oracle fixture; rows in S0-04/S0-09 records marked pending), S0-01 (asset inventory / T1 clock). No correctness failure open; no resource limitation hit.

## 3. Controls

| control | expected | observed | pass | blocks if failing |
| --- | --- | --- | --- | --- |
| Numerical known answers | rank/PR/overlap/JS/D.7/η² cases pass | 39 known-answer tests (S0-07/S0-07b) green | pass | every S1 measurement using the metric |
| PC-2 identity | 256-probe cap-off equality (max |Δ| = 0); oracle-false gate exact | probes 256, max |Δ| cap-off 0.0, gate 0.0, unrelated fired 0 | pass | everything |
| PC-3 idempotence | 20 repeated threshold-fitted edits, no new slots | reached 20, checked 20, violations 0 | pass | S3-04, S4 |
| PC-4 conflicts/revisions | distinct, identical, newer version, replay, failed rollback | pytest green (see test-fast / test-gpu logs) | pass | S3-04, correction track |
| PC-5 probe/search | signed scores, non-monotone, exact candidate, rollback | pytest green (see test-fast / test-gpu logs) | pass | C2 and all cap learning |
| PC-6 budgets | equal ceilings, overhead, wide keys, aggregate increment, eviction, use-count once | pytest green (see test-fast / test-gpu logs) | pass | all arms |
| PC-7 complete answers | wrong second token; teacher-forced vs generation; terminators | pytest green (see test-fast / test-gpu logs) | pass | all editing metrics |
| PC-8 isolation/read-only | state hash after predict/decode unchanged | hash unchanged after predict + decode | pass | evaluation validity |
| PC-9 cloning/randomness | clone equality, replay, reversal start, item-keyed CR, scalar order effect | decisions 12, clone/replay/reversal equal | pass | S7, all confirmatory |
| Reproducibility | two replays: identical decisions, metrics within tolerance | 11 decisions identical | pass | all confirmatory |
| Sign convention | analytic descent direction reduces the loss | loss 19.963 -> 19.797 (flipped 20.130) | pass | all credit |
| ePC sign convention | +e reduces the toy loss; cos(e, −adjoint) ≈ 1 | cos(e, −adjoint) = 1.000000 | pass | ePC credit |
| Adjoint finite difference | rel err < 1e-3 vs f64 reference at step 1e-2 | worst rel err vs f64 = 1.43e-05 (fp32-internal FD 3.11e-02) | pass | all credit |
| ePC zero-error identity | sites exact; logits within SD-10 record | sites max |Δ| = 0.0, logits max |Δ| = 8.39e-05 (kernel: head GEMM; SD-10 record) | pass (with record) | ePC arms |
| Frozen base | base_hash_before == base_hash_after | before c4ac3fb867 == after c4ac3fb867 | pass | that run |

Geometry alerts: none measured yet (S1). Scientific outcomes: none claimed at S0.

## 4. Coverage

- Planned S0 arms: one smoke edit, C1, BP, R-h. Completed: 1/1.
- Unsupported/undefined so far: HF-oracle parity rows (pending REF-01, recorded `unavailable`); sibling fast tests (`unsupported`, DEC-001).
- ePC checkpoint: absent (S0-01 inventory pending; PA-1 clock starts at CP-A). ePC wrapper built and tested on BP weights.

## 5. Results (development smoke, not a finding)

- Item `zsre-eval-100`: outcome `accepted`, rounds 8; ES 0.0 → 1.0; teacher-forced NLL 23.72 → 0.16 nats.
- Memory: occupied 56664 B of allocated 38535384 B (ceiling 38535168 B).
- Base hash before/after: `c4ac3fb867da` / `c4ac3fb867da`.

## 6. Mechanism evidence

None at S0 (oracle fixture, random-routing comparison and signed scores arrive with S3).

## 7. Optional mathematics

HVP small-matrix controls (S0-07b) pass; no HVP diagnostics run.

## 8. Deviations

See `docs/decisions.md` DEC-001..DEC-009 and `docs/spec_defects.md` SD-13..SD-16: JAX-only stack (SD-13); HF oracle via stored fixtures (SD-14); PA-1 needs a JAX distillation driver (SD-15); C2 tie rule (SD-16); adjoint finite-difference oracle is the float64 reference (S0-05 record); ePC ledger counts the terminal residual (docs/epc_energy.md); ePC head-GEMM logit difference 8.4e-5 recorded (SD-10). All before any test access.

## 9. Interpretation

S0 establishes the apparatus only: cap-off identity, memory accounting, transactional rollback and complete-state cloning hold; one development edit is acquired. No claim about routing, representation or credit is supported or refuted by S0.

ePC status: wrapper on FabricPC; on BP weights, 8-step energy descent monotone on 16/16 prompts; r_8 in [0.17, 0.42] → label 'finite-iteration error credit'. Distilled checkpoint: absent.

## 10. Reproduction

```
make test-fast && make test-gpu
python -m pccap.data.fetch --verify
python -m pccap.cli run --stage S0 --arm C1 --base BP --read h --realization 0 --perm 0 --manifest manifests/dev/s0_smoke.json
python -m pccap.cli report --stage S0
```

Licences/provenance: `manifests/datasets.json`, `manifests/assets.json`. Remaining S0 work in priority order: REF-01 oracle fixtures; S0-01 inventory and T1 clock; CAP-08 read variants (optional).
