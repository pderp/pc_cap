# R1-77d — prepared cadence patch for the orchestrator's idle boundary

Status: prepared and tested; **not applied**. Round24 explicitly assigns application after chains M/N/O.
User permission to edit existing files does not remove this active-run coordination boundary.

The [exact patch](R1-77d-cadence.patch) changes only
`src/pccap/revision_v1/stage4_cell.py` and `scripts/r1_77b_sealed_backend.py`.
[Patch identities](../../logs/r1_round24/r1-77d-patch.json) record original and proposed file SHAs.
It replaces the uniform real-payload cadence guard with a bound per-dataset contract and retains
the existing payload, integrity, content-seal, code, frozen-recipe and final-admission checks.

Legacy schema-1 protocol/recipes retain uniform 100/300/1000 support. A version-2 population recipe
must bind a schema-2 final protocol: DEC-060 option D, exact roles/demands/realizations/layout hash,
matrix, lead approval, no open gates, explicit extension choice, max_new32, DEC-053 scoring and
October9 deadline. The four-coordinate cell must occur exactly once in the admitted matrix,
with checkpoints 100/300 for MQuAKE or 100/300/1000 for zsRE/CounterFact. Arbitrary shortened
cadences, counterfactual options, unapproved protocols and altered hashes are refused.

Tests delivered alongside the patch:
`tests/revision_v1/test_r1_77d_cadence_patch.py`, `r1_77d_patch_support.py`, and
`test_r1_58e_rehearsal.py`. They compile the proposed function bodies in memory; installed files
are never changed by these tests. The two full rehearsals pass with genuine 300/1000 edit counts.
The wider regression is 153 passing tests, including legacy sealed admission/integrity/queue paths.
`git apply --check docs/tasks/R1-77d-cadence.patch` succeeds on the recorded originals.

At the idle boundary:

1. Confirm no active job uses either file; verify their hashes against the patch record.
2. Apply with `git apply docs/tasks/R1-77d-cadence.patch`. Keep the new tests and supporting files.
3. Run the cadence and sealed backend tests with CPU JAX. The test helper recognizes the installed
   helper, verifies both files against the recorded proposed hashes, then tests them directly.
   Before application it compiles the proposed bodies in memory. It never applies the patch.
4. Recompute installed tree, driver and backend identities; rebuild final recipes/protocol,
   bindings and freeze candidate v8. D9 request digests include installed dependencies and must
   be refreshed/reapproved where affected. Historical freezes/receipts must remain historical.

No source/backend patch, actual draw/seal, GPU run, freeze, staging or commit occurred in this lane.
