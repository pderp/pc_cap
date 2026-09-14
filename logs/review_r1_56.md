# R1-X8 — counter-review of R1-55, R1-56 and the Stage 2 report

Codex, 2026-09-14. **Review complete; implementation and final admission require the owner actions below.**
This lane performed CPU source/payload arithmetic and synthetic state tests. It did not execute the real base,
use the GPU, open sealed streams, alter installed owner files, or select final examples.

Evidence: [initial source snapshots](r1_round9/source_evidence.json),
[DEC-043/044/045 update](r1_round9/source_update_dec045/index.json),
[100-source numerical recount](r1_round9/x8_evidence.json),
[cache reproduction](r1_round9/x8_cache_review.json),
[protocol/MQuAKE audit](r1_round9/protocol_reconciliation.json).
The recount checks six P1 profiles, sixteen unseen summaries/reports and twelve development streams; source hashes
are rechecked at the end of collection. The current adopted gate and three-dataset scope supersede the report's
earlier proposed-gate and reduced-matrix wording.

## 1. High priority: cache identity is not memory-content identity

The reviewed `RevisionCap._rare_overlap` caches active-record token document frequencies under
`(len(store.records), len(store.active_records()))`. This works for an ordinary supersession that appends a
record and for the tested rollback after an intervening query. It fails when contents change but both counts match.

| CPU state transition | Correct overlap for query token 7 | Current result | Proposed repair |
| --- | ---: | ---: | ---: |
| Import three records containing token 7 after caching a different three-record store where token 7 appears once | 0 | 1 | 0 |
| Cache [7], [7], [9]; remove [9] and add [7] before another query | 0 | 1 | 0 |
| Append a superseding record changing DF from 2 to 3 | 0 | 0 | 0 |
| Roll back that queried supersession to DF 2 | 1 | 1 | 1 |

With the accepted maximum DF of 2, the first two stale caches admit a token that is no longer rare.
`import_state` replaces the store but does not clear the cache. Equal state hashes and equal exported byte
counts do not test this behavior.

[scripts/r1_x8_cache_review.py](../scripts/r1_x8_cache_review.py) reproduces the transitions using the actual
RecordStore and a RevisionCap shell, without a base constructor or model forward. The
[proposed patch](../docs/tasks/R1-X8-cache-repair.patch) adds a store lexical mutation version, increments it on
add/remove, keys the cache by store identity/version and clears it on import. It passes the same reproductions
when compiled in memory. **The patch is not applied.**

Reviewed hashes: memory `c214c2a74cd396936cc674befda13c79ad04e126759872eed1a3b55d70169f64`;
learner `4bb7b848bd1e3d34249379fb5b840062e5f95082a403a8895f8cb6d7ae68b451`.
The owner must review any later changes before applying it, add installed regression coverage, and check all
permitted active-record mutation paths. This patch does not resolve host-cache byte accounting.

## 2. Rarity is a lexical rejection rule, not a semantic guarantee

Both support and query overlap are sets. Repeating a record's rare token 100 times contributes **one**, so
repetition cannot manufacture a minimum of two distinct rare tokens. Under the accepted minimum of one,
an otherwise unrelated sequence containing one rare support token satisfies this predicate.

That is a demonstrated predicate limitation, not a demonstrated complete model attack: learned selection,
null mass and any cosine floor run before the rare-token test and can still reject the query.
A BPE token can be rare without uniquely identifying the subject or relation. Document frequency also changes
as active memory changes. The existing CPU test checks template/common versus rare overlap and config mismatch;
it does not cover same-count restore/replacement or adversarial lexical insertion.

Owner action: retain the gate as the accepted fixed development rule, qualify semantic claims, add transition
tests, and predeclare a development-only adversarial insertion/alias/morphology screen. Do not tune the gate
against final examples or call a rare-token hit proof of applicability.

## 3. High priority: P1 does not profile the registered random condition or adopted v3

All six P1 artifacts concern ungated configurations. The historical files predate explicit gate metadata or record
`rare_overlap_min=None`; the driver has no requested gate in these runs. They support v2 capacity observations,
not adopted-v3 cache cost or byte certification.

Both the original `nonlearned` and its `nonlearned_v2` rerun use lexical features and pairwise null, null
threshold .5, minimum cosine .93 and newly initialized weights. The registered random condition has lexical off,
pairwise null off, null threshold **1.01**, minimum .93 and a pinned random checkpoint. The rerun corrected the
firing observer to use actual hard-null decisions; it did not make the condition match the matrix.

Learned-v2 measurements are internally consistent:

| Dataset | 1,000-record logical bytes | Fraction of 67,108,864 bytes | Query median at 1,000 | Whole profile wall |
| --- | ---: | ---: | ---: | ---: |
| zsRE | 49,941,992 | .744 | 14.374 ms | 139.669 s |
| CounterFact | 34,032,624 | .507 | 14.552 ms | 90.413 s |

