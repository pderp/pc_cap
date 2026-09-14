# Revision v1 — Stage 4 protocol draft (R1-49)

**Draft for owner revision and lead approval; not a freeze or launch authorization.** Prepared by Codex, 2026-09-14,
from plan 9, DEC-033/034/035/037/039/040/041, matrix v3 and the endpoint implementations. The lead alone writes
`manifests/frozen_revision_v1.json` after Stage 2 counter-review. All choices marked **OPEN** below must be resolved,
or explicitly removed from the confirmatory scope with a recorded reason, before that act.

The [source index](../logs/r1_round8/source_evidence.json) preserves the exact working-tree inputs at
`d2f2e77a62b8c4858b128cf0689078a6a3934ebd`; it includes concurrent owner development results. The
[placeholder inventory](../logs/r1_round8/protocol_placeholder_inventory.json) enumerates every matrix-v3 null field,
distinguishes intentional nulls and records additional scientific omissions. This document does not convert old
development or previously opened v0 examples into fresh evidence.

## 1. Scientific question and limits of this matrix

The practical question is whether a small, bounded editing memory can retain requested factual changes, generalize
them to paraphrases, reject unrelated queries and preserve ordinary language modeling. The base model and reusable
cap weights remain frozen during each evaluation stream; only declared support-driven episodic state may change.

Plan 9 requests four comparisons: (i) current cap versus stronger base with fast-rule/budget fixed; (ii) current versus
episodically trained base with cap/budget fixed; (iii) alternating BP versus alternating ePC on matched episodes, masks
and schedules; (iv) feedforward versus settled inference within the same cap family, base and memory. It also calls for
the retrained-cap 2×2 comparison. **Matrix v3 covers the working feedforward package and teacher-only continuation
controls; it does not fulfill all four comparisons or the retrained-cap 2×2.** Episodic BP/ePC, fixed-unroll reference,
settled/recurrent/parameter-matched controls, continued-base retrained readers and matched-total-memory variants remain
conditional/deferred. Their absence is unavailable evidence, not a failed scientific test. External learned-memory
baselines remain outside this cycle under DEC-033.

Before freeze the lead must accept this narrower scope or add implemented, audited and profiled branches (U01).
Stage 3 remains conditional on a working Stage 1–2 cap. The current learned-vs-random comparison changes lexical
features, null architecture and gating as well as training; its claim is about the deployed package, not the isolated
effect of learning.

## 2. Conditions and identities

Source identities:

| Object | SHA-256 |
| --- | --- |
| `run_matrix_draft_v3.json` | `43618eabfb147d31e41229bb82b09b7f0387cb4d52e9901dec7ac462158b520c` |
| `primary_condition_v1.json` | `51560c17947b49c15529c9bd82949d941dfdc8678b2193350304d328368bf83c` |
| original GPT-2 weights | `248dfc3911869ec493c76e65bf2fcf7f615828b0254c12b473182f0f81d3a707` |
| seed-0 mixed learned reader file | `9f676076ad94df2fb6a3257c5838edb9e365f7ddc808efd2d044ef6e01f626fd` |
| seed-0 random tied reader file | `a0e50ef72af48963062f8acabcf02ca66171d5d87f12cebf7074978a38a8317c` |
| stop list v1 | `90b6cd9f118aae8d13742e54601e25fe12fb28ef7a4c7abed171bc446687d711` |
| inherited v2 calibration | `84126123f48c83e9270d6995335e86562e733efab7926ffa3178daadc5305a1f` |
| accepted-register wrapper | `d3549f43327ec80f497cfd71df82494c7c0bded02c8e6f5c2c333800b2489805` |

Paths and child identities are in the bound manifests. The calibration contributes A=.3,
b₁=70.70187377929688, b₂=106.5766658782959, b₃=425.5740661621094. Preserve it unless a separately declared variant
is calibrated during development. Cap settings include τ_edit=.1; decoding is greedy, bounded at 32 new tokens with
the declared newline/EOS stopping and answer normalization. Freeze exact token IDs, not a prose approximation.

