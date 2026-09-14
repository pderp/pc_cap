# R1-D1f — accepted-register binding

- Status: done; register binding only, no draw.
- Agent: Codex; 2026-09-14.
- Inputs: DEC-041; exclusions v2/v3; DEC-039 six-thousand-subject reservation and accepted training pool;
  zsRE fresh candidates v1 plus the v3 overlay; CounterFact fresh candidates v1 under both readings.
- Outputs: [exclusions_frozen_v3.json](../../manifests/revision_v1/exclusions_frozen_v3.json),
  [builder/verifier](../../scripts/r1_d1f_freeze_register.py), [CPU guards](../../tests/revision_v1/test_r1_d1f_binding.py),
  [build log](../../logs/r1_round8/d1f_manifest_cpu.txt), [test log](../../logs/r1_round8/d1f_tests_cpu.txt).
- Verify command: `PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= /home/derp/cap/venv/bin/python -B -m pytest -q -p no:cacheprovider tests/revision_v1/test_r1_d1f_binding.py`.
- Verify output: **15 passed**; Ruff passed. Builder replayed the v2+reservation fold, verified every survivor's source
  and mapped-content hash, counted both candidate readings and rechecked all 14 bound input/resource hashes.
- Done when: accepted policy/register/counts and derived inventories have one immutable binding, with both CF readings
  explicit and no draw. Satisfied.
- Cost: GPU 0 s; no teacher/model execution; CPU metadata and resource-integrity checks. Elapsed round time is in the
  separate completion record, not multiplied across lanes.
- Deviations: added reusable verification and refusal tests so draw consumers can pin the wrapper directly.
- Unresolved: fresh eligibility/context review, CounterFact source decision, subsequent-exposure review, endpoint
  reservation/sealing and final lead freeze are separate gates.
- Questions for lead: no new decision beyond the already open CounterFact source choice. No existing board file
  was edited; completion is supplied additively for the owner to mirror.

The wrapper's SHA-256 is **`d3549f43327ec80f497cfd71df82494c7c0bded02c8e6f5c2c333800b2489805`**.
The accepted register SHA is `e214de7d048c6b104fc62c75757eed01f12b47fb330eaeeb58c1a2bec8fbbd4a`;
policy v2 SHA is `481e04c3eba70ea2f85aada9c0599c4f44031ea6cd7c75cf6c03cadec2c369a8`.
It snapshots the exact DEC-041 row and its hash. The whole decisions file hash is creation provenance, not an immutable
child binding, so an unrelated future DEC row does not invalidate historical acceptance.

| Bound count | Value |
| --- | ---: |
| excluded source subject keys | 38,029 |
| excluded canonical keys | 38,027 |
| reserved zsRE candidate subjects | 6,000 |
| accepted zsRE training items | 3,000 |
| v3 raw MEND candidate records / unique primary subjects | 143,753 / 81,857 |
| historical prior-clear representatives | 58,498 |
| current v3 prior-clear direct survivors | 52,498 |
| strict-v3 old CounterFact candidates | 0 |
| conditional CounterFact remainder | 12,246 |
| distinct local fresh-source CounterFact candidates | 0 |

Join the v3 zsRE survivor index to the historical clear payload by `source_record_index`, verifying source and mapped
hashes and preserving index order. Never sample the historical 58,498 clear list directly: all 6,000 reserved subjects
remain excluded. “Prior clear” is a historical primary-subject review, not final teacher/context admission.

CounterFact's 12,246 conditional candidates remove 895 other-v3 exclusions from the nominal 13,141 remainder after
training reservation. Every candidate has only `old_eligible:counterfact` as its remaining exclusion reason. Reusing
it needs a **separate, explicit reason-specific exception**; the wrapper selects neither reading and admits neither.
DEC-041 itself does not grant that waiver.

Consumers must pin the wrapper hash externally and call `verify(path, expected_sha256)` before using child resources.
That verifies current child identities and guard semantics; it does not perform teacher eligibility, automatically
authorize sampling, or detect new exposures outside the bound historical register. Later exposures, including prose
containing candidate entities, require an attestation/review and a new register/binding when applicable. Never overwrite
this version to fold in new observations.

The CLI only creates a new repository output path:
`python -B -m scripts.r1_d1f_freeze_register --output manifests/revision_v1/exclusions_frozen_v3_recheck.json`.
No final examples were emitted; no sealed payload was read; no existing manifest was changed.
