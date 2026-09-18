# Operator sheet v9 — D.5, candidate v15, inputs v11

Use `manifests/revision_v1/freeze_candidate_v15.json`, `docs/tasks/R1-D9-inputs-v11.json`, forms `*-template-v10.json`, runtime catalog `docs/tasks/R1-63o-runtime-v3/catalog.json`, cost artifact v5 (typed receipt revision 4), and execution plan v4. Old sessions and signatures remain historical. **Start a fresh session `logs/R1/operator_v10` at step 1**, using the same lead seed **378462438976234321867** at step 4. Never resume v9 with new input flags: the operator continues from its last successful state.

Protocol D.5 incorporates DEC-068 triplet-first ordering, DEC-069 preliminary decision summaries with assumption-labelled secondary pointwise 95% t intervals (2 d.f.), and the lead's September 18 deterministic locality exclusion/selection approval. Unperformed factorial and predictive-coding branches are deferred. Populations, 285 core + 45 optional cells, registered 63 primary intervals, original classifier, costs, failure charging and October 9 stop are unchanged. The 50 locality slots stay fixed, including any unavailable rows after exclusions. No treatment outcomes were used to select prompts.

## Review and source lock

Review `docs/tasks/R1-63o.md` and `logs/r1_63o/final/package-verification.json`. Verify the content lock after the lead's commit and again before publication/launch:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m scripts.r1_63o_live_audit \
  --verify-lock logs/r1_63o/final/live-content-lock.json
```

The lock lists every installed Python implementation under `scripts/` and `src/pccap/`, plus current input bindings. Any changed or additional implementation requires a new package and orchestrator review. This source-content lock is **not** the scientific freeze or permission to execute. Historical artifacts retain their historical producer identities; the unrestricted historical scan and explicit immutable-input boundaries are disclosed separately. Do not relabel historical measured recipes, signatures or register ancestry as current executions.

The unchanged combined forecast is 431.307 expected process-hours, 646.960 at the sum of per-cell ceilings, within the 750-hour shared cap; 227.303 elapsed hours assumes 1.65× throughput. S1 historical continuation uses 771,581 forward-input tokens and does not establish exact-v5-compute matching. Keep sampled-memory and transferred-cost qualifications.

## Fresh session

All metadata commands use the CPU environment below. Actual GPU execution after launch admission requires Claude's JAX CUDA environment and GPU lease.

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m scripts.r1_58g_operator protocol-admit \
  --inputs docs/tasks/R1-D9-inputs-v11.json \
  --candidate manifests/revision_v1/freeze_candidate_v15.json \
  --session logs/R1/operator_v10 \
  --write-form docs/tasks/operator-v10/01-protocol-preview.json
```

For each step, preview; fill the required review fields; preview again to a new form path; approve/sign that **exact** request under the lead's delegated authority (DEC-067); then invoke the same step with `--form <reviewed-form>` and `--execute`. Do not pre-sign downstream requests. Initial unset-review previews deliberately return exit 2. The operator now propagates all nested blockers except the current step's exactly identified unsigned authorization.

| Step | Command | Required review/action |
|---|---|---|
| 1 | `protocol-admit` | D.5, optional extension choice, near-family/multiple-disjoint-pair policy, zsRE empty baseline, queue/failure policy, full validation, DEC-064 and DEC-069 qualifications, approved locality selection. |
| 2 | `cost-admit` | All 27 cost rows, unchanged 750 process-hour cap, transfers, failure charges and memory limitations. Source cost v5 remains unsigned; the operator emits its signed derivative. |
| 3 | `clearance` | Current exposure attestation and exact exhaustive clearance using evidence v7 and role plan v2. |
| 4 | `rng-admit` | Enter integer master seed `378462438976234321867`; retain family-coordinated allocation. |
| 5 | `draw` | Exact current request and exposure attestation; inspect actual reservations and all planned pairs. |
| 6 | `endpoints` | Actual identities, nine locality-selection audits, all independent denominators and actual missingness. Preview is deterministic; only authorized execution writes resources. |
| 7 | `seal` | Actual endpoint inventory and exact seal request. |
| 8 | `freeze` | Genuine gate/schedule evidence, complete staged bundle, exact publication; writes canonical frozen manifest last. |
| 9 | `launch` | Actual final matrix/bindings, two workers, host guard, budget, GPU lease and JAX CUDA environment. |

After the seven successful steps, derive assembly inputs from those exact signed requests. The verifier supports candidate v15 and cost artifact v5 while retaining typed revision-4 numerical checks:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m scripts.r1_63n_assembly_inputs \
  --inputs docs/tasks/R1-D9-inputs-v11.json \
  --candidate manifests/revision_v1/freeze_candidate_v15.json \
  --session logs/R1/operator_v10 \
  --output docs/tasks/R1-63o-actual-assembly
```

Use the emitted assembly-input path (printed by that command) with the bundle producer; this path does not exist before genuine step 7. Its gate wrappers inherit the checked approvals and do not manufacture a new lead signature.

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m scripts.r1_63j_production_bundle \
  --inputs docs/tasks/R1-63o-actual-assembly/assembly-inputs.json \
  --templates docs/tasks/R1-63o-runtime-v3/catalog.json \
  --staging docs/tasks/R1-final-proposal-v15 \
  --report logs/R1/operator_v10/production-proposal.json
```

Review the staged bundle with the same gate/schedule receipts in step 8. X20 independently verifies after genuine step 8. The lane's synthetic assemblies and dry construction using historical reservations do not authorize D.5 draw, seal, publication or launch.
