# Codex round 17 — completion and owner handoff

2026-09-16. All six currently assigned lanes have reviewable deliverables. **Two existing-file edits await user permission.**
Only the driver and its tests were edited under the explicit R1-68d permission in ongoing.md. Everything else is new.
No GPU/real-base execution, final draw, sealed payload read, freeze, staging or commit was performed by Codex.

## Lane status

| Lane | Delivered | Remaining boundary |
| --- | --- | --- |
| R1-68d | Applied driver repair, legacy snapshot/diff, seven CPU driver tests, both source-bound successor recipes | R1-74 landing and unmocked loader check; owner real-base re-profile |
| R1-74 | Exact source patch, tested preview, rescoring script/report, fourteen tests | User permission to apply source patch after profile coordination |
| R1-75 | Cell-directory analysis/CLI, independent dev matrix, JSON/Markdown results, five tests; all405 draft cells explicitly missing | Optional inventory helper's two-line hash-format repair awaits permission; existing analysis reproduction works |
| R1-40c | Matrix v5, generator/strict validator, three tests, freeze audit | Final costs/calibration/populations/admission/freeze are owner gates |
| R1-49e | Protocol draft v5, all18 gates, explicit inequalities/denominators, DEC-050–053 and change log | Q4/Q5 and U12/U13/U14 lead decisions remain open |
| R1-76 | Fixed-outside runner, six tests, prepared zsRE/CF specs/resources, MQuAKE capacity memo/audit | No experiments run; owner execution and MQuAKE Q10 remain separate |

The old R1-63c fragment at the end of ongoing.md refers to completed round16 work and was not repeated.
The old R1-40c task record belongs to another round; this lane's new record is [R1-40c-round17.md](R1-40c-round17.md).

## Verification

**582 passed, 8 skipped, 11 subtests passed in88.61seconds**, CPU revision suite:
[full output](../../logs/r1_round17/revision-tests.txt). All16 new/changed Python files pass Ruff:
[lint](../../logs/r1_round17/lint.txt). git diff --check and both proposed patches' git apply --check pass.
New protocol/memo/report links resolve. The scoring source remains byte-for-byte at its pre-patch SHA256.

Recipe preparation additionally verified the exact hypothetical post-patch code identity without changing files.
Both live loaders currently refuse the prepared recipes with “installed development code identity mismatch,”
as required. The preparation and capacity scripts made no model calls.

## Permission requests and immediate owner sequence

1. [R1-74 edit request](R1-74-edit-request.md), exact [scoring patch](R1-74-stage4_assays.patch):
   bounded equality primary, terminated/truncation counts alongside.
2. [R1-75 helper request](R1-75-inventory-hash-edit-request.md), exact [hash-format patch](R1-75-inventory-hash.patch):
   match the driver's row_hash encoding. The corrected version was validated in memory and used to prepare
   the saved independent analysis matrix. The on-disk helper remains unchanged.

These await permission because the user's rule covers every existing file, including files newly created this turn.
No permission is inferred from a prepared recipe or patch.

After approval and confirmation that an owner profile is not using the installed tree: verify the R1-74 before hash,
apply its exact patch, verify the after hash, run scoring tests against the landed source and check both real recipe
loaders. The recipes already bind that exact successor, so no rewrite should be necessary if no other source drifts.

[Prepared recipe identities](../../logs/r1_round17/R1-68d-recipe-preparation.json):

- Full: R1-68d-zsre-v5-full.recipe.json, SHA256 baa35ac96f2f4043d7927d281d9ab46356a7a69959a28aca82e043f08bd3ba85.
- Incremental: R1-68d-zsre-v5-incremental.recipe.json, SHA256 fceb3d2986a26b253c44511fd59918d84f1fa25c6769cd6c9f87383b32040b68.
- Expected installed code: 51263d99ad957c58cd7ac5e56acc6ae904dbdbaec0c49e7ac203ffaf777beb8f.
- Expected scoring source: af4b050dfeaa165c8d4af9ab8893322a6e22421d32baec5f21cdd66f8a9b89b5.

The owner can then re-profile and rebind comparator recipes/calibration as needed. Matrix v5 costs remain null
until the September20 measurement/admission. Freeze candidate v4 must be replaced; its strict audit detects the
driver change and retains every open scientific gate.

## Findings to carry forward

- CounterFact locality is49/50 bounded vs36/50 terminated; near-miss100/100 vs63/100.
- The bound zsRE driver cells have no near-miss/revision rows despite100/50 planned cases; those rates are unavailable.
  Separate endpoint reports cannot fill them. Newer R1-68c ES299/300 is also not silently substituted for the
  older development cell's300/300.
- Drift means conceal localized harm: positive-part ES99≈.220nats zsRE and.638nats CF; maxima8.686/7.315;
 17/52 positions exceed.1nat. This is empirical tail evidence, not a fitted power-law claim.
- Prior10/12/9% zsRE occupancy rates used different outside sets. The new fixed-outside design is prepared,
  unexecuted, and reports missing actual target occupancy honestly.
- [MQuAKE memo](R1-76-mquake-occupancy.md): current sources yield100 eligible rows; historical already-reserved
  sources contain700 metadata-eligible rows outside selected training/exact queries. That may support a separately
  approved100/300-only diagnostic, but the full1,100-row design is400 short. Even all168 nominal register slack
  would leave232 missing. Do not spend final-register headroom to claim that this closes the gap.
- October9 is the experiment stop. October10–14 is presentation preparation. DEC-052 requires complete-block
  and explicit incomplete-cell reporting if the full matrix cannot finish.

## Files and coordination

Detailed task records: [R1-68d](R1-68d.md), [R1-74](R1-74.md), [R1-75](R1-75.md),
[R1-40c round17](R1-40c-round17.md), [R1-49e](R1-49e.md), [R1-76](R1-76.md).
Main artifacts: [protocol v5](../R1_stage4_protocol_draft_v5.md),
[matrix v5](../../manifests/revision_v1/run_matrix_v5.json),
[development analysis](../../logs/r1_round17/R1-75-development.md),
[draft inventory](../../logs/r1_round17/R1-75-draft-matrix.md).

TinyBase/failure fixtures created additional new directories under results/R1/r1_75_cpu_tests,
results/R1/r1_76_cpu_tests and results/R1/stage4_dev_cells/r1_68c_cpu_tests. Snapshot resources and prepared
occupancy populations are under assets. None of the existing logs, status board, lead queue, task claims,
historical recipes/results or sibling repositories were edited. The lead handles status mirroring and commits.
