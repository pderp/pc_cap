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
