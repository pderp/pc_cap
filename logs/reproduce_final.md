# P2 final-tree CPU reproduction audit

Codex, 13 September 2026. Source snapshot `170fad3ac538ea0df90d0993aa44e2af71628ec0`. S8-02 was marked done before this audit.

**CPU audit complete, with one fresh-checkout defect and the expected frozen-code refusal documented.** All documented CPU paths have a successful invocation after resolving their isolated prerequisites. A current-tree confirm dry-run correctly refuses with exit 2; a separate historical frozen-source positive control resolves the same job with exit 0. No production job or GPU test was executed.

## Results that reproduce

- **360 tests passed, 5 skipped, 52 deselected** in 58.95 s, using `make PY="$P" test-fast` in the recreated ENV-05 environment. The existing JAX/multiprocessing fork warning was emitted; the suite completed. This selector is not the complete slow/GPU/PC-10 control suite.
- The OpenWebText shard rebuild reproduced the pinned **52,500,000-token** shard. The corrected `../assets` command is executable with the documented sibling directory layout.
- CPU grammar training, competence, generator, streams, tracing, calibration, a fresh C2 development run and the grammar summary completed. The fresh run destination was omitted from the initial copy, so no `--force` rerun was needed.
- Retraining produced **bit-identical parameter arrays** to the committed grammar resource. The NPZ container hashes differ; no new container was substituted for the frozen identity. See [grammar_retraining_comparison.json](reproduce_final_20260913/grammar_retraining_comparison.json).
- Regenerated **zsRE paired analysis, resource views, zsRE C2 order summary and all four S7 checkpoint summaries** exactly match the original numerical sections. The comparison record is [numeric_checks.json](review_report_draft1/numeric_checks.json). Timestamps and presentation-only metadata are excluded where appropriate.
- Read-only progress reports confirm **210/210 S4** and **60/60 S5** completed.
- S4 and S5 queue previews list 210/60 attempts and execute **zero jobs** in an empty result copy. S5’s generic `unavailable=30` count refers to reused SB cells; it is not 30 unavailable S5 experiments.

## Fresh-checkout defect and confirm dry-run boundary

The initial regeneration copy intentionally excluded the final frozen manifest. Its two queue previews correctly refused with exit 2. After copying the existing lead-authored freeze into that new location and regenerating a matching schedule, S4 preview passed. S5 then raised `FileNotFoundError` because `results/S5` did not exist: `execute.main` writes its summary without first ensuring that directory exists, and dry-run does not create it through job execution. Creating the missing directory in the isolated copy made S5 preview pass. These initial failures remain in the evidence; they are not silently reclassified as passes.

The production source at `9b1d9984c3d4…` differs from the frozen `0f20e120067b…`; the requested confirm-mode job with `--dry-run` therefore returns **exit 2 before execution**. This is expected enforcement, not an audit failure to bypass. The positive control materialized only the historical source at `6b4b769` and a copy of the unchanged final manifest in a separate new directory. Its tree matches the frozen identity, and the same job resolves with exit 0. It checks configuration admission only: no GPU, model preflight, learner update, checkpoint load or sealed payload read occurs in dry-run. No `--allow-code-drift` was used.

A minimal [source proposal](../docs/tasks/P2-s5-dryrun-directory.patch) creates the output directory before rendering the queue summary. It is not applied or represented as a tested source repair; the successful directory-creation workaround is the executed evidence. Applying a harness fix requires the user’s permission and a recorded source/version decision. The [documentation patch](../docs/tasks/P2-X2-documentation-corrections.patch) instead documents the runnable workaround and the dry-run boundary.

## Exact invocation record

There were **38 invocations**: 34 returned zero, three returned 2 (two missing-freeze prerequisite checks and the expected current-tree refusal), and one returned 1 (the S5 missing-directory defect, then resolved). The initial sequence including setup took **194.94 s**; subsequent prerequisite/workaround calls are separately timed. GPU seconds: **0**.

