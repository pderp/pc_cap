# Round19 approved edits applied

Status: all three authorized patches applied exactly; follow-up verification found two additional
edits that await permission. Agent: Codex,2026-09-16. GPU time:0; commits:0.

This record updates the status of the earlier immutable round19 handoff and edit request. Those
files describe the state before approval and have been preserved.

Applied:

1. `scripts/r1_77_queue.py`: sealed backend dispatch, final matrix/population checks and canonical locks.
2. `scripts/r1_76_unseen_common.py`: labelled DEC-056 MQuAKE100/300 cadence, with1000 explicitly absent.
3. `scripts/r1_58c_draw_seal_preflight.py`: validate the Markdown protocol by hash at its actual docs path.

Source/patch hashes and approval receipt: `logs/r1_round19/approved-edits-applied.json`.
The four new focused CPU test modules pass **34 tests in23.72s**. Lint passes on all affected scripts
and tests. Logs: `approved-edits-tests.txt`, `approved-edits-lint.txt` under `logs/r1_round19/`.

The four regenerated dry-run reports are `r1-58c-{clearance,draw,seal,freeze}-approved-dry.json` in
that directory. They validate the bound input hashes and correctly refuse for2,5,7 and10 missing
owner receipts respectively. No protocol-parsing blocker remains. No draw/seal/freeze occurs.

A new `R1-76b-mquake-historical-v2.population.spec.json` binds the approved runner. Its production
population validation succeeds, but full metadata inspection remains blocked: the original loader
rejects three bound provenance files under assets. Separately, the older queue suite has one stale
expected-error-string assertion (10 pass,1 fails); draft execution remains refused correctly.

The exact narrowly scoped follow-up patches, tests and requested permission are in
`CODEX-R1-round19-followup-edit-request.md`. The proposed metadata fix passes7 checks; the corrected
older queue suite passes11. Neither follow-up has been applied. The v2 MQuAKE spec is **not yet
ready for execution**. After approval, a new v3 spec will bind the repaired loader.

Only the three approved existing source files were edited. All subsequent reports, tests, specs and
patches are new files. The orchestrator's results, running GPU jobs, installed source tree, previous
reports, task board, protocols and sibling repositories were left alone. Nothing was committed.
