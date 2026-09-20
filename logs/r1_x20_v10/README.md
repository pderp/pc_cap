# X20 post-session-v10 review

This directory is Codex's CPU-only verification lane. The locked project tree,
operator journal, forms, published metadata, and resources are read-only inputs.
No signing, experiment launch, GPU execution, or sealed-payload parsing occurs.

`claim.json` records the lane claim. `verify.py` reconstructs the signed requests,
replays clearance and the deterministic draw, rebuilds endpoints in memory from
the bound unsealed resources, checks the sealed copies by hash, and validates
publication and the final queue against the installed backend.

**During development, `attempt-*` files are reviewer harness diagnostics, not
project defect reports.** Attempt 01 corrected the reviewer's assumption that an
initial unsigned preview form was the full preview report. Attempt 02 corrected
the reviewer's serialization assumption: endpoint resources use compact JSON,
while the D9 seal writer uses indented JSON. Both formats are independently
reconstructed. Any later harness correction is documented in the final report.

The final [report.md](report.md) and [attempt-04 verification](attempt-04/verification.json)
are the completed **PASS** finding. Attempt 03 narrowed the sealed-payload guard
to allow inventory metadata while retaining the payload/reservation parsing ban.
The orchestrator records its separately authorized launch in lead-queue item 100;
the review records immutable steps 1–8 separately from concurrent step-9 activity.
