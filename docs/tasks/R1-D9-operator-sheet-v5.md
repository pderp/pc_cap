# Stage 4 operator sheet v5 — stepwise requests and receipts

Round 27, 2026-09-17. **Do not sign the current package yet.** X16 identified
missing normative bindings, a DEC-062/protocol conflict, incomplete typed cost
evidence and a missing final recipe/publication bundle. See `X16-edit-requests.md`.
The operator is implemented and tested; this sheet does not certify those inputs.

## Inputs and responsibilities

Use `scripts/r1_58g_operator.py`. It defaults to unsigned candidate v11 and
`docs/tasks/R1-D9-inputs-v6.json`; these bind DEC-062's `family_coordinated` choice.
Candidate verification is not scientific approval. After the X16 repairs, the
owner must provide the successor candidate and inputs explicitly on every command.
Do not sign the historical v4/v5 previews or reuse their request digests.

The lead runs protocol, cost, clearance, RNG, draw, seal and freeze steps.
The orchestrator runs endpoints and launch using the lead-approved exact request.
Every step is dry by default. CPU metadata work uses the existing JAX venv; final
model execution uses CUDA/JAX with a live externally held GPU lease. No PyTorch is
introduced and no other repository is modified.

## One command, nine steps

Run from `/home/derp/cap/pc_cap`. Set these shell variables to the **reviewed
successor** package once X16 is repaired. The current paths below are for dry
inspection only:

```bash
operator_inputs=docs/tasks/R1-D9-inputs-v6.json
operator_candidate=manifests/revision_v1/freeze_candidate_v11.json
operator_session=logs/R1/operator_v5
```

Use one stable, unique session directory. Its basename also identifies immutable
output files under `docs/tasks/R1-58g-<basename>/`; do not reuse a basename for a
different sitting. Begin with the dry protocol request:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  ../venv/bin/python -m scripts.r1_58g_operator protocol-admit \
  --inputs "$operator_inputs" --candidate "$operator_candidate" \
  --session "$operator_session" \
  --write-form docs/tasks/operator-protocol-form.json
```

Exit 2 means blocked; inspect both `blocked` and `dry_run`. Fill the requested
`fields` in the form while leaving `lead_approved` false. Run the same dry command
with `--form docs/tasks/operator-protocol-form.json` and **without** `--write-form`.
Every changed field changes the request digest. After the request and its source
bindings are reviewed and blockers resolved, copy the current printed digest into
the form and set the lead's name, date and `lead_approved: true`. Only then run:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  ../venv/bin/python -m scripts.r1_58g_operator protocol-admit \
  --inputs "$operator_inputs" --candidate "$operator_candidate" \
  --session "$operator_session" \
  --form docs/tasks/operator-protocol-form.json --execute
```

Repeat that dry → fill fields → re-dry → exact approval → execute procedure with
each next step and a separate form filename. The tool reads the last completed
step's new input binding from the journal automatically. There is no command to
sign everything at once, and no downstream step can bypass the required prefix.
A signature here is a named local attestation, not cryptographic identity proof.

| Order | Step | Lead-supplied fields / checkpoint |
|---:|---|---|
| 1 | `protocol-admit` | Explicit extension yes/no; near-family, empty-zsRE-baseline and queue-policy reviews; bound allocation mode and decision; review of the exact multiple-pairs-per-family contract. Requires repaired normative protocol and bindings. |
| 2 | `cost-admit` | All 27 condition/dataset rows with peak host/device MiB and hash-bound measurement JSON; explicit positive shared **process-hour** budget; full-endpoint/validation cost basis reviewed. Wall ceilings are copied from the bound table. |
| 3 | `clearance` | Exposure-current attestation; inspect the actual D9 clearance dry-run and certified teacher/role/Hall evidence; sign its exact wrapped request. |
| 4 | `rng-admit` | Lead's master seed, supplied once; same allocation mode as signed protocol; closed allocation-contract binding from step 1. |
| 5 | `draw` | Exposure-current attestation; inspect deterministic D9 dry output and matching mode/seed/role/source identities. No seed retry to improve matching. |
| 6 | `endpoints` | Missingness review; orchestrator inspects constructor dry identities, then executes the approved request. CPU construction, no model call. |
| 7 | `seal` | Endpoint-inventory review; actual draw, resources, independent expected populations and endpoint identities must validate. |
| 8 | `freeze` | Owner-prepared publication-bundle binding, September 20 admission and closed U01–U18 receipt map. Publish only after preflight and all final recipe checks. |
| 9 | `launch` | Frozen matrix and recipe-bindings references, persistent queue receipt root, `workers: 2`; orchestrator already holds the GPU lease. Uses the signed shared process-hour ceiling from step 2. |

