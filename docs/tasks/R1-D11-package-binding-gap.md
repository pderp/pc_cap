# R1-D11 — launch integration findings for the owner

2026-09-18, Codex; found while writing the exact launch runbook. The assembler is
reserved for Claude's post-chain-S patch, so its installed source was not edited.

`scripts/r1_63j_production_bundle.py` currently emits final queue bindings with
`recipes`, `matrix`, `freeze`, `cost_admission`; the `matrix` binding contains the
path and byte hash. `scripts/r1_77f_scheduler.py:108` requires a separate
`bindings['matrix_sha256']` before any dispatch. `virtual_validate()` invokes
`queue.verify_sealed_matrix()`, which does not check this scheduler-only field.
The pending HT-8 successor-package patch does not add it either.

Owner repair before rebuilding candidate/runtime templates: add
`matrix_sha256=mb['sha256']` alongside `matrix=mb` in the assembler's final
queue-bindings dictionary. Proposed one-line patch:
`docs/tasks/R1-D11-package-binding.patch`. It is independent of the HT-8 patch;
both must land before hashes are regenerated. No published file should be
hand-edited. The runbook's launch wrapper explicitly checks this guard before
taking the lease. A full scheduler-entry rehearsal is still needed on the
successor bundle; the old virtual backend check alone cannot establish launch
readiness.

A second integration item belongs with R1-58l/R1-63m: `cost-admit` in
`scripts/r1_58g_operator.py` reads `cell_ceilings_v1.json` directly. Revision-4
costs/ceilings v2 must flow from the exact typed receipt's bound ceiling document,
with matching rows and explicit validation, rather than retaining this v1 path.
No cost values, source bindings or approval flags were changed in this lane.
