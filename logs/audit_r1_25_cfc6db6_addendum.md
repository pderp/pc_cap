# R1-X2 addendum — concurrent commits f95606a and cfc6db6

2026-09-14. Read together with `logs/audit_r1_25.md`, which records the earlier `e9c22c4` snapshot. Claude committed new results and a class-balanced retrieval loss during the final source checks. No existing audit or manifest was edited; this addendum records the delta.

## What changed and what was checked

At `cfc6db6`, `LossConfig.balance_null=True` gives record-target and null-target queries half the retrieval-loss weight each, averaging within each class. If either class is absent, the function falls back to a uniform query mean. Both BP and ePC callers pass the same flag. `featurize` now adds own-prompt supervision only for the **new** support by default; all-history own prompts require `own_prompt_history=True`. The earlier five-own-prompt audit count is therefore historical; the new default count is **one** for that fixture.

New `tests/revision_v1/test_r1_x2_class_balance.py` checks class-mean arithmetic, invariance to repeating one entire class, finite single-class fallback and explicit history opt-in. Three tests pass. The six existing train/reference and ePC-surrogate tests were rerun after this change: **6 pass in 18.33 s**. Full current-code audit controls were rerun to `logs/r1_round3/r1_25_controls_cfc6db6.json`; source hashes before/after match and the previously reproduced memory, delta-selection and query-boundary defects persist.

This is a useful correction to the relative influence of null supervision. It does not supply normalized answer/preservation losses, training through the deployed delta adaptation, the differentiable fast unroll or a base-update phase. The loss-source table still needs the new role population and L2 class denominator documented. Within-episode balancing also differs from calibration under the much larger ordinary-query population; measure false firing at deployment prevalence rather than interpreting balanced logits as calibrated probabilities.

## New completed evidence, distinct from the active retrain

Commit `f95606a` records the completed combined pairwise-null/own-prompt reader at null threshold .5:

| Development stream | ES | RET-ES | RET-GS | LS |
| --- | ---: | ---: | ---: | ---: |
| zsRE | 1.00 | 1.00 | .61 | .14 |
| CounterFact | .96 | .97 | .28 | .20 |

Source: committed `results/R1/stream_eval_pairown_delta5_null0.5*.json` and `docs/R1_stage2_notes.md`. These results show that own-prompt rejection has largely been removed. CounterFact RET-GS exceeds the random-reader reference .18, but locality remains far below a usable gate. Lowering the threshold to .15 raises CounterFact LS to .54 while reducing ES to .62; the threshold sweep does not establish joint non-inferiority. These are selected development outcomes, not confirmatory evidence.

The newly launched `cf_pool3k_pair_own_bal_400` remains Claude's active lane and was not run, altered or preempted here. The recommendation to test scope rejection separately from similarity and answer writing remains appropriate, now with the class-balanced run supplying the next bounded comparison. Do not pool its training budget with its predecessor without an explicit treatment/lineage decision.

## Continuation-manifest handoff

The original `manifests/revision_v1/r1_24_control.json` correctly failed its source-integrity check after the two training files changed. It remains preserved as the `e9c22c4` preparation record. A **new** dry-run manifest, `manifests/revision_v1/r1_24_control_v2.json`, binds the `cfc6db6` source tree. This version still selects the same completed `cf_pool3k_pairnull_400` checkpoint and 493,752 reported learning tokens; it does not silently switch to the newly finished own-prompt checkpoint or the active balanced run.

Use the v2 manifest explicitly for any scheduled reported-ledger diagnostic. Exact-budget preparation requires another **new** output path, such as `manifests/revision_v1/r1_24_control_reconciled_01.json`, and actual pass-count reconciliation evidence. The illustrative v2 filename in the original R1-24 task document is now occupied and will correctly refuse overwrite. Neither manifest authorizes GPU use during this CPU lane, and neither fixes the underlying ledger incompleteness.

No Codex edits or commits were made to the concurrent source changes. They were ingested and checked read-only.