All 1,000 edit rows are present/unique and accepted. Saved query medians and role firing rates recount correctly.
Round-trip export/import hash and reported bytes agree at each checkpoint. Answer length affects cost and storage:
these histories do not certify every possible fresh 1,000-answer distribution. Logical state, device peak and host
RSS are distinct measures; the mutable Python DF cache is not included in the logical-store byte/hash reports.

Owner action: label P1 as v2/development and the random surrogate by its actual configuration. Profile exact v3,
registered random and all other retained conditions with source/config/weights bound; measure cache rebuild and
restore-equivalent query behavior. Initialization/JIT and steady-state edits need separate timer boundaries.

## 4. CounterFact locality firing is not an observed LS loss

P1 CounterFact locality firing rises from 0 to .06 to .10 at 100/300/1,000. Its query records save role, time,
steps, stopping and firing, but no prompt IDs or generated answer text. A fired write need not change the final
bounded answer. Therefore the report's “LS at 1,000 CounterFact records will fall below 1.00” is a hypothesis,
not a measured result.

Likewise “the 1,000-edit endpoint is admissible” overstates an occupancy/restore profile. Full retained ES/GS,
paired locality answers, source freshness and implementation admission have not all been shown for that endpoint.

Owner action: report the firing diagnostic precisely and run paired cap-on/reference decoding on fixed query IDs
for actual high-occupancy locality and retention. Store IDs, stop flags and outputs in the profile artifact.

## 5. Pool fillers are development evidence; cross-size comparisons change query populations

R1-44 extends the 300-item development store with training-pool rows beyond the first 1,000 used in the feature
bank, excluding development IDs. At 1,000 edits it consumes 700 such filler rows. The outside list comes from
remaining pool rows. All belong to already reserved/exposed development resources; being outside the feature bank
does not make them fresh confirmation subjects.

Independent identity recount:

| Size comparison | zsRE outside-ID overlap | CounterFact overlap |
| --- | ---: | ---: |
| 100-pool → 300-pool | 80/100 | 62/100 |
| 300-pool → 1,000-pool | 0/100 | 0/100 |

The source-qualified 100/300/1,000 v2 rates are zsRE pool **12/25/45%**, CounterFact pool **0/2/5%**.
The often quoted zsRE **7/25/45%** uses the development remainder at 100 and pool remainders later.
Neither sequence alone identifies a pure memory-size effect.

The gate comparisons **within each size** are better controlled: v2 versus v3 uses identical ordered edits and
outside IDs for zsRE 100-development (7→5), 300-pool (25→11), 1,000-pool (45→10), and CounterFact 1,000-pool
(5→0). This supports a development reduction with the gate on those paired examples. It does not establish
a universally flat rejection curve or justify a pass threshold of 10%.

Owner action: fix the causal wording and source labels; keep a fixed outside population disjoint from the entire
future edit history for final size comparisons. Preserve canonical subjects/aliases and full attempted history.
R1-44's observed inactive/superseded metadata checks and retention of attempted failed edits are useful; extend them
to every comparator before final use.

## 6. The CounterFact truncation count is reversed in the report

`text_s0_v1_unseen_counterfact` contains **67 pairs where both answers terminate and 33 pairs with truncation**.
The report says “33 pairs untruncated.” All 100 bounded answers are unchanged, but strict complete-answer
preservation is **67/100=.67**, not 100% and not 33/100. All 100 firing outcomes remain in the false-fire denominator.

Owner action: correct this table and consistently publish both bounded and strict-preservation denominators.
Do not discard truncated examples or call missing stopping information a complete pair.

## 7. Drift is substantially reduced, not certified removed; gated drift remains unavailable

The text-null **v2** CounterFact assay has on-NLL 4.12145133175, off-NLL 4.10904388702:
Δ=.01240744473 nats/token, exp(Δ)=1.0124847364. Fourteen of 4,064 scored prefixes fire; the three sampled
lengths per window see 0/96. The zsRE v2 Δ is approximately −.00000117634.

The abstract's “drift ... removed” is too strong: the CounterFact value exceeds the provisional .01 ceiling
on that diagnostic. These small fixed-window results do not certify full-validation preservation.
The current drift script cannot configure the rare gate, so none is exact-v3 drift evidence.

K windows of 128 tokens score **127K**, not 128K, positions. K=128 is 16,256, and that subset is still not the
full validation split. The ≈165-second timing is a component estimate for the stated assay, not a priced full
corpus endpoint.

Owner action: add hash-bound rare-gate configuration to the drift driver and exact selection receipts,
evaluate the adopted recipe, and distinguish probes, scored positions, subset and full-split denominators.

