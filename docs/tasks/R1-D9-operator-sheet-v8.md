# Operator sheet v8 — candidate v14, D.4, typed costs v4

The review package is `manifests/revision_v1/freeze_candidate_v14.json`, `docs/tasks/R1-D9-inputs-v9.json`, the `*-template-v9.json` forms, and `docs/tasks/R1-63m-runtime-v2/catalog.json`. These bind DEC-063 full validation, DEC-064 secondary cap-fidelity reporting, and DEC-066's **285 core + 45 optional cells**. All source forms and the cost receipt remain unsigned. Historical candidates and measured recipes remain audit records; no old signature authorizes the new requests.

## Review before signatures

Use `docs/R1_execution_plan_v3.md` and `logs/r1_round36/X19-review.json`. The final cost forecast is **431.307 process-hours** including extension, or **646.960 hours at the sum of per-cell ceilings**, against a shared 750-hour cap. The expected elapsed scenario is 227.303 hours at 1.65× throughput. These retain labelled transfers, historical component estimates and memory qualifications. The four donors provide direct whole-process/host evidence; missing endpoint measurements remain missing even when their costs have approved transfers. No budget, timestamp or data value in a synthetic rehearsal is a real admission.

The U03 dossier is `logs/r1_round36/U03-continuation-evidence.json`: both retained continuation checkpoints pass their original fidelity certification and match the current recipes/calibration. Their historical training budgets are **not** a demonstrated exact compute match to primary v5. Gate review must retain that distinction. MQuAKE's five omitted arms have no new observed outcomes; they are calibration-determined configurations prospectively not run.

## Ordered operator workflow

From the repository, start a fresh real operator session. These environment flags are for CPU metadata inspection; Claude's eventual model execution uses the JAX CUDA environment and the GPU lease.

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator protocol-admit \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --write-form docs/tasks/operator-v8/01-protocol-preview.json
```

An unsigned form with unset reviews produces a blocked preview (exit 2). Complete the review fields, preview again using `--form` and a **new** `--write-form` path, then sign that exact reviewed request with the lead's name/date and approval. Only the explicitly signed `--execute` invocation performs the action. Do not pre-sign downstream forms: prior receipts, seed choice and actual endpoint inventories change their request hashes.

1. **protocol-admit:** choose optional extension; review near-family semantics, zsRE empty baseline, queue ceilings/failure policy, multiple disjoint pairs per family, DEC-063 full validation and DEC-064 cap-fidelity policy. The new fields `full_validation_reviewed` and `cap_fidelity_policy_reviewed` must be true after review.
2. **cost-admit:** the operator reads ceilings v2 from the typed receipt's binding, validates all 27 evidence rows and recomputes transfers/projections. Review the complete cost basis, 750 process-hour budget, failure charging and memory qualifications. Signing produces a new receipt; leave the source v4 document unsigned.
3. **clearance:** review current exposure and the exact clearance request. This step recomputes exhaustive clearance on the bound unsealed evidence before any draw.
4. **rng-admit:** supply the lead's master seed; retain DEC-062 allocation semantics.
5. **draw:** sign the current request and exposure attestation; obtain the actual fixed reservations. Draw demand is unchanged by DEC-066.
6. **endpoints:** inspect actual missingness and construction identities; sign the exact request. Independent expected populations retain missing planned slots and the full-validation contract.
7. **seal:** review the actual endpoint inventory and sign its exact seal request.
8. **freeze:** bind genuine U01–U18 closure receipts and schedule admission, stage the whole production bundle, review it, and sign exact publication. Publication writes the canonical frozen manifest last and revalidates the real backend.
9. **launch:** review the actual final matrix/bindings, two workers, signed budget and host floor. Execution additionally requires Claude's live GPU lease and CUDA environment. Preserve the receipt root for accounting and retries.

After step 7, add the genuine schedule and gate-closure receipt bindings to a **new** assembly-input document derived from the operator's latest `*-inputs.json`. Inspect/stage using:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_63j_production_bundle \
  --inputs docs/tasks/ACTUAL-REVIEWED-ASSEMBLY-INPUTS.json \
  --templates docs/tasks/R1-63m-runtime-v2/catalog.json \
  --staging docs/tasks/R1-final-proposal-v14 \
  --report logs/R1/operator_v8/production-proposal.json
```

`ACTUAL-REVIEWED-ASSEMBLY-INPUTS.json` above is an explicit placeholder for the future signed-input package; it has not been manufactured. Feed the resulting publication bundle and the same gate/schedule receipts into the operator freeze form. Synthetic fixtures validate the interfaces but cannot substitute for these artifacts.

## Full commands for every lead step (added by the orchestrator, 2026-09-18)

Each lead step is the same three-command cycle as step 1. Replace nothing but the step name and the form paths.
Quote every text value in the forms (`"name": "charlie derr"`, `"date": "2026-09-18"`).

