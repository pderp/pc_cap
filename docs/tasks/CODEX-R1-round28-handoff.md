# Round 28 handoff — protocol repairs, typed costs and four owner recipes

Codex completed the available CPU preparation from `docs/ongoing.md` against
incoming commit `23e8325`. **No GPU/model execution, actual population operation,
signature, staging or commit.** Changes are left for the lead/Claude to review
and commit. No `src/pccap` or sibling repository files were edited.

| Lane | Delivered | Remaining dependency |
|---|---|---|
| R1-49j | D.1 amendment, six-document normative closure, unchanged 360+45-cell matrix and mutation checks | Formal protocol admission |
| R1-58h | Typed cost producer/validator, source-bound v2 draft, operator integration and 6 GiB launch floor | Full-endpoint runs, host peaks, full-validation evidence, reviewed transfer assumptions and approval |
| R1-64f | Four validated zsRE/MQuAKE × primary-v5/v0-stable recipes and exposed-development payloads | Claude's GPU execution and telemetry |
| R1-63i | Candidate v12, inputs/forms v7, operator sheet v6, production-bundle interface | Measurement/gate closure, missing whole assembler, refreshed final requests and actual admissions |
| X17 | Machine audit and written re-review | Verdict remains not ready for signature or launch |
| HT-4f | Updated waiting record | Complete valid signed cost receipt; then current-input ledger producer |

## Immediate handoff to Claude

Use [the four-cell run list](R1-64f/ordered-runlist.md). Each recipe has 300 edits,
checkpoints 100/300, near-miss 100 and revision 50. Both conditions use each
dataset's identical payload. Inspection already passes the current driver loader.
Execution needs JAX CUDA and the GPU lease; capture process RSS and outer wall
time as well as the driver's JAX device peaks. The primary MQuAKE recipe preserves
the selected averaged v5 reader and rare-token gate. These exposed-development
recipes are separate from the DEC-056 occupancy diagnostic and production draw.

The pending cost source can ingest completed R1-64f driver results. Rebuild into
new paths as shown in [R1-58h](R1-58h.md), preserving this reviewed draft. A further
input extension is needed for host-envelope and full-validation evidence. Four
representative runs do not automatically supply measurements for all other
conditions; record any accepted extrapolation explicitly before admission.

The [production-bundle interface](R1-63i-production-bundle-interface.md) lists
exactly what publication needs and which component producers exist. The whole
final-recipe/freeze assembler is still missing. It can be implemented while the
development profiles run, using fixtures until actual authorized population
artifacts exist. Formal exposure attestation must incorporate the four new
recipe declarations; zero subject overlap was checked but does not replace that
attestation.

## Current reviewable package

- Protocol: `docs/R1_stage4_protocol_v5_2_D_1.md`.
- Matrix: `manifests/revision_v1/run_matrix_v5_2_D_1.json`.
- Candidate: `manifests/revision_v1/freeze_candidate_v12.json`, 1,408 bindings.
- Inputs/forms: `docs/tasks/R1-D9-inputs-v7.json` and v7 templates.
- Operator instructions: [sheet v6](R1-D9-operator-sheet-v6.md).
- Cost draft: `docs/tasks/R1-cost-admission-receipt-v2.json` (byte-identical to
  `R1-cost-admission-receipt-v2-review.json`).
- Review: [X17 report](../../logs/r1_round28/X17-review.md) and
  `logs/r1_round28/r1-x17-review.json`.
- Current proof: `logs/r1_round28/r1-63i-verification.json` and
  `operator-protocol-current-dry.json`.

Do not use the earlier v12 build console or first protocol dry preview as the
current digest: host-floor forwarding changed the operator binding before final
review. Previous bytes and proof are retained under `source_snapshot/`. Likewise,
the initial cost parser draft is superseded by the corrected canonical v2, which
verifies batched phase journals. New evidence requires refreshed successor
bindings and request digests; no historical approval is portable.

## Readiness and validation

X17 verifies the protocol repair and current package, but **17 gate IDs remain
open**. There are 45 detailed pending cost reasons and 51 total non-signature
blocker entries. These are evidence dependencies, not merely missing signatures.
The expected combined process-time projection is 254.7825 h; the proposed budget
is 750 h. The extreme two-attempt padded sum is 764.3475 h, so budget exhaustion
can leave cells incomplete. Preserve October 9 as the experimental stop.

The combined CPU suite passed **100 tests**. Following the final host-floor
forwarding change, **18 focused operator/package/queue tests** passed; ten overlap
the first suite. Logs: `regression-tests.txt` and `final-operator-queue-tests.txt`
under `logs/r1_round28/`. Final lint, whitespace, current binding and source-state
checks are recorded in `logs/r1_round28/handoff-validation.json`.

Existing edits are limited to four scripts (candidate verifier, cost preflight,
D9 implementation binding and operator) and two current-package test pointers.
Other implementation/test/documentation artifacts are new. Synthetic CPU test
outputs also appear under prior-round rehearsal/operator-log directories and the
queue-lock directory; they are fixtures, not production observations. Resources
remain outside the repo under `assets/`. The claim record tracks delivered lanes
and remaining owner dependencies without marking scientific admission complete.