| Matrix condition | Base and cap | Declared distinguishing settings |
| --- | --- | --- |
| R1_learned_ff (R0) | original + learned RevisionCap | stable observations; tied cosine; lexical + pairwise/query null; hard top-1; top-k 4; null .5; no cosine floor; binary mass; five delta steps, lr .1 |
| R1_nonlearned | original + random tied RevisionCap | lexical off, pairwise null off, cosine floor .93, null 1.01; five delta steps, lr .1; hard top-1/binary mass |
| matched_update | original + MatchedUpdateCap C1 | five normalized adjoint steps, lr .1; historical three-step results cannot be relabeled |
| v0_live_C1 | original + live Cap C1 | v0 search, all declared sites |
| v0_live_C2 | original + live Cap C2 | v0 search and declared site-selection probe |
| v0_stable (S0) | original + StableCap C1 | DEC-035 stable observations, v0 search |
| S1_literal | literal-continued base + StableCap C1 | cap not retrained; common-original-base LS reference |
| S1_LM | LM-continued base + StableCap C1 | cap not retrained; common-original-base LS reference |

All full constructors, defaults, observation/encoder/cache versions, support and answer masks, delta positions,
null/write branches and memory policies must be pinned; this table is not sufficient runtime configuration.

The completed continuation outputs and recipes are verified in [R1-X7](../logs/review_r1_24.md).
Literal checkpoint `7591cfd1209f01c1d9877be6b596da56e3a3b45c2fa3e693cdb31407bbf59ef5` passes aggregate base fidelity;
LM checkpoint `4b09cb8d7d3fb301025d0ecdcaede7ecca68c0703ab0a63fd60bb6a77aa50a3a` fails KL (.0949791 > .001).
The matrix intentionally has no admitted continuation paths/hashes yet. Literal self-distillation is a numerical
negative control, not an exactly unchanged executed checkpoint. A valid S1_LM needs a new admitted recipe/output or
an explicit scope amendment (U03). Continued-base learned-reader pilot cells do not become S1 or retrained-cap evidence.

Primary v1 also has substantial ordinary-text drift after edits. R1-54's new text-null reader has promising zsRE
development drift but changed RET-GS (.96/.725) and incomplete replication at this cutoff. **No automatic replacement
of primary v1 occurs here.** Final reader/rule/training seed, all updated identities, R1-54 acceptance, exposure review
and any continuation-budget refresh are U02. The [null specification](tasks/R1-50b.md) distinguishes implemented and
proposed training recipes.

## 3. Fresh datasets, exclusions and sealing

Use three fresh zsRE realizations from MEND train through the E.2 teacher filter, each with 1,000 edits, subject-disjoint
from every v0 development, opened sealed and S7 example and all revision training/development exposures.
DEC-034's conservative policy excludes the whole old eligible factual pools, not just reported examples.

DEC-041 accepts v2 policy and the current v3 register. The R1-D1f wrapper binds that acceptance, every derived inventory
and its resource hashes; it does **not** authorize a draw. It records 38,029 source subject keys / 38,027 canonical keys.
Normalization is NFKC + casefold + collapsed whitespace, preserving punctuation, with only the explicitly verified
alias pairs. Unknown global alias underexclusion is not certified as zero.

For zsRE the original fresh-candidate v1 review had 58,498 prior-clear representatives. Use its payload only through
the v3 source-index overlay: **52,498** direct prior-clear survivors after all **6,000** DEC-039 candidate subjects were
reserved. The accepted training subset contains 3,000; the other 3,000 are not released. The larger v3 raw inventory
(143,753 source records / 81,857 unique primary subjects) is not a teacher-eligible or context-cleared final population.
Context/entity/alias review, teacher eligibility yield and final exact counts remain U04.

CounterFact has two explicit readings (U05):

- Strict v3 policy leaves **zero** old-pool candidates. A distinct fresh source would need provenance, review and
  a new inventory; no distinct local candidate payload is currently admitted.
- A reason-specific exception for `old_eligible:counterfact` would leave **12,246** candidates after every other v3
  exposure exclusion, including the 3,000 DEC-037 training facts. It cannot waive another exclusion reason.
  The separate CounterFact source decision is not recorded in DEC-041. A proposed default in the lead queue is not
  acceptance. No selection is made by this draft.

Before sampling, account for every exposure after v3, including ordinary-text training that could mention candidate
subjects. New exposure may require v4 and a new binding. Pin canonical IDs, source record hashes, exact prompts/targets,
answer-token lengths, alias normalization, teacher checkpoint/filter code and receipts. Teacher/context failures get
explicit exclusion reasons before the draw; eligibility must not depend on a cap's performance.

