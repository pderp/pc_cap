# R1-D9 operator sheet v2 — not yet ready to sign

Work from `/home/derp/cap/pc_cap`, using `../venv/bin/python -m`. Experiments stop October9.
Current inputs: [R1-D9-inputs-v2.json](R1-D9-inputs-v2.json). The three recorded dry runs correctly refuse:
clearance has incomplete joint review; draw/seal have missing or unsigned prerequisites. No approval was created.

**Resolve before GPU or signatures.** D10a v4 conservatively retains 6,075 zsRE / 6,075 CounterFact / **2,129 MQuAKE
subjects**, before teacher filtering, versus 4,050 required per dataset. Even ignoring every near-miss reservation
as an optimistic diagnostic leaves only3,450 MQuAKE subjects. Reconcile protocol v5.1's verified-near-miss wording
with the frozen register's three exact query waivers; review incidental/homonym context matches with source evidence.
Do not drop context checks, change the sample size, or substitute subjects to make a draw fit. New exposure after
commit `2a8b237` requires a supplement before draw. Also explicitly review the proposed zsRE same-template,
different-subject near-miss family and all endpoint shortfalls; this differs from the historical development family.

1. **Review the evidence.** See [R1-D10a.md](R1-D10a.md), [R1-D10c.md](R1-D10c.md) and the
   [capacity diagnostic](../../logs/r1_round22/r1-d10a-capacity-diagnostics-v2.json). Version the evidence and role plan
   if any policy/context disposition changes. Inputs currently bind partial evidence deliberately; they cannot clear.
2. **Teacher pass, orchestrator after chain M.** The exact current dry command is below. Add `--execute` only for
   the owner GPU run, with CUDA enabled and no competing job. The default stops before GPU if capacity is short.
   An explicitly requested exploratory run can use `--allow-under-capacity-exploration`; it cannot authorize a draw.
   Resume with the identical command/output directory; changed inputs/code/chunk settings require a new version.

   ```bash
   JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.r1_d10b_teacher_review \
     --evidence /home/derp/cap/assets/runs/pc_cap/R1/r1_d10a/round22_v4/evidence.json \
     --evidence-sha256 733f4a269379b961c78e3583178e5688106d0d1b16f080f998058c2dee3ea2de \
     --output /home/derp/cap/assets/runs/pc_cap/R1/r1_d10b/round22_v1 \
     --log-dir logs/r1_round22/teacher
   ```

   For owner execution replace the environment prefix with `JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0` and append
   `--execute`. One lease covers the run; the default MemAvailable floor is8GiB. Current workload14,331 rows,
   ≤458,592 generated tokens: historical-throughput extrapolation385s, planning allowance770–1,924s plus any
   unmodelled startup/shape overhead. This is an estimate, not a fresh GPU measurement.
3. **Merge completed teacher and role evidence.** Run `scripts.r1_d10c_endpoints merge-review` with `--teacher`,
   `--teacher-sha256`, `--role-plan`, `--role-plan-sha256`, and a new assets `--output`. The current role plan is
   `assets/runs/pc_cap/R1/r1_d10c/round22_v2/role_plan.json` (relative to `/home/derp/cap`), SHA
   `bb83f0eee6466512b4774e324e3eacccc1521cb12b661cc70c3c0730873d5732`. Replace
   `d9.clearance.evidence` with the merged file binding. This merge grants no approval or capacity exception.
4. **Clearance signature.** Run `../venv/bin/python -m scripts.r1_d9_clearance --inputs docs/tasks/R1-D9-inputs-v2.json --dry-run`.
   Require all three usable counts≥4,050, role-subset feasibility, complete actual review, and no blocker except the
   unsigned authorization. The lead fills the clearance authorization template's **current** `request_sha256`,
   changes `status` to`closed` and `lead_approved` to`true`; bind its resulting file SHA. Rerun dry, require
   `ready_for_owner_execution:true`, then repeat with `--execute`. Bind the emitted `joint_clearance` receipt.
5. **Protocol/RNG and draw signature.** Complete the separate protocol/RNG templates, including the extension
   decision and one explicit master seed. Set the identical seed in `d9.draw.master_seed`. Bind the signed prerequisite
   receipts. Run `scripts.r1_d9_draw` with the same `--inputs ... --dry-run`; the lead signs its **new** request digest
   and attests current exposure in the draw template. Rehash/rebind that template, require a ready dry run, then
   `--execute`. Never retry seeds on a shortfall. Bind the actual draw receipt.
6. **Construct and review endpoints.** Fill the actual draw receipt binding and extension choice in
   [R1-D10c-construction-inputs-template-v1.json](R1-D10c-construction-inputs-template-v1.json).
   Run `../venv/bin/python -m scripts.r1_d10c_endpoints construct --spec docs/tasks/R1-D10c-construction-inputs-template-v1.json --dry-run`.
   Inspect missing rows and fixed denominators; after satisfactory review use `--write` to publish unsealed resources.
   Complete/sign the endpoint-construction template with the exact draw, reservations, bundle and independent-population
   bindings and reviewed role/dependency flags. Bind it and the two resources in the D9 inputs.
7. **Seal signature.** Run `scripts.r1_d9_seal --inputs ... --dry-run`; the lead signs the seal template against the
   current request digest after inspecting the endpoint inventory. Rehash/rebind, require ready, then `--execute`.
8. **Separate freeze/launch acts.** Cost/protocol/gate admission, updated freeze candidate, final frozen manifest,
   final recipes and queue admission are still the orchestrator/lead's work. A D9 seal alone does not launch a run.

Each signature covers its stage's exact producer/configuration/prerequisite hashes. `inspection_only_request_sha256`
in a draft is informational: use the fresh dry-run digest after the prerequisites change. Never copy a prior stage's
digest or treat an unsigned template, capacity sensitivity, synthetic test or development result as admission.
