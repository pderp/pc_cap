# Round19 — three prepared existing-file edits

Status: permission requested; none applied. Agent: Codex,2026-09-16.
The lead's standing rule requires approval even for a file created earlier in this round.
Exact current source and patch hashes: `CODEX-R1-round19-edit-bindings.json`.

1. **`scripts/r1_77_queue.py`** — apply `R1-77b-queue-dispatch.patch`. Add the separately tested sealed
   backend's hash-bound dispatch, frozen matrix/population checks, canonical destinations and locks.
   A draft/candidate or open freeze still cannot launch. Tests cover partial-block stop/resume and
   wrong backend/population refusal. No experiment is launched by applying the patch.
2. **`scripts/r1_76_unseen_common.py`** — apply `R1-76b-runner-cadence.patch`. Admit only the explicitly
   labelled DEC-056 MQuAKE100/300 population with missing1000; preserve the full cadence otherwise.
   This enables the production validator for the new population. Create a new spec version after
   application to bind the changed runner; the v1 spec remains historical. No GPU run is included.
3. **`scripts/r1_58c_draw_seal_preflight.py`** — apply **`R1-58c-markdown-binding-v2.patch`**. Correct
   the newly created dry checker to hash the Markdown protocol without parsing it as JSON and accept
   its `docs/` location. This preserves file-hash validation and metadata-only behavior. The earlier
   `R1-58c-markdown-binding.patch` is superseded and must not be applied. All real missing receipts
   continue to refuse after the correction.

Validation: 29 tests of backend/queue/occupancy/proposed corrected preflights pass in
`logs/r1_round19/proposed-patches-tests-v2.txt`; five additional uninterrupted/resumed and parameter
identity tests pass (8.30s). Lint passes. `git apply --check` passes for the three listed patches.
The currently delivered preflight regression test exposes the third defect until its source patch
is applied; its corrected version passes. That is documented, not silently waived.

After approval: verify source hashes; apply exactly these three patches; run the four new focused
CPU test modules and lint; regenerate dry previews into **new** log files; create the version2
MQuAKE spec with the now-approved runner hash; inspect that spec. Do not modify protocols, decisions,
boards, candidate manifests or previous logs. Do not draw, seal, freeze, launch or commit.

Reason for pause: the user's standing “only additional files creation” instruction explicitly requires
permission for edits to existing files. Independent new-file preparation is complete.
