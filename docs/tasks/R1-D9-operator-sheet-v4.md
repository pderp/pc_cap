# R1-D9 operator sheet v4 — current preview and final handoff

Work from `/home/derp/cap/pc_cap`. Experiments stop **October 9**. This sheet supersedes v3's
stale teacher/patch instructions and v1 concurrency multiplier. No signature or launch is granted.

The current [candidate v9 preview](../../manifests/revision_v1/freeze_candidate_v9_preview.json)
binds 728 files and [unsigned inputs v4-preview](R1-D9-inputs-v4-preview.json). At publication,
three of eight corrected MQuAKE profiles were complete; matched_update, v0_live_C1/C2 and
S1_LM/literal plus execution plan v2 remain external dependencies. Cost admission remains unsigned.
Do not sign preview requests that will change when those dependencies arrive.

Once chain Q and `docs/R1_execution_plan_v2.md` exist, the CPU publisher:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.r1_63h_refresh
```

refuses missing dependencies, then creates **new** candidate v9, v4 inputs/forms and dry reports.
It never overwrites v3 or preview documents, signs a form or freezes the package. Review
`logs/r1_round26/r1-63h-v9-verification.json`: require all eight exact recipe-bound profiles,
no external dependency entries, verified hashes and all remaining scientific/operational gates
printed. Missing receipts still leave gates open. Presence of plan v2 is not cost approval.
If these outputs already exist, preserve them and create a separately reviewed version.

## Protocol, clearance and current request identities

The lead reviews [final protocol text](../R1_stage4_protocol_v5_2_D_final.md),
[matrix policy contracts](../R1_stage4_matrix_schema_DEC061.md),
[concurrency v2](../R1_stage4_queue_concurrency_v2.md) and the
[real-pool diagnostic](../../logs/r1_round26/near_final/r1-d9e-real-pool-review.json).
Usable capacities are 6084/6121/2161 against 4050/4050/1950; all93 Hall checks pass.
Teacher/role checks and installed R1-77d are complete. No repeated teacher GPU run or cadence
patch is needed. The zsRE empty baseline and potentially missing near slots require explicit review.

Every v4 prerequisite and authorization binds contract_version2, register, matrix, protocol,
layout/hash and the exact DEC-061 near-family contract. Protocol admission additionally signs
`near_family_reviewed`; its template also exposes the zsRE-baseline and queue-policy review fields.
Fill an actual named signer/date and keep the receipt hash-bound. No template sets approval true.

Current **inspection-only** preview request hashes are:

| Stage | Digest |
|---|---|
| clearance | `72cfc8d7adeefca4810dfeb36b32fd96795b672cca82eab552fdd6c802fa08af` |
| draw | `b7f61c00ff2fcaea9f3f67fd23940f61cacfdc14d6c0124aea02b7dfa15592b1` |
| seal | `6f3222954f0ff9cf9260ce017751198ce4b295e36d61c2b26cc63cf4a96dddfb` |

They are **not signatures**. Final v4 generation, the master seed, every newly bound prerequisite
and any code change alter downstream requests. Obtain each digest from its current dry report.

## Exact execution order

1. **Clearance.** Start with final `docs/tasks/R1-D9-inputs-v4.json`. Run
   `../venv/bin/python -m scripts.r1_d9_clearance --inputs docs/tasks/R1-D9-inputs-v4.json --dry-run`
   under the CPU environment above. Require capacities6084/6121/2161, valid source/history bindings,
   no `bound_inputs_or_outputs` or `exhaustive_clearance_review` errors, zero draws/seals.
   The unsigned report correctly has `ready_for_owner_execution=false` for owner receipts only.
   After the lead attests current exposure and signs the exact clearance request, rehash/rebind
   the authorization. Require `blocked=[]`, ready=true, then run the same module with `--execute`.
   Bind the emitted joint-clearance receipt; preserve its independent resources.
2. **Protocol/RNG and draw.** Sign final protocol/extension choice and RNG admission. Enter the
   lead's chosen master seed once in the RNG form and `d9.draw.master_seed`. Attest current
   exposure through draw time. Run `scripts.r1_d9_draw --inputs ... --dry-run`, sign its **new**
   request, rehash/rebind, require ready=true/blocked=[], then `--execute`. Bind the actual draw
   receipt. No seed retry or role/family coordination to improve endpoint availability.
3. **Endpoints.** Fill actual draw binding and extension choice in
   `docs/tasks/R1-D10c-construction-inputs-template-v4.json`. Run
   `scripts.r1_d10c_endpoints construct --spec <filled-construction-inputs.json> --dry-run`.
   Require deterministic source-based pairing, fixed near100/revision50 inventories, explicit
   missing rows, globally disjoint roles and locality collision checks. A dry run prints zero
   draws/seals/model calls and validated payload identities. Review missingness, then `--write`
   creates new unsealed resources. Sign endpoint_construction with exact draw/reservations,
   bundle and independent-population hashes. Bind those resources in `d9.seal` and the receipt.
4. **Seal.** Run `scripts.r1_d9_seal --inputs ... --dry-run`, obtain/sign the current seal request,
   rehash/rebind, require ready=true/blocked=[], then `--execute`. Bind the actual seal receipt.
   Endpoint/source/missing-inventory tampering must fail. A successful seal grants no launch authority.
5. **Freeze.** Bind signed measured ceilings and September20 schedule admission, all U01–U18
   closure receipts, final independent populations, final protocol JSON, source/backend/environment
   identities and confirmatory recipes. The final executable protocol remains schema2 with exact
   DEC-060 layout, max_new32, DEC-053 scoring and October9 stop. Obtain the lead's final freeze
   authorization and use the owner freeze procedure. Candidate v9 is a dry inventory, not the frozen
   manifest. Do not improvise an executable freeze by turning candidate flags true.
6. **Queue.** With final matrix/recipe bindings and signed process-hour budget, inspect:

   ```bash
   JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.r1_77_queue status \
     --matrix manifests/revision_v1/run_matrix_final.json --workers 2 --dry-run \
     --receipt-root logs/R1/final_queue
   ```

   Require complete declared inventory, effective multiplier1.15, positive admitted solo ceilings,
   no unknown costs/invalid receipts and headroom against the **process-hour** budget. This status
   command inventories results; it does not replace the run-time recipe/freeze checks. The owner
   launches CUDA under an externally held live GPU lease using `scripts.r1_77_queue run --execute`,
   final `--matrix`, `--bindings`, `--workers 2`, the admitted `--ceiling-hours` and that same receipt
   root. Use CUDA for real execution; the CPU environment above is for metadata inspection only.
   Preserve the receipt root across resumes so failed-cell counts and all spent costs persist.

Ordinary failure retries once; the second leaves an incomplete cell and advances while the other
worker runs. Host/memory/lease failure stops dispatch. Unknown costs/torn state require owner
reconciliation. Report DEC-052 complete blocks and exact incomplete cells/checkpoints daily and
at block boundaries, including an early stop. No substituted populations or erased failure costs.

## Claim ledger after cost admission

The [v6 preview](../talk_claim_ledger_v6_preview.md) binds three corrected MQuAKE results and leaves
five pending. After final v4 forms and the signed full-endpoint cost receipt exist, run:

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.ht4f_claim_ledger \
  --cost-receipt <signed-current-chain-i-cell-ceilings-receipt.json>
```

The final publisher refuses absent profiles, plan v2 or an unapproved/mismatched receipt. Review the
new `talk_evidence_v6.json` and ledger before using their claims. Prior κ/tail/stress evidence and
its preliminary framing remain in v5; these CPU lanes produce no new confirmatory outcomes.
