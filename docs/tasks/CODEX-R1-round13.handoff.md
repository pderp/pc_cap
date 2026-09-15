# Codex round 13 handoff — 2026-09-15

No existing tracked files were edited, no commit was made, no GPU/real-base work ran, and no draw or seal occurred.
The clean driver profile was already complete when the three new src modules were created.
The latest owner HEAD observed was c7e9b62; the initial round snapshot was 58ffbf1.

| Lane | Delivered | Outstanding |
| --- | --- | --- |
| R1-D1h | v5 exclusion register, generator, tests; 4,489 MQ items / 4,218 subjects; all 43 bindings match | Actual alias/context/role clearance and owner draw integration; 169 MQ subject losses abort |
| R1-49d | Protocol v4, DEC-048 disclosure/objection, open final-reference rule, updated U01–U18 and profiles | Common-population reader selection, final matrix, cost and lead admission |
| R1-67 | dev_loader.py and selection_trace.py with CPU/TinyBase tests | Owner wires existing stream CLI/endpoints; two additional fixture cases need approved typo correction |
| R1-X11 | Review, reproducible metadata rehearsal, result/checkpoint/population/profile recounts and edit requests | Owner qualifies notes and probability/selection/profiling behavior |
| R1-68 | Record-digest index, immutable batched journal, clone-free checked RevisionCap immediate helper, verified checkpoint components | Not a completed alternate driver: mutation inventory, durable crash accounting, recipe/driver wiring, whole-cell all-endpoint resume parity and real-base profile remain |

Main findings:
- Historical mixed-recipe MQ locality collisions were 2.1–2.3% in the source-bound rehearsal, .43–.47% of
  all locality queries. The ≈13% statement assumes a different homogeneous pool. The fixed builder had zero
  collisions in the rehearsals; its unseen false fires nevertheless remain 30–52/100.
- Question-form nulls retain L2's balanced .5/.5 class masses while changing the null subclasses.
  Seed-0 unseen firing improves 30→5/100 with GS zsRE .98→.91, CF .86→.81, MQ .79→.55.
- Historical v4 and recent MQ streams share only 47/100 items. Final-reader selection requires common populations.
- The clean profile records 976.310 s inside phase timers; owner notes give 1252 s total. Different timer
  boundaries must remain explicit; an incremental speedup has not been measured.

Validation:
- Full revision-v1 plus package-layout CPU run: **552 passed, 8 skipped, 2 failed**, 70.97 s.
  [Log](../../logs/r1_round13/installed_cpu_before_fixture_permission.txt).
- Both failures are this round's test-fixture constructor typo, not a production-helper failure.
  [Corrected in-memory preview](../../logs/r1_round13/test_fixture_preview.json): 2/2 passed.
- Seven installed Python files pass Ruff. The 38 original round-13 tests and seven R1-68 integrity tests pass.
- Register bindings: 43/43 unchanged. Generated-document links resolve. Archived source snapshots preserve original
  relative links and are interpreted relative to their original paths.

**Permission pending:** apply only [R1-68-test-fixture-fix-v2.patch](R1-68-test-fixture-fix-v2.patch), one constructor
call in tests/revision_v1/test_r1_68_integrity_components.py, then rerun the affected tests. The patch passes
`git apply --check`. The first unversioned patch is malformed and must not be applied.
The question was submitted with the exact proposed correction; no answer was received at this handoff snapshot.

The source candidates and malformed first patch are retained as proposal history under the new-files-only rule.
Owner board/notes/result files and pre-existing untracked driver scratch remain untouched. No commit is requested
or authorized by this turn. Existing-file work and scientific integration gates are not marked complete.
