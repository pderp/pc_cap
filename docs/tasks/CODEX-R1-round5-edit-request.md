# Round 5: three tested one-line corrections (permission requested)

Status: awaiting permission; no existing file has been edited.

The new-files-only instruction applies even to files I created this round. The first correction below was already requested. This request consolidates it with two further corrections to the newly created validation files:

| File | Exact correction | Reason |
| --- | --- | --- |
| `tests/revision_v1/test_endpoints.py` | `list(k)` → `[int(i) for i in k]` in the mock snapshot | JSON cannot encode NumPy int32 token IDs. |
| `tests/revision_v1/test_r1_27_superseding_cpu.py` | preflight statement count `7` → `6` | The extracted driver contains five assignments and one refusal check. |
| `scripts/r1_stage2_table_audit.py` | compare the full summary tag with the full table tag | CounterFact rows already carry `@counterfact`; stripping only the source suffix prevented nine matches. |

Exact patch: `logs/r1_round5/repair_preview_v2/proposed.patch`.
Source hashes and validation: `logs/r1_round5/repair_preview_v2/verification.json`.

All three corrections were compiled and exercised **in memory**. Nineteen endpoint/boundary test functions passed; the remaining boundary test failed for the intended production checkpoint-path defect (X4-10). All 30 stream-table rows matched their correctly identified summaries. This is direct test invocation, not a claim that the unedited on-disk pytest suite passes. The separate LM/boundary pytest run passed 30 tests before its two statement-count fixture failures; its original xfail occurred before reaching the intended checkpoint check, so only the repaired preview establishes that defect.

Reproduce with a fresh output directory:
```bash
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /home/derp/cap/venv/bin/python scripts/r1_round5_repair_preview.py --output-dir logs/r1_round5/<new-preview-directory>
```

Approval would allow only these three one-line edits, followed by normal CPU pytest and a fresh table audit. No production module, owner file, task board, source data, GPU job or commit is included. The production checkpoint-path correction belongs to the orchestrator lane and is documented separately in `logs/review_r1_stage2.md`.
