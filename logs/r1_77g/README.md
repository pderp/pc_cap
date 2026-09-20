# R1-77g preparation artifacts

The current handoff is [R1-77g.md](../../docs/tasks/R1-77g.md), with
[Q21](../../docs/tasks/R1-77g-Q21.md),
[resume procedure](../../docs/tasks/R1-77g-resume.md), and the unsigned
[v2 amendment](../../docs/tasks/R1-final-queue-bindings-v2.json).
The live queue remains under v1. No real signal, signature, model call, GPU run,
source-lock edit or commit was performed by this lane.

Current verification: `tests-release.txt` (16 passing CPU cases),
`lint-release.txt`, `inspect-release.txt`, `accounting-release.txt`,
`content-lock-verification.json`, and `block1-accounting-scenario-final.json`.
`block1-evidence.json` contains every selected immutable source identity, all 45
timing rows, nine class summaries and explicitly historical ceiling scenarios.
`completion.json` identifies final artifact hashes.

`consumer.py` is a proposed operational extension outside the locked source
inventory. Its `run --execute` mode requires a new exact signed request, clean
current D11 cutover evidence and the external GPU lease. It was tested only with
synthetic JSON executors. `accounting.py` is read-only and never applies policy.

Earlier `preparation.json`, the original preparation/inspection console logs and
`block1-accounting-scenario.json` refer to the initial unsigned draft consumer
binding. `draft-consumer-finalization.json` records the final metadata-read
hardening and resulting proposal hash; no scientific or numerical policy changed.
The earlier files are retained as draft history, not current activation inputs.

`tests-01.txt` records an initial fixture error: synthetic cell IDs were not
canonical and their order slots began at zero. The fixtures were corrected to
use the installed coordinate IDs and positive slots; no production validation
was weakened. The `test-scratch-*` directories contain only synthetic records;
they must never be treated as real process costs or approvals. Tests 02/final/
complete predate additional cases or final hardening; `tests-release.txt` is the
authoritative result.
