# Phase 0 — cheap analyses before any new training

Capstan · 2026-10-20 · post-conference programme, study `phase0` · inputs: the frozen ext-20261009 record (scores, raw selection chunks, memory snapshots), forward-only GPU replays (no training, no new memories), payloads and the certified clearance register.

Question A of the programme is what a cap adds to frozen GPT-2 small and where its remaining error comes from; question B is whether predictive coding adds anything backprop does not. Phase 0 answers the parts of both that the saved record already decides, so that Phase 1 (a cached-feature small-reader harness) starts from the right hypotheses. All caps are the six PC-reader study readers at 300 edits (realization 0, order 100); 'BP-CAP' and 'PC-CAP' are seed means over three paired training seeds unless a seed is named.

## Findings

1. **Mostly the same frontier.** zsRE: registered 98.0 % (BP) vs 96.6 % (PC) at 15.0 % / 6.0 % near-miss false fires; at a matched 10 % false-fire rate PC − BP = +1.0 pp (seed ranges overlap), at 2 % +4.6 pp; CounterFact: registered 81.5 % (BP) vs 66.9 % (PC) at 0.3 % / 2.7 % near-miss false fires; at a matched 10 % false-fire rate PC − BP = -1.5 pp (seed ranges overlap), at 2 % -19.8 pp; MQuAKE: registered 67.4 % (BP) vs 59.6 % (PC) at 0.0 % / 0.0 % near-miss false fires; at a matched 10 % false-fire rate PC − BP = +0.3 pp (seed ranges overlap), at 2 % -4.3 pp. The registered PC/BP paraphrase gap is largely an operating-point difference (the PC readers sit at a more conservative threshold); what remains at matched false-fire rates is small at open settings and larger on CounterFact at tight ones, with wide PC seed ranges. Each arm carries its own acquired payloads, so even a residual difference is not a difference between gates alone (table 1.2).
2. **Gating on CounterFact, payload on MQuAKE.** CounterFact paraphrase failures are 84.0 % abstentions (seed mean over both rules), and 26.2 % of all failures never had the own record among the four retrieved candidates. On MQuAKE 32.5 % of failures fired the correct record and still failed: the per-position delta acquired on the taught prompt does not transfer to the question wording.
3. **Oracle selection rescues** zsRE 100.0 % (BP) / 100.0 % (PC) of paraphrase failures; CounterFact 95.5 % (BP) / 97.3 % (PC) of paraphrase failures; MQuAKE 51.1 % (BP) / 61.2 % (PC) of paraphrase failures, lifting paraphrase EM to zsRE 100.0 %; CounterFact 99.2 %; MQuAKE 84.3 %. The remainder fails with the correct record applied.
4. **In-context retrieval is the bar.** zsRE: in-context oracle EM 74.7 % / NLL 0.91, knn 46.7 % / 2.19, lex 74.3 % / 0.92, versus BP-CAP 98.0 % / 0.13 and PC-CAP 96.6 % / 0.20; CounterFact: in-context oracle EM 51.8 % / NLL 2.88, knn 11.0 % / 3.56, lex 47.3 % / 3.16, versus BP-CAP 81.5 % / 1.31 and PC-CAP 66.9 % / 2.43; MQuAKE: in-context oracle EM 1.7 % / NLL 2.63, knn 0.3 % / 4.57, lex 1.7 % / 2.68, versus BP-CAP 67.4 % / 1.59 and PC-CAP 59.6 % / 2.09 (prefix exact match; collateral in §4).
5. **Corrigendum.** 40 of 600 MQuAKE item-locality prompts are taught items; all but 0–4 of the ~33 severe 'collateral' events per seed were the cap correctly applying its own record. Genuine false fires are the zsRE near-miss neighbours and MQuAKE's same-template prompts (§5).
6. **Composition.** The dependency record is retrieved on 80.0 %–83.3 % of multi-hop questions but the gate fires on 17.5 %–43.3 %; when it fires the composed answer's loss moves by 0.47–0.74 nats/token. Frozen GPT-2 small answers the unedited hop on 10.8 % of cloze prompts (prefix match; NLL 4.93), and with the taught fact in its context its multi-hop target NLL falls from 6.61 to 4.85 nats/token while the caps leave it at 6.70–6.89: a one-shot context composes better than a write at blocks 4/8/12.
7. **Reserves.** zsRE 684; CounterFact 721; MQuAKE 4549 unexposed items remain (zsRE/CounterFact by the certified register; MQuAKE by population tables only), none overlapping the reader-training pool.

## 1. Are the BP and PC readers on the same gate frontier?

The registered gate fires when the reader's null mass is below 0.5 and the rare-token veto passes. Sweeping the threshold on the saved null masses, with forward-only replays of every probe the threshold had stopped (validation: the untouched replay reproduces the saved losses exactly, table `replay_validation.csv`), gives each reader's operating curve. The rare-token veto is threshold-independent and is kept in every point.

![Gate frontier](../../../../../assets/post_conference/phase0/figures/frontier.png)

![Threshold sweep](../../../../../assets/post_conference/phase0/figures/frontier_threshold_sweep.png)

### 1.1 Registered gate versus the fully open gate (seed means)

| dataset | cap | τ = 0.5: paraphrase EM / near-miss fires / unseen fires | τ = 1 (no null veto): same | paraphrase mean NLL | paraphrase CVaR95 | item-locality fire rate | τ maximising paraphrase EM (mean over seeds) |
|---|---|---|---|---|---|---|---|
| zsRE | BP-CAP | 98.0 % / 15.0 % / 9.7 % | 99.3 % / 46.3 % / 43.0 % | 0.13 → 0.06 | 2.19 → 0.82 | 0.0 % → 20.8 % | 0.73 |
| zsRE | PC-CAP | 96.6 % / 6.0 % / 3.7 % | 99.4 % / 45.7 % / 42.3 % | 0.20 → 0.05 | 3.65 → 0.66 | 0.0 % → 16.1 % | 0.87 |
| CounterFact | BP-CAP | 81.5 % / 0.3 % / 0.3 % | 86.2 % / 45.0 % / 41.0 % | 1.31 → 0.96 | 8.99 → 8.61 | 0.3 % → 33.6 % | 1.00 |
| CounterFact | PC-CAP | 66.9 % / 2.7 % / 0.3 % | 85.7 % / 37.0 % / 36.3 % | 2.43 → 0.99 | 9.58 → 8.79 | 1.0 % → 29.0 % | 0.98 |
| MQuAKE | BP-CAP | 67.4 % / 0.0 % / 0.0 % | 83.1 % / 32.0 % / 28.0 % | 1.59 → 0.59 | 7.63 → 3.85 | 0.7 % → 32.1 % | 0.96 |
| MQuAKE | PC-CAP | 59.6 % / 0.0 % / 0.0 % | 83.3 % / 32.0 % / 27.0 % | 2.09 → 0.57 | 7.99 → 3.60 | 1.0 % → 31.1 % | 0.96 |

