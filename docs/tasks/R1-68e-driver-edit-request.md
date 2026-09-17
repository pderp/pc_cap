# R1-68e — opt-in v0 drift dispatch: existing-file edit request

Status: tested, NOT applied. Agent: Codex. CPU only; no commits.

The lead's new-files-only rule requires permission to change
`scripts/r1_68c_dev_cell.py`. The exact patch is `docs/tasks/R1-68e-driver.patch`;
source/proposed SHA-256 values are in
`logs/r1_round20/r1-68e-driver-patch-identity.json`.

The patch binds the new batch module into the driver identity and adds explicit
`drift_implementation: "v0_batched_v1"` dispatch for the six v0-family comparators.
It retains full integrity mode, phase state checks, snapshot/restore, cadence,
receipts and accounting. Existing recipes keep their scalar/full or
RevisionCap/incremental dispatch but require rebinding because the driver changed.
No learning or installed `src/pccap` code changes.

Validation: 31 CPU tests passed in 4.28 seconds, including all six adapters,
occupied/empty banks, zero-value hits, fresh independent retrieval, live versus
stable downstream keys, exact null preservation even with poisoned partial rows,
S1's distinct original base, physical padding, failure costs, length buckets,
profile admission and projected driver dispatch. Maximum TinyBase per-position
NLL difference: 1.8158412e-6 nats (test ceiling 1e-4).
Log: `logs/r1_round20/r1-68e-final-tests.txt`.

Apply only after the orchestrator confirms an idle boundary: chain I/J may be
using the old driver identity. An observed idle GPU alone is insufficient evidence
that queued work has released the code binding. Then build R1-64d/R1-73b recipes
and have the orchestrator run the real-base parity/re-profile gate (each position
<=1e-3 nats; identical exceedance counts at .01/.1/1 against both references).
CPU parity is not real-base admission or a measured speedup.

The sealed backend `scripts/r1_77b_sealed_backend.py` pins the old donor SHA and
will refuse after this patch. It must be reviewed and rebound separately before
sealed execution; this request does not authorize a silent donor rehash or final
freeze. Current owner development runs must retain their existing driver until
coordinated rebinding.

No real execution, draw, seal or frozen manifest is requested. Please approve
this exact driver patch, subject to the orchestrator's idle-boundary confirmation.
