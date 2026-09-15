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

## M3: one null for both domains (2026-09-14, 14:50 EDT)

`r1_50_stream_mixed`: mixed bank (1,000 CounterFact + 1,000 zsRE training-pool items, DEC-037/039), 64-record memories
drawn from both pools, 300 steps × 2 (2 min); best held-out retrieval CE 0.19. Learned null alone, no gate, one threshold:

| stream | null 0.5 | null 0.7 |
| --- | ---: | ---: |
| zsRE | ES 1.00 / RET-ES 1.00 / RET-GS **0.98** / LS **1.00** | 1.00 / 1.00 / 0.98 / 1.00 |
| CounterFact | 1.00 / 1.00 / **0.795** / **1.00** | 1.00 / 1.00 / 0.805 / 1.00 |

Against v0 live (zsRE 0.24–0.29, CounterFact 0.00) and the non-learned controls (0.44 / 0.18): the learned reader with
stream-scale mixed-domain training and the lexical feature is the primary revision condition with a single deployment
rule. The recovery plan's five mismatches are all addressed (M1/M2 stream episodes, M3 mixed domains, M4 lexical feature,
M5 no longer needed for the rule). Seeds and second streams follow.

Second development streams (seed 22), mixed reader, null 0.5: zsRE 1.00 / 1.00 / 0.99 / 1.00; CounterFact 1.00 / 1.00 /
0.765 / 1.00. Seed replicates of the mixed training are running.

Seed replicates of the mixed-domain reader (null 0.5, no gate; RET-GS / LS; ES and RET-ES ≥ 0.99 everywhere):

| seed | zsRE (stream 21) | CounterFact (stream 21) |
| --- | ---: | ---: |
| 0 | 0.98 / 1.00 | 0.795 / 1.00 |
| 1 | 0.96 / 1.00 | 0.78 / 1.00 |
| 2 | 0.97 / 1.00 | 0.785 / 1.00 |

Three seeds and two streams agree: zsRE 0.96–0.99, CounterFact 0.765–0.805, LS 1.00 throughout, one rule. This is the
condition to carry into the run matrix (R1-40b) and the freeze (R1-41).

Occupancy 250 (R50-07), mixed reader, null 0.5: zsRE 1.00 / 1.00 / 0.98 / 1.00; CounterFact 1.00 / 1.00 / 0.722 / 1.00
(from 0.795 at 100 records). Locality holds at 2.5× occupancy; CounterFact paraphrase retention loses about 0.07,
consistent with more near-neighbour records competing for the same subject-free features. Codex's R1-46 review is
answered in `docs/tasks/R1-46-response.md` (R50-04/06/08/09 repaired).

## Scale profile by memory size (R50-07; mixed reader, null 0.5, banks; `results/R1/scale_profile_r1_50_stream_mixed.json`)

| memory | zsRE paraphrase fires own / in top-4 | zsRE locality hard-null | zsRE out-of-memory hard-null | CounterFact paraphrase fires own / in top-4 | CounterFact locality hard-null | CounterFact out hard-null |
| ---: | --- | ---: | ---: | --- | ---: | ---: |
| 64 | 1.00 / 1.00 | 1.00 | 0.92 | 0.72 / 0.88 | 0.97 | 1.00 |
| 100 | 0.98 / 1.00 | 1.00 | 0.87 | 0.81 / 0.95 | 0.99 | 1.00 |
| 300 | 0.99 / 1.00 | 1.00 | 0.67 | 0.80 / 0.90 | 0.99 | 0.98 |
| 1,000 | 0.98 / 1.00 | 1.00 | — | 0.59 / 0.73 | 0.98 | — |

Reading: the null is stable with memory size on both datasets (locality hard-null ≥ 0.97 everywhere); two scale effects
remain. (a) CounterFact candidate recall: at 1,000 records the own record is outside the top-4 for 27 % of paraphrases,
so the loss is retrieval, not the null — a larger candidate set is the cheap fix (tested next). (b) zsRE out-of-memory
prompts (edit-like prompts of facts not in memory) are accepted more often as memory grows (hard-null 0.92 → 0.67 at
300): a near-duplicate record with high lexical overlap wins. This population is not in the current LS endpoint (NQ
locality prompts) but is the right stress test for a fresh-draw protocol; recorded as an open risk for R1-40b.

Top-16 candidates on CounterFact (`scale_profile_r1_50_stream_mixed_top16.json`): in-candidate recall at 1,000 records
rises 0.73 → 0.895 but "fires the own record" only 0.59 → 0.64 and locality hard-null slips 0.98 → 0.925: at that scale
the limit is the selection among near-duplicate candidates, not retrieval. The lever is training with larger memories
(256-record episodes; run `r1_50_stream_mixed_m256`, profiled and evaluated next).

