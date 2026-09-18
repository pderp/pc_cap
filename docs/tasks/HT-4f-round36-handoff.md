# HT-4f — round-36 readiness

The final v6 claim ledger remains **blocked on an actual signed typed cost receipt v4**, as ongoing.md requires. The source `R1-cost-admission-receipt-v4.json` has `lead_approved: false`; using it in `ht4f_claim_ledger.build` raises “open or unapproved receipt” before ledger files are written. This rejection is recorded in `logs/r1_round36/unsigned-rehearsal-final.json`.

The future consumer was repaired to require `receipt_revision == 4`, validate against inputs v9, bind execution plan v3 and protocol/matrix D.4, and report 285 core +45 optional cells. Historical corrected MQuAKE development observations remain development evidence even for arms omitted prospectively from confirmation. Final claims must preserve that distinction, the unchanged 63-interval family, and the absence of MQuAKE checkpoint-1,000 observations.

Once the lead signs cost admission through the operator, use the **new signed receipt's path**, not the unsigned source:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.ht4f_claim_ledger \
  --cost-receipt PATH-TO-ACTUAL-SIGNED-V4-RECEIPT
```

The final ledger was not generated, and no approval or signature was fabricated. No additional engineering permission request is waiting.
