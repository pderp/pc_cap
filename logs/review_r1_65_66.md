# R1-X11 — R1-65/R1-66 and primary-selection counter-review

2026-09-15. CPU metadata/code review and stored-result recount. No real-base execution, training, draw, seal,
sealed-payload read or primary selection. Existing owner files are unchanged. Reproduce the episode/result audit with
`PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= /home/derp/cap/venv/bin/python -m scripts.r1_x11_training_review --output logs/<new-name>.json`.

Evidence: [rehearsals and result/source hashes](r1_round13/training_review_evidence.json),
[checkpoint and population recount](r1_round13/population_and_checkpoint_recount.json),
[profile recount](r1_round13/clean_profile_recount.json).
Sources include the actual training pools, old pre-R1-65 builder snapshot, current builder, loss implementations,
training CLI, nine stream summaries/checkpoints and three row-level unseen reports. No cached feature-bank pickle
or model checkpoint was loaded by the review script. Numeric feature placeholders never enter a loss or model.

## Findings

### X11-01 — the collision mechanism is real; the ≈13% denominator is wrong for these mixed runs

`_locality_choices` excludes locality token sequences equal to **any** in-memory record's own prompt. Both the
ordinary selection branch and mixed-domain query-repair branch use it. Remaining choices are permuted; if none
remain the locality query is omitted. The own-prompt and paraphrase targets are retained.

The heuristic (64−1)/(500−1) = 12.63% describes a homogeneous random 64-record memory from 500 items whose
locality neighbor is another item in that pool. The actual mixed run first holds out 100 items **per pool**,
then draws from CF 900 + zsRE 900 + MQ 400. Its proportional-domain episode builder does not put 64 MQ records
in memory. The heuristic also ignores which neighbors remain in the training versus held-out ranges.

A source-bound, metadata-only rehearsal of 300 batches × 2 episodes reproduces the ordered source pools,
first two paraphrases/localities, 64 memory records, 8 queried records, 8 outside records, training RNG seeds 0/2
and the **post-batch** draws for 8 of 1,536 ordinary-text null prefixes. It invokes the pre-repair builder snapshot.

| Historical builder rehearsal | MQ collisions / MQ locality queries | Rate | All collisions / all locality queries | Rate |
| --- | ---: | ---: | ---: | ---: |
| Seed 0 | 23 / 1,004 | 2.291% | 23 / 4,938 | .466% |
| Seed 2 | 21 / 996 | 2.108% | 21 / 4,912 | .428% |

CF and zsRE have zero such exact-token collisions in these rehearsals. These are reconstructed episode counts,
not recovered logs of actual historical episodes or a population confidence interval. They depend on the
bound source order/code/RNG recipe; cached-bank execution equivalence was not independently established.

The repaired seed-0 builder has **0/4,926** locality collisions; full-rate question nulls 0/4,929; 35% nulls
0/4,922. One locality query is omitted in the latter run. Random draws differ between variants, so the three
rehearsals are not paired training trajectories. The repair is justified by label consistency, but its existence
and a lower collision count do not establish that this was the sole cause of unseen false fires. Fixed-locality
tri4 still fires on 30–52/100 unseen zsRE queries.

Limits: exact own-prompt token equality is narrower than alias, paraphrase or semantic conflict clearance.
The helper does not certify all remaining null targets. R1-D1h's exposure policy is independent of this
within-episode target-consistency repair.

**Requested owner edit ER-01:** qualify the R1-65 paragraph in `docs/R1_stage2_notes.md`: replace the mixed-run
13% claim with the scoped counts above, preserve 12.63% only as a homogeneous-pool illustration, and replace
the unqualified causal assertion with “a contradictory-label mechanism and possible contributor.”
Keep the observed tri4 result explicit.

### X11-02 — R1-66 changes the null mixture, while balanced L2 keeps equal aggregate class mass