At τ = 1 the only remaining abstentions are the rare-token veto (evaluated on every forced acceptance, as the learner evaluates it after the null gate) and empty retrievals; the table therefore gives the whole range the null threshold can reach without changing the reader. Each arm carries its own acquired payloads, so a difference between curves mixes selection and payload; coincident curves mean similar trade-offs on this population, not identical gates or representations.

### 1.1b Selection risk and answer risk along the sweep (paraphrases, seed means)

| dataset | cap | τ | coverage (fired) | selection risk: wrong record accepted | answer risk: failed given fired | failed given fired own record | paraphrase EM |
|---|---|---|---|---|---|---|---|
| zsRE | BP-CAP | 0.3 | 95.8 % | 0.2 % | 0.2 % | 0.0 % | 95.6 % |
| zsRE | BP-CAP | 0.5 | 98.3 % | 0.3 % | 0.3 % | 0.0 % | 98.0 % |
| zsRE | BP-CAP | 0.7 | 99.6 % | 0.3 % | 0.3 % | 0.0 % | 99.2 % |
| zsRE | BP-CAP | 0.9 | 99.7 % | 0.3 % | 0.3 % | 0.0 % | 99.3 % |
| zsRE | BP-CAP | 1 | 99.7 % | 0.3 % | 0.3 % | 0.0 % | 99.3 % |
| zsRE | PC-CAP | 0.3 | 91.9 % | 0.0 % | 0.0 % | 0.0 % | 91.9 % |
| zsRE | PC-CAP | 0.5 | 96.7 % | 0.1 % | 0.1 % | 0.0 % | 96.6 % |
| zsRE | PC-CAP | 0.7 | 98.9 % | 0.2 % | 0.2 % | 0.0 % | 98.7 % |
| zsRE | PC-CAP | 0.9 | 99.7 % | 0.2 % | 0.2 % | 0.0 % | 99.4 % |
| zsRE | PC-CAP | 1 | 99.7 % | 0.2 % | 0.2 % | 0.0 % | 99.4 % |
| CounterFact | BP-CAP | 0.3 | 77.7 % | 2.6 % | 4.2 % | 1.0 % | 74.4 % |
| CounterFact | BP-CAP | 0.5 | 85.7 % | 3.6 % | 4.9 % | 1.0 % | 81.5 % |
| CounterFact | BP-CAP | 0.7 | 89.1 % | 4.2 % | 5.4 % | 1.0 % | 84.3 % |
| CounterFact | BP-CAP | 0.9 | 90.8 % | 4.6 % | 5.7 % | 1.0 % | 85.6 % |
| CounterFact | BP-CAP | 1 | 91.5 % | 4.8 % | 5.8 % | 1.0 % | 86.2 % |
| CounterFact | PC-CAP | 0.3 | 53.4 % | 1.2 % | 2.7 % | 0.9 % | 51.9 % |
| CounterFact | PC-CAP | 0.5 | 69.5 % | 2.2 % | 3.7 % | 0.8 % | 66.9 % |
| CounterFact | PC-CAP | 0.7 | 80.9 % | 3.7 % | 5.1 % | 1.0 % | 76.8 % |
| CounterFact | PC-CAP | 0.9 | 90.1 % | 5.3 % | 6.3 % | 0.9 % | 84.4 % |
| CounterFact | PC-CAP | 1 | 91.7 % | 5.6 % | 6.5 % | 0.9 % | 85.7 % |
| MQuAKE | BP-CAP | 0.3 | 63.7 % | 0.4 % | 16.2 % | 15.6 % | 53.2 % |
| MQuAKE | BP-CAP | 0.5 | 80.1 % | 0.6 % | 15.7 % | 15.1 % | 67.4 % |
| MQuAKE | BP-CAP | 0.7 | 90.3 % | 0.6 % | 16.1 % | 15.6 % | 75.8 % |
| MQuAKE | BP-CAP | 0.9 | 97.6 % | 1.0 % | 16.4 % | 15.5 % | 81.6 % |
| MQuAKE | BP-CAP | 1 | 99.7 % | 1.1 % | 16.6 % | 15.7 % | 83.1 % |
| MQuAKE | PC-CAP | 0.3 | 50.9 % | 0.4 % | 17.9 % | 17.2 % | 41.8 % |
| MQuAKE | PC-CAP | 0.5 | 70.8 % | 0.4 % | 15.8 % | 15.3 % | 59.6 % |
| MQuAKE | PC-CAP | 0.7 | 84.9 % | 0.6 % | 16.1 % | 15.5 % | 71.2 % |
| MQuAKE | PC-CAP | 0.9 | 97.3 % | 0.6 % | 16.2 % | 15.7 % | 81.6 % |
| MQuAKE | PC-CAP | 1 | 99.7 % | 0.9 % | 16.4 % | 15.6 % | 83.3 % |
### 1.2 Matched false-fire comparison

| dataset | near-miss false-fire rate | BP-CAP paraphrase EM (seed range) | PC-CAP paraphrase EM (seed range) | PC − BP |
|---|---|---|---|---|
| zsRE | 2 % | 87.9 % (87.7 %–88.2 %) | 92.4 % (90.0 %–93.8 %) | +4.6 pp |
| zsRE | 5 % | 93.5 % (93.0 %–94.3 %) | 95.1 % (94.3 %–96.2 %) | +1.7 pp |
| zsRE | 10 % | 96.7 % (96.1 %–97.6 %) | 97.8 % (97.2 %–98.3 %) | +1.0 pp |
| CounterFact | 2 % | 85.2 % (82.7 %–88.3 %) | 65.4 % (56.8 %–81.7 %) | -19.8 pp |
| CounterFact | 5 % | 85.7 % (83.7 %–88.7 %) | 79.8 % (77.8 %–82.5 %) | -5.9 pp |
| CounterFact | 10 % | 85.8 % (83.8 %–88.9 %) | 84.4 % (83.2 %–86.1 %) | -1.5 pp |
| MQuAKE | 2 % | 80.8 % (78.5 %–83.0 %) | 76.6 % (71.7 %–82.3 %) | -4.3 pp |
| MQuAKE | 5 % | 82.4 % (82.0 %–83.0 %) | 81.8 % (80.7 %–83.1 %) | -0.6 pp |
| MQuAKE | 10 % | 82.8 % (82.5 %–83.0 %) | 83.0 % (82.4 %–83.3 %) | +0.3 pp |

Interpolated along each seed's own sweep; when a reader never reaches the stated false-fire rate even with the null veto removed, its most open point is used. A difference inside the seed ranges means the two training rules produced gates on the same frontier and differ only in where the registered threshold placed them.

### 1.3 The in-context retrievers on the same axes