For final launch, use the CUDA-enabled venv configuration the owner has verified;
**omit `JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=` from the command**. The parent
environment propagates to workers. The operator does not acquire the lease or
make an allocation of GPU time on its own.

## Cost evidence and publication bundle

The unsigned cost receipt v1 is bound as a source. Its signature flag alone does
not make it the typed receipt accepted by freeze or HT-4f. Step 2 creates a new
typed receipt only from the reviewed, exactly approved request, carrying register,
matrix, protocol, layout, family, 27 measurements and shared budget. Missing
measurements and the full-validation cost basis are not supplied by the script.
Do not copy elapsed-wall estimates into the process-hour field.

The `freeze` step validates and publishes a **supplied** bundle. It does not build
360/405 executable recipes or manufacture gate closures. The bundle is a
hash-bound repository JSON object with:

```json
{
  "artifacts": [
    {"source": {"path": "/absolute/reviewed/source.json", "sha256": "..."},
     "destination": "/home/derp/cap/pc_cap/manifests/revision_v1/new-file.json"}
  ],
  "matrix": {"path": "/absolute/final/matrix.json", "sha256": "..."},
  "bindings": {"path": "/absolute/final/recipe-bindings.json", "sha256": "..."}
}
```

Every source must already exist, have the reviewed bytes and bind its final
destination dependencies. Destinations must be new paths under repository
`docs/tasks` or `manifests/revision_v1`. Include the complete final matrix,
protocol, recipes and bindings, and exactly the required
`manifests/revision_v1/frozen_stage4.json`. Resources remain under assets. The
freeze must bind this session's actual protocol/cost/seal/gate receipts and sealed
populations; coordinates must match all admitted core and optional extension
cells. Publication copies bytes exactly and writes the freeze last, then checks
the real queue/backend. Preparing this bundle is still owner work.

## Receipt log and recovery

`<session>/receipts.jsonl` is appended and fsynced, with a chained content hash.
It records dry runs, completed steps and failures. An exclusive session lock
prevents two invocations sharing that session. New per-step input/receipt files
are written exclusively; existing files are never replaced.

**A failed step signs nothing downstream.** It can leave its own authorization,
an endpoint request or partial resources before failure; inspect the journal and
reconcile these artifacts before retrying. Do not delete costs, mutate completed
receipts, change seeds or automatically reset the journal. A torn log or unknown
cost is a stop condition. The operator detects such conditions; it is not an
automatic crash-recovery service.

If freeze publication raises a caught error, only files exclusively created by
that publication attempt are removed; pre-existing files survive. An abrupt
machine crash may leave partial publication and requires owner reconciliation.
If launch stops with an incomplete queue, preserve its receipt root and use the
existing queue recovery rules; the operator does not pretend the launch completed
or overwrite its result. Retry-once, host-failure stopping and process accounting
remain the production queue's responsibility.

## Evidence from this round

`logs/r1_round27/r1-58g-DEC062-package-verification.json` verifies the 772-bound
unsigned v11 package. `r1-58g-protocol-DEC062-dry.json` shows the real first-step
preview refusing missing lead fields. Its digest is a preview, not a signature.
Tests cover exact signatures, sequencing, unsigned refusal, recorded decision
review, journal corruption, typed-cost rejection and publication rollback. A
separate synthetic D9 rehearsal exercises draw/endpoints/seal. No production
signature, reservation, freeze, GPU job or launch was performed.
