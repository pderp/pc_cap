# ext-20261009 — dataset extremes, heavy tails and the frozen / ePC-reader / BP-reader comparison

Supplemental study commissioned on 9 October 2026 after the 17:00 EDT experimental freeze, by
`docs/AgentHandoffForResearchInTheExtremes.md` (pc_cap `22d19ab`) as amended by `docs/mandatory_ammendment.md`
(pc_cap `d003c10`). The amendment takes precedence wherever the two differ. Capstan executes; the lead signs off.

**Nothing in the frozen record is modified.** Frozen inputs (sealed recipes, payloads, memory snapshots, saved
full-validation vectors, reports) are read and hash-checked only. Every new number lives under this directory or
under `assets/extremes_analysis/ext-20261009/`, and every new model execution carries its own receipt.

## Layout

| where | what |
|---|---|
| `README.md`, `STATUS.md`, `config.json`, `manifest.json` | this file; live progress; study configuration; artifact registry (paths + SHA-256) |
| `audit/` | Stage 1: `model_and_dataset_inventory.md`, `analysis_matrix.md`, baseline completeness matrix |
| `validation/` | unit-test and smoke-test records (frozen equivalence, log-likelihood, joins, GPD, CVaR, bootstrap...) |
| `tables/` | CSV summary tables (every percentage with numerator and denominator) |
| `reports/` | `research_report.md`, `research_report.pdf`, data dictionary |
| `logs/` | per-stage logs and GPU receipts |
| `scripts/` | reproduction commands |
| `assets/extremes_analysis/ext-20261009/data/` | parquet: example manifest, scores, paired cases, dataset statistics, tail fits, bootstrap, residual statistics |
| `assets/extremes_analysis/ext-20261009/figures/` | PNG/SVG figures |
| `assets/extremes_analysis/ext-20261009/checkpoints/` | new memory snapshots / chunked raw outputs from this study's GPU work |

Code: `pc_cap/aw/extremes/` (new package; nothing under `scripts/` or `src/pccap/` is touched). Tests:
`pc_cap/aw/tests/test_extremes_*.py`.

## Experiment families (never pooled)

| id | family | backbone | what varies | horizon | population |
|---|---|---|---|---|---|
| `FROZEN` | frozen GPT-2 small, no cap | GPT-2 small 124M | — | evaluated on the same probes at the same checkpoints | same probes as the compared family |
| `PCR` | PC-trained reader study | GPT-2 small | reader **training rule**: BP vs ePC; 3 paired seeds; adjoint acquisition in both | 300 edits (checkpoints 100, 300) | realization 0, order 100; zsRE, CounterFact |
| `EXT` | this study's new evaluations | GPT-2 small | same PCR readers on MQuAKE (if valid); direct frozen scoring; teacher-forced losses | as stated per table | as stated per table |
| `S4` | Stage-4 confirmatory `R1_learned_ff` | GPT-2 small | selected v5 BP-trained reader vs registered controls | 1,000 edits (300 MQuAKE) | 3 realizations x 5 orders |
| `FV5` | fixed-v5 acquisition credit | GPT-2 small | **acquisition credit**: adjoint vs error inference, reader fixed | 300 edits | realization 0, order 100; zsRE, CounterFact |
| `PCV0` | PC-v0 corrected credit | **regenerated ePC 50M base**, v0 live cap | acquisition credit | 1,000 zsRE / 300 CounterFact | 3 exposed S5 realizations |

## Principal question

Across zsRE, CounterFact and MQuAKE, how do frozen GPT-2, the ePC-trained reader cap and the BP-trained reader cap
compare in ordinary benchmark performance, prediction difficulty, heavy-tail behaviour, extreme losses, adaptation
benefit, residual correction magnitude, locality and stability? Does the ePC-trained cap show distinctive advantages in
rare and extreme situations, and are those robust against the BP-trained cap rather than only against the frozen base?

## Final completion checklist (handoff §29)

| item | state |
|---|---|
| All three datasets represented with exact versions | yes — zsRE (MEND train rows, eligible pool), CounterFact (original, eligible pool), MQuAKE-CF (9,218 cases; v2 and T present but unused) — `audit/model_and_dataset_inventory.md` §3 |
| All three models have comparable basic benchmark results | yes for zsRE/CounterFact (record + frozen [new]); yes for MQuAKE after this study's six supplemental evaluations [new] — `tables/benchmark_original.csv` |
| Missing frozen-only tests genuinely performed | yes — direct frozen scoring of every probe family on all datasets, validated against the cap-off path (`validation/gpu_checks.json`) |
| PC/BP prior results preserved and reconciled | yes — copied with hashes; HT-17 PC-reader cells reproduced field by field (`tables/ht17_reproduction_checks.csv`) |
| Per-example joins and loss definitions tested | yes — `aw/tests/test_extremes_stats.py` (10 tests), `validation/gpu_checks.json` (9 checks), joins on explicit keys only |
| Tail fitting and uncertainty diagnostics documented | yes — `tables/*tail*`, thresholds P90/P95/P97.5 and the record's u = 0.01/0.1/0.5/1; insufficient/exploratory statuses retained |
| All available locality and residual metrics included | yes — locality/near-miss/unseen families scored for all models; write norms per site at every scored position |
| MQuAKE success aggregation correct | yes — all-question, any-question and question-level with denominators (`tables/mquake_composition.csv`; unit test) |
| PDF renders with equations/figures | yes — `reports/research_report.pdf` (xelatex via `aw/extremes/md2tex.py`) |
| Raw data and scripts complete and reload | yes — parquet under `assets/extremes_analysis/ext-20261009/data/`, JSONL chunks with hash manifests, `scripts/run_gpu_chain.sh`, `scripts/run_cpu_pipeline.sh` |
| Final STATUS.md marks completed / unavailable / incomplete | see `STATUS.md` |
