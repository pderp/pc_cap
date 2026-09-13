# P2 / X2 handoff, 13 September 2026

**Both assigned CPU lanes are complete. The active v3 grammar rerun has a newly identified coverage issue for the lead/run owner.** No existing live file was edited and no commit was made.

Read these files in order:

1. [V3 paraphrase coverage finding](../docs/tasks/P2-X2-v3-paraphrase-coverage.md): deterministic generation still leaves **seven items without paraphrases** (4/1/2 by realization). The unchanged missing-pair policy can therefore still prevent a complete grammar classification. No queue or policy action was taken by this lane.
2. [V3 transition addendum](p2_x2_v3_transition/review.md): the lead committed DEC-029/030 during the audit. **24 affected tests pass**; a 60-job grammar-only preview executes nothing; the matching-source v3 confirm dry-run passes. This supersedes the main reports' historical statements that the seed fix/version choice were still pending.
3. [P2 reproduction audit](reproduce_final.md): the full `170fad3` snapshot passed **360 CPU tests**, and saved paired/resource/order/S7 numerical outputs reproduce exactly. The fresh-checkout S5 directory defect has a tested directory-creation workaround and an unapplied source proposal. The original sequence and follow-ups retain every failure/refusal and its explanation.
4. [X2 report review](review_report_draft1.md): twelve v2 finding groups plus the additional v3 coverage finding above. All 270 v2 runs and descriptive means check out; constraint labels, missingness counts, causal/equivalence language, drift coverage, source history, order variation and budget reporting need correction. V2 classifications remain zsRE negative, CounterFact negative at the observed floor, grammar incomplete.

The **current documentation proposal** is [P2-X2-documentation-corrections-v2.patch](../docs/tasks/P2-X2-documentation-corrections-v2.patch), covering `docs/D3_decision.md`, `docs/report.md`, and `docs/REPRODUCE.md`. Its [edit request](../docs/tasks/P2-X2-documentation-edit-request-v2.json) has the exact before/after hashes. It describes the reviewed v2 results separately from the active v3 phase. Permission is still required to apply it.

The separate [S5 source proposal against v3](../docs/tasks/P2-s5-dryrun-directory-v3-source.patch) requires source/version approval before application. The old source hunk targets the earlier snapshot and was superseded after the concurrent dataset-filter change. No source proposal was applied to the frozen tree.

Reproducer scripts have exclusive output destinations to protect evidence; they are snapshot-specific, not arbitrary-current-tree rerun recipes. The primary P2 copy and archived v2 manifest retain the old execution identity. The transition copy records the v3 source separately. S5 keeps v2 results; an S5 queue preview for that historical programme belongs in the v2 metadata copy, not a new v3 S5 experiment.

Completion evidence: [CODEX-P2-X2-20260913.completion.json](../docs/tasks/CODEX-P2-X2-20260913.completion.json). The orchestrator can mirror P2/S8-01 and X2 to the board. T4 / CP-F, whole-validation drift remediation, complete cost reconciliation and the active grammar outcome remain owner/lead actions.
