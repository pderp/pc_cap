# DATA-02a completion: public confirmation loader connected

status: done (implementation and CPU verification; shared board mirror remains with orchestrator)
agent: codex
completed: 2026-09-10T12:03:22.395689+00:00
commit: none; the lead handles commits

This addendum supersedes the pending-integration statements in DATA-02a.md,
DATA-02a.claim.json, the edit requests, and manifests/confirm/README.md. Those historical
records were preserved except for the specifically approved PDF-reference correction.

## Approved changes

The lead replied “yes, go ahead with that” to the request for exactly two edits:

1. Applied DATA-02a-confirm-api.patch to src/pccap/data/confirm.py. The public
   `load(manifest_path, frozen=ROOT / "manifests" / "frozen.json")` API now delegates to
   the previously tested freeze-gated integrity helper. S4's existing import is available.
2. Applied DATA-02a-reference-correction.patch to docs/tasks/DATA-02a.md, correcting
   the package/harness contract reference from Appendix H to section F.7 of the PDF.

The placeholder hash matched its reviewed value before application. Both patches passed
`git apply --check` and were applied to the working tree without updating the index.
Other staged work present at turn start was left alone.

## Verification

Executed with `PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=''`
and the existing project Python environment:

```sh
/home/derp/cap/venv/bin/python -B -m pytest -q -p no:cacheprovider   tests/data/test_confirm_seal.py tests/test_package_layout.py   --basetemp=/home/derp/cap/assets/tmp/data02a_approved_controls_20260910_01
/home/derp/cap/venv/bin/ruff check --no-cache   src/pccap/data/confirm.py src/pccap/data/confirmation_integrity.py   scripts/seal_confirm.py tests/data/test_confirm_seal.py
GIT_OPTIONAL_LOCKS=0 git diff --check -- src/pccap/data/confirm.py docs/tasks/DATA-02a.md
```

Results: **90 pytest tests passed in 0.34 seconds**, Ruff passed, and the diff check passed.
Logs are results/data02a/approved_controls.txt, approved_lint.txt, and approved_diff_check.txt.
Future reruns must use fresh fixture directories and new log filenames.

A separate smoke check imported the actual public `pccap.data.confirm.load` after patching
and used fresh synthetic fixtures under assets/tmp/data02a_public_api_20260910_01:

| Case | Result | Payload reads |
| --- | --- | --- |
| Valid frozen binding and realization | Exact manifest returned | 1 |
| Missing freeze | PermissionError | 0 |
| Invalid freeze schema | SchemaError | 0 |
| Missing SHA256SUMS entry | ConfirmationIntegrityError | 0 |
| Payload hash mismatch | ConfirmationIntegrityError | 1 |

The repository default freeze path was also checked without opening the real freeze.
The smoke fixtures copy frozen.draft.json metadata and contain synthetic items only.
The code used the same existing synthetic case factory as the targeted tests, called
`load(manifest, frozen=frozen)` for each case, and intercepted Path.read_bytes to check
the read counts above. Full results, output paths, and final approved-file hashes are in
results/data02a/public_api_completed.json.

## Completed checkpoints and handoff

- The public loader required by S4 is implemented and verified.
- Freeze validation, exact file/index/payload hashes, DATA-02 structure, orders, and named
  seeds are covered by the tests. The confirmation firewall passes.
- The sealer and six metadata-only sidecars from the preceding round remain verified.
  Existing SHA256SUMS, aggregate metadata, requirements.lock, and all six sidecar output
  hashes were checked unchanged. Actual confirmation payloads were never opened.
- No GPU execution, dependency updates, shared board/ledger writes, or commits were performed.
  The orchestrator can mirror DATA-02a as done using this completion record.
- Actual freeze approval and S4 execution remain with the lead and orchestrator.
  This implementation does not authorize confirmation-data access before that freeze.

Cost for this approval round: gpu_seconds=0; pytest process wall_seconds=0.566849;
lint wall_seconds=0.004319; diff check wall_seconds=0.001017; public API smoke
wall_seconds=0.0266873340588063. Other work was CPU-only review and documentation.

Deviations: completion is recorded in this new file because approval covered only the two
specific existing-file patches. The shared task board and older pending-status text were
not edited. No change to a freeze, seal, environment, or sibling repository was included.

Unresolved within DATA-02a: none. The unrelated GRACE Setuptools pin remains unapproved;
GRAM-01/02 and ENV-05 were not part of this two-patch approval.
Questions for lead: none for DATA-02a.
