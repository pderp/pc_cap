# R1-46 — review of stream-scale training, feature banks and operating points

Codex, 2026-09-14. Read-only review of `stream_train.py`, `train_fast.py`, the lexical reader/deployment path, `r1_50_stream_train.py` and `r1_52_operating_point.py`. Evidence and source hashes: [stream_review_evidence.json](r1_round6/stream_review_evidence.json). No real-base queries, GPU training or existing-file edits were performed.

**The reader-input boundary appears correct in the inspected path:** query selection uses prompt-only observations and prompt-token overlap; target record IDs and answer labels select training losses rather than reader inputs. The four intended populations are present under valid default sizes. The main remaining concerns are reproducible cache/configuration identity, silent population changes for invalid/small pools, calibration across memory sizes and domains, and incomplete compute accounting. They warrant gates before freezing, not an assertion that the current learned-reader result is invalid.

The owner has now completed mixed-domain training: at null threshold 0.5 with no cosine gate, the saved development summaries show ES/RET-ES/RET-GS/LS = **1.00/1.00/0.98/1.00 on zsRE** and **1.00/1.00/0.795/1.00 on CounterFact** (`stream_eval_mixed_null0.5[ @counterfact].json`; the space is only explanatory). This supersedes the earlier default to drop the learned reader; DEC-038's proposal was withdrawn. These remain 100-edit development results with selected architecture/data, not confirmatory evidence or proof that one rule will work at all occupancies.

## R50-01 — Prompt-only selection survives label reassignment (positive gate, limited scope)

`build_bank` obtains record keys from the support prompt alone and obtains code features from support prompt plus taught answer. The latter is legitimate support information. Own-query selection reuses the prompt key observation. Paraphrase selection observes only its prompt IDs; locality selection observes only its locality prompt. `stream_episode` exposes those prompt observations and prompt IDs in QueryFeat; `lex_matrix` compares them with support prompt IDs. `_selection` and the batched selection function receive embeddings/keys/lexical values, not `target_record` or answer targets.

Teacher-forced answer-prefix observations occur in PrefixFeat for the outer answer objective. Later prefix IDs contain earlier answer tokens, which is appropriate for the training loss. The selection embedding remains the original prompt embedding across those prefixes. Target labels must not be confused with those training-only causal prefix inputs.

The CPU control runs the actual episode builder and packer on controlled features, changes every query's record label and token target, and confirms unchanged support/query observations, lexical matrices and prefix token inputs while packed training targets change. This is a boundary test, not a claim that a real-base bank was recomputed under alternate labels. The static builder inspection supplies the complementary source trace. The query objects carry labels for loss computation, but the reader-facing argument boundary excludes them.

No evidence of held-out-answer leakage into selection was found. Preserve this separation when adding subject spans or more lexical features. A future cache must bind the exact text/token source so that label/input boundaries remain reviewable after loading.

## R50-02 — Valid default populations are correct; input admission is incomplete (medium)

With eight memory records, three queried records and two outside records, the executable control produces three own prompts, three paraphrases, three locality nulls and two out-of-memory prompt nulls. Positive target indices map to memory positions; outside-query IDs are absent from memory. Locality prefixes carry cap-off logits for preservation KL. Out-of-memory prompts carry only the null retrieval target and no KL reference.

Several unchecked inputs silently change that population:

| CPU reproduction | Observed behavior |
| --- | --- |
| 20-item pool, memory 20, requested outside 8 | Zero outside queries, no refusal |
| Repeated pool indices [0,0,0,0] | Four copies of one support record, no refusal |
| Merge banks with duplicate item IDs | Eight items but only four `by_id` entries, no refusal |
| Different items with the same fact ID | Out-of-memory rows are still labelled null although that fact is represented in memory |
| Per-pool held-out count 6 with a four-item pool | Driver split arithmetic creates indices [-2,-1,0,1,2,3]; negative indexing can repeat/overlap items |

These are boundary defects, not demonstrations that the current 1,000-item banks hit them. Require integer/nonnegative sizes, unique pool indices and item/fact identities, explicit subject/group split rules, and enough items for memory plus outside queries before building anything. Validate train/dev indices as disjoint in-range sets and report actual counts rather than silently truncating requests. If incomplete role coverage is intended, name the reduced population and weight policy.

`build_bank` also does not inspect the `excluded` result of paraphrase `tokenize_pair` or explicitly validate all locality lengths before observation. Valid prepared pools may avoid this; a malformed/overlong new pool should fail with a data-admission result before partial feature computation. Do not treat tokenization failure as an ordinary negative query.