**Proposed outside reserve:** 100 original edit prompts per realization, wholly absent from every final edit realization
and other reserved populations, paired across conditions, orders and checkpoints. That requires at least 3,300
distinct admitted facts per dataset before additional challenge reserves. Do not reuse unused training-reservation
subjects. Fix all final counts, draw algorithm, RNG implementation, seeds, canonical draw order, stratification and
replacement/shortfall rule before drawing (U06). Insufficient yield requires a new source/scope decision, never silent
resampling around test results.

Near-miss, explicit revision and controlled composition inventories need their own reviewed support/query construction
and disjointness plan (U09). Existing development challenges are exposed; the 54 composition rows are not 100 verified
fresh cases. Confirm-mode loading/sealing and schema/normalization round-trip checks must succeed before launch (U07).
Development code in this lane opens no sealed realization payload.

## 4. Experimental units and schedule

Matrix v3 has **8 conditions × 2 datasets × 3 realizations × 5 orders = 240 cells**. Realization seeds are 0/1/2;
order seeds are 100/101/102/103/104; **model-training seed is 0**. Three data seeds are not three independent trained
models. If the lead requests a model-seed axis, regenerate the entire eight-condition matrix and budget. The retained
“300 core cells” alternative text refers to an older six-condition matrix and must not be copied as the expanded count.

Within a dataset, the same items, item IDs, targets, locality/outside/challenge inventories and order mappings are paired
across conditions. Independent realizations are the statistical clusters; order permutations stay within a realization.
Run each condition from its admitted clean state. S0 and R0 each contribute their same 30 cells once and are reused
across continuation contrasts. Training jobs are shared and charged once, not multiplied by evaluation cells.

Every stream plans 1,000 attempted edits, checkpointed after 100, 300 and 1,000 attempts. Immediate ES is recorded after
each completed edit; checkpoint retention re-queries all prior attempted items with the declared prompts. Final
RET-ES/RET-GS at 1,000 are the main retention endpoints. Proposed cadence: unseen and size diagnostics at all three
checkpoints; challenge clones at the final endpoint; a declared drift subset per checkpoint and full validation at the
final endpoint. **Exact challenge/LS/drift cadence, full-validation allocation and reserve identities remain U08/U09**
and must be priced; the current matrix/profile prose does not completely resolve them.

Condition scheduling, run order RNG, resume semantics and wall/accelerator stop rules are U17. Save every attempt,
failure and resume boundary. Resume only from a matching checkpoint/ledger/code identity; do not try different seeds
or rules after inspecting confirmation results.

## 5. Endpoint definitions and denominators

All answer queries reset selection at the prompt boundary and hold that selection throughout generated answer tokens.
No gold query label enters reader features, candidate selection or fast updates. Support labels are available only in
the support-driven update API; query labels are used for scoring. Snapshot and restore any challenge mutation, and
verify base/reusable parameters and parent episodic state before/after.

