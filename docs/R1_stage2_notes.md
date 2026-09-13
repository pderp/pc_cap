# Revision v1 — Stage 2 notes (episodic co-training pilots)

Orchestrator; started 2026-09-13 evening. Synthetic domain = the installed generator (`pccap.revision_v1.episodes`,
Codex R1-20): train split contexts 0–3 / families 0–1, dev split contexts 4–5 / families 2–3 (unseen). Reader/controller
at the first development configuration (3.28 M parameters), fast steps 0 (initial codes), losses per
`docs/revision_v1_losses.md`, optax adamw with global-norm clipping 1.0. Dev evaluation = the exact reference losses on
16 held-out episodes; behavioural check = a fresh `RevisionCap` adapts on each dev episode's supports (2–8 history + 1
new) and answers its queries by greedy decoding. Weights under `/home/derp/cap/assets/runs/pc_cap/R1/pilot/<tag>/`.

| tag | estimator | train eps | steps × batch | lr | dev answer NLL before → after | dev retrieval CE | dev preserve KL | paraphrase exact | old fact exact | near-miss unchanged | unrelated unchanged | null mass (para / near-miss / unrel) | wall |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| bp_100_lr1e-4 | BP reference | 64 | 100 × 4 | 1e-4 | 6.22 → 4.02 | 1.89 → 1.31 | 0.005 → 0.38 | 0.03 | 0.00 | n/a (label metric only) | n/a | 0.47 / 0.50 / 0.57 | 8.5 min |
| bp_500_lr1e-3 | BP reference | 128 | 500 × 4 | 1e-3 | 6.22 → 2.85 | 1.89 → 0.46 | 0.005 → 0.46 | **0.41** | 0.125 | 0.94 | 1.00 | 0.31 / 0.82 / 0.89 | 44 min |
| epc_500_lr1e-3 | ePC surrogate (8 iters) | 128 | 500 × 4 | 1e-3 | running | | | | | | | | |

Observations after bp_500: the training answer loss was still falling (50-step means 3.60 → 1.63), so the reader is not
converged; the null mass separates roles (0.31 on paraphrases vs 0.82–0.89 on near-miss/unrelated) with a 0.5 hard-null
threshold; old-fact retention (0.125) lags new-paraphrase acquisition (0.41) — the selection tends to favour the newest
record, which the L2 target over all records should correct with more training and possibly a history-weighted
sampling. The mechanics check (`results/R1/pilot/overfit_check.json`) drives a single episode to zero loss in ~12 steps.

Numerical note: the write bound's norm had a NaN gradient at exactly-zero writes (a saturated null); fixed with a safe
norm (commit 6959a64) before bp_500 and the ePC run.

Next: (1) the matched ePC run (same seeds, episodes, schedule; only the estimator differs); (2) a longer BP run and a
history-balanced sampler if old-fact retention stays low; (3) CounterFact natural episodes once Codex's R1-20b lands;
(4) the behavioural gate 7 on the real edit stream (`RevisionCap` on the 100-edit zsRE dev stream with trained weights,
against the v0-stable / matched-update 0.44 baseline).
