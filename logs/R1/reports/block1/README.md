# Block-1 report, X22 audit and v10 ledger supplement

Authoritative deliverables:

- `docs/R1_stage4_report_block1_partial.md`: readable partial research report.
- `analysis.json`: locked native analysis plus explicit block-only scope/provenance.
- `appendix/report.md`, CSV tables, `report-data.json`: complete filled native skeleton.
- `receipt-audit.json`: X22 passes for all 45 cells, including 120 checkpoints and 69,660 phase records.
- `summary.json`, `primary-realization0.csv`: descriptive effects/order dispersion; no intervals or classifiers.
- `accounting-processes.csv`: enclosing process charges; covered driver time is not added again.
- `watch-block1.jsonl`: exact 49-event historical prefix (4 development +45 confirmation).
- `docs/talk_claim_ledger_v6_session_v10.md` and `talk-evidence-v6-session-v10.json`: preserved v6 history with the verified v10 step-2 signed cost and current D.5 qualifications.
- `completion.json`: final evidence/export identities and verification results.

The 285 later-block slots are outside this snapshot. Native tables use their no-result representation; they are not a current-run failure inventory. Composition, some stable-v0 flags, global accounting and resource ratios retain the documented unavailable states. The readable report supplies X22-verified block accounting separately: a global D11 replay would mix in later live work. No native accounting validator is bypassed.

Six standard figures have 18 exports under `appendix/figures/`; three additional descriptive figures have nine exports under `slide-figures/`. Six selected figures /18 files are copied outside the repo to `assets/presentation-materials/figures/block1/`. Final visual checks corrected spacing only; all plot values are bound to the same summary.

## Verification

From the repo root:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m pytest -q -p no:cacheprovider \
  logs/R1/reports/block1/test_block1_report.py \
  tests/revision_v1/test_r1_d14_report.py tests/revision_v1/test_r1_d14b_report.py
```

55 tests pass. `lint.txt` covers this lane's Python files; `content-lock.txt` verifies all 916 resources and the exact 446-file installed implementation inventory. Final artifact verification rehashes immutable source bindings, both figure inventories and all presentation copies.

Generation order is `analyze_block1.py`, `audit_receipts.py`, `summarize.py`, native `scripts.r1_d14_report`, native `scripts.r1_d14_figures`, `slide_figures.py`, `publish_ledger_supplement.py`, `write_report.py`, then final verification. Generation scripts target this snapshot and normally refuse existing outputs. Do not rerun them over historical evidence; make a reviewed new snapshot directory/version. `--replace` exists only on this lane's figure and ledger-supplement generators for their pre-handoff formatting/provenance cleanup. It does not modify any original v6, signing receipt or frozen source.

Use the main JAX venv for analysis/tests; plotting uses the existing `assets/envs/status-paper-20260911/bin/python` with `MPLCONFIGDIR=assets/test_scratch/block1-report-mpl`. No environment installation or GPU use occurred.

## Harness history

`audit-run.txt` rejected the first attempt because the harness incorrectly used today's manually edited watch-document surrounding text to reconstruct older document hashes. Version 2 searches exact Git versions of those surrounding sections. `audit-run-v2.txt` then stopped after 30 cells because the harness incorrectly expected incremental journals in the 15 full-profile stable-v0 cells. Version 3 validates each recipe's declared integrity profile and succeeds. These were audit-harness assumptions, not experiment defects. `audit-run-v3.txt` is authoritative.

The original ledger publication and figure logs predate an unused-import cleanup and plot-label spacing correction. `ledger-publication-final.txt`, `slide-figures-final.txt`, their current manifests and `completion.json` identify final artifacts. Historical inference source bytes archived here are provenance data; they are not imported or installed.

CPU only. Live queue, results, watch, source lock and signing state were read-only. No commit or operational cutover was performed.