| Endpoint | Numerator / denominator and required reporting |
| --- | --- |
| Immediate ES | Exact normalized complete-answer correctness immediately after each edit / all planned edit attempts. A behavioral update rejection counts as an unsuccessful edit; an infrastructure-short stream is incomplete, with completed-only diagnostic values separately labeled. |
| RET-ES | Correct original edit prompts at checkpoint / every predeclared prior edit item, including failed acquisition. No acquisition conditioning. |
| RET-GS | Mean correctness over each item's predeclared paraphrases, then equal mean over all prior edit items. Retain item and paraphrase counts; do not let items with more paraphrases receive more weight. |
| Survival conditional | Retained correctness among items satisfying the frozen acquisition criterion; report numerator and acquired count separately. Diagnostic only, never a replacement for unconditional RET-ES/GS. |
| LS | Preserved normalized generated answer versus the frozen reference / every planned locality query. Full-answer is the main endpoint; first-token agreement and KL are separate. For S1, reference is the original base under DEC-040. |
| Near-miss | On an independent clone, teach the support and query its own prompt plus the neighbour. Neighbour answer preservation / all planned cases is primary; own success separate, without excluding failed acquisition. Matrix proposes 100 cases; final inventory/cadence U09. |
| Explicit revision | Teach old then new versions on an independent clone. Primary success requires old acquisition, new correct answer, no old-alias answer, old record correctly inactive/superseded and new version active. Denominator is every planned case. Latest-answer success, paraphrase success and old-alias reappearance are additional counts. Matrix proposes 50 clones; final allocation U09. |
| Two-fact composition | Correct composed answer / every planned semantically verified case with two declared support facts. Missing/unverified construction is unreachable; a wrong generated bridge is a scored failure. Chained generation must use the generated bridge, not a supplied gold bridge. Report reviewed direct-prompt composition separately; one does not substitute for the other. |
| Unseen edit prompt | One original prompt per reserved outside item. Hard-gate false fires / planned inventory; bounded answer-text changes / planned inventory; strict complete-answer preservation / planned inventory. Record distinct scored-answer and firing-observed counts. Never condition the denominator on firing or acquisition. |
| Memory-size profile | At attempted-edit checkpoints, report actual active and all retained records, bytes, candidate recall, own firing, per-role null/rejection and full-answer outcomes. Target active sizes 100/300/1,000 separately; if a size is not reached, show actual occupancy and mark the exact-size result unavailable. |
| Ordinary-text drift | Sum paired next-token losses / actual valid positions; ΔNLL in nats and PPL ratio exp(ΔNLL). For 128 windows of 128 tokens under current-prefix selection, denominator is 128×127=16,256. Full-validation count and dropped-tail policy must be pinned separately. |
| Base fidelity | KL(original || candidate) and candidate-minus-original NLL on a declared paired validation inventory. Report positions, full distributions, dtype and reference hashes. Current R1-24 diagnostic used 8,192 positions; it is not the 16,256-position cap-drift sample. |

The existing main LS convention compares normalized bounded decoded text and does not itself gate equality on both
stop flags. Preserve it explicitly for comparability; also publish termination, truncation and strict complete-pair
counts. If the lead requires termination-qualified LS as primary, version the endpoint before freeze (U10).
For unseen prompts, report both bounded text change and strict complete preservation; missing stop information cannot
be manufactured as a complete answer.

Unseen eligibility must consult full attempted history, including failed, evicted, revised/superseded and inactive
records, and exclude overlapping fact/item/subject/prompt identities. Unknown history or missing firing instrumentation
is unavailable, not evidence of abstention. All comparator adapters must expose real memory identities and hard
decisions. Per-condition cap-off is the unseen reference; original-base substrate drift is separate.

The challenge evaluator currently loads **development-mode** inventories. A final challenge loader/driver, verified
composition inventory and budget allocation are absent from the 240-cell composition schedule (U09/U11). Composition
appears in plan 9 but not the current cell endpoint lists; add an explicit paired allocation or record a scope change.
Do not equate a tested endpoint class with completed final execution.

For ordinary text, every next-token prefix is a new query: reset and select from the full prefix before predicting.
Do not reuse the selection made for its first token across later prefixes. Firing probes at lengths 16/48/96 have
denominator 3K, distinct from loss denominator 127K. Compare each cap with its own cap-off base, and separately compare
continued to original bases. Training windows, model-selection text and final validation must remain distinct;
[the text-null spec](tasks/R1-50b.md) gives exact definitions and current implementation limitations.

## 6. Contrasts, margins and analysis

The current ordered contrasts are treatment minus control:

| Registry ID | Difference |
| --- | --- |
| stable_observations | v0_stable − v0_live_C1 |
| matched_updates | matched_update − v0_stable |
| nonlearned_geometry | R1_nonlearned − matched_update |
| learned_component | R1_learned_ff − R1_nonlearned (package comparison) |
| v0_routing | v0_live_C2 − v0_live_C1 |
| literal_vs_S0 | S1_literal − v0_stable |
| LM_vs_S0 | S1_LM − v0_stable |
| R0_vs_literal_S1 | R1_learned_ff − S1_literal |
| R0_vs_LM_S1 | R1_learned_ff − S1_LM |
| informative_vs_literal | S1_LM − S1_literal |

Primary contrast selection and multiplicity are **OPEN U12**. A useful proposal is to state the deployed-package claim
against the random package and explicitly require comparisons to the strong fixed-rule controls. Direct primary-minus-
stable and primary-minus-matched-update contrasts can reuse existing cells, but are not registered by matrix v3; add
them before freeze if they are claimed. Freeze a primary family, datasets and any conjunctive success rule; label
remaining contrasts secondary/descriptive. A nominal 97.5% interval does not automatically control error across ten
contrasts, two datasets and all endpoints. Do not choose the primary family after fresh outcomes are opened.

