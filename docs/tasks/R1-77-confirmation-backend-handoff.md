# R1-77 confirmation-backend handoff

The queue is tested against the installed R1-68d development engine. **It cannot execute confirmation yet.** `load_development_cell` rejects sealed mode, reservations and protocol bindings; `run_development_cell` always emits a development banner and uses the development output/resource namespace. A freeze marker does not change that contract. No final recipes currently exist in matrixv5, and all405 final population/result bindings are unset.

## Work required before an owner launch

1. Provide a separately reviewed sealed R1-68d backend. Prefer a new module under scripts while the installed tree is pinned. It must use the actual sealed admission loader and final protocol/reservation identities; it must never transform a sealed recipe into a development recipe or weaken the existing firewall.
2. Preserve the measured boundary-identity policy, read-only phase state checks, exact RevisionCap incremental type restriction, immutable phase journals, contiguous checkpoint chains, snapshot restore verification and full failure-cost accounting. Full-profile adapters retain their correct base/continued-base construction, especially S1 NPZ checkpoints.
3. Give the backend an explicit metadata inspection and execution interface. A queue binding should identify recipe path/hash, backend module/hash, allowed mode, expected canonical result/resource directories, independent populations and admitted per-cell ceilings. Bind all these in the final matrix/freeze; do not dynamically import an arbitrary unbound module.
4. Keep final recipes sealed and inaccessible to development loaders. No final examples are needed for CPU integration: synthetic TinyBase sealed fixtures should exercise genuine freeze/protocol/reservation checks in an isolated test root, without opening real sealed payloads.
5. Test uninterrupted versus checkpoint-resumed final execution; wrong recipe/code/base/reader/calibration/initial-state/snapshot IDs; duplicate/noncontiguous checkpoints; changed endpoint state; missing/torn journal intents; failed construction and out-of-memory/timeout envelopes; duplicate launch locks; October9 stop; partial blocks. Verify complete final reports satisfy the independently declared analysis population, not merely file existence.
6. Extend the new queue's non-development dispatch only after that backend and final bindings are reviewed. This would edit an existing queue file, so request the lead's permission first, with a tested concrete patch. Likewise any existing installed driver/source change needs permission and a new identity/freeze binding.
7. After the September20 cost admission, final draw/seal/freeze and other gate closures, owner launches with a GPU lease and a stable receipt root. The queue's CPU pass is not scientific launch approval.

## Current execution and accounting limits

- Dry-run/status support the405-coordinate final draft and list every incomplete checkpoint. Saved development results are independently analyzed without re-execution.
- The delivered runner executes only explicitly development-scoped matrices. It refuses confirmation before model construction, even if someone adds a true admission flag.
- For exact-code current development recipes, pause/resume is verified at each checkpoint. Unknown attempt/process costs or torn/open journal intents stop automatic progress; retries require reconciliation. It does not silently discount failed work.
- Full child-process time is charged when the queue has a valid start/finish envelope; covered driver attempt time is not counted twice. Historical jobs without an envelope exclude construction. CounterFact's old driver supplies no attempt-total wall field, so its scientific completion is retained but cost is unknown.
- `--ceiling-hours` needs positive cell ceilings. A scenario fallback is status-only and never grants execution. Real-base GPU memory consumption itself is owner-profile evidence; the runner's host MemAvailable guard does not replace a GPU lease.
- Keep the same receipt root across restarts so all process-envelope receipts remain discoverable. Tests redirect old driver output paths in memory only; there is no production switch that turns final results into test results.

No existing driver, source, protocol, board or queue file was changed in this lane. The handoff records a prerequisite rather than claiming the missing sealed backend exists.
