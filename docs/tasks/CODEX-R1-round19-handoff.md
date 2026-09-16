# Codex round19 handoff

Status: available CPU preparation complete; three existing-file edits await lead permission.
Agent: Codex, 2026-09-16. Claim: `CODEX-R1-round19.claim.json`; later DEC-056 lane recorded in
`CODEX-R1-round19-claim-addendum.json`. The owner committed other work during this round; no Codex
commit/stage occurred. Existing source files and `results/R1/` were not modified by this work.

| Lane | Delivered | Remaining dependency |
| --- | --- | --- |
| R1-77b | Separate sealed admission/execution backend, metadata API, cost envelopes,29 backend/queue/parity tests, concrete dispatch patch | Lead approves queue edit; owner reviews/materializes final frozen authority and does real-base admission |
| R1-76b | Historical1200→700→657 bounded review;300 edits+outside100; labelled assets population; versioned spec; narrow cadence patch | Approve runner edit, create a new spec binding its new hash; owner runs after stress panel |
| R1-58c | Exact draw/seal/freeze checklist, named admission inputs, four dry commands and corrected refusal previews | Approve Markdown-binding correction; owner clearance/protocol/RNG/seal/cost receipts and final draw adapter remain absent |
| R1-49f | Q11–Q13 proposed defaults, alternatives, consequences and exact protocol insertion text | Orchestrator posts questions; lead decides; no protocol change inferred |
| HT-3e | Prerequisite checked | `results/R1/ht3d_final/` absent at handoff; do not label the round18 watcher output as the orchestrator's final report |
| R1-73b | Prerequisite checked | `results/R1/calibration_mquake_v3/calibration_candidate.json` absent at handoff |

The previous round18 after-chain watcher has now produced `logs/r1_round18/ht3d-after-chain-host.json`.
That is useful upstream evidence for the orchestrator's final aggregation. The designated final pilot
review lane remains pending its requested owner artifact. No new GPU worker or background monitor
was started in round19. October9 remains the experimental deadline.

## Read first

- `CODEX-R1-round19-edit-request.md`: three exact proposed edits and their boundaries.
- `R1-77b-sealed-backend.md`: the proposed final freeze/protocol/recipe contract and operational limits.
- `R1-76b-mquake-occupancy-review.md`:657 survivors, cached-teacher provenance limit, and exact
  CPU-only version2 spec rebinding step after runner approval.
- `R1-58c-draw-seal-plan-v2.md`: checklist, command sequence and owner implementation gaps.
- `R1-49f-lead-bindings.md`: proposed scientific decisions, not accepted thresholds.

## Verification and pending correction

29 tests pass against the proposed queue/cadence/preflight changes, plus five additional sealed
parity/identity tests. Lint and the three-patch Git apply check pass. Evidence:
`logs/r1_round19/proposed-patches-tests-v2.txt`, `logs/r1_round19/lint.txt`,
`logs/r1_round19/completion.json`. Tests use JAX CPU and isolated TinyBase fixture roots.

There is **one known current-tree test failure**, intentionally not hidden: the new dry preflight
initially treated the Markdown protocol like JSON and restricted it to `docs/tasks`. The tested
**v2** correction awaits permission because the new-files-only rule also applies to a file created
this round. Its corrected previews contain only the genuine absent-receipt blockers. The first
`R1-58c-markdown-binding.patch` is superseded. Do not apply it.

After the three approved source patches, use:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m pytest -q -p no:cacheprovider tests/revision_v1/test_r1_77b_sealed_backend.py tests/revision_v1/test_r1_77b_integrity_additional.py tests/revision_v1/test_r1_77b_queue_dispatch.py tests/revision_v1/test_r1_round19_preflight.py --basetemp=logs/r1_round19/pytest-approved
```

The new preflight tests use the applied source directly once its correction is present. The queue
and cadence tests can apply the proposed patches entirely in memory before approval. Regenerate
previews under new filenames; preserve all prior reports and input versions. Rebind the MQuAKE
spec to a new version, inspect it without a model, and leave actual execution to the orchestrator.

## Intended review / eventual commit set

Three new scripts: `r1_77b_sealed_backend.py`, `r1_76b_mquake_review.py`,
`r1_58c_draw_seal_preflight.py`. Four new tests: `test_r1_77b_sealed_backend.py`,
`test_r1_77b_integrity_additional.py`, `test_r1_77b_queue_dispatch.py`,
`test_r1_round19_preflight.py`. Include this round's task documents/specs/patches and final JSON/text
reports under `logs/r1_round19/`. The local `.gitignore` keeps immutable draft Python previews,
pytest scratch and detailed synthetic fixture trees out of normal staging; they remain on disk.
Resources are in assets and never part of the repository commit. Do not stage the owner's active
comparator log merely because it appears in `git diff`.

No board row, protocol, decision, source under src/pccap, existing result, old report, sibling repo,
service or environment was edited. The proposals do not approve a draw, seal, freeze, launch or commit.
