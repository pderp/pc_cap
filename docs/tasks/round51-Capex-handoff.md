# Round 51 — Capex handoff

2026-09-27. **PC-10 prepared on tested copies; X24 passes the finished subset;
REV-3 complete.** PC-8 still waits for the complete 60-cell run and harm output.

- **[PC-10](PC-10.md):** config/finish treatment validation, separate reports
  and sweep tables, treatment-aware harm restoration and fixed-v5 snapshot
  support. No mixed-treatment pooling. The combined PC-9/PC-10 patch reproduces
  all six candidate files when applied to copies. Exact safe-boundary apply
  commands are in the task record; no live file was patched.
- **[X24](X24.md):** at **11:46 EDT**, all **44 finished cells** pass, forming
  **22 complete pairs**. The remaining 16 cells are pending. Ordered items,
  calibration/seeds, fresh memory, unchanged base, scoring schemas and credit
  costs check out; no efficacy values were decoded or published. Rerun with
  `--require-complete` before PC-8, while the original source tree is intact.
- **[REV-3](REV-3.md):** [Tuesday decision form](../presentation/final-experiments.md),
  with identical export under `assets/presentation-materials/review-data/`.
  All seven candidates have question/design/population/cost/deadline/theme
  fields; decision, owner and start stay blank. No experiment is ranked or selected.

Validation: **129 final broader CPU tests passed, two slow tests deselected**;
**12 final targeted tests passed** (overlapping counts). Lint and exact combined-patch application to disposable copies pass.
Logs: `logs/additional_work/round51/`; audit: `logs/r1_x24/`.

No GPU use, scorer changes, frozen-source edits, queue operations, staging or
commit. Existing live PC-v0 result changes and final-queue launch/resume logs
belong to operations. New owned files are the PC-10 staging helper/candidates,
X24 audit and both test modules, reviewer form, task records and round-51 logs.
Apply PC-9/PC-10 only after the existing source-bound chain's reports/exports
exist and Capstan confirms an idle boundary; preserve the old source version and
obtain matching new profiles before any approved contingency run.
