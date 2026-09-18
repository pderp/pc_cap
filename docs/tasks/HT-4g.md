# HT-4g — prepared v6 claim ledger

Status: **done**, Codex, round40, September18, 2026. New files only; no signing-bound source edits, models, GPU or commits.

[Readable v6 content](../talk_claim_ledger_v6_content.md) and [exact JSON content](../../logs/r1_round40/talk_evidence_v6_content.json) contain **40 rows**: inherited qualified history plus the six HT-11 additions. The eight corrected MQuAKE profile rows now use verified completed Chain-Q receipts, not the earlier pending snapshot. Full-validation content includes all eight exact cell/reference numerical rows, including undefined half-KL positions for zero total KL.

The six additions cover programme/meeting, selection uncertainty, HT6 full validation, DEC064, D4 scope and plan-v3 cost scenarios. `DEC060-scale` and `COST-matrix` remain visible but explicitly superseded; deck consumers reject them as current evidence. Four changed historical source bindings (notes, decisions, inference, queue) retain old and current SHA values plus a review explanation. A fifth changed binding, the old execution plan, appears only in the superseded cost lineage; it is not promoted to current cost evidence.

There is exactly one pending publication field: **`signed_cost_receipt = null`**. This is complete content preparation, not signed-cost publication, confirmatory results or launch approval.

## Additive HT-4f publication interface

The new `scripts/ht4g_ledger_content.py` prepares the content and provides an additive `publish` action. It avoids editing the signing-bound existing `ht4f_claim_ledger.py`. The old standalone publisher does not include this expanded40-row content; use the new action for the round40 final ledger.

Once the genuine step2 receipt exists, from the repo root:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m scripts.ht4g_ledger_content publish \
  --content logs/r1_round40/talk_evidence_v6_content.json \
  --cost-receipt docs/tasks/R1-58g-operator_v8/02-cost-admit.receipt.json
```

The publisher rechecks prepared evidence, validates the typed v4 receipt against the reviewed input specification, and requires a matching completed `cost-admit` journal entry with the exact receipt/request digest. It writes **new** `logs/r1_round40/talk_evidence_v6.json` and `docs/talk_claim_ledger_v6.md`, attaches the cost binding and prepared-content reference, and leaves all empirical rows and historical rebindings unchanged. It refuses unsigned templates, stale sources, duplicate publication destinations and a missing/mismatched completed cost request. It never calls the operator to sign or advance a step.

If a bound narrative/source file changes while waiting, refresh and review a new versioned content snapshot rather than bypassing the hash check. Completion of cost publication closes only this ledger dependency; all other scientific/signing/launch gates remain separate.

## Task record

| Field | Record |
|---|---|
| Inputs | v5 ledger, HT11 six additions, HT6 source audit, eight corrected profile receipts, current normative/code/plan evidence |
| Outputs | New content/publisher script, Markdown and JSON v6 content, shared eight-test module, build log |
| Verify command | CPU `python -m pytest -q -p no:cacheprovider tests/revision_v1/test_ht4g_ledger_content.py`; Ruff on new scripts/tests |
| Verify output | Eight tests pass in4.16s; all lint checks pass; unsigned genuine cost template refused without publication |
| Done-when | Six additions/eight numeric rows; explicit supersession; four rebindings; sole pending cost field and publication seam; satisfied |
| Cost | GPU0s; no new research measurements |
| Deviations | Additional changed historical plan binding explicitly quarantined under the superseded cost row; original publisher left untouched |
| Unresolved | Final HT4f publication waits for real signed step2 receipt, still absent at handoff |
| Questions | None; exact later publication command is prepared |
