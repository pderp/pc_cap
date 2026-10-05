# Sources and selected examples

Result snapshot: 2026-10-04. No model calls or new fits.

## Source map

- **short_deck**: `assets/presentation-materials/deck_v3/deck-pdf-20261004/active-inference-in-the-extremes-deck-20261004.pdf`
- **brief**: `pc_cap/docs/presentation/presentation_brief_2026-09-26.md`
- **mapping**: `pc_cap/docs/presentation/abstract_to_testbed.md`
- **proposal**: `pc_cap/docs/post_conference/coupled_collaboration_proposal.md`
- **feedback**: `pc_cap/docs/friday-10.02-review/feedback-MMK-nelson-entropy-capex.md`
- **stage4**: `pc_cap/docs/R1_stage4_report.md`
- **triplet**: `pc_cap/logs/R1/reports/triplet/summary.json`
- **examples**: `assets/support-information/examples.json`
- **examples_readme**: `assets/support-information/Capstan-README.md`
- **ht17**: `pc_cap/docs/additional_work/HT-17_report.md`
- **tails**: `pc_cap/logs/additional_work/HT-17/snapshot-20261004-complete/report.json`
- **awb**: `pc_cap/docs/additional_work/AW-B_report.md`
- **awb_data**: `pc_cap/logs/additional_work/AW-B/report-20260929/report.json`
- **pilot**: `pc_cap/docs/presentation/abstract_to_testbed.md`
- **pc_spec**: `pc_cap/docs/additional_work/PC-v0.md`
- **pc0**: `pc_cap/docs/additional_work/PC-v0_report.md`
- **pc1**: `pc_cap/docs/additional_work/PC-v1_report.md`
- **controls**: `pc_cap/docs/additional_work/PC-controls_report.md`
- **depth**: `pc_cap/logs/additional_work/PC-v0/controls-report-20260929/report.json`
- **matched**: `pc_cap/docs/additional_work/PC-matched-control_report.md`
- **reader**: `pc_cap/logs/additional_work/PC-reader/report-round63-final/report.json`
- **reader_doc**: `pc_cap/docs/additional_work/PC-reader_report.md`
- **upper**: `pc_cap/logs/additional_work/AW-L/report-round63-final/report.json`
- **upper_doc**: `pc_cap/docs/additional_work/AW-L_report.md`
- **option_r**: `pc_cap/docs/additional_work/R_report.md`
- **decisions**: `pc_cap/docs/decisions.md`

## Selection and display policy

Examples are selected for explanation, not randomly sampled or used to estimate an endpoint. All come from Capstan's first-30-item collection, realization 0/order 100. The slide set includes both success and failure, plus preservation of a poor base output. Leading/trailing whitespace is removed for display; long continuations are explicitly marked as excerpts. The full strings, including the original prompt, are in `assets/support-information/examples.json`. No grammar or factual content of the saved prompts was repaired. Counterfactual targets are experimental instructions, not asserted world facts.

The Fred Flintstone prompt is shown without its `nq question:` prefix on slide 8; the full source is `nq question: what is the name of fred flintstones wife`. Empty answer and no-cap-firing are separate observations. The example's stored selection flag is used when stating whether the cap fired.

| Dataset | Item / endpoint | Stream index | Final checkpoint |
|---|---|---:|---:|
| zsre | `zsre-train-14871` | 1 | 1000 |
| zsre | `zsre:0:near:0` | endpoint probe | 1000 |
| zsre | `zsre:0:locality:0` | endpoint probe | 1000 |
| counterfact | `cf-9366` | 1 | 1000 |
| counterfact | `cf-9025` | 11 | 1000 |
| mquake | `mquake:3218c8106c48e72c7297475f` | 1 | 300 |
| mquake | `mquake:f14bb41c4706241d480a5904` | 4 | 300 |

## Plot policy

Graph coordinates are exported in `logs/presentation/colleague_deck_20261004/plotted-values.json`. Retention dots are realization means after averaging orders; all three are displayed. Frequency and severity are the saved HT-17 group summaries with no new interval claim. Survival curves reuse exactly two preselected zsRE cells (realization 0, order 100); empirical stairs use unique observed values and `where=post`, with zero survival masked on the log axis rather than floored. GPD/exponential parameters come from the saved report; no refits. Reader differences intersect dataset/seed/rule identities. Upper-layer graph shows all twelve paired last-only/all-write ratios. Source hashes are in the build receipt.