For an out-of-memory support, the builder always adds its own-prompt null. When enabled, it **adds** a
paraphrase-form null with probability p; it does not replace the original null. The added query takes the
prompt-only prefix from the paraphrase features, target record −1, no answer-token target and no cap-off logits.
Its `unrelated_no_kl` role contributes retrieval L2, not answer L1 or preservation L3.

Both `train.retrieval_loss` and `FastTrainer` use `LossConfig.balance_null=True`. When both classes exist,
each record query has weight .5/n_record and each null query .5/n_null. Thus adding question nulls does **not**
double aggregate null weight or change its .5 share. It redistributes that share among ordinary-text, locality,
outside-own and outside-question examples.

| Seed-0 repaired rehearsal | Mean record queries | Mean null queries, including 8 text | Mean question nulls | Mean weight per null query | Mean L2 mass on question nulls |
| --- | ---: | ---: | ---: | ---: | ---: |
| Disabled | 16.420 | 24.210 | 0 | .020658 | 0 |
| p=1 | 16.430 | 32.215 | 8 | .015523 | .124186 |
| p=.35 | 16.410 | 26.995 | 2.792 | .018571 | .050619 |

The total record/null masses remain .5/.5 in all these episodes. Dilution of the existing null subclasses
can contribute to a tradeoff without any change to the top-level loss weights.

Two caveats affect interpretation:
- The CLI accepts any float for `--out-para-prob`, and the builder does not enforce a finite [0,1] probability.
  Negative/NaN values silently add none; values above 1 add all. Validate before GPU/base initialization and also
  at the public builder boundary.
- Enabling the flag consumes RNG draws, even at p=0 for eligible outside items. It therefore changes subsequent
  episode trajectories. Same seed across variants does not establish a paired training experiment.
  Within-run checkpoint selection still minimizes held-out episode retrieval loss. The six held-out episodes
  are constructed **without** the R1-66 flags, so they do not test the newly added question-null subclass.

**Requested owner edits ER-02/ER-03:** add probability validation/refusal tests and record flag, probability,
null-subclass counts and loss balancing in each training summary. Declare whether held-out checkpoint selection
intentionally excludes question nulls. Any change to the held-out objective or RNG streams needs a new run identity;
do not rewrite existing result provenance. A separate diagnostics RNG would enable paired episode comparison,
but is a future experiment change rather than an interpretation of the existing runs.

### X11-03 — the reported seed-0 tradeoff is correctly denominated

| Reader | Immediate ES zs/CF/MQ | RET-ES zs/CF/MQ | RET-GS zs/CF/MQ | LS zs/CF/MQ | zsRE unseen false fires |
| --- | --- | --- | --- | --- | ---: |
| tri4 seed 0 | 1 / 1 / 1 | 1 / 1 / 1 | .98 / .86 / .79 | 1 / 1 / .98 | 30/100 |
| tri4 seed 2 | 1 / 1 / 1 | 1 / 1 / 1 | .98 / .86 / .79 | 1 / .98 / 1 | 52/100 |
| tri5 seed 0, p=1 | 1 / 1 / .99 | 1 / 1 / .99 | .91 / .81 / .55 | 1 / .98 / 1 | 5/100 |

Each stream has 100 edits and 100 checkpoint retention rows; all nine RET-ES and RET-GS summaries match
recalculation from those rows. The final GS statistic is **retention**, not immediate paraphrase success.
The LS denominator is **50**, so .98 is 49/50; individual locality generation traces are not retained in these
checkpoint files, and the review verifies aggregate agreement rather than reconstructing those 50 decodes.

The three unseen assays have identical ordered edit IDs, identical outside IDs, the same source SHA and
`outside_source=dev_remainder`. Each has 100 records, 100 planned/scored outside queries, 100 observed firing
decisions and 100 terminated reference/cap pairs. Row-level false fires and changed answers are 30/52/5.
Those two outcomes happen to agree here; they are different definitions and should stay separately reported.
Firing is post-hard-gate acceptance, not proof of a nonzero write.

