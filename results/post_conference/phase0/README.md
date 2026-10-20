# Phase 0 — cheap analyses before any new training (post-conference programme)

Capstan, 20 October 2026. Study id `phase0`. Decided by the lead on 20 Oct ("go ahead with Phase 0") after
`docs/post_conference_capstan_proposal.md` §5.

Everything here is built from the frozen ext-20261009 record (scores, raw selection chunks, memory snapshots, payloads)
plus **forward-only** GPU replays of the six saved readers and the frozen base. No training, no new memories, no
modification of the frozen record. GPU work runs under the exclusive lease (`aw/post_conference/run_phase0_gpu.sh`).

| Item (proposal §5) | Module | Needs GPU | Outputs |
|---|---|---|---|
| 1 Gate frontier of the six readers; oracle record replay | `aw/post_conference/phase0_frontier.py` | yes (replay of abstained probes) | `tables/frontier.csv`, `oracle_rescue.csv`, `replay_validation.csv`; `data/replay.parquet`, `frontier_cases.parquet`, `oracle_cases.parquet` |
| 2 Failure atlas, oracle selection rate, payload vs gating | `phase0_atlas.py` | no | `failure_atlas*.csv`, `payload_vs_gating.csv`, `oracle_selection_rate.csv`, `failures_by_difficulty.csv`; `selection_table.parquet` |
| 3 In-context retrieval arms (oracle / knn / lex) | `phase0_incontext.py` | yes (frozen base) | `incontext_summary.csv`, `incontext_frontier.csv`; `incontext.parquet` |
| 4 Locality audit + corrigendum | `phase0_locality.py` | no | `locality_audit*.csv`, `locality_contamination.csv`, `template_overlap.csv` |
| 5 Composition: retrieval, firing, frozen-base ceiling | `phase0_composition.py` | partly (frozen base) | `composition_retrieval.csv`, `composition_questions.csv`, `composition_frozen_ceiling.csv`; `composition_frozen.parquet` |
| 6 Unexposed subjects | `phase0_reserves.py` | no | `reserves.csv`, `reserves.json` |
| Figures / report | `phase0_figures.py`, `phase0_report.py` | no | `../../../../assets/post_conference/phase0/figures/*.{png,svg}`, `phase0_report.{md,pdf}` |

Layout: text (tables, report, manifest) under `pc_cap/results/post_conference/phase0/`; parquet and figures under
`assets/post_conference/phase0/`; raw replay / in-context JSONL chunks under `assets/runs/post_conference/phase0/`;
logs under `pc_cap/logs/post_conference/phase0/`.

Rerun order (CPU unless noted): atlas → locality → composition → reserves → [GPU: composition --execute, incontext
--execute, frontier --execute] → composition --assemble → incontext --assemble → frontier --assemble → figures → report.

Corrigendum applied to the extremes study on 20 Oct: `aw/extremes/assemble.py` relabels item-locality prompts that are
themselves taught stream items (40 of 600 on MQuAKE) as family `locality_item_taught`; ext-20261009 tables, figures and
reports were regenerated with `results/extremes_analysis/ext-20261009/scripts/run_cpu_pipeline.sh`.
