# R1-77b — separate sealed backend and queue dispatch proposal

Status: new backend implemented and CPU-tested; existing queue dispatch patch awaits permission.
Agent: Codex, 2026-09-16. Inputs: installed Stage4 sealed loader, R1-68d execution engine,
R1-75 analysis, R1-77 queue, round18 backend handoff. No real sealed payload opened or model run.

## Delivered execution interface

`scripts/r1_77b_sealed_backend.py` uses the actual installed
`stage4_cell.load_cell(..., allow_sealed=True)` admission route. It never invokes the development
loader and never relabels sealed data as synthetic/development. It copies the R1-68d execution body
into a separate module, pins the donor source SHA and checks the donor's profile/dependency bindings.
The installed `src/pccap` tree is unchanged.

Metadata inspection (does not open payloads/reservations or construct the model):

```bash
../venv/bin/python -m scripts.r1_77b_sealed_backend --manifest OWNER_RECIPE --manifest-sha256 OWNER_RECIPE_SHA256
```

Owner-only execution adds `--execute`; checkpoint recovery additionally uses `--resume`.
The Python API is `inspect(path, sha)` / `execute(path, sha, ...)`. Synthetic tests inject a TinyBase
factory and patch isolated test roots/cadence in the test process. There is no production CLI
fixture switch and no code path that admits a development recipe as sealed. The owner still
supplies the GPU lease and final scientific admission.

Canonical production destinations are `results/R1/stage4_sealed_cells/` and the corresponding
`assets/runs/pc_cap/R1/stage4_sealed_cells/` resource tree. Execution envelopes are under
`logs/r1_77b_execution/`, with stable per-coordinate locks under `logs/r1_77b_locks/`.
Tests redirect results into unique roots under `logs/r1_round19/`; snapshots/payload fixtures are
under `assets/test_scratch/r1_round19/`. No test writes to the orchestrator's `results/R1/`.

## Proposed final authority contract — needs owner review and materialization

This is a **new explicit interface**, not a claim that final artifacts already exist. Existing
Markdown protocol v5 and freeze candidate v5 cannot be passed as the executable final artifacts.
The canonical final marker is `manifests/revision_v1/frozen_stage4.json`, deliberately distinct
from the historical v0 `manifests/frozen.json`.

A sealed recipe retains schema1, mode `stage4_sealed_cell`, installed-core `code_sha256`, exact
adapter identity, tokenizer identity, construction, payload, protocol and reservations. It additionally
binds the exact backend `{module,path,sha256}`, independent population file, final freeze and integrity
driver bindings/profile. The four existing admission flags must be literal true.

The final freeze must contain:

- schema1, mode `stage4_final_freeze`, true lead approval and launch authorization, no open gates;
- `closed_gates`, exactly U01–U18, each a hash-bound JSON receipt with matching gate ID,
  status `closed`, and lead approval;
- exact backend, installed-core code identity, driver bindings, protocol/reservation/population bindings;
- nonempty `bindings_sha256` for independently reviewed provenance/code/environment files;
- `recipe_contracts`, keyed by coordinate ID, equal to each canonical compact recipe digest with
  **only its `freeze` field omitted**.

The final protocol JSON has schema1, mode `stage4_final_protocol`, lead approval, no open gates,
checkpoints `[100,300,1000]`, max_new32, locality convention `bounded_text_equality_DEC053` and
experiment deadline `2026-10-09`. The reviewed scientific protocol and decision/evidence files must
be included in the freeze provenance and gate receipts. This compact execution header is not a
replacement for the actual scientific protocol or approved thresholds.

The independent population file contains `cells[coordinate_id]` with ordered edit IDs, paraphrase
counts, expected endpoint IDs and drift denominator/position IDs/source hash. Execution requires
it to equal the payload's planned population. Missing observed endpoint rows remain missing in
analysis; artifact completion alone never grants scientific admission. Reservation content, edit
membership/hash, outside membership, endpoint bundle hash and exact item-order hash are checked by
the installed sealed loader. Final joint role/alias/teacher clearance remains separately reviewed
and bound by the owner; CPU fixtures do not certify real population eligibility.

Write contract hashes → frozen manifest → final recipe envelopes → final matrix → queue binding.
Do not freeze the hash of a file that contains the freeze's own hash. The final queue matrix must
use scope `confirmatory`, contain the entire frozen cell inventory, match the frozen population,
use canonical destinations and have positive admitted per-cell ceilings. A prefix is selected with
`--stop-after`; it is not a smaller replacement matrix.

## Integrity, recovery and cost policy

Full recipe/adapter hashing occurs at attempt start, after resume restore, every checkpoint before
issuing a receipt, and completion/pause. Per-phase in-memory immutable-object/configuration checks
remain. Read-only state hashes, defensive full-profile clones, the exact RevisionCap incremental
restriction, batched drift, immutable journal intents/records, snapshot round-trip hashes and unique
contiguous checkpoint receipt chains are preserved. S1's continued-NPZ construction uses its actual
continued parameters and original-base locality reference, without entering development admission.

The outer backend envelope starts before admission/model construction and records every catchable
failure, including constructor MemoryError and timeout. A hard-killed process leaves a start without
a finish: spend is **unknown**, never zero, and automatic resume refuses until owner reconciliation.
Keep one receipt root across restarts. The queue's larger subprocess envelope supersedes nested
backend/driver times; they are not summed. Completed cells are not rerun. October9 is enforced at
start and between phases/boundaries; queue subprocess timeout supplies the hard end-of-day boundary.
A single long native operation is not asynchronously interrupted by the standalone Python backend.

## Queue patch and validation

`docs/tasks/R1-77b-queue-dispatch.patch` adds statically selected sealed dispatch, exact backend
hash verification, full frozen matrix/population/ceiling agreement, canonical destinations and a
stable queue-lock namespace. It retains development dispatch and the existing metadata-only status
path. No arbitrary module is imported from a recipe. It has not been applied.

CPU evidence: 21 backend tests, 3 proposed-queue tests, 5 additional integrity/parity tests. Cases
include uninterrupted/resumed parity for full and incremental profiles; wrong code/backend/base/
reader/config/budget identities; initial-state/snapshot mismatch; wrong reservations; duplicate
checkpoints/locks; torn journals; mutation rejection; construction failures; deadline boundary;
unknown abandoned spend; partial-block stop and later resume; and incomplete analysis populations.
Five additional round19 tests cover occupancy and corrected draw preflights. Lint and `git apply
--check` pass. Real-base performance, GPU out-of-memory behavior and final owner artifact compatibility
are not validated by TinyBase tests and remain owner admission work.

Done-when for this CPU lane: tested separate sealed API and concrete queue patch delivered. Launch
readiness additionally requires approval/application of that patch and actual final protocol,
reservations, populations, closed gates, reviewed recipe contracts, costs and owner freeze.
