# PC-9 — contingency solver options prepared on copies

2026-09-27, Capex. **CPU preparation complete; patch not applied, variants unrun.**
The active replication and the downstream source-bound chain retain their exact
runner bytes. This record does not authorize a sweep or select settings.

## Prepared changes

The exact two-file [patch](PC-9-candidate/solver-options.patch) targets
`aw/pc_v0.py` and `aw/pc_v1_run.py`. Review copies and original/candidate hashes
are in [PC-9-candidate](PC-9-candidate/sources.json); `aw/pc9_stage.py` reproduces
them from the matching original files. Copies are **not runnable entrypoints**:
their module paths and source inventory deliberately target the eventual live files.

- Both CLIs accept `--credit-iters 8|16|32` (default 8) and positive finite
  `--error-lr` (default 0.1). Group dispatch forwards both to every child.
- SE-E receives the selected cap iteration count and EPCBase learning rate at
  construction, before solver graphs are cached. SE-A keeps its original inert
  solver defaults; requested and effective settings are distinguished.
- Every created cell config and finish records effective settings; requested
  settings remain in the config/finish metadata. Early failures that create a
  finish still record the treatment, rather than appearing to be default cells.
- Fixed-v5 snapshot metadata includes its solver rate. Its production gate
  requires a complete development profile with matching settings and source;
  an eight-step profile cannot authorize a 32-step production run.
- `plan --profile <completed-development-directory>` adds cost scenarios for
  8/16/32 at the requested rate. `--sweep-error-lrs` can list rates in plan mode;
  no command launches a sweep automatically. GPU lease, deadline, output-reuse,
  exposed-population and unchanged-weight checks remain in place.

The new CPU-only helper, `aw/pc_sweep.py`, can be used now without changing a live
runner, for example:

```bash
PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m aw.pc_sweep \
  --profile results/additional_work/PC-v0/dev-profile-20260927 \
  --design development --error-lrs 0.1
```

Its existing-profile reproduction estimates **1,499.84 process seconds** for the
whole development-sized sweep: three settings, four cells at each setting, both
controls rerun rather than shared. This is an extrapolation from the completed
ten-item profile, not a measured 16/32-step GPU runtime. See
`logs/additional_work/round50/pc9-development-cost.json` for cell calculations
and source hashes.

Full-stream sensitivity scenarios are retained in
`logs/additional_work/round50/pc9-v0-60-cost-scenarios.json`. They separately scale
learning with items and `(k+1)/(profile_k+1)` and either hold query cost fixed or
scale it with items. **Neither scenario is a budget bound or a useful scheduling
guarantee:** endpoint cadence, growing memory/search, changed convergence and
compilation can invalidate them. Harm readout, new profiling and retries are
excluded; no fixed-v5 profile exists yet, so its projection stays pending.

## Integration boundary and additional reporting dependency

Do not apply merely because the last replication cell finishes. The PC-v0 report
loader and PC-5 readout compare saved source hashes to the current tree, and
PC-7 binds `aw/pc_v0.py` as an input. Applying now, or between PC-7 profile and
production, would invalidate those checks. Preserve the old source version for
regeneration, finish its source-bound reports/readouts/exports, and coordinate
an idle boundary with Capstan before applying and obtaining a new matching profile.
The patch passes `git apply --check`; this turn did not apply it.

**Tuesday's full “no new code” objective is not yet met by the requested runner
options alone.** Existing consumers intentionally bind the eight-step experiment:

| Consumer | Current restriction | Needed for a separately approved variant |
| --- | --- | --- |
| `aw/pc_v0_report.py:load_group` | Requires eight steps / rate 0.1; solver settings are also in paired-input identity | Explicit variant specification, distinct report/population label and treatment-aware pairing; preserve the default experiment checks |
| `aw/pc_harm_readout.py:run` | Uses that loader and reconstructs default solver settings | Variant-aware loading and restoration from the cell's actual configuration |
| `aw/pc_v1_readout.py:PCPositionBatchReader.from_checkpoint` | Admits eight-step snapshots only | Admit approved settings and construct the matching rate before strict snapshot restore |
| `aw/presentation_pc.py` and result-source register | Describe the original fixed treatment and source plan | Keep contingency results separate; do not fill the original eight-step slots with tuned outcomes |

These are follow-up integration tasks, not defects in the current default run.
I left the live reporting chain intact rather than weakening its specification
checks. Capstan can schedule this additional CPU lane before a contingency is
launched; the staged driver code itself is ready for its safe boundary.
Any “retry only failed cells” exploration should be labelled outcome-selected;
choose settings on development and retain the full paired design for the stated
comparison rather than replacing unfavorable original results.

## Validation

`aw/tests/test_pc9.py`: **18 CPU tests pass**. Tests use the actual tiny EPC solver
at 16 and 32 steps, test the changed-rate one-step identity, count real operations,
verify fixed-v5 constructor/query-state parity, preserve failed-cell settings,
exercise native endpoint execution, reject a mismatched profile and check child
argument forwarding with subprocesses stubbed. Cost fixtures distinguish fixed
overhead from query scaling and reject inconsistent completed records.

The broader `aw/tests -m 'not slow'` pass has **114 passing tests, two deselected**;
it ran before the final three additional constructor/failure tests. The final
18-test PC-9 pass includes those three. Lint passes for new modules and candidates
at their intended `aw/` paths. No GPU, existing runner edit, staging or commit.
