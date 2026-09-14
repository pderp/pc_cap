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
| cf_pool3k_tiedcos_400 | BP, 3k pool, tied cosine reader (query-only null), fresh episodes, wd 0.01, best-dev @ 399 | fresh | 400 × 4 | 1e-3 | 8.03 → 3.27 | 5.14 → 0.91 | 0.009 → 0.065 | 0.05 (top-1 hit 0.45) | 0.06 (top-1 0.53) | 1.00 | 1.00 | 0.02 / 0.98 / 0.98 | 74 min |
| cf_pool3k_pairnull_400 | BP, 3k pool, tied cosine + pairwise null (no own-prompt role), fresh episodes, wd 0.01, best-dev @ 349 | fresh | 400 × 4 | 1e-3 | 8.03 → 3.29 | 5.32 → 0.98 | 0.009 → 0.14 | 0.03 (top-1 0.45) | 0.03 (top-1 0.53) | 0.97 | 0.94 | 0.001 / 0.96 / 0.93 | 74 min |
| cf_pool3k_pair_own_400 | BP, 3k pool, tied cosine + pairwise null + own-prompt queries (all supports), fresh, wd 0.01, best-dev @ 399 | fresh | 400 × 4 | 1e-3 | 7.41 → 2.62 | 3.06 → 0.74 | 0.009 → 1.12 | 0.06 (top-1 0.53) | 0.28 (top-1 0.69) | 0.34 | 0.66 | 0.06 / 0.43 / 0.63 | 147 min (shared GPU) |
| cf_pool3k_pair_own_bal_400 | as above + class-balanced L2, one own-prompt query, best-dev @ 299 | fresh | 400 × 4 | 1e-3 | 7.84 → 3.40 | 6.27 → 0.87 | 0.009 → 0.61 | 0.06 (top-1 0.42) | 0.06 (top-1 0.66) | 0.94 | 0.94 | 0.01 / 0.78 / 0.84 | 85 min |
| cf_pool3k_pair_own_loc_400 | as balanced + locality near-neighbour prompts as null targets, best-dev @ 399 | fresh | 400 × 4 | 1e-3 | 7.84 → 3.35 | 6.29 → 1.00 | 0.009 → 0.24 | 0.06 (top-1 0.38) | 0.03 (top-1 0.59) | 0.81 | 0.80 | 0.01 / 0.70 / 0.73 | 99 min |
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

## Non-learned revision condition on the zsRE stream (2026-09-14, 01:40 EDT)

