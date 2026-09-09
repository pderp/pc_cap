# Codex Lane B handoff — 2026-09-09

Implementation complete for the three independent CPU tasks in ongoing.md Lane B. All changes are in task worktrees under pc_cap; no GPU, dataset access, external resource changes, main-branch source edits, merges or pushes were performed by this lane. Both reference repositories and the JAX/FabricPC venv were left unchanged. Only Codex-owned task rows in the shared task manifest were updated.

| Task | Branch / tip | Evidence | Result |
| --- | --- | --- | --- |
| S0-07 metrics | `task/S0-07`, `a39be6b` (code `d9f9f5e`) | [record](../../.worktrees/S0-07/docs/tasks/S0-07.md), [verification](../../.worktrees/S0-07/results/S0/metrics/verify.txt) | 33 known-answer tests; lint passed |
| ANA-01 analysis | `task/ANA-01`, `bc04bc5` | [record](../../.worktrees/ANA-01/docs/tasks/ANA-01.md), [verification](../../.worktrees/ANA-01/results/ANA-01/verify.txt) | 19 tests; lint passed; synthetic report artifact included |
| S0-07b HVP controls | `task/S0-07b`, `65ffe84` | [record](../../.worktrees/S0-07b/docs/tasks/S0-07b.md), [verification](../../.worktrees/S0-07b/results/S0/hvp/verify.txt) | 6 new controls plus 33 metric tests; all pass; lint passed |

58 distinct tests in total. `JAX_PLATFORMS=cpu PYTHONPATH=src` was set for verification using `/home/derp/cap/venv/bin/python`. Reports contain task timing and zero accelerator seconds. These are implementation controls, not S1/S4/S7 experimental evidence.

## Integration

Claude retains review and merge ownership. Review S0-07 and ANA-01 against their task records, then merge S0-07 before S0-07b (the latter branches from the metrics implementation). ANA-01 is independent and based on the committed scaffold/harness predecessor. All branches edit only their assigned metric/analysis code, tests and task evidence. The S0-07 follow-up records exact task timestamps; it does not change tested code. Run the shared integration suite after merges, per the orchestrator protocol. Do not dispatch replacement agents over these paths while their task branches await integration.

## Review points

1. The S0-07 task asks for rank zero with undefined status, while `contracts.metric` replaces undefined values with null. The implementation reports undefined/null with `strata.effective_rank=0`, zero operands and `reason=zero_matrix`, preserving the PDF's zero-rank fact. Confirm this schema interpretation before S1 reporting; no shared contract was edited.
2. ANA-01 enforces both primary comparisons and all D.11 inequalities. Its deterministic negative/qualified/inconclusive policy is recorded for review before freeze. Missing comparisons are incomplete, never imputed. Pass `expected_items` from the frozen inventory to catch items absent in all arms; without it, coverage is expressly observed-union-only.
3. The HVP module provides exact small-matrix oracles only. It does not supply a JAX HVP over cap values, run a sweep, or establish any behavioral order-effect finding. Its 4x4 example has total commutator mass 20, of which 16 is in cross-bank blocks.

No user input is needed for this handoff. The other ongoing.md lanes remain available to their owners; this lane has not claimed DATA, MEMORY, BASELINES or REG work.