## R50-03 — “Out of memory” and “locality” are hypotheses about facts, not merely row positions (medium)

The sampler uses distinct item indices, which is sufficient only if the pool already enforces distinct relevant facts/subjects. A neighbour can in principle coincide with another edited fact's own prompt; an outside row can alias an in-memory fact. Those should not be automatically labelled null. The generic builder currently trusts the pool.

The actual inspected banks have unique exact subject strings, zero exact train/dev subject-string overlap, and zero exact cross-domain subject-string overlap. An additional check of every cached locality prefix against all 2,000 support prompts found **zero exact token-sequence matches**. Across 512 default mixed training episodes, no null query exactly matched an in-memory prompt. See [population collision check](r1_round6/stream_review_population_collisions.json). These positive checks do not resolve paraphrase/alias equivalence or hidden contextual entity overlap; the versioned exclusion policy remains necessary.

Both dev banks are held out from their training indices, but they are development data used for checkpoint selection. The stop list also incorporates natural development texts. Neither bank's held-out partition is a final untouched test population.

## R50-04 — Mixed-domain allocation is approximate and does not ensure both domains' queries in every episode (medium)

`stream_episode_mixed` independently rounds each pool's share of memory-plus-outside rows, with a minimum of one, then reshuffles and delegates to the generic sampler. This can alter requested totals: equal pools with memory 5 and outside 0 produce four memory records because Python rounds 2.5 to 2 for each pool. Small pools are also silently clipped.

The default two equal 900-item training pools with memory 64/outside 8 do not hit that rounding shortage. However, drawing query records uniformly from the mixed memory does not guarantee both domains' own/paraphrase/locality queries in each episode: **3 of 512 deterministic default-sized synthetic episodes** missed a domain among their eight own-prompt query records (seeds 119, 238 and 295). Thus the docstring's every-episode language is too strong.

Use exact integer apportionment with a stated remainder/tie policy and capacity checks. If per-episode domain coverage matters, stratify memory and query-record selection separately. Otherwise describe the sampler as proportional in expectation and report domain/role counts; do not infer exact balance from the merge operation. No need to retroactively reject valid runs solely because their per-episode draws fluctuate.

## R50-05 — Binary class balancing differs from role/domain balancing and from the optimized prefix objective (medium)

The retrieval loss assigns half its total weight to record-target queries and half to null-target queries when both exist. Within each binary class, queries are weighted equally. The normal default with eight queried memory records and eight outside records gives own/paraphrase/locality/outside counts 8/8/8/8, hence one quarter of L2 mass per role. With only two outside records in the CPU example, locality receives 0.30 and outside 0.20, while the six positive queries share 0.50. Missing classes use the fallback mean.

This balances applicability classes, not domains, subjects, relation families or answer lengths. The two training pools currently contribute different source label lengths: the CounterFact pool contains only two-token answer sequences including newline, while the inspected zsRE bank spans 2–14 tokens. Both banks exactly match the first 1,000 ordered rows of their current source pools; the CounterFact observation is a property of the source population, **not cache corruption**.

FastTrainer sums per-prefix answer/KL contributions into gradients while reporting mean per-prefix loss values. The reference also accumulates prefix gradients, so the batched implementation is not thereby numerically wrong. It means variable answer length, number of queries and number of preservation prefixes change the effective balance between answer, preservation and the one-per-episode retrieval objective. Mixed-domain runs can therefore weight longer zsRE answers more heavily even with equal domain query counts. State the optimized reduction and report role/domain/token totals; compare any normalized alternative as an explicit change.

## R50-06 — Loaded feature banks lack sufficient cache identity and cost provenance (high before freeze)

The cached files contain only `items`, `dataset` and `cost`. The driver key is pool basename plus requested item count. Loading does not verify a pool-content hash, ordered item/token hash, base checkpoint, observation encoder version/taps, builder source, paraphrase/locality limits or logits dtype.

This review hashed both actual files and checked their ordered IDs and prompt/answer arrays against the current source pools: **both match; zero missing IDs or token mismatches**. Nevertheless, matching now does not establish the base/encoder identity used to construct them, and a future changed pool/base/code can silently reuse the same path. Different pool paths sharing a basename can also collide.

Use a cache manifest with those identities and refuse mismatches before loading into an episode; include the exact bank hash in every training summary. Version result and checkpoint destinations together. The training driver refuses an existing result directory but permits an existing weight directory with `exist_ok=True` and overwrites `theta.npz`; it should guard orphan checkpoint directories as well. These are owner file changes, not performed in this review.

