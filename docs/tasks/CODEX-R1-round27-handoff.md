# Codex round 27 handoff

2026-09-17. Latest task list: `docs/ongoing.md`, priority R1-D9f → R1-58g → X16 → HT-4f.
Read the X16 report before planning the signing sitting: **the current package is
not ready for signature or launch**. All work remains unstaged and uncommitted.

| Lane | Delivered | Remaining dependency |
|---|---|---|
| R1-D9f | Coordinated allocator, public draw/seal hooks, RNG/selection receipts, sparse/heterogeneous-pool tests and real-pool diagnostic for both modes. DEC-062 B is selected in unsigned RNG/operator inputs. | Clarify whether repeated-family pairs are allowed; amend the conflicting protocol text; exact lead admission and authorized population execution. |
| R1-58g | Nine-step Python operator, exact request/signature checks, receipt journal, rollback, unsigned candidate v11/forms v6 and operator sheet v5. | X16 repairs, measured typed cost evidence, closed gates and owner-prepared final recipe/publication bundle. No one-sitting readiness claim is made. |
| X16 | Full independent report, DEC-033–061 trace, DEC-062 addendum, reproduced arithmetic/profile scores, repair requests and exact notes patch. | Owner applies reviewed repairs and refreshes the signature package. |
| HT-4f | Cost gate checked; eight corrected profile results prepared in X16; round-27 waiting record. | Valid signed typed cost receipt and current protocol/input bindings. Final ledger was not published. |

## Start here

- Review: `logs/r1_round27/X16-review.md`.
- Exact proposed repairs: `docs/tasks/X16-edit-requests.md` and
  `docs/tasks/X16-notes-correction.patch` (checked with `git apply --check`, not applied).
- Operator: `docs/tasks/R1-D9-operator-sheet-v5.md` and `scripts/r1_58g_operator.py`.
- Allocation contract/results: `docs/tasks/R1-D9f.md` and
  `logs/r1_round27/r1-d9f-real-pool.json`.
- Current candidate proof: `logs/r1_round27/r1-58g-DEC062-package-verification.json`.
- Ledger gate: `docs/tasks/HT-4f-round27.md`; historical `HT-4f.md` is preserved.

## Findings that affect the next signing sitting

1. The final protocol incorporates normative v5.1 definitions without binding
   that file in the candidate. Bind the normative dependency closure.
2. The final protocol still explicitly forbids the coordinated allocation now
   selected by DEC-062. Publish and bind a versioned amendment.
3. DEC-062 is accepted B. The initial audit/diagnostic incorrectly marked it
   pending; the explicit addendum corrects that status. What is still unresolved
   is whether the 100 planned cases can include multiple pairs per family. The
   implementation and its 900/900 diagnostic result use that interpretation; the
   lead has been asked for clarification. No actual draw depends on an assumption.
4. Cost receipt v1 is unsigned **and structurally insufficient** for the typed
   validator. Measured memory ceilings, full-endpoint/validation evidence and an
   explicit shared process-hour budget are still needed. A signature flag alone
   does not close this gate.
5. A final recipe/publication bundle and genuine closure evidence for the open
   gates are required. The CLI verifies and publishes a supplied bundle; it does
   not generate the missing production recipes or fabricate gate receipts.
6. Six corrected v0/S1 profiles have unavailable unseen firing telemetry, not
   zero false fires. Correct the notes and carry that distinction into HT-4f.

The cost table reproduces **209.4 solo core hours + 12.15 optional extension
hours**, approximately 126.91 core elapsed hours at the assumed 1.65 throughput.
These are projections. They do not supply a signed process-hour budget or measured
whole-matrix throughput. The experimental stop remains October 9.

## Current package and diagnostic result

Candidate v11 / inputs and forms v6 bind 772 files, have 17 open gate identifiers
and remain unsigned/non-executable. DEC-062 B is selected in the operative inputs
and, as explicitly requested by the lane, in the unsigned v4 RNG template. Old v4
bytes and changed producer bytes are archived. v9/v10 are historical after these
authorized changes; do not reuse their request digests. The package remains a
review draft until X16 is repaired and a successor version is bound.

One predeclared diagnostic seed, 20260917, yielded near matches:

| Dataset | Independent r0/r1/r2 | Coordinated r0/r1/r2 |
|---|---|---|
| zsRE | 21/16/18 | 100/100/100 |
| CounterFact | 63/72/68 | 100/100/100 |
| MQuAKE | 77/79/79 | 100/100/100 |

Every planned denominator is 100. Non-near selections are identical. The result
is one diagnostic allocation, not a final draw, probability estimate or model
performance claim. Exact selected-ID/RNG diagnostic resources live outside the
repo under `assets/runs/pc_cap/R1/r1_d9f/round27/`.

## Validation and boundaries

**80 CPU tests passed in 38.64 s**, covering allocation, D9 receipts, layouts,
endpoint validation, the synthetic public clearance/draw/endpoints/seal chain,
operator safeguards and current candidate/form bindings. Log:
`logs/r1_round27/final-validation-tests.txt`.

The operator tests initially exposed a fixture-location issue: production
metadata reads correctly reject `/tmp`. They now create synthetic metadata under
repo logs, preserve the actual production read boundary and pass with ordinary
pytest defaults (7/7, `operator-portable-tests.txt`). An old independent-mode
fixture was updated from stale v4 inputs to the preserved v5 independent inputs.
No production validation was weakened. Initial failed runs are retained for
transparency; the final suite and subsequent fixture-only check pass.

Ruff passes all changed Python files, `git diff --check` passes, and the proposed
notes patch passes an applicability check. No broad GPU/model tests were run.
The existing rehearsal fixture produces synthetic artifacts under
`logs/r1_round24/rehearsal/<uuid>/` and corresponding assets resources; these new
directories are test evidence, not final Stage 4 admissions.

CPU checks used the existing JAX venv with `JAX_PLATFORMS=cpu` and empty
`CUDA_VISIBLE_DEVICES`. No `src/pccap` changes, sibling-repository edits, actual
population operations, GPU execution, production signatures, staging or commits
were performed. Reviewed owner protocol, notes, cost and plan documents were left
unchanged; proposed X16 repairs are separate files.

## Suggested division of next work

The protocol/package owner can repair normative bindings and the DEC-062 text
while the cost owner identifies complete measurements and the explicit process
budget. The production-recipe owner can prepare the publication builder and gate
inventory; final identities wait for the actual seal and admissions. Notes can be
corrected independently using the supplied patch after checking for concurrent
edits. HT-4f resumes after typed cost admission and must bind the successor inputs.
Agree those interfaces before rebuilding final packages to avoid competing edits.
