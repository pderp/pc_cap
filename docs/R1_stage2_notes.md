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
| cf_fresh_wd_400_r25 (answer-sensitive codes) | BP, CounterFact dev pool, fresh episodes/step, wd 0.01, best-dev @ step 99 | fresh | 400 × 4 | 1e-3 | 6.59 → 2.29 | 1.94 → 1.13 | 0.006 → 0.000 | 0.16 | 0.00 | 1.00 | 1.00 | 0.08 / 1.00 / 1.00 | 72 min |
| cf_pool3k_r25_600 | BP, CounterFact 3k training pool (DEC-037), fresh episodes/step, wd 0.01, best-dev @ 449, 32 dev eps | fresh | 600 × 4 | 1e-3 | 8.02 → 3.50 | 1.87 → 0.70 | 0.007 → 0.006 | 0.03 (n=64) | 0.00 | 1.00 | 0.97 | 0.03 / 0.99 / 0.98 | 100 min |
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

Small-pool verdict (cf_fresh_wd_400 vs _r25): with ~100 distinct training facts the answer-sensitive code neither helps nor
hurts held-out answers (2.21 vs 2.29; paraphrase exact 0.19 vs 0.16), preservation is perfect in both, and old-fact
retention is zero in both — the selection or the codes of history records fail on dev episodes. The 3k-pool run decides
whether facts, not mechanism, were the limit; a per-role selection diagnostic (top-1 record vs supporting record, null
mass) is added to the pilot for the runs after it.

## 3k-pool verdict (cf_pool3k_r25_600) and the fast rule with trained weights

With 3,000 training facts the training answer loss no longer collapses (≈ 2.0 at the end) and the held-out loss improves
only to 3.50; paraphrase exact 0.03 (2/64), old fact 0/32; top-1 selection hits the supporting record on 41 % of
paraphrases and 56 % of old-fact queries; preservation 1.00 / 0.97 with null masses 0.03 vs 0.99. Re-evaluating the same
weights with the fast rule on (5 steps, lr 0.1 / 1 / 10) changes nothing. So, with the current design, selection is
mediocre and answer production for unseen facts fails: a 256-d observation-derived code passed through a fixed controller
does not carry an arbitrary new answer, and the fast rule's gradient through that controller is too weak to inject it —
whereas v0's direct gradient optimization of the write vector acquired every edit (ES 1.00). Next design step: give each
record an explicit fast-state delta write (3 × 768, taught by the base adjoint under the same aggregate bound, as in v0
and the matched-update control) on top of the controller's code-driven write; the learned reader keeps selection, the
null and stable observations. Bytes: 9 KB per record, within the ceiling for the stream lengths in plan 9.

## Design change after the 3k-pool run (2026-09-14, 00:30 EDT): explicit deltas and tied heads

Diagnostics on a held-out CounterFact support with the cf_pool3k weights: (1) the fast rule through the code lowers the
support loss only slowly (3.43 → 2.50 after 20 steps at lr 100); (2) an explicit per-record delta write taught by
normalized adjoint steps (the v0 mechanism) reaches 3.04 and then stalls, because the controller's raw write has aggregate
7.8 against the bound 0.3 — after projection the delta is ≈ 4 % of the direction; (3) the reader hard-nulls the support's
OWN prompt on unseen facts (null mass 1.00): separate query/key heads only align on training facts. Changes (commit
29a8ec9): the query and key heads are tied (an identical observation scores itself by construction, the learned part is
paraphrase similarity), and a record's taught delta replaces the code-driven write (the controller's write serves only
records without a delta). The learned reader therefore keeps selection, the null and stable observations; acquisition is
v0's gradient write per record. Run cf_pool3k_tied_400 retrains the reader under this design; evaluation with delta
steps follows on the CounterFact dev episodes and on the zsRE stream against the 0.44 controls.

## First learner numbers on the zsRE stream above the controls (2026-09-14, 01:10 EDT)

`results/R1/stream_eval.md`, rows `random_tied_*`: a RANDOM-initialized tied cosine reader (no training), stable
observations, per-position delta writes (5 normalized adjoint steps, τ = 0.1), hard top-1 selection and no null
(threshold 1.01) on the Stage 0 zsRE stream: ES 1.00, RET-ES 1.00, **RET-GS 0.65** (controls 0.44; v0 live 0.24/0.29),
LS 0.24. Acquisition and retention now come from v0's per-prefix gradient write; the paraphrase gain comes from the
siamese cosine geometry over stable observations (even untrained), which generalizes across formulations better than
v0's radius-gated key distance. Locality is destroyed because nothing rejects unrelated prompts: the trained null (and,
as a non-learned fallback, a cosine firing threshold) must restore LS without giving back RET-GS. The intermediate
variants document why each piece is needed: one delta per record ES 0.02; soft mixing ES 0.13; dot-product scoring with
hard top-1 ES 0.23; cosine + hard top-1 ES 1.00.