Accepted provisional DEC-033 margins: practical RET-GS improvement **≥ .05**, ES difference **≥ −.02**, LS difference
**≥ −.01**; base fidelity KL **≤ .001 nats**, NLL increase **≤ .01 nats/token**. Final inequalities and applicability
are frozen after development (U13). No accepted numerical success margin exists for unseen rejection, composition,
revision or size profile; report their estimates descriptively unless the lead registers one before outcomes (U14).

For each complete dataset/contrast/checkpoint, score item outcomes, average paraphrases within item, then equally
average paired item differences for each realization/order. Obtain a complete 3×5 difference matrix per metric.
Use the v0 `cluster_bootstrap` primitive on CPU float64:

1. Average the five order differences within each realization.
2. With NumPy `default_rng(0)`, draw 10,000 bootstrap samples of three realization indices with replacement.
3. Keep all orders of a realization together; average the three sampled realization means.
4. Point estimate is the equal mean of realization means. Proposed two-sided confidence is .975, using percentile
   bounds at .0125/.9875 with linear quantiles. Pin NumPy/code version, seed, draws, confidence and method.
5. Report all 15 differences, three cluster means, order ranges, interval and cluster count. Do not resample items
   independently or treat 15 orders as 15 independent datasets. With only three clusters, uncertainty is preliminary.

**U15:** build/validate the revision pairing adapter against the frozen item inventory. The v0 `paired.py` still
hardcodes C2/C1/CR and a .02 RET-GS practical margin; it must not be run unchanged to classify revision results.
The reusable bootstrap primitive is applicable; the old arm/margin wrapper is not.

Proposed classifier, subject to explicit U12/U13 adoption: positive requires point ΔGS≥.05, GS lower bound>0,
ES lower bound>−.02 and LS lower bound>−.01 for every required primary comparison. Negative is evaluated before
qualified when GS upper bound<.05 or an ES/LS upper bound is below its negative margin. Qualified requires
point GS≥.05, GS lower>0 and point ES/LS within margins while interval noninferiority is unresolved. Otherwise
inconclusive. Missing pairs are incomplete. A failed fidelity/admission gate yields ineligible/mismatched status;
a favorable retention interval cannot override it. This proposed mapping does not retrospectively classify pilots.

## 7. Missingness, failures and invalid runs

Bind the full expected item/prompt inventory independently of observed rows; agreement between two equally shortened
files does not establish completeness. Reject duplicate IDs, wrong order, mixed datasets, nonfinite numbers,
mismatched labels/reference hashes and missing pairs. No imputation or bootstrap over only surviving orders/realizations.

For challenge/unseen results retain `ok`, `unreachable`, `resource_failure`, not-run and contract/identity failures
with reasons. Publish planned, attempted, scored and firing-observed counts, and success among scored as a diagnostic.
The full-inventory fraction is null until all planned cases are scored. Validly executed wrong answers, wrong bridges,
wrong revision state and behaviorally rejected edits remain scored failures. Infrastructure failures are not silently
converted into model errors or removed to improve means.

Pin the bounded retry policy (U17). A permitted retry repeats the same cell identity and records all failed cost.
Parameter/base mutation or unrecoverable state restoration is a contract failure that stops the affected queue.
New code/config/source identities require a versioned admission decision; never continue a frozen run with silent drift.

## 8. Memory, compute and execution budget

Enforce ≤5 million reusable cap parameters and ≤64 MiB persistent deployed memory, including weights, stored stable
observations/keys/codes, all answer-position deltas, support tokens and persistent indices/metadata. Report optimizer,
replay, caches, physical RSS/device peak and temporary clone peaks separately. Compare to v0's 36.75 MiB with a
matched-total-memory branch or a cost frontier; equal edit counts do not establish equal memory. At 1,000 edits exact
answer-length/delta counts and physical peaks remain unmeasured (U16). Duplicate-key stress is capacity/timing evidence,
not factual generalization.

Profile exact admitted configurations, datasets, lengths and occupancies before pricing confirmation:

