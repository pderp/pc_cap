Status: V3 and Lane X reviews complete; B4-S partially complete, integration awaiting permission; S3-01 conditional work blocked.

Agent: Codex. Round started from f3da69e; Claude committed b9f03af during the round. Source hashes in each audit bind the actual reviewed working tree. No subagents, GPU use, environment installations, sibling-repository changes or Git commits by Codex.

Inputs: docs/ongoing.md, updated_plan7.md, DEC-020, the plan PDF (D.4/D.9), V2 repair code/reports, fixed GRACE reference artifacts, published P4, S7 inventory and E.2 selection, and subject-only projections of the unsealed source-pool inventories.

| Lane / checkpoint | Result | Evidence / remaining action |
| --- | --- | --- |
| B4-S: preregister conditioning rule | Done before execution | B4-S-sensitivity-policy.json |
| B4-S: 20 cases, steps 1/10/100, both perturbations | Done; inconclusive magnitude | logs/grace_sensitivity_round3.md; sensitivity.json |
| B4-S: PC-10 form (b), isolated and sequential | Not cleared | Required divergence class was not reproduced; keep diagnosing |
| B4-S: vmapped queries, ragged input order, original prompt boundary | New helper implemented and exercised | grace_batch.py; 20-case/61-prefix scalar comparison passes |
| B4-S: full state/learning continuity and query accounting | Candidate verified | Four in-memory corrected controls pass; existing file still has two test failures until approval |
| B4-S: canonical integration / adapter re-export | Prepared, unapplied | B4-S-batch-edit-request.md (five files) |
| B4-S: reference label / task-board completion | Withheld | Requires the scientific gate; no tolerance or status edits |
| V3: fresh full synthetic study | Done | 150/150 editing jobs; 16 confirmation controls pass |
| V3: opposing outcomes under two experiment IDs | Done | Exact filters preserve 1.0 vs 0.0 retention; all unfiltered analyses refuse |
| V3: independent report / expectation review | Done | logs/review_repairs_r2d.md |
| Lane X: fresh P4 seed block, n=2048 | Done | logs/p4_s7_review/P4_gram.json and comparison |
| Lane X: S7 subject separation and E.2 order | Done | s7_audit.json; all nine selection-order checks pass |
| Lane X: D.9 counterexamples / review | Done, repair findings handed off | logs/review_p4_s7.md |
| S3-01 full control table | Not started | Depends on B4-S step 2; a passing table would be inaccurate now |

Outputs: see CODEX-round3-20260911.outputs.json for the new-file inventory and hashes. Shared source/manifests/boards were not edited. The untracked results/tests/baseline_smoke/B4 subtree belongs to Claude, not this work.

Verify commands: active ../venv/bin/python -B; process-local CPU flags, two BLAS/OpenMP threads, no bytecode, no pytest cache and fresh assets/tmp fixture directories. V3: scripts/review_repairs_r2b_study.py, scripts/review_repairs_r2d_study.py, pytest tests/harness/test_confirm_cli.py. B4: scripts/grace_sensitivity.py, scripts/grace_batch_smoke.py, and PYTHONPATH=. scripts/grace_batch_candidate_check.py. X: scripts/review_p4_fresh.py and PYTHONPATH=. scripts/review_s7_inventory.py. Exact output namespaces and commands are in the lane reports and patch request; do not overwrite retained run evidence.

Verify output: V3 drivers exit 0; 16 confirmation controls pass (20.52 s). B4 sensitivity completes but does not qualify; source batch smoke passes (3.49 s), corrected/integrated candidate smoke passes (3.36 s), and four corrected candidate controls pass. As-created GRACE tests remain 7 passed / 2 failed due solely to the prepared ledger-API test correction; no false claim of a green working tree is made. P4 and S7 audit exit 0. Eight new Python files pass Ruff.

Cost: GPU seconds = 0 throughout. Principal CPU elapsed times: sensitivity 98.33 s; P4 265.77 s; V3 study 6.05 s; confirmation tests 20.52 s; original GRACE test attempt 1.40 s; full-size smoke 3.49 s plus candidate smoke 3.36 s. Some work ran concurrently, so these are per-operation elapsed times, not an overall elapsed-time total. Ledgers and stdout/stderr remain in the new artifacts. No shared cost log was appended.

Deviations: negative sensitivity result is retained. The first S7 audit command lacked PYTHONPATH=. and failed at import; the corrected invocation passed, without a source edit. Two new test controls used the wrong ledger API; a concrete three-line correction was requested and validated in memory while awaiting permission. The broader five-file integration request retains scalar comparison oracles.

Unresolved / handoff:

1. Codex can next localize B4's first cross-framework gradient difference; output agreement alone does not satisfy DEC-020. The existing control table must not call B4 complete.
2. Claude owns S7 repairs: average damage over Q_i, propagate GRACE original prompt boundaries, replace the grammar probe block that overlaps P4 before S7 outcomes, and qualify natural-language stratum labels. Reuse the two synthetic audit counterexamples as regressions.
3. Claude can harden s4_05 against duplicate roots/same-experiment duplicate cells; this is distinct from the five repaired V2 issues.
4. The lead's freeze/availability decisions remain separate. V3's independent acceptance is now supported; B4 availability is not.

Questions for lead: permission is required to apply B4-S-batch-edit-request.md. This is the only requested edit set from Codex this round; no S7/shared-board changes are included, and no commit is requested.