256-record training (`r1_50_stream_mixed_m256`; 16 query records + 16 out-of-memory nulls per episode): streams zsRE
1.00 / 1.00 / 0.97 / 1.00, CounterFact 1.00 / 1.00 / 0.83 / 0.98; profile at 1,000 records: CounterFact fires-own 0.625
(64-record training: 0.59), zsRE out-of-memory hard-null 0.59 / 0.50 at 100 / 300 (64-record training: 0.87 / 0.67). A
modest CounterFact gain at scale, a small LS cost and a worse unseen-prompt rejection on zsRE — not a clear improvement;
the 64-record mixed reader (seeds 0–2) stays the reference configuration, and the scale effects stay recorded as
protocol risks for the run matrix (memory sizes and an unseen-edit-prompt endpoint).

## R1-24 teacher-only continuation control — both treatments run (DEC-040; 2026-09-14, 12:15 EDT)

Budget: 771,581 forward-pass tokens (the reference reader's re-executed training ledger 458,002 + feature-bank
construction 313,579; reverse positions 458,002 reported separately). Evaluation: the same two 100-edit development
streams, S0 = original base + v0-stable cap, S1 = continued base + v0-stable cap, R0/R1 = original/continued base +
reference reader; LS is scored against the ORIGINAL base's answers in every cell (common reference).

| treatment | fidelity (held-out tail) | zsRE S0 → S1 (RET-GS / LS) | zsRE R0 → R1 | CounterFact S0 → S1 | CounterFact R0 → R1 |
| --- | --- | --- | --- | --- | --- |
| literal self-KD (3,014 steps) | KL 3e-5, ΔNLL −6e-5: pass | 0.44 / 1.00 → 0.49 / 1.00 | 0.98 / 1.00 → 0.98 / 1.00 | 0.00 / 1.00 → 0.00 / 0.92 | 0.795 / 1.00 → 0.795 / 0.92 |
| LM continuation (6,028 steps, lr 1e-6) | KL 0.095, ΔNLL −0.105: **fail** | 0.44 / 1.00 → 0.39 / 0.86 | 0.98 / 1.00 → 0.97 / 0.88 | 0.00 / 1.00 → 0.00 / 0.28 | 0.795 / 1.00 → 0.775 / 0.28 |

Reading (DEC-033 margins: RET-GS 0.05, ES −0.02, LS −0.01). Continued-base training does not explain the revision's
gain: with the no-op control S1−S0 is +0.05 (zsRE) and 0.00 (CounterFact) while R0−S1 stays +0.49 and +0.795; the
informative continuation moves S1 in the wrong direction (−0.05 / 0.00) and R0−S1 stays +0.59 / +0.795. The informative
treatment fails its pre-registered fidelity gate (the base's own held-out distribution moved by 0.095 nats, i.e. the
budget at lr 1e-6 is a substantial base change), so it is not a valid matched control as run: the LS collapse under it
(0.86 / 0.28) is the base answering its own locality prompts differently, not the cap's damage — the same collapse
appears with no cap writes at all (S1 rows). A valid informative control needs a KL-bounded continuation (smaller step or
a KL penalty to the original) that passes fidelity; that is a follow-up, not a Stage 4 blocker. Two side findings:
(1) the reference reader keeps its retention on a substantially changed base (0.97 / 0.775) — robustness to base drift;
(2) even the no-op control moved CounterFact's LS by 0.08 through floating-point residuals of 3e-5 nats, which says the
50-prompt complete-answer LS metric is sensitive to near-tie answers; report it with its step size.

## R1-54: ordinary-text drift of the learned cap — diagnosis and fix (2026-09-14, 13:20 EDT)

