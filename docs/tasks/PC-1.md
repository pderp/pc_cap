# PC-1 — corrected v0 credit runner

Status: CPU implementation delivered; GPU profile and experiment pending owner release. Agent: Capex. 2026-09-24, ongoing.md round 44 / DEC-074b.

Owned files: `aw/pc_v0.py`, `aw/tests/test_pc_v0.py`, this record and its completion JSON. CPU validation only; GPU profiling and experimental execution belong to the orchestrator after release. The current queue runs to cell 270. No locked source or Claude-owned file is edited.

Inputs: archived S5 v2 settings, corrected EPCBase solver, unchanged stream runner, PC refocus proposal and response.
Required outputs: isolated runner, actual-solver SD-24 regression, development diagnostics and profile command, secondary bounded-text scores, measured operation counts.

Delivery: [runner](../../aw/pc_v0.py), [tests](../../aw/tests/test_pc_v0.py). The installed S5 acquisition, legacy scoring and checkpoint machinery are reused unchanged. Each cell loads the pinned regenerated NPZ, starts empty, uses the archived calibration and named seeds, and writes under a new supplemental directory. Its snapshots use the inherited `assets/runs/additional_work/PC-v0/` namespace. Existing result or snapshot directories refuse rather than overwrite.

Validation: actual FabricPC solver on a tiny 12-block transformer passes the nonzero-write one-step adjoint identity, zero-error identity, absence of a prior penalty on writes, frozen weights, fresh error state, 1/8/32 diagnostics and nine-forwards/nine-reverses accounting. Acquisition uses only the current support target; prediction makes no clamped call. Secondary bounded edit/paraphrase scores reuse the same decodes and leave legacy primary scores unchanged. Legacy S5 locality already uses bounded decoded-text equality. Tiny vocabulary padding is explicitly mapped to token zero in the test fixture; production math is unchanged.

CPU verification: 30 tests passed across both PC modules, the existing error-credit regressions and supplemental interface/wrapper regressions. Shared test and lint logs are in `logs/additional_work/pc_round44/`. Final verification of the active content lock passed (916 resources, 446 scripts).

The focused PC test command is:

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m pytest -q -p no:cacheprovider aw/tests/test_pc_v0.py aw/tests/test_pc_v1_acquire.py
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 \
  ../venv/bin/python -m aw.pc_v0 plan --orders 1
```

**Owner commands, only after release/reconciliation.** These are not executed by this lane. A single owner schedules these jobs. The CLI requires `--execute`, obtains the existing exclusive lease before initializing the GPU, checks other compute processes, refuses CPU fallback for the real model, enforces a process wall allowance and the October 9 17:00 cutoff. Each child process has its own fresh JAX context; the parent stops after an incomplete/failed cell and records it without imputation. Edit the run-directory names if any already exist.

```bash
JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 \
  ../venv/bin/python -m aw.pc_v0 diagnose --execute \
  --output results/additional_work/PC-v0/dev-diagnostic-20260926 --wall-seconds 1800
JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 \
  ../venv/bin/python -m aw.pc_v0 profile --execute --items 10 --orders 1 \
  --output results/additional_work/PC-v0/dev-profile-20260926 --wall-seconds 5400
JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 \
  ../venv/bin/python -m aw.pc_v0 run --execute --orders 1 \
  --output results/additional_work/PC-v0/replication-12-20260926 --wall-seconds 79200
```

The first two allowances sum to the proposed two-hour development ceiling; the last reserves the remaining 22 hours of the v0 ceiling. These are upper limits, not forecasts. Diagnostics acquire three fixed seed-21 development items with adjoint credit and inspect their first three support prefixes, both without writes and with their acquired writes. Profile runs four development cells (both datasets/arms); `plan.json` also records the full 12-cell replication design. Each profile includes compilation, locality and endpoint scoring. Do not scale its per-item time mechanically into a full-stream guarantee. Choose `--orders 5` (60 cells) only from the development profile, before inspecting replication comparisons, and retain the same total v0 ceiling.

Recorded outputs: configuration/source/model/data identities, ordered item IDs, original metrics and checkpoints, `secondary.jsonl`, secondary summary, actual operation ledger and `finish.json` with complete/partial status and process time. Both arms retain the historical 2,400-second synchronized-call allowance; the additional group/process wall ceiling includes startup and diagnostics. GPU throughput, CUDA compilation and real-data execution remain untested. No experiment result is claimed.

Cost: 0 GPU seconds. No source-lock edits, sibling writes, new dependency installation or commit. Claude owns `docs/additional_work/PC-v0.md`; this implementation record does not replace that specification.
