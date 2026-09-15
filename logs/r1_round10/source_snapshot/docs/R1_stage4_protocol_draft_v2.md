# Revision v1 — Stage 4 protocol draft v2 (R1-59)

**Draft for owner implementation and lead freeze; no draw, seal or launch authorization.** Codex, 2026-09-14.
This revision incorporates DEC-043 (primary gate accepted), DEC-044 (retain full scope) and DEC-045
(add MQuAKE-CF while retaining CounterFact). The current design is **360 cells**, not the former 240.
No reduction is proposed. The 15-hour confirmation envelope and the earlier 48-cell proposal are superseded.

The [decision update snapshot](../logs/r1_round9/source_update_dec045/index.json) records the task-list change
during round 9. Numerical support is in the [100-source recount](../logs/r1_round9/x8_evidence.json),
[protocol arithmetic and resource audit](../logs/r1_round9/protocol_reconciliation.json), and
[counter-review](../logs/review_r1_56.md). The earlier [protocol draft](R1_stage4_protocol_draft.md) remains
historical; its older reference, dataset count, budget and unresolved gate-choice statements are superseded here.
The machine matrix `run_matrix_draft_v3.json` still has 240 cells and older reference bindings: it needs an owner
version update before admission. This document does not rewrite it.

## 1. Scientific question and scope

Can a small editing memory retain requested facts, answer their paraphrases, reject unrelated requests, and
preserve ordinary language modeling while the base and reusable cap weights stay fixed? Only declared,
support-driven episodic state changes during a stream.

The adopted matrix evaluates the current feedforward editing package and stronger controls. It still does not
complete all plan-9 comparisons: episodically trained bases, alternating BP versus ePC on matched episodes,
feedforward versus settled inference, and the retrained-cap 2×2 require their own implemented and admitted branches.
Retaining every existing matrix condition does not make these missing comparisons completed. U01 records the
remaining scientific scope decision; no missing branch is scored as a negative result.

The learned/random contrast compares deployed packages, including different lexical/null/gating settings.
It cannot isolate learning alone. A gate-on versus gate-off comparison does isolate the deployment gate when
weights, edit history, queries and all other settings are paired.

## 2. Conditions, checkpoints and independent units

Use **8 conditions × 3 datasets × 3 fresh realizations × 5 update orders = 360 cells**.
Datasets are zsRE, CounterFact and MQuAKE-CF. Each condition/dataset has 15 cells; each dataset has 120.
Retain checkpoints after attempted edits **100, 300 and 1,000**. Actual occupancy and attempted-edit count are
separate fields. Three reader training seeds in development are not three independent fresh-data realizations.

| Condition | Frozen-base substrate and distinguishing behavior |
| --- | --- |
| R1_learned_ff | Primary v3: original base, text-null learned reader, gate minimum 1 distinct rare token, active-record document frequency maximum 2 |
| R1_nonlearned | Original base, random tied reader; lexical off, pairwise null off, cosine floor .93, null 1.01 |
| matched_update | Original base, MatchedUpdateCap C1; five normalized adjoint steps, learning rate .1 |
| v0_live_C1 | Original base, live C1 observations and declared v0 search/sites |
| v0_live_C2 | Original base, live C2 with declared site-selection probes |
| v0_stable | Original base, StableCap C1 under DEC-035 |
| S1_literal | Literal-continued base plus StableCap C1; cap not retrained |
| S1_LM | Fidelity-admitted LM-continued base plus StableCap C1; cap not retrained |

Primary v3 uses the weights in [primary_condition_v3.json](../manifests/revision_v1/primary_condition_v3.json).
Seed-0 reader file SHA-256 is `c5777b5bf0df754766463737f53f641f624de8bc98ac0420fd99bec8850730db`.
Its learned settings include stable observations, tied cosine, lexical overlap, pairwise/query null, hard top-1,
top-k 4, binary mass, null threshold .5, no cosine floor, five delta steps at learning rate .1 and zero fast-code
steps. Preserve calibration A=.3 and the exact registered bank scales unless a separately declared variant
is calibrated. Freeze constructor defaults, stop-token identity, encoder/tap versions, answer masks,
per-position delta semantics, byte accounting and serialization behavior.

