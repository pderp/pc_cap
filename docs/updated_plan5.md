# Updated plan 5 — 2026-09-10, day 2 (late morning EDT), after the second reviews and 60% of REG-02

Delta over [updated_plan4.md](updated_plan4.md) (which stands where not restated). Inputs:
`docs/derp_review2.md` (third reviewer; response in `docs/derp_review2_response.md`), Codex's
`logs/interim_report2.md` (already folded into plan 4; no newer Codex response exists in `logs/` at
writing), and the REG-02 evidence to step 5,878.

## 1. REG-02 evidence and what it changes

| stage | steps | KD loss mean ours / sibling | tracking-residual median ours / sibling | grad-norm median ours / sibling | s/step |
| --- | ---: | --- | --- | --- | ---: |
| T=1 | 1,396 | 7.0e-5 / 6.6e-5 | 0.991 / 0.991 | 1.24e-2 / 1.26e-2 | 0.72 |
| T=2 | 1,395 | 1.3e-4 / 1.3e-4 | 0.986 / 0.987 | 1.94e-2 / 1.90e-2 | 0.96 |
| T=4 | 1,395 | 9.5e-5 / 1.2e-4 | 0.975 / 0.978 | 2.01e-2 / 2.17e-2 | 1.40 |
| T=8 | 1,395 | 1.9e-4 / 2.1e-4 | 0.972 / 0.973 | 2.78e-2 / 2.73e-2 | 2.28 |
| T=16 (partial) | 297 | 1.2e-4 / 2.3e-4 | 0.967 / 0.970 | 3.21e-2 / 3.70e-2 | 4.00 |

Stage boundaries 1396 / 2791 / 4186 / 5581 identical to the sibling's realized run; no holds,
subdivisions, non-finite values; 15 process restarts with contiguous steps (resumability exercised in
production). Fidelity: prompt KL ≤ 2.9e-5 (abort 0.05); 32k-token tail KL 4e-6…7e-5 with student−teacher
NLL ≤ 5e-4 nats at every milestone; the 96-token perplexity probe wanders ±1% (noise). GPU time so
far 2.0 h; ETA ≈ 19:40 EDT; final cost ≈ 12.4 GPU-h plus ≈ 1 h of automatic follow-ups.

Consequences:
1. **REG-03 and S5 eligibility are likely** (the P1 rule is mean KL ≤ 1e-3 on H; the tail figure is two
   orders of magnitude below). Plan the S5 substrate comparison as *expected to run*, not as a bonus:
   its arms, runner and calibration are ready (S5-01); S5-02 follows the freeze and the ePC calibration.
2. **S6 (conditional re-distillation) is not affordable this month.** DEC-014 charges REG to S6's
   20 A100-h allocation; REG-02 + REG-01 + chains consume ≈ 14 of them, and a matched continuation pair
   (two arms from the same checkpoint) would need ≥ 2 × the remaining hours. D2's "defer" becomes
   "closed unless the lead reassigns hours"; the deficit statement (S6-01) can still be written from S5
   evidence as a preregistered proposal for a follow-up.
3. **The GPU is committed until ≈ 20:40 EDT** (run + chains). GRAM-02 training, the GPU test subset,
   the re-profile and B4 profiling queue behind it; the PA-2 clock (2026-09-11 23:59 ET) is not at
   risk. Order in the first free window: GPU tests → re-profile (ledger deltas) → GRAM-02 training if
   Lane G′ code is ready → B4 profile if Lane D delivered.
4. The regenerated checkpoint is a *new* substrate (PA-1). Every inherited ePC claim is re-measured
   (S1-01, ePC rows of P2/P3/P5/P6 — automatic); no continuity language.

## 2. Documentation and process (from the reviews)

- One current log: `docs/ongoing.md`; superseded versions dated under `docs/archive/` (policy in
  CONTRIBUTING). `docs/decisions.md` has a typed index.
- Runtime determinism guard (`pccap.assert_determinism()`, called by `pccap run` after the lease;
  importing `pccap` after a live JAX backend raises).
- Coverage tooling: not in the frozen venv. **Lead decision requested** (see §4): allow adding
  `pytest-cov` to the venv (recorded in `requirements.lock` and `docs/environment.md`) or accept the
  test counts as the coverage evidence.
- Reports record their evidence snapshot time; reviewers should state the tree time they read
  (both reviews so far read snapshots that predated actions taken the same hour).

## 3. Sequence (unchanged from plan 4 except the S6 closure and the window order)

REG-02 → auto chains (REG-03, S1-01, ePC rows, S1 report; S5 prep) → GPU window 1 (tests, re-profile,
GRAM-02 training, B4 profile) → gate §2 of plan 4 green → lead freeze (CP-E) → S4-02 scope and
per-run allowance → S4-03/04 execution → S4-05/06 · S5-02 · S7 · S8. S6: closed for this month
unless reassigned.

## 4. Decisions requested from the lead

1. Coverage tooling in the venv (yes/no).
2. Confirmation that S6 is closed for the month under DEC-014's charge, or a reassignment of hours.
3. T-CP-E stands as re-dated (after the plan-4 gate).
