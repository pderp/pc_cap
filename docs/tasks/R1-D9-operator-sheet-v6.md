# Operator sheet v6 — D.1 / typed cost v2 / candidate v12

2026-09-17. **The current package is not ready to sign or launch.** Read the X17
report and complete the evidence/bundle work listed below. This sheet supersedes
v5's package paths and cost-source instructions; v5 retains the detailed step and
recovery descriptions.

## Current entry point

From `/home/derp/cap/pc_cap`:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  ../venv/bin/python -m scripts.r1_58g_operator protocol-admit \
  --inputs docs/tasks/R1-D9-inputs-v7.json \
  --candidate manifests/revision_v1/freeze_candidate_v12.json \
  --session logs/R1/operator_v6 \
  --write-form docs/tasks/operator-v6-protocol-form.json
```

This is a dry inspection. The script also defaults to v7/v12, but explicit paths
make the chosen package clear. The new session name avoids colliding with earlier
dry/historical sessions. After evidence repair, substitute the successor package.

Each step follows dry → fill fields → re-dry with `--form` → review exact current
digest → lead signs → `--execute`. A changed field or prerequisite changes the
digest. Do not copy an old preview signature. The lead's earlier clarification
already resolves multiple disjoint pairs per family; v7 records it as reviewed.
The complete protocol/admission request still needs its exact sitting signature.

| Order | Step | Required checkpoint |
|---:|---|---|
| 1 | `protocol-admit` | D.1 and all six normative bindings; explicit extension choice, empty-zsRE baseline and queue/family reviews. |
| 2 | `cost-admit` | Typed v2/successor, complete measured evidence and reviewed transfers, explicit 750 process-hour proposal accepted, exact signature. Current pending receipt refuses admission even if its flag is flipped. |
| 3 | `clearance` | Current exposure including the four newly declared recipes; certified source, teacher and Hall evidence. |
| 4 | `rng-admit` | Lead's one master seed; bound DEC-062 mode and exact allocation-contract receipt. |
| 5 | `draw` | Exact current request and exposure attestation; no seed retry. |
| 6 | `endpoints` | Orchestrator constructs from the actual draw; inspect identities and missing slots. |
| 7 | `seal` | Actual complete endpoint and independent-population inventory; exact authorization. |
| 8 | `freeze` | Owner-built final publication bundle, schedule and all gate receipts; real backend validation. |
| 9 | `launch` | Orchestrator holds the GPU lease, uses the admitted matrix/recipe bindings and persistent queue receipt root. |

The operator passes the signed cost receipt's `host_mem_available_floor_mib` to
the queue: v2 proposes **6144 MiB for every launch**, including the first worker.
750 process-hours is the shared proposal; approximately 255 is the expected
combined core+extension process projection. Neither is an elapsed-time substitute.
The 6 GiB floor is not a measured process-memory ceiling.

For GPU execution **omit `JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=`** and use the
owner's verified CUDA/JAX environment. The CPU flags above are for inspection.
The operator does not obtain the lease. Endpoints construction is CPU work.

## Work before signing

Execute `R1-64f/ordered-runlist.md`, collect process host RSS and whole-process
timings, supply full-validation cost evidence, and resolve any representative
cost transfers explicitly. Refresh the typed receipt, candidate, forms and request
digests afterward. The current cost producer reports absent measurements; its
host/full-validation placeholders need a measured-input extension before closure.

The missing whole final-recipe/freeze assembler and required publication inventory
are documented in `R1-63i-production-bundle-interface.md`. The operator can verify
and publish a supplied bundle; it cannot invent 360/405 executable final recipes
or closed gates. Synthetic development artifacts cannot fill that gap.

## Recovery and evidence

Use one session and its append-only, fsynced, hash-chained receipt journal.
Failure never signs downstream steps. A failed step can leave its own partial
authorization/resources; reconcile them without changing seeds or discarding
costs. Freeze publication removes only newly created files on caught failure;
crash recovery still needs owner reconciliation. Queue retries once, preserves
incomplete cells and stops on host-level failures, using the same receipt root.

Current dry evidence: `logs/r1_round28/operator-protocol-current-dry.json`.
Current package proof: `logs/r1_round28/r1-63i-verification.json`.
`R1-58h-protocol-current-unsigned.json` is a preview, not a signed form.
Earlier round-28 dry digests predate the host-floor forwarding update and are
historical. No production signature, draw, seal, freeze or launch occurred here.
