# R1-X2 supplementary finding X25-06 — dataset output collision

2026-09-14, read-only check after Claude's `f95606a`/`cfc6db6` commits. This supplements `logs/audit_r1_25.md` and `logs/audit_r1_25_cfc6db6_addendum.md`.

**High provenance risk:** `scripts/r1_13_stream_eval.py` constructs `rd = OUT / "streams_revision" / tag` before suffixing the summary tag with `@counterfact`. Thus running zsRE and CounterFact with the same tag reuses the same per-item/checkpoint directory. `run_stream` unlinks the existing items/decisions logs on entry and writes the same metrics/checkpoint paths; the derived assets checkpoint directory also collides. The two top-level summary JSONs have different names, so their existence does not prove the detailed evidence for both runs survived.

Observed at the current committed output:

- `results/R1/stream_eval_pairown_delta5_null0.5.json`: dataset zsRE, ES 1.00, RET-GS .61, LS .14.
- `results/R1/stream_eval_pairown_delta5_null0.5@counterfact.json`: dataset CounterFact, ES .96, RET-GS .28, LS .20.
- The sole shared `results/R1/streams_revision/pairown_delta5_null0.5/items.jsonl` contains 100 rows beginning `cf-2230`, `cf-10664`, `cf-12815`. It currently preserves CounterFact's detailed item stream. There is no dataset suffix in that run directory.

The per-dataset summaries remain useful descriptive evidence. Paired item-level analysis, error inspection and checkpoint drift for the earlier zsRE cell cannot safely use that now-CounterFact directory. Do not infer that the scores themselves were corrupted merely from the artifact collision; their reconstructability and per-item provenance are the issue.

Owner repair/checkpoint: compute the complete dataset/condition/run identity before choosing **both** result and checkpoint paths; require a new run root unless an explicit resume protocol applies. Execute two tiny dataset fixtures under one human tag and assert all paths differ and the first fixture's files/checkpoint hashes remain unchanged. Inventory older affected runs before claiming their detailed artifacts are complete. Recover from preserved logs/checkpoints if possible; rerun only missing evidence under the corrected naming and declared source version.

No shared script or existing result was edited. The new R1-24 runtime already namespaces its fresh results as `<run-id>/<dataset>/<original|continued>/<cap>/` and checks the result, weights and snapshot roots are absent before launch.
