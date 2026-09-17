# R1-D9e — round26

Status: done.

Agent: Codex. Round26, CPU only. No staging/commit, GPU work, actual draw, real seal, freeze or lead signature. Source/base/driver/backend and Claude's chain Q outputs were not edited. Resources are under `assets/runs/pc_cap/R1/r1_d9e/round26_final/`.

Inputs: DEC-061, certified post77d teacher/evidence, original D10a source pools and role policy.

Outputs: `scripts/r1_d9e_near_family.py`, `scripts/r1_d9e_review.py`; constructor, seal validator,
receipt binding and analysis updates; `logs/r1_round26/near_final/r1-d9e-real-pool-review.json`;
new source-bound roles/joint evidence and deterministic diagnostic resources in assets.

Pairing is recomputed from source-reserved records, with exact relation/template family,
different subjects and first-unused lexical neighbour. Missing planned slots remain named.
Analysis recomputes bounded equality against the actual cap-off neighbour baseline; failed
support acquisition never filters cases. Receipt forms explicitly bind the adopted family.

Real-pool counts unchanged:6084/6121/2161 usable subjects; all93 Hall checks pass. The lexical
600-subject convenience samples per dataset yield61/300zsRE,210/300CF,221/300MQ matches.
Those are diagnostic availability counts, not final reservations or unbiased forecasts.
There were no RNG calls, model calls, actual draws or seals in this pool review.

Verify: source/family/missing/bounded-score tests;107-test regression; full actual-cadence
synthetic producer→seal→TinyBase→analysis rehearsal (300and1000) passed before adding explicit
receipt-family assertions; final explicit-contract run passed both tests in254.32s, logged in final-contract-rehearsal-tests.txt.
Historical evidence producer bytes are preserved with original SHA; no historical result was
rehashed to pretend it used current code. `near_final/` is operative; the earlier review is
superseded only for the helper's import-order cleanup, not numerical changes.

Done-when: adopted semantics enforced and synthetic plus real-pool dry paths exercised.
Cost:0GPU seconds. Initial full synthetic rehearsal259.69sCPU wall; final timing in test log.
Deviation: real-pool diagnostic uses deterministic nonauthorizing convenience groups, not
admitted role RNG or a real draw. Missingness can be substantial, especially for zsRE.
Unresolved: final drawn pair availability, signatures and current-exposure attestation.
Questions for lead: none; do not resample to improve missingness.