**v2 is the no-gate comparison**, using those same learned weights and settings with the rare-token gate disabled.
It is not one of the other seven rows above. All-eight retention therefore leaves an allocation decision:
a complete paired v2 axis would add 45 cells, making 405. Keep the accepted 360 intact; obtain a specific
additional comparison allocation, or explicitly label v2 as development-only. Do not silently replace a retained
control with v2. Direct primary-minus-stable and primary-minus-matched contrasts reuse existing cells and
require no extra executions.

The historical data seeds are 0/1/2 and order seeds 100–104; model seed 0 is a separate proposed fixed axis.
Final seed/identity receipt remains U06/U12. An additional model-seed axis must be priced explicitly.
The primary checkpoint may need a new identity if the lead chooses MQuAKE training instead of transfer evaluation.

S1_literal passed its development fidelity screen but is a numerical negative control, not an exactly unchanged
tensor checkpoint. The executed S1_LM failed KL (.0949791 versus .001). A valid replacement and matched training
budget are necessary while that condition remains in scope. It cannot become an admitted negative control by
labeling its rerun optional. See [R1-X7](../logs/review_r1_24.md).

## 3. What the development evidence establishes

All stream values below are independently recounted from 100-item rows, checkpoint rows and summaries.
The three columns are reader seeds 0/1/2 on development data, without an independent-data confidence interval.

| Dataset and condition | RET-GS, seeds 0 / 1 / 2 | ES / RET-ES / bounded LS |
| --- | --- | --- |
| zsRE, v2 | .96 / .98 / .96 | 1 / 1 / 1 |
| zsRE, v3 | .96 / .98 / .96 | 1 / 1 / 1 |
| CounterFact, v2 | .725 / .85 / .79 | 1 / 1 / 1 |
| CounterFact, v3 | .715 / .85 / .79 | 1 / 1 / 1 |
| MQuAKE | unavailable | no model execution yet |

The v3-minus-v2 seed-0 dry run gives ΔRET-GS 0 for zsRE and −.01 for CounterFact.
No scientific verdict follows from one independent development realization. The new analysis adapter reports
these cells as unadmitted development evidence.

Outside queries have denominator 100 for each row:

| Dataset / occupancy / outside source | v2 false fires | v3 false fires | Pairing qualification |
| --- | ---: | ---: | --- |
| zsRE / 100 / development remainder | 7 | 5 | identical ordered edits and outside queries |
| zsRE / 100 / training-pool remainder | 12 | unavailable | separate development population |
| zsRE / 300 / training-pool remainder | 25 | 11 | identical ordered edits and outside queries within this row |
| zsRE / 1,000 / training-pool remainder | 45 | 10 | identical ordered edits and outside queries within this row |
| CounterFact / 100 / development remainder | 0 | unavailable | 67 complete pairs, 33 truncated pairs |
| CounterFact / 100 / training-pool remainder | 0 | unavailable | 65 complete pairs |
| CounterFact / 300 / training-pool remainder | 2 | unavailable | 71 complete pairs |
| CounterFact / 1,000 / training-pool remainder | 5 | 0 | identical ordered edits and outside queries; 70 complete pairs |

The zsRE v3 1,000-record outside result is 10/10/11 fires for reader seeds 0/1/2.
Within-size gate comparisons are paired and support a reduction on these examples. **Cross-size curves are
not fully paired:** pool outside IDs overlap by only 80/100 for zsRE and 62/100 for CounterFact between 100 and
300 edits, and by 0/100 between 300 and 1,000. The developmental 7→25→45 series changes source as well.
No pure memory-size causal effect or final unseen rejection rate is established by that sequence.
Final evaluation must reuse a disjoint fixed outside inventory across checkpoints.

The v2 CounterFact-edit ordinary-text recount has ΔNLL **+.01240744473 nats/token**, PPL ratio 1.0124847364,
and 14/4,064 scored-position fires despite 0/96 sampled-prefix fires. This exceeds the provisional .01 loss
ceiling on that assay. zsRE v2 is approximately −.00000117634 nats. These are **ungated v2** results:
the current drift driver has no rare-gate configuration. v3 ordinary-text preservation remains unmeasured.

