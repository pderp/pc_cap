# PC-4 — fixed-v5 acquisition seam on a saved development checkpoint

Status: done. Agent: Capex. Date: 2026-09-26. CPU only; no GPU claim.

Inputs: the same selected-v5 recipe, original BP base parameters, reader weights and 300-edit development snapshot used by AW-L0. Recipe: `docs/tasks/R1-post63l-active/R1-64e/R1-64e-zsre-primary-v5.recipe.json`. Output: `aw/tests/test_pc_v1_devcheckpoint.py`, `results/additional_work/PC-4/devcheckpoint.json`, `logs/additional_work/round45/pc4-tests.txt`. Resource identities are recorded in the result JSON.

The test verifies recipe/adapter identity, snapshot bytes and internal state, and development payload identity. It restores the snapshot independently into original `RevisionCap` and adjoint-mode `PCRevisionCap`, using an EPC interface on the **same original BP parameters**, not the PC-v0 regenerated checkpoint. Four development facts supply eight prefixes, covering null and nonzero-write predictions. All eight logit vectors and operation counts are exactly equal; saved memory stays unchanged. A short acquisition (first development item with at most two answer tokens, including its terminator) then gives equal outcomes, exact resulting memory and cumulative counters, and an additional exact prediction check: **9/9** total.

For error mode, the same saved memory is explicitly copied in memory with the PC acquisition semantic configuration; the original checkpoint is not relabelled or rewritten. Eight-step PC acquisition completes with an accepted outcome and finite predictions. Both base checksums and reusable-reader weights remain unchanged. This establishes execution on the real base, not relative editing quality or robustness.

Measured CPU replay time: **13.023 seconds**, including construction/replay. Short-acquisition times: original 2.804 s, adjoint seam 0.265 s, error seam 3.337 s. Sequential calls have unequal compilation/warmup, so these are reference timings, not speedup estimates or GPU forecasts. Adjoint acquisition: 12 forwards, 4 reverses; error acquisition: 28 forwards, 20 reverses, 16 settle iterations (two eight-step credits plus unchanged setup/acceptance work).

Verification: **1 passed in 13.63 s**. The test skips explicitly if the local saved checkpoint or recipe is absent. For a rerun use a fresh output filename (or omit `PC4_OUTPUT` to test without publishing):

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 \
  OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1 PC4_OUTPUT=results/additional_work/PC-4/devcheckpoint-REPLAY.json \
  ../venv/bin/python -m pytest -q -s -p no:cacheprovider aw/tests/test_pc_v1_devcheckpoint.py
```

Done-when: saved-development predictions, acquisition, memory and accounting reproduce on the real base, and error mode executes. Remaining: owner's GPU profile and paired experiment; fixed-v5 experimental outcome remains empty in claim ledger v7. Cost: 0 GPU seconds. No locked-source edits, snapshot mutation, new training or commit.
