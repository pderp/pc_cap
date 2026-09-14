# Revision v1, Stage 2 report — learned applicability with stable observations and per-position writes

Orchestrator's revision (2026-09-14, afternoon) of Codex's [draft 1](R1_stage2_report_draft.md) and its
[addendum](R1_stage2_report_draft_addendum.md), which are preserved unchanged. Evidence cutoff: the working tree at the
time of writing (the last committed state is named in the git log entry that adds this file); numbers come from the
files linked in each section and from [R1_stage2_notes.md](R1_stage2_notes.md). Contract: [plan 9](updated_plan9.md)
with the recorded [decisions](decisions.md) (DEC-033 … DEC-042). The [v0 report](report.md) and its negative findings
stand; nothing here is confirmatory and nothing is frozen.

## 1. Abstract

The v0 cap mostly stored usable values but read the wrong record. Revision v1 replaces the read path: observations are
taken from a write-free pass of the fixed base, a small learned reader (tied cosine embedding, pairwise null head,
lexical-overlap feature) chooses at most one record per query or declines, and each record carries per-answer-position
deltas taught by normalized adjoint steps under the v0 aggregate bound. One deployment rule serves both datasets.

On the 100-edit development streams the current reference (condition v2, trained with ordinary-text null queries)
reaches zsRE RET-GS 0.96–0.98 and CounterFact 0.725–0.85 over three training seeds, with ES 1.00, RET-ES 1.00 and
LS 1.00 on every run. The non-learned controls sit at 0.44 (v0-stable, matched-update) and 0.65 / 0.18 (random reader
with the same write path) and v0 live at 0.24–0.29. Continued training of the base on the same token budget does not
reproduce the gain (R1-24). The drift that Codex's addendum found (+0.60 / +0.39 nats on ordinary text) is traced to a
null that had never seen low-similarity text and removed by training on ordinary-text windows (0.000 / +0.012 nats).
On the real base the reader preserves 100/100 near-neighbour answers, completes 100/100 revisions, uses 51–74 % of the
64 MiB state ceiling at 1,000 records with exact restore, and costs 0.07–0.13 s per edit and 10–15 ms per query.

What is not established: fresh-data generalization (no confirmatory stream has been run), any advantage of predictive
coding (the reference is BP-trained and feedforward), retention at 1,000 edits (CounterFact locality firing rises to
10 % of locality prompts at 1,000 records; zsRE accepts 7 % / 25 % / 45 % of edit-style prompts about absent facts at 100 / 300 / 1,000 records), and
compute-matched superiority over the controls. The run matrix (240 cells) does not fit the 15-hour envelope at
measured costs; §7 proposes the cut for the lead's decision.

## 2. The system and how it is trained

### 2.1 Architecture and boundaries

The base is the JAX GPT-2 (BP) implementation of v0, fixed throughout. The cap observes it with writes disabled at
blocks 3, 7 and 11 (last-position and span features), so support keys and query keys share one stable representation.
A tied cosine embedding retrieves the top four records; a pairwise null head over [q̂, k̂, q̂⊙k̂], a query-only null
term and a lexical-overlap feature with stop list v1 decide whether the best candidate applies (threshold 0.5, no
cosine gate). The decision is made once per query, held across the generated answer and reset between queries; it
supplies binary write mass. A record's write is the per-position delta taught at edit time (five normalized adjoint
steps, learning rate 0.1, τ 0.1, aggregate bound A 0.3 with the archived v2 calibration scales); the controller write is
replaced by the delta for records that carry one; fast code adaptation is off. Prediction sees only the query prompt and
stored support; labels and target record ids are training and evaluation quantities (checked in R1-46).

Identity: [primary_condition_v2.json](../manifests/revision_v1/primary_condition_v2.json) (three seeds; seed 0 NPZ
SHA-256 `c5777b5b…`); v1 ([primary_condition_v1.json](../manifests/revision_v1/primary_condition_v1.json)) is the same
package trained without ordinary-text nulls and is kept as the R1-54 comparison. Stop list:
[stop_tokens_v1.json](../manifests/revision_v1/stop_tokens_v1.json).

### 2.2 Training