| dataset | retriever | always prepend: paraphrase EM (prefix) | paraphrase mean NLL | near-miss prepend rate | item-locality worse by > 1 nat | best EM along the threshold sweep |
|---|---|---|---|---|---|---|
| zsRE | knn | 46.7 % | 2.19 | 100.0 % | 0.0 % | 46.7 % at θ = 0 (near-miss fires 100.0 %) |
| zsRE | lex | 74.3 % | 0.92 | 100.0 % | 0.0 % | 74.3 % at θ = 0 (near-miss fires 100.0 %) |
| CounterFact | knn | 11.0 % | 3.56 | 100.0 % | 0.0 % | 11.0 % at θ = 0 (near-miss fires 100.0 %) |
| CounterFact | lex | 47.3 % | 3.16 | 100.0 % | 1.7 % | 47.3 % at θ = 0 (near-miss fires 100.0 %) |
| MQuAKE | knn | 0.3 % | 4.57 | 100.0 % | 0.3 % | 0.3 % at θ = 0 (near-miss fires 100.0 %) |
| MQuAKE | lex | 1.7 % | 2.68 | 100.0 % | 0.5 % | 1.7 % at θ = 0 (near-miss fires 100.0 %) |
## 2. Where the remaining error is: gating, retrieval or payload

![Failure atlas](../../../../../assets/post_conference/phase0/figures/failure_atlas.png)

### 2.1 Paraphrase failures (generation not exact) by cause, seed means

| dataset | cap | failures | abstained: null ≥ 0.5 | abstained: rare-token veto | of which own record not among the 4 candidates | fired own record, still failed (payload) | fired a wrong record | success when fired | share of own worst 5 % that abstained |
|---|---|---|---|---|---|---|---|---|---|
| zsRE | BP-CAP | 6 of 300 | 5 | 0 | 0 | 0 | 1 | 99.7 % | 33.3 % |
| zsRE | PC-CAP | 10 of 300 | 10 | 0 | 0 | 0 | 0 | 99.9 % | 64.4 % |
| CounterFact | BP-CAP | 111 of 600 | 66 | 20 | 32 | 5 | 20 | 95.1 % | 95.6 % |
| CounterFact | PC-CAP | 199 of 600 | 176 | 7 | 43 | 3 | 12 | 96.3 % | 97.8 % |
| MQuAKE | BP-CAP | 98 of 300 | 59 | 1 | 1 | 36 | 2 | 84.3 % | 95.6 % |
| MQuAKE | PC-CAP | 121 of 300 | 87 | 0 | 1 | 32 | 1 | 84.2 % | 97.8 % |

'Abstained: own record not retrieved' is a subset of the two abstention columns: the reader's top-4 retrieval did not contain the item's own record, so no threshold could have applied it.


### 2.2 Oracle selection rate (review §3.1)

| dataset | cap | failures | own record among candidates | own record already top | already applied and failed |
|---|---|---|---|---|---|
| zsRE | BP-CAP | 6 | 100.0 % | 4 | 0 |
| zsRE | PC-CAP | 10 | 96.3 % | 9 | 0 |
| CounterFact | BP-CAP | 111 | 68.3 % | 33 | 5 |
| CounterFact | PC-CAP | 199 | 75.1 % | 117 | 3 |
| MQuAKE | BP-CAP | 98 | 97.9 % | 94 | 36 |
| MQuAKE | PC-CAP | 121 | 98.4 % | 119 | 32 |

### 2.3 Failures by frozen difficulty and answer length (seed-pooled)

| dataset | rule | frozen-loss tercile | n (3 seeds) | success | abstain rate | fired-and-failed rate |
|---|---|---|---|---|---|---|
| zsRE | BP | easy | 300 | 98.0 % | 1.0 % | 1.0 % |
| zsRE | BP | medium | 300 | 96.0 % | 4.0 % | 0.0 % |
| zsRE | BP | hard | 300 | 100.0 % | 0.0 % | 0.0 % |
| zsRE | EPC | easy | 300 | 96.0 % | 3.7 % | 0.3 % |
| zsRE | EPC | medium | 300 | 94.7 % | 5.3 % | 0.0 % |
| zsRE | EPC | hard | 300 | 99.0 % | 1.0 % | 0.0 % |
| CounterFact | BP | easy | 600 | 84.5 % | 12.3 % | 3.2 % |
| CounterFact | BP | medium | 600 | 80.8 % | 15.7 % | 3.5 % |
| CounterFact | BP | hard | 600 | 79.2 % | 14.8 % | 6.0 % |
| CounterFact | EPC | easy | 600 | 69.2 % | 29.3 % | 1.5 % |
| CounterFact | EPC | medium | 600 | 67.8 % | 30.0 % | 2.2 % |
| CounterFact | EPC | hard | 600 | 63.7 % | 32.2 % | 4.2 % |
## 3. Oracle selection: what perfect record choice would and would not fix

![Oracle rescue](../../../../../assets/post_conference/phase0/figures/oracle_rescue.png)

| dataset | cap | paraphrase EM registered → oracle | mean NLL | CVaR95 | failures rescued | rescued among abstentions | rescued among wrong-record fires | own record applied and still failed | in-context oracle EM (prefix) / NLL |
|---|---|---|---|---|---|---|---|---|---|
| zsRE | BP-CAP | 98.0 % → 100.0 % | 0.13 → 0.02 | 2.19 → 0.09 | 6 of 6 (100.0 %) | 5 of 5 | 1 of 1 | 0 | 74.7 % / 0.91 |
| zsRE | PC-CAP | 96.6 % → 100.0 % | 0.20 → 0.02 | 3.65 → 0.09 | 10 of 10 (100.0 %) | 10 of 10 | 0 of 0 | 0 | 74.7 % / 0.91 |
| CounterFact | BP-CAP | 81.5 % → 99.2 % | 1.31 → 0.09 | 8.99 → 0.80 | 106 of 111 (95.5 %) | 86 of 86 | 20 of 20 | 5 | 51.8 % / 2.88 |
| CounterFact | PC-CAP | 66.9 % → 99.2 % | 2.43 → 0.09 | 9.58 → 0.80 | 194 of 199 (97.3 %) | 181 of 183 | 12 of 12 | 3 | 51.8 % / 2.88 |
| MQuAKE | BP-CAP | 67.4 % → 84.3 % | 1.59 → 0.51 | 7.63 → 2.76 | 51 of 98 (51.1 %) | 50 of 60 | 1 of 2 | 36 | 1.7 % / 2.63 |
| MQuAKE | PC-CAP | 59.6 % → 84.3 % | 2.09 → 0.51 | 7.99 → 2.76 | 74 of 121 (61.2 %) | 73 of 88 | 1 of 1 | 32 | 1.7 % / 2.63 |

The oracle forces the item's own record (identity only; nothing about the answer enters the prediction). The last column is the other oracle: the same fact placed in frozen GPT-2's context. The gap between the two oracles is the value of the write mechanism over a one-shot prompt when retrieval is perfect.

## 4. Equal-information baseline: frozen GPT-2 with the taught fact in context

![In-context vs cap](../../../../../assets/post_conference/phase0/figures/incontext_vs_cap.png)

