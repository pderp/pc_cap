# Execution plan v4 — block 1 cost proposal

Synthetic rehearsal: True. Unsigned; active ceilings are unchanged.

Measured class replacements: 1/1; remaining classes retain plan-v3 estimates.
Actual spend: 0.095833 process h; expected total: 0.191667; proposed ceiling total: 0.287500.
Buffer against 750 h: expected 749.808333; proposed ceilings 749.712500.
Active admitted ceiling projection (unchanged): 2.835169 h.

| Condition / dataset / edits / checkpoints | N measured | Expected process s | Proposed effective ceiling s | Basis |
|---|---:|---:|---:|---|
| R1_learned_ff / zsre / 1000 / [100, 300, 1000] | 2 | 172.500 | 345.000 | measured_completed_cell_process_envelopes |

Re-pricing rule: {"version": 1, "class": "condition, dataset, attempted edits, checkpoint cadence, full-validation contract", "donors": "artifact-complete cells through boundary, including every covered failed/retry process; same configured worker count", "expected": "arithmetic mean of comparable completed-cell process envelopes", "ceiling": "1.5 times maximum comparable completed-cell process envelope", "concurrency": "measured envelopes already include concurrency; do not multiply by 1.15 again", "failures": "all failures charged to actual spending; exhausted incomplete cells never become zero-cost donors", "scope": "no outcome-based exclusions; no transfer across dataset, condition, occupancy or cadence", "authority": "unsigned planning proposal only; versioned admission at an idle boundary required before changing ceilings"}

- Rates use only completed comparable chains; failures remain in actual spend and successful retry chains. No fixed future failure allowance is invented.
- Few observations and configured workers do not establish throughput, peak memory or a guaranteed upper bound. Keep existing memory ceilings and admission floor.
- Different occupancy/cadence/classes keep labelled plan-v3 estimates; measured phase rates are not extrapolated without a separately reviewed transfer.
- A quiet snapshot is not a lock or launch permission. Owner must stop dispatch, review the proposal and issue versioned admission before a changed ceiling can take effect.
- October 9 experimental stop; DEC-052 incomplete inventory and DEC-064 secondary benchmark reporting remain unchanged.

## D11 accounting, fidelity watch and DEC-052 inventory

R1 block 1 — 2026-09-18T14:12:35.730511+00:00
Scope: confirmatory; matrix SHA256 aef17ca50b99bb7260daf531dad2f2206c5c543b9920360093da866b55ae6a2d.
Artifact-complete cells: 2/4; complete blocks: [1].
Known spend: 0.095833 process-hours; projected total: 2.835169; declared ceiling: 750.000000.
Projection uses the entire matrix, remaining solo ceilings × 1.15; retry-exhausted incomplete cells are not reserved again. It is not an elapsed-time forecast or a guarantee of full completion.
Cost ledger: Process envelopes replace covered driver attempts; overlap and failures charged once each. Uncovered legacy driver times exclude process startup. JAX timers are not added.
Incomplete cells:
- 996aeb9361c348b8b0aa7fd3: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 1dfef2e4e9a36d84f5bd3af1: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
Watch since previous posted snapshot: 2 global observations (2 in this matrix), 2 breach entries, 0 creep alerts.
- Breach 8ac801b775b03013412fa07d (R1_learned_ff/zsre): capoff: KL=0.002, signed ΔNLL=0; original: KL=0.002, signed ΔNLL=0 nats.
- Breach 0c6cc01e0cc460179ad2d414 (R1_learned_ff/zsre): capoff: KL=0.002, signed ΔNLL=0; original: KL=0.002, signed ΔNLL=0 nats.
Checks: no snapshot/accounting/watch gaps detected
Boundary ready: True; unprocessed cells through boundary: []; accounting/watch gap cells through boundary: [].
Known process-hours through this boundary: 0.095833. Later active blocks can leave the whole-matrix spend/projection incomplete without reopening this boundary.
Artifact completeness does not assert benchmark success, effect significance, admission or launch authority.
This text has not been posted; creep alerts require immediate owner relay, not a wait for the next boundary.
Report digest: ec0fbba6786d0b8855e5832edab99575b98477ac14e8478b9db37aedb785c569

This text has not been posted to the lead queue. Cost proposals are not signatures.
Plan digest: 1d8919dedc8286f0dcfd78a1ffd217354a30616ae5a429bf29d13cc2957aaf3e
