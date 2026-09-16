# HT-3d — registered κ pilot aggregation

- Status: implementation and partial-data aggregation complete; automatic final-chain refresh pending.
- Agent: Codex, round18.
- Inputs: kappa_pilot_v3.json; counter-review §4; arm/seed/dataset retention, unseen and 32×127 per-position drift records.
- Outputs: scripts/ht3d_pilot_aggregate.py; scripts/ht3d_bound_aliases.py; scripts/ht3d_after_chain.py; three corresponding test modules; HT-3d-ordinary-seed2-unseen-aliases.json; HT-3d-after-chain-watch.spec.json; logs/r1_round18/ht3d-pilot-partial-v{1,2-verified-aliases}.{json,md}.
- Verify command: PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.ht3d_bound_aliases --output-prefix logs/r1_round18/ht3d-next-snapshot
- Verify output: snapshot v2 has27/36 complete rows, with all ordinary/coupled rows present; clipped controls were still running. See the report for complete metrics and registered verdicts.
- Done-when: fractional ES95/max positive harm; equal dataset/seed means; strict seed-range separation; retention floor; per-dataset unseen nonincrease; missing/nonfinite/charged failures retained; full framing in JSON and Markdown; immutable refresh after owner chain.
- Cost: GPU0; standard-library aggregation, no model execution.
- Deviations: two expected ordinary-seed2 unseen paths are absent, but equivalent measurements exist under v5_rare1_n100. The explicit alias supplement verifies the exact averaged weight SHA, occupancy, tag and all edited/outside IDs before reading measured values. It does not fill missing values or change owner files. Strict-path snapshot v1 remains historical; use v2.
- Population qualification: legacy tail files omit explicit token hashes. Comparison uses manifest-bound deterministic producer ordering and exact ordered cap-off matrix identity. Future sealed receipts should bind token IDs directly. MQuAKE retention-v3b and legacy standalone unseen/drift are distinct within-endpoint populations.
- Unresolved: finish all clipped-control seeds; await owner chain terminal full-profile receipt. The host CPU watcher checks once/minute and writes a new report pair at logs/r1_round18/ht3d-after-chain-host.{json,md}, plus .watch-status.json. Six-hour timeout emits a labeled partial snapshot; a charged training failure triggers a failure-preserving snapshot. It never launches or changes owner experiments.
- Questions for lead: none for current CPU work.

The initial detached sandbox watcher did not persist; its launch receipt is historical, not a running-process claim. The replacement host session is recorded separately in logs/r1_round18/ht3d-after-chain-host-session.json.

Mandatory DEC-054 framing:

**What it is not.** It is not the coupled free energy of Nelson et al. (no coupled expectation, no changed
inference distribution), not a coupled Markov blanket, and not a test of the one-κ conjecture that porosity and
interference are the same parameter. It is the first controlled measurement of what a loss-level coupling does on
this substrate, which is the honest thing to bring to a session chaired by the people who defined κ.

Validation: 60 focused CPU tests passed (6.49 s); ruff passes all new scripts/tests. Logs: logs/r1_round18/lanes-tests-v2.txt. No real-base calls, GPU time, source-tree changes, results/R1 writes, staging or commits.