For seed 0, **30% → 5% is −25 percentage points**, alongside zsRE GS .98 → .91 (−7 points),
CF .86 → .81 (−5 points), MQ .79 → .55 (−24 points), and mean GS .876667 → .756667 (−12 points).
The favorable unseen rate does not erase the retention loss or prove robustness to another reader seed.
Do not describe 30→5 as a result across all tri4 seeds.

### X11-04 — final selection needs a common population and a complete candidate receipt

The new protocol's required rule is one configuration for three datasets, maximizing equal-dataset mean RET-GS,
subject to zsRE unseen firing ≤10% at 100 actual records and LS ≥.98. Under the conservative per-dataset LS
interpretation, all three completed recent candidates pass LS, both tri4 readers fail firing, and tri5 passes
the numerical firing condition. This is **not a final-primary selection**.

Historical v4 (tri2) MQ streams share only **47/100 item IDs** with the tri4/tri5 MQ stream. The unrelated
inventory also changed to development v3b. Therefore the older .79 v4 value is not a paired baseline for choosing
between readers. Re-evaluate remaining candidates against one ordered development receipt; preserve the existing
historical results separately.

A 100-record training-pool outside population cannot stand in for development remainder, and a 1,000-record
point cannot stand in for 100. An unseen pair must be outside the full attempted history, including failed edits.
The recent tri4/tri5 unseen populations are paired within their assay, but candidate selection must bind both the
retention stream and outside assay edit inventories rather than assume they are the same merely from the seed.

**Requested owner edit ER-04:** issue a new selection receipt containing candidate roster/cutoff, exact weights and
configuration hashes, ordered selected IDs and manifest SHA for each dataset, fixed unrelated and outside IDs,
actual occupancy, complete denominators, seed aggregation/tie rule and outcome. Explicitly bind whether LS ≥.98
is per dataset (recommended) and which LS statistic is used. Select before any draw.
Tri4 seed 1 and tri6 are incomplete in the review snapshot; do not treat a metrics log, failed evaluation, or
missing summary as a pass. R1-67 supplies the loader receipt and final-gate trace helpers; owner wiring remains.

### X11-05 — driver timings have two scopes; component speedup remains unmeasured

The clean profile completed at 300 edits. Its 610 phase JSON files contain **976.310 s** of recorded phase wall:
edit 177.147, immediate 153.506, drift 508.487, remaining endpoints 137.170 s.
The code starts this timer **after** input verification, initial full state hashing and cloning. The owner's
1,252 s total and approximately 1 s per edit/immediate include a wider boundary. Raw edit/phase timers are
.5905/.5117 s, so the two tables cannot be compared without their timing scopes.

**Requested owner edit ER-05:** label these boundaries explicitly in the notes and future profiling receipt.
Instrument input/code checks, immutable parameter checks, state export/hash, clone/restore, model work, JSON
serialization/fsync and complete process elapsed separately. Do not infer a measured speedup by subtracting model
time from unmatched timer scopes. Zero-case challenge overhead cannot price an actual 100-case endpoint.

R1-68's new components retain full input/parameter verification in the integration contract. Caching a base
checksum solely by object identity, or a file checksum solely by mtime, would weaken the existing refusal guarantee.
An incremental record-root is a **new** hash scheme, not the legacy snapshot SHA, and `lexical_version` alone is
insufficient because code/delta changes do not advance it. Checkpoint full recomputation and mutation inventory
tests are required before enabling it. See [R1-68](../docs/tasks/R1-68.md) for implemented components and remaining
integration gates. No real-base incremental speedup is claimed.

## Handoff and scope

R1-D1h and protocol v4 address the population decision without declaring clearance complete. R1-67 creates the
strict development loader and trace renderer; its new modules were installed after the clean profile completed.
R1-X11's requested owner changes are collected in [the edit request](../docs/tasks/R1-X11-edit-request.md).
The current lane does not change the owner training loop, result files, task board, notes or selection.
