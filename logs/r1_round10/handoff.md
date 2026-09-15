# Round 10 handoff — CPU lanes

Codex picked up every lane in docs/ongoing.md: R1-D1g, R1-60, R1-61 and R1-57b. All new implementation and report artifacts are present. Two functional repairs and six import-grouping changes are prepared but **unapplied**, because the user requires permission before changing any existing file.

## Lane status

| Lane | Delivered | Remaining |
| --- | --- | --- |
| R1-D1g | Reason-specific CounterFact exception, v4 register, current MQuAKE exposure supplement, child-hash checks and cross-dataset counts | Lead population-policy review; a new supplement binding after the proposed import-only producer edit |
| R1-60 | Direct three-question composition evaluator, TinyBase tests, membership rule, exact expectation formula and candidate-graph audit | Owner admission of a feasible population and composition inventory; real-base validation |
| R1-61 | Nine comparator configurations, one-cell execution, all checkpoints/assays, immutable outputs, verified resume and CLI/template | Apply tested fixture repair and import cleanup; owner real-base timing, resource ceiling and launch validation |
| R1-57b | 360-cell inventory, separate 45-cell v2 extension, missing-cell accounting, secondary summaries and 15-cell development dry analysis | Apply tested missing-path compatibility repair and import cleanup; final admission/multiplicity bindings |

Detailed subtasks, validation and interfaces are in docs/tasks/R1-D1g.md, R1-60.md, R1-61.md and R1-57b.md.

## Validation and permission boundary

- Full revision CPU suite: **403 passed, 8 skipped**, in 62.66 seconds, with the two proposed functional repairs applied **only in memory**. Evidence: full_cpu_pending_repairs.txt and full_cpu_pending_repairs.json.
- Package layout: **59 passed**.
- New code passes Ruff with explicit first-party grouping; default repository Ruff identifies six import-only differences. Their prepared patch passes the default check on the corrected text.
- Installed files remain unpatched. There are three known new test failures without the functional repairs; the passing preview is not an installed-tree pass.
- Exact changes: [edit request](../../docs/tasks/R1-round10-edit-request.md), with three patches. No task-board, lead-queue, ongoing-plan, owner result, source-repository, or existing code/document file was edited.
- CPU/TinyBase only. No real-base or teacher execution, GPU job, fresh draw, sealed payload access, seal, staging or commit.

The original register remains a snapshot of pool v1. Claude subsequently created the 1,000-item MQuAKE training pool v2; the **separate** supplement captures that newer exposure without overwriting v4.

## Main research finding: population capacity

| Current supplement | Candidate items | Distinct candidate subjects | Proposed distinct-subject demand |
| --- | ---: | ---: | ---: |
| zsRE | 52,411 | 52,411 | 4,050 |
| CounterFact | 12,246 | 12,246 | 4,050 |
| MQuAKE | 2,171 | 2,100 | 4,050 |

The MQuAKE deficit is **1,950 subjects** under conservative reservation of all declared training/development locality and unrelated-query lists. Three disjoint 1,000-edit streams alone exceed this capacity. These counts distinguish subjects from facts and include all currently reserved pool versions.

The 1,200 primary training/development subjects alone would leave 4,218 subjects after the overlap rule, but that ceiling does not account for the query reservations. The supplement reserves 2,106 locality subjects and 990 unrelated-query subjects, with overlaps across categories; the full new-exposure union is 3,405. It does not claim every reserved query was actually executed.

The requested zsRE-priority rule is preserved. Its original scarcity rationale is now questionable: MQuAKE is the limiting source. Reversing priority could recover at most the 72 shared subjects not already excluded by query exposure (159 minus 87), far short of the deficit; such a change still needs lead approval and rebinding.

Potential next work that requires no GPU is an audit of immutable training/evaluation recipes, RNG schedules and query traces to distinguish executed queries from unused reservations. Release is a separate lead decision; lack of a trace is not proof of non-exposure. Other options are an approved additional source or an explicitly revised design. Do not silently shrink the accepted full scope, reuse exposed facts or count multiple facts about the same subject as independent fresh subjects.

## Composition coverage

There are 9,218 source cases. The current supplement leaves 1,087 with all dependencies among current candidates: 832 need one changed fact, 244 need two, and 11 need three. A multi-hop question can need only one edited fact.

These are candidate-graph ceilings. Cases can attach to a realization only when all dependency edits are actually in that realization. Source-unavailable cases and excluded dependencies are explicit categories. Final expected attached-case counts remain unavailable because the registered role allocation is infeasible and its unique-subject representation/quotas are not admitted.

## Development observations

The [development table](analysis_development_dry_run.md) and [JSON](analysis_development_dry_run.json) are **NOT CONFIRMATORY**. Thirteen of fifteen declared development cells have complete primary metrics. Historical MQuAKE v2/v3 entries stay missing. None satisfies any of the 360 fresh cells.

The three-source reader has MQuAKE RET-GS 0.80/0.47/0.82 across seeds, with LS 1.00/0.98/0.98. CounterFact RET-GS is 0.66/0.85/0.83 and zsRE is 0.98/0.97/0.98. Immediate ES and retained ES are 1.00 for those cells. These are the same development populations reused across reader seeds, so there is no independent-population confidence claim.

Claude's newer threshold investigations and larger-pool retraining are different conditions. They are outside the independently declared dry-run inventory and should not overwrite these results. The historical two-source reader weights also remain distinct from the newer three-source weights; the final condition must bind its actual chosen checkpoint.

## Owner sequence before a real run

1. Approve/apply the prepared repairs, then validate the installed files and publish a new supplement binding for the changed producer hash.
2. Resolve MQuAKE capacity and all remaining exposure, alias/context and source-admission gates.
3. Bind the final reader, thresholds, calibration, original/continued bases, resources and protocol. Keep S1 locality relative to the original base and unseen effects relative to its own cap-off base.
4. Construct and independently admit challenges, outside prompts, drift windows and ordered stream memberships. A fact-reservation content seal alone is not a scientific launch seal.
5. Decide whether to allocate the additional 45 v2 cells. The registered core remains 360.
6. Validate the one-cell driver on the real base with a resource lease and agreed watchdog/ceilings, then check its reports with the analysis reader.
7. Profile the actual new driver before extrapolating time. It performs sequential scoring, repeated integrity checks, cloning and many immutable phase-file writes; the earlier component timings do not measure this implementation.
8. Freeze and launch only after those conditions are satisfied. Sum costs across all attempt directories for resumed cells; the final attempt's ledger is not the whole run's cost.

Test-generated phase logs under driver_tests are synthetic execution evidence, not research outcomes. Snapshots and temporary resources are under assets. Hash-bound source evidence and the initial source snapshot are retained under this log directory.
