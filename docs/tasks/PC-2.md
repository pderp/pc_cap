# PC-2 — fixed-v5 acquisition credit

Status: CPU implementation delivered; real-base integration/profile pending release. Agent: Capex. 2026-09-24.

Owned files: `aw/pc_v1_acquire.py`, `aw/tests/test_pc_v1_acquire.py`, this record and its completion JSON. CPU only. Preserve v5 initialization, feedforward acceptance loss, bounds, stopping and rollback; change only delta credit with full inference cost. Adjoint mode must match existing v5 behavior. No GPU execution or new reader training.

Delivery: [isolated acquisition seam](../../aw/pc_v1_acquire.py), [tests](../../aw/tests/test_pc_v1_acquire.py). `PCRevisionCap` inherits prediction unchanged and reuses the installed preparation/outcome functions in private function namespaces; no shared module or base method is patched. In error mode only the delta-update direction changes. The initial controller/code adjoint calculation remains in both arms for exact setup parity; the treatment is not backpropagation-free reader training.

Use the same original BP base parameters, selected v5 theta, calibrated config, seeds, gate and fresh memory in both arms. An `EPCBase` constructed on those BP weights supplies the error-inference interface; do **not** load PC-1's regenerated ePC checkpoint here. Instantiate `PCRevisionCap(base, cfg, ledger, params=theta, acquisition_credit="adjoint")` or `acquisition_credit="error", credit_iters=8`, then use its ordinary `update_item` / `predict` API. Scope remains the exposed realization-0 zsRE/CounterFact streams, 300 edits, one order; this lane adds no new population, training or GPU execution.

Validation: adjoint mode is bitwise equal to `RevisionCap` on taught memory, predictions and cost counters. Real-solver eight-step acquisition checks actual support prefixes/targets, aggregate write bound, unchanged reusable/base weights, feedforward acceptance loss, and no clamping at prediction. Costs include nine forwards/nine reverses per credit plus the unchanged setup adjoints. Nonfinite inference removes a failed revision, restores the previous active record, and preserves the failed inference charge. A separate mock plumbing check shows identical stored arrays and outcomes when error credit equals the negative adjoint; it does not replace the actual-solver regression in PC-1. Snapshots carry the error-credit horizon/learning rate and reject mismatched credit restoration. Adjoint snapshots retain the original v5 identity.

Verify with the combined CPU command in [PC-1](PC-1.md). Real v5 CUDA parity/profile and the paired experimental run remain the owner's post-release work. This is an acquisition module, not a new training or sealed-experiment driver.

Cost: 0 GPU seconds. No existing source/driver edits or commit. Completion JSON records final checks and artifact hashes.