Cosine firing threshold (v0's radius in cosine units) with the random tied reader, per-position deltas, hard top-1:

| min cosine | ES | RET-ES | RET-GS | LS |
| ---: | ---: | ---: | ---: | ---: |
| none | 1.00 | 1.00 | 0.65 | 0.24 |
| 0.90 | 1.00 | 1.00 | 0.65 | 0.98 |
| **0.93** | 1.00 | 1.00 | **0.65** | **1.00** |
| 0.95 | 1.00 | 1.00 | 0.65 | 1.00 |

Score populations with the random reader: own prompts 1.00, paraphrases mean 0.98 (p10 0.96), unrelated mean 0.86
(p90 0.89), so a fixed threshold separates them on this stream. This condition — stable observations, a siamese cosine
embedding of the tapped features (random weights), v0's per-prefix gradient writes, top-1 selection and a cosine gate —
has NO trained component and reaches RET-GS 0.65 with LS 1.00 against the controls' 0.44 (v0 live 0.24 / 0.29). It
becomes the reference condition ("R1-nonlearned") that the trained reader/null must beat; it also relocates the source of
the paraphrase gain to the observation geometry (write-free features at blocks 3/7/11, last position + prompt span,
cosine) rather than to learning. One seed, one order, 100 edits: development evidence only.

CounterFact development stream (same condition, `random_tied_cos_min0.93@counterfact`): ES 1.00, RET-ES 1.00, RET-GS 0.18,
LS 0.16. Here the untrained geometry fails on both counts: CounterFact paraphrases carry long distractor prefixes (mean
best cosine 0.95, p10 0.92) while the locality prompts are near-neighbours of the same relation (mean 0.97, p90 0.99), so
no fixed cosine threshold separates them. Two consequences: (1) the zsRE 0.65 is a property of zsRE's paraphrase/locality
structure, not a general result; (2) near-neighbour rejection needs a pairwise decision (query vs the best record —
same subject or not), whereas the current null logit is a function of the query alone and can only learn "this looks like
a near-miss prompt". A pairwise null head is the next design item if the trained reader does not separate near-misses.

## Trained tied-cosine reader on the streams (2026-09-14, 02:40 EDT): the query-only null rejects own prompts

`tiedcos_delta5_null0.5` (trained reader, deltas, null threshold 0.5): zsRE ES 0.02 / RET-GS 0.04 / LS 0.46; CounterFact
ES 0.08 / RET-GS 0.22 / LS 0.90. The null hard-nulls the items' OWN prompts (98 % zsRE, 92 % CounterFact): training
episodes never query a support's own prompt, and a query-only null cannot tell an own prompt from a near-miss prompt of
the same template. On zsRE the null is also inverted by domain shift (paraphrases 0.91 null mass, unrelated 0.11). Fixes:
(1) an `own_prompt` query role (support prompt → taught answer) in every training episode; (2) the pairwise null (run
`cf_pool3k_pairnull_400` in progress; `cf_pool3k_pair_own_400` launched with both). Deployment keeps the non-learned
cosine gate available as a fallback and the controls' numbers as the bar.

## Trained similarity under the non-learned gate (2026-09-14, 03:30 EDT)

After fixing the deployment write mass (binary: full write unless hard-nulled — the soft non-null mass had been scaling
deltas to zero whenever the null was confident, commit 5a37027), the pairwise-null weights with the trained null disabled
and the cosine gate 0.93:

| stream | reader | ES | RET-ES | RET-GS | LS |
| --- | --- | ---: | ---: | ---: | ---: |
| zsRE | random tied (reference) | 1.00 | 1.00 | 0.65 | 1.00 |
| zsRE | trained (cf_pool3k_pairnull) | 1.00 | 1.00 | 0.54 | 0.92 |
| CounterFact | random tied (reference) | 1.00 | 1.00 | 0.18 | 0.16 |
| CounterFact | trained (cf_pool3k_pairnull) | 1.00 | 1.00 | 0.02 | 0.04 |

Training the similarity on CounterFact episodes made the cosine geometry WORSE for gating on both streams: CounterFact
near-neighbour locality prompts now score 0.98 (above the gate) and paraphrases 0.72 (below it), and zsRE loses 0.11
RET-GS and 0.08 LS. The trained reader's value must come from its null decision, not from the cosine geometry; the
combined run (`cf_pool3k_pair_own_400`: pairwise null + own-prompt queries) is the test. If the trained null does not
transfer to zsRE, the next data decision is a zsRE training pool from MEND train (one paraphrase per item; own-prompt +
rephrase + locality queries), which would amend DEC-034(b) for training only.

## Combined reader (pairwise null + own-prompt queries) on the streams (2026-09-14, 04:15 EDT)

| stream | null threshold | ES | RET-ES | RET-GS | LS |
| --- | ---: | ---: | ---: | ---: | ---: |
| zsRE | 0.5 | 1.00 | 1.00 | 0.61 | 0.14 |
| zsRE | 0.3 | 1.00 | 1.00 | 0.60 | 0.14 |
| zsRE | 0.15 | 0.98 | 0.98 | 0.55 | 0.18 |
| CounterFact | 0.5 | 0.96 | 0.97 | 0.28 | 0.20 |
| CounterFact | 0.3 | 0.89 | 0.91 | 0.28 | 0.24 |
| CounterFact | 0.15 | 0.62 | 0.71 | 0.27 | 0.54 |

The own-prompt role removes self-rejection (ES 1.00 / 0.96) and the trained similarity now beats the random reader on
CounterFact paraphrases (RET-GS 0.28 vs 0.18; old-fact top-1 0.69 vs 0.53) — but the null became too permissive
(unrelated null mass 0.05 zsRE / 0.20 CounterFact; LS 0.14 / 0.20): five own-prompt queries per episode outnumbered the
two null-target queries 4:1 and the null threshold cannot recover locality without losing acquisition. Fix in training:
class-balanced L2 (null-target and record-target queries carry equal weight) and one own-prompt query per episode (the new
support); run `cf_pool3k_pair_own_bal_400`.

## Balanced reader on the streams (2026-09-14, 05:50 EDT): the trained null does not transfer to the streams

| stream | ES | RET-ES | RET-GS | LS | null mass own / paraphrase / unrelated |
| --- | ---: | ---: | ---: | ---: | --- |
| zsRE | 0.93 | 0.97 | 0.44 | 0.10 | 0.14 / 0.20 / 0.02 |
| CounterFact | 0.45 | 0.53 | 0.16 | 0.70 | 0.47 / 0.03 / 0.52 |

Inside CounterFact training-style dev episodes the balanced null is right (near-miss 0.78, unrelated 0.84, own 0.01), but on
the streams it is not: on zsRE it passes almost every unrelated prompt, on CounterFact it rejects half of the own prompts
and half of the locality prompts. The episodes' "unrelated" queries are other facts' prompts, whereas the streams' LS
prompts are the rows' locality near-neighbours (same relation, other subject), and a stream holds 100 records, not 5.
Fix in data: the new support's locality prompts join every training episode as null-target queries
(`--locality-queries`; run `cf_pool3k_pair_own_loc_400`). If the trained null still does not transfer, the learned
component reduces to the similarity and the null stays non-learned (the cosine gate) — the outcome X1-08 item 5 asks
us to prefer when the simpler measured control explains the gain.

## Locality-null reader on the streams (2026-09-14, 07:40 EDT) and the Stage 2 recommendation

| stream | ES | RET-ES | RET-GS | LS | null mass own / paraphrase / unrelated |
| --- | ---: | ---: | ---: | ---: | --- |
| zsRE | 0.89 | 0.92 | 0.43 | 0.12 | 0.20 / 0.24 / 0.05 |
| CounterFact | 0.53 | 0.60 | 0.16 | 0.50 | 0.42 / 0.01 / 0.54 |

With locality near-neighbours as null targets the null still does not transfer: on zsRE it passes nearly every unrelated
prompt; on CounterFact it rejects own prompts and locality prompts at about the same rate. Five trained readers
(tiedcos, pairnull, pair+own, balanced, locality) all fail the same way on the streams while behaving inside
training-style episodes, and the trained similarity under the non-learned gate was worse than the random reader.

**Recommendation (for the lead; DEC-038 proposal).** For the revision v1 comparative design, the learned reader is
dropped from the primary condition: the revision condition is the non-learned system — stable observations, the
random-initialized tied cosine embedding, per-position gradient writes under the v0 bound, hard top-1 selection and a
cosine gate — which on the zsRE development stream gives ES 1.00 / RET-ES 1.00 / RET-GS 0.65 / LS 1.00 against the controls'
0.44, and on CounterFact 1.00 / 1.00 / 0.18 / 0.16 (v0 live: 0.0 at the exact-key floor with LS 1.0). The learned reader
becomes a named secondary condition ("learned null", best available weights) reported honestly as not transferring.
CounterFact's near-neighbour locality remains unsolved by either; it is the open problem to state in the Stage 2 report,
with the pairwise-null failure mode documented. Stage 3 (cap-level PC energy) does not rest on a working learned reader
and can be scoped as a design note (R1-30a) rather than an implementation until this is resolved.

## Reference regenerated under fresh identities (2026-09-14, 08:10 EDT; X4-01/X4-10)

`ref_nonlearned_gate0.93_v2` (zsRE) and `ref_nonlearned_gate0.93_v2@counterfact`, run after the checkpoint-root guard fix:
zsRE ES 1.00 / RET-ES 1.00 / RET-GS 0.65 / LS 1.00; CounterFact 1.00 / 1.00 / 0.18 / 0.16 — identical to the earlier
summaries, now with per-dataset detail and checkpoint directories. The eight earlier zsRE summaries whose detail
directories were overwritten by CounterFact runs (X4-01) are historical: `random_tied_cos_min0.93`,
`tiedcos_delta5_null0.5`, `pairnull_delta5_null0.5`, `pairnull_delta5_gate0.93`, `pairnull_delta5_gate0.93_bin`,
`pairown_delta5_null0.5`, `pairown_delta5_null0.3`, `pairown_delta5_null0.15`. Wording corrections from the review
(X4-02..08) are recorded in `docs/tasks/R1-X4-response.md`: cost columns are wall times; the fact-code result is a negative
for the tested configurations; the zsRE 0.65 is a one-stream development comparator attributed to the observation
geometry and the per-position write rule; delta bytes scale with answer tokens (≈ 37 KB per 4-token record).

## Learned-reader recovery plan (2026-09-14, 08:40 EDT; lead directive: make the learned reader work before other issues)

Why the trained nulls fail on the streams while passing training-style episodes — four mismatches, each with a fix:

| # | mismatch (episode → stream) | fix | who |
| --- | --- | --- | --- |
| M1 | memory of 5 records → 100 records; the pairwise null was never shown a best-key drawn from a large memory | **stream-scale training episodes**: a memory of 64–128 pool records per episode with queries drawn from IN-memory records (own prompt, paraphrases, their locality prompts as nulls) and from OUT-of-memory facts (their prompts as nulls); a feature bank caches every pool item's observations once so 100-record episodes cost no extra base passes | orchestrator (R1-50) |
| M2 | null targets = other facts' prompts → stream LS prompts = the items' own locality near-neighbours | stream episodes take null queries from the locality prompts of records IN memory (the exact LS population) and from out-of-memory prompts | orchestrator (R1-50) |
| M3 | CounterFact-only training → zsRE domain shift (zsRE null inverted) | a **zsRE training pool** (3,000 items from the D1c clear candidates, one rephrase + locality each, E.2-filtered by the teacher; exposure recorded, excluded from the fresh draw) and mixed-domain training | Codex prepares the list (R1-D3), orchestrator runs E.2 and trains |
| M4 | the null sees only tapped-feature geometry; near-neighbours share the relation and differ in the subject, which mean-pooled span features blur | a **lexical pairwise feature** (overlap of the query's tokens with the record's support-prompt tokens, common tokens excluded) fed to the null head, and max-pooled prompt-span features beside the mean | orchestrator (R1-51); Codex quantifies separability first (R1-45) |
| M5 | null threshold 0.5 = balanced-episode calibration ≠ deployment prevalence | per-dataset threshold selected on a development stream and reported as such; the confirmatory streams are fresh | orchestrator (R1-52) |

Order: R1-50 (M1+M2) first with the CounterFact pool, evaluated on both streams; then M4; then M3 when the zsRE pool is
ready; M5 last. Success criterion (X4-07): a learned null re-enters the primary condition only if it beats the cosine
gate's LS on BOTH streams without losing RET-GS on a fresh development draw. Until then DEC-038's default stands.

## M1+M2+M4 together: the learned reader beats every control on CounterFact (2026-09-14, 11:05 EDT)

Run `r1_50_stream_lex` (stream-scale episodes over a 1,000-item CounterFact feature bank, 64-record memories, in-memory
locality near-neighbours and out-of-memory prompts as null targets; tied cosine reader + pairwise null + lexical overlap
feature with stop list v1; 300 steps × 2 episodes, 2 min of training; best held-out retrieval CE 0.40):

| stream | ES | RET-ES | RET-GS | LS | null mass own / paraphrase / unrelated |
| --- | ---: | ---: | ---: | ---: | --- |
| CounterFact | 1.00 | 1.00 | **0.775** | **1.00** | 0.17 / 0.19 / 1.00 |
| zsRE | 0.98 | 0.98 | 0.49 | 0.98 | 0.20 / 0.52 / 0.87 |

For reference on CounterFact: v0 live 0.00 (exact-key floor, LS 1.0), v0-stable / matched-update 0.00, non-learned
revision 0.18 / 0.16. The lexical diagnostic explains the gain: on the bank, overlap alone ranks a paraphrase's own record
first 94 % of the time while locality near-neighbours overlap their item's prompt at 0.035 (paraphrases 0.48); the tapped
features alone ranked the own record ~100th of 400. On zsRE the same reader now rejects half the paraphrases (rewordings
with lower overlap; CounterFact-only training) — M3 (zsRE-domain training pool) and M5 (per-dataset threshold) are the
next steps for zsRE, where the non-learned gate still holds 0.65 / 1.00.

zsRE null-threshold sweep with the same weights (`r1_50_lex_null*`): 0.5 → RET-GS 0.49 / LS 0.98; 0.7 → 0.62 / 0.92;
0.85 → 0.77 / 0.82; 0.95 → 0.86 / 0.64. The trained similarity is strong on zsRE too (0.86 with the null nearly off, vs
0.65 for the non-learned gate); the CounterFact-trained null is what is miscalibrated there (M3/M5).

Combined rules (2026-09-14, 11:40 EDT), same weights: on zsRE the cosine gate 0.93 with the null off gives **ES 1.00 /
RET-ES 1.00 / RET-GS 0.97 / LS 1.00** (null 0.95 + gate: 0.85 / 1.00); on CounterFact the gate is harmful (paraphrase mean
cosine 0.85 < gate; RET-GS 0.14–0.21) while the learned null alone gives 0.775 / 1.00. So the trained similarity is
excellent on both datasets; the locality decision is the only open piece: the CounterFact-trained null over-rejects zsRE
paraphrases, and the cosine geometry that separates zsRE unrelated prompts (0.74 vs 0.98) does not separate CounterFact
near-neighbours (0.98 vs 0.85). One rule for both datasets needs the null trained on both domains (M3) — or a null that
does not depend on the query's style (dropping the query-only linear term; tested next).

Seed robustness (CounterFact, null 0.5): seed 0 → RET-GS 0.775 / LS 1.00; seed 1 → 0.93 / 0.92 (the null's operating
point varies with the seed; the similarity does not). Seed 2 and a query-style-free null variant (pairwise + lexical terms
only) follow.

## Seeds and the query-style-free null (2026-09-14, 12:20 EDT)

| reader (stream-scale + lexical) | CounterFact null 0.5 | zsRE null 0.5 | zsRE gate 0.93, null off |
| --- | ---: | ---: | ---: |
| seed 0 | 0.775 / 1.00 | 0.49 / 0.98 | 0.97 / 1.00 |
| seed 1 | 0.93 / 0.92 | — | — |
| seed 2 | 0.93 / 1.00 | 0.68 / 0.82 | 0.97 / 0.96 |
| seed 0, query-style-free null | 0.93 / 1.00 | 0.94 / 0.38 | — |

(RET-GS / LS; ES and RET-ES are 1.00 in every cell.) Three seeds put CounterFact at RET-GS 0.78–0.93 with LS 0.92–1.00
against a 0.00 floor. Dropping the query-only null term (pairwise + lexical terms only) keeps CounterFact at 0.93 / 1.00
and removes the over-rejection of zsRE paraphrases (RET-GS 0.94) but then passes zsRE's unrelated prompts (LS 0.38): the
zsRE locality population (unrelated facts, low overlap with any record, moderate cosine) is what the CounterFact-trained
pairwise term does not reject. A null trained on both domains (M3) is the remaining step to one rule for both datasets.

Query-style-free null on zsRE, threshold sweep: 0.15 → 0.86 / 0.64; 0.25 → 0.88 / 0.50; with the cosine gate (null off)
0.95 / 1.00. State of play: similarity solved on both datasets (zsRE 0.95–0.97, CounterFact 0.93 with LS 1.00 under the
right locality rule); the locality rule is dataset-specific until the null is trained on both domains (M3, waiting on the
zsRE training pool, Codex R1-D3 → `scripts/r1_d3_e2_filter.py`). If M3 does not unify the rule, the fallback is a
per-dataset rule fixed on development streams before the freeze (M5), stated as such in the protocol.

## M5 operating points (seed-2 reader; development streams; LS ≥ 0.99) — 2026-09-14, 13:05 EDT

`scripts/r1_52_operating_point.py` over 7 null thresholds × {no gate, gate 0.93}: CounterFact → null 0.7, no gate:
RET-GS 0.935 / LS 1.00; zsRE → null 0.95 + gate 0.93: RET-GS 0.95 / LS 1.00
(`results/R1/operating_point_*_r1_50_stream_lex_s2.json`). Development-stream choices (one stream, one order each); under
the fallback protocol they are fixed before the freeze and the confirmatory streams are fresh draws. The single-rule
version (null trained on both domains, M3) is still preferred and waits on the zsRE pool.

Second development streams (seed 22: a different 100 of the 300 development items, overlap 36 / 33 with the seed-21 streams),
same seed-2 reader and the chosen rules: CounterFact null 0.7 → ES 1.00 / RET-ES 1.00 / RET-GS 0.935 / LS 1.00; zsRE null
0.95 + gate 0.93 → 1.00 / 1.00 / 0.95 / 1.00 — numerically the same as on the calibration streams (coincidence to three
decimals; the item sets differ). One order each; still development evidence, but the operating points are not tuned to
one particular stream.