| Profile | Required resolution |
| --- | --- |
| P1 edit/memory | all eight conditions; five-step matched control; 0/100/300/1,000 occupancy; true bytes including clone peaks; warm p50/p95/max edit time, rejected work and cold compile separately |
| P2 outer/endpoints | actual differentiated forward/reverse work; cache construction; query resets; max-32 generation; challenges and full-validation drift; support/base masks; in-flight stop overshoot |
| P3 unseen/scale | every comparator adapter; paired IDs and at least 1,100 distinct development facts per dataset; real 100-query cap-on/off generations at each size, role counts, truncation and selection costs |
| P4 continuation | admitted checkpoint identities and base-specific caches/calibration; teacher/student/source exposure; forward and separate reverse work; base fidelity; full 1,000-edit S1 endpoint cost |

Existing P1/P2 allowances of 1,800/3,600 seconds need review for the expanded scope; P3/P4 allowances and full-profile
cost are null. Every cell has `proposed_seconds=null`, `failure_reserve_seconds=null`, `frozen=false`,
`launch_allowed=false`; the .20 reserve fraction alone is not a measured ceiling. Freeze support-token totals,
training-token counts or explicit not-applicable values, memory admission and continuation training accelerator cost.

The working budget is ≈20 development GPU-hours + ≈15 confirmation hours + co-training (≈40 total), with plan 9's
development two-hour run ceiling and checkpointed stops. Do not infer remaining allocation from wall-clock dates.
Matrix v3's legacy endpoint proxies sum to **802,440 s (222.9 h)**: the older 538,920 s plus 263,520 s borrowed for new S1
cells. These are neither measured lower bounds nor approved limits. They already exceed the 54,000 s confirmation
envelope, while new endpoints remain unpriced. The new outside workload alone is 72,000 paired queries / 144,000
max-32 greedy decodes across 240 cells. A measured revised budget/scope decision is mandatory (U16).

Charge shared reader/continuation training once; report bank construction, valid forward tokens, reverse positions,
relaxation/JIT work, failed/rolled-back work, warm device time, cold compilation and wall time independently.
Do not equate forward-token matching with total-compute equality. The current continuation basis is 771,581 forward
tokens against primary v1's configuration re-execution; a new text-null reference requires a fresh reconciliation.
Reused analytical reference cells and repeated actual executions have different cost implications.

Plan 9 places Stage 2 on relative days 8–18 and Stage 4 on days 20–28. These are planning windows, not a verified
calendar deadline or proof of being on schedule. A refreshed stage start, work ledger and profiled critical path (U18)
are needed to state timeline position. CPU inventory/analysis/adapter work can proceed while GPU diagnosis runs;
the final GPU profiles, admission and sealing are serial gates.

## 9. Exact freeze binding checklist

The lead's final manifest must bind all of the following explicitly, with no unresolved execution placeholders:

1. Accepted protocol text/hash, relevant DEC row identities, scope/deferred claims, counter-review disposition,
   final matrix version/hash, unique cell/contrast IDs, primary family and multiplicity/classification rules.
2. Git/source identity and every executable source tree, external wrapper/adapter, endpoint and analysis script used;
   runtime/library lock, JAX backend/determinism/dtypes, hardware and code-drift/resume policy.
3. Original and every continued base file hash and tensor digest; reader/controller files and parameter digests,
   architecture/config, training seeds, random initialization, provenance and output-admission receipts.
4. Calibration A/b_m/τ values and source, all routing/null/top-k/lexical/stop settings, support/query masks, encoder/tap
   versions, exact training objective/normalizations/schedules, fast update rules and permitted base leaf-change masks.
5. Tokenizer/vocabulary/normalization/alias/stop token hashes, generation limits/termination/selection policy, immutable
   support/query-label API boundary and base/parameter/state before-after checks.
6. Accepted exclusion wrapper and every child resource hash, normalization/canonical aliases/reasons, subsequent-exposure
   attestation or new register version, independent CounterFact source decision and any reason-specific waiver.
7. Fresh source/filter/context review, teacher identity and eligibility receipts, canonical ordered final inventories,
   dataset realization and order maps, outside/challenge reserves, exact labels/prompts and sealed payload hashes.
8. Training/development/validation separation, all exposed pool IDs and text offsets, feature-bank content/identity/
   dtype/cache hashes, new-population handling and cache rejection tests.
9. Endpoint schemas, full expected denominators and failure statuses, query inventories/cadence, revision/composition
   semantic provenance, LS and ordinary-text reference definitions, drift windows/positions/tail rule and full split.
