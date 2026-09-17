# Stage 4 queue concurrency — R1-77e

The orchestrator admitted two concurrent cells after the measured probe in
`R1_stage2_notes.md`, section “Concurrency probe 2” (commit `2c63842`). This implementation
adds `--workers 2` to the queue; default `--workers 1` preserves serial execution.
This operational admission does not replace the final population, scientific or freeze gates.

The queue launches at most two cells, in declared order, from the same block. It drains each
pair before scheduling the next pair and completes the current block before entering another.
The existing matrix lock and backend canonical per-cell locks remain in force. Shared output
and snapshot parent directories are created durably by the scheduler before the first launch,
preventing simultaneous cell writers from racing to create them. Per-cell directories remain
the backend's responsibility.

Before every launch, the queue rechecks matrix/bindings/implementation identities, recipe
admission, destination, resume eligibility, deadline, memory and the shared cost account.
With another cell outstanding, MemAvailable must be at least **6144 MiB (6 GiB)**, or a higher
user-specified floor. Otherwise the existing 4096 MiB default applies. The check is made before
launch; it is not a forecast of later process peaks.

Concurrent wall ceilings are **1.5 × 1.1 = 1.65 times the bound solo wall ceiling**. Each
in-flight process reserves that full amount against the same queue budget. Completed process
envelopes replace reservations with actual charged duration. If a second reservation will not
fit, the first worker drains and the queue rechecks actual spend; no two workers independently
spend the same remaining budget. The production subprocess timeout uses this effective ceiling,
bounded also by the October 9 deadline. No recipe or admission flag is rewritten to scale it.
Each start receipt records solo/effective ceilings, other reservations, previous spend and the
memory threshold; each finish records the full process envelope and covered attempt directories.

The shared budget retains the existing **sum of process durations** convention, including time
when cells overlap. It is conservative process-hours, not elapsed queue wall-hours and not a
speedup-discounted GPU cost estimate. `queue_wall_seconds` is reported separately. The final
cost/queue/freeze admission must bind both this policy and the measured solo ceilings; planning
for 140 elapsed hours must not silently treat 140 as the process-hour budget.

On a failed process or executor exception, the queue stops new dispatch, lets the other running
cell finish, writes both envelopes and reports/refuses the failed cell normally. Complete cells
are verified and skipped on restart; incomplete cells use the unchanged resume checks. Unknown
costs, torn state or changed identities still require reconciliation. DEC-052 block membership,
checkpoint missingness and incomplete-cell lists are unchanged. Dry status can use `--workers 2`
to apply the same 1.65 factor to remaining-cost projections.

CPU tests use actual sealed TinyBase cells and real locks/receipts, including a failed worker
paired with a completing worker, restart, shared reservation pressure, memory stops and block
boundaries. No new GPU throughput measurement or real confirmatory execution occurred here.