The near-miss and explicit revision development runs report 100/100 each for v2 and v3. They use independent
case clones from empty memory, not the final 1,000-edit stream. Historical composition remains unreachable
in that driver. MQuAKE supplies direct source questions, but their existence is not a completed composition result.

## 4. Fresh populations, exclusions and MQuAKE preparation

The accepted v3 register wrapper SHA-256 is
`d3549f43327ec80f497cfd71df82494c7c0bded02c8e6f5c2c333800b2489805`.
It binds historical policy and child resources, not fresh sampling authorization.
Use NFKC, casefold and collapsed whitespace, plus only explicitly verified canonical alias mappings.
Track exposure after that register, including text training and any MQuAKE pool; publish the next version before
a three-dataset draw.

zsRE has **52,498** prior-clear representatives through the v3 overlay, not the historical 58,498.
Final contextual/alias clearance and teacher E.2 yield remain unknown. CounterFact has **0 strict** candidates,
or **12,246** under the reason-specific old-pool exception. Keeping CounterFact in DEC-045 makes the exception
necessary with current local resources; the queue still requests its explicit confirmation under DEC-042.
It never waives another exclusion reason.

R1-D4 prepared [mquake_items_v1.json](../manifests/revision_v1/mquake_items_v1.json) and source resources under
`assets/data/prepared/revision_v1/r1_d4_v1/`. The source hash is
`fbf1ab9e5243e52da429f7636990096ae0b5f8fbf60f1d4d3a4bf0c9214cd6ea`.

| MQuAKE preparation quantity | Count / meaning |
| --- | --- |
| Source cases / rewrite occurrences | 9,218 / 16,835 |
| Unique normalized subject/relation rewrites | 7,236 |
| Excluded subjects / excluded unique rewrites | 924 / 1,193 |
| Remaining rewrites / subjects / relations | 6,043 / 5,577 / 37 |
| Conflicting later new-target occurrences | 19; first case wins; incompatible composition cases retained as unavailable |
| Token-length failures | 0; answers including newline span 2–16 tokens |
| Per-item locality / near-miss candidates | 2 + 2 other same-relation subjects for every item |
| Direct composition questions | 27,654 across 9,218 source cases |
| Cases with every retained rewrite dependency available | 4,981 |
| Cases with available dependencies and no exact excluded path-subject hit | 2,391; still not teacher/context certified |
| Items with no composition question whose full dependency set remains available | 1,649 |
| Subject overlap with zsRE v3 candidates | 159 |

Locality answers use the neighbour's source `target_true`; these are not teacher-generated preservation references.
Locality and near-miss lists are disjoint **within an item's proposal**. They are not a globally sealed split:
neighbours can appear elsewhere as candidate edits. Final allocation must reject edited/held-out/alias/context
overlap and construct fresh role-specific neighbourhoods.

Composition preserves all three source questions, answers/aliases, original/new triples, source case hashes
and dependency IDs. `verified_source: MQuAKE` means source provenance. It does not certify that a selected
stream has installed all required rewrites, that other edits cannot affect a path, or that the teacher accepts
the original fact. Conflicts, excluded dependencies and exposure hits stay explicit. Count and stratify the
number of required edits/hops rather than relabeling every case a two-fact test.

The lead still chooses **transfer evaluation versus a new MQuAKE training pool/retrained reader**.
The queue's proposed 1,000-item pool has not been drawn. Under a conservative first-source, one-primary-subject
capacity policy, MQuAKE has 5,418 subjects after zsRE overlap. A 1,000-subject training reservation would leave
4,418, only **368 above** the 4,050-subject confirmation-role proposal below. Teacher/context failures and
composition dependency closure may exhaust that surplus. Resolve yield and training scope before sampling;
do not silently reduce realizations, reuse training subjects or substitute outcomes.

## 5. Draw, split, seal and checkpoint recipe

R1-58's [recipe](../scripts/r1_58_draw_streams.py) and
[three-dataset count-only adapter](../scripts/r1_58_three_dataset_dry_run.py) perform no actual draw in this round.
Both source readings have reports under [round-9 logs](../logs/r1_round9/).

