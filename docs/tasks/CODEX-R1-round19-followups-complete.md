# Round19 follow-up repairs complete

Status: both additional edits approved by the lead, applied exactly and validated.
Agent: Codex, 2026-09-16. This new record supersedes the pending-repair status in
`CODEX-R1-round19-followup-edit-request.md` and `CODEX-R1-round19-approved-edits.md`.
Previous records and spec versions remain unchanged as audit history.

## Changes

- `scripts/r1_76_unseen_common.py`: DEC-056 MQuAKE provenance can include only the exact
  prepared-items file and the default snapshot's tokenizer/configuration files. All three
  still require their bound SHA256. Other external resources and sealed paths remain refused.
- `tests/revision_v1/test_r1_77_queue.py`: the draft-execution refusal assertion now matches
  the approved queue's message. The test continues requiring a PermissionError.

Input and patch identities: `R1-76b-metadata-resource-edit-bindings.json` and
`R1-77b-legacy-test-edit-bindings.json`. Applied source hashes were checked again after validation.

## Validated owner handoff

Use **`docs/tasks/R1-76b-mquake-historical-v3.population.spec.json`**. It binds the repaired
runner and the unchanged population of300 edits and100 fixed outside prompts. Checkpoints
are100 and300;1000 remains explicitly absent. All14 source bindings verify. Every row retains
the historical-exposure label and the bounded review's previously documented limitations,
including cached teacher evidence without a historical base-weight hash.

The following metadata inspection completed successfully without constructing a model:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.r1_76_unseen_common --spec docs/tasks/R1-76b-mquake-historical-v3.population.spec.json
```

The v1/v2 specs are historical; their old runner hashes should not be used for execution.
Actual GPU execution remains the orchestrator's scheduled task after the stress panel.

## Verification and completion

**52 CPU tests passed in25.20s**, covering the four round19 modules, the new metadata-resource
admission tests and the existing queue regression suite. Lint and the targeted Git diff check pass.
There are no remaining known test failures or approval requests for these repairs.

Evidence under `logs/r1_round19/`:

- `approved-followups-applied.json`: approval, exact patches and before/after identities.
- `approved-followups-tests.txt` and `approved-followups-lint.txt`: validation output.
- `r1-76b-v3-spec-inspection.txt` and `.json`: successful CLI inspection and source verification.
- `approved-followups-verification.json`: final completion receipt.

Done-when: both approved edits applied; new spec bound to the final runner; full metadata inspection
successful; affected CPU tests and lint passing. All satisfied. GPU cost:0. No real-base experiment,
draw, seal, freeze, staging or commit occurred. Other than the two approved targets, this follow-up
created new files only. No change to the orchestrator's running jobs or result files was made.
