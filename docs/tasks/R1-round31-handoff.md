# Round 31 handoff — DEC-063 production consumers and protocol D.2

Codex, September 18, 2026. CPU only; no commits, production draw/seal/freeze, real-base execution, GPU lease or installed driver/backend changes. Starting HEAD: `b8c5f89`.

## Outcome and next dependency

| Lane | State | Next action |
|---|---|---|
| R1-63l | Consumers implemented; both synthetic cadences pass; backend admission patch prepared | Owner applies patch after chain S reaches an idle boundary, then rebuilds package identities |
| R1-49k | Complete: D.2 text, seven-document closure, 405-cell planned matrix | Review/admit with the successor package |
| R1-58l | Partial: independent audit of 1/4 chain-S measurements | Finish four donors, explicit transfers, typed v4 validator, ceilings v2 and revised process-hour projection |
| R1-63m | Waiting on R1-58l and backend installation | Candidate v14 / forms v9 / sheet v8; preserve all evidence gaps |
| X19 | Waiting on v14 | Review exact successor package |
| HT-4f | Waiting on signed receipt v4 | Claim ledger v6 |

The currently listed remaining lanes have these explicit dependencies. No missing result or reviewed transfer was invented to move them forward. The preceding v13 package is historical: changed consumer/D9/normative bindings require a successor, not reuse of its old request digests/signatures.

## Scientific finding for the owner

The first completed chain-S learned-reader MQuAKE run independently verifies all **245,237 full-validation predictions**, source identities, finite vectors, receipt chain and sampled overlap. Its mean KL is **.0055436876 nats**, above the registered **.001** limit; mean signed NLL increase is **.0056009764**, below **.01**. Consequently full fidelity fails even though measurement integrity passes. Both references coincide for this condition. This is development evidence and does not support a confirmatory conclusion or a threshold change.

ES95 positive loss harm is .1144675627; ES99 .5723378136; maximum 8.1875503498 nats. These are complete fixed-validation population descriptions, not estimates establishing a power law. Keep the talk's 128-window sampled tail population separate. Review the other classes/datasets before interpreting the generality of this observation. The counterfactual-edit results and fidelity result should remain separately visible.

The full phase costs 1,298.987703 seconds including its outer integrity overhead, versus 138.931263 seconds for both sampled checkpoints combined. Attempt wall is 1,864.606192 seconds; direct GNU time host peak is 2,675.347656 MiB; JAX allocator lifetime peak is 742.720215 MiB. None of these measurements alone prices CounterFact, S1's extra reference, or 1,000-record state. Snapshot and bound sources: [partial measurement inventory](../../logs/r1_round31/chain-s-partial-inventory-v2.json); details: [R1-58l](R1-58l.md).

## Implemented behavior

- Every core/extension recipe, executable protocol, freeze and independent population carries the same source/window/reference/cadence contract and consumer implementation binding. Missing or altered declarations refuse new production assembly/admission.
- Constructor and seal independently bind the sample to the complete source's first 128 windows. D9 authorization digests and receipt review fields include the endpoint, and matrix/spec/draw mismatches cannot downgrade it.
- R1-49g/R1-75 recompute complete loss/KL metrics from the local hash-bound vectors, verify coverage/reference/state and sampled overlap, preserve unavailable/corrupt outcomes, and report completeness and fidelity separately. Sampled checkpoints and full final validation are labelled separately; ES95 and ES99 are both present.
- D.2 states population/tail/context, both references, cadence, storage, overlap, fidelity, confirmatory/descriptive limits, U08/U16 closure and the change log. Its matrix keeps all 360 core + 45 optional cells, all 63 primary intervals, the original contrasts, and all execution/cost flags closed.

Files and implementation details: [R1-63l](R1-63l.md), [R1-49k](R1-49k.md), [protocol D.2](../R1_stage4_protocol_v5_2_D_2.md), [planned matrix](../../manifests/revision_v1/run_matrix_v5_2_D_2.json).

## Verification and coordination

The final focused regression run passed **98 tests** in 8.82 seconds. Both actual synthetic execution cadences passed **5 tests** in 295.99 seconds. The final full-package rerun passed **11 tests** in 485.55 seconds, recorded in `logs/r1_round31/assembly-final-tests.txt`: **114 final focused tests passed**. The earlier full-package/vector run also passed 24 tests. Ruff and `git diff --check` pass; the backend patch passes `git apply --check` and lint as proposed source. This is focused validation, not a claim that the whole repository suite ran.

The generated draft matrix analyzes as 405 expected cells, 21 declared contrasts, zero scientifically admitted cells, all classifications unavailable and all six blocks incomplete. No denominator shrank to the observed subset. The 300/1,000-edit fixtures execute the proposed backend in memory and use synthetic bases, isolated fixture receipts and resources. They grant no real authorization.

All **168 protected source/recipe bindings** and the installed driver code identity remain unchanged: [integrity check](../../logs/r1_round31/final-integrity-check.json). Claude's chain-S progress/run/time/result files are read-only to this work. The backend patch is [ready for the idle boundary](R1-63l-backend.patch); original/proposed SHA identities are in [its record](../../logs/r1_round31/r1-63l-backend-patch.json).

Existing test fixtures generated additional UUID directories under `docs/tasks/R1-63j-rehearsal`, `docs/tasks/R1-63j-runtime`, `logs/r1_round24/rehearsal`, `logs/r1_round27`, `logs/r1_round29`, and CPU-test result roots. These are synthetic review/reproduction artifacts; they are separate from Claude's real chain-S results. The large assembler fixture trees contain repeated generated recipe bundles. Nothing is staged or committed; compact validation logs and new lane records identify the work for the lead's commit review.

## Remaining resource and gate work

R1-58l must include intermediate sampled phases and full-validation outer time, startup/identity/durable writes, measured host/device evidence and failed attempts. CounterFact needs the explicit measured sampled-drift per-position transfer basis; S1 and occupancy/class transfers need review or measurement. Previously outstanding near-miss/revision rows stay outstanding. Typed revision-4 dispatch must be explicit, rather than falling through the revision-3 validator.

The revised schedule must retain 1.5× solo ceilings, the single 1.15× two-worker adjustment, retry charging, the shared 750-process-hour ceiling and the **October 9** experimental stop. A package awaiting measurements, transfer review, validator implementation or scientific fidelity interpretation is not “signatures only.”