Per realization, the proposed disjoint fact reserves are 1,000 edits, 100 outside prompts, 100 near-miss
supports, 100 near-miss neighbours and 50 explicit-revision facts: **1,350**, or **4,050 per dataset**.
A revision fact supports old/new versions of the same entity; it is not two independent sampled subjects.
Composition support closures and final global locality exclusions may require additional reservations.

Proposed stratification is proportional answer-token length (terminal included): 1–2, 3–4, 5–8, 9+.
Largest-remainder quotas use lexical tie-breaking; allocation order is realization 0–2, then the roles above.
No replacement is allowed. The future pure allocator sorts canonical subject/item identities and uses
separate PCG64 streams, seeded from the first 16 bytes of SHA-256 of
`R1-58:<seed>:<dataset>:<stratum>`. Default seed 158 is a proposal, unused in dry runs.
Freeze NumPy/version, source order, seed derivation, strata and training reservation first. Composition may
require additional dependency-aware sampling rules; do not choose them from final performance.

Dry reports emit quotas/counts only, with RNG unused, no candidate IDs and no payload/manifest/seal writes.
Strict CounterFact reports a 4,050 shortfall; exception has pre-eligibility capacity. Three-dataset reports
count 52,498 / 12,246 / 5,418 under the exception. These are candidate capacities, not accepted sample sizes.

Any future selection aborts globally on insufficient admitted capacity before RNG or partial writes.
The two-dataset future CLI requires a lead flag and independent hash-bound approval, source, eligibility,
context, exposure and recipe receipts. Its optional seal concerns fact reservations only.
The additive three-dataset CLI deliberately has no execution/seal interface; final integration must bind the
new register, MQuAKE inventory, training decision and eligible records. Never invoke the old two-dataset
writer as if it implemented the accepted 360-cell freeze.

Serial admission checkpoints:

1. Record source and training/transfer decisions; reserve training exposure without consuming confirmation subjects.
2. Complete teacher E.2 and canonical/context review; measure final yield and joint dependency capacity.
3. Freeze independent expected populations and RNG rules; lead draws all roles once.
4. Construct and validate locality, revision and composition cases; verify ordered token/schema round trips.
5. Write immutable assets payloads and hash manifests; verify confirm loaders and refusal paths.
6. Lead freezes protocol, code, identities, costs and execution inventory together; only then admit jobs.

## 6. Endpoints and analysis contract

At checkpoints 100/300/1,000 retain unconditional immediate ES, RET-ES and item-averaged RET-GS, including
failed behavioral acquisitions. Retain all predeclared paraphrases per item. Report actual occupancy, all retained
records, logical bytes, peak device/RSS, retrieval/firing by role and complete generated outcomes. A missed target
occupancy is an unavailable exact-size result, not a relabeled smaller sample.

Use a fixed outside inventory of 100 per realization, paired over conditions/orders/checkpoints and absent from
the entire attempted edit history, including failed, evicted and superseded edits. Record true hard-gate firing,
bounded answer changes and complete-answer preservation separately. Unknown firing/history is unavailable.

Freeze the main LS convention explicitly. Existing LS compares normalized bounded generated text; it does not
require both answers to terminate. Publish strict complete-pair counts and truncation alongside it. A stricter
primary LS requires an endpoint version before the freeze. Continued-base locality references the original base;
incremental cap drift additionally references its own continued cap-off base.

Near-miss and revision tests run on isolated clones with before/after identity checks and full planned denominators.
Near-miss preservation must not condition on own-answer success. Explicit revision reports old acquisition, latest
answer, old-alias reappearance and active/inactive version state separately. Final counts/cadence and MQuAKE direct
composition allocation remain U09; a source case is not a performed result.

Ordinary text selects anew at every prefix. With K complete 128-token windows, there are **127K scored positions**:
4,064 for K=32 and 16,256 for K=128. The 3K probe denominator is separate.
Report mean ΔNLL in nats, exp(ΔNLL), per-position firing and source/window identities.
The 128-window assay is not the full validation split required by plan 9. Freeze full-split/window/tail policy
and cost; include continued-versus-original and cap-on-versus-own-base comparisons.

