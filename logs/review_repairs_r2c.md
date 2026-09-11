# V3 — the V2-01…V2-05 repairs, re-checked with the unchanged negative inputs

Written 2026-09-11 07:05 EDT by the orchestrator (the lead asked the orchestrator to proceed with V3 while Codex
is paused; Codex's independent re-check of the same fixture remains the acceptance step named in
`docs/updated_plan7.md` §2). Tree: commit `f5d3810` plus the repairs below; `src/pccap` tree sha `98215f4a…`
(`results/V2/v3/provenance.json`). All CPU; no production freeze, sealed payload or GPU touched.

## Repairs (production code)

| finding | repair | where |
| --- | --- | --- |
| V2-01 loaded BP/tokenizer identity never compared with the freeze | `pccap.harness.identity.check_frozen_identity` at confirm-mode stage entry: BP parameter digest (`base.checksum()` vs `base_checkpoints.bp.param_digest`), tokenizer file hash (`GPT2Tokenizer.file_sha256()` vs `tokenizer_rev.tokenizer_json_sha256`), grammar weights file hash (`dataset_ids.grammar["grammar_base.npz"]`), ePC checkpoint hash; an absent frozen identity or an artifact that cannot report one is refused too. Refusals are `PreflightRefusal` → run status `refused`, exit 2, before any edit or evaluation; a refused attempt leaves no results and may be retried without `--force` | `harness/identity.py`, `stage_s4.py` (both branches), `stage_s5.py`, `runner.py`, `records.RunStatus.refused`, `data/tokenize.py` |
| V2-02 runs with no `experiment_id` matched a specific filter | a specific filter requires the exact id; unknown-provenance runs are listed in the collector notes and excluded | `analysis/s4_05.discover`, `s4_06.collect_rows`, `s7_03.load_runs` |
| V2-03 unfiltered analysis merged two experiments silently; S7-03 CLI had no filter | without a filter, more than one experiment id under the root raises (`collect_rows`, `load_runs`, `s4_05.views` via `require_one_experiment`); a duplicate (realization, order) cell raises; `--experiment-id` on the S7-03 CLI; the resource views and the S7 report record the experiment id | same modules |
| V2-04 finite stage ceiling with `run_allowance_seconds = None` labelled enforced | refused at admission (exit 2, no run directory); with both set, the run's stop allowance is recorded as `effective_run_allowance_seconds` (= the run allowance; admission already guarantees the remaining stage budget covers it) and the stages stop on that value | `runner.py`, `stage_s4._allowance`, `stage_s5` |
| V2-05 archived attempts excluded from stage spending | `_stage_spent_seconds` sums every attempt, superseded or not; analysis still excludes superseded results | `runner.py` |
| (V2 note) S5 malformed inputs exited 1 | missing arm / calibration / checkpoint-hash mismatch raise `PreflightRefusal` → exit 2, still before any model construction | `stage_s5.resolve_frozen_arm` |

## Re-check with Codex's study driver

`scripts/review_repairs_r2b_study.py` was rerun from a fresh fixture root
(`assets/tmp/review_repairs_r2b_20260911T105536449721Z`), output in `results/V2/v3/`. The driver's *inputs* are unchanged;
its *expectations* were updated to the repaired behaviour and the synthetic freeze now binds the synthetic base and
tokenizer identities (`param_digest = "synthetic-weight-hash"`, `tokenizer_json_sha256 = "synthetic-tokenizer-hash"`),
which the V2-01 repair requires for the positive runs. The pre-V3 driver is preserved byte-for-byte as
`results/V2/review_repairs_r2b_study.pre-v3.py` (hashes in `provenance.json`). Exit 0; 2.9 s.

| probe (unchanged input) | before (V2) | after (V3) |
| --- | --- | --- |
| 150 scheduled synthetic S4 jobs through the real CLI/stage/loader/collectors | 150/150 | 150/150 |
| `bp_frozen_digest_mismatch`, `tokenizer_frozen_hash_mismatch` | exit 0 | **exit 2** |
| two experiments, unfiltered `collect_rows` / `load_runs` / `views` | 16 rows / 1 cell / 1 cell (silent merge) | **ValueError naming both ids** |
| two experiments, filtered | 1 run / 8 rows / 1 cell | 1 run / 8 rows / 1 cell |
| legacy run with no id under a specific filter | 2 runs / 16 rows | **1 run / 8 rows** + an "unknown provenance" note |
| stage 0.01 s, run allowance None | exit 0, `enforced = true`, 7.2 s charged | **exit 2, no run directory, 0 s** |
| ordinary stage allowance (25 s, run 20 s) | 0 then 5 | 0 then 5 |
| forced rerun with distinct state, two attempts | runner counted 7.2 of 14.4 s | **14.4 s counted**; old result dir and checkpoint bytes preserved |
| S5 valid frozen authority / missing arm / missing calibration / bad checkpoint | 0 / 2 / 1 / 1 | 0 / 2 / **2** / **2**; no construction event in any refusal |
| code drift refused / accepted with the flag; schedule and base/read negatives | 2 / 0; all 2 | 2 / 0; all 2 |

## Unit controls added (`tests/harness/test_confirm_cli.py`, 15 controls in the file)

`test_v2_01_frozen_identity_check`, `test_v2_01_stage_refusal_maps_to_exit_2_and_is_retryable`,
`test_v2_02_specific_filter_excludes_unknown_identity`, `test_v2_03_unfiltered_mixed_experiments_are_refused`
(incl. the S7-03 CLI flag), `test_v2_04_stage_ceiling_without_run_allowance_is_refused`,
`test_v2_05_archived_attempts_count_toward_stage_spending`.

CPU suite: 344 passed, 5 skipped, 1 failed — the failure is the PC-10 gate (`test_pc10_parity`), which is
Codex's Lane B4-S under DEC-020 and unrelated to these repairs. Lint clean.

## Boundaries

The identity check is exercised with synthetic bases and tokenizers; the production values it compares are the
digests the freeze writer already records (`base_checkpoints.bp.param_digest`, `tokenizer_rev.tokenizer_json_sha256`,
`dataset_ids.grammar`). A GPU smoke of one confirm-mode job against the real BP base is part of the orchestrator's
GPU test window before the freeze. The 210 scheduled paths of the current draft are still checked for uniqueness only;
grammar confirmation execution is exercised by `tests/harness/test_grammar_stream.py`, not by this study.