## 8. Other report claims need narrower language

- Oracle routing at .94 shows much stored information is usable. “Storage exonerated” does not prove absence of
  all value/retention problems.
- The tested random packages fail some neighbours. “A learned applicability decision is needed” does not rule
  out every alternative nonlearned rule.
- Text-null training changes the episode RNG stream and summed preservation terms. Its comparison is a package
  intervention, not an isolated null-example ablation with every factual episode/weight held fixed.
- Seed-0 CounterFact RET-GS falls .725→.715 under the gate; seeds 1/2 match, and zsRE matches. The twelve recounted
  streams support that statement. Reader seeds on reused data do not justify a paired noninferiority confidence claim.
- The report still calls literal continuation a numerical “no-op,” attributes S1 behavior to “no cap writes,” and
  broadly says continued training does not reproduce the gain. R1-X7 already established changed tensors,
  active StableCap use, and failure of the tested LM fidelity bound. Carry the qualifications already added to
  the notes into the report. A valid KL-bounded LM remains an unperformed retained control.
- The text-null training charge does not include the separately itemized factual bank. Candidate seed-0
  forward-token total is 1,134,362, not R1-24's matching basis of 771,581. Forward-token matching also does not
  establish equal reverse/JIT compute.
- Primary-v3 metadata inherits some v2 result fields alongside explicit gated results. Use named condition-specific
  result bindings; do not read inherited .725 CounterFact as the gated seed-0 result.
- R1-43/R1-44 endpoint summaries omit exact rare-gate settings even when tags differ; v2/v3 share weight files.
  Names and weight hashes alone are insufficient executable provenance.
- Reproduction commands without the gate reproduce v2. “Every script refuses overwrite” is false for the drift
  writer's existing output behavior. Fix the statement or the writer; bind actual behavior.

## 9. Scope, budget and new MQuAKE admission

DEC-043 accepts the gate. DEC-044 withdraws the scope reduction and supersedes 15 hours. DEC-045 keeps CounterFact
and adds MQuAKE, giving **360 cells**, not 240. At the same homogeneous 1,150 seconds/cell and .2 reserve,
the estimate becomes **138 hours**. This is not a measured all-condition ceiling. Whole R1-44 jobs include
edit replay; adding them as endpoint-only cost double-charges edits. Exact stable/live/S1/MQuAKE costs,
full-validation drift, composition and shared training remain unpriced.

A full v2 no-gate condition would add 45 cells. Resolve that allocation explicitly while preserving all eight
retained rows. The [new protocol draft](../docs/R1_stage4_protocol_draft_v2.md) lists all U01–U18 statuses and
the measurements still needed; nothing here admits a final launch.

MQuAKE provides 6,043 unexcluded subject/relation rewrites and 27,654 direct source questions. However, only
4,981 source cases retain all rewrite dependencies; 2,391 also have no exact excluded path-subject hit.
Neither count is final semantic/teacher eligibility. There are 19 later target conflicts, all retained and
marked incompatible with the first-case choice. The 924 exclusions are **subjects** covering 1,193 rewrites.

After cross-dataset primary-subject avoidance, a proposed additional 1,000-subject MQuAKE training reserve leaves
only 368 subjects of surplus beyond 4,050 confirmation-role reservations. This is a real yield risk.
Resolve training versus transfer and teacher/context yield before draw. The prepared locality/near lists are
per-item source annotations, not globally disjoint final reserves. Multi-hop dependencies cannot be assumed
compatible with arbitrary independently sampled edit streams.

## 10. Validation and owner disposition

The full installed CPU revision suite returned **318 passed, 8 skipped, 2 failures**:
an obsolete strict xfail now unexpectedly passes, and an old matrix test compares historical hashes against current
append-only decisions. These are outside the newly added implementations. The
[test-maintenance patch](../docs/tasks/R1-round9-test-maintenance.patch) passes both direct in-memory reproductions;
the [receipt](r1_round9/test_maintenance_preview.json) preserves the exact proposed scope. Application requires
the user's permission under the new-files-only rule; any subsequent disposition is recorded separately.

The new analysis/draw/MQuAKE/three-dataset tests account for 52 passing cases within that suite.
The cache reproduction separately demonstrates the two defects and the proposed fix. No real-base result was
generated by this review.

Prioritize owner work as follows: repair/cache regression and accounting; bind exact gate/profile/endpoint
configurations; resolve MQuAKE/CounterFact source and training eligibility; measure adopted/all-control profiles
and gated drift; update the report's factual/causal qualifications and the 360-cell matrix; admit final analysis,
payloads and costs. Concrete existing-file requests are in
[docs/tasks/R1-X8-edit-request.md](../docs/tasks/R1-X8-edit-request.md). No requested owner edit is silently applied.
