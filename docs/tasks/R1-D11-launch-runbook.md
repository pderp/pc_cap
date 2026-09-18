# R1-D11 — launch-day runbook

2026-09-18, Codex. **Preparation only; production launch is not yet ready.**
The instructions below use the proposed candidate v14 / inputs v9 paths. Those
successors must actually exist, pass X19, and bind the installed D.3 backend,
watch and typed cost v4 before the first request. Do not substitute historical
v13/v8 merely to get past a missing file. No command here was used to draw,
seal, freeze, sign or launch production during this lane.

## Sequence and remaining integration work

The lead's approval to enter the freeze workflow begins a sequence of separate,
exact requests. Final **freeze publication happens after draw, endpoint
construction and sealing**. Endpoints are constructed by the authorized owner
from the admitted draw, before the final sealed cell payloads are published;
development/reporting scripts never open those payloads.

1. Complete cost v4's four-donor audit, explicit transfers, ceilings v2, typed
   validator and all remaining evidence gaps. Obtain actual admission; a general
   permission to work does not fill in any scientific signature.
2. Apply the owner-held backend and HT-8 package patches after chain S; rebuild
   runtime templates and candidate/forms. All prior signatures/digests are
   historical after a source or field change.
3. Resolve the **additional queue-binding defect found in this lane**:
   `r1_63j_production_bundle.assemble()` emits a `matrix` path/hash binding but
   omits `matrix_sha256`, which `r1_77f_scheduler.run_workers()` requires before
   dispatch. The existing virtual bundle check does not exercise this scheduler
   guard. Proposed owner patch and evidence: `R1-D11-package-binding-gap.md`.
   Apply it before generating/signing a bundle; do not patch published bindings.
4. The operator's `cost-admit` currently reads **cell_ceilings_v1.json directly**.
   R1-58l/R1-63m must update and test this integration to use the exact receipt-bound
   v2 ceilings. Installing a standalone v4 validator is insufficient.
5. Close actual exposure, allocation, schedule and U01–U18 prerequisites, run the
   full synthetic operator/assembler/scheduler rehearsal on the final identities,
   then review/sign each actual request below. The October 9 completion deadline
   and 750 **process-hour** ceiling remain unchanged.

The two additional integration findings are software/evidence work, not missing
signatures. This document is not a claim that only signatures remain.

## CPU preparation and per-step approval

Run from `/home/derp/cap/pc_cap`. Select a new session name once and keep it for
this sitting. These shell functions only define commands; they do not execute a
step until called. Use the project venv; CPU flags are confined to metadata work.

```bash
cd /home/derp/cap/pc_cap
export R1_SESSION=logs/R1/operator_v8
export R1_INPUTS=docs/tasks/R1-D9-inputs-v9.json
export R1_CANDIDATE=manifests/revision_v1/freeze_candidate_v14.json
export R1_FORMS=docs/tasks/R1-D11-sitting-v8
export R1_RECEIPTS=logs/R1/final_queue
export R1_MATRIX=manifests/revision_v1/run_matrix_final.json
export R1_BINDINGS=docs/tasks/R1-final-queue-bindings.json
mkdir "$R1_FORMS"

cpu_python() {
  env PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
    OPENBLAS_NUM_THREADS=1 ../venv/bin/python "$@"
}
operator_preview() {
  cpu_python -m scripts.r1_58g_operator "$1" \
    --inputs "$R1_INPUTS" --candidate "$R1_CANDIDATE" \
    --session "$R1_SESSION" --write-form "$R1_FORMS/$1-draft.json"
}
operator_review() {
  cpu_python -m scripts.r1_58g_operator "$1" \
    --inputs "$R1_INPUTS" --candidate "$R1_CANDIDATE" \
    --session "$R1_SESSION" --form "$R1_FORMS/$1-fields.json" \
    --write-form "$R1_FORMS/$1-reviewed.json"
}
operator_apply_cpu() {
  cpu_python -m scripts.r1_58g_operator "$1" \
    --inputs "$R1_INPUTS" --candidate "$R1_CANDIDATE" \
    --session "$R1_SESSION" --form "$R1_FORMS/$1-signed.json" --execute
}
```

For **each step**, call preview; review its `blocked` and `dry_run` outputs.
Make a new `STEP-fields.json` from the draft with the actual reviewed fields,
leaving `lead_approved: false` and the signature empty. Call review, then have
the lead sign a separate `STEP-signed.json` copied from the newly emitted
`STEP-reviewed.json`. The signature is the lead's actual name/date plus
`lead_approved: true`, approving that exact `request_sha256`. Do not change
fields after signing. Each `--write-form` is create-only: a further field change
needs another new filename and re-review. Stop on an error or unexpected blocker.

Execute these steps **one at a time with the review/signing pause between calls**:

