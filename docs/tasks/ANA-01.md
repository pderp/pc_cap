# ANA-01 Paired confirmatory analysis and realization-cluster bootstrap
status: done
agent: codex   started: 2026-09-09T18:51:50.751497+00:00   finished: 2026-09-09T18:57:33.272233+00:00
commit: task/ANA-01 (this implementation commit, resolved via git log)
inputs used: ENV-03 contracts, ongoing.md Lane B; updated_plan2.md S4-01/S4-06; PDF D.11; entirely synthetic tables.
outputs: src/pccap/analysis/{paired,bootstrap,__init__}.py; tests/analysis/test_paired.py; results/ANA-01/{verify.txt,constant_shift_control.json}
verify command: JAX_PLATFORMS=cpu PYTHONPATH=src /home/derp/cap/venv/bin/python -m pytest -q tests/analysis/ --basetemp=results/ANA-01/pytest-tmp; ruff check of owned analysis paths and tests
verify output: results/ANA-01/verify.txt — 19 passed; lint passed.
done-when check:
- PASS: per-item ID pairing, item means per order, five-order means per realization, and complete paired tables.
- PASS: 10,000 draws of three realization clusters; all five orders travel together; default 97.5% two-sided percentile intervals with linear quantiles and explicit seed.
- PASS: both required contrasts and all practical-gain/acquisition/locality checks; positive, negative, qualified, inconclusive and incomplete outcomes.
- PASS: missing pair/order/null metric yields incomplete with no imputation or partial-cell bootstrap; duplicate/nonfinite/mixed-stream inputs raise.
- PASS: frozen inventory additionally detects items missing from every arm; no inventory is explicitly observed-union-only coverage.
- PASS: per-item RET-GS losses/gains retained even for equal aggregate accuracy; no claim to identify individual paraphrases from their mean.
- PASS: deterministic output under shuffled input row order; strict JSON; CLI returns exit 2 for incomplete comparisons.
cost: gpu_seconds=0 wall_seconds=342.521 peak_mem_mib=0 (CPU-only convention). Wall is elapsed task time, not scientific compute.
deviations: added optional frozen inventory validation and separate stream IDs to close shared-omission/mixed-dataset failure modes. No shared contract changes. The function accepts explicitly configured bootstrap seed/draw/confidence values; confirmation must pass the frozen settings (defaults are D.11). Classification policy is documented below for pre-freeze review.
unresolved: orchestrator review required before integration/freeze. No actual experiments or confirmation data were used.
questions for lead: none

## API and policy for integrator review

`analyze_paired(rows, expected_items={realization: item_ids}, stream_id=...)` accepts one frozen dataset/scope, realizations 0/1/2 and orders 0…4 by default; identifiers can be explicitly configured. `python -m pccap.analysis.paired INPUT.jsonl --output REPORT.json --inventory INVENTORY.json --stream-id NAME` is independent of the orchestrator CLI. Inventory JSON is a list of `{"realization": 0, "item_ids": [...]}` records. Supply inventory for confirmation; the minimal ongoing.md input table cannot reveal items absent from every arm.

D.11 thresholds are unchanged: RET-GS point gain≥.02 with lower interval>0; ES lower>−.02; LS lower>−.01. Both C2−C1 and C2−CR must pass. Every constraint is reported. Positive satisfies all; negative has RET-GS upper<.02 or a noninferiority upper below its allowed negative margin; qualified has demonstrated practical positive RET-GS and acceptable ES/LS points with unresolved noninferiority; remaining uncertain cases are inconclusive. Empty/missing pairs take incomplete precedence. Zero effect is negative for the primary practical claim, not a correctness failure. This deterministic classification policy should be frozen after review.

Compute comparability is always marked unassessed here; Appendix B resource evidence must come from the harness. Three independent realizations remain the uncertainty unit; neither orders nor item rows become independent model replicates.
