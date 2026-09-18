# Round 35 — Codex handoff

2026-09-18. CPU only; no model/GPU use, signatures, sealed payload access,
production draw/seal/freeze/launch, staging or commits by Codex.

| Lane | Work completed this round | Remaining |
|---|---|---|
| R1-D11 | Launch-day runbook, read-only block/daily report, 15 synthetic reporting tests, concrete scheduler-binding defect reproduction and proposed patch | Production prerequisites remain open; owner should incorporate the proposed assembler fix before rebuilding/signing metadata |
| R1-58l | Four exact donors independently audited; all27 historical sampled-phase costs extracted/bound; explicit unreviewed rate-transfer/replacement sensitivity and gaps; 13 cost-basis tests | Typed v4 validator and receipt, actual reviewed transfers/occupancy/reference evidence, updated host/endpoint accounting, final ceilings v2 and schedule |
| R1-63m | Two additional integration gaps documented | Correct assembler matrix hash and operator receipt-bound ceilings; then complete candidate v14/forms v9/sheet v8 and full rehearsal after cost work |
| X19 | Not begun | Requires actual v14 package |
| HT-4f | Not begun | Requires signed receipt v4 |

The dependency state changed during this turn: chain S completed, and Claude
applied the backend and HT-8 assembler patches, updated the fourth watch entry,
and generated the final HT-6 report. Those owner outputs were not duplicated.
Claude also committed an intermediate snapshot of our D11 files in `c3484f3`;
the later block-report improvement, cost basis and final documentation followed.
The owner's deletion of `results/R1/chain_s.progress` is not our change.

Read `R1-D11.md` and `R1-D11-launch-runbook.md` for the operator sequence. The
report uses verified queue inventory and the process receipt ledger, replays the
canonical watch, and checks the previous report's hash/run identity/journal
prefix. It exposes missing costs and watches, preserves completed versus
retry-exhausted incomplete cells, and handles a closed block while later workers
are live. It writes new JSON and text files, never posts or acknowledges alerts.
`logs/r1_round35/d11-example/` is explicitly synthetic, not production evidence.

The assembler omission is reproduced in
`logs/r1_round35/package-binding-gap.json`: the actual emitted dictionary fails
the real scheduler's required `matrix_sha256` guard before any model call.
`R1-D11-package-binding.patch` remains unapplied because Claude was editing that
file in this round; it passes `git apply --check` against the installed HT-8
successor. Separately, `r1_58g_operator.check_fields(cost-admit)` still selects
ceilings v1 by path; it must consume the new typed receipt's exact bound ceilings.
Both fixes must precede candidate/signature identity generation. No permission
question is needed for these repairs once the file owner is clear.

Read `R1-58l-round35-cost-basis.md` for the exact four-donor table, full-versus-
sample separation, CounterFact implementation mismatch, explicit sensitivity
formula and nonsignature gaps. `transfer-basis-v2.json` is current. Its combined
483.70 process-hour scenario (725.55 after the solo safety margin) is **not an
admitted projection**: inherited nonvalidation estimates, missing endpoint/state
measurements and unreviewed sample/full transfers remain. No typed receipt or
production ceiling was manufactured from this exploratory arithmetic.

Verification: **52 focused CPU tests pass**, Ruff passes for all four new Python
files, nine shell blocks and both embedded Python snippets parse, independent
four-donor/all27 extraction succeeds, and the new assembler patch applies cleanly
in check-only mode. Current evidence: `logs/r1_round35/focused-tests-v2.txt`,
`runbook-syntax.json`, `chain-s-inventory.json`, `transfer-basis-v2.json`.

Remaining work in R1-58l and R1-63m includes implementation as well as evidence
review; this handoff does not mark the whole round complete or signatures-only.