[R1-57 analysis](../src/pccap/revision_v1/analysis.py) accepts independently supplied dataset/condition/realization/order
axes, ordered item IDs, paraphrase counts, checkpoints, locality IDs and endpoint case inventories. It validates
observed rows against these expectations. Absent cells/items/required endpoints remain in expected denominators;
fully unavailable metrics are null, with scored-only means explicitly diagnostic. Failed behavioral acquisition
is scored, not dropped. A resource acquisition failure is unavailable.

For each metric/contrast, average paired item differences per realization/order; keep all orders together within
a realization. Bootstrap the three realization means with replacement, NumPy float64, seed 0, 10,000 draws,
proposed .975 confidence and linear percentile bounds .0125/.9875. Report all order differences and cluster means.
With only three independent realizations intervals remain preliminary. Overlapping development draws or repeated
reader seeds must not be treated as independent clusters; one realization yields no interval.

Proposed classifier, treatment minus control, after complete inventory and fidelity admission:

- **Positive:** ΔRET-GS ≥ .05, GS lower bound > 0, ES lower bound > −.02, LS lower bound > −.01.
- **Negative:** GS upper bound < .05, or ES upper bound < −.02, or LS upper bound < −.01.
- **Qualified:** not negative; ΔRET-GS ≥ .05 with lower bound > 0, ES point ≥ −.02 and LS point ≥ −.01,
  while required noninferiority lower-bound tests remain unresolved.
- **Inconclusive:** complete/admitted evidence meeting none of those rules.
- Missingness, failed admission and insufficient independent clusters have separate statuses before classification.

Exact boundary rules and applicability remain lead-owned U13. The adapter tests the revision .05 margin against
the incompatible v0 .02 wrapper. Bootstrap confidence is not multiplicity control. U12 must freeze primary
contrasts, datasets, endpoint family and any conjunctive claim. Report secondary contrasts descriptively until
specified. No accepted numeric threshold makes 10% unseen firing a pass.

The adapter's CLI requires `--dry-run` and cannot admit confirmation. Legacy development LS lacks saved query IDs;
only a labeled aggregate recount is possible. Final LS identity, full endpoint rows, analysis admission and
multiplicity wiring remain necessary before freeze.

## 7. Measured costs and full-scope pricing

The following are **ungated v2** development P1 observations, not exact v3/all-comparator profiles:

| Dataset | Bytes at 100 / 300 / 1,000 | Fraction of 64 MiB at 1,000 | Query p50 at 100 / 300 / 1,000 | Whole P1 wall |
| --- | --- | ---: | --- | ---: |
| zsRE | 17,264,392 / 24,565,172 / 49,941,992 | .744 | 12.52 / 10.32 / 14.37 ms | 139.669 s |
| CounterFact | 15,456,840 / 19,584,816 / 34,032,624 | .507 | 10.04 / 10.44 / 14.55 ms | 90.413 s |
| MQuAKE | unmeasured | unavailable | unavailable | unavailable |

The 1,000 recorded edit calls sum to 131.731 s / 79.020 s for zsRE / CounterFact; warm medians are .1109 / .0727 s.
Round-trip hash/byte checks pass at each occupancy. These measurements establish capacity for those development
histories, not a final 1,000-edit retention result, a universal answer-length bound or cache-equivalent restore.
The persistent rarity cache is not represented in that logical-state counter.

Registered random settings differ from both `nonlearned` and `nonlearned_v2` P1 runs. Stable/live/matched/S1
conditions and all MQuAKE conditions lack exact full-workload measurements here. Gate rebuild cost is also absent
from v2 P1. Consequently **no condition/dataset full-cell ceiling can yet be filled from an exact profile**.

Component accounting for each condition c and dataset d must use:

`W[c,d] = initialization/compilation + 1,000 edits + sum(checkpoint retention + LS + outside-query-only + drift-on + applicable challenge work + clone/restore) + final serialization`.

The observed reference components are query medians 10–15 ms, reported retention ≈20 ms/query (≈60 s for a
3,000-query CounterFact endpoint), LS 50 pairs ≈2 s, outside query-only ≈5 s, and the reported 128-window
drift-on assay ≈165 s/checkpoint. R1-43's **151 s covers 200 independent development challenge cases**,
not an exact 100-near/50-revision final checkpoint at high occupancy. R1-44 complete jobs range roughly
72–200 s and include setup/edit replay: never add their full wall times to an in-stream edit charge as
if they were query-only. MQuAKE composition and full-validation drift remain unpriced.

