# R1-D9d — versioned per-dataset demand

- Status: implementation and unsigned v3 operator artifacts complete; no actual clearance/draw/seal.
- Agent: Codex, Round24.
- Changed: shared D9 core/producers, metadata preflight and endpoint constructor; added pure `r1_d9_layouts.py`.
  Public clearance/draw/seal wrappers dispatch the shared implementation and need no separate edits.
- Contract: v3 inputs and version-2 receipts bind exact roles, realizations, cadence, layout hash, matrix/protocol.
  Demand is4050/4050/1950; legacy uniform v5.1 remains supported. Counterfactual A/B/C layouts refuse.
  Synthetic size overrides remain limited to pure APIs/tests.
- Preserved: global entity/fact and role disjointness, Hall subset feasibility, source content, RNG namespaces,
  deterministic substreams, paired orders, planned composition dependencies, missingness and whole-draw refusals.
  Tests establish unchanged zsRE/CounterFact allocation and substreams when only MQ demand changes.
- Outputs: `docs/tasks/R1-D9-inputs-v3.json`, six unsigned authorization/prerequisite forms, construction inputs v3;
  three `logs/r1_round24/r1-d9-*-dry-v3.json` reports. Generator: `scripts/r1_58e_operator_inputs.py`.
- Validation: both-layout regression plus malformed demand/cadence/boolean/realization, stale receipt,
  endpoint count and missing-denominator rejection; included in153 passing regression tests.
- Done-when: real input bindings/layout pass dry preparation; each stage refuses unsigned prerequisites;
  the full synthetic production-API path produces and verifies all stage receipts.
- Cost: CPU only. Pending: completed teacher/role evidence, near semantics, current exposure and lead signatures.