Three retrieval arms prepend one taught fact (prompt + answer + newline) to the probe and run the frozen model: `oracle` prepends the probe's own fact (collateral families get no context: an oracle knows they are unrelated), `knn` the nearest taught prompt by cosine of the frozen residual keys at blocks 4/8/12 (the cap's own key feature, no learning), `lex` the best IDF-weighted token overlap. `knn`/`lex` always prepend, so their collateral columns are the worst case; §1.3 sweeps their retrieval scores as a threshold. Exact match is reported two ways: the project's strict rule (generation stops at a newline) and a prefix rule (generation starts with an alias), because a one-shot context often makes the model continue past the answer instead of emitting a newline; the caps' generations are rescored with the same prefix rule. The per-token NLL includes the newline terminator; a one-shot context demonstrates the answer format and so lowers the terminator's loss on *every* prompt, related or not, which is why the always-prepend arms look 'better than frozen' on unrelated prompts. The column without the terminator removes that format effect and is the one to read for collateral.

### Paraphrases (new answer)

| dataset | arm | n | mean NLL | mean NLL w/o terminator | CVaR95 | EM strict | EM prefix | worse than frozen > 1 nat | > 2 nats | better > 1 nat | retrieved own item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| zsRE | frozen | 300 | 6.10 | 7.91 | 11.37 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 0.0 % | — |
| zsRE | in-context oracle | 300 | 0.91 | 0.97 | 2.19 | 69.3 % | 74.7 % | 0.0 % | 0.0 % | 100.0 % | 100.0 % |
| zsRE | in-context knn | 300 | 2.19 | 2.87 | 6.97 | 42.7 % | 46.7 % | 0.0 % | 0.0 % | 84.7 % | 56.7 % |
| zsRE | in-context lex | 300 | 0.92 | 0.98 | 2.22 | 69.0 % | 74.3 % | 0.0 % | 0.0 % | 100.0 % | 99.7 % |
| zsRE | BP-CAP seed mean | 300 | 0.13 | 0.15 | 2.18 | 98.0 % | 98.0 % | 0.3 % | 0.0 % | 98.7 % | — |
| zsRE | PC-CAP seed mean | 300 | 0.20 | 0.23 | 3.47 | 96.6 % | 96.6 % | 0.0 % | 0.0 % | 97.7 % | — |
| CounterFact | frozen | 600 | 7.37 | 8.41 | 10.42 | 0.0 % | 0.2 % | 0.0 % | 0.0 % | 0.0 % | — |
| CounterFact | in-context oracle | 600 | 2.88 | 2.64 | 6.71 | 11.7 % | 51.8 % | 0.0 % | 0.0 % | 99.5 % | 100.0 % |
| CounterFact | in-context knn | 600 | 3.56 | 5.86 | 7.52 | 7.3 % | 11.0 % | 0.0 % | 0.0 % | 96.3 % | 5.7 % |
| CounterFact | in-context lex | 600 | 3.16 | 3.16 | 7.71 | 10.8 % | 47.3 % | 0.0 % | 0.0 % | 95.7 % | 89.8 % |
| CounterFact | BP-CAP seed mean | 600 | 1.31 | 1.69 | 7.97 | 81.5 % | 81.5 % | 0.0 % | 0.0 % | 93.2 % | — |
| CounterFact | PC-CAP seed mean | 600 | 2.43 | 2.92 | 8.81 | 66.9 % | 66.9 % | 0.0 % | 0.0 % | 84.3 % | — |
| MQuAKE | frozen | 300 | 6.05 | 7.82 | 10.17 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 0.0 % | — |
| MQuAKE | in-context oracle | 300 | 2.63 | 3.33 | 6.33 | 1.0 % | 1.7 % | 0.0 % | 0.0 % | 99.0 % | 100.0 % |
| MQuAKE | in-context knn | 300 | 4.57 | 6.46 | 8.08 | 0.0 % | 0.3 % | 0.3 % | 0.0 % | 56.3 % | 14.3 % |
| MQuAKE | in-context lex | 300 | 2.68 | 3.42 | 6.53 | 1.0 % | 1.7 % | 0.0 % | 0.0 % | 97.7 % | 97.3 % |
| MQuAKE | BP-CAP seed mean | 300 | 1.59 | 2.21 | 6.92 | 67.4 % | 67.4 % | 0.0 % | 0.0 % | 89.3 % | — |
| MQuAKE | PC-CAP seed mean | 300 | 2.09 | 2.86 | 7.68 | 59.6 % | 59.6 % | 0.0 % | 0.0 % | 75.3 % | — |

### Taught prompts (new answer)

| dataset | arm | n | mean NLL | mean NLL w/o terminator | CVaR95 | EM strict | EM prefix | worse than frozen > 1 nat | > 2 nats | better > 1 nat | retrieved own item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| zsRE | frozen | 300 | 6.01 | 7.79 | 10.99 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 0.0 % | — |
| zsRE | in-context oracle | 300 | 0.94 | 0.72 | 2.17 | 73.0 % | 85.0 % | 0.0 % | 0.0 % | 100.0 % | 100.0 % |
| zsRE | in-context knn | 300 | 0.94 | 0.72 | 2.17 | 73.0 % | 85.0 % | 0.0 % | 0.0 % | 100.0 % | 100.0 % |
| zsRE | in-context lex | 300 | 0.94 | 0.72 | 2.17 | 73.0 % | 85.0 % | 0.0 % | 0.0 % | 100.0 % | 100.0 % |
| zsRE | BP-CAP seed mean | 300 | 0.01 | 0.01 | 0.04 | 100.0 % | 100.0 % | 0.0 % | 0.0 % | 100.0 % | — |
| zsRE | PC-CAP seed mean | 300 | 0.01 | 0.01 | 0.04 | 100.0 % | 100.0 % | 0.0 % | 0.0 % | 100.0 % | — |
| CounterFact | frozen | 300 | 6.96 | 8.29 | 10.13 | 0.0 % | 0.7 % | 0.0 % | 0.0 % | 0.0 % | — |
| CounterFact | in-context oracle | 300 | 1.62 | 0.39 | 2.94 | 50.3 % | 97.3 % | 0.0 % | 0.0 % | 100.0 % | 100.0 % |
| CounterFact | in-context knn | 300 | 1.62 | 0.39 | 2.94 | 50.3 % | 97.3 % | 0.0 % | 0.0 % | 100.0 % | 100.0 % |
| CounterFact | in-context lex | 300 | 1.62 | 0.39 | 2.94 | 50.3 % | 97.3 % | 0.0 % | 0.0 % | 100.0 % | 100.0 % |
| CounterFact | BP-CAP seed mean | 300 | 0.05 | 0.06 | 0.59 | 99.7 % | 99.7 % | 0.0 % | 0.0 % | 100.0 % | — |
| CounterFact | PC-CAP seed mean | 300 | 0.02 | 0.02 | 0.05 | 100.0 % | 100.0 % | 0.0 % | 0.0 % | 100.0 % | — |
| MQuAKE | frozen | 300 | 5.17 | 5.38 | 8.45 | 0.0 % | 3.7 % | 0.0 % | 0.0 % | 0.0 % | — |
| MQuAKE | in-context oracle | 300 | 1.32 | 0.16 | 2.37 | 27.0 % | 99.3 % | 0.0 % | 0.0 % | 100.0 % | 100.0 % |
| MQuAKE | in-context knn | 300 | 1.32 | 0.16 | 2.37 | 27.0 % | 99.3 % | 0.0 % | 0.0 % | 100.0 % | 100.0 % |
| MQuAKE | in-context lex | 300 | 1.32 | 0.16 | 2.37 | 27.0 % | 99.3 % | 0.0 % | 0.0 % | 100.0 % | 100.0 % |
| MQuAKE | BP-CAP seed mean | 300 | 0.12 | 0.13 | 1.98 | 98.0 % | 98.0 % | 0.0 % | 0.0 % | 100.0 % | — |
| MQuAKE | PC-CAP seed mean | 300 | 0.01 | 0.01 | 0.05 | 100.0 % | 100.0 % | 0.0 % | 0.0 % | 100.0 % | — |

