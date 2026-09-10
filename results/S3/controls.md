# S3-01 control suite (CP-D input)

Rendered 2026-09-10 01:27 UTC.

| control | expected | observed | pass | blocks if failing |
| --- | --- | --- | --- | --- |
| Numerical known answers | rank/PR/overlap/JS/D.7/η² cases pass | 39 known-answer tests (S0-07/S0-07b) green | pass | every S1 measurement using the metric |
| PC-1 planted acquisition | >= 19/20 targets; full fixture >= 95%; unrelated <= 1e-6 | oracle 20/20, unrelated max |dp| 0.0; full 120/120; wrong-router 1/30 | pass | S3-02 |
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
| PC-10 parity (GRACE) | single/multi-token parity with the reference within fp32 tolerance | pending S2-05 (PA-6; reference env exists) | pending | B4 comparison |

Applicability: PC-8 label isolation for R-g/R-e keys applies only once CAP-08 exists (optional keys). PC-10 is pending the GRACE adapter.

## Development run matrix (frozen for S3)

- Realization: development pools (`manifests/dev/{zsre,counterfact}_dev.json`, seed 13), one realization.
- Orders: two (order seeds 100 and 101 via `--perm 0/1`), 100 items per dataset per arm (S3-04), all four routing arms C0/C1/C2/CR; CR uniform (SD-11, `cr_profile_uniform`) for this first pass.
- Fixture: MODULAR-CONTROL variants useful-sharing / no-sharing / wrong-router, 60 items per kind, arms C0/C1/C2/CR/CO (S3-02).
- Grammar: pending GRAM-02/DATA-06 (S3-03).
- Numerics: A = 0.3 (DEC-012), radii per dataset (SD-17), b_m from S2-01, ε = 0.01, R = 5, τ = 0.1.
