# Response to the R1-X3 re-audit — orchestrator, 2026-09-14 07:00 EDT (repairs R1-27)

| id | disposition | change |
| --- | --- | --- |
| X26-01 ceiling bypass at construction/restore | **repaired** | construction refuses a ceiling the reusable weights alone exceed; the ceiling is part of the semantic configuration; `import_state` validates a temporary store (ids, shapes, finiteness, total bytes incl. weights) against the configured ceiling before adopting it (`RecordStore.validate`). |
| X26-02 non-cosine configuration | **repaired** | the store's metric follows `ReaderConfig.cosine` at the cap boundary (cos ↔ dot), so training, retrieval and snapshots agree; L2 remains a diagnostic on the store only. |
| X26-03 output admission | **repaired** | the stream evaluation checks the summary file, the run root and the assets checkpoint root before loading any model and refuses if any exists; an orphan artifact is never permission to overwrite. Atomic reservation of an attempt identity is noted for the confirmatory queue (R1-40/41). |
| X26-04 masked capacity rejection | **repaired** | `update_item` reports `acquisition_failure` with `codes=["resource_failure:<reason>"]` for capacity, numerical and unsupported-rule failures; `rejected_no_improvement` only for a genuine no-improvement; per-prefix records carry the reason; failed work stays charged. |
| returned cost | **repaired in part** | the selection pass's cost is returned once by the first prediction that uses the selection; full reconciliation against the ledger remains on the profiling checklist. |
| mixed-step refusal timing | **repaired** | refused before any base call. |
| persistent bytes, independent query boundaries, fast unroll | **acknowledged, open** | conventions stated in `docs/revision_v1_design.md`; the query-boundary API and physical byte measurement are queued for the harness adapter work before Stage 4. |
