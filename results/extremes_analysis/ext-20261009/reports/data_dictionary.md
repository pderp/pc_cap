# Data dictionary — ext-20261009

All losses are natural-log units (nats). Missing values are empty/NaN, never zero. Every table carries the observation
unit in its `family` column; percentages carry numerators and denominators.

## Identifiers and families

| field | meaning |
|---|---|
| `dataset` | `zsre`, `counterfact`, `mquake` |
| `model` | `frozen`; `bp_reader_s{0,1,2}`; `epc_reader_s{0,1,2}` (families FROZEN, PCR/EXT). In paired tables the short names `frozen`, `bp0..2`, `epc0..2` are used |
| `horizon` | memory checkpoint in edits: 100 or 300 for readers; 0 for the frozen model (no memory) |
| `probe_id` | 20-hex stable id = sha256(dataset|family|parts) |
| `family` | observation unit: `edit` (own prompt of a stream item), `paraphrase` (held-out rewording), `locality_item` (the item's own unrelated prompts, first 3 per item), `locality` (50 sealed unrelated prompts), `near_miss_neighbour` / `near_miss_edit` (100 matched-family neighbour prompts and the paired edit prompts), `revision` / `revision_paraphrase` (50 retire-and-replace cases), `unseen` (100 un-taught pool prompts), `composition` (MQuAKE multi-hop questions, 80 cases x 3) |
| `item_id` | stream item id (item families) or endpoint row id / composition id |
| `stream_index` | 1-based teaching position in the sealed order (order 100) |
| `target` | which answer was scored: `new` (taught/requested), `true` (original fact), `v1`/`v2` (revision versions), `old`/`new` (composition) |

## scores.parquet (one row per model x dataset x horizon x probe x target)

| field | meaning |
|---|---|
| `status` | `ok` or an exclusion reason (`excluded:answer_tokens>32`, `empty_prompt`) |
| `target_text`, `n_tokens` | the scored answer; number of target tokens including the newline terminator (project convention) |
| `per_token_nll` | JSON list of −log p(y_t | x, y_<t), teacher forced, one prediction per gold prefix (cap writes at every prediction position) |
| `nll_total`, `nll_token` | sum and mean over target tokens including the terminator |
| `nll_total_no_terminator`, `nll_token_no_terminator` | same excluding the final newline token |
| `exact` | greedy generation (max 32 tokens, stop at newline/EOS) matches the target's aliases after NFKC/casefold/whitespace normalisation (only for generated families) |
| `fired` | reader selected a record at the prompt (not a hard null); None for frozen |
| `null_mass`, `best_score`, `n_records`, `selected_own_record` | reader selection at the prompt |
| `write_abs_s{m}_{mean,max}` | ‖W_m‖ at site m (blocks 4, 8, 12) averaged / maximised over the scored target positions |
| `write_rel_s{m}_{mean,max}` | ‖W_m‖ / (‖h_m‖ + 1e-12) with h_m the pre-write residual at the prediction position |
| `write_energy_{sum,mean}` | Σ_m ‖W_m‖² per position, summed / averaged over positions |
| `write_rel_max_over_sites`, `write_abs_max_over_sites` | maxima over sites and positions |
| `subject`, `relation_id`, `answer_tokens`, `hop_count`, `n_edits`, `case_id`, `question_index`, `paraphrase_index`, `locality_index`, `family_key`, `edit_item_id` | manifest metadata |

## generations.parquet (one row per generated probe)

`text` (decoded new tokens before the terminator), `stopped_by` (`newline`/`eos`/`max`), `truncated`, `steps`, `logprob_sum` (sum of greedy token log-probs), `exact_<target>` per target, `gen_write_abs_max`.

## paired_cases.parquet (one row per dataset x probe x target)

`L_<model>_h<h>` per-token NLL; `T_<model>_h<h>` total NLL; `X_<model>_h<h>` exact match; `F_<model>_h<h>` fired; `W_<model>_h<h>` max relative write norm; plus manifest metadata. Models never scored on a probe are NaN.

## tables/benchmark_original.csv

Registered metrics copied from the saved checkpoints (`source` column): `ES`, `RET-ES`, `RET-GS`, `LS`, `near_miss`, `revision`, `revision_latest_answer` with `_num`/`_den`; `unseen_false_fires`, `unseen_false_fire_rate`, `unseen_answer_changes`; MQuAKE `composition_success` (all three questions correct), `composition_num/den`, `composition_paraphrase_hits/paraphrases`. Frozen rows: ES/RET-ES/RET-GS are the frozen greedy answers against the taught aliases; LS and near-miss are 1 by definition; revision and unseen are N/A; `original_fact_exact_edit` is the frozen exact rate on `target_true`.

## tables/benchmark_standardized.csv / preference_margins.csv

Per (dataset, model, horizon, family, target): `n`, `nll_token_mean/median`, `nll_total_mean`, `nll_token_no_term_mean`, `exact_rate/num`, `fired_rate`, `cvar95_nll_token` (mean of the worst 5 %). Margins: `margin_total = logP(new) − logP(true)` and `margin_token = −NLL_token(new) + NLL_token(true)`, with positive fractions.

## tables/paired_gains.csv (bootstrap_results.parquet)

Per (dataset, family, target, horizon, seed, gain): `G_PC = L_frozen − L_ePC`, `G_BP = L_frozen − L_BP`, `G_PCvsBP = L_BP − L_ePC`; `mean`, `median`, `frac_helped` (G > 0), `frac_harmed` (G < 0), `p5`, `p95`, `worst5pct_mean_negative_gain` (mean of the 5 % most negative gains), `sd`, 95 % percentile intervals from 2,000 group-bootstrap draws (groups = item_id for item families, row id otherwise; seed 20261009). `seed = mean` rows use the seed-mean of the three readers.

## tables/cvar_A_B.csv

`A_cvar95_own` (each model's own worst 5 %); `B_mean_loss_on_frozen_hard5` and `B_success_on_frozen_hard5` (the frozen model's hardest 5 %, fixed set), `B_mean_loss_on_frozen_hard1`.

## tables/difficulty_deciles.csv

Deciles fixed by the frozen per-token NLL (ties broken by probe id); per decile the mean gain per seed and the seed-mean with 500-draw bootstrap intervals, and the success rates.

## tables/regressions.csv / worst_regressions.csv

`D = L_model − L_frozen` (positive = worse): `frac_worse`, `mean_positive_deterioration`, `p95_D`, `p99_D`, `worst5pct_mean_D`, `max_D`, `frac_D_gt_{0.5,1,2}`; rows `epc{s}_minus_bp{s}` give the same for ePC relative to BP. `worst_regressions` lists the five largest D per model with identifiers.

## tables/rank_correlations.csv, joint_extremes.csv, sequential.csv

Spearman rho (statistic, p) between frozen surprisal, write magnitude and gain; tail lift P(A|B)/P(A) with A = locality deterioration in its worst 10 %, B = top 10 % relative write (or any write when fewer than 10 % fire); sequential: immediate acquisition outcomes along the real teaching order with lag-1..5 autocorrelation of the per-edit paraphrase score.

## tables/ht17_*.csv, mquake_pcreader_harm_tails.csv, probe_loss_tail_fits.csv, frozen_text_surprisal_tails.json

HT-17 reproduction rows (PC-reader cells) and the field-by-field equality checks against the record; new MQuAKE harm statistics at thresholds 0.01/0.1/0.5/1 with the record's analyzer (`shape` = GPD shape = kappa, `gpd_minus_exp` = held-out log-likelihood gain per excess, positive favours GPD); per-probe loss tail fits at P90/P95/P97.5 (`kappa`, `sigma`, `loglik_gain_per_excess`, item-bootstrap CI); frozen ordinary-text surprisal fits.

## tables/dataset_statistics.csv / .json, data/case_populations.parquet, data/frequency/*.csv

Per population (eligible, reader_train, sealed_r0/r1/r2, pcr_r0_300): counts, unique categories, singleton and ≤5 fractions, top-1/5/10 % category shares, Shannon H, normalised H, N_effective, H(target_new | relation), Zipf slopes (ranks 1..100 and all ranks), token-length percentiles, duplicates; train/test shift (JS, smoothed KL with pseudocount 0.5, unseen-in-train fractions, train-count percentiles, triple overlap); MQuAKE-CF hop counts, requested-edit counts, relation chains.

## tables/cap_value/ (supplement, 2026-10-10) and data/cap_value/

Model keys: `frozen`; `bp_reader_s{0,1,2}` / `epc_reader_s{0,1,2}` (per seed); `bp_mean` / `epc_mean` = BP-CAP / PC-CAP seed mean (per-probe mean of the three seeds' losses, success indicators or fired flags). Horizons 300 (principal) and 100; at 100 the item-level families (edit, paraphrase, locality_item) cover `stream_index <= 100` only.

- `support_matrix.csv`: each requested comparison, whether existing data support it, how, and where.
- `denominator_audit_probes.csv` (probe/item counts per model x dataset x horizon x family, with the within-horizon count) and `denominator_audit_record.csv` (ES/RET-ES/RET-GS/LS/near-miss denominators as written in `benchmark_original.csv`, `consistent_with_horizon`).
- `basic_performance.csv`: per dataset x horizon x model: registered rates (`ES`, `RET_ES`, `RET_GS`, `LS`, `near_miss`, `unseen_false_fire_rate`, with `_num`/`_den`, `_seed_min`/`_seed_max` for seed means and `_flag` text for by-screen / by-definition cells), teacher-forced mean/median NLL per family (`nll_<family>`, `nll_edit_true_target`), `exact_<family>`, deteriorations vs frozen (`D_<family>_mean`, `_frac_worse`, `_frac_better`, `_max`), MQuAKE multi-hop (`mh_question_accuracy`, `mh_any_case`, `mh_all_case`, `mh_questions`, `mh_cases`), unrelated-text harm (`harm_*`).
- `improvements.csv`: `absolute_improvement` (loss: nats/token reduction; rate: percentage points) and `percent_improvement` (loss: % of frozen loss; rate: relative, null when frozen is 0) per metric x model.
- `extremes_own_worst.csv`: per model: `mean`, `cvar95`, `cvar99` (k = ceil(0.05 n), ceil(0.01 n)) with 95 % group-bootstrap intervals (2,000 draws at 300 edits, 500 at 100), `p95`, `p99`, `max`.
- `extremes_frozen_hardest.csv`: fixed sets `hard5` / `hard1` defined by the frozen loss (`frozen_threshold` = smallest frozen loss in the set); per model `mean_loss` [CI over items in the set], `success` [CI], `max_loss`, `frac_below_1nat`, `frac_still_above_frozen_median`.
- `deciles_actual_loss.csv`: per dataset x family x decile x model: `mean_loss` [CI, 500 draws], `median_loss`, `success`, `frozen_min`/`frozen_max` of the decile.
- `token_tails_common_thresholds.csv`: token-level pooled target surprisal (terminator excluded; families edit/paraphrase/unseen new target, locality_item/locality/near_miss_neighbour true target) per model (and `*_pooled_seeds`, flagged); thresholds `frozen P90/P95/P97.5` and `5/8/10 nats`; `n_exceed`, `frac_exceed`, `mean_excess`, GPD `kappa`/`sigma` with `fit_status` (insufficient < 50, exploratory 50–99, ok >= 100), `kappa_ci_*` (200 item-group draws), `loglik_gain_per_excess_vs_exponential`, `heavy_tail_supported` (CI entirely above 0).
- `collateral_vs_frozen.csv`: per collateral family x model: `frac_worse`/`frac_better`/`frac_unchanged` (|D| <= 1e-3 = unchanged) with CIs, `mean_D`, `mean_positive_D`, `p99_D`, `max_D`, `cvar95_D`, counts `n_D_gt_1/2/5`, `n_D_lt_minus_1/2/5`, `fired_rate`, `answer_changed_vs_frozen` (decoded text differs from the frozen generation; generated families only), `record_own_reference_metric/value` (LS, near-miss, false-fire rate vs the cell's cap-off reference). `collateral_worst_cases.csv`: the three largest D per family and seed.
- `harm_unrelated_text.csv`: record harm summaries per cell (reference = cap-off = frozen): `positions`, `mean_signed`, `mean_positive`, `es99_positive`, `maximum`, `count_gt_0.01/0.1/1.0`, `frac_gt_*`, `changed_distribution_fraction`.
- `gating_failures.csv`: paraphrase/edit probes per seed: `abstain_rate`, losses and CVaR95 among abstained vs fired, `success_fired/abstained`, `frozen_hard5_abstained` of `frozen_hard5_n`, `share_of_worst5pct_that_abstained`, `n_fired_but_above_2nats`, `abstained_equal_frozen_max_abs_diff` (0 = abstained loss equals frozen loss exactly).
- `data/cap_value/cases_seed_mean.parquet`: per probe (300 edits): frozen loss/success, each seed's loss, seed-mean loss/success/fired per rule. `data/cap_value/survival_curves.parquet`: token-loss survival on a common log grid per model.