10. Deployed parameter/byte caps, memory accounting/eviction/version/serialization policy, exact-size and clone behavior,
    actual token/memory profiles and matched-memory comparison or explicit frontier-only scope.
11. Per-job and total ceilings, failure/endpoint reserves, overshoot limit, training/shared cost ownership, profiling
    receipts, compilation/warm timing convention, GPU queue order/lease, checkpoint/retry/stop policies.
12. Paired item inventory/analysis adapter, aggregation/bootstrap RNG/draws/confidence/quantiles, margins and equality
    boundaries, diagnostic versus confirmatory endpoint registry, missingness and ineligible-condition rules.
13. Lead approval identity/time, destination paths under results/logs versus assets, freeze ID and integrity validation
    command. Run admission must compare all bindings and refuse differences before any confirmation workload.

This draft and the register-only wrapper are not substitutes for that final manifest.

## 10. Open items and checkpoints

| ID | Unresolved choice or missing artifact | Owner / checkpoint |
| --- | --- | --- |
| U01 | Which plan-9 base-learning, ePC, unroll, settling and retrained-cap comparisons are included/deferred; matched-memory scope | lead, scientific scope |
| U02 | Final reference v1 versus text-null successor; rule, weights, model seeds, R1-54 seed/CF/long-memory evidence; refresh all dependent IDs/budgets | owner + lead, Stage 2 acceptance |
| U03 | Final continuation checkpoint admission; literal numerical qualification; fidelity-valid LM or explicit scope amendment | owner + lead, base-fidelity gate |
| U04 | zsRE context/alias and E.2 eligibility, actual final yield; post-v3 exposure audit/new register | data owner, before draw |
| U05 | CounterFact strict fresh source versus reason-specific old-remainder exception | lead, before draw |
| U06 | Exact draw/split/stratification/RNG/shortfall rules, data/model axes and disjoint outside reserves | owner + lead, before seal |
| U07 | Final payload schema, tokenizer round-trip, seals, confirm-mode loaders and immutable IDs | owner, data admission |
| U08 | Exact core/LS/unseen/size/drift cadence, full-validation positions/window/tail policy and reference bases | owner + lead, endpoint freeze |
| U09 | Fresh near-miss/revision counts/cadence and composition inventory, semantic review, direct vs chained endpoint, matrix allocation | owner + lead, challenge admission |
| U10 | Preserve existing bounded LS convention or version a termination-qualified primary; all generation defaults | lead, endpoint definition |
| U11 | Final challenge driver, all comparator memory/firing observers, restore/cache/API/hash gates on actual implementations | owner, implementation admission |
| U12 | Primary contrasts/datasets, direct stronger-control comparisons, multiplicity and conjunctive claim | lead, analysis preregistration |
| U13 | Exact classifier and inequalities; final margin applicability and fidelity/full-drift admission | lead, analysis preregistration |
| U14 | Descriptive-only versus numerical claims for unseen/revision/composition/size; any precision/sample-size rule | lead, analysis preregistration |
| U15 | Revision pairing/analysis adapter with independent expected inventories and .05 margin | CPU implementation owner, before freeze |
| U16 | P1–P4 measured profiles; 1,000-edit bytes/tokens, shared-training cost, all cell ceilings/reserves and affordable scope | GPU owner + lead, budget gate |
| U17 | Queue RNG/order, bounded retry/resume policy, failure handling, code identity, runtime/environment freeze | owner, launch admission |
| U18 | Calendar anchor, cumulative charged spend and updated critical-path forecast | owner + lead, schedule review |

Every grouped JSON-null occurrence is listed in the placeholder inventory. Intentional nulls (no cosine floor, no
training job for an unchanged base/random reader) remain semantic settings, not missing values. Historical pruning
counts and the old model-seed alternative must be corrected in a new matrix version before admission, not interpreted
as current 240-cell totals.

Parallel work before the freeze: CPU data/context review and source-decision preparation; revision pairing/missingness
adapter; comparator observers/final challenge loader; composition semantic inventory; receipt/budget aggregation.
Assign distinct new files and preserve the active R1-54 owner lane. GPU profiles follow the selected reference and
implemented adapters. Fresh sampling follows source/exposure decisions; sealing follows eligibility/schema checks;
the lead freeze follows complete protocol, budget and counter-review; confirmation follows identity admission.
No dependency is satisfied merely by the completion of this draft.
