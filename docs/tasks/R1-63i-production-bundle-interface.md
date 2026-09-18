# Production publication bundle interface — R1-63i

2026-09-17. No final production bundle has been emitted. **A producer that
assembles the whole final recipe/freeze package is still missing.** The existing
operator publishes and validates an owner-prepared bundle; it does not generate it.

## Existing producers and missing assembly

| Artifact | Producer / responsibility | Required state |
|---|---|---|
| Cleared role population | `scripts.r1_d9_receipts` clearance | Actual current exposure attestation and authorization. |
| Reserved edit/outside/near/revision groups and orders | D9 draw using `r1_d9f_allocation` | Signed RNG, fixed lead seed, DEC-062 mode and complete disjointness/Hall receipt. |
| Source-derived per-cell endpoint resources and independent population | `scripts.r1_d10c_endpoints construct` | Actual draw; no substitution or seed retry; fixed missing slots. |
| Sealed resources / payload inventory / analysis population | D9 seal | Valid current endpoint construction and exact seal authorization. |
| Typed resource costs | `scripts.r1_58h_cost_receipt` | Complete measured evidence and reviewed extrapolations, then exact lead signature. Pending v2 is not admission. |
| Final protocol JSON, executable final recipes, final matrix, recipe bindings, freeze JSON | **Whole-package assembler not implemented** | Owner must create and validate these from the actual signed receipts/sealed resources and pinned adapter identities. |
| Publication of approved bytes | `scripts.r1_58g_operator freeze` | Supplied bundle, exact request approval, schedule and U01–U18 closure receipts. |
| Execution | `scripts.r1_77_queue`, sealed backend `r1_77b_sealed_backend` | Final validated metadata, explicit process budget and live GPU lease. |

## Required publication inventory

The bundle JSON contains `artifacts` (source path/hash → unique new destination),
`matrix` and `bindings` references. Its byte-exact source files must already exist
under repository metadata paths. Publish resources under assets separately through
the authorized constructor/seal. The bundle must contain:

1. A schema-2 `stage4_final_protocol` JSON binding the D.1 protocol text and its
   normative closure, DEC-060 layout, DEC-061 family, DEC-062 allocation contract,
   max_new=32, DEC-053 equality, October 9 stop, closed gates and signed admissions.
2. Every executable admitted cell recipe: 360 core, or 405 when the extension is
   explicitly admitted. Preserve condition/dataset/realization/order coordinates,
   checkpoints, selected adapter/base/reader/calibration identities and exact
   sealed payload/expected-population bindings. Development recipes cannot be used.
3. Final executable matrix and queue recipe-bindings inventory with exactly those
   coordinates and admitted per-cell costs. Include process-budget and retry policy
   references; do not multiply the stored solo 1.5 padding a second time.
4. `manifests/revision_v1/frozen_stage4.json`, binding this sitting's protocol,
   cost and seal receipts, actual reservations/population, U01–U18 receipt map,
   installed source/backend/environment identities and final protocol.
5. Every new metadata dependency needed to resolve the preceding objects at its
   final path. Source bytes must contain final references before publication so
   their precomputed hashes survive byte-exact copying. Historical immutable
   dependencies can remain at their already bound paths.

Only new destination paths under `docs/tasks` or `manifests/revision_v1` are
accepted. The freeze manifest is published last. Post-publication validation calls
the actual queue/backend; caught failure removes only this transaction's new
files. Machine-crash recovery still requires reconciliation. No recipe, receipt,
signature or close-out evidence is inferred from this interface document.

## Pending work that cannot be relabelled as signatures

Four R1-64f endpoint runs are not measurements until executed. Full-validation
cost evidence and per-process host peaks remain absent from the typed receipt;
the 6 GiB available-memory floor is a different quantity. Some U03 and population
gates also require substantive evidence/operations. The missing package assembler
is implementation work. Candidate v12 must report these facts and cannot truthfully
print `signatures_only: true` while they remain.
