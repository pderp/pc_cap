# P2/X2 addendum: concurrent v3 transition

The main reports `logs/reproduce_final.md` and `logs/review_report_draft1.md` capture completed **v2** evidence at commit `170fad3`. While their final checks were running, the lead/orchestrator committed:

- `b48dff1`: DEC-029, deterministic grammar paraphrase seeds and queue dataset filtering.
- `2b35079`: DEC-030, the v3 final freeze and grammar-only rerun schedule. The lead queue explicitly says the Codex lanes otherwise remain unchanged.

The new freeze is `frozen-confirmatory-v3-163d04e2`, source `67787f49ec16f1bbc7b0a51fa8f019597ed238a7b80a630c16facc6bc7dc5069`. The exact v2 manifest used for the earlier audit is now archived at `manifests/archive/frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json`. Its hash still matches the recorded v2 evidence. zsRE, CounterFact and S5 continue to use v2 results; v3 supersedes grammar only. No results from different identities were merged in these reviews.

## Additional CPU checks

[summary.json](summary.json) records three fresh-shell ENV-05 invocations:

1. Cross-process paraphrase regression, ablation-knob tests and the confirm CLI test module: **24 passed in 16.57 s**.
2. `queue --dataset grammar --dry-run` in a new empty result copy: **60 scheduled, zero executed**, no other dataset selected.
3. One v3 grammar C0 `run --mode confirm --dry-run`: **exit 0** with the matching v3 source and freeze. No model preflight or GPU execution.

The earlier exit-2 dry-run correctly described the then-current pre-v3 tree against the v2 freeze; it is **not** the current v3 behavior. The source snapshot with which it was recorded remains available and hash bound in the earlier logs.

## New finding X2-13: residual missing paraphrases

A full CPU generator inventory check found **4/1/2 zero-paraphrase items** in v3 realizations 0/1/2. The deterministic seed fix removes process salt, but the unchanged 50-try search still leaves seven undefined RET-GS outcomes. See the [urgent finding](../../docs/tasks/P2-X2-v3-paraphrase-coverage.md) and [coverage evidence](paraphrase_coverage.json). These are expected evaluation-coverage gaps, not model results. The active grammar rerun should not be called a complete confirmatory row merely because seeds are now deterministic.

The main X2 report's twelve v2 finding groups remain evidence-based. Its statements that the seed fix/source version still awaited action are historical: DEC-029/030 now records and applies those changes. The remaining issues are complete paraphrase coverage, the unchanged v2 numerical/reporting findings, full-validation drift, and complete cost reconciliation. SD-22 option (c) has been chosen; it is no longer an unanswered choice. A v3 result update and any consequent report regeneration stay with the run owner.

## Proposal versions and preserved files

The original documentation proposal and source patch are retained as snapshot artifacts under the new-files-only rule. The initial source hunk no longer applies because the new queue filter added `dataset=args.dataset` to its context. The current proposals are:

- [Documentation corrections v2](../../docs/tasks/P2-X2-documentation-corrections-v2.patch), with the [current edit request](../../docs/tasks/P2-X2-documentation-edit-request-v2.json). These distinguish the reviewed v2 results from the active v3 phase.
- [S5 directory-creation source proposal rebased onto v3](../../docs/tasks/P2-s5-dryrun-directory-v3-source.patch). This is **not applied** and requires separate permission and versioned source handling. The earlier missing-directory counterexample and successful directory workaround remain applicable.

Only newly created audit files were written. The active queue and all current source/manifest/report files were left to their owner. These additional checks used zero GPU seconds. No commit was made.
