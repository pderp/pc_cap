# R1-43 test fixture serialization repair

The new endpoint module passes all ten endpoint tests when this one-line test-fixture correction is applied in memory. The fixture currently serializes NumPy int32 token IDs through JSON, which requires Python ints. Proposed change in `tests/revision_v1/test_endpoints.py`: replace `list(k)` with `[int(i) for i in k]` in `Cap.export_state`. No endpoint implementation, source dataset, core module or production behavior changes.

Exact patch: `docs/tasks/R1-43-test-fixture.patch`. Before/after source hashes and the ten successful direct test invocations: `logs/r1_round5/endpoint_test_repair_preview.json`. Original pytest output: `logs/r1_round5/endpoints_cpu_v2.txt` (five affected failures, five passes).

The user's new-files-only rule requires permission before revising this file, even though it was created in the current round. Requested approval is limited to this one-line fixture repair. The source has not been edited. Other round-5 work continues independently; no commit or GPU use is requested.
