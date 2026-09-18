> Historical scientific-review handoff. DEC-068/069 and the later locality approval are now incorporated into D.5; see [the current R1-63o record](R1-63o.md) for implementation, validation and handoff. The earlier pending items below describe that earlier review state.

# R1-63o and scientific-review handoff — September 18, 2026

**Scientific review complete; R1-63o package issuance remains open.** Charlie broadened the task to an independent programme review, then explicitly prioritized scientific structure and approved decisions over signing mechanics. Claude is idle for this review. The main deliverable is [Scientific programme review](../scientific_program_review_2026-09-18.md).

## Scientific findings to discuss before issuing the next package

1. DEC-057's installed three-realization percentile intervals collapse to the observed realization range, both at 97.5% and the adjusted 99.9206% label. An independent symmetric-error counterexample has 75% coverage. The report proposes resolving the interpretation before outcomes; no inference method or classifier was edited.
2. Consider amending DEC-051 to finish primary/random/stable across all three realizations first. The proposed 135-cell milestone costs about 147.83 expected process-hours, versus 283.14 for completing the current 225-cell first-four-block milestone. Same final 285 core cells; no scope change, scheduling change or draw was applied.
3. Keep the scientific claim at package effectiveness unless controls isolate the claimed cause. Retain U03's historical-compute qualification, the reduced MQuAKE scope, visible fidelity failures and the κ null. The report gives the remaining population, tail, stress and composition limitations and a deadline-oriented work programme.

New evidence is under `logs/scientific_review_20260918/`. The diagnostic script independently recounts all four saved development vectors and probes the installed inference function; it loads no model. All 31 source bindings and all 20 document links were checked. Targeted regression: **135 passed, one skipped**, `logs/r1_63o/existing-tests.txt`; the skip is a live-session-sensitive test. Ruff passes both new scripts.

## Operational work completed before the scientific redirection

The new read-only `scripts/r1_63o_graph.py` inventories explicit path/SHA JSON records and path-keyed SHA maps, hashes other resources as opaque bytes, and refuses protected targets. It does not rewrite provenance. The corrected inventory is `logs/r1_63o/pre-refresh-scan-v2.json`: **3,158 resources, 71 stale-or-protected edges** from inputs v10. This differs from the orchestrator's 93-resource inventory because the traversal/counting rules differ; neither count represents 71/93 scientific-result failures. The initial scan JSON is superseded: it misclassified a path/SHA object in a named SHA field and some named content identities as path maps.

Three concrete implementation issues deserve resolution before final package construction:

- `scripts/r1_d10c_endpoints.py` removes `identities` from construct's stdout, while `scripts/r1_58g_operator.py` accesses `dry['identities']`. The source-level interface mismatch is clear; the existing real step-6 refusal occurs earlier at stale role-plan bindings. A full corrected CLI/operator rehearsal is still needed.
- The operator records nested D9 blockers in `dry_run` without propagating them to its outer `blocked` list. Ignore only the precisely expected unsigned current authorization during preview; other errors must remain execution blockers. This repair has not been applied here.
- `scripts/r1_49n_protocol_matrix.document()` refreshes `analysis_implementation` but inherits a stale `classifier.implementation` binding. A fresh matrix must bind those current implementations consistently without changing the classifier's mathematics.

There is also a real distinction between an **active execution dependency** and **historical provenance**. `r1_d1i_register_v6.verify_register()` deliberately reconstructs the approved v6 register from an exact v5 parent; the parent retains a superseded live decisions hash, explicitly described as historical. Blanket recursive replacement or hiding historical JSON in opaque archives would not prove the current package correct. Define and audit the two roles explicitly. Preserve historical bytes and measured recipe/result identities; regenerate active declarations. Do not call an unqualified all-history traversal clean when it is not.

Cost file version v5 can retain the supported typed `receipt_revision=4`: filename/package revision and validator schema revision are different. The current validator does not accept typed revision 5. The numerical costs and approved transfers need not change solely for provenance repair.

## Remaining R1-63o work

After any scientific decisions are resolved, repair the active interfaces and complete the requested versioned role/evidence/matrix/runtime/cost/input/form/candidate/operator package in one pass. Validate native consumers and the explicitly defined live dependency graph; list and lock every bound implementation after those repairs. Then Claude can perform the authorized fresh session, with X20 after genuine step 8. No candidate v15, inputs v11, new role-plan/evidence release, forms v10 or frozen tree is claimed by this review.

No pre-existing file was changed in this turn. Earlier dirty report work was preserved. New test fixtures/logs were created by the regression suite under its established repository paths; its metadata rehearsals are synthetic. No real signatures, new experimental draws, protected payload reads, GPU runs, services, sibling-repository changes or commits were performed. The initial claim's in-progress state is superseded by this explicit handoff for current status; no global task board was edited.
