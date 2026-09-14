# Codex round 7 — completion and owner handoff

2026-09-14. All five assigned CPU lanes are delivered. Initial source HEAD `0d79f51`; the owner committed completed continuation jobs as `9c459aa` during final review. Codex did not stage or commit work.

**Read the [Stage 2 addendum](../R1_stage2_report_draft_addendum.md) with the [main draft](../R1_stage2_report_draft.md).** The late-arriving controls are complete, and the new original-base cap drift result needs diagnosis before a fidelity claim/freeze: learned-cap ordinary-text loss rises +0.599062 nats after zsRE edits and +0.393528 after CounterFact edits on 16,256 sampled positions. These imply perplexity ratios 1.820411 and 1.482201. They are substantial subset findings, not a full-validation estimate or a proven mechanism.

## Completed lanes

| Lane | Deliverable | Validation / remaining owner boundary |
| --- | --- | --- |
| R1-X6 | [Repair/reference/scale audit](../../logs/audit_r1_28b.md), CPU audit script and source-bound JSON | Both scale risks reproduced; logical ledger 6F/6R/331 tokens; cache and population admission still incomplete |
| R1-44 | [Endpoint task/API](R1-44.md), new unseen-prompt module and TinyBase tests | 10 passed; owner wires GPU/other-comparator adapters and reserves |
| R1-40c | [Matrix v3 task](R1-40c.md), [240-cell draft](../../manifests/revision_v1/run_matrix_draft_v3.json), builder | Unlaunchable/unfrozen, four required profiles, all expanded ceilings null |
| R1-D2 | [Candidate task](R1-D2.md), [ordered candidate manifest](../../manifests/revision_v1/counterfact_fresh_candidates_v1.json), resources in assets | Strict v3 0; conditional remainder 12,246 after all other reasons; no new local source, no draw/seal |
| R1-47 | [Paper draft](../R1_stage2_report_draft.md), [completion addendum](../R1_stage2_report_draft_addendum.md), two recount scripts/JSONs | 100 stream summaries inventoried; 84 matching detail sets reconcile; 16 completed continuation cells reconcile |

Shared candidate/matrix tests: **18 passed**; together with endpoint tests, **28 new CPU tests pass**. No real-base/teacher execution by Codex. All scripts were checked with Ruff; see [validation log](../../logs/r1_round7/final_validation.txt). Existing GPU jobs/results were read only, and no sealed payload was opened.

## Key next actions

1. **Ordinary-text cap drift:** run the small fixed-prefix positive/null controls and selection/delta traces specified in the addendum before another broad training sweep. The drift exists in original-base R0, so LM continuation is not its cause. Separate independent-prefix and held-selection assays. This is the highest-priority new scientific risk.
2. **Continuation admission:** literal KD passes its 8,192-position base-fidelity probe; LM fails teacher KL (0.094979 > 0.001) despite improved NLL. Both training budgets reconcile. Do not call LM a fidelity-matched control. A newly constrained treatment or explicit exclusion/reclassification is needed for that final claim. Completed development execution does not automatically bind matrix checkpoint placeholders.
3. **Full endpoint integration:** implement actual memory/firing adapters for v0/comparators; invoke unseen endpoint and actual active-record/byte profiles at 100/300/1,000. Preserve complete versus truncated outcomes and missingness. Distinguish original-base LS from same-condition cap-off unseen reference.
4. **Cache/admission repairs:** include all text/tokens/build inputs and serialized feature checksums; fix legacy migration policy; validate IDs, split ranges, memory/outside availability and actual role coverage. The audit describes concrete CPU reproductions.
5. **Data/budget decisions:** choose the reason-specific CounterFact remainder exception or a reviewed fresh source; finish zsRE E.2/context/alias review; reserve at least 3,300 distinct edit+outside facts per dataset plus other challenges. Execute P1–P4 and reconcile the 240-cell scope with budget. Legacy proxies sum to 222.9 h, already above the approximately 15 h proposal, before pricing new endpoints.

CPU admission fixtures, adapter work and analysis preparation can run while the owner does GPU diagnostics. These are owner/shared-file follow-ups under the existing permission protocol; Codex did not apply shared-file repairs or alter the board. No permission question remains pending for the completed new-file deliverables.

## Provenance and exact scope

The first source check found all 461 bindings unchanged. After the owner's continuation commit, the notes changed. The [second source check](../../logs/r1_round7/final_source_integrity_after_continuation.json) verifies **540 bindings** with every bound version available; the original notes are preserved under `logs/r1_round7/source_snapshots/15c1b2cb472ccf81064905dd073c27954d51f3e2d4573d9bc8265bd77d3df277/docs/R1_stage2_notes.md`. The addendum reviews the newly completed jobs. This avoids rewriting a report/evidence snapshot underneath its SHA-bound inputs.

The ordinary drift assay uses a different dataset/window population from the continuation base-fidelity probe. Small KL does not guarantee identical greedy strings; unchanged editing LS does not certify ordinary-text preservation. Per-position/individual locality output evidence remains a GPU diagnostic task.

All round-7 code, logs, documentation and manifests are under pc_cap. Ordered CounterFact payload/exclusion resources are new files under `/home/derp/cap/assets/data/prepared/revision_v1/r1_d2_v1/`. Sibling repositories and the venv were not changed.

[Artifact inventory](../../logs/r1_round7/artifact_inventory.json) identifies this round's new files for review/manual commit; it excludes owner `results/R1/` artifacts and the pre-existing untracked ledger session log. `CODEX-R1-round7.claim.json` remains as the historical claim; the separate completion JSON records the delivered status.
