# PC-7 — fixed-v5 paired credit driver

Status: CPU implementation and tests complete; GPU profile/run are Capstan's.
Agent: Capex. Date: 2026-09-27. No frozen source edits or GPU use.

`aw/pc_v1_run.py` provides `plan`, `profile`, `run`, and `cell`. It imports the
installed `CellAssays`, `endpoint_summary` and semantic revision verdict, and
the existing `PCRevisionCap` acquisition seam. Four production cells compare
SE-A and corrected eight-step SE-E on zsRE and CounterFact, realization 0,
order 100, the first 300 items of the **same exposed block-1 streams**. They are
post hoc / exposed supplemental evidence, not fresh confirmation or a
three-realization experiment. Each arm starts with fresh memory and the same
selected v5 recipe, theta, original BP tensors, calibration, seed and gates.

Checkpoints 100 and 300 contain installed R1 ES, RET-ES, RET-GS, bounded-text LS,
near-miss and semantic revision measurements, raw query/termination traces, and
PC-6-compatible snapshot bindings. Near-miss/revision at **both** checkpoints is
this lane's supplemental cadence; the main R1 queue used them only at the final
checkpoint. Stream memory is unchanged by every assay, including challenge
teaching. Missing cases remain unavailable. Resource failures stop the cell
instead of becoming model failures. Unseen/composition assays are outside this
assigned experiment; ordinary-text harm is a separate PC-5/6 readout.

The profile uses ten development edits per arm/dataset and the full three
challenge inventories (50/100/50). A completed current-code four-cell profile
is required before the exposed run. Its measured edit and endpoint costs are
separated in `phases.jsonl`; a 300-item forecast must distinguish approximately
30 times the acquisition cost from the larger retention history and two endpoint
passes. Do not scale the entire profile by 30. Each production cell runs in its
own process, takes the exclusive lease and is capped at two hours. The group
allowance defaults to eight hours; the October 9 17:00 ET cutoff always applies.
The Monday hold was lifted by lead queue **121**; no hold remains in this driver.

Output plan (metadata only, no data payload/model opened):

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 \
  ../venv/bin/python -m aw.pc_v1_run plan --population replication
```

Capstan's GPU commands, once the PC-v0 chain releases the device. These output
directories are **proposed new paths**, not completed experiments:

```bash
JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 \
  ../venv/bin/python -m aw.pc_v1_run profile --execute \
  --output results/additional_work/PC-v1/profile-20260927 --wall-seconds 7200

JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 \
  ../venv/bin/python -m aw.pc_v1_run run --execute \
  --profile results/additional_work/PC-v1/profile-20260927 \
  --output results/additional_work/PC-v1/replication-4-20260927 --wall-seconds 28800
```

Individual `cell` dispatch also requires `--execute`, `--dataset`, `--arm`,
`--population` and, for replication, `--profile`. Existing output/snapshot paths
are refused. Checkpoints live under `assets/runs/additional_work/PC-v1/`; code,
per-cell logs, configuration, raw endpoints and finish/cost records remain in
pc_cap. `process.json` includes startup/lease wait/construction; `finish.json`
times the stream engine. These overlapping times are not additive. Shared
ledger totals and returned event costs are also separate accounts.

Harm integration: reconstruct the same base/config/theta with `construct`, then
pass the checkpoint report's `snapshot` binding to
`PCPositionBatchReader.from_checkpoint(...)`. Use `selection('v5')` and `read_arm`
from PC-5 and pair equal checkpoints/positions. This driver does not consume the
separate shared eight-hour harm allowance or perform a full fidelity sweep.

Verification: `aw/tests/test_pc_v1_run.py` passes five CPU tests: metadata-only
planning, real tiny-solver paired acquisition/native assays, snapshot/PC-6 restore
and harm integration, read-only challenges, failed-work cost retention, profile
gates and missing semantic evidence. Development input inventory is checked in
`logs/additional_work/round48/pc7-development-inputs.json`. The reproducible
`aw.pc_v1_smoke` fixture writes a labeled two-arm smoke; its small vocabulary,
single delta step and two-token decoder are not production settings.

Review of the occupancy change: importing `aw.pc_v0.blocking_cuda_processes`
preserves the accepted distinction between project/Python jobs and desktop
contexts. The helper depends on readable process command lines; inaccessible
or vanished PIDs and non-Python compute outside the project are not classified
as blockers. An occupancy-query error is explicitly refused by PC-7. No edit
was made to the live, source-bound PC-v0 runner. The still-unrun PC-5 harm driver
used the older blanket check; it now imports this same guard and records the
other contexts, preventing a repeat of the desktop refusal without changing
numerics or acquisition source identities.