### Item-locality prompts (true answer)

| dataset | arm | n | mean NLL | mean NLL w/o terminator | CVaR95 | EM strict | EM prefix | worse than frozen > 1 nat | > 2 nats | better > 1 nat | retrieved own item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| zsRE | frozen | 296 | 6.22 | 7.15 | 10.33 | — | — | 0.0 % | 0.0 % | 0.0 % | — |
| zsRE | in-context knn | 296 | 5.90 | 7.12 | 9.71 | — | — | 0.0 % | 0.0 % | 7.1 % | — |
| zsRE | in-context lex | 296 | 5.83 | 7.05 | 9.48 | — | — | 0.0 % | 0.0 % | 11.5 % | — |
| zsRE | BP-CAP seed mean | 296 | 6.22 | 7.15 | 10.33 | — | — | 0.0 % | 0.0 % | 0.0 % | — |
| zsRE | PC-CAP seed mean | 296 | 6.22 | 7.15 | 10.33 | — | — | 0.0 % | 0.0 % | 0.0 % | — |
| CounterFact | frozen | 900 | 6.30 | 6.93 | 10.05 | — | — | 0.0 % | 0.0 % | 0.0 % | — |
| CounterFact | in-context knn | 900 | 2.81 | 4.80 | 6.73 | — | — | 0.0 % | 0.0 % | 96.7 % | — |
| CounterFact | in-context lex | 900 | 4.81 | 6.35 | 9.35 | — | — | 1.7 % | 0.1 % | 56.1 % | — |
| CounterFact | BP-CAP seed mean | 900 | 6.29 | 6.93 | 10.05 | — | — | 0.0 % | 0.0 % | 0.2 % | — |
| CounterFact | PC-CAP seed mean | 900 | 6.28 | 6.95 | 10.05 | — | — | 0.1 % | 0.0 % | 0.8 % | — |
| MQuAKE | frozen | 560 | 4.48 | 4.29 | 7.75 | — | — | 0.0 % | 0.0 % | 0.0 % | — |
| MQuAKE | in-context knn | 600 | 2.69 | 3.86 | 5.87 | — | — | 0.3 % | 0.0 % | 75.7 % | — |
| MQuAKE | in-context lex | 600 | 3.30 | 4.24 | 6.49 | — | — | 0.5 % | 0.0 % | 50.0 % | — |
| MQuAKE | BP-CAP seed mean | 560 | 4.49 | 4.31 | 7.79 | — | — | 1.1 % | 0.0 % | 0.0 % | — |
| MQuAKE | PC-CAP seed mean | 560 | 4.50 | 4.33 | 7.95 | — | — | 0.9 % | 0.5 % | 0.2 % | — |

### Near-miss neighbours (true answer)

| dataset | arm | n | mean NLL | mean NLL w/o terminator | CVaR95 | EM strict | EM prefix | worse than frozen > 1 nat | > 2 nats | better > 1 nat | retrieved own item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| zsRE | frozen | 100 | 5.97 | 7.75 | 11.60 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 0.0 % | — |
| zsRE | in-context knn | 100 | 3.79 | 5.44 | 7.54 | 9.0 % | 9.0 % | 1.0 % | 0.0 % | 73.0 % | — |
| zsRE | in-context lex | 100 | 4.19 | 6.05 | 8.49 | 7.0 % | 7.0 % | 2.0 % | 0.0 % | 57.0 % | — |
| zsRE | BP-CAP seed mean | 100 | 6.16 | 8.04 | 12.92 | 2.3 % | 2.3 % | 10.0 % | 5.0 % | 5.0 % | — |
| zsRE | PC-CAP seed mean | 100 | 6.10 | 7.90 | 12.43 | 1.0 % | 1.0 % | 4.0 % | 2.0 % | 1.0 % | — |
| CounterFact | frozen | 100 | 7.17 | 8.67 | 10.76 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 0.0 % | — |
| CounterFact | in-context knn | 100 | 3.35 | 6.00 | 6.61 | 4.0 % | 5.0 % | 0.0 % | 0.0 % | 97.0 % | — |
| CounterFact | in-context lex | 100 | 5.49 | 7.93 | 10.04 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 59.0 % | — |
| CounterFact | BP-CAP seed mean | 100 | 7.16 | 8.68 | 10.76 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 0.0 % | — |
| CounterFact | PC-CAP seed mean | 100 | 7.12 | 8.73 | 10.76 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 2.0 % | — |
| MQuAKE | frozen | 100 | 5.20 | 5.34 | 8.71 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 0.0 % | — |
| MQuAKE | in-context knn | 100 | 3.24 | 4.59 | 8.01 | 7.0 % | 7.0 % | 0.0 % | 0.0 % | 77.0 % | — |
| MQuAKE | in-context lex | 100 | 3.91 | 5.14 | 8.06 | 2.0 % | 2.0 % | 0.0 % | 0.0 % | 50.0 % | — |
| MQuAKE | BP-CAP seed mean | 100 | 5.20 | 5.34 | 8.71 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 0.0 % | — |
| MQuAKE | PC-CAP seed mean | 100 | 5.20 | 5.34 | 8.71 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 0.0 % | — |

### Unseen prompts (new answer; a 'success' here is a false fire)