| Invocation | Exit | Seconds | Interpretation |
| --- | ---: | ---: | --- |
| [01_environment](reproduce_final_20260913/01_environment.txt) | 0 | 1.62 | completed |
| [02_assets](reproduce_final_20260913/02_assets.txt) | 0 | 0.66 | completed |
| [03_schema](reproduce_final_20260913/03_schema.txt) | 0 | 0.92 | completed |
| [04_test_fast](reproduce_final_20260913/04_test_fast.txt) | 0 | 59.98 | completed |
| [05_report_s0](reproduce_final_20260913/05_report_s0.txt) | 0 | 0.86 | completed |
| [06_report_s1](reproduce_final_20260913/06_report_s1.txt) | 0 | 0.92 | completed |
| [07_splits_audit](reproduce_final_20260913/07_splits_audit.txt) | 0 | 0.87 | completed |
| [08_cr_distribution](reproduce_final_20260913/08_cr_distribution.txt) | 0 | 0.86 | completed |
| [09_distill_data](reproduce_final_20260913/09_distill_data.txt) | 0 | 23.75 | completed |
| [10_pilot_compare](reproduce_final_20260913/10_pilot_compare.txt) | 0 | 0.16 | completed |
| [11_merge_throughput](reproduce_final_20260913/11_merge_throughput.txt) | 0 | 0.02 | completed |
| [12_d1](reproduce_final_20260913/12_d1.txt) | 0 | 0.86 | completed |
| [13_short_editing](reproduce_final_20260913/13_short_editing.txt) | 0 | 0.92 | completed |
| [14_d2](reproduce_final_20260913/14_d2.txt) | 0 | 0.86 | completed |
| [15_grammar_generator](reproduce_final_20260913/15_grammar_generator.txt) | 0 | 0.97 | completed |
| [16_grammar_training](reproduce_final_20260913/16_grammar_training.txt) | 0 | 9.40 | completed |
| [17_grammar_competence](reproduce_final_20260913/17_grammar_competence.txt) | 0 | 35.33 | completed |
| [18_grammar_streams](reproduce_final_20260913/18_grammar_streams.txt) | 0 | 1.12 | completed |
| [19_grammar_tracing](reproduce_final_20260913/19_grammar_tracing.txt) | 0 | 2.37 | completed |
| [20_grammar_calibration](reproduce_final_20260913/20_grammar_calibration.txt) | 0 | 3.22 | completed |
| [21_grammar_run](reproduce_final_20260913/21_grammar_run.txt) | 0 | 34.57 | completed |
| [22_grammar_analysis](reproduce_final_20260913/22_grammar_analysis.txt) | 0 | 1.02 | completed |
| [23_draft](reproduce_final_20260913/23_draft.txt) | 0 | 1.77 | completed |
| [24_schedule](reproduce_final_20260913/24_schedule.txt) | 0 | 0.87 | completed |
| [25_resource_analysis](reproduce_final_20260913/25_resource_analysis.txt) | 0 | 3.77 | completed |
| [26_paired_analysis](reproduce_final_20260913/26_paired_analysis.txt) | 0 | 2.12 | completed |
| [27_order_analysis](reproduce_final_20260913/27_order_analysis.txt) | 0 | 1.17 | completed |
| [28_progress_s4](reproduce_final_20260913/28_progress_s4.txt) | 0 | 0.06 | completed |
| [29_progress_s5](reproduce_final_20260913/29_progress_s5.txt) | 0 | 0.03 | completed |
| [30_queue_S4](reproduce_final_20260913/30_queue_S4.txt) | 2 | 0.86 | missing final freeze in initial regeneration copy; followed up |
| [30_queue_S5](reproduce_final_20260913/30_queue_S5.txt) | 2 | 0.86 | missing final freeze in initial regeneration copy; followed up |
| [31_final_tree_confirm_dryrun](reproduce_final_20260913/31_final_tree_confirm_dryrun.txt) | 2 | 0.96 | expected source-drift refusal |
| [32_frozen_tree_confirm_dryrun](reproduce_final_20260913/32_frozen_tree_confirm_dryrun.txt) | 0 | 0.91 | historical frozen-source admission only |
| [33_s7_summary](reproduce_final_20260913/33_s7_summary.txt) | 0 | 0.03 | completed |
| [01_frozen_schedule](reproduce_final_20260913/queue_followup/01_frozen_schedule.txt) | 0 | 0.92 | completed |
| [02_s4_dry_queue](reproduce_final_20260913/queue_followup/02_s4_dry_queue.txt) | 0 | 0.92 | completed |
| [03_s5_dry_queue](reproduce_final_20260913/queue_followup/03_s5_dry_queue.txt) | 1 | 0.92 | fresh-checkout output-directory defect; followed up |
| [S5 dry-run after creating output directory](reproduce_final_20260913/queue_followup_missing_parent/s5_dry_queue.txt) | 0 | 0.91 | completed |

