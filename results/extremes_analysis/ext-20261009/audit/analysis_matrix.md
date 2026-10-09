# Analysis matrix: already complete / computable from saved data / needs new evaluation

Capstan · Stage 1 · keyed to the handoff sections (H§) and the amendment (A§).

| requested analysis | status | source or plan |
|---|---|---|
| H§1 audit of models, datasets, checkpoints, seeds | **done** (this directory) | `audit/model_and_dataset_inventory.md` |
| H§2 basic 3-model × 3-dataset table, original metrics (ES, RET-ES, RET-GS, LS, near-miss, revision, unseen) for BP and ePC readers on zsRE/CounterFact at 100 and 300 | **complete in record** | `results/additional_work/PC-reader/eval-*/stream/checkpoint-{100,300}.json`; `docs/additional_work/PC-reader_report.md` — copied with hashes, denominators restated |
| H§2 same for frozen GPT-2 on identical probes | **new evaluation (cheap, GPU)** | Stage 2: direct frozen greedy generation on edit prompts, paraphrases, locality, near-miss, unseen at the 100/300 horizons; original-fact (`target_true`) generation for CounterFact/MQuAKE; validated vs cap-off path |
| H§2 PCR readers on MQuAKE | **missing → new supplemental evaluation (GPU)** | Stage 3: six saved readers × MQuAKE r0 o100, 300 edits with the sealed MQuAKE recipe endpoints (locality 50, near-miss 100, revision 50, unseen 100, composition 80 cases) + harm assay; estimated 0.5–0.7 h per evaluation from PCR/S4 receipts (≈ 3–4.5 h total) |
| H§2 S4 v5 reader context table (1,000 edits, all datasets) | **complete in record** | `logs/R1/reports/triplet/summary.json`; `docs/R1_stage4_report.md` — shown as family S4 only |
| H§2 FV5 and PCV0 | **complete in record** | `docs/additional_work/PC-v1_report.md`, `PC-v0_report.md` — separate sections |
| H§3 example manifest (parquet) and long-format results table with stable keys | **from saved data + new scores** | Stage 1/2: built from sealed payloads (items, endpoints, composition rows), eligible pools, MQuAKE-CF raw; scores joined on (dataset, item_id/probe_id, model, horizon) |
| H§4 teacher-forced target log-probs (total, per-token) for all three models on identical probes; counterfactual margins | **new evaluation (GPU)** | Stage 2: frozen = direct forward; readers = reload the saved 300-edit (and 100-edit) memory snapshots and score with `teacher_forced_nll` through the cap's read path (same E.2 per-prefix semantics); target_true vs target_new margins where both exist |
| H§5 success rates with numerators/denominators | **from saved data** | restate from checkpoint metrics (planned/scored/numerator) |
| H§6 MQuAKE: question accuracy, any-question, all-question, by hop/edit count | **partly from saved data** | S4 MQuAKE cells have composition rows (multi-hop questions, per-question outcomes) — parse; PCR readers on MQuAKE need Stage 3; frozen needs Stage 2 |
| H§7 frequency, rarity, diversity, Zipf, Shannon/conditional entropy | **computable (CPU)** | Stage 4 from pools, realizations and MQuAKE-CF raw; train = reader-training pools (`manifests/revision_v1/train_pools*`), test = sealed realizations |
| H§8 JS/KL shift, Wasserstein on surprisal, extreme-vs-typical subsets | **computable (CPU) after Stage 2 surprisal** | Stage 4 |
| H§9 empirical distributions of frozen surprisal, cap losses, correction magnitudes, harm, locality | **ordinary text: from saved vectors; probes: after Stage 2; corrections: new** | saved `full-validation` / `harm/vectors.npz` (loss_cap, loss_capoff, loss_original, KLs) for every cell; per-probe losses Stage 2; write norms need a targeted instrumented pass (Stage 6) |
| H§10 GPD tail fits | **reproduce HT-17 first (A§5), extend** | HT-17 report + `aw/tail_class.py` (203 Stage-4 + 12 PCR + 30 AW-B + κ cells); Capex's 9 Oct release adds MQuAKE and KL tails. Extension: PCR readers' per-probe losses, frozen surprisal by dataset, PCR MQuAKE harm (after Stage 3) |
| H§11 paired gains G_PC, G_BP, G_PCvsBP; CVaR A and B | **after Stage 2** | Stage 6; ordinary-text paired harm already available per window for the 12 PCR cells |
| H§12 gain vs frozen-difficulty deciles; sensitivity by length, relation, preference, hop count | **after Stage 2/3** | Stage 6 |
| H§13 catastrophic regressions D > 0.5 nat etc. | **ordinary text: from saved vectors; probes: after Stage 2** | Stage 6 |
| H§14 locality: correct-answer loss, joint extremes, Spearman | **after Stage 2; joint extremes need write norms** | Stage 6 |
| H§15 MQuAKE reasoning analysis | **S4 from record; PCR after Stage 3** | Stage 6 |
| H§16 sequential behaviour / correlated extremes | **computable from saved per-edit `items.jsonl` order** (real teaching order) | Stage 6, exploratory: autocorrelation of immediate ES / harm by edit index; ordinary-text windows are not a time series |
| H§17 residual correction norms (abs, relative, energy) per site | **new targeted pass (GPU, small)** | Stage 6: instrument `RevisionCap.predict` outputs (write W per site) for the 300 edit prompts + paraphrases + locality with each reader; frozen = structural zeros (not fitted) |
| H§18–19 Nelson informational scale identity on fitted GPD | **computable** | Stage 7: symbolic/numeric check on HT-17 and new fits |
| H§20 coupled-entropy sensitivity (optional) | **optional, last** | Stage 7, labelled exploratory; separate from HT-17 |
| H§21 bootstrap CIs | **new** | Stage 6; groups = edit items / composition cases; windows for text; seeds reported separately (A§5) |
| H§22 validation tests | **new** | Stage 1: `aw/tests/test_extremes_*.py` + `validation/` records |
| H§24–26 persistence, STATUS | **new** | this directory |
| H§27–29 report, figures, raw data | **new** | Stage 8 |

## Baseline completeness matrix (per model × dataset, principal families)

| model | zsRE 100/300 metrics | CounterFact 100/300 metrics | MQuAKE 100/300 metrics | ordinary-text harm (245,237) | per-probe teacher-forced NLL |
|---|---|---|---|---|---|
| frozen | **to run** | **to run** | **to run** | saved (cap-off field in every vector) | **to run** |
| bp_reader_s0/s1/s2 | saved | saved | **to run (Stage 3)** | saved (zsRE, CounterFact) | **to run** |
| epc_reader_s0/s1/s2 | saved | saved | **to run (Stage 3)** | saved (zsRE, CounterFact) | **to run** |
