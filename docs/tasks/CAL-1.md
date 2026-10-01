# CAL-1 — known-distribution calibration and objective note

Status: complete. Agent: Capex. Inputs: locally shared Nelson manuscript, one-sided α=d=1 formulas; existing κ pilot and entropy review. Outputs: `aw/calibration_demo.py`, canonical `logs/additional_work/CAL-1/final/{checks.json,report.md}`, `docs/additional_work/coupled_objective_note.md`.

Twelve κ/σ combinations numerically verify density normalization, informational slope, normalized escort mean and calibrated entropy. Maximum absolute error: 1.77e-11; κ→0 exponential check passes. Ordinary mean divergence for κ≥1 is explicit and not replaced with a large finite quadrature estimate. The note specifies probability variables/units, reference and constraints, normalization, escort-gradient covariance, outer-root/domain issues, policy ingredients and JAX tests before any model experiment. No objective was trained or library port attempted.

Verify: `JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ../venv/bin/python -m aw.calibration_demo --output logs/additional_work/CAL-1-NEW`. Known-distribution quadrature is independent of the analytic expressions under test. Earlier root-level logs precede a lint-only cleanup; use `final/` for current source hashes.

Done-when: met within the bounded optional lane. Cost: CPU only; zero GPU/model calls. Limitations: this is a restricted formula check, not proof of the manuscript, entropy-class identification, or a coupled free-energy experiment. Questions for lead: none; scientific objective choices remain post-conference discussion.
