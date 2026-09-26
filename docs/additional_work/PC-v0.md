# PC-v0 — corrected SE-E vs SE-A on the original v0 cap: specification of record

2026-09-26, Claude (orchestrator). Design: Codex's `additional_work_pc_refocus.md` §2–3 as amended by `_review.md`
and `_response.md`; consolidated in `plan_from_saturday.md` §3; decisions DEC-074/074a/074b. Implementation:
`aw/pc_v0.py` with `aw/tests/test_pc_v0.py` (Codex lane PC-1, committed e5b7446; 55 `aw` tests pass on CPU).
This page is the one specification the runs are checked against; substantive changes are recorded here.

## Question

With the same frozen base and cap architecture, does finite-iteration predictive-coding credit (corrected energy)
acquire useful factual edits and retain them, and what does it cost, relative to ordinary adjoint credit?

## Arms

| fixed for both | SE-A | SE-E |
|---|---|---|
| base: regenerated ePC 50M checkpoint `assets/models/epc/epc-50m/checkpoints/final-009766/params.npz`, SHA-256 `ea4c561d3963ffd89f866337ef5e789a4ef15b7558b4c717594dbef88cd26f51`, loaded with `EPCBase.from_npz` (never the default constructor) | | |
| cap: original v0 C1, live R-h keys, writes at banks 1–3; archived S5 v2 calibration and stream-selection rules; fresh empty memory per cell | credit = negative normalised adjoint | credit = normalised site error after 8 inference steps, energy `½‖e‖² + task` (SD-24 corrected), error lr 0.1 |

## Populations and scope

Exposed historical S5 populations: zsRE 1,000 edits, CounterFact 300 edits, realizations 0–2, one preselected order
(`--orders 1`): **12 cells**. All five orders (60 cells) only if the profile projects completion inside the 24-hour
ceiling; that decision is taken from the profile output before any comparison outcome is inspected. Labelled a
supplemental defect-correction replication, not fresh confirmation; DEC-073's reserved subjects are untouched.

## Pre-run checks (all passed on CPU against the real solver; recorded in the PC-1 record)

1. With nonzero cap writes, the one-step site error from zero error equals −0.1 × adjoint within tolerance
   (the check that would have caught SD-24).
2. Zero-error forward identity; no prior penalty on writes; base weights unchanged after acquisition.
3. Independent empty memories per arm; identical items, seeds, calibration and stopping.
4. Target clamped only for the taught support answer during acquisition; scoring by ordinary generation.
5. Cost ledger: an eight-step credit is nine forwards and nine reverses; operation counts and process time recorded.

GPU development steps before the paired run (owner, under the lease, ≤ 2 h together): `diagnose` (energy, gradient
residual, direction cosine and norm at 1 / 8 / 32 iterations on three fixed seed-21 development items, with and without
acquired writes; 8 stays the treatment) and `profile` (10 items, one order) to fix the 12- or 60-cell scope.

## Endpoints

Per paired stream, old S5 scoring: ES, RET-ES, RET-GS, LS; the modern bounded-text score in `secondary.jsonl` as a
separate column; process time and operation counts. zsRE carries the credit comparison; CounterFact's historical
paraphrase floor (zero for every arm) is stated. Every realization and order difference shown; no token-level
independence claims. Historical reference under the defective energy: SE-E − SE-A ES −0.336, RET-GS +0.019.

A companion paired ordinary-text harm readout (same preselected validation positions, both arms, same checkpoint;
mean KL, signed ΔNLL, upper quantiles, maximum, exceedance) is run by the orchestrator with `aw/scoring.py` after the
replication, within the 8-hour readout ceiling.

## Execution

Owner commands (PC-1 record), run only after the queue's halt, reconciliation and boundary report, holding the GPU
lease, one job at a time:

```bash
JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m aw.pc_v0 diagnose --execute --output results/additional_work/PC-v0/dev-diagnostic-20260926 --wall-seconds 1800
JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m aw.pc_v0 profile --execute --items 10 --orders 1 --output results/additional_work/PC-v0/dev-profile-20260926 --wall-seconds 5400
JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m aw.pc_v0 run --execute --orders 1 --output results/additional_work/PC-v0/replication-12-20260926 --wall-seconds 79200
```

Stop ceiling 24 GPU-hours including the development steps. Outputs: identities of configuration, source, model and
data; ordered item IDs; metrics and checkpoints; operation ledger; `finish.json` with complete/partial status. Report:
one comparison table with efficacy, harm and cost together; a negative result is the answer, not a failure.

## Change log

- 2026-09-26: specification written from the agreed design; no changes.
