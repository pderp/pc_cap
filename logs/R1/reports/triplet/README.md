# Complete triplet snapshot — R1-D14d

Read [the scientific report](../../../../docs/R1_stage4_report_triplet.md). This snapshot covers 135 cells in blocks 1–3, with three realizations and five orders. It does not use results from the advancing later blocks. No model calls or experimental re-scoring were performed.

Artifacts:

- `analysis-native.json` / `.md`: unchanged registered analyzer output through the scoped loader. `analysis.json` adds the explicit snapshot scope and wrapper source hash.
- `summary.json`, `realization-summary.csv`: 27 dataset/condition/realization groups, with all five order values and source pointers.
- `appendix/report.md`, `appendix/report-data.json`, `appendix/*.csv`: filled D14 skeleton, all 63 primary metric slots, paired order differences, uncertainty sensitivity, fidelity, concentration and secondary endpoints.
- `accounting.json` / `.csv`: 135 process envelopes, reconciled with the historical block-3 report. The two absent Q21 parent decisions are disclosed. The native whole-queue accounting field is explicitly unavailable; it must not be read as an absence of this separately verified inventory.
- `watch-triplet.jsonl`: unmodified historical journal prefix through the final triplet observation, verified by replay.
- `appendix/figures/`: six standard figures, each in PDF/SVG/PNG. `slide-figures/`: behavior across realizations in the same three formats. Both directories have manifests. Four selected figures were also copied to `/home/derp/cap/assets/presentation-materials/figures/triplet/` (12 exports), with copy hashes in the slide manifest.
- `tests.txt`: 48 passing actual-snapshot and formatter tests.

The production commands, in order, were:

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m aw.triplet_report analyze
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m aw.triplet_report publish
MPLCONFIGDIR=/home/derp/cap/assets/test_scratch/triplet-report-mpl \
  JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 \
  /home/derp/cap/assets/envs/status-paper-20260911/bin/python -m scripts.r1_d14_figures \
  --data logs/R1/reports/triplet/appendix/report-data.json
MPLCONFIGDIR=/home/derp/cap/assets/test_scratch/triplet-report-mpl \
  JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 \
  /home/derp/cap/assets/envs/status-paper-20260911/bin/python -m aw.triplet_figures
```

Run from the repository root. The existing plotting environment was reused; no dependency installation was needed. These commands document the completed production sequence: the producers refuse existing snapshot/export paths. For an independent rebuild, use a separate checkout/output namespace and update the producer constants (`OUT`, `EXPORT`, report path) before production; do not overwrite this source-bound snapshot. The final presentation pass adds the concise findings and image to the readable report without changing the inference producer or statistics.

Verification:

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m pytest -q -p no:cacheprovider \
  aw/tests/test_triplet_report.py tests/revision_v1/test_r1_d14_report.py \
  tests/revision_v1/test_r1_d14b_report.py
```

The three-realization range intervals are registered preliminary decision summaries; they do not establish 95% familywise coverage. Adjacent t intervals are assumption-dependent, pointwise sensitivity displays with two degrees of freedom. Orders sharing subjects are not extra independent replications. MQuAKE at 300 edits remains descriptive. Benchmark breaches do not imply corrupt data, and passing integrity does not imply good fidelity.
