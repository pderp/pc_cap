# Deck v3 figure pipeline

Canonical outline: `docs/presentation/deck_v3_outline.md`. Export directory: `/home/derp/cap/assets/presentation-materials/deck_v3/`. Run commands from `/home/derp/cap/pc_cap`. No command below executes a model, changes a registered result or dispatches the queue. Data sources and hashes for exported files are recorded in the deck's `manifest.json`.

Use the project Python for analysis and the existing plotting environment for rendering:

```bash
export JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1
export MPLCONFIGDIR=/home/derp/cap/assets/test_scratch/triplet-report-mpl
```

`../venv/bin/python` is the project Python. `/home/derp/cap/assets/envs/status-paper-20260911/bin/python` is the existing Matplotlib environment. Substitute it for `PLOT_PYTHON` in the command table. Tokens such as `NEW_REPORT_DIR`, `NEW_FIGURE_DIR` and `NEW_RUN_GROUP` are explicit placeholders, not existing files. Analysis snapshot producers refuse existing directories. The plotting-only `aw.plot_comparators` helper refreshes its named figure exports and manifest; use a new figure directory when changing the data snapshot.

| Figure / slides | Generator command | Data and report |
| --- | --- | --- |
| `three-questions.svg`, `programme-and-testbed.svg` / 1, 2, 11 | `../venv/bin/python -m aw.presentation_prepare --comparators logs/R1/reports/comparators-225/report.json --output /home/derp/cap/assets/presentation-materials/deck_v3` | Authored conceptual diagrams grounded in the shared presentation brief; no numerical results. This command also copies outline, pipeline and selected existing plots and writes the claim ledger. |
| Triplet behavior / 5 | `PLOT_PYTHON -m aw.triplet_figures` | `logs/R1/reports/triplet/{summary,analysis}.json`; existing image `slide-figures/behavior-by-realization.png`. This historical producer has fixed paths and has **already run**; reuse its verified export. For an independent rebuild use a separate checkout/output namespace as the triplet README explains. |
| Comparator retention vs harm, one figure per dataset / 5, 7 | `../venv/bin/python -m aw.plot_comparators --report-dir logs/R1/reports/comparators-225 --output NEW_FIGURE_DIR` | `report.json` built from unchanged D.5 analysis; original-base mean KL and maximum positive ΔNLL. This helper appends the existing plotting packages to the project environment, preserving its JAX/NumPy; it installs nothing. Three realizations per condition; MQuAKE is descriptive at 300. |
| Full-validation development survival curve / 6 | `PLOT_PYTHON -m scripts.ht6_plot --input logs/r1_round35/ht6-final/curve-series.json --output NEW_FIGURE_DIR` | Existing `tail-survival.png`; explicit development scope. Use a new directory under `pc_cap/logs/`, then copy exports to assets. This command plots saved empirical curves and performs no new assay. |
| κ trade-off, development full-fidelity comparison, stress trajectories / 7, 8, 11 or backup | `PLOT_PYTHON -m scripts.ht9_presentation_figures --output NEW_FIGURE_DIR` | `logs/r1_round22/ht3e-independent-review-v2.json` and `logs/r1_round35/ht6-final/report.json`; audited pilot/stress development evidence. Existing exports in `logs/r1_round37/presentation-figures-v2/`. |
| PC-v0 efficacy vs cost / 9 | `PLOT_PYTHON -m aw.pc_v0_report plot --report NEW_REPORT_DIR/report.json --output NEW_FIGURE_DIR` | Corrected-run groups only. Current `logs/additional_work/PC-v0/report/report.json` has 0/12 completed cells, so its figure honestly says results pending. Keep CPU-smoke figures outside the presentation. |
| Fixed-v5 PC comparison and paired harm / 9–10 | Generator/report to be supplied with Claude's experimental output; no such figure is represented as existing | Pending measured experiments. `PC-4` is implementation validation only. Bind population, reference, endpoint and operation costs before rendering. |

Prepare a new comparator snapshot after the orchestrator reconciles the halt:

```bash
../venv/bin/python -m aw.comparator_report analyze --through 270 --output logs/R1/reports/comparators-270
../venv/bin/python -m aw.comparator_report publish --output logs/R1/reports/comparators-270 \
  --previous logs/R1/reports/comparators-225/report.json \
  --document docs/R1_stage4_report_comparators.md
../venv/bin/python -m aw.plot_comparators --report-dir logs/R1/reports/comparators-270 \
  --output /home/derp/cap/assets/presentation-materials/figures/comparators-270
```

Prepare the PC-v0 report after the actual runs, with `--orders 1` or `5` matching the choice made from development profiling:

```bash
../venv/bin/python -m aw.pc_v0_report build --run NEW_RUN_GROUP \
  --diagnostic-group DEVELOPMENT_DIAGNOSTIC_GROUP --orders 1 \
  --output NEW_REPORT_DIR --document docs/additional_work/PC-v0_report.md
```

Repeat `--run` for nonoverlapping run groups; duplicate coordinates are rejected rather than chosen by outcome. Partial cells stay visible, but only complete paired endpoints enter the comparison. The generator verifies source/model/data identities and binds the observed input bytes; the runner does not provide historical signatures on metrics. Raw diagnostic rows remain in the report JSON.

When regenerating the deck export, pass the chosen comparator snapshot to `aw.presentation_prepare` and use a new output directory. The initial `deck_v3` remains a dated preparation snapshot. Update the canonical outline and ledger with the actual experimental reports before producing final slides; do not present a pending image or CPU smoke as a measured PC result.
