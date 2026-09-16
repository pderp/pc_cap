# R1-40c — successor matrix v5 (round 17)

- Status: complete draft artifact and validator; execution/freeze/cost admission intentionally open.
- Agent: Codex.
- Inputs: matrix v4, primary v5, selection v2, register v6, R1-64/R1-64b recipes, R1-73 calibration spec, freeze candidate v4 and DEC-051/052.
- Outputs: scripts/r1_40c_matrix_v5.py; manifests/revision_v1/run_matrix_v5.json; tests/revision_v1/test_r1_40c_v5.py; logs/r1_round17/R1-40c-freeze-audit.json.
- Verify command: PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m pytest tests/revision_v1/test_r1_40c_v5.py -q -p no:cacheprovider
- Verify output: 3 tests passed; full revision suite 582 passed, 8 skipped, 11 subtests passed.
- Done-when: 360 core +45 extension; exact axes/unique coordinate IDs; six block sizes45/45/90/90/90/45; null ceilings; named construction families; explicit queue/retry/resume/refusal and freeze audit.
- Cost: GPU0; metadata/hash reads only, no model or sealed payload.
- Deviations: docs/tasks/R1-40c.md already describes an older round, so this new record avoids overwriting it.
- Unresolved: final populations/executable recipes, U12/U14, MQuAKE calibration, continuation transfer, September20 ceilings, final freeze and extension interpretation.
- Questions for lead: current R1-64b extension uses historical v2 weights; retain the package-comparison label unless an explicitly versioned same-v5-weight gate-only extension is chosen.

Coordinate IDs depend only on condition/dataset/realization/order. expected_definition_sha256 separately binds scientific definitions/templates. Recipe, population and result bindings remain null until independently prepared; the matrix contains no final subject IDs. Template recipes are development constructors, not launchable final cells. MQuAKE v0-style cells name the R1-73-calibrated family with a required null calibration receipt.

The queue uses immutable attempts, unique contiguous checkpoint receipts, snapshot/state restoration and full identity checks. It retains failed spend, refuses torn incremental journals/unknown costs and stops on identity mismatch. No automatic retry budget is authorized. Optional HT-7h between B3/B4 adds no cells here. September20 remeasurement and October9 stop are explicit; incomplete cells remain individually reported.

The strict audit rehashed the predecessor candidate's bound files: no missing files or conflicting selected-primary/selection/register authority; the repaired R1-68c driver is a stale binding. The candidate still binds matrix/protocol v4 and open gates. ready_for_freeze is false. It must be versioned to this matrix, protocol v5, final approved source and all admission receipts. A matching subset of hashes never closes U17.