| Step | Exact calls, in order | Fields/evidence the lead reviews |
|---|---|---|
| 1 | `operator_preview protocol-admit`, `operator_review protocol-admit`, `operator_apply_cpu protocol-admit` | D.3, extension choice, family allocation including multiple disjoint pairs, empty zsRE baseline, failure/ceiling policy |
| 2 | Same three calls with `cost-admit` | Typed receipt v4 and receipt-bound ceilings v2, reviewed transfers, complete evidence, 750 process-hours |
| 3 | Same with `clearance` | Current cumulative exposure, certified population/teacher/Hall evidence |
| 4 | Same with `rng-admit` | Lead's one nonnegative integer master seed and exact allocation receipt; no seed search |
| 5 | Same with `draw` | Actual admitted draw request and current exposure |
| 6 | Same with `endpoints` | Missingness and dry endpoint identities; owner constructs from the actual draw |
| 7 | Same with `seal` | Full endpoint inventory, reservations and independent population |

The operator enforces the successful step prefix in
`$R1_SESSION/receipts.jsonl`. It uses the previous successful `NN-inputs.json`
automatically; do not restart a new session to jump past a failed step.

At step 6 the operator itself invokes the following producer, first with
`--dry-run`, then after exact approval with `--write`:

```bash
cpu_python -m scripts.r1_d10c_endpoints construct \
  --spec docs/tasks/R1-58g-operator_v8/endpoints-request.json --dry-run
```

That optional repeat inspection is only valid **after** step 5 and the endpoint
preview created the request. Use `operator_apply_cpu endpoints` for the actual
write, so identities and the endpoint receipt are recorded together. Resources
go under `assets/runs/pc_cap/R1/operator-operator_v8/endpoints`; the report goes
to `$R1_SESSION/endpoints-written.json`. Do not rerun a completed draw/write to
resolve a downstream problem.

## Stage, review and publish the final bundle

After seal, the current input file is
`docs/tasks/R1-58g-operator_v8/07-inputs.json`. Have the owner prepare
`08-package-inputs.json` as a new copy that substitutes the **actual signed**
`receipts.september20_admission` and `receipts.closed_gate_receipts` bindings.
These are needed by the assembler as well as the subsequent freeze form.
Preserve every other bound input. These receipts must pass the existing
preflight against this exact register, matrix, protocol and seal.

Use the runtime catalog bound by v14; resolve it from the candidate's input file
instead of choosing an arbitrary earlier catalog:

```bash
cpu_python - <<'PY'
import json
import os
from pathlib import Path
from scripts import r1_d9_receipts as d9
spec = d9.read_metadata(d9.ref(Path(os.environ['R1_INPUTS'])))
catalog = spec['runtime_templates']
d9.read_metadata(catalog)
print(json.dumps(catalog, indent=2))
PY
```

Set `R1_TEMPLATES` to that exact printed path, and inspect/stage new metadata:

```bash
cpu_python -m scripts.r1_63j_production_bundle \
  --inputs docs/tasks/R1-58g-operator_v8/08-package-inputs.json \
  --report "$R1_SESSION/package-inspection.json"

cpu_python -m scripts.r1_63j_production_bundle \
  --inputs docs/tasks/R1-58g-operator_v8/08-package-inputs.json \
  --templates "$R1_TEMPLATES" \
  --staging docs/tasks/R1-D11-production-staging-v8 \
  --report "$R1_SESSION/package-staged.json"

operator_preview freeze
```

Fill `freeze-fields.json` with the staged `publication-bundle.json` path/SHA256,
the same actual schedule receipt and all-gates receipt. Use `d9.ref(path)` to
compute file bindings, never a content hash in place of a byte hash. Run
`operator_review freeze`; the lead inspects the full concrete bundle and signs
the newly emitted request; then:

```bash
operator_apply_cpu freeze
operator_preview launch
```

The freeze transaction writes approved new metadata byte-for-byte and publishes
`manifests/revision_v1/frozen_stage4.json` last. Confirm this is the exact bundle
reviewed, with D.3 and the HT-8 policy/implementations bound. Complete the launch
fields with `d9.ref(R1_MATRIX)`, `d9.ref(R1_BINDINGS)`, the **absolute** persistent
receipt root `/home/derp/cap/pc_cap/logs/R1/final_queue`, and `workers: 2`.
Run `operator_review launch`; obtain the exact named signature in
`launch-signed.json`. A numeric cap fidelity breach is recorded under DEC-064,
not converted into a new admission veto. Integrity failures still block.

## Launch with CUDA and the external GPU lease

The CPU shell function must **not** wrap launch. This command removes inherited
CPU-only/device-hiding variables and requires JAX's CUDA platform. It holds one
external lease for the two-worker queue's entire lifetime. Run it in the owner's
persistent terminal; do not also launch a second queue or profile. The operator
uses the signed cost receipt's host floor (currently 6144 MiB) for both workers.

