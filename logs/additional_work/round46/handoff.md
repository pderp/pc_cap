# Round 46 — Capex to charlie and Capstan

2026-09-26. Three assigned CPU lanes delivered. **No GPU execution, queue action,
frozen-tree edit or commit.** The user now calls the Claude agent Capstan and this
Codex agent Capex.

| Lane | Delivered | Remaining owner step |
| --- | --- | --- |
| PC-5 | Checkpoint-restoring paired harm driver, 68f vectors, correct fractional ES99, location/exceedance/concentration summaries, paired differences, separate cost, CPU smoke/tests. Runbook: `docs/tasks/PC-5.md`. | Capstan dispatches after the completed PC-v0 run; account against the shared 8-hour readout ceiling. Later fixed-v5 needs its checkpoint/batch-reader adapter, not a bypass of the frozen reader's exact-class guard. |
| R1-D14f | One-command post-halt refresh plus dry run; preserves unrelated ledger rows and the correct omission reasons. Runbook: `docs/tasks/R1-D14f.md`. | Reconcile halt, post D11 block-5 report and owner note; repair HT-13 before publication. |
| PRES-2 | Full speaker drafts for 2/3/6/11, claim links, renderable specs and four SVG exports; all three central themes. Runbook: `docs/tasks/PRES-2.md`. | charlie reviews wording; Capstan supplies HT-14 and corrected HT-13; insert measured PC outcomes when available. |

**Actionable scientific finding:** `aw.scoring.Accumulator.summary` and HT-13
currently label a 99th percentile as ES99. PC-5 uses the unchanged per-position
scorer and computes the actual worst-1% average separately. See
`docs/tasks/HT-13-round46-review.md` for the minimal owner correction and title /
pooling / reference qualifications. This is reporting code, not contamination
of the running R1 algorithms or registered ES95 results. No reason to abort the
GPU run arises from this finding.

The live dry run saw 253 completed cells; its 270-cell output directory remains
absent. The canonical comparator report is byte-identical to the committed 225
snapshot. Native block-5 completeness remains false at the planned halt because
15 CounterFact cells are deliberately unrun; the wrapper validates the exact
270 prefix without changing that native flag or any recipe.

Final smoke: `results/additional_work/PC-v0/harm/cpu-smoke-round46-v2/`.
Final slide export: `/home/derp/cap/assets/presentation-materials/deck_v3/round46-drafts-v3/`.
Earlier smoke/draft versions are superseded; none is experimental efficacy.
Current source and export identities verify. Slide 6 is a visible pending figure
slot until HT-13 is repaired. HT-14 did not exist when these drafts were prepared.

Validation: **74 passed, one slow real-base test deselected** in the broad CPU
suite; two presentation checks rerun after the final diagram adjustment; Ruff
and `git diff --check` pass. SVG XML and font bounds checked; PC branching diagram
visually reviewed. `final-artifact-check.json` verifies unchanged frozen tree,
unchanged shared scorer/tail generator, no premature comparator publication and
current source/export bindings. The completed round-45 real-base parity test was
not repeated, since no acquisition code changed.
