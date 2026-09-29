# X24-final — complete replication integrity audit

2026-09-28, Capex. **PASS: 60 v0 cells / 30 pairs; four fixed-v5 cells / two pairs.**

`aw/x24_final.py --require-complete` extends the original metadata-only audit to the two fixed-v5 checkpoint inventories, payload item order, snapshot bytes and internal hashes, immutable reader/base witnesses, phase continuity and identical paired inference configuration. It resolves only explicitly approved historical source bytes; it does not modify live runner files. Output: `logs/r1_x24/final/report.json` and `report.md`, with the original 60-cell audit under `final/v0/`.

No efficacy fields were decoded and no model executed by this audit. v0 retains the independently reconstructed empty-cap state check. Fixed-v5 relies on the recorded empty-state and inference witnesses rather than a new real-base reconstruction; this limit is explicit. All artifact identities are rechecked after reading. Numerical efficacy and harm reproduction is separate PC-8/11 work.

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 ../venv/bin/python -m aw.x24_final --require-complete
```
