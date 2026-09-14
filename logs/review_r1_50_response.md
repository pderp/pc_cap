# R1-46 addendum — recheck of the owner's repairs

Codex, 2026-09-14. This additive report follows `review_r1_50.md` and `docs/tasks/R1-46-response.md`. The owner applied repairs in ae22d73 and an old-pickle access correction in b7a38e5 while the round was in progress. CPU evidence is in `r1_round6/stream_response_evidence.json`; the exact reproduction is `scripts/r1_46_response_audit.py`. No existing files, banks or weights were changed by Codex.

**The first repairs improve default mixed-domain coverage and add cost/identity metadata, but bank identity is not yet a complete pre-freeze gate.** The earlier report describes its earlier hashes; this addendum distinguishes repairs already made from remaining defects.

## R50-06 remains partially open: recorded identity is not a verified cache

Three independent synthetic counterexamples remain at the hashes recorded in the new evidence:

1. **Migration compares the bank with itself.** The allegedly verifying expression compares `b.content_hash()` with a second hash assembled from the same bank's item IDs, prompt tokens and answer tokens. Both sides change together. Length and item IDs are compared with source rows, but token arrays are not. A bank with one changed prompt token still passes the entire migration predicate. It is then stamped with the requested pool/base/encoder identity without evidence that those features were built with it.
2. **Identity omits inputs used to build queries.** `bank_identity` hashes source item IDs and prompt/answer arrays only. Changing paraphrases, locality prompts or subjects leaves the pool identity unchanged. The builder uses paraphrases/localities to construct cached query observations and preservation logits, so those fields must be included with exact tokenization/recipe identity. Builder version 2 is useful only with disciplined changes and complete inputs.
3. **Verification checks the stored dictionary, not cached contents.** `verify_bank` compares metadata to expected metadata. It still accepts a bank after modifying its prompt array, and the reported `content_hash` ignores observations, code features, prefix targets and locality logits. A modified key observation does not even change that hash. The current field called `bank_sha256` should not be read as a complete serialized-bank checksum.

These demonstrate missing detection, **not evidence that existing cached feature values are wrong**. The initial audit independently matched both real banks' prompt/answer arrays to their pools. Both real files now have identity attributes and new byte hashes, consistent with owner-managed stamping during this round. Retrofitting the current expected base identity still cannot establish historical construction provenance.

Recommended owner repair: hash the complete build inputs and recipe; bind a complete artifact checksum; check loaded artifact bytes and stored identity against a versioned manifest. For pre-identity banks, either recover an independently recorded construction identity or rebuild under a new resource path. Token equality alone cannot certify the historical base/encoder used for feature computation. Do not overwrite the old bank while manufacturing new provenance.

The direct `b.identity` access failure for old pickles was repaired by b7a38e5's `getattr`. Our synthetic legacy object still demonstrates why that change is needed, but it is **not an unresolved driver crash in the rechecked version**.

## R50-02/04: coverage improved, with remaining admission and population details

The repaired sampler produces exactly five supports for the earlier odd-size fixture. Across the same 512 default-size synthetic draws, every episode now contains own/paraphrase/locality queries from both domains. Own-query counts are eight in 509 episodes and nine in three: the repair appends a triple when a domain is missing. This changes the role counts and prefix-summed objective weight on those episodes; it is not fixed-count stratified selection.

The broader docstring still promises every domain's **out-of-memory** prompts in every episode. Seeds 113 and 251 omit one domain among outside queries. Stratify the memory/outside partitions separately if this is a requirement; otherwise state expectation rather than guarantee.

Contrary to the response's “undersized pools still raise” statement, two domains with only two available rows each, memory four and requested outside eight produce **zero outside queries with no refusal**. Slicing silently clips selected pools. Duplicate indices/item IDs, disjoint held-out ranges, valid sizes and nonempty role lists remain preflight work. These are reproducible boundary issues, not proof that the owner's normal 1,000-item banks are invalid.

## R50-08/09: improvements and limits

The operating-point helper now delegates to leased child runs by default, can explicitly skip the lease when already coordinated, binds theta bytes plus dataset/query-null mode into the tag, and records the grid/selection caveat. Threshold/gate values also occur in each run tag. The old per-dataset selection is no longer needed for the present single deployment rule.

The tag still omits source-tree, base, stop-list and implicit-default identities, so identical weight/config tags should not alone justify reusing summaries after those dependencies change. Full admitted run configuration needs a source/resource fingerprint before formal reuse.

FastTrainer now accepts a ledger and charges outer full forward/reverse counts and prefix tokens. Training summaries include per-bank construction counters and the shared-cost policy; weight directories refuse overwrite. These are visible source improvements. No fresh real-base gradient or GPU timing run was executed in this CPU recheck. The historical mixed seed-0 summary used in matrix v2 predates those counters; the repair does not retroactively make its exact training tokens known. Acceleration-time attribution and cold compilation still need the dedicated profile.

## Scale evidence changes the next scientific priority

The owner's new bank profiles already show why 100-edit development success is insufficient. At 1,000 records, CounterFact's top-4 retrieval misses the own record for 27% of paraphrases; top-16 improves coverage but does not restore reliable selection and lowers locality rejection. zsRE's out-of-memory null rejection worsens with occupancy even while its existing locality endpoint remains high.

Continue the larger-memory training/selection experiments on development data, measuring both candidate recall and null/selection errors across all four populations. The subject-overlap feature recommended by R1-45 is a targeted candidate for a declared ablation; high lexical AUC by itself does not guarantee a better deployed null. Neither a larger candidate set nor a new checkpoint should be silently substituted into the pinned matrix.

The owner can address these source repairs concurrently with Codex's additive data/matrix work. Existing-file repairs remain with the owner; Codex has not applied them or requested a source edit for this review-only lane.