| dataset | arm | n | mean NLL | mean NLL w/o terminator | CVaR95 | EM strict | EM prefix | worse than frozen > 1 nat | > 2 nats | better > 1 nat | retrieved own item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| zsRE | frozen | 100 | 6.13 | 7.75 | 10.55 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 0.0 % | — |
| zsRE | in-context knn | 100 | 4.06 | 5.79 | 7.78 | 4.0 % | 4.0 % | 0.0 % | 0.0 % | 67.0 % | — |
| zsRE | in-context lex | 100 | 4.15 | 5.87 | 8.42 | 4.0 % | 4.0 % | 1.0 % | 0.0 % | 66.0 % | — |
| zsRE | BP-CAP seed mean | 100 | 6.24 | 7.94 | 12.31 | 1.7 % | 1.7 % | 7.0 % | 5.0 % | 3.0 % | — |
| zsRE | PC-CAP seed mean | 100 | 6.28 | 7.97 | 12.05 | 0.0 % | 0.0 % | 5.0 % | 3.0 % | 0.0 % | — |
| CounterFact | frozen | 100 | 6.92 | 8.34 | 9.75 | 0.0 % | 1.0 % | 0.0 % | 0.0 % | 0.0 % | — |
| CounterFact | in-context knn | 100 | 3.19 | 5.69 | 7.16 | 10.0 % | 10.0 % | 0.0 % | 0.0 % | 95.0 % | — |
| CounterFact | in-context lex | 100 | 5.24 | 7.51 | 8.95 | 1.0 % | 2.0 % | 0.0 % | 0.0 % | 67.0 % | — |
| CounterFact | BP-CAP seed mean | 100 | 6.92 | 8.35 | 9.75 | 0.0 % | 1.0 % | 0.0 % | 0.0 % | 0.0 % | — |
| CounterFact | PC-CAP seed mean | 100 | 6.92 | 8.35 | 9.75 | 0.0 % | 1.0 % | 0.0 % | 0.0 % | 0.0 % | — |
| MQuAKE | frozen | 100 | 5.28 | 5.51 | 8.14 | 0.0 % | 2.0 % | 0.0 % | 0.0 % | 0.0 % | — |
| MQuAKE | in-context knn | 100 | 3.36 | 4.91 | 6.57 | 3.0 % | 4.0 % | 0.0 % | 0.0 % | 81.0 % | — |
| MQuAKE | in-context lex | 100 | 3.96 | 5.33 | 7.25 | 2.0 % | 3.0 % | 0.0 % | 0.0 % | 61.0 % | — |
| MQuAKE | BP-CAP seed mean | 100 | 5.28 | 5.51 | 8.14 | 0.0 % | 2.0 % | 0.0 % | 0.0 % | 0.0 % | — |
| MQuAKE | PC-CAP seed mean | 100 | 5.28 | 5.51 | 8.14 | 0.0 % | 2.0 % | 0.0 % | 0.0 % | 0.0 % | — |

### MQuAKE multi-hop questions (new answer)

| dataset | arm | n | mean NLL | mean NLL w/o terminator | CVaR95 | EM strict | EM prefix | worse than frozen > 1 nat | > 2 nats | better > 1 nat | retrieved own item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MQuAKE | frozen | 240 | 6.61 | 8.88 | 10.70 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 0.0 % | — |
| MQuAKE | in-context oracle | 240 | 4.85 | 6.73 | 9.64 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 64.6 % | 100.0 % |
| MQuAKE | in-context knn | 240 | 5.26 | 7.84 | 9.30 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 60.8 % | 1.7 % |
| MQuAKE | in-context lex | 240 | 5.08 | 7.16 | 9.63 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 57.5 % | 75.8 % |
| MQuAKE | BP-CAP seed mean | 240 | 6.82 | 9.07 | 12.06 | 0.6 % | 1.0 % | 18.8 % | 5.8 % | 5.4 % | — |
| MQuAKE | PC-CAP seed mean | 240 | 6.72 | 8.87 | 11.55 | 0.6 % | 0.8 % | 10.4 % | 4.6 % | 2.9 % | — |

## 5. Locality audit and a corrigendum to the supplement

![Locality corrigendum](../../../../../assets/post_conference/phase0/figures/locality_corrigendum.png)

| dataset | cap | locality probes | that are taught items | fired on them | fired their own record | severe (D > 2) on them | genuinely unrelated | fired | worse than frozen | severe | max D | supplement 'worse than frozen' | supplement severe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CounterFact | BP-CAP seed 0 | 900 | 0 | 0 | 0 | 0 | 900 | 4 | 0 | 0 | 0.00 | 0.0 % | 0 |
| CounterFact | BP-CAP seed 1 | 900 | 0 | 0 | 0 | 0 | 900 | 4 | 0 | 0 | 0.00 | 0.0 % | 0 |
| CounterFact | BP-CAP seed 2 | 900 | 0 | 0 | 0 | 0 | 900 | 1 | 0 | 0 | 0.00 | 0.0 % | 0 |
| CounterFact | PC-CAP seed 0 | 900 | 0 | 0 | 0 | 0 | 900 | 9 | 1 | 1 | 2.26 | 0.1 % | 1 |
| CounterFact | PC-CAP seed 1 | 900 | 0 | 0 | 0 | 0 | 900 | 15 | 3 | 1 | 2.26 | 0.3 % | 1 |
| CounterFact | PC-CAP seed 2 | 900 | 0 | 0 | 0 | 0 | 900 | 4 | 0 | 0 | 0.00 | 0.0 % | 0 |
| MQuAKE | BP-CAP seed 0 | 600 | 40 | 40 | 40 | 31 | 560 | 3 | 2 | 0 | 1.39 | 7.0 % | 31 |
| MQuAKE | BP-CAP seed 1 | 600 | 40 | 40 | 40 | 31 | 560 | 3 | 3 | 1 | 5.75 | 7.2 % | 32 |
| MQuAKE | BP-CAP seed 2 | 600 | 40 | 40 | 40 | 31 | 560 | 6 | 5 | 3 | 3.68 | 7.5 % | 34 |
| MQuAKE | PC-CAP seed 0 | 600 | 40 | 40 | 40 | 31 | 560 | 4 | 3 | 1 | 5.75 | 7.2 % | 32 |
| MQuAKE | PC-CAP seed 1 | 600 | 40 | 40 | 40 | 31 | 560 | 8 | 6 | 4 | 5.75 | 7.7 % | 35 |
| MQuAKE | PC-CAP seed 2 | 600 | 40 | 40 | 40 | 31 | 560 | 5 | 4 | 3 | 5.75 | 7.3 % | 34 |
| zsRE | BP-CAP seed 0 | 296 | 0 | 0 | 0 | 0 | 296 | 0 | 0 | 0 | 0.00 | 0.0 % | 0 |
| zsRE | BP-CAP seed 1 | 296 | 0 | 0 | 0 | 0 | 296 | 0 | 0 | 0 | 0.00 | 0.0 % | 0 |
| zsRE | BP-CAP seed 2 | 296 | 0 | 0 | 0 | 0 | 296 | 0 | 0 | 0 | 0.00 | 0.0 % | 0 |
| zsRE | PC-CAP seed 0 | 296 | 0 | 0 | 0 | 0 | 296 | 0 | 0 | 0 | 0.00 | 0.0 % | 0 |
| zsRE | PC-CAP seed 1 | 296 | 0 | 0 | 0 | 0 | 296 | 0 | 0 | 0 | 0.00 | 0.0 % | 0 |
| zsRE | PC-CAP seed 2 | 296 | 0 | 0 | 0 | 0 | 296 | 0 | 0 | 0 | 0.00 | 0.0 % | 0 |