Exact shell commands, cwd and outcomes are in [summary.json](reproduce_final_20260913/summary.json), [queue follow-up](reproduce_final_20260913/queue_followup/summary.json), and [directory follow-up](reproduce_final_20260913/queue_followup_missing_parent/summary.json). Fresh shells use `bash --noprofile --norc -c`.

## Isolation and command coverage

Code copy: `pc_cap/.worktrees/reproduce_final_20260913/pc_cap`; resources: `/home/derp/cap/assets/tmp/reproduce_final_20260913`. The copy’s sibling `assets` link points to those independent resource copies. Regeneration writes only these new copies; original assets and repository records remain unchanged. Historical development inputs are copied for the report renderers; rendering them does not rerun their original GPU experiments. The recreated interpreter is `/home/derp/cap/assets/envs/venv-check-plan6-df/bin/python`; PYTHONPATH explicitly selects each audited source tree. CUDA is hidden, JAX is forced to CPU, caches/temp files are isolated, bytecode and pytest caches are disabled, and the sibling reference path is explicit. Git ceiling settings prevent the copy from silently discovering the parent checkout’s commit. The isolated draft consequently is not a final freeze artifact.

Live analytical inputs were read through the existing CPU interfaces; `--out` points to new audit artifacts. The paired CLI’s expected inventory uses the sanctioned confirmation loader. Sealed files were never copied or opened directly by an audit script. `scripts/s7_summary.py` has no output argument, so its reversal records were copied to the isolated root before rendering. All originally copied live input hashes remained unchanged during the sequence.

The 27 CPU commands from the earlier Lane P inventory were repeated with the current document’s asset path, explicit freeze allowances and experiment IDs. Additional calls cover progress, both queue stages, current/frozen-source confirm dry-runs and S7 summary. Commands containing `<id>`, `<npz>`, `<same npz>`, `N` or bracketed optional flags require substitution; the queue previews use actual flags rather than passing bracketed pseudocode to a shell.

The GPU-tagged controls, BP/ePC property measurements, teacher generation, calibration, A-screening, REG execution/preflight, throughput and BP development run were classified rather than executed. The lead-only final freeze and sealed-realization creation were also not performed. Their inventory is in [setup.json](reproduce_final_20260913/setup.json); these are intentional audit boundaries, not claimed CPU successes. The requested P2 lane is expressly CPU-only, although the older S8-01 task text also discusses future GPU reproduction.

## Handoff

P2’s independent audit is complete; the orchestrator can mirror it to S8-01. The report has substantive X2 corrections in [review_report_draft1.md](review_report_draft1.md). Existing-document changes are prepared in [P2-X2-documentation-corrections.patch](../docs/tasks/P2-X2-documentation-corrections.patch) with before/after hashes in its [edit request](../docs/tasks/P2-X2-documentation-edit-request.json); they await permission. No shared task board, source module, scientific result or existing document was edited. No commit was made.