Pools: CounterFact training pool v1 (3,000 items drawn from the unopened remainder of the old eligible pool, DEC-037)
and zsRE training pool v1 (3,000 teacher-incorrect items from Codex's 6,000-candidate draw, DEC-039); the first 1,000
of each are cached as feature banks (900 training / 100 checkpoint-selection rows per bank). All 6,000 zsRE candidates
and the 3,000 CounterFact items are recorded as exposed. Episodes are stream-scale: 64-record memories mixed across
both domains, eight queried records (own-prompt, paraphrase, locality roles), out-of-memory nulls from the same pools,
and — in v2 — eight ordinary-text null queries per episode from 512 OpenWebText windows in the training range at
prefix lengths 16/48/96 (cap-off logits kept for the preservation term). Objective: answer cross-entropy, class-balanced
retrieval/null cross-entropy over all records, and a preservation KL to cap-off logits; AdamW 1e-3, weight decay 0.01,
clip 1.0, 300 steps × 2 episodes, checkpoint chosen by development retrieval loss on six fixed episodes (v2 seeds
selected steps 149 / 249 / 299). Cost per seed: 339–379 s training wall, ≈ 42k logical full forwards, ≈ 41k reverses,
≈ 815k forward-token positions (R50-09 ledger; earlier runs are wall time only). Training uses a soft distribution
over all episode records and controller writes while deployment uses hard selection and per-position deltas; the
result is empirical for this package, not a meta-gradient through the deployed update (R1-46).

### 2.3 Measurements

| quantity | definition |
| --- | --- |
| ES | immediate full-answer acquisition after each edit (greedy, ≤ 32 tokens, newline/EOS stop, alias match) |
| RET-ES / RET-GS | original-prompt / paraphrase full-answer success at the end of the stream, averaged within item then across items; no conditioning on acquisition |
| LS | identical cap-on vs cap-off decoded text on 50 locality prompts at the end of the stream |
| drift | mean next-token NLL change on ordinary text (128-token windows, one selection per position) |
| near-miss, revision, unseen-prompt | Codex's R1-43/R1-44 endpoints on the real base (§5) |
| bank own-firing / recall | cached-feature selection diagnostics without decoding; never a substitute for RET-GS or LS |

## 3. Why the design changed

The chain is recorded in [R1_diagnosis.md](R1_diagnosis.md) and the notes; several components changed together, so it
motivates the design and is not a factorial ablation.

| observation | evidence | consequence |
| --- | --- | --- |
| v0 stored usable values but read the wrong record | zsRE stream: live C1/C2 paraphrase 0.24/0.29; oracle reads 0.94 | storage exonerated; selection and observation are the loci |
| edited observations drift from stored keys | C1 site-3 key displacement 0.23 vs radius 0.189; shadow stable keys 0.67/0.49 | write-free observations at write and read (v0-stable control: 0.44) |
| fact code + controller could not carry new answers | intermediate ES 0.02 (one delta per record) → 0.13 (soft mixing) → 0.23 (hard dot) → 1.00 (tied cosine, hard top-1) | per-position deltas, tied cosine reader, binary mass |
| random geometry solves much of zsRE, fails CounterFact locality | random reader + gate: zsRE 0.65/1.00, CounterFact 0.18/0.16 | a learned applicability decision is needed for relation neighbours |
| small natural episodes taught the wrong null | own prompts rejected; balanced/locality nulls alone did not transfer | stream-scale episodes, out-of-memory nulls, both domains, lexical feature |
| one domain's null does not transfer | CounterFact-only reader: CounterFact 0.775/1.00, zsRE 0.49/0.98 | mixed-domain training with the zsRE pool (DEC-039): one rule |
| the null never saw ordinary text | v1 fires on 37–49 % of ordinary prefixes; +0.65 / +0.38 nats | ordinary-text null queries (v2): 0 firing at probe lengths, 0.000 / +0.012 nats |

DEC-038 (drop the learned reader) was withdrawn on the lead's instruction to keep pushing; the recovery above is the
result.

## 4. Development results (100-edit streams unless stated)

### 4.1 Controls on the zsRE Stage 0 stream

| condition | ES | RET-ES | RET-GS | LS |
| --- | ---: | ---: | ---: | ---: |
| v0 live C1 / C2 | 1.00 / 1.00 | 0.92 / 0.79 | 0.24 / 0.29 | 1.00 / 1.00 |
| v0-stable C1 / C2 (DEC-035) | 1.00 / 0.99 | 0.99 / 0.97 | 0.44 / 0.44 | 1.00 / 1.00 |
| matched-update (three normalized steps) | 1.00 | 0.99 | 0.44 | 1.00 |
| random tied reader + gate 0.93 + deltas (R1-nonlearned), zsRE / CounterFact | 1.00 / 1.00 | 1.00 / 1.00 | 0.65 / 0.18 | 1.00 / 0.16 |

### 4.2 Learned reader, three training seeds, stream 21

| reader | zsRE ES / RET-ES / RET-GS / LS | CounterFact ES / RET-ES / RET-GS / LS |
| --- | --- | --- |
| v1 seed 0 / 1 / 2 | 1.00 / 1.00 / 0.98 / 1.00; 0.96; 0.97 | 1.00 / 1.00 / 0.795 / 1.00; 0.78; 0.785 (seed 2 ES 0.99) |
| v1 seed 0, stream 22 | 0.99 / 1.00 | 0.765 / 1.00 |
| **v2 seed 0 / 1 / 2** | **0.96 / 0.98 / 0.96**, LS 1.00 | **0.725 / 0.85 / 0.79**, LS 1.00 |

Rows link from [stream_eval.md](../results/R1/stream_eval.md) (`mixed_*` and `mixed_text_*` tags); Codex's recount
([stage2_report_evidence.json](../logs/r1_round7/stage2_report_evidence.json)) binds the v1 rows to their item files.
Seeds are reader replicates on one development draw; streams 21 and 22 overlap by 33 zsRE and 36 CounterFact items, so
these are not independent realizations. The v2 CounterFact spread (0.725–0.85) contains the v1 spread (0.765–0.805);
the ordinary-text nulls cost nothing measurable on zsRE. Against the random reader the package gains +0.31 to +0.33
(zsRE) and +0.55 to +0.67 (CounterFact) RET-GS and lifts CounterFact LS from 0.16 to 1.00 — a package comparison, not
the isolated effect of learning.

### 4.3 Longer streams and the larger-memory variant (v1 reader)

250 edits: zsRE 0.98 / 1.00, CounterFact 0.722 / 1.00. Training with 256-record memories: zsRE 0.97 / 1.00,
CounterFact 0.83 / 0.98 at 100 edits, worse zsRE unseen rejection in the bank assay; not promoted.

## 5. Behaviour at scale, endpoints on the real base, drift and cost

### 5.1 Ordinary-text drift (R1-54)

Per-position selection on 32 windows × 128 positions after 100 edits ([drift_assay_*.json](../results/R1/)):

| reader | after zsRE edits: firing / Δ nats / ratio | after CounterFact edits |
| --- | --- | --- |
| v1 | 0.365 / +0.647 / 1.91 | 0.490 / +0.379 / 1.46 |
| v1 + cosine floor 0.5 (non-learned fallback) | 0.010 / +0.002 / 1.002 | — |
| **v2** | 0.000 / 0.000 / 1.000 | 0.000 at probe lengths / +0.012 / 1.012 |

v0's ratios were 1.001–1.004. The +0.012 after CounterFact edits is residual firing at prefix lengths the fixed probes
did not sample; the assay now counts every scored position and a recount is queued. Codex's addendum measured the v1
drift on the full 16,256-position subset (+0.60 / +0.39); the figures agree in kind.

### 5.2 Endpoints (R1-43, R1-44; v2 reader; [results/R1/endpoints/](../results/R1/endpoints/))

| endpoint | n | result |
| --- | ---: | --- |
| near-miss preservation (CounterFact near-neighbour prompts) | 100 | 100/100 preserved; edited prompt exact 100/100; neighbour never fired |
| revision (v1 then v2 of a fact) | 100 | 100/100 (old record retired, new active, latest answer exact); old answer reappeared 0/300; new-answer paraphrase exactness 0.79 |
| composition | 0 | unreachable: no verified direct composition questions (54 two-hop chains are diagnostic only) |
| unseen edit-prompt, zsRE, after 100 edits (dev-remainder prompts) | 100 | false fires 7 %, all with answer changes |
| unseen edit-prompt, CounterFact, after 100 edits | 100 | 0 false fires, 0 answer changes (33 pairs untruncated at 32 tokens in both decodes) |
| unseen edit-prompt at 300 / 1,000 records (pool-sourced prompts and fillers) | 100 each | zsRE 25 % / 45 % false fires (every one changes the answer); CounterFact 2 % / 5 % |

The zsRE unseen rate is the main scale risk: plausible edit-style prompts about facts not in memory are accepted more
often as memory grows (7 → 25 → 45 % at 100 / 300 / 1,000 records; bank profile: out-of-memory hard-null 0.87 → 0.67 at 300). The 300/1,000-record points use
training-pool rows beyond the reader's 1,000 training items as labelled memory fillers and outside prompts; a
100-record run with the same pool-sourced prompts is queued to separate memory size from prompt source.

### 5.3 Cost and state at occupancy (R1-40c P1; [results/R1/p1_profile/](../results/R1/p1_profile/))

1,000 edits per dataset on the real base, v2 reader and the non-learned control, all accepted:

| quantity | zsRE | CounterFact |
| --- | --- | --- |
| cold first edit | 3.5 s | 3.4 s |
| warm edit p50 / p95 (independent of occupancy) | 0.11 / 0.22 s (19 forwards, 7 reverses, 232 tokens) | 0.07 / 0.08 s (12 / 4 / 103) |
| edit p50 by answer positions [2,4) / [4,8) / [8,33) | 0.08 / 0.15 / 0.26 s | 0.07 / — / — |
| query p50 at 100 → 1,000 records (greedy ≤ 32) | 12.5 → 14.4 ms (3.8 → 5.3 ms per step) | 10.0 → 14.6 ms (4.4 → 6.8 ms per step) |
| persistent state at 100 / 300 / 1,000 (13.39 MB weights included) | 17.3 / 24.6 / 49.9 MB (0.74 of ceiling) | 15.5 / 19.6 / 34.0 MB (0.51) |
| restore (export → import → export) | hash and bytes equal at every checkpoint; 7 ms | equal; 6 ms |
| locality-prompt firing at 100 / 300 / 1,000 (v2) | 0 / 0 / 0 | 0 / 0.06 / 0.10 |
| device peak / process RSS | 763 MiB / 2.3 GB | 752 MiB / 2.2 GB |

The 1,000-edit endpoint is admissible on both datasets without eviction. Edit cost scales with answer length, not
occupancy; query cost grows slowly through the lexical term. CounterFact locality firing at 300–1,000 records is the
near-duplicate failure already seen in the bank profile (own-record firing 0.59 at 1,000), now measured with decoding:
LS at 1,000 CounterFact records will fall below 1.00.

## 6. Continuation and fidelity controls; predictive coding

R1-24 (DEC-040) ran both treatments on the matched budget of 771,581 forward-pass tokens (458,002 outer-training +
313,579 bank-construction positions): literal self-distillation (a numerical no-op; passes fidelity) and continued
language-model training (fails its fidelity gate: the base's held-out distribution moved 0.095 nats at lr 1e-6). S1−S0
stays within ±0.05 RET-GS and R0−S1 is +0.49 to +0.59 (zsRE) and +0.78 to +0.80 (CounterFact): continued base training
does not explain the revision's gain. The LM treatment's LS collapse (0.86 / 0.28) is the changed base answering its
own locality prompts differently, present with no cap writes; a KL-bounded continuation would be needed to certify an
informative control. Side finding: the v1 reader keeps its retention on the changed base (0.97 / 0.775).

Predictive coding: the reference is BP-trained and feedforward; the earlier matched synthetic comparison (BP vs the
SD-24-corrected ePC surrogate at identical schedules) favoured BP on every development metric (answer NLL 2.85 vs 4.50,
retrieval CE 0.46 vs 0.96) and is diagnostic only. No claim about cap-level settling is made; Stage 3 remains
conditional.

## 7. Fresh data, the run matrix and the scope decision

CounterFact confirmatory source (R1-D2): 12,246 candidates remain under the reason-specific exception "old-pool
membership alone is not exposure" (0 under the strict v3 register); no distinct fresh CounterFact source exists locally.
DEC-042 (proposed): the exception applies unless the lead chooses otherwise; the draw and seal are the lead's acts.
zsRE: 52,498 pre-context candidates after the training-filter reservation; E.2 and context/alias exclusions to finish.

Codex's [matrix v3](../manifests/revision_v1/run_matrix_draft_v3.json): 8 conditions × 2 datasets × 3 realizations ×
5 orders = 240 cells of 1,000 edits with checkpoints at 100/300/1,000; all launches disabled, ceilings null; legacy
proxies 802,440 s (222.9 h) against a 54,000 s (15 h) envelope.

Measured components for one learned cell (§5.3 and the endpoint runs; wall time, real base): edits 73–111 s;
retention decoding at a checkpoint ≈ 20 ms per query (≈ 60 s at 1,000 CounterFact records); locality 50 pairs ≈ 2 s;
unseen 100 pairs ≈ 5 s; the full declared drift assay (128 windows × 128 positions, one selection per position) ≈ 165 s
cap-on per checkpoint plus one shared cap-off pass; near-miss + revision challenges ≈ 150 s. A cell with every
endpoint at all three checkpoints costs ≈ 1,150 s; with the 0.2 reserve ≈ 23 min, so 240 cells ≈ 92 h. The proposal
for the lead, recorded in the lead queue: keep all eight conditions and three realizations, run one update order per
realization (48 cells), run the full drift assay and the challenge endpoints at the final checkpoint only and the
cheap endpoints (retention, locality, unseen) at all three: ≈ 14 min per cell, ≈ 11 h plus reserve ≈ 13.5 h, inside
the envelope. Order effects are then unmeasured in the confirmatory runs and must be stated as such.

## 8. Limitations and artifact quality

- Development selection: all results are on repeated development draws with the reader's checkpoint chosen on bank
  rows; nothing is fresh. Seeds are reader replicates, not realizations.
- Short answers: CounterFact answers are one content token; zsRE answers average 3.7 positions. Longer answers cost
  proportionally more delta bytes (9,216 B per position) and edit time.
- The bank profiles at 1,000 records have zero outside queries; the real-base unseen runs at 300/1,000 use
  pool-sourced prompts, a different population from the dev remainder.
- Ledger accelerator seconds understate the wall cost (57 s charged vs 140 s wall for the zsRE profile); ceilings are
  set from wall time.
- Historical artifacts: eight early stream stems wrote both datasets to one directory; the recount keeps their
  summaries as history and uses the regenerated random reference (Codex R1-X6). Cache metadata does not bind
  paraphrase/locality inputs (Codex R1-28b); the bank identities are content hashes stamped after the fact.
- The composition endpoint is unreachable without verified direct questions; the two-hop chains stay diagnostic.
- The v0 negative conclusion is untouched; revision v1 has not been tested on any confirmatory stream.

## 9. What Stage 4 must establish

1. Lead decisions: DEC-042 (source), the matrix scope (§7), then the freeze (R1-41).
2. Before the freeze: Codex's protocol draft (R1-49) with the measured ceilings, the frozen exclusion register (R1-D1f),
   admitted candidate inventories with disjoint edit / unseen / challenge reservations, and the drift recount.
3. Confirmatory: fresh streams paired by item and order across conditions, three realizations, endpoints at
   100/300/1,000 with failed acquisitions and missing endpoints retained; contrasts and margins as pre-registered
   (RET-GS +0.05, ES loss ≤ 0.02, LS loss ≤ 0.01).
4. Optional, not blocking: a KL-bounded informative continuation control; top-k pairing on identical memories to
   separate CounterFact candidate misses from selection errors; Stage 3 settling against the same zero-step cap.

## 10. Reproduction

Training: `scripts/r1_50_stream_train.py --pool <counterfact_v1>,<zsre_v1> --pool-items 1000 --steps 300 --batch 2
--n-memory 64 --text-nulls 8 --text-windows 512 --seed <s>`; streams: `scripts/r1_13_stream_eval.py --dataset <d>
--theta <npz> --delta-steps 5 --delta-lr 0.1 --null-threshold 0.5`; drift: `scripts/r1_54_drift_assay.py`; endpoints:
`scripts/r1_43_endpoints_run.py`, `scripts/r1_44_unseen_run.py [--n-edits N --outside-from-pool]`; profile:
`scripts/r1_55_p1_profile.py`. Weights and banks live under `/home/derp/cap/assets/runs/pc_cap/R1/`; every script
refuses to overwrite an existing output. Codex's CPU recounts: `scripts.r1_47_evidence`, `scripts.r1_x6_audit`.

Disposition: the learned feedforward package is the primary revision condition for Stage 4; the report is a
development record for the lead's Stage 2 review, not an authorization to draw, seal, launch or freeze.