**Corrigendum.** On MQuAKE, 40 of the 600 item-locality prompts are themselves prompts of other taught stream items (the locality rows of MQuAKE cases are other cases' edited facts). A cap that fires on them is applying its own record for that item, and the 'true' answer it is scored against was deliberately overwritten. The supplement's statement that both caps got worse than frozen on 7.7 % of MQuAKE item-locality prompts with about 33 severe events per seed therefore counted 31–31 correct applications as collateral damage; on the genuinely unrelated prompts the counts are 0–4 severe events per seed (0.4 %–1.1 % worse than frozen). `aw/extremes/assemble.py` now labels these prompts `locality_item_taught`, and the extremes study's tables and reports were regenerated (zsRE and CounterFact have no such overlap).

### 5.1 The remaining false fires are same-template, different-subject prompts

| dataset | family | cap | n | fired | severe | severe fires on another item's record | share of fires that are severe | mean D when fired | non-stop token overlap with the taught prompt when fired | when abstained |
|---|---|---|---|---|---|---|---|---|---|---|
| CounterFact | locality_item | BP-CAP seed 0 | 900 | 0.4 % | 0 | 0 | 0.0 % | -1.56 | 0.00 | 0.03 |
| CounterFact | locality_item | BP-CAP seed 1 | 900 | 0.4 % | 0 | 0 | 0.0 % | -1.96 | 0.11 | 0.03 |
| CounterFact | locality_item | BP-CAP seed 2 | 900 | 0.1 % | 0 | 0 | 0.0 % | -2.89 | 0.00 | 0.03 |
| CounterFact | locality_item | PC-CAP seed 0 | 900 | 1.0 % | 1 | 1 | 11.1 % | -2.66 | 0.19 | 0.03 |
| CounterFact | locality_item | PC-CAP seed 1 | 900 | 1.7 % | 1 | 1 | 6.7 % | -1.42 | 0.10 | 0.03 |
| CounterFact | locality_item | PC-CAP seed 2 | 900 | 0.4 % | 0 | 0 | 0.0 % | -1.56 | 0.00 | 0.03 |
| CounterFact | near_miss_neighbour | BP-CAP seed 0 | 100 | 0.0 % | 0 | 0 | — | — | — | 0.00 |
| CounterFact | near_miss_neighbour | BP-CAP seed 1 | 100 | 1.0 % | 0 | 0 | 0.0 % | -1.97 | 0.00 | 0.00 |
| CounterFact | near_miss_neighbour | BP-CAP seed 2 | 100 | 0.0 % | 0 | 0 | — | — | — | 0.00 |
| CounterFact | near_miss_neighbour | PC-CAP seed 0 | 100 | 2.0 % | 0 | 0 | 0.0 % | -2.85 | 0.00 | 0.00 |
| CounterFact | near_miss_neighbour | PC-CAP seed 1 | 100 | 5.0 % | 0 | 0 | 0.0 % | -1.53 | 0.00 | 0.00 |
| CounterFact | near_miss_neighbour | PC-CAP seed 2 | 100 | 1.0 % | 0 | 0 | 0.0 % | -1.02 | 0.00 | 0.00 |
| MQuAKE | locality_item | BP-CAP seed 0 | 560 | 0.5 % | 0 | 0 | 0.0 % | 0.66 | 0.14 | 0.21 |
| MQuAKE | locality_item | BP-CAP seed 1 | 560 | 0.5 % | 1 | 1 | 33.3 % | 2.73 | 0.18 | 0.21 |
| MQuAKE | locality_item | BP-CAP seed 2 | 560 | 1.1 % | 3 | 0 | 50.0 % | 1.76 | 0.56 | 0.20 |
| MQuAKE | locality_item | PC-CAP seed 0 | 560 | 0.7 % | 1 | 1 | 25.0 % | 1.42 | 0.35 | 0.21 |
| MQuAKE | locality_item | PC-CAP seed 1 | 560 | 1.4 % | 4 | 1 | 50.0 % | 1.98 | 0.50 | 0.20 |
| MQuAKE | locality_item | PC-CAP seed 2 | 560 | 0.9 % | 3 | 1 | 60.0 % | 2.37 | 0.55 | 0.20 |
| MQuAKE | near_miss_neighbour | BP-CAP seed 0 | 100 | 0.0 % | 0 | 0 | — | — | — | 0.00 |
| MQuAKE | near_miss_neighbour | BP-CAP seed 1 | 100 | 0.0 % | 0 | 0 | — | — | — | 0.00 |
| MQuAKE | near_miss_neighbour | BP-CAP seed 2 | 100 | 0.0 % | 0 | 0 | — | — | — | 0.00 |
| MQuAKE | near_miss_neighbour | PC-CAP seed 0 | 100 | 0.0 % | 0 | 0 | — | — | — | 0.00 |
| MQuAKE | near_miss_neighbour | PC-CAP seed 1 | 100 | 0.0 % | 0 | 0 | — | — | — | 0.00 |
| MQuAKE | near_miss_neighbour | PC-CAP seed 2 | 100 | 0.0 % | 0 | 0 | — | — | — | 0.00 |
| zsRE | near_miss_neighbour | BP-CAP seed 0 | 100 | 8.0 % | 4 | 4 | 50.0 % | 2.72 | 0.00 | 0.00 |
| zsRE | near_miss_neighbour | BP-CAP seed 1 | 100 | 21.0 % | 8 | 8 | 38.1 % | 0.89 | 0.00 | 0.00 |
| zsRE | near_miss_neighbour | BP-CAP seed 2 | 100 | 16.0 % | 6 | 6 | 37.5 % | 1.04 | 0.00 | 0.00 |
| zsRE | near_miss_neighbour | PC-CAP seed 0 | 100 | 3.0 % | 2 | 2 | 66.7 % | 2.47 | 0.00 | 0.00 |
| zsRE | near_miss_neighbour | PC-CAP seed 1 | 100 | 8.0 % | 3 | 3 | 37.5 % | 2.16 | 0.00 | 0.00 |
| zsRE | near_miss_neighbour | PC-CAP seed 2 | 100 | 7.0 % | 3 | 3 | 42.9 % | 1.88 | 0.00 | 0.00 |

zsRE near-miss neighbours (matched-template questions about a different subject) and MQuAKE's unrelated locality prompts (same relation template, different subject) are where the genuine false fires are. The near-miss neighbour fires are the false fires that matter for a selection fix: they are the hard negatives the reader training recipe did not contain (its negatives were other items' paraphrases and ordinary text).

## 6. Why composition scores zero

![Composition](../../../../../assets/post_conference/phase0/figures/composition.png)

78 of the 80 MQuAKE composition cases have exactly one dependency in the 300-edit stream; the other hop is an unedited fact the frozen base must supply. The learned readers select one record at the prompt from a write-free pass and apply it at all three sites, so bank-to-bank chaining is not a mechanism these readers have (Capex review §3); the registered composition endpoint evaluates fresh-start dependency-edit states, not a query into the 300-edit memory. The table below reads the reader's selection fields on those endpoint states.

