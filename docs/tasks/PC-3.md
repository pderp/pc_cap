# PC-3 — PC-v0 comparison report generator

Status: done (CPU preparation). Agent: Capex. Date: 2026-09-26. Experimental GPU results remain pending.

Inputs: round-45 lane, `aw/pc_v0.py` output format, `docs/additional_work/PC-v0.md`, and the shared three-theme presentation brief. Outputs: `aw/pc_v0_report.py`, `aw/pc_v0_smoke.py`, `aw/tests/test_pc_v0_report.py`, `docs/additional_work/PC-v0_report.md`, `logs/additional_work/PC-v0/{report,smoke-report}/`, and the explicitly synthetic `results/additional_work/PC-v0/cpu-smoke-round45/`. Pending figure exports are under `assets/presentation-materials/figures/pc_v0/pending-20260926/`; smoke figures stay outside the deck.

The generator checks plan/config coordinates and source inventories, pinned regenerated model/archive/tokenizer and data/drift identities, paired item order/seeds/locality/initial-state identities, unchanged base hashes, finish/metric/secondary counts and group-finish consistency. Real replication, development diagnostics and synthetic smoke are kept distinct. Duplicate coordinates refuse rather than selecting a favorable attempt. Missing/partial cells remain in the planned denominator; only complete paired endpoints supply differences. Realization means average the preselected orders, and the overall mean/range requires all three complete realization groups. No token-level interval is constructed.

The readable report includes primary and secondary bounded-text differences separately, historical defective-energy reference, process/operation counts, and actual 1/8/32 diagnostics when supplied. The production runner does not pre-sign metrics/configuration files; this report verifies identities and binds their present bytes, not historical authenticity. GPU companion ordinary-text harm is explicitly pending, not inferred from editing scores.

Verification: **5 focused report tests pass**, including actual tiny-model `run_stream` output from both credit arms, incomplete/missing cells, mismatched identities, finish inconsistencies and real-solver diagnostic rendering. The smoke uses the same stream runner and supplemental evaluator, with a 64-token test base, synthetic identity fixtures, and sequential decoding to avoid GPT-2 EOS padding in that tiny vocabulary. It does not exercise the production GPU lease/launcher or claim real-model results. Logs: `logs/additional_work/round45/pc3-smoke.txt`, `pc3-tests.txt`, `report-tests.txt`.

Commands already run:

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m aw.pc_v0_smoke --output results/additional_work/PC-v0/cpu-smoke-round45
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m pytest -q -p no:cacheprovider aw/tests/test_pc_v0_report.py
../venv/bin/python -m aw.pc_v0_report build --output logs/additional_work/PC-v0/report \
  --document docs/additional_work/PC-v0_report.md
```

The smoke output already exists; use a new directory for an independent rerun and point the fixture at that output. Owner command after GPU completion: `python -m aw.pc_v0_report build --run RUN_GROUP --diagnostic-group DEV_DIAGNOSTIC_GROUP --orders 1 --output NEW_REPORT_DIR --document docs/additional_work/PC-v0_report.md`; `--orders 5` only if that was the preselected design. Repeat `--run` for disjoint groups. Plot with the existing plotting environment: `python -m aw.pc_v0_report plot --report NEW_REPORT_DIR/report.json --output NEW_FIGURE_DIR`. Exact environments and export commands are in `docs/presentation/deck_v3_figure_pipeline.md`.

Done-when: the reporting path is proven before real results arrive. Remaining: feed in those results and companion harm, not additional CPU implementation. Cost: 0 GPU seconds; shared CPU work was not separately timed. No locked-code changes, dependencies installed, queue operation or commit.
