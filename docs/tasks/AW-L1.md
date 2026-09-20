# AW-L1 — cached development tap screen

**Status:** done; exploratory diagnostic, no layer selection. **Agent:** Codex. **Date:** 2026-09-20. **Cost:** CPU only, zero model calls, zero GPU seconds, no cache build.

**Inputs:** the existing zsRE/CounterFact v1 1,000-item feature banks and the selected v5 training summary. Cached identities, complete cache file hashes, ordered token hashes, base checksum, tap order and source pool identities were checked. Only the historical last-100 development items of each bank enter this screen. No fresh Option R subjects or realization-0 treatment outcomes are used.

**Method.** Join each cached item to its source subject and DEC-061 template family; union connected subjects **and** families, then assign whole components by a fixed hash (nominal 70/30 train/test). Neither identity overlaps between probe folds. No item lacks a usable family. Inside each fold, a fixed hash puts half the items in memory. Positive queries are cached paraphrases of memory facts; null queries are their locality prompts and outside-fact questions/paraphrases. Exact null-query collisions with memory support/paraphrase inputs are excluded. All read-set probes see identical folds, queries and memories.

For each tap, separately normalize last-position and prompt-span vectors with the reader's layer-norm epsilon, concatenate, and use cosine similarity against each candidate. A small balanced logistic ridge probe (lambda 0.01, at most 40 Newton steps, training-only standardization, fixed logit threshold zero) combines the selected tap similarities and the existing stop-token lexical overlap. The lexical-only control removes neural features. This is a low-capacity metric diagnostic, **not** retraining/evaluating the v5 reader or testing editing quality. Its pair classifier threshold is not a calibrated memory-level null threshold.

## Paired evaluation

All combined read sets and the lexical-only control made identical decisions on these small held-out episodes. A tap-only secondary diagnostic was added after observing that equality; it is explicitly exploratory and is not used for arm selection. Numbers below are raw proportions; query rows sharing a fact/family are dependent.

| Dataset | Arm | Forced retrieval | Gated retrieval | Null false fires | Retrieval/null AUROC |
|---|---|---:|---:|---:|---:|
| counterfact | 123 | 1.000 | 1.000 | 0.171 | 0.980 |
| counterfact | 23 | 1.000 | 1.000 | 0.171 | 0.980 |
| counterfact | 3 | 1.000 | 1.000 | 0.171 | 0.980 |
| counterfact | 2 | 1.000 | 1.000 | 0.171 | 0.980 |
| counterfact | lexical | 1.000 | 1.000 | 0.171 | 0.980 |
| counterfact | 123-no-lex | 0.786 | 0.714 | 1.000 | 0.398 |
| counterfact | 23-no-lex | 0.786 | 0.643 | 0.914 | 0.400 |
| counterfact | 3-no-lex | 0.786 | 0.643 | 0.886 | 0.451 |
| counterfact | 2-no-lex | 0.643 | 0.500 | 0.943 | 0.367 |
| zsre | 123 | 1.000 | 1.000 | 0.043 | 1.000 |
| zsre | 23 | 1.000 | 1.000 | 0.043 | 1.000 |
| zsre | 3 | 1.000 | 1.000 | 0.043 | 1.000 |
| zsre | 2 | 1.000 | 1.000 | 0.043 | 1.000 |
| zsre | lexical | 1.000 | 1.000 | 0.043 | 1.000 |
| zsre | 123-no-lex | 1.000 | 0.933 | 0.340 | 0.935 |
| zsre | 23-no-lex | 1.000 | 0.933 | 0.340 | 0.933 |
| zsre | 3-no-lex | 1.000 | 0.933 | 0.340 | 0.935 |
| zsre | 2-no-lex | 0.867 | 0.867 | 0.638 | 0.852 |

“Forced” ignores the probe gate; “gated” requires correct retrieval and firing. AUC compares each query's maximum candidate logit for retrieval versus null queries; it does not require the selected candidate to be correct. Exact per-role denominators, all query decisions, model coefficients and discordant counts versus {1,2,3} are saved, not just aggregate percentages.

- counterfact: 30 subject/template components; 86/14 train/test items; 7 evaluation memory records; 14 positive and 35 null queries. Combined and lexical-only arms retrieve 14/14 positives and false-fire on 6/35 nulls.
- zsre: 86 subject/template components; 69/31 train/test items; 15 evaluation memory records; 15 positive and 47 null queries. Combined and lexical-only arms retrieve 15/15 positives and false-fire on 2/47 nulls.

## Raw residual scale

| Dataset | Tap | Mean last-position norm | Norm SD | Mean coordinate variance across items |
|---|---:|---:|---:|---:|
| counterfact | 1 | 63.851 | 4.024 | 1.494 |
| counterfact | 2 | 100.492 | 5.246 | 4.381 |
| counterfact | 3 | 472.154 | 53.173 | 26.033 |
| zsre | 1 | 65.288 | 2.223 | 0.264 |
| zsre | 2 | 101.884 | 2.848 | 1.372 |
| zsre | 3 | 514.059 | 27.402 | 11.963 |

Prompt-span statistics are in `screen.json` too. The late residuals are much larger in raw norm, but the learned reader normalizes features before projection. Raw magnitude or variance does not establish which tap contains useful task information.

**Interpretation.** Lexical overlap solves this small retrieval problem as well as the combined probes. Without it, the CounterFact probe rejects nulls poorly at every tap; zsRE also has many more false fires. No evidence here warrants saying the lower layers are noise, that upper-only editing will preserve retention, or that any write-site policy is better. The CounterFact test contains only seven memory records, versus 300 in the planned stream; effects at scale, actual learned query/key transforms, near-miss behavior, acquisition success and ordinary-text fidelity still need AW-L. The early/late tap comparison has limited resolution and cannot rank the optional read arms for confirmation.

**Outputs:** `aw/tap_screen.py`, `aw/tests/test_tap_screen.py`, `results/additional_work/L1/{screen,zsre-predictions,counterfact-predictions}.json`, `logs/additional_work-L1-console-final.log`.

**Verify:** `JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /home/derp/cap/venv/bin/python -m aw.tap_screen screen`; tests and Ruff in the round-43 final logs. Tests cover transitive subject/family splitting, missing-family refusal, logistic fitting without evaluation refits, normalization and retrieval/null scoring.

**Done-when:** cache identities, per-tap norm/variance, required four read-set probes, lexical control, paired retrieval/false-fire outputs and limitations delivered. **Deviations:** additional tap-only exploratory table; no tuning of the registered AW-L arms. **Unresolved:** L4 must profile actual trained readers and stream-scale null behavior. No commit.