Use each measured phase once. Shared cap-off drift may be reused only for an identical base, tokenizer,
window/position inventory and reference policy. Continued bases need their own references. Different memory
states require cap-on work. Reader/continuation training, feature construction and actual failed training jobs
are charged **once per unique executed job**, not once per analysis contrast or each of its 15 paired cells.

The lead's ≈1,150 s learned-cell estimate gives the following transparent full-matrix **planning scenario**.
Each dataset entry is 15 cells × 1,150 s × 1.20 / 3,600 = 5.75 h; the JSON receipt expands all 24 rows.

| Retained condition | zsRE cells / scenario h | CounterFact cells / scenario h | MQuAKE cells / scenario h | Total cells / scenario h |
| --- | ---: | ---: | ---: | ---: |
| R1_learned_ff | 15 / 5.75 | 15 / 5.75 | 15 / 5.75 | 45 / 17.25 |
| R1_nonlearned | 15 / 5.75 | 15 / 5.75 | 15 / 5.75 | 45 / 17.25 |
| matched_update | 15 / 5.75 | 15 / 5.75 | 15 / 5.75 | 45 / 17.25 |
| v0_live_C1 | 15 / 5.75 | 15 / 5.75 | 15 / 5.75 | 45 / 17.25 |
| v0_live_C2 | 15 / 5.75 | 15 / 5.75 | 15 / 5.75 | 45 / 17.25 |
| v0_stable | 15 / 5.75 | 15 / 5.75 | 15 / 5.75 | 45 / 17.25 |
| S1_literal | 15 / 5.75 | 15 / 5.75 | 15 / 5.75 | 45 / 17.25 |
| S1_LM | 15 / 5.75 | 15 / 5.75 | 15 / 5.75 | 45 / 17.25 |
| **All retained** | **120 / 46** | **120 / 46** | **120 / 46** | **360 / 138** |

This is **115 h nominal + 23 h failure reserve**, excluding separately charged shared training and unresolved work.
It extrapolates learned-cell timing to unprofiled conditions/datasets; it is neither an approved ceiling nor a
measured lower/upper bound. The accepted scope must be profiled at its exact settings. Slower controls, long
answers, full-validation work and composition can increase it. The old 92 h estimate covered only two datasets.
A full additional v2 comparison would add 17.25 scenario hours, totaling 405 cells / 155.25 h before those extras.

Historical training reconciliation is also incomplete: text-null seed 0 records 820,783 forward-token charge
including text-bank work; adding the separately itemized 313,579 factual-bank positions gives candidate
1,134,362, versus R1-24's 771,581 matching basis. Do not double-count the text bank or claim those controls match
the new reference's total compute. Record forward, reverse, padded/JIT work and actual wall/device time separately.
MQuAKE retraining would require new measured shared costs and reference/control identities.

DEC-044 supersedes the 15-hour envelope; it does not waive profiled per-job ceilings, failure reserves,
checkpointed stops or GPU lease rules. Keep all ceiling fields null and launch disabled until measured and accepted.

## 8. U01–U18 status after this round

“Partial” means a concrete artifact exists, with the listed admission work still open. No owner/lead gate is closed
by this draft.

