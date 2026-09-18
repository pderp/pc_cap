# Operator sheet v7 — assembler and cost revision 3

This supersedes v6's package paths. **The package remains unsigned and has
substantive evidence gaps.** The ordered admission workflow and recovery rules
in v6 still apply; no prior digest or signature authorizes the new inputs.

The current defaults are candidate v13 and inputs/forms v8. For an explicit dry
protocol inspection, from pc_cap:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  ../venv/bin/python -m scripts.r1_58g_operator protocol-admit \
  --inputs docs/tasks/R1-D9-inputs-v8.json \
  --candidate manifests/revision_v1/freeze_candidate_v13.json \
  --session logs/R1/operator_v7 \
  --write-form docs/tasks/operator-v7-protocol-form.json
```

Receipt v3 uses the existing typed schema v2 with `receipt_revision: 3`; it adds
host provenance and the bound full-validation inventory. Missing full-validation
evidence still fails if an approval flag or top-level status is changed. Matched
monitor RSS is explicitly sampled and temporally attributed. Extrapolated peaks
are proposals, never entered as measured values. The first v3 draft may precede
chain R completion; inspect the exact recorded completion inventory before use.

After remaining chain R results and direct `.time` files exist, rebuild host
evidence and costs into new paths, then version the package and requests again:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  ../venv/bin/python -m scripts.r1_58i_host_peaks \
  --output docs/tasks/R1-host-peaks-after-chain-R.json \
  --evidence-dir logs/r1_round29/host-after-chain-R

PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  ../venv/bin/python -m scripts.r1_58j_cost_receipt \
  --host-evidence docs/tasks/R1-host-peaks-after-chain-R.json \
  --output docs/tasks/R1-cost-after-chain-R.json \
  --evidence-dir logs/r1_round29/cost-after-chain-R
```

These producers preserve missing measurements. They do not implement approval of
cross-condition cost transfers or invent the full-validation run. See
`R1-58j-full-validation-required.md`. Candidate v13/forms v8 are an immutable
review snapshot; do not overwrite their inputs after reviewing a digest.

The final production assembler now exists. Follow
`R1-63j-production-interface.md`: obtain actual signed prerequisite receipts and
the sealed population, supply the reviewed runtime catalog, and stage the whole
360/405-cell bundle in new metadata paths. The assembler validates a virtual
final namespace and does not publish it. Feed its `publication-bundle.json` to
the existing operator freeze form. The lead's exact freeze signature is the
last act before byte-exact publication and real backend revalidation. The
canonical freeze file is written last by that separate operator transaction.

GPU execution remains Claude's responsibility with JAX CUDA and the lease. The
CPU flags above are for inspection and metadata preparation. The signed host
floor is 6 GiB; the proposed shared budget remains 750 process-hours, with the
October 9 experimental stop and explicit incomplete-cell reporting unchanged.
