# HT-8 — automatic fidelity watch (DEC-064a)

- Status: watch and queue/report hooks implemented and verified; populated from 3/4 completed chain-S profiles. Binding into the successor publication package remains R1-63m's dependency.
- Agent: Codex, round 34, September 18, 2026.
- Inputs: DEC-064a, round-33 HT-8 specification preserved in commit `037d70a`, round-34 task list; certified completion/checkpoint receipts, exact recipe identities, full-validation vectors, HT-7 concentration and DEC-064 benchmark policy.
- Outputs: `scripts/ht8_fidelity_watch.py`; installed hooks in `r1_77_queue.py`, `r1_77f_scheduler.py`, `ht6_full_validation_report.py`; `docs/fidelity_watch.md`; `results/R1/fidelity_watch/{observations.jsonl,entries.jsonl,alerts.jsonl,maxima.json}`; two new test modules; `HT-8-queue-binding.json`; prepared `HT-8-successor-package.patch`; logs and three-cell preview under `logs/r1_round34/`.
- Verify command: focused command in `R1-round34-handoff.md`; operational scanner command below.
- Verify output: **78 tests passed**, one older TinyBase test excluded. Ruff, patch applicability and proposed-source syntax/lint pass. Real evidence: three audited observations, two breaching cells, zero creep alerts; a repeat update adds zero observations and leaves Markdown bytes unchanged.

## Checks and state

The watch verifies recipe SHA, cell coordinates/mode/cadence/adapter identity, unique completed result, each checkpoint's self-hash/report hash/state and contiguous chain, terminal receipt, complete finite full vectors, both reference identities, exact source/coverage and independent sample overlap. Missing full evidence and corrupted/duplicate completion artifacts are reported as unavailable/invalid; they never become a zero or passing measurement. It reads no model weights or sealed payload bytes and runs no model.

Breach is strictly mean KL >.001 or mean signed NLL increase >.01 against **either** reference. Equality passes. Each breaching cell retains full both-reference summaries, source identities, HT-7 concentration, actual record count (or explicitly unavailable), attempted checkpoint, scope, condition, dataset, realization and order. No-breach observations remain in the journal so they supply valid zero/nonzero baselines and maxima without polluting the breach table.

Identity is the digest of declared mode, recipe SHA and cell coordinates. A duplicate exact observation is a no-op; changed evidence for the same identity is rejected. Recipe identity changes create a distinct observed cell, whose provenance remains visible. Failed/incomplete attempts are not counted as completed cells.

Running maxima are separate by condition × dataset × reference × metric and include all valid observations. The development reference is the **first verified development observation** for the condition/dataset, frozen in journal order with its exact recipe and cell identity. A confirmatory cell cannot establish a development reference. Missing references remain unavailable. The three current development references are the three chain-S profiles; later profiles do not silently reset them.

For each new **breaching** entry, a creep alert records every mean exceeding its prior running maximum or twice its fixed development reference, using strict comparisons. The first observation has no prior maximum; equality at exactly twice the reference does not trigger the twice-reference rule. A zero reference makes any positive mean exceed twice zero. Signed NLL uses its declared signed value, not a percentage-growth calculation. The watch does not add a statistical significance claim or change thresholds/classification.

## Durability, notifications and hooks

An exclusive file lock serializes concurrent queue/report/manual invocations. `observations.jsonl` is the canonical append journal, fsynced with its directory. The breach log, alert log, maxima and a marked section of Markdown are rebuilt atomically from that journal; manual notes are preserved. A retry after interruption between journal and view writes repairs the views without duplication. A torn journal fails visibly for explicit recovery rather than silently discarding data. Markdown change detection refuses an observed concurrent edit. The lock and temporary files are ignored by Git.

The queue invokes the watch **after receipt certification**, and also backfills previously completed cells when a queue resumes. Numerical breaches/creep alerts leave cell completion and scientific admission unchanged. A technical inability to record the watch stops further dispatch for reconciliation; it does not convert a benchmark failure into a scientific veto. Already active workers are drained through the normal scheduler. Existing host/reconciliation stops retain precedence.

New full-validation queues require `matrix.fidelity_watch == ht8_fidelity_watch.binding()`. This binds the policy and exact watch/full-contract/fidelity/concentration sources; changes or omitted bindings refuse execution. Queue start receipts record that binding, and decision receipts record the watch outcome. Historical sampled-only queues remain compatible. Queue status/dry-run stays read-only.

New alerts are written to `alerts.jsonl`, emitted immediately to stderr as `HT-8 CREEP`, and included in the queue's decision receipt. They remain marked pending orchestrator notification. The **orchestrator delivers** alerts immediately and ordinary breach entries at block boundaries; this script does not send messages or modify `lead_queue.md`. A local log entry is not a claim that the lead has already received a notification.

The HT-6 CLI now updates the watch after auditing completed report inputs; its JSON/Markdown record the watch snapshot and counts. `build()` remains read-only. A final HT-6 still refuses fewer than four completed donors. The active shell-driven chain S was not modified: until it completes, invoke the scanner or the partial HT-6 CLI at completed-cell boundaries.

```bash
# Read-only inspection; explicitly lists older cells without catalogued recipes.
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m scripts.ht8_fidelity_watch \
  --recipe-dir docs/tasks/R1-64g --result-root results/R1/stage4_dev_cells

# Add --apply to persist verified observations and update the watch.
```

## Observed development results

The first automated entry reproduces the manual MQuAKE result: mean KL .0055436876 (fail), mean signed NLL increase .0056009764 (pass), ES95 positive loss .114467563, maximum 8.18755035, 171 positions carrying half KL and near-zero target loss fraction .99631377. The completed v0 MQuAKE profile has zero observed KL/NLL change; it supplies a no-breach observation and zero development reference. Its record-count telemetry is unavailable, distinct from its 300-attempt checkpoint.

The third, learned-reader zsRE profile gives mean KL **.0022697245** (fail), mean signed NLL increase **.0023100153** (pass), ES95 positive loss **.0474726905**, maximum **9.94468865**, 64 positions carrying half KL and near-zero loss fraction .99857689. Both references coincide in these original-base profiles. This is a new dataset-specific development reference and a breach notice, **not** a creep alert against MQuAKE. All three full-vector and overlap audits pass. No confirmatory conclusion follows.

- Done-when: certified reader, idempotent logs/maxima/alerts, queue/report hooks, synthetic tests and first-entry reproduction delivered. Reached for HT-8; successor publication binding explicitly remains below.
- Cost: CPU only; model calls and GPU seconds 0. All new fixtures under `assets/runs/pc_cap/R1/rehearsal_fixtures/round34/`.
- Deviations: JSONL views are atomically regenerated from the append-only journal for recovery; their logical records remain append-only. Added explicit unavailable telemetry and preserved manual entries.
- Unresolved: `HT-8-successor-package.patch` is **prepared, not applied**. It switches the assembler to D.3 and binds policy, watch and analysis sources into protocol/freeze/final matrix/publication evidence. It passes syntax/lint and `git apply --check`; full D9/package rehearsal waits for R1-63m's post-chain-S backend and cost dependencies. Old full-validation matrices lacking the watch binding intentionally cannot launch under the new queue.
- Questions for lead: none; reporting delivery remains with the orchestrator as DEC-064a specifies.
