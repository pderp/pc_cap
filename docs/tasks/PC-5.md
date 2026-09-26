# PC-5 — paired ordinary-text harm readout

Capex, 2026-09-26. **CPU implementation complete; production GPU dispatch belongs
to Capstan (the Claude agent).** No GPU use or acquisition rerun in this lane.

`aw/pc_harm_readout.py` verifies the completed group's model/data/config identities,
restores `learner_end.ckpt` using both file and state hashes, and reuses the frozen
batched v0 reader. Its shared base pass supplies both retrieval features and
cap-off logits; cap partial passes are charged. It calls **unchanged
`aw.scoring.score_configs`** once per batch. No full-vocabulary logits survive
a batch, and query state / base hashes must remain unchanged.

The v0 inventory exactly matches the legacy S5 drift evaluator: the first 32
complete 128-token windows, 127 next-token targets each, **4,064 positions**.
`selection('v5')` validates the full **245,237-position** inventory. `read_arm`
and `pair` are reusable by the future fixed-v5 runner, but that runner still needs
to supply its restored checkpoint and an audited batch reader. In particular,
the frozen `PositionBatchReader` accepts exact `RevisionCap`, not the new
`PCRevisionCap` subclass: do not bypass that guard or claim this lane has tested
the fixed-v5 GPU integration. Its separate execution remains held for reviewer
feedback until Monday 09:00 EDT per lead-queue item 120.

Outputs in a new subdirectory of `results/additional_work/PC-v0/harm/`:

- Per-arm `vectors.npz` in 68f `(window, target, field)` layout; the five fields
  retain losses for cap / own-cap-off / original and both reference-to-cap KLs.
- `summary.json`: signed mean ΔNLL, mean KL, fractional empirical ES99 of positive
  harm, signed/positive maximum, first maximum location and tie count, strict
  exceedances at .01/.1/1 nat, and positive-mass concentration. Half-mass count
  and fraction are undefined (`null`) when total positive mass is zero.
- Per-pair NPZ: SE-E minus SE-A at identical positions. Pairing checks the
  position identity, base identity, vocabulary layout and exact reference losses.
  ES99 of paired changes and the difference of the two arm ES99s are separate.
- `report.json` and `table.md`: same dataset / realization / order table style
  as PC-3. `table_block(report)` is directly includable by the efficacy report;
  no edit to its currently bound producer was necessary. No token-based intervals.
- Per-arm `cost.json` and enclosing `cost.json`, including attempted work on
  failure. Enclosing process time replaces, rather than adds to, its contained
  query timers. These are **readout costs, separate from replication costs**.

Owner invocation, once the completed PC-v0 group exists and the GPU is released:

```bash
JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 \
  ../venv/bin/python -m aw.pc_harm_readout --execute \
  --run results/additional_work/PC-v0/replication-12-20260926 \
  --output results/additional_work/PC-v0/harm/pc-v0-NEW \
  --batch-size 16 --wall-seconds 14400
```

The 14,400-second value is a suggested v0 sub-allowance, not a measured forecast.
Use only the remaining approved allowance: **the 28,800-second ceiling is shared
across v0, fixed-v5 and any readout reruns**. The CLI limits an invocation to at
most that ceiling, requires the normal exclusive GPU lease, rejects competing
CUDA jobs, and enforces the October 9 17:00 ET cutoff. Capstan accounts for the
sum across invocations; this tool does not administer the whole project budget.
Incomplete groups are refused rather than silently comparing unequal prefixes.

Validation: four focused CPU tests and the broader 74-test `aw` suite pass.
Actual saved round-45 smoke checkpoints were restored and compared with direct
scalar predictions; the paired vectors equal the exact difference of the arm
vectors. Coverage, fractional ES, ties, zero mass, mutation/digest checks and
failed-query costs are exercised. The final CLI smoke artifact is
`results/additional_work/PC-v0/harm/cpu-smoke-round46-v2/` (supersedes the initial
fixture's zero-mass convention). These six synthetic positions are not research
results. Logs: `logs/additional_work/round46/aw-tests.txt`, `pc5-smoke-v2.txt`.

Scientific issue surfaced: the existing shared helper's `summary()` ES99 is a
percentile. PC-5 avoids that summary and imports its unchanged numerical scorer;
the owner handoff is [HT-13 review](HT-13-round46-review.md). No frozen source or
running experimental algorithm was changed.