| cap | questions | dependency record retrieved | dependency is top candidate | fired | fired on the dependency | stopped by null threshold | new answer exact | frozen NLL | cap NLL | mean D when fired | improved > 1 nat when fired |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BP-CAP seed 0 | 240 | 82.5 % | 79.6 % | 21.7 % | 49 | 188 | 0.0 % | 6.61 | 6.75 | 0.64 | 13.5 % |
| BP-CAP seed 1 | 240 | 80.0 % | 77.5 % | 43.3 % | 101 | 136 | 0.8 % | 6.61 | 6.81 | 0.47 | 13.5 % |
| BP-CAP seed 2 | 240 | 83.3 % | 81.2 % | 37.1 % | 86 | 151 | 0.8 % | 6.61 | 6.89 | 0.74 | 10.1 % |
| PC-CAP seed 0 | 240 | 83.3 % | 80.8 % | 19.2 % | 43 | 194 | 0.0 % | 6.61 | 6.75 | 0.71 | 10.9 % |
| PC-CAP seed 1 | 240 | 81.7 % | 78.8 % | 17.5 % | 40 | 198 | 0.8 % | 6.61 | 6.70 | 0.52 | 11.9 % |
| PC-CAP seed 2 | 240 | 82.1 % | 78.8 % | 20.4 % | 46 | 191 | 0.8 % | 6.61 | 6.72 | 0.52 | 12.2 % |

### 6.1 Frozen GPT-2 small on the other hop

| probe kind | target | n | EM strict | EM prefix | generation = immediate newline | mean NLL | cases |
|---|---|---|---|---|---|---|---|
| multihop_in_context | new | 240 | 0.0 % | 0.0 % | 99.2 % | 4.85 | 80 |
| multihop_in_context | old | 240 | 0.0 % | 0.0 % | 99.2 % | 4.48 | 80 |
| single_hop_cloze | new | 182 | 0.0 % | 6.0 % | 0.0 % | 5.07 | 80 |
| single_hop_question | new | 182 | 0.0 % | 0.5 % | 99.5 % | 5.46 | 80 |
| single_hop_cloze (unedited hop) | new | 102 | 0.0 % | 10.8 % | 0.0 % | 4.93 | 80 |
| single_hop_cloze (edited hop) | new | 80 | 0.0 % | 0.0 % | 0.0 % | 5.25 | 80 |
| single_hop_question (unedited hop) | new | 102 | 0.0 % | 1.0 % | 99.0 % | 5.15 | 80 |
| single_hop_question (edited hop) | new | 80 | 0.0 % | 0.0 % | 100.0 % | 5.86 | 80 |
| cases whose unedited hops frozen GPT-2 answers (cloze, prefix match) | new | 8 | — | 10.0 % | — | — | 80 |
| multihop_in_context: any question correct (case level, prefix match) | new | 0 | — | 0.0 % | — | — | 80 |
| multihop_in_context: all three correct (case level, prefix match) | new | 0 | — | 0.0 % | — | — | 80 |

Greedy GPT-2 small answers a question-form prompt with a newline almost always (the 'immediate newline' column), so for question-form and in-context probes only the teacher-forced NLL is informative; on cloze prompts it continues past the answer, which the prefix rule credits.


Reading: the reader retrieves the right record on most multi-hop wordings but the gate stops it (the question does not look like the taught prompt); when it fires, the taught delta moves the composed answer's loss only slightly, because the delta was acquired to produce the hop-1 answer at the hop-1 prompt, not to steer a two-hop question. And the frozen model's own knowledge of the unedited hop, asked directly with the new entity, bounds what any single-fact mechanism could compose. With the taught fact in its context, frozen GPT-2 small reaches the in-context row above on the multi-hop questions: that is the composition ceiling of the base model itself.

## 7. Unexposed subjects available for confirmation

| dataset | method | cleared | reserved by r0–r3 | remaining | distinct subjects | overlap with reader-training pool | clean of reader training | note |
|---|---|---|---|---|---|---|---|---|
| zsRE | certified clearance replay (aw.r_extension), minus reservations r0-r3 | 6084 | 5400 | 684 | 684 | 0 | 684 | dated: later exposures only reduce this; 300-edit confirmation needs 300 edits + 350 endpoint roles per realization |
| CounterFact | certified clearance replay (aw.r_extension), minus reservations r0-r3 | 6121 | 5400 | 721 | 721 | 0 | 721 | dated: later exposures only reduce this; 300-edit confirmation needs 300 edits + 350 endpoint roles per realization |
| MQuAKE | case_populations: eligible minus sealed r0-r2, reader_train and pcr_r0_300 (item and subject); no entity/canonical-subject register | 6043 | 1400 | 4549 | 4177 | 0 | 4549 | upper bound: endpoint roles (outside/near-miss/revision) of the sealed realizations are not in case_populations and are not excluded here; composition cases and their dependency subjects not excluded |

A 300-edit confirmation realization needs 300 edit subjects plus 350 endpoint-role subjects (outside, near-miss support and neighbour, revision). zsRE and CounterFact can each support one more such realization; MQuAKE can support several, subject to the entity/canonical-subject checks the certified register applies to the other two datasets.

## 8. What this decides for Phase 1

- The selection experiment (Capex's A) should start from the hard negatives that actually fire: matched-template, different-subject prompts (zsRE near-miss neighbours, MQuAKE same-relation locality prompts), with labels defined against the whole active memory (a prompt that should invoke another taught record is a positive for that record). The proposal's same-subject hypothesis was wrong.
- Retrieval misses on CounterFact (own record not in the top-4) cap what any gate can do; the small-reader harness needs a retrieval endpoint, not only a gate endpoint.
- MQuAKE's payload failures (correct record applied, wrong answer) are a write-transfer problem: the per-position delta is prompt-specific. A Phase 1 arm should test deltas acquired on more than one wording, or a code-conditioned controller write, before any new learning rule.
- The in-context arms set the accuracy bar the cap must beat or be cheaper than; every Phase 1 table carries them.
- Composition needs an explicit mechanism or a base that knows the second hop; neither cap training rule addresses it. Treat E as conditional on the frozen-base ceiling in §6.1.
- The PC-specific hypotheses (energy-based abstention; low-interference online learning) stand: nothing in the saved record tests them, and the frontier result says the registered PC/BP difference is not evidence either way.

## 9. Reproducibility

Code: `aw/post_conference/phase0_*.py` (CPU: atlas, locality, composition, reserves, figures, report; GPU forward-only: frontier replay, in-context arms, composition probes), runner `aw/post_conference/run_phase0_gpu.sh`. Tables: `results/post_conference/phase0/tables/`. Data and figures: `assets/post_conference/phase0/`. Raw replay chunks: `assets/runs/post_conference/phase0/`. Replay validation: untouched replays of 216 fired paraphrases across 18 reader/dataset cells reproduce the saved losses with max |diff| = 0.0e+00 nats. GPU process time: composition 18 s, in-context 436 s, frontier replay 110 s. Manifest: `results/post_conference/phase0/manifest.json` (stages: atlas, composition_cpu, composition_gpu, figures, frontier, incontext, locality, report, reserves).
