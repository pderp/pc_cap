# Ongoing-work reconciliation and Lane P follow-up

This revision supersedes `review.md`: the prior completion record contains 110 owned-file hashes, all unchanged.

Codex, 11 September 2026. CPU only; new files only. This is a completed follow-up to the assignments in `docs/ongoing.md`, not a new production run.

The four Codex round-four lanes already have completion evidence. All 110 recorded owned-file hashes in `docs/tasks/CODEX-round4-20260911.completion.json` were checked for changes; none differed. The apparent open work in `ongoing.md` is partly stale bookkeeping.

| Lane | Evidence-based state | Remaining boundary |
| --- | --- | --- |
| B4-D | The declared two-case gradient localization and reduction replay are complete; `docs/tasks/B4-D.md` and `logs/grace_gradient_localization.md` describe the result. | B4 qualification is still unmet and B4 is excluded from the frozen month programme. A larger diagnostic study is future work, not an unfinished requirement of the two-case policy. The report's 28-to-27 count typo still needs permission to edit. |
| S3-01 | The control table, development coverage and full-before-S7 requirements are complete in `docs/controls.md`; task record is done. | The shared board still says pending. The orchestrator can mirror the completion record; PC-10 must stay explicitly unqualified. |
| V4 | All three S7 repair findings are closed, with nine prior regression tests; `docs/tasks/V4.md` is done. | Production reversals and natural-language semantic contradiction review remain assigned to the orchestrator. |
| P | The original 27-command CPU audit is complete. The subsequent changes to `REPRODUCE.md` required the delta audit below, now complete. | Final S8 reproduction awaits the final research outputs and GPU coordination. |

## Work completed in this follow-up

The exact execution record is [summary.json](summary.json). Twelve fresh-shell CPU invocations returned zero, taking 16.53 seconds of summed subprocess wall time. The copy contained 179 source/input files; none was modified by a command, and no copied live input changed during the audit. The source snapshot was `6b4b76918966487a4f0593bbe8f71d4decb89152`.

| Invocation | Observed result | Interpretation |
| --- | --- | --- |
| CPU environment probe | JAX 0.11.1, CPU, explicit isolated import path | Used the recreated ENV-05 environment; no install or GPU use. |
| Draft freeze with explicit allowances | Schema errors none; pending inputs none | A new draft in the isolated copy, not a final CP-E act. |
| Draft schedule | 210 S4 + 60 S5 scheduled; 30 B4 unavailable; 30 SB reused | Preview only. |
| S4-05 with experiment ID | Zero input runs | Explicit-ID parsing and empty resource views work; no completed comparison claimed. |
| S4-06 with experiment ID | Zero rows; classification incomplete | No sealed payload exists in this copy; expected-item loader coverage is not tested by this empty invocation. |
| S7-03 with experiment ID | Zero runs; variation unavailable | Does not replace production checkpoint analysis. |
| Progress on empty copied queue | 0/210 finished | Read-only progress works against copied schedule/projection metadata. |
| Schedule from copied lead-authored v2 freeze | Hash bound; same 270/30/30 schedule counts | Existing frozen metadata was copied; no new final manifest was generated. |
| S4 queue dry-run | 210 planned attempts, zero executed; B4 skipped | Writes only the new copied dry-run summary; launches no experiment subprocess. |
| S5 queue dry-run | 60 planned attempts, zero executed; 30 SB reuses skipped | The summary's generic `unavailable` counter includes these reused jobs; the job list identifies them as reused, not unavailable science. |
| Five affected regressions | **5 passed in 5.02 s** | Allowances, resume/refusal, S5 reuse, cross-dataset resource binding and stopping after systematic no-item failures. |
| Read-only live progress | 10/210 finished at 18:03:34 UTC (14:03:34 EDT) | Five C0 and five C1 orders of zsRE realization 0; no completed required C2 contrast yet. |

Logs are numbered `01_...txt` through `12_...txt`. Generated isolated artifacts are copied under [generated](generated/). The source copy is `pc_cap/.worktrees/ongoing_followup_20260911`; temporary resources are under `assets/tmp/ongoing_followup_20260911`. No production result tree or sealed realization payload was copied. The only live research outputs read by the progress command were queue summaries and schedule/projection metadata.

The original drivers produced the recorded outputs. The `_v2.py` drivers differ only by removal of an unused import and an import-order comment, respectively; their normalized syntax trees were compared and the v2 files pass Ruff. Both versions refuse to replace their evidence destinations.

## Drift coverage: reproducible finding, not just a prose concern

[drift_coverage.json](drift_coverage.json) records a model-free execution of the actual `Evaluator` window selection and reported position counting. Only the NLL calculation is stubbed, and those stub values are not reported as research results. All ten completed S4 records present at 18:03:41 UTC report 4,064 drift prediction positions.

- SD-3 authorizes the full **247,289-token** validation split; no million-token expansion is needed.
- Current S4/S5 settings select 32 full windows, yielding **4,064 scored positions**.
- Supplying all 247,289 tokens while leaving the evaluator argument at its default still scores **4,064** positions.
- Supplying the explicit full count yields **1,931 full windows / 245,237 positions**, with **121 trailing tokens dropped** and one initial token per full window used only as context.
- Exact-window and partial-tail controls reproduce the counting behavior on tiny synthetic arrays.

The required repair decisions and checks are in [drift_remediation.md](drift_remediation.md). No source change or extra GPU assay was attempted.

## Work that remains outside these completed Codex lanes

Claude retains S4 execution and its resource/paired analysis, S5 substrate execution, S7 checkpoint reversals and semantic review, and the final S8 reproduction/report/handoff. At the captured live status there are 200 S4 jobs remaining. S6 computation is closed for the month under DEC-022; optional CAP-08/CAP-09 and HVP work do not become new core work merely because their board rows are open.

Two existing-document edits are prepared in `docs/tasks/ONGOING-followup-documentation-v2.patch`: correct executable/reproduction guidance in `docs/REPRODUCE.md`, and correct the GRACE boundary count from 28 to 27. `git apply --check` passes. They have not been applied because the user's standing rule requires permission first. Shared task-board and ongoing-log edits remain with the orchestrator.

No existing file was edited, no GPU lease was taken, and no commit was made for this follow-up.