```bash
env -u CUDA_VISIBLE_DEVICES PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cuda \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python - <<'PY'
import json
import os
from pathlib import Path
from scripts import r1_58g_operator as op
from scripts import r1_77_queue as queue
from pccap.harness.lease import gpu_lease

matrix_path = Path(os.environ['R1_MATRIX']).resolve()
bindings = queue.read(Path(os.environ['R1_BINDINGS']))
if bindings.get('matrix_sha256') != queue.sha(matrix_path):
    raise ValueError('Assembler/scheduler matrix hash mismatch; do not launch')
matrix = queue.read(matrix_path)
queue.verify_sealed_matrix(matrix, bindings)
form = json.loads((Path(os.environ['R1_FORMS']) / 'launch-signed.json').read_text())
with gpu_lease('R1-final-queue', stage='Stage4', exclusive=False):
    result = op.run(
        'launch', inputs=Path(os.environ['R1_INPUTS']),
        candidate=Path(os.environ['R1_CANDIDATE']),
        session=Path(os.environ['R1_SESSION']), form=form, execute=True,
    )
print(json.dumps(result, indent=2))
PY
```

Scheduler dispatch is ordered by block/within-block slot, two workers maximum,
with no next-block dispatch until the current block drains. It writes unique
`start.json`, `finish.json`, `decision.json` and `process.log` under the same
`R1_RECEIPTS`. A start without a finish leaves unknown spend for reconciliation.
It retries ordinary cell failures once; a second failure leaves the cell
incomplete. Host, lease, memory or watch-write failures stop dispatch. The watch
audits each completed cell; breaches do not by themselves stop the queue.
The runtime cutoff is October 10 00:00 America/New_York, ending October 9 work.

## Daily status and block-boundary handoff

Both commands below are CPU/read-only with respect to the queue, results and
watch. They write only their requested new report directory. They need no lease.
Use a new `R1_REPORT` value for each run; replace the illustrative date/time.

```bash
export R1_REPORT=logs/R1/operator_reports/20260920-090000
cpu_python -m scripts.r1_d11_block_report \
  --matrix "$R1_MATRIX" --receipt-root "$R1_RECEIPTS" --workers 2 \
  --output-dir "$R1_REPORT"
```

This first snapshot reports the global watch from its beginning, including
development baselines explicitly labelled **outside this matrix**. After the
orchestrator actually posts `lead-queue.txt`, use its `report.json` as the cursor:

```bash
export R1_PREVIOUS=logs/R1/operator_reports/20260920-090000/report.json
export R1_REPORT=logs/R1/operator_reports/20260920-block1
cpu_python -m scripts.r1_d11_block_report \
  --matrix "$R1_MATRIX" --receipt-root "$R1_RECEIPTS" --workers 2 \
  --previous "$R1_PREVIOUS" --boundary-block 1 --output-dir "$R1_REPORT"
```

For later daily reports use the same command without `--boundary-block`. Always
point `--previous` to the **last actually posted** report, not a merely generated
preview. The report does not append to `docs/lead_queue.md`, send messages or mark
alerts delivered. The orchestrator posts the text, then advances its cursor.
Unexpected watch truncation/prefix rewrites, wrong matrix/root or changing inputs
fail visibly. A writer active during a read can cause a retryable snapshot error.
No running worker is stopped or locked by the report.

The report uses the **entire matrix** for spent/projected process-hours even at
an early block boundary. Overlapping worker envelopes are summed; failed starts
count; covered inner driver times and JAX call timers are not added again.
Incomplete cells after exhausted retries stay listed; the queue's projection
does not reserve another forbidden retry for them. Unknown/live costs make the
known spend a lower bound and remove the projection. Legacy driver-only costs
are labelled as excluding process startup. Boundary mode returns exit 2 when
the boundary has unprocessed cells or accounting/integrity/watch gaps; it still
writes the diagnostic report. Artifact completeness alone is not scientific
success or a claim that a condition passes the fidelity benchmark.

The current operator launch runs the whole admitted matrix; it does not pause
at each block. If next-block workers are already active, take a daily snapshot
and label unknown spend, then obtain a coherent boundary report at a quiescent
point. A future deliberate block-at-a-time launch requires an explicit operator
interface change/review; this runbook does not bypass the signed launch contract
with an ad-hoc `stop_after` value. **Creep alerts must be relayed immediately**
from stderr/watch alerts, rather than waiting for a clean block-boundary report.

For raw inventory inspection the equivalent command is:

```bash
cpu_python -m scripts.r1_77_queue status \
  --matrix "$R1_MATRIX" --bindings "$R1_BINDINGS" \
  --receipt-root "$R1_RECEIPTS" --workers 2 --ceiling-hours 750
```

After a host stop or partial operator publication, preserve the session, seed,
all attempts and the receipt root. Reconcile costs/identities first; preview the
same step again and obtain any newly required exact approval. Do not erase
receipts, change roots to reset retry history, silently repair a signed file,
or mistake an exit-0 process for a certified completed cell.
