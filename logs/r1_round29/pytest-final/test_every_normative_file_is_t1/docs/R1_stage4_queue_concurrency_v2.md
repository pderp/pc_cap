# Stage 4 queue concurrency v2 — R1-77f

This replaces v1's double safety factor and stop-on-first-cell-failure policy. Operational
concurrency is admitted from two zsRE development probes; final population, cost, protocol and
freeze approvals remain separate. No GPU measurement is added by this CPU implementation.

## Ceilings and accounting

The matrix's `cell.ceilings.wall_seconds` is the **admitted solo ceiling**, already containing
1.5 times the measured solo process cost. `--workers 1` uses that ceiling. `--workers 2`
multiplies it once by **1.15**, covering the observed probe slowdown up to 1.1335. Thus a
100-second measured solo process has a 150-second matrix ceiling and a 172.5-second two-worker
ceiling. Never apply 1.5 again to the stored ceiling. These measurements are short development
probes, not a guarantee for all datasets, S1, or complete final endpoints.

The machine-readable `queue_ceiling_contract` is defined in
`scripts/r1_77f_scheduler.py:CEILING_DEFINITION` and recorded in the versioned matrix/schema.
Version-2 population recipes require that matrix contract. Contradictory definitions refuse.
The production child timeout uses the effective ceiling and the October 9 deadline.

One shared budget charges **the sum of full process envelopes**, including initialization,
failed attempts and time when workers overlap. Each active process reserves its entire
effective ceiling. Finished envelopes replace reservations with actual spend, without double
counting covered driver attempts. A retry requires another reservation. Insufficient headroom
for a second process defers it until actual cost is known. Elapsed queue wall time is reported
separately; a wall-clock speedup must never discount the process-hour budget.

## Dispatch and failures

At most two cells run in the same declared block. The next cell fills a free worker slot;
the other worker continues. The scheduler drains all active cells at a block boundary before
starting the next block. Matrix and per-cell locks still enforce exclusive writers. Complete
cells are hash-verified and skipped. Resume uses the unchanged driver/backend checks for the
last certified checkpoint, snapshots and receipt chain.

An ordinary cell failure gets **one automatic retry**. A second failure leaves the cell
incomplete in the DEC-052 inventory and dispatch proceeds to the next cell without draining
the other worker. The two-failure count is reconstructed from hash-linked queue receipts for
the same matrix/cell, so restarting with the same receipt root cannot reset it. Preserve and
reuse that root when resuming this queue. A new root or changed matrix is a new operational
admission, not a way to erase a failure. Deliberate successful checkpoint pauses stop for
explicit resume and are not classified as failed attempts.

Host failures stop new dispatch: memory guards/OOM, signal termination, lease loss, and
storage/I/O failures. The production queue requires a live, externally held owner GPU lease
and checks its identity and lock before dispatch and during polling. Already running workers
finish under their existing timeouts and guards; their envelopes are charged. Unknown costs,
torn state, damaged snapshots or changed identities require owner reconciliation and never
receive a blind automatic repair/retry.

Before every launch, verify matrix/bindings/implementation hashes, recipe admission, output
destination, resume state, deadline, memory and budget. The default memory floor is 4096 MiB;
with another active cell it is at least 6144 MiB (or a higher requested floor). This is a
launch guard, not a prediction of later peaks. Start/finish/decision receipts record policy,
previous failures, reserved/charged amounts, lease identity and whether other workers remained
active. Status reports complete blocks, missing checkpoints, exhausted retries and all
incomplete cells. Missing endpoints and partial cells never become successful observations.

Tests use actual CPU TinyBase drivers and sealed synthetic cells: checkpoint recovery,
retry exhaustion across restart, continuation with the other worker active, budget pressure,
memory/lease stops, changed contracts and bounded process-log failure classification.