Codex's report addendum found the reference reader raises ordinary-text loss after edits (+0.60 nats zsRE / +0.39
CounterFact on the R1-24 drift subset). Reproduced with per-position selection on 32 fixed-prefix windows after the
100-edit zsRE stream (`scripts/r1_54_drift_assay.py`; a first version that let sliding prefixes inherit the first
token's selection showed zero drift and is filed as an artifact — ordinary text has no query boundary):

| reader / rule | firing on ordinary prefixes | Δ NLL (nats) | perplexity ratio | zsRE RET-GS / LS | CounterFact RET-GS / LS |
| --- | ---: | ---: | ---: | ---: | ---: |
| reference (mixed), null 0.5 | 0.365 | +0.647 | 1.91 | 0.98 / 1.00 | 0.795 / 1.00 |
| reference + cosine floor 0.3 | 0.010 | +0.048 | 1.05 | — | — |
| reference + cosine floor 0.5 | 0.010 | +0.002 | 1.002 | — | — |
| **trained with ordinary-text nulls** (`r1_50_stream_mixed_text`), null 0.5 | **0.000** | **0.000** | **1.000** | 0.96 / 1.00 | 0.725 / 1.00 |

Cause: the null was never shown low-similarity text (best cosine to any record ≈ 0.17 on ordinary prefixes) and fired
on 36 % of it; 8 ordinary-text null queries per episode (512 OpenWebText training-range windows × 3 prefix lengths,
cap-off logits kept for the preservation KL) remove the firing entirely at no cost to zsRE and a 0.07 dip on CounterFact
(one seed; the seed range of the reference was 0.765–0.805). v0's drift ratios were 1.001–1.004; the cosine floor 0.5 is
kept as a non-learned fallback rule. Seed replicates of the text-null reader and its CounterFact-edit drift follow; if
they hold, it becomes reference condition v2.

## R1-43 / R1-44 endpoints on the real base with the text-null reader (2026-09-14, 13:00 EDT)

Owner adapters for Codex's endpoint modules (`scripts/r1_43_endpoints_run.py`, `scripts/r1_44_unseen_run.py`), run with
the ordinary-text-null reader (seed 0, `r1_50_stream_mixed_text`), null 0.5, lexical stop list v1, 5 delta steps; every
case restores a clone of the starting state (`results/R1/endpoints/text_s0_v1*/`).

| endpoint | population | n | result |
| --- | --- | ---: | --- |
| near-miss preservation (R1-43) | CounterFact near-neighbour rows from `manifests/dev/challenges.json` | 100 | preserved 100/100 (neighbour decoded text identical to cap-off); edited prompt exact 100/100; the neighbour query never fired (null mass ≥ 0.99998) |
| revision (R1-43) | temporal-correction rows (v1 then v2 of the same fact) | 100 | revision success 100/100 (old acquired, old record retired, new record active, latest answer exact); old answer reappeared 0/300 queries; paraphrase exactness of the new answer 0.79 (mean over 2 paraphrases per case) |
| composition (R1-43) | direct composition questions | 54 avail. | unreachable: no verified direct composition questions (two-hop chains are diagnostic only); shortfall 46 |
| unseen edit-prompt (R1-44), zsRE | 100 original prompts of un-edited dev items after 100 edits | 100 | false fires 7/100 (all with answer changes); complete-answer preservation 0.93; all 200 answers terminated |
| unseen edit-prompt (R1-44), CounterFact | same after 100 CounterFact edits | 100 | false fires 0/100; answer changes 0/100; 33 pairs hit the 32-token limit in both cap-off and cap-on decoding (base behaviour, not a cap effect), so the complete-pair preservation denominator is 67 |

Costs: R1-43 (200 cases) 151 s wall, 9.5k full forwards; each R1-44 dataset ≈ 75 s. The zsRE unseen rate (7 %) is the
declared scale risk (out-of-memory hard-null 0.87 → 0.67 at 300 in the bank profile); the 300/1,000-record points are
what R1-40c's P3 profile must measure with the same adapter.

## Text-null reader: seeds and CounterFact-edit drift → reference condition v2 (2026-09-14, 13:15 EDT)

| seed | zsRE ES / RET-ES / RET-GS / LS | CounterFact ES / RET-ES / RET-GS / LS | training wall |
| --- | --- | --- | ---: |
| 0 (`r1_50_stream_mixed_text`) | 1.00 / 1.00 / 0.96 / 1.00 | 1.00 / 1.00 / 0.725 / 1.00 | — |
| 1 | 1.00 / 1.00 / 0.98 / 1.00 | 1.00 / 1.00 / 0.85 / 1.00 | 351 s |
| 2 | 1.00 / 1.00 / 0.96 / 1.00 | 1.00 / 1.00 / 0.79 / 1.00 | 368 s |

Stream 21, 100 edits, null 0.5, no gate. The v1 reference's range was zsRE 0.96–0.99 and CounterFact 0.765–0.805, so
the ordinary-text nulls cost nothing on zsRE and leave CounterFact inside its seed spread (0.725–0.85 vs 0.765–0.805).

Ordinary-text drift after 100 **CounterFact** edits (32 windows × 128 positions, per-position selection):

| reader | firing at probe lengths 16/48/96 | Δ NLL (nats) | perplexity ratio |
| --- | ---: | ---: | ---: |
| v1 reference (`r1_50_stream_mixed`) | 0.490 | +0.379 | 1.461 |
| text-null reader (seed 0) | 0.000 | +0.012 | 1.012 |

The +0.012 with no firing at the three probe lengths means a small number of positions at other prefix lengths still
fire after CounterFact edits: the recount over every scored position (`drift_assay_text_counterfact_v2.log`) finds 14 of
4,064 positions firing (0.34 %), which is the whole residual.
v0's drift ratios were 1.001–1.004; 1.012 is reported as a residual, not zero. The text-null reader is promoted to
**reference condition v2** (`manifests/revision_v1/primary_condition_v2.json`; v1 is kept as the R1-54 comparison).

## R1-40c P1 edit/memory profile on the real base (`scripts/r1_55_p1_profile.py`; `results/R1/p1_profile/`)

1,000 edits per dataset in one stream (300 dev items, seed 21, then labelled training-pool rows beyond index 1,000 as
fillers; no fresh candidate opened), reference reader v2 (seed 0) and the non-learned control (random tied reader,
cosine gate 0.93); query profiles of 100 greedy decodes (50 own prompts, 50 locality prompts) at 100/300/1,000 active
records; export → import → export restore check at every checkpoint. All 4,000 edits were accepted; no capacity
failure.

| quantity | zsRE | CounterFact |
| --- | --- | --- |
| cold first edit (compilation) | 3.5 s | 3.4 s |
| warm edit p50 / p95, occupancy [0,100) | 0.130 / 0.287 s | 0.070 / 0.111 s |
| warm edit p50 / p95, occupancy [300,1000) | 0.111 / 0.222 s | 0.073 / 0.080 s |
| warm edit logical cost p50 (full forwards / reverses / tokens) | 19 / 7 / 232 | 12 / 4 / 103 |
| warm edit p50 by answer positions [2,4) / [4,8) / [8,33) | 0.081 / 0.150 / 0.260 s | 0.073 / — / — |
| query p50 / p95 at 100 records (greedy, ≤ 32 tokens) | 12.5 / 38 ms | 10.0 / 62 ms |
| query p50 / p95 at 1,000 records | 14.4 / 29 ms | 14.6 / 66 ms |
| per decode step p50 at 100 → 1,000 records | 3.8 → 5.3 ms | 4.4 → 6.8 ms |
| persistent state at 100 / 300 / 1,000 records (weights 13.39 MB included) | 17.3 / 24.6 / 49.9 MB | 15.5 / 19.6 / 34.0 MB |
| fraction of the 64 MiB ceiling at 1,000 records | 0.744 | 0.507 |
| delta bytes at 1,000 records (answer positions mean / max) | 34.3 MB (3.7 / 14) | 18.4 MB (2 / 2) |
| restore hash and byte equality at every checkpoint; import time at 1,000 | yes; 7 ms | yes; 6 ms |
| own-prompt firing at 100 / 300 / 1,000 (v2 reader) | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 |
| locality-prompt firing at 100 / 300 / 1,000 (v2 reader) | 0.00 / 0.00 / 0.00 | 0.00 / 0.06 / 0.10 |
| process RSS / device peak | 2.3 GB / 763 MiB | 2.2 GB / 752 MiB |
| whole profile wall (1,000 edits + 300 queries + 3 restores) | 140 s | 90 s |

Edit cost does not depend on occupancy (selection is not part of an edit); it scales with answer length (each answer
position costs one prefix forward + reverse per delta step). Query cost grows slowly with occupancy through the
lexical-overlap term (a Python loop over all records per prefix). The worst-case 32-position record costs 294,912 delta
bytes; at the observed answer-length distributions 1,000 records use 51–74 % of the ceiling, so the 1,000-edit
endpoint is admissible on both datasets without eviction. The one scale signal is CounterFact locality firing rising to
6 % at 300 and 10 % at 1,000 records under the v2 reader (0 % at 100) — the near-duplicate risk already flagged from
the bank profile, now measured on the real base with decoding; LS at 1,000 CounterFact records will not stay at 1.00.
Ledger accelerator seconds (57 s zsRE, 38 s CounterFact) are the charged base-call time; the wall includes Python
selection, decoding and restore work, so ceilings must be set from wall time. The non-learned control has the same
edit and query costs; under its own cosine gate (`nonlearned_v2`) it fires on 0 % of zsRE locality prompts and on 86–100 %
of CounterFact locality prompts at every occupancy — the LS 0.16 of §4.1 seen from the selection side.

## Unseen edit-prompt endpoint by memory size (R1-44 adapter; v2 reader; `results/R1/endpoints/text_s0_n*_unseen_*/`)

Memory = the dev stream (300 items) extended with training-pool rows beyond index 1,000 as labelled fillers; outside
prompts = 100 pool rows never edited (`--outside-from-pool`); at 100 records the earlier run used dev-remainder prompts.

| dataset | records | outside source | false fires | answer changes | complete pairs | wall |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| zsRE | 100 | dev remainder | 7 % | 7 | 100 | 73 s |
| zsRE | 100 | training pool | 12 % | 12 | 100 | 72 s |
| zsRE | 300 | training pool | 25 % | 25 | 100 | 98 s |
| zsRE | 1,000 | training pool | 45 % | 45 | 99 | 200 s |
| CounterFact | 100 | dev remainder | 0 % | 0 | 67 | 77 s |
| CounterFact | 100 | training pool | 0 % | 0 | 65 | 73 s |
| CounterFact | 300 | training pool | 2 % | 2 | 71 | 86 s |
| CounterFact | 1,000 | training pool | 5 % | 5 | 70 | 148 s |

Every false fire changed the answer. zsRE's acceptance of edit-style prompts about facts not in memory grows steeply
with occupancy (7 → 25 → 45 %); CounterFact stays low (0 → 2 → 5 %). Prompt source matters less than size: with pool-sourced prompts at 100 records zsRE
fires on 12 % (dev remainder 7 %), so the size effect is 12 → 25 → 45 % on one source. Every false fire at 300 and
1,000 records is a same-relation, different-subject prompt (the fired record's subject appears in the query in 0 of
70 cases; the query and record share 2.2 template words on average, e.g. "What company published The Firebrand?" fires
"What company published Nail'd? → Deep Silver"): at 1,000 records almost every relation template has a stored
record, and template overlap counts fully in the lexical feature. CounterFact's incomplete pairs are
the base's untruncated answers (the 32-token limit), not a cap effect. This is the largest open scale risk for the
1,000-edit endpoint and is a protocol fact, not a bug: the reader was trained with 64-record memories and
out-of-memory nulls drawn at that scale.

## R1-56: a memory-rare overlap gate against same-template false fires (2026-09-14, 13:50 EDT)

Non-learned deployment rule (`RevisionConfig.rare_overlap_min`, `rare_df_max=2`): after the learned decision, the query
must share at least `rare_overlap_min` distinct non-stop tokens with the selected record's support prompt, counting
only tokens that occur in at most two active records (document frequency over the current memory, recomputed as it
grows). Template words are common at any useful occupancy; subject tokens are rare. CPU test in
`tests/revision_v1/test_learner_cpu.py`; the gate is part of the semantic configuration bound into snapshots.

| condition | zsRE stream RET-GS / LS | CounterFact stream RET-GS / LS | zsRE unseen false fires at 100 (dev) / 300 / 1,000 | CounterFact unseen at 1,000 |
| --- | --- | --- | --- | --- |
| v2 reader, no gate | 0.96 / 1.00 | 0.725 / 1.00 | 7 % / 25 % / 45 % | 5 % |
| v2 + rare overlap ≥ 1 | 0.96 / 1.00 | 0.715 / 1.00 | 5 % / 11 % / 10 % | 0 % |
| v2 + rare overlap ≥ 2 | 0.94 / 1.00 (ES 0.99) | 0.62 / 1.00 (ES 0.98) | 3 % / — / 1 % | — |

Every false fire still changes the answer. The gate removes the growth with memory size at a cost of at most one
CounterFact paraphrase (0.715 vs 0.725; ES, RET-ES and LS unchanged). The ten residual zsRE fires at 1,000 records
share one token that happens to be rare in memory: a relation word with one or two stored records ("established",
"dissolve", "stars", "School"), a subword fragment ("CJ", "og") or a capitalized stop word the list misses ("Is",
"of"). The two-token variant removes almost all of them (1 % at 1,000) but rejects single-token subjects on their own
prompts (ES 0.99 / 0.98, CounterFact RET-GS 0.62), so it is not acceptable. **Recommendation:** v2 reader + rare
overlap ≥ 1 as the primary condition (`manifests/revision_v1/primary_condition_v3.json`, DEC-043 proposed); the
residual 10 % at 1,000 records is reported as the endpoint's development value. A stop list with capitalized forms is
a possible data fix before the freeze (it would change the lexical feature the reader was trained with, so it would
need a retrain; not done).

Seed coverage of the gated condition (v3; `mixed_text_s{1,2}_rare1_*`, `text_s{1,2}_rare1_n1000_unseen_zsre`,
`endpoints/text_s0_rare1_v1`): seeds 1 and 2 keep exactly their ungated stream results (zsRE 0.98 / 0.96, CounterFact
0.85 / 0.79, ES / RET-ES / LS 1.00) and fire on 10 % / 11 % of unseen zsRE prompts at 1,000 records (seed 0: 10 %);
near-miss preservation 100/100, revision 100/100 (new-answer paraphrase exactness 0.79, reappearance 0) are unchanged
under the gate. v3 = v2 weights + gate is therefore fully characterised on the development streams: zsRE RET-GS
0.96–0.98, CounterFact 0.715–0.85, LS 1.00, unseen false fires 10–11 % at 1,000 zsRE records, 0 % CounterFact.

### R1-24 qualifications from Codex's review (R1-X7, applied 2026-09-14, 17:15 EDT)

Codex's review of the execution records (`logs/review_r1_24.md`) reconciles all 16 cells and 9,042 accepted steps and
asks for three qualifications to the R1-24 section above, which stand as written here: (1) the S1 cells carry an
active v0-stable cap, so S1−S0 measures the continued base under that cap, not a bare base; (2) the literal
self-distillation run does change parameters (floating-point residuals of 3e-5 nats), so it is a numerical
near-no-op, not an identity; (3) the informative LM treatment's fidelity gate remains failed regardless of its improved
held-out NLL — a fidelity-valid S1_LM needs a KL-bounded recipe or an explicit scope amendment before it can be a
Stage 4 condition (U03 in the protocol draft).

## Third dataset: MQuAKE-CF chosen over WikiFactDiff and RippleEdits (DEC-045; 2026-09-14, 17:40 EDT)

The strict register v3 leaves no fresh CounterFact item (every CounterFact subject is in the old eligible pool), so the
lead asked for an external source. Three were inspected from the network (copies in the session scratchpad only;
nothing under `assets/` until the lead's approval):

| source | licence | usable items | paraphrases | locality | answers (GPT-2 tokens) | verdict |
| --- | --- | ---: | --- | --- | --- | --- |
| MQuAKE-CF (Princeton, 2023) | MIT | 7,236 unique (subject, relation) counterfactual rewrites, 6,043 on subjects outside register v3; 37 relations | question form of each cloze prompt; aliases from `new_single_hops` | same-relation prompts of other subjects (CounterFact convention) | 77 % ≤ 3 tokens | **chosen**: CounterFact-like construction, short answers, and 9,218 verified two-hop questions (3 paraphrases each) for the composition endpoint |
| WikiFactDiff (Orange, 2024) | CC-BY-SA-4.0 | 32,873 replacement updates but only 5,031 with entity objects (4,813 unexposed); 157 relations | 4 templates per update | 3 neighbour facts per update | median 5 tokens, 19 % ≥ 8 | real-world updates 2021→2023 (unknown to GPT-2): a different claim; long answers; kept in mind for a later stage |
| RippleEdits (2023) | MIT | 4,755 edits (1,948 recent / 1,922 random / 885 popular) | subject-aliasing tests for 731 of the recent edits only | relation-specificity tests for most | — | prompts ship with the subject blanked (Wikidata id only): label lookups needed; thinner coverage |
| KnowEdit WikiData_counterfact | MIT | 2,340 | subject aliasing | relation specificity | — | too small |

MQuAKE-CF subjects overlap CounterFact's by 837 and the register by 924 (removed in the 6,043 count); overlap with the
zsRE pools is 22 subjects. The lead keeps CounterFact (hence the DEC-042 exception) and adds MQuAKE-CF as the third
dataset; the matrix becomes 360 cells. Codex lane R1-D4 prepares the items; the orchestrator's teacher pass follows
(zsRE rule: the base's greedy answer must not already match the new answer; one paraphrase suffices, as for zsRE).

## R1-24 follow-up: a fidelity-valid informative continuation exists at lr 1e-8 (2026-09-14, 20:40 EDT)

Same recipe as `r1_24_control_lm_v2` (Adam, seed 1729, 771,581 forward-pass tokens of the training shard, 128-token
sequences) at smaller learning rates (`manifests/revision_v1/r1_24_control_lm_v3_lr*.json`; gate: KL ≤ 0.001 nats and
NLL increase ≤ 0.01 on the held-out tail; S = v0-stable cap, R = revision cap v1 reader; LS against the original base):

| weight lr | KL (nats) | ΔNLL | gate | zsRE S0 → S1 (RET-GS / LS) | zsRE R0 / R1 | CounterFact S0 → S1 | CounterFact R0 / R1 |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| 1e-6 (v2) | 0.0950 | −0.105 | fail | 0.44/1.00 → 0.39/0.86 | 0.98/1.00 / 0.97/0.88 | 0.00/1.00 → 0.00/0.28 | 0.795/1.00 / 0.775/0.28 |
| 1e-7 | 0.0186 | −0.054 | fail | 0.44 → 0.45/0.94 | 0.98 / 0.98/0.94 | 0.00 → 0.00/0.64 | 0.795 / 0.795/0.64 |
| 3e-8 | 0.0043 | −0.026 | fail | 0.44 → 0.45/0.98 | 0.98 / 0.98/0.98 | 0.00 → 0.00/0.82 | 0.795 / 0.795/0.82 |
| **1e-8** | **0.0005** | −0.009 | **pass** | 0.44 → 0.45/0.98 | 0.98 / 0.98/0.98 | 0.00 → 0.00/0.88 | 0.795 / 0.795/0.88 |

KL scales as ≈ lr^1.3 over this range. At lr 1e-8 the continuation passes the pre-registered gate while still
lowering the held-out NLL by 0.009 nats, so it is a certified informative control (U03 closes by data: S1_LM =
`r1_24_control_lm_v3_lr1e-8`). Its verdict is the same as the literal control's: S1−S0 is +0.01 / 0.00 and R0−S1 is
+0.53 / +0.795, so continued training of the base on the matched budget does not produce the revision's gain. The LS
column on the continued base is measured against the original base's answers: even a 0.0005-nat move changes 12 % of
the CounterFact locality decodes (near-tie answers), which is why the protocol keeps the original base as the common
LS reference and reports the S1 rows with their base shift. Runs `results/R1/r1_24/r1_24_lm_v3_lr*/`.

## MQuAKE on the real base: three-pool readers, seed variance and its cause (2026-09-14, 21:30 EDT)

Reader retrained on three pools (CounterFact 1,000 + zsRE 1,000 + MQuAKE 500 = pool v1, or 1,000 = pool v2; ordinary-text
nulls; gate on; 100-edit development streams, stream 21; ES / RET-ES / RET-GS / LS):

| reader | MQuAKE | zsRE | CounterFact |
| --- | --- | --- | --- |
| v2 reader, no MQuAKE training (transfer) | 1.00 / 1.00 / **0.16** / 0.98 | — | — |
| three pools, MQuAKE 500, seed 0 / 1 / 2 | 0.80 / 1.00; 0.47 / 0.98; 0.82 / 0.98 | 0.98; 0.97; 0.98 (LS 1.00) | 0.66; 0.85; 0.83 (LS 1.00 / 0.98 / 1.00) |
| three pools, MQuAKE 1,000, seed 0 / 1 / 2 | 0.79 / 1.00 (ES 0.92); 0.68 / 1.00; 0.56 / 1.00 | 0.98; 0.96; 0.95 | 0.76; 0.83; 0.785 |

(RET-GS / LS shown for MQuAKE; ES and RET-ES are 1.00 unless stated.) MQuAKE unseen-prompt false fires 0/100 at 100
records; ordinary-text drift after MQuAKE edits +0.005 nats (0.39 % of positions fire). Training on MQuAKE is
necessary (0.16 → 0.80) and the DEC-046 default stands. The MQuAKE paraphrase result varies 0.47–0.82 across six
reader instances while zsRE and CounterFact hold their ranges. Cause: the MQuAKE paraphrase is the question form of a
cloze support ("Who is the employer of Carl Sagan?" vs "Carl Sagan is employed by"), and the same-relation locality
prompts have cosine 0.99 to the best record, so the null decision rests on the lexical-overlap feature alone; failing
paraphrases have lower plain overlap (0.54–0.56 vs 0.74–0.82 for successes) because the question form adds template
words that count as non-overlap. For seed 1 (pool v1) the loss is null over-rejection: raising the threshold to 0.9 /
0.97 recovers 0.76 / 0.81 at LS 0.92 / 0.90; the gate is not involved (0.47 without it). The larger pool does not
stabilise it (seed 2: 0.82 → 0.56).

Fix under test (R1-57c, `ReaderConfig.lex_idf`): weight the lexical overlap by memory rarity, w(t) = log((N+1)/(df+1))
/ log(N+1) over the current memory (the episode's records in training, the store's active records at deployment), so
template words weigh ≈ 0 and subject tokens ≈ 1 — the continuous form of the R1-56 gate, learned into the null.
Unit test in `tests/revision_v1/test_r1_45_lexical.py`; retrain with pool v2 over three seeds running.

### R1-57c result: the weighted lexical feature is not adopted (2026-09-14, 22:20 EDT)

Three seeds with pool v2 and `lex_idf` (gate on): MQuAKE 0.62 / 0.74 / 0.80 (ES 0.85 / 0.99 / 0.99), zsRE 0.98 / 0.98 / 0.99,
CounterFact 0.76 / 0.83 / 0.71 (ES 0.96 / 0.99 / 0.99); zsRE unseen false fires at 1,000 records 12 % (v3 reader:
10–11 %); MQuAKE unseen 0 %. The weighting narrows the MQuAKE spread slightly but introduces own-prompt rejections
(ES < 1) on all three datasets and does not improve the unseen endpoint, so the plain lexical feature stays; `lex_idf`
remains an implemented, tested ablation (off by default). MQuAKE paraphrase retention on the development stream is
therefore reported as it is: 0.47–0.82 over the six plain-lexical reader instances, with one rule for three datasets.
Proposed primary condition v4 = three-pool reader (MQuAKE pool v2), plain lexical, gate
(`manifests/revision_v1/primary_condition_v4.json`); v3 stays the two-dataset fallback.

## R1-60 composition endpoint on the real base — development floor (2026-09-15, 00:30 EDT)

`scripts/r1_60_composition_run.py`, v4 reader seed 0, gate on, 300 MQuAKE composition cases whose dependency edits all
lie in the MQuAKE training pool v2 (484 attach to it; exposed, development only): each case restores an empty memory,
teaches its 1–2 dependency edits, and asks the three multi-hop paraphrases (`results/R1/endpoints/v4_s0_dev300_composition/`).

| quantity | value |
| --- | ---: |
| cases evaluated / unavailable | 299 / 1 |
| composition success (all three paraphrases) | 1 / 299 |
| paraphrase-level post-edit exact | 8 / 897 |
| cap-off base exact on the pre-edit answer / post-edit answer | 0 / 897, 0 / 897 |
| pre-edit answer reappearing after the edit | 0 |
| wall | 195 s (0.65 s per case) |

The base itself answers none of the multi-hop questions before or after editing, so the endpoint has no headroom for
GPT-2 small: a memory cap that fires on the bridge entity's single-hop prompt cannot make the base compose two hops it
cannot compose unedited. The endpoint is kept as a descriptive secondary outcome (protocol U14) with this floor
recorded; it is not evidence about the reader. Firing statistics are in the report rows.
The cap fired (null mass < 0.5) on 369 of the 897 multi-hop questions — those that name the edited subject directly —
and 8 of those decodes were exact; the remaining firings changed nothing the base could compose.

## Stage 4 cell driver validated on the real base (development cell; 2026-09-15, 12:40 EDT)

Codex's driver (R1-61/R1-64) ran end to end on the real base in development mode: `R1_learned_ff` (v4 seed 0, gate on)
× zsRE, 300 development edits in source order, checkpoints 100 and 300, every endpoint, immutable phase records (610),
receipts and a complete result (`results/R1/stage4_dev_cells/R1_learned_ff-zsre-development-source-9084e84fc6dd00038904/`;
recipe `docs/tasks/R1-64-zsre-v4.recipe.json`, sha `5b9bca5d…`).

| checkpoint | retention ES / RET-GS (all edited items) | LS (50 original-base references) | unseen false fires (100 pool prompts) | near-miss / revision | composition | drift (16,256 positions) |
| ---: | --- | --- | ---: | --- | --- | --- |
| 100 | 1.000 / 0.990 | 50/50 | 25 | — | — | — |
| 300 | 0.997 / 0.987 | 50/50 | 16 | planned 100 each, available 0 (no zsRE development challenge rows; missing cases retained) | planned 0 (not applicable) | +0.0002 nats |

Wall: 277 s to checkpoint 100 and 1,126 s from 100 to 300 (1,403 s total) while a reader retrain shared the GPU;
the clean profile is rerun separately. Two observations for the protocol: (1) the driver's zsRE unseen rate with the
v4 seed-0 reader is 25 % / 16 % at 100 / 300 records, and my runner confirms v4 seed 0 at 21–25 % at 100 records
(pool / dev sources), versus 5–12 % for the two-pool v3 reader — adding the MQuAKE pool worsened zsRE unseen rejection
for this seed (the v3-slice readers are being measured); (2) the full 128-window drift assay under the gated reader
after 300 edits is +0.0002 nats, i.e. the gate removes the residual seen in the 32-window assay.
