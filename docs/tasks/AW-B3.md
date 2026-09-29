# AW-B3 — bounded-correction calibration and evaluation

2026-09-28, Capex. **Implementation complete, CPU validated; GPU dispatch belongs to Capstan after the settling-depth controls.** No model run was launched here. User decisions made before calibration (DEC-076a): use the actual full-endpoint zsRE development population behind the requested saved memory; rank eligible candidates by the smaller dataset maximum-harm reduction, then the smaller ES99 reduction. The approved specification now records both choices.

`aw/aw_b_calibrate.py` qualifies existing 300-edit snapshots against their actual recipes, payload order, checkpoint state, reader and base. Both development memories and all ten exposed realization-0 evaluation memories exist; no new training is needed. `logs/additional_work/round52/aw-b3-plan.json` and `manifests/additional_work/AW-B_v1.json` record exact identities. CounterFact uses its original r16 development memory; zsRE uses `R1-64g-post63l/R1-64g-zsre-R1_learned_ff.recipe.json`. The rejected older zsRE pairing is documented in `AW-B3-population-check.md` and retained as a regression test.

The native batch reader streams the full 245,237-position inventory. Thirteen numerical settings share one base/cap pass; each of three stricter gates requires another pass. Every setting gets both-reference KL/loss vectors, signed maximum/location/ties, ES99+, exceedances, half-mass and changed fraction. Gate selection, hard-null and actually corrected positions are separate telemetry. Vectors go under assets; reports and receipts go under pc_cap. Numerical settings share charged pass cost; do not sum repeated telemetry as separate compute.

All sixteen settings also run the installed retention, bounded-text locality, near-miss and revision functions through `BoundedCap`. ES here means saved-memory re-query (equal to RET-ES), not original immediate acquisition. There is no new stream acquisition; native near-miss/revision assays temporarily teach and restore state, with their cost included. Base, reader and memory identities are checked afterward. CPU tests use the real tiny base, all sixteen settings and these native endpoint paths.

Selection requires both datasets' RET-ES/RET-GS within **±0.02** of v5, LS/near-miss not decreased. Missing scores are ineligible. At most one bound and one shrink/gate comparator are selected; if none qualifies, that category is explicitly absent. Complete numerical ties retain the predeclared order. Evaluation recomputes the selection from its bound calibration report, refuses changed sources, and reports success separately for every dataset/order before the all-coordinate summary. No evaluation outcome can alter selection.

Owner commands, in the CUDA-enabled project venv, from pc_cap (choose new output directories):

```bash
../venv/bin/python -m aw.aw_b_calibrate plan
../venv/bin/python -m aw.aw_b_calibrate calibrate --execute --output results/additional_work/AW-B/calibration-20260929
../venv/bin/python -m aw.aw_b_calibrate evaluate --execute --selection results/additional_work/AW-B/calibration-20260929/selection.json --output results/additional_work/AW-B/evaluation-20260929
```

Calibration ceiling: 8 hours; evaluation: 16 hours; both stop by October 9 at 17:00 EDT. Exclusive lease, project-process occupancy check, explicit CUDA backend, fresh output directory and source stability are enforced. Construction, fixed-prefix scoring, generation, temporary teaching and failed work are charged. Preliminary read-only snapshot qualification is outside the execution timer. A failed or incomplete run cannot yield a selected result. No automatic retries or unrecorded expansion of the budget.

The older specification's one-pass statement applies to the thirteen numerical settings; gates need three additional passes. The current lane selects `results/additional_work/AW-B/` as the output namespace. Full CPU validation is recorded in `logs/additional_work/round52/round52-tests.log`; GPU throughput and the 8/16-hour feasibility remain to be measured by the owner.
