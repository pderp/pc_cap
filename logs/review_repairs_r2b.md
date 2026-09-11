# Lane V2 — completed independent study after D-F approval

Reviewed 2026-09-11, starting from `af98eab218ef55308be333615c9a228a0b0eb5ef`.
The approved review-tools patch was applied before execution. Source tree SHA-256
`4b2ff4c090c912b643f53f9489eed0b3fe8b7e9fae92722bedbce78a5fca0f10`
matches the synthetic freeze and the tree after the study. Exact files, fixture hashes
and evidence hashes are in `results/V2/plan6_df/provenance.json`.

**The review is complete; confirmation readiness is not established.** The study
completed successfully and confirmed several repairs, while its negative probes
reproduced the remaining failures below. Exit zero means the measurement completed,
not that every property passed. No production final freeze or confirmation payload
was opened or written. All model/learner tests used CPU; GPU usage was zero.

## Execution and passing checks

```bash
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu \
  OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 GIT_OPTIONAL_LOCKS=0 \
  ../venv/bin/python -B scripts/review_repairs_r2b_study.py
```

The script chooses a fresh `assets/tmp/review_repairs_r2b_<timestamp>` fixture root.
This invocation's captured output, stderr and duration are under
`results/V2/plan6_df/`; it completed in 2.787 seconds. The original failed attempt
under `results/V2/` remains intact. Removing the schema-invalid `[1, 2]` checkpoint
override fixed the review fixture; the required `[100, 300, 1000, 3000]` schedule
was retained.

| Property | Independent result |
| --- | --- |
| Denied confirmation access | Exit 2; zero payload reads |
| Actual S4 path | 150/150 synthetic editing jobs completed through the real CLI, stage, loader, stream, snapshots and collectors |
| Lease order | Lease entry precedes backend discovery and base construction |
| Schedule/config validation | Negative/past-last order, invalid realization, wrong base/read and unknown arm refused with exit 2 |
| Code drift | Refused with exit 2; accepted only when the explicit override flag was supplied |
| Paired collection | zsRE 540 rows; CounterFact 420 rows; both required contrasts complete, no notes |
| Rerun protection | Existing run refused with exit 4; explicit force succeeded |
| Archive exclusion | Superseded attempts excluded from analysis; no duplicate paired-row failure |
| State preservation under force | Different learned state produced; old result directory and external checkpoint bytes preserved |
| Frozen S5 authority | Frozen EPC base, radii `.21/.22/.23`, scales `7/8/9`, and 1.2-second allowance used; mutable calibration/checkpoint helpers were replaced with assertions and were never called |
| Invalid S5 authority | Missing arm refused with exit 2; missing calibration and checkpoint hash mismatch stopped with exit 1, before any model construction |
| Ordinary stage allowance | With a finite run allowance, first job completed and next job was refused with exit 5 |

The two required paired contrasts have the synthetic classification `negative` because
the fake outcomes are equal. This is pipeline evidence, not an experimental conclusion.
The current draft's 210 scheduled paths were checked for uniqueness, but the executed
fixture contains **150 editing jobs only**. Grammar confirmation execution is not
covered by this study. A separate targeted run passed all 14 tests: nine existing
confirmation controls and five GRACE unit controls (`results/PLAN6/DF/cpu_controls.txt`).
Patched scripts and the environment helper pass Ruff (`results/PLAN6/DF/lint.txt`).

## Findings requiring orchestrator repairs

### V2-01 — loaded BP/tokenizer identity is not compared with the freeze

Both `bp_frozen_digest_mismatch` and `tokenizer_frozen_hash_mismatch` completed with
exit 0. The probes supplied deliberately inconsistent frozen hashes while retaining
the synthetic base/tokenizer. They did not corrupt or load a real production model.
Inspection of `stage_s4.run_s4`, `BPBase.__init__`, and `GPT2Tokenizer.__init__`
confirms that this path has no comparison against those frozen identities.
Before/after immutability checks cannot establish that the initial resource is the
resource selected by the freeze.

The S5 EPC file-hash refusal works, as measured separately. Extend startup identity
checks to all relevant bases/tokenizers and reject mismatches before editing or
evaluation. Preserve the two negative controls when implementing the repair. The
plan's proposed exit-2 preflight behavior should be tested explicitly; the current
S5 malformed-input path instead records `correctness_failure` with exit 1.

### V2-02 — a selected experiment includes runs with unknown identity

With two identified experiments, an explicit filter correctly selected one run and
eight paired rows. Adding an otherwise valid synthetic legacy run with no
`config.experiment_id` changed those filtered counts to **two runs and 16 rows**.
`s4_05.discover`, `s4_06.collect_rows`, and `s7_03.load_runs` currently accept
`None` alongside the requested ID. A specific filter must require an exact match;
unknown-identity records should be excluded with a diagnostic or rejected.

### V2-03 — S7 CLI cannot select an experiment; unfiltered analysis loses identity

`s7_03.load_runs` accepts an experiment filter, but its CLI does not expose it.
The two-experiment control supplied two runs with the same dataset/arm/realization/
order: unfiltered S7 loading returned **one cell**, silently replacing an entry.
`s4_05.views` likewise produced one comparable-compute cell from those two runs.
Unfiltered paired collection returned 16 rows rather than eight, leaving duplicate
identity detection to downstream analysis.

Expose `--experiment-id` in S7 and require a single experiment or preserve experiment
identity in downstream grouping. Adding the CLI flag alone does not make an
unfiltered multi-experiment invocation safe. Include conflicting outcomes in a
follow-up control so accidental cross-experiment replacement cannot go unnoticed.

### V2-04 — a finite stage ceiling can be declared enforced without constraining a run

The schema-valid control set `stage_allowance_seconds.S4 = 0.01` and
`run_allowance_seconds = None`. It completed with exit 0, recorded
`stage_allowance_enforced=true`, and charged **7.2000034 synthetic seconds**.
`runner.main` treats a missing run allowance as zero during admission; the stream
then receives no run limit. Reject this inconsistent configuration or derive an
effective allowance from the remaining stage budget. Do not claim enforcement
merely because a stage field is non-null.

### V2-05 — force removes previous attempts from the stage spending total

A read-only follow-up on the distinct-state forced-rerun fixture found two preserved
attempts charging **14.4000069 synthetic seconds** in total. The runner's
`_stage_spent_seconds` counted only **7.2000035**, because it excludes archived
attempts. Evidence: `results/V2/plan6_df/archive_budget.json`.

Excluding superseded attempts from scientific analysis is correct; excluding their
consumed work from an experiment's resource budget is not. Account for all attempts
in the spending total, independently of which result is selected for analysis.
Keep this distinct from V2-04's missing-run-allowance case.

## Completion and boundaries

The D-F review task is finished and all its remaining controls have been exercised.
The orchestrator owns production repairs; no harness, collector, model, frozen
manifest, threshold or allowance was changed by this review. Re-check repaired
behavior with the unchanged negative inputs before using this report as support
for confirmation readiness. CPU environment installation is recorded separately
in `docs/tasks/ENV-05.md`; it does not supply GPU or scientific validation.
