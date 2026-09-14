# R1-X6 — round-6 repairs, reference identity and scale audit

Codex, 2026-09-14; source HEAD `0d79f513dbba023bfd9635ef00504a4807ced8d4`. Read-only CPU audit. Evidence: [x6_audit.json](r1_round7/x6_audit.json); command/log: [x6_audit_cpu.txt](r1_round7/x6_audit_cpu.txt); reproduction: `PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= python -m scripts.r1_x6_audit --output <new-repository-path>`. The run took 16.93 s, used the CPU JAX backend, and made no real-base or teacher queries.

**Both stated scale risks reproduce. The reference weights/pool/stop-list hashes match. Ledger charging is repaired at the tested logical-prefix boundary; bank cache verification and some population guarantees remain incomplete.** The earlier owner's response marking R50-06 fully repaired overstates the code's guarantees. This audit extends [the round-6 response recheck](review_r1_50_response.md).

## 1. Disposition of ae22d73 and b7a38e5

| Checkpoint | Current evidence | Disposition |
| --- | --- | --- |
| R50-04 integer allocation | Odd memory 5 now yields five records. | Repaired in the tested case. |
| R50-04 both domains' own/paraphrase/locality queries | All 512 default-sized synthetic episodes include both domains. Query triples number eight in 509 episodes and nine in three, because repair appends a missing domain. | Default coverage reproduced; not fixed-count domain stratification. |
| R50-04 outside-domain guarantee | Outside queries omit a domain in seeds 113 and 251. | Broader every-domain/every-role docstring remains false. |
| R50-02 insufficient pool | Two domains with two available rows each, memory 4/outside 8, return zero outside queries without refusal. | Admission still incomplete; do not infer that sampling always raises. |
| R50-06 recorded metadata | Real banks now have identity metadata; constructor binds requested pool/base/encoder/limits. | Useful metadata addition, insufficient content/provenance verification. |
| R50-06 migration | A changed cached prompt still passes the migration's self-comparison and ID/length checks. | Open before freeze. |
| R50-06 query-source identity | Changing paraphrases, locality prompts or subject leaves `bank_identity` unchanged. | Open; these affect the cached query features. |
| R50-06 artifact identity | Changing a cached key feature leaves `content_hash` unchanged; changing prompt tokens still passes `verify_bank` if metadata is untouched. | Open; the reported hash is not a serialized-feature-bank checksum. |
| Legacy pickle access | b7a38e5 uses `getattr` in the driver. | Prior direct-attribute crash repaired. Synthetic `AttributeError` in evidence explains the repair and is not a current driver failure. |
| R50-08 operating-point hygiene | Weight bytes, dataset/query-null mode and threshold/gate naming improve identity; child jobs lease by default; grid and selection caveat recorded. | Partial: source/base/stop-list/default identity is still not bound to summary reuse. Per-dataset M5 is retired for the current single rule. |
| R50-09 fast trainer | Actual tiny-base differentiated episode charges six full forwards, six reverses and 331 valid forward-token positions; finite gradients. | Logical prefix accounting reproduced. Accelerator-time/compilation accounting still requires profiling. |
| R50-09 cached construction | Re-execution summary records bank construction separately, charged once. Weight directories refuse overwrite. | Source and arithmetic checks pass; historical original-run costs are not retroactively measured. |

The synthetic cache mutations occur only in memory. No real bank is changed. Both actual banks' current identities and byte SHA-256s are recorded. Earlier independent token equality checks remain useful, but stamping the current expected base/encoder identity does not prove which base originally computed those features. A complete repair needs all build inputs and recipe in the identity, an independently bound artifact checksum, and a documented migration/rebuild policy. Full pool admission must check unique fact/item IDs, valid/disjoint splits, sufficient memory/outside counts and required query-role coverage.

## 2. Reference-condition identity

Every declared seed-0/1/2 weight file, both training-pool JSON hashes and the installed stop-token manifest hash in `primary_condition_v1.json` match disk. The reference parameter hash is `e53d7ee1baaf9c47a827b5914cad1a128214484587c1b6da28a6816a56e7d81e`; seed-0 NPZ SHA-256 is `9f676076ad94df2fb6a3257c5838edb9e365f7ddc808efd2d044ef6e01f626fd`.

The primary is the **64-record mixed-domain trained reader**, stable observations, tied cosine heads, pairwise/query-null/lexical terms, stop list v1, hard top-1, top-k four, null threshold 0.5, no cosine gate, binary mass and five normalized per-position delta steps. No predictive-coding superiority or settling benefit follows from this feedforward BP development result.

The reference manifest is a development pointer, not a complete freeze: several settings are prose/default-dependent; source code, the complete base/calibration/decoder configuration and outcome artifact hashes are not fully enumerated there. Its continuation-control text says the variant decision is pending, but **DEC-040 has since chosen both treatments**. Its CounterFact risk range includes 0.625 from the distinct 256-record-training candidate; that value is not seed-0 reference behavior. Matrix v3 uses the explicit reference identity, retains the original seed-0 checkpoint, and labels continuation and alternative-reader evidence separately.

