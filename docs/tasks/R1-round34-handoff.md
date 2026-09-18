# Round 34 handoff — fidelity watch installed; three profiles complete

Codex, September 18, 2026, 08:10 EDT. Starting HEAD `4e5a3c4`. CPU only; no commits, staging, GPU/model execution, production draw/seal/freeze or signatures. Active chain-S driver/backend/source bindings remain untouched.

| Lane | State | Next action |
|---|---|---|
| HT-8 | **Done:** independent certified reader, durable idempotent watch, maxima/creep alerts, installed queue and HT-6 hooks, first-result reproduction | Orchestrator reports breach entries at block boundaries and creep alerts immediately; bind hook into successor package |
| R1-63m | Prepared package patch; candidate/forms/sheet still pending | Owner's backend patch after chain S, complete cost evidence, then D.3/watch-bound candidate v14/forms v9/sheet v8 and full rehearsal |
| R1-58l | Three donor profiles audited; no v4 receipt issued | Final v0 zsRE donor; typed v4 validator, explicit transfers, ceilings v2, revised schedule and gap inventory |
| HT-6 | Reviewed **3/4** preview with automatic watch update | Fourth donor, final build without `--allow-partial`, then figure/two-sentence presentation export |
| X19 | Waiting | Exact successor package |
| HT-4f | Waiting | Signed receipt v4 |

## New breach notice for the lead

The completed learned-reader **zsRE** profile measures full-validation mean KL **.0022697245**, above the **.001** benchmark, and mean signed NLL increase **.0023100153**, below **.01**. Both reference measurements coincide for this original-base condition and pass integrity/coverage/overlap checks. Positive-loss ES95 is .0474726905, maximum 9.94468865, and 64 positions carry half KL. This establishes the first development reference for that condition/dataset; it is a **breach notice, not a creep alert relative to MQuAKE**. It remains development evidence and does not veto primary comparisons under DEC-064.

The automated watch now contains three audited observations, two breaching cells (learned MQuAKE and zsRE), and zero creep alerts. The v0 MQuAKE result has zero observed KL/NLL change and is retained as a no-breach observation/zero reference. Watch: [current entries and maxima](../fidelity_watch.md). Preview: [report](../../logs/r1_round34/ht6-partial-preview/report.md), [figure](../../logs/r1_round34/ht6-partial-preview/tail-survival.png). The first learned MQuAKE entry reproduces the manual source numbers, including 171 positions carrying half KL.

## Installed behavior

`scripts/ht8_fidelity_watch.py` verifies exact recipe/completion/checkpoint/report/vector/source/reference identities and full coverage/overlap without a model or sealed payload read. Both references' KL/NLL thresholds use strict exceedance; equality passes. Actual record telemetry is kept separate from attempted checkpoint count. Full tail and HT-7 concentration summaries remain in each machine entry.

The locked, fsynced `results/R1/fidelity_watch/observations.jsonl` is canonical. Breach/alert JSONL views, running maxima and the managed Markdown section are rebuilt atomically; retries repair interrupted view writes without duplicate cells. Existing manual notes remain. Changed evidence for an existing cell or a torn journal fails visibly. Running maxima are separate by condition/dataset/reference/metric. The first verified development observation supplies a fixed, source-bound reference; confirmatory data do not define it. This operational convention and exact alert comparisons are documented in [HT-8](HT-8.md).

Queue calls occur after receipt certification and during backfill of already completed cells on resume. Benchmarks and creep alerts do not stop cells or change their scientific admission. Failure to **record** the watch stops new dispatch for reconciliation while preserving completed evidence and existing host-stop precedence. The hook emits new alerts to stderr and durable local logs/queue decision receipts. The orchestrator conveys alerts to the lead; the script does not send messages or edit `lead_queue.md`.

The HT-6 CLI now also updates the watch; its report records a snapshot of the live watch's hashes/counts. `build()` and queue status/dry-run remain read-only. The current shell-driven chain was not altered; the owner can invoke the scanner/HT-6 hook after the fourth profile completes. A repeated update on all three current inputs was a no-op for observations and Markdown: `logs/r1_round34/repeat-watch-check.json`.

## Validation

**78 tests passed**, one older TinyBase case deliberately excluded; `logs/r1_round34/final-tests.txt`. This includes numerical boundaries, either-reference breaches, separate groups, fixed and zero development references, new maxima versus twice-reference alerts, concurrent duplicate writers, interrupted-view recovery, torn-journal refusal, corrupted receipts/vectors, actual small certified-vector input, scanner/report integration and one/two-worker scheduler hooks. The existing primary-policy, concentration, full/sample and inference checks also pass. No whole-suite claim is made.

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m pytest \
  tests/revision_v1/test_ht8_fidelity_watch.py \
  tests/revision_v1/test_ht8_queue_hook.py \
  tests/revision_v1/test_ht6_full_validation_report.py \
  tests/revision_v1/test_ht7_concentration.py \
  tests/revision_v1/test_r1_49m_fidelity_policy.py \
  tests/revision_v1/test_r1_49h_analysis.py \
  tests/revision_v1/test_r1_49g_analysis.py -k 'not tinybase' \
  --basetemp ../assets/runs/pc_cap/R1/rehearsal_fixtures/round34/<new-pytest-directory> -q
```

Ruff and `git diff --check` pass. The three-cell PNG was visually inspected. Tests/fixtures use the required assets rehearsal directory. `logs/r1_round34/final-integrity-check.json` records protected-source, preview, watch and measurement verification. Claude's progress, log, time and live result changes belong to Claude; this lane did not write them.

## Package boundary and remaining work

`docs/tasks/HT-8-queue-binding.json` is the current exact binding. New full-validation queues now require it in `matrix.fidelity_watch`; its source hashes are rechecked before dispatch. Queue start receipts carry the binding. Old full-validation matrices without the watch intentionally cannot launch with this queue version.

`docs/tasks/HT-8-successor-package.patch` is **prepared but not applied**. It changes the assembler to D.3, validates the DEC-064 policy on all cells, binds all declared analysis sources and watch/queue sources in publication evidence, and carries watch/policy metadata into the executable protocol, freeze and final matrix. Syntax, Ruff and `git apply --check` pass; full D9/package execution rehearsal remains with R1-63m after the explicitly required backend/cost dependencies. The installed assembler currently still uses its D.2 default and does not yet emit the mandatory watch field; do not present it as a ready successor package or reuse v13 signatures/digests. A new request digest and complete rehearsal are required.

The measured-cost inventory is now 3/4: `logs/r1_round34/chain-s-partial-inventory.json`. It is not v4 admission. Keep full outer phases and all sampled phases separate to avoid double counting, and preserve S1's extra original-base forward, CounterFact per-position transfer, 1,000-record occupancy, unmeasured condition/near-revision gaps, memory scope, failed-attempt charging, 750 process-hours, 1.5× solo ceilings, one 1.15× two-worker adjustment and the October 9 stop. The final figure/result have not been exported to presentation materials.

All changes remain uncommitted for the lead. New files: watch script, two test modules, watch logs/ignore file, watch binding, package patch, claim/task/handoff and round-34 evidence. Existing files edited: queue, scheduler, HT-6 generator, watch Markdown and HT-6/R1-58l task records.
