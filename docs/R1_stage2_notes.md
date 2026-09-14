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
| cf_bp_500_lr1e-3 | BP reference, CounterFact natural episodes | 128 | 500 × 4 | 1e-3 | 6.55 → 3.22 | 1.94 → 1.53 | 0.005 → 0.000 | 0.03 | 0.00 | 1.00 | 1.00 | 0.12 / 1.00 / 1.00 | 73 min |
| cf_fresh_wd_400 (prompt-only codes) | BP, CounterFact dev pool, fresh episodes/step, wd 0.01, best-dev @ step 99 | fresh | 400 × 4 | 1e-3 | 6.55 → 2.21 | 1.94 → 1.17 | 0.005 → 0.11 | 0.19 | 0.00 | 0.81 | 1.00 | 0.01 / 0.81 / 0.92 | 72 min |
| epc_500_lr1e-3_sd24 | ePC-credit surrogate (8 iters), corrected energy | 128 | 500 × 4 | 1e-3 | 6.22 → 4.50 | 1.89 → 0.96 | 0.005 → 1.14 | 0.25 | 0.25 | 1.00 | 0.81 | 0.42 / 0.98 / 0.77 | 68 min |
| epc_500_lr1e-3 (under SD-24 defect) | ePC surrogate (8 iters) | 128 | 500 × 4 | 1e-3 | 6.22 → 6.11 | 1.89 → 0.62 | 0.005 → 0.000 | 0.00 | 0.00 | 1.00 | 1.00 | 0.45 / 0.85 / 0.83 | 61 min |

Observations after bp_500: the training answer loss was still falling (50-step means 3.60 → 1.63), so the reader is not
converged; the null mass separates roles (0.31 on paraphrases vs 0.82–0.89 on near-miss/unrelated) with a 0.5 hard-null
threshold; old-fact retention (0.125) lags new-paraphrase acquisition (0.41) — the selection tends to favour the newest
record, which the L2 target over all records should correct with more training and possibly a history-weighted
sampling. The mechanics check (`results/R1/pilot/overfit_check.json`) drives a single episode to zero loss in ~12 steps.

SD-24 (found here): the ePC base's site prior penalized the cap write (½‖e + w‖²), so the surrogate's write gradient
had cosine ≈ 0.05 to the exact gradient whenever writes were present — the defective row above learned only the exact
retrieval term. With the prior on the pre-write latent (DEC-036) the surrogate is a genuine PC estimate on real episode
prefixes: cosine to the adjoint 1.00 at 1 iteration, 0.97 / 0.99 / 1.00 (sites 1/2/3) at 8, 0.90 / 0.95 / 0.99 at 32
(`results/R1/pilot/surrogate_check_fixed.json`); the matched run is repeated as `epc_500_lr1e-3_sd24`.

Numerical note: the write bound's norm had a NaN gradient at exactly-zero writes (a saturated null); fixed with a safe
norm (commit 6959a64) before bp_500 and the ePC run.

Next: (1) the matched ePC run (same seeds, episodes, schedule; only the estimator differs); (2) a longer BP run and a
history-balanced sampler if old-fact retention stays low; (3) CounterFact natural episodes once Codex's R1-20b lands;
(4) the behavioural gate 7 on the real edit stream (`RevisionCap` on the 100-edit zsRE dev stream with trained weights,
against the v0-stable / matched-update 0.44 baseline).

## Gate 7 on the real stream with synthetic-trained weights (`results/R1/stream_eval.md`)

`RevisionCap` with the bp_500 weights on the 100-edit zsRE development stream: ES 0.00, RET-ES 0.00, RET-GS 0.00,
LS 0.96, whether the fast rule is off or runs 5 steps at lr 0.1 or 1.0 (all steps accepted; per-item teacher-forced NLL
23.1 → 22.9 nats — no acquisition). The null mass sits at 0.35 on zsRE prompts and paraphrases and 0.49 on unrelated
prompts (45 % hard null), i.e. the synthetic-trained reader treats every zsRE prompt as "some record applies" but the
controller's writes carry no answer for this domain. Expected (plan 9 D-R2: the synthetic domain is for mechanics; the
natural domain trains the reader that is evaluated) and cheap to establish: the whole stream plus evaluation takes 28 s.
Consequence: CounterFact natural episodes (Codex lane R1-20b) are on the critical path for Stage 2; the orchestrator
checks whether the installed `natural_episode` already yields usable CounterFact training episodes.

## CounterFact natural episodes (cf_bp_500): memorization, not generalization

Training answer loss fell to 0.41 (100-step means 2.71 → 0.41) while the held-out answer loss stayed at 3.22 and only
1 of 32 dev paraphrases decoded exactly; the null decision, by contrast, generalized perfectly on dev (null mass 1.00 on
near-miss and unrelated, 0.12 on paraphrases; preservation 100 %). On the zsRE stream (`results/R1/stream_eval.md`,
row cf_bp_500_lr1e-3) the same reader hard-nulls every zsRE prompt (null mass 0.998) and only 47 % of unrelated prompts,
with LS 0.74: it learned to recognize its 128 training episodes' subjects and to reject everything else. Cause: the
development pool is small (411 train-partition rows across both datasets, so the 128 episodes reuse the same facts) and
the reader has 3.28 M parameters to memorize them. Remedies, in order of cost: fresh episodes every step (new supports
and queries drawn from the same rows), weight decay and early stopping on the dev loss, mixed synthetic + natural
training, and — the plan's own answer — a larger natural training pool from the fresh-data draw (R1-D1 exclusion
register, then the E.2 filter over MEND train; plan 9 D-R2). The first three are cheap and run next; the fourth is on
Codex's critical path.

## Matched estimator comparison (prompt-only-code design; synthetic domain; seeds, episodes and schedule identical)

| dev metric after 500 × 4 | BP reference (bp_500) | ePC-credit surrogate, corrected (epc_500_sd24) |
| --- | ---: | ---: |
| answer NLL | 2.85 | 4.50 |
| retrieval CE (exact in both) | 0.46 | 0.96 |
| preservation KL | 0.46 | 1.14 |
| paraphrase exact / old fact | 0.41 / 0.125 | 0.25 / 0.25 |
| near-miss / unrelated unchanged | 0.94 / 1.00 | 1.00 / 0.81 |
| wall | 44 min | 68 min (≈ 6× the base calls per prefix) |

Reading: with the SD-24 fix the surrogate's write gradient has cosine ≥ 0.97 to backprop at 8 iterations, yet it trains
more slowly and preserves less at the same optimizer schedule; the settled-error magnitude differs from the true gradient
by a prefix-dependent factor (norm ratio 0.55 at 8 iterations), which changes the effective step size after global-norm
clipping, and the preservation gradient from the KD head is the weakest part (training feedforward KL 1–2 vs 0.4). The
comparison is one seed on the pre-R23-02 design and is not a Stage 4 claim. Next: repeat both estimators on the repaired
(answer-sensitive) design with the CounterFact corpus once cf_fresh_wd_400_r25 shows what the reference reaches.

## Training data (DEC-037)

`manifests/revision_v1/train_pool_counterfact_v1.json`: 3,000 CounterFact items (seed 137) from the 16,141-item remainder of
the old eligible pool after removing the 3,000 sealed-realization items and 950 items whose subjects are exposed for other
reasons; every item has ≥ 2 paraphrases, locality prompts and token ids. Episodes are generated from these rows with the
installed generator (`--pool`); the run `cf_pool3k_r25_600` (repaired codes, fresh episodes, weight decay 0.01, dev every
50 steps on 32 held-out episodes) is the first on this pool.