## 3. CPU reproduction of the scale profiles

The audit invokes the installed `profile_memory` calculation on the cached banks, with the same seed-0 RNG sequence, bank order, memory sizes and 200-query limit. It records exact item IDs and per-role denominators absent from the original summaries. **No saved metric differs from the CPU reproduction by more than 1e-5.** The discrete risk rates reproduce exactly.

| Dataset / memory | Paraphrase own-record firing | Own record in top-4 | Locality hard-null | Outside hard-null | Own/para queries | Outside queries |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CounterFact / 64 | 0.71875 | 0.875 | 0.96875 | 1.000 | 64 | 200 |
| CounterFact / 100 | 0.810 | 0.950 | 0.990 | 0.995 | 100 | 200 |
| CounterFact / 300 | 0.795 | 0.900 | 0.990 | 0.980 | 200 | 200 |
| CounterFact / 1,000 | **0.590** | **0.725** | 0.975 | unavailable | 200 | **0** |
| zsRE / 64 | 1.000 | 1.000 | 1.000 | 0.915 | 64 | 200 |
| zsRE / 100 | 0.980 | 1.000 | 1.000 | **0.870** | 100 | 200 |
| zsRE / 300 | 0.985 | 1.000 | 1.000 | **0.665** | 200 | 200 |
| zsRE / 1,000 | 0.980 | 0.995 | 1.000 | unavailable | 200 | **0** |

At 1,000 CounterFact records, 27.5% of tested paraphrases lack their own record among the four candidates. Own firing additionally requires selection and non-null acceptance; candidate recall alone cannot explain all failures. On zsRE, the outside false-fire rate rises from 13% at memory 100 to 33.5% at 300 while locality hard-null remains 100%.

The two banks contain only 1,000 records each, so at memory 1,000 no outside fact remains. Null entries are unavailable results, not perfect rejection. R1-44 supplies the actual generation endpoint; a separate same-pool reserve is required for its 1,000-record point.

The reviewed top-16 file reports CounterFact memory-1,000 candidate recall 0.895, own firing 0.64 and locality hard-null 0.925. Its RNG uses a **different size schedule (300, 1,000)** from the top-4 file (64, 100, 300, 1,000), so the compared memories/queries are not a paired top-k ablation. The direction is suggestive but cannot isolate top-k's effect; rerun with identical IDs. Likewise the m256 profile uses a different schedule and a different trained checkpoint.

These are cached-feature **selection diagnostics**, not complete-answer ES/RET-GS/LS measurements. Memory points use separate permutations, query counts vary, and the bank includes training/selection-held-out items. No causal memory-size estimate, independent confirmation or confidence interval based on 200 independent facts across reused sizes is established. The script omits full config/source/bank hashes and denominator/RNG metadata in its original output, imports JAX before the determinism setup, and can overwrite an existing profile path. The audit captures these missing identities additively and forces CPU operation; it does not change the owner's script.

## 4. Continuation budget reconciliation

The new accounting re-execution gives **458,002 outer forward-token positions + 313,579 cached-bank construction positions = 771,581 forward-pass tokens**. The reconciliation manifest and summary hashes match. Reverse positions are reported separately; equal forward tokens are not equal FLOPs, wall time or data exposure.

The accounting rerun's parameter hash is `d1d9bc609fe30ae4b39654d6c432d8f264e89afa9799400a4d74e475e4acfe28`, different from the reference checkpoint above. The manifests disclose this correctly: continuation evaluates the pinned reference reader but uses a re-execution of its training configuration for accounting. Do not describe the rerun as reproducing the exact reference weights, nor its cost as a retrospectively measured original-run ledger.

Literal self-KD spends 771,580 forward-pass tokens (one odd token unspent), split across 385,790 teacher and 385,790 student positions. Informative LM uses 771,581 student forward positions and reads 771,582 source tokens including lookahead. The different reverse work and exposure are explicit comparison limits. Existing recipe `limitations` strings inherited from older manifests are stale where they still imply the fast trainer lacks forward/reverse counters; exact hardware cost still remains unverified.

## 5. Before Stage 4

Close cache verification and input admission; bind complete run identities and immutable profile outputs; execute paired scale diagnostics and same-pool unseen generation with sufficient reserve; distinguish the pinned reference from alternative training/accounting checkpoints. Profile every new endpoint and both DEC-040 treatment evaluations before choosing ceilings. Keep the learned primary, but require fresh-data evidence above stable and matched controls and a clear separation of full-package gain from learning-specific or predictive-coding claims. No existing files, GPU jobs, sealed payloads or final populations were changed by this audit.
