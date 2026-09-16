# R1-D1i — immutable decisions snapshot and register v6

Status: complete (dry artifacts only). Agent: Codex.

Inputs: register v5, live decisions at snapshot time, protocol v4, matrix v4, bound candidate sources, dataset manifest and installed source tree. No selection outcomes or sealed payloads were read.

Outputs: `scripts/r1_d1i_register_v6.py`, `tests/revision_v1/test_r1_d1i_snapshot.py`, `manifests/revision_v1/decisions_snapshot_v6.md`, `manifests/revision_v1/exclusions_frozen_v6.json`, `logs/r1_round15/draw_plan_v6.json`, and `manifests/revision_v1/freeze_candidate_v3.json`.

The snapshot is an exact byte copy of decisions at binding time, including DEC-049/050. Every v5 scientific field is unchanged: policy, acceptance, candidates, removals, counts, clearance state and original parent. Only version/identity metadata and the live decisions binding change. The original v5 file remains hashed historical provenance; its superseded live-file binding is explicitly identified. All other bindings remain mandatory. Re-verification replays the transformation and rejects scientific changes, not merely bad hashes.

The dry plan checks every candidate's bound payload/source-record hashes, deduplicates subjects for count-only strata and emits no candidate identities or draw. Demand is 3 × (1,000 edits + 100 outside + 100 near supports + 100 near neighbours + 50 revision) = 4,050 subjects per dataset.

| Dataset | Candidate subjects | Nominal slack | First loss count causing shortfall |
| --- | ---: | ---: | ---: |
| zsRE | 52,411 | 48,361 | 48,362 |
| CounterFact | 12,246 | 8,196 | 8,197 |
| MQuAKE | 4,218 | 168 | 169 |

MQuAKE has 4,489 candidate items but only 4,218 distinct subjects. Approximately 4% subject loss would exhaust its slack. No positive number of finally cleared subjects is yet certified. Each pending clearance operation can, without further evidence, remove anywhere from zero to the entire remaining candidate set:

1. Alias/entity equivalence and cross-dataset collisions.
2. Context mentions and cumulative exposure through draw time.
3. Final-base E.2 teacher, token and context eligibility.
4. Disjoint roles and compatible near-miss/revision cases.
5. Composition dependency closure.

These upper bounds overlap and must not be added. Historical teacher receipts do not replace final joint clearance. The plan still aborts before draw for that scientific reason; the former live-document hash mismatch is gone.

Freeze candidate v3 contains 238 file bindings, all 18 U gates, 360 core cells and the separate 45-cell extension. Its selected-primary slot remains open. Matrix v4's historical reader/register references are documented as historical; a successor matrix and final gate receipts remain necessary. Candidate emission does not authorize a freeze, draw, seal or launch. Later installed-code changes can make this candidate stale and require a new candidate version.

Verify command: `PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.r1_d1i_register_v6 --create-register --audit` (completed once; outputs use exclusive creation and must not be overwritten). For read-only verification, call `verify_register` on v6 or run `tests/revision_v1/test_r1_d1i_snapshot.py`.

Verify output: zero binding errors; four new tests pass; DEC-043–050 present; policy/membership preserved; MQuAKE slack 168. Combined targeted regression suite: 28 passed in 30.57 s.

Done-when: snapshot/register and both dry outputs emitted with existing scientific gates retained. Cost: GPU seconds 0; CPU hashing only, wall time not separately metered. Deviations: none. Unresolved/questions for lead: final clearance, selected-primary matrix, gate receipts and runtime ceilings. No board or existing file was changed; the orchestrator can mirror this record.
