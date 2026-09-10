# DATA-02a: sealed-confirmation integrity and metadata

status: partial — additive implementation verified; public API integration awaits permission
agent: codex
task source: docs/ongoing4.md, Lane H
claim: docs/tasks/DATA-02a.claim.json
commit: none; the lead handles commits

## Inputs

- PDF source of truth, Appendix A rules 3–4 and Appendix H harness/frozen-manifest contract
  (`docs/pdf_text/plan.txt`, extracted from `docs/pc_cap_month_plan_readable.pdf`).
- DATA-02 manifest contract from `scripts/sample_confirm.py` and `docs/tasks/DATA-02.md`.
- Existing `manifest_frozen` schema and S4's `pccap.data.confirm.load` call.
- Metadata only: `manifests/frozen.draft.json`, `SHA256SUMS`, and `DATA-02.meta.json`.
  No actual confirmation item payload was opened, parsed, hashed, or used as a fixture.

## Outputs and behavior

1. `src/pccap/data/confirmation_integrity.py`:
   - Explicit-path helper `load_frozen_manifest`; no default confirmation-data path.
   - Freeze existence and schema gate before payload reads.
   - Exact per-file dataset binding, SHA-256 syntax, and unambiguous index checks.
   - One byte read for hash validation and subsequent parsing.
   - DATA-02 layout checks: confirm mode, item count, unique IDs, order permutations,
     named seeds, dataset/realization/order-seed agreement with the freeze.
   - Aggregate-only sidecar construction, preserving DATA-02 fields and order hash format.
2. `scripts/seal_confirm.py`:
   - Reads explicit preparation inputs, validates every input before creating outputs,
     writes sidecars then the standard SHA256SUMS index.
   - Refuses existing destinations by default, before payload reads; preserves the aggregate.
   - Explicit `--replace` is available for a future authorized reseal. Existing-file
     replacement was not exercised in this task.
3. `tests/data/test_confirm_seal.py`: synthetic success, missing/invalid freeze, malformed
   or ambiguous bindings, absent/mismatched/duplicate index entries, hash-before-decode,
   invalid layouts, metadata privacy/format, multiple realizations, existing-output refusal,
   and no partial publication on invalid input.
4. Six new `manifests/confirm/{zsre,counterfact}_r{0,1,2}.meta.json` files:
   - Copied the allowlisted per-realization records from DATA-02.meta.json.
   - Checked filename/realization correspondence, nonnegative counts, strata totals,
     named order hash format, exact aggregate/index coverage, and draft/index hash equality.
   - These are derived metadata; actual payload hashes were not recomputed.
5. `manifests/confirm/README.md`: layouts, provenance, gates, permitted preparation workflow,
   and the explicit pending public API integration.
6. `docs/tasks/DATA-02a-confirm-api.patch` and `DATA-02a-edit-request.md`: exact proposed
   change to the existing placeholder, awaiting permission.
7. Verification and provenance logs:
   `results/data02a/{synthetic_controls.txt,lint.txt,patch_check.txt,api_proposal.txt,
   metadata_sidecars.json}`.

## Verification

Executed from `/home/derp/cap/pc_cap` with
`PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=''`:

```sh
/home/derp/cap/venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/data/test_confirm_seal.py tests/test_package_layout.py \
  --basetemp=/home/derp/cap/assets/tmp/data02a_controls_20260910_01
/home/derp/cap/venv/bin/ruff check --no-cache \
  src/pccap/data/confirmation_integrity.py scripts/seal_confirm.py \
  tests/data/test_confirm_seal.py
GIT_OPTIONAL_LOCKS=0 git apply --check docs/tasks/DATA-02a-confirm-api.patch
```

Result: **90 passed in 0.37 seconds**; Ruff passed; patch applies cleanly.
Use a new basetemp directory and new log filenames for any rerun.

The proposed wrapper was compiled from the patch additions in memory, with its intended
repository filename. Its default freeze path, successful synthetic load, and missing-freeze
failure passed. This checks the proposal; it is not a claim that S4 is already wired.

Protected-file hash checks confirm `confirm.py`, `SHA256SUMS`, `DATA-02.meta.json`, and
`requirements.lock` match their values at claim creation. No existing dependency environment
or sibling repository was modified. Shared files changed by other agents were left alone.

## Done-when checkpoints

| Checkpoint | State |
| --- | --- |
| Freeze/schema gate before payload access | Passed in the new helper |
| Exact dataset/file/index/payload hashes | Passed on synthetic fixtures |
| DATA-02 layout and order contract | Passed on synthetic fixtures |
| Metadata-only per-file sidecars | Created for all six realizations from existing aggregate metadata |
| Sealing utility and preservation/refusal controls | Passed on synthetic fixtures |
| Confirmation manifest firewall | Passed |
| Public `pccap.data.confirm.load` available to S4 | Pending the existing-file edit permission |
| Task board and shared status update | Deferred to orchestrator; claim/task records available |
| Actual freeze decision / confirmatory execution | Orchestrator and lead ownership; not performed |

## Cost and deviations

GPU seconds: 0. CPU test process wall time: 0.621 seconds (pytest reports 0.37 seconds).
Lint: 0.004 seconds. Patch check: 0.001 seconds. Other work was CPU-only inspection,
implementation, metadata checks, and an in-memory API smoke check. No lease was requested.

The newest user instruction requires approval for every existing-file edit, including
the lane-owned placeholder. The helper and exact patch allow useful additive work while
that public integration waits. The shared status/ledger tools were not run because they
append to existing files; the orchestrator may mirror these records.

The task requested fresh per-file metadata. The already prepared aggregate provided it
without another confirmation-payload read, so the six real sidecars were materialized from
that aggregate. The new sealer's computation from payload bytes was tested only on synthetic
inputs. Existing sums and aggregate formats/content were preserved.

Schema validation establishes structural validity and bindings, not that the lead has
committed or approved a freeze. That decision remains with the freeze producer.
The sealer prevalidates all inputs and writes the index last; its multi-file output is
not an atomic transaction. Run an authorized reseal only when other readers/writers are idle.

## Next steps and concurrency

1. Lead approves `DATA-02a-edit-request.md`.
2. Recheck the placeholder hash/patch against concurrent changes and apply only the public
   loader patch. Add a public API smoke check using fresh synthetic fixtures and logs.
3. Re-run the targeted CPU checks with fresh output paths, then create a new completion
   addendum; do not append to this record without permission.
4. Orchestrator mirrors completion on the shared task board. S4 can then import the loader;
   actual data access still requires the lead's freeze.
5. Future changes to existing seals or the aggregate require separate permission. None is
   needed merely to consume these metadata-only sidecars.

The orchestrator's REG-02 GPU run and other lanes can continue during these CPU checks.
GRAM-01/model code and ENV-05 remain separate future lanes from ongoing4.md; they were not
started while preparing this bounded loader handoff. The GRACE Setuptools pin remains a
separate pending decision. No tasks from those lanes are claimed as complete.

questions for lead: May the prepared patch replace `src/pccap/data/confirm.py`?