Locality logits are stored in float16 and upcast by the trainer. That is a declared approximation to a full-precision cap-off KL target, not an exact reference representation. Record the dtype and quantify any relevant effect in the fidelity profile.

## R50-07 — Training and deployment have different selection support and write semantics (high for calibration claims)

Training computes a softmax over **all episode records plus null**. Deployment retrieves top-k records, computes its null against that restricted set, then makes a hard top-1/gated decision and uses taught per-position deltas. Training's answer/preservation objective passes a soft code mixture through the controller; it does not simulate the deployed support-delta optimization and hard writes.

Thus the improved trained embedding/null is supported by the observed stream results, but the training objective is a surrogate for deployment. The null probability's denominator changes with record count and top-k filtering even if individual logits stay fixed. A balanced-training threshold of 0.5 has no automatic deployment-prevalence interpretation. A data-prior correction alone is insufficient when the candidate support and score distributions also change.

Profile and evaluate memory sizes 64/100/300/1,000, candidate recall, best-record identity, null/gate activation and full-answer locality separately. Any train-with-top-k, hard/soft relaxation or delta-in-the-objective experiment needs its own declared estimator and controls. The current mixed-domain 0.5 result is a promising operating point; it does not remove these scale-transfer questions.

## R50-08 — M5 is an explicit development optimization, with missing admission checks (high before freeze)

The helper chooses the largest RET-GS subject to observed LS >= 0.99 among seven null thresholds crossed with two gate settings. This is a transparent development policy if its data/checkpoint/choices are frozen before the fresh run. At 50 locality queries, LS changes in steps of 0.02, so LS >= 0.99 requires 50/50 observed successes; it does not establish 99% population preservation.

The helper's objective does not enforce ES or RET-ES floors, though the presently selected rows have ES/RET-ES 1.00. Add the plan's chosen acquisition constraints before a final operating-point protocol. Record the grid, tie-break policy, failed/unavailable rows and held-out data identities. Repeated seed-22 streams from the same development pool are useful replication, not a fresh confirmatory realization.

Cached sweep results are accepted merely because a tag-based summary exists. The tag omits such potentially changing identities as checkpoint bytes, stop-list contents, query-null configuration, data/source version and stream seed. The helper does not compare cached summary arguments/hashes with the requested condition. A reused tag can therefore select from stale results. Before reuse, validate the full configuration, dataset and ordered items; otherwise require a new identity.

The helper also invokes the stream driver with `--no-lease` unconditionally and itself has no enclosing GPU lease. The owner may have coordinated the particular runs externally, but the entry point alone does not guarantee that coordination. A new sweep must hold the normal lease rather than rely on an unrecorded assumption. This review did not launch one.

## R50-09 — Fast training remains outside complete ledger accounting (high before matched-compute claims)

The feature builder charges its base forwards. Cached banks carry the original construction cost, but loading them does not add that historical cost to the current ledger, which is reasonable for incremental reuse only if shared construction is recorded and charged once separately. The current summaries do not bind a cache identity/accounting policy.

FastTrainer calls `g.forward_jit` inside differentiated JAX functions without routing the outer answer/preservation work through the ledger. Reported train wall times are therefore useful synchronized-work proxies but the ledger cannot certify full forward/reverse/token totals. With cache reuse, this can make the apparent learning ledger particularly small despite substantial work. A two-minute trained-reader run is not a two-minute full pipeline including all earlier bank construction by implication.

Require actual base/solver call and token accounting, cold compilation/warm execution spans, shared feature-bank cost and all rejected work before comparing against continuation or PC variants. The mixed training summary records 286.851 s training wall time; that number does not close the cost gate by itself.

## Recommended next checkpoint

Keep the learned mixed-domain reader as the current development primary, with the random reference, matched updates and stable/live controls. Before freezing: validate and hash banks/configurations; reject invalid sampling/split cases; make the deployment threshold/grid and class/domain reductions explicit; reconcile actual cost; and complete register v3 with **all 6,000** reserved zsRE subjects. Then replicate across fresh development orders/subjects and occupancies, preserving ES/LS alongside RET-GS.

R1-45 recommends adding a support-subject overlap signal beside the existing lexical overlap, but the current single-rule improvement is already an important comparator. Treat the proposed feature as an ablation, not a mandatory redesign that delays checking the working system.

The review is complete. Repairs to shared builder/trainer/driver files belong to the orchestrator and require the existing ownership/permission protocol. No production repair was needed to produce this report, so this lane did not request or apply shared-file edits.
