# R1-D1h — exclusion register v5

Status: implementation and 38-test round-13 focused suite passed; no draw/seal. Owner mirrors the board.

Artifacts: [register](../../manifests/revision_v1/exclusions_frozen_v5.json),
[producer](../../scripts/r1_d1h_register_v5.py), [tests](../../tests/revision_v1/test_r1_round13.py),
[protocol v4](../R1_stage4_protocol_draft_v4.md).

DEC-048 removes only three explicitly recorded MQ true-query reasons. Primary training/development and every
independent protected reason remain. Historical exposure evidence is retained. The v3 near-candidate inventory
coincides with locality neighbors and is primary-reserved; unverified/counterfactual near-miss reasons stay excluded.
Forty-three SHA bindings cover the cumulative parent, eligibility/prepared sources, v3/v3b lineage, split X9 audit
and the producer. The other two datasets remain identical to the parent candidate/removal inventories.

Counts: zsRE 52,411 items/subjects; CF 12,246 items/subjects; MQ 4,489 items / 4,218 subjects.
Demand is 4,050 subjects per dataset. MQ headroom 168; the 169th loss aborts. No finite smaller pending-clearance
loss bound is established: all candidates could fail. No guaranteed cleared subjects are claimed.

Checkpoint sequence:
1. Verify source bindings and DEC-048, rebuild to a **new** output path using module invocation.
2. Validate ordered primary slices and historical reservation preservation; no historical primary release.
3. Obtain independently justified alias/context/teacher/role clearance.
4. Call `require_usable_capacity(register, cleared_subjects)` **before RNG/draw output**; then check joint role feasibility.
5. Owner versions the final matrix/recipe/reference. Register freeze is not final launch admission.

Invocation: `python -m scripts.r1_d1h_register_v5 --output <new-repo-path>` under CPU venv environment.
The script refuses overwrite. No existing register, board, code, notes or decision file was edited.
