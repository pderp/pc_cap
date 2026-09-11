V3 independent review — 2026-09-11, Codex

The five V2 repairs are confirmed on the current working tree. The independent acceptance step requested in ongoing.md is complete. This finding does not authorize a production freeze or clear the separate B4/S7 issues.

Evidence: [fresh study](../results/V2/codex_v3/study.json), [provenance](../results/V2/codex_v3/provenance.json), [opposing outcomes](../results/V2/codex_v3/conflicting_outcomes.json), and [confirmation controls](../results/V2/codex_v3/confirm_tests.txt). The study ran in 6.05 seconds, entirely on CPU, from the new fixture root assets/tmp/review_repairs_r2b_20260911T111901819959Z. No real confirmation realization was opened. Model, tokenizer, evaluator and lease replacements are synthetic; the CLI, admission, stages, stream runner, snapshots and collectors are real.

The base commit was f3da69e8f409af7919740c8f7df7f899c3f2ae81 plus Claude's concurrent changes. The Python source-tree digest at study completion was 40218028898b94ac3cf53bcbf8e4de36cbcc05e5ffaa16833fff452a567a3c26. Per-file hashes cover the sources, driver, draft and confirmation tests before and after execution; none changed during that run. The three collector files also remained unchanged during the added control.

| Probe | V2 before | Independent result |
| --- | --- | --- |
| V2-01 BP parameter/tokenizer identity mismatch | Accepted, exit 0 | Both refused, exit 2 |
| V2-02 unknown experiment under a specific filter | Included: 2 runs / 16 rows | Excluded: 1 run / 8 rows, unknown-provenance note |
| V2-03 mixed experiments without a filter | Silent merge | All three analyses raise ValueError naming the IDs |
| V2-03 explicit experiment filter | 1 run / 8 rows / 1 order cell | Preserved; opposing outcomes stay isolated |
| V2-04 finite stage ceiling with no run allowance | Accepted, 7.2 seconds spent | Refused, exit 2; no output directory or charged work |
| V2-05 archived spending | 7.2 of 14.4 seconds counted | 14.400007 seconds, both attempts counted |
| Ordinary allowance: stage 25 s, run 20 s | Exit 0 then 5 | Exit 0 then 5 |
| Forced rerun with a different state | Archive control | Distinct endpoint hashes; old checkpoint bytes and old result directory preserved |
| S5 valid / missing arm / missing calibration / bad checkpoint | 0 / 2 / 1 / 1 | 0 / 2 / 2 / 2; no model construction in refusals |
| Real synthetic S4 pipeline | 150/150 jobs | 150/150 jobs |
| Code drift / explicit acceptance flag | 2 / 0 | 2 / 0 |
| Invalid order, realization, base, read or arm | Exit 2 | All exit 2 |
| Firewall denial | No payload read | Exit 2, zero payload reads |

The current draft generates 210 unique paths with the current path-helper API. Only the 150 synthetic editing jobs were executed end to end here; path uniqueness is not evidence of 210 model runs. Claude's real-base GPU identity evidence remains separately attributable to results/GPUWIN2/.

The expectation edits are appropriate. I compared the driver against commit 80ad746: negative inputs are unchanged; the positive synthetic freeze and fake tokenizer now report matching synthetic identities, as required by the repaired admission check. Replacing silent-merge expectations with refusals tests the intended behavior. The archived pre-V3 driver is byte-identical to the committed original (SHA256 f582172299bb8aa5654ed6c943e9af5744066c59f2f05df9fccb917ba8b0fb14).

The new [control driver](../scripts/review_repairs_r2d_study.py) plants opposite endpoint outcomes for the same eight items and the same C2 realization/order cell in two different experiments. Both initially acquire every item. Experiment A retains all eight; experiment B loses all eight. Resource views, paired rows, order-analysis inputs and the S7 CLI each preserve 1.0 versus 0.0 retention under the exact filter. The CLI records the selected experiment and reports zero versus eight lost items. All three unfiltered analyses refuse the mixture. A nonexistent experiment selects nothing.

One additional boundary remains: passing the same result root twice to s4_05.discover produces two per-run entries, while s4_05.views collapses them into one cell table without a refusal. This is a same-experiment duplicate-input issue, distinct from the repaired cross-experiment merge. The added evidence records two rows / one cell / no error. The collector owner should canonicalize repeated paths and refuse distinct directories representing the same experiment/dataset/arm/realization/order cell. Until then, use one non-overlapping root per analysis. This does not reopen V2-01…05.

Verification: tests/harness/test_confirm_cli.py — 16 passed in 20.52 seconds. The previous orchestrator report named 15; this review records the current file's actual result. Both study drivers exited 0. Source checksums, synthetic evidence and stdout/stderr are retained. No existing repository file, shared board row, lease, environment or Git index was changed by this review.