### Step 2 — `cost-admit`

```bash
# (a) preview, write the unsigned form
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator cost-admit \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --write-form docs/tasks/operator-v8/02-cost-preview.json
# (b) after setting the review fields to true, preview again with the reviewed form
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator cost-admit \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --form docs/tasks/operator-v8/02-cost-preview.json \
  --write-form docs/tasks/operator-v8/02-cost-reviewed.json
# (c) after setting lead_approved true with name and date in the reviewed form, execute
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator cost-admit \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --form docs/tasks/operator-v8/02-cost-reviewed.json \
  --execute
```

### Step 3 — `clearance`

```bash
# (a) preview, write the unsigned form
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator clearance \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --write-form docs/tasks/operator-v8/03-clearance-preview.json
# (b) after setting the review fields to true, preview again with the reviewed form
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator clearance \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --form docs/tasks/operator-v8/03-clearance-preview.json \
  --write-form docs/tasks/operator-v8/03-clearance-reviewed.json
# (c) after setting lead_approved true with name and date in the reviewed form, execute
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator clearance \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --form docs/tasks/operator-v8/03-clearance-reviewed.json \
  --execute
```

### Step 4 — `rng-admit`

```bash
# (a) preview, write the unsigned form
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator rng-admit \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --write-form docs/tasks/operator-v8/04-rng-preview.json
# (b) after setting the review fields to true, preview again with the reviewed form
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator rng-admit \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --form docs/tasks/operator-v8/04-rng-preview.json \
  --write-form docs/tasks/operator-v8/04-rng-reviewed.json
# (c) after setting lead_approved true with name and date in the reviewed form, execute
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator rng-admit \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --form docs/tasks/operator-v8/04-rng-reviewed.json \
  --execute
```

### Step 5 — `draw`

```bash
# (a) preview, write the unsigned form
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator draw \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --write-form docs/tasks/operator-v8/05-draw-preview.json
# (b) after setting the review fields to true, preview again with the reviewed form
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator draw \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --form docs/tasks/operator-v8/05-draw-preview.json \
  --write-form docs/tasks/operator-v8/05-draw-reviewed.json
# (c) after setting lead_approved true with name and date in the reviewed form, execute
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator draw \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --form docs/tasks/operator-v8/05-draw-reviewed.json \
  --execute
```

### Step 7 — `seal`

```bash
# (a) preview, write the unsigned form
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator seal \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --write-form docs/tasks/operator-v8/07-seal-preview.json
# (b) after setting the review fields to true, preview again with the reviewed form
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator seal \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --form docs/tasks/operator-v8/07-seal-preview.json \
  --write-form docs/tasks/operator-v8/07-seal-reviewed.json
# (c) after setting lead_approved true with name and date in the reviewed form, execute
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator seal \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --form docs/tasks/operator-v8/07-seal-reviewed.json \
  --execute
```

### Step 8 — `freeze`

```bash
# (a) preview, write the unsigned form
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator freeze \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --write-form docs/tasks/operator-v8/08-freeze-preview.json
# (b) after setting the review fields to true, preview again with the reviewed form
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator freeze \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --form docs/tasks/operator-v8/08-freeze-preview.json \
  --write-form docs/tasks/operator-v8/08-freeze-reviewed.json
# (c) after setting lead_approved true with name and date in the reviewed form, execute
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58g_operator freeze \
  --inputs docs/tasks/R1-D9-inputs-v9.json \
  --candidate manifests/revision_v1/freeze_candidate_v14.json \
  --session logs/R1/operator_v8 \
  --form docs/tasks/operator-v8/08-freeze-reviewed.json \
  --execute
```

Step 4 (`rng-admit`) additionally takes your master seed in its form (`master_seed`, an integer you choose and record).
Steps 6 (`endpoints`) and 9 (`launch`) are the orchestrator's; step 8 (`freeze`) is preceded by the orchestrator's
assembly-inputs run (R1-63n) after your step 7.

## Subsequent checkpoints

After the actual cost v4 receipt is signed, HT-4f may build the final v6 claim ledger with `scripts.ht4f_claim_ledger --cost-receipt PATH-TO-ACTUAL-SIGNED-RECEIPT`. It now checks v4 against inputs v9 and uses D.4/plan v3. The unsigned source is deliberately refused; no final ledger was emitted in this round.

At block 1 and later block boundaries, run the D11 report with actual frozen matrix, queue receipts and watch evidence. Reconcile measured process time and memory; replace available transfers through a new reviewed admission at a stopped boundary. Preserve DEC-052 missing/incomplete reporting, the 63-interval family, and the October 9 experimental stop. The operator stops on stale identities, unresolved signatures, missing scientific evidence or unknown spending instead of silently repairing or approving them.
