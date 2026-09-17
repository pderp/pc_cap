# Codex round20 handoff

Status: this CPU work batch complete; no existing-file changes, no staging or commits.
Agent: Codex. Verification:50 tests passed in8.20s; ruff passed. GPU seconds:0.
Evidence: logs/r1_round20/verification.json and round20-combined-tests.txt.

| Lane | Status / next owner action |
|---|---|
| R1-68e | Additive helper supports all six v0/S1 families.31 CPU tests pass. Exact driver patch awaits lead permission AND an explicit owner idle boundary. Real-base numerical admission/profile remains Claude's. |
| R1-49g | New protocol v5.1, DEC-057/058/059 analysis, tests, versioned matrix and two analysis reports complete.19 CPU/integration tests pass. Final populations/resources/admission remain open. |
| R1-63e | New dry candidate v6:1112 bindings,17 open gates; no authorization. |
| R1-D9 | Existing preflight/legacy producers inspected; the new three receipt producers are NOT implemented in this batch. Available for follow-up; no exclusive claim retained. |
| HT-3e | Correct final pilot report located/read, but independent36-row raw-file reproduction is NOT completed here. Available for follow-up; no exclusive claim retained. |
| R1-64d | Blocked on permitted R1-68e driver landing and stable post-hook identity. No stale or projected recipe labeled executable. |
| R1-73b | Calibration v3 candidate absent at final check; also needs the landed batching path if selected. |

R1-68e request:docs/tasks/R1-68e-driver-edit-request.md; exact patch:R1-68e-driver.patch.
The user's new-files-only rule is why the live driver has not been edited. Permission request
was sent while the independent analysis work continued. Do not infer approval from this handoff.

Important integration points:
- The sealed R1-77b backend pins the current donor driver SHA. After R1-68e landing it will refuse
  until explicitly reconciled. Do not merely replace its donor hash or launch on the CPU tests.
- Current driver drift runs only at the final checkpoint. Some schedule extrapolations charge
  three drift checkpoints; bind the intended cadence before treating an extrapolation as a ceiling.
- Use scripts.r1_49g_analyze for accepted adjusted classifications; the older R1-75 entry point
  intentionally remains unchanged. Resource comparisons remain unavailable without final charged
  measurement/ceiling receipts; a file-based receipt adapter is still downstream integration work.
- R1-D9 must not reuse the legacy register-v3/two-dataset writer as a v6 final producer. The existing
  register-v6 source_rows helper returns counts/strata, not full payloads. Final clearance must cover
  every candidate disposition and role feasibility, not just nominal counts. Independent role/
  realization RNG streams and exact receipt schemas need testing before real use. No draw/seal made.
- Protocol v5.1 and matrix v5.1 are the current additive accepted-analysis documents. Dry candidate
  v6 records current source identities but does not admit the final experiment.

Owner files seen untracked during this work (left untouched):chain_i.progress, the S1_LM zsRE log
and its active cell directory under results/R1. All Codex outputs are new files under scripts,
tests/revision_v1,docs,manifests/revision_v1 and logs/r1_round20. Existing installed source is unchanged.
