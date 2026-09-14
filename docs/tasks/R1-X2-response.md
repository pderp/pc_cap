# Response to the R1-X2 re-audit — orchestrator, 2026-09-14 05:05 EDT (repairs in commit 5a46d2e, R1-26)

| id | disposition | change |
| --- | --- | --- |
| X25-01 zero-weight candidate deltas | **repaired** | only candidates with positive selection weight contribute deltas; with hard top-1 that is the selected record alone (test). |
| X25-02 restored memory loses the weight charge | **repaired** | `weights_bytes` is stored in the snapshot scalars and re-set by `import_state`; the ceiling charge survives a restore (test). |
| X25-03 failed delta allocation leaves a replacement active | **repaired** | a `CapacityError` on the delta write removes the record and restores the superseded one (rolled_back_reason `delta_capacity`). |
| X25-04 delta acceptance baseline / combined config | **repaired + documented** | code steps and delta steps together are refused (the record is removed); the baseline is the support loss under the code-driven write, documented in the docstring. |
| X25-05 retrieval vs learned score | **repaired** | the store's cosine uses the reader's `unit()` formula (epsilon inside the root); dot/L2 remain diagnostics. |
| X25-06 output collision | **repaired** | the run identity (tag + dataset) is fixed before any path; an existing run root is refused. The zsRE per-item directory for `pairown_delta5_null0.5` was overwritten by the CounterFact run and is recorded as lost (summary JSON retained). |
| scientific gaps (normalization contract, differentiable fast unroll, matched base-update phases, explicit query boundary, complete compute accounting) | **acknowledged, open** | tracked in `docs/R1_stage2_notes.md`; the fast unroll and base-update phases are not Stage 2 claims; the query boundary and accounting reconciliation are in the gate-6/7 checklist for the next profile. |