| Gate | Current status and next checkpoint |
| --- | --- |
| U01 scientific comparisons | Open: retain all eight controls and three datasets; specify plan-9 deferred branches and primary stronger-control claims |
| U02 reference | Gate choice accepted (DEC-043), three development seeds recounted; cache repair, exact v3 drift/profile and MQuAKE training/transfer identity remain |
| U03 continuation | Open: literal qualified; executed LM fails fidelity; obtain admitted LM checkpoint and refreshed budget |
| U04 zsRE freshness | Partial: 52,498 bound candidates; post-register exposure, aliases/context and teacher yield pending |
| U05 CounterFact source | Open receipt: strict zero; retained dataset needs explicit reason-specific exception under DEC-042 |
| U06 draw/RNG/splits | Partial: tested count-only recipe and all-three counts; lead approves strata, source precedence, training reservation, seeds and joint capacity |
| U07 payload/seal | Open: MQuAKE source schema prepared, no final payloads/seals; construct challenges and validate final three-dataset loaders |
| U08 endpoint cadence | 100/300/1,000 retained by scope decision; full-validation windows/tail/reference and detailed challenge cadence still need binding |
| U09 challenge semantics | Partial: MQuAKE direct source questions/dependencies now available; final compatible composition and near/revision reservation/cadence not admitted |
| U10 LS convention | Open: freeze bounded-versus-termination-qualified primary and all decode settings |
| U11 implementation | Open: rarity-cache defects reproduced; exact comparator observers, final challenge loader and replay/cache identity checks needed |
| U12 contrasts/multiplicity | Open: freeze family across three datasets, strong controls, v2 allocation and conjunctive claims |
| U13 classifier/fidelity | Partial: .05/−.02/−.01 CPU adapter tested; lead freezes inequalities/applicability and fidelity/drift admission |
| U14 secondary thresholds | Open: no accepted numerical pass rule for unseen, composition, revision or size |
| U15 analysis adapter | CPU implementation/dry run complete; final independent LS/case identities and confirm-mode admission remain |
| U16 budget | Full scope accepted, old envelope superseded; v2 P1 measured only; exact all-condition/all-dataset profiles, shared costs and ceilings remain open |
| U17 execution controls | Open: final matrix/code hashes, queue RNG, bounded retry/resume and failure accounting |
| U18 schedule | Open: charged-spend ledger/calendar anchor and measured 360-cell critical-path forecast needed |

The CPU suite's installed-state result is 318 passed, 8 skipped, 2 existing maintenance failures. Both candidate
test fixes pass an in-memory reproduction and are supplied as an unapplied patch; status follow-up, if authorized,
will be recorded separately. Passing new tests is not a substitute for resolving the full-suite admission gate.

## 9. Freeze contents, timeline and concurrent work

The lead's final manifest must bind the accepted protocol/decisions, 360-cell matrix and contrast IDs;
all executable code/environment/hardware/determinism settings; original/continued base and reader weights;
calibration, tokenizer, masks, stop/null/rarity rules; exclusion wrapper and subsequent exposure; eligible ordered
realization/order/role payloads and challenge dependency schemas; training/validation separation and caches;
endpoint denominators, reference bases and full-validation windows; byte/eviction/restore accounting;
per-job/total ceilings, shared-cost ownership and retry/overshoot rules; independent analysis inventory,
bootstrap/margins/multiplicity; and the lead approval identity. A register-only freeze or a content-sealed
fact reservation is insufficient. Admission compares hashes before work and refuses mismatch.

At the homogeneous scenario, 138 h is **5.75 uninterrupted accelerator-days** before unpriced/shared work,
other users' GPU time, failures beyond reserve and serial preparation. It is not an elapsed-calendar completion
promise. Plan 9's relative Stage 2 days 8–18 and Stage 4 days 20–28 need a refreshed start/spend/critical-path
ledger. Do not report schedule compliance from calendar date alone.

Useful concurrent lanes, with separate files/ownership:

- CPU: finish canonical/context and composition dependency review; quantify MQuAKE yield after proposed training
  and cross-dataset exclusions. No teacher/model evaluation is performed in this lane.
- CPU: integrate exact comparator endpoint observers and independent expected inventories; test missingness,
  replay equivalence, final loader and source-change refusals.
- Owner repair: apply/test the cache invalidation fix and complete logical/cache memory accounting; update metadata
  writers and report qualifications before freeze.
- GPU owner: teacher eligibility, final-reference training if selected, v3 drift/high-occupancy checks, and exact
  P1–P4 profiles for all retained conditions and MQuAKE under leases.
- Lead: source/training/analysis decisions, measured budget acceptance, draw/seal/freeze and then launch.

Parallel preparation ends at the shared admission checkpoints. Final sampling depends on source/eligibility;
sealing depends on complete compatible payloads; freeze depends on counter-review, implementation and budget;
confirmation depends on successful identity admission. None is authorized solely by this draft.
