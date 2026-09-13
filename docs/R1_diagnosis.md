# Revision v1 — Stage 0 diagnosis memo (R1-04)

Orchestrator, 2026-09-13 19:40 EDT. Inputs: `scripts/r1_diagnostics.py` (revised per R1-X0 finding X0-14, commit `f8c8c74`),
outputs under `results/R1/` (`diagnostics_{C1,C2}.json`, `traces_{C1,C2}.jsonl`, `diagnostics.md`; the earlier pre-review pass
is kept under `results/R1/prereview/` and is superseded). Setting: the v0 cap under the frozen v2 zsRE calibration and
budget (A = 0.3, R = 5, τ = 0.1), a fresh 100-edit zsRE development stream (seed 21, order seed 1), arms C1 (fixed
three-site schedule) and C2 (probe-and-choose). One seed, one order: this is a diagnosis, not an estimate.

## 1. Question

Plan 9 (DEC-033) asked Stage 0 to locate the v0 failure: is the paraphrase gap (RET-GS ≈ 0.24–0.29 against RET-ES ≈ 0.8–0.9
on this stream) a storage failure (the written values do not carry the answer), a read failure (the right record is not
selected), or an observation failure (keys and queries move with earlier writes)? Each answer points at a different part
of the revision design.

## 2. Measurements

Four read policies were applied to the same endpoint state, on each item's own prompt and on its paraphrase, teacher-forced
over the complete answer (exact = every position's argmax matches; the first-token statistic is reported but qualified):

| policy | what decides retrieval | C1 prompt / paraphrase exact | C2 prompt / paraphrase exact |
| --- | --- | ---: | ---: |
| live | the arm's sequential edited read (v0 as deployed) | 0.92 / 0.24 | 0.79 / 0.29 |
| oracle | the item's own slot per answer prefix, verified against the current bank (owner digest, active, presented token); unverified or missing entries force none | 0.93 / 0.94 | 0.92 / 0.94 |
| stable | cap-off (unedited-pass) query keys against the stored keys | 0.35 / 0.11 | 0.62 / 0.29 |
| stable_rebuilt | cap-off query keys against keys re-derived from cap-off passes on every slot's write prefix (shadow keys; cap untouched) | 1.00 / 0.67 | 0.98 / 0.49 |

Teacher-forced NLL per answer moves the same way (C1 paraphrase: live 7.64, stable_rebuilt 4.37, oracle 0.48). Oracle
verification: C1 1094 claimed bank×prefix entries, 1080 verified, 14 reused or inactive (excluded), 112 missing (27 items had
answer prefixes with no accepted write); C2 374 claimed, all verified, 832 missing because C2 left banks 1 and 2 nearly
empty (occupancy 6 / 4 / 364). Unrelated prompts never fire at any site in either arm (200 prompts).

Key geometry: C1's stored keys at site 3 sit a mean 0.23 (max 1.33) from their cap-off counterparts against a read radius
of 0.189, and at site 2 a mean 0.22 against 0.414; C2's keys barely move (0.026 at site 3) because it rarely writes
upstream. Under the live read, site 3 fires nothing on 72 (C1) and 58 (C2) of the 100 paraphrases at the first answer
position. Under stable_rebuilt, site 3 fires the item's own record on 71 (C1) and 51 (C2) paraphrases, and exact answers
follow that event almost one to one (C1: own → 67 exact of 71; other → 0 of 22; none → 0 of 7).

Costs (accelerator seconds, reconciled with the ledger to 0.1 s): C1 stream 88.3, diagnostics 14.7 (live 2.8, oracle 2.7,
stable 2.4, stable_rebuilt 2.7, cap-off key passes 2.6, key rebuild 0.5); C2 stream 20.2, diagnostics 9.8. A cap-off key
pass costs about as much as a live read at every position; the key rebuild is 0.5 s for 362 slots.

## 3. Diagnosis

1. **Storage is not the bottleneck.** With the right record forced, both arms answer 94 % of paraphrases exactly. The
   values written by v0 carry the answer for formulations they never saw.
2. **The first failure is observational.** v0 computes keys at write time and queries at read time from a sequential
   edited pass, so what site 3 sees depends on what sites 1 and 2 just wrote for the same prefix. That moves keys and
   queries by more than the site-3 read radius (C1) or moves the query away from a nearly stable key (C2). Reading with
   unedited-pass queries against unedited-pass keys, with no learned component and no retraining, raises paraphrase exact
   answers from 0.24 to 0.67 (C1) and 0.29 to 0.49 (C2), and restores own-prompt recall to 1.00 / 0.98.
3. **The second failure is selection.** With stable observations in place, the fixed geometry (nearest key inside a
   radius, one record per site) still picks another item's record on 22–27 % of paraphrases and nothing on 7–21 %. Sites 1
   and 2 fire other items' records on most paraphrases in C1; the answer survives only when site 3 fires the right one.
   That residual (0.67 → 0.94, 0.49 → 0.94) is the applicability decision the learned reader with an explicit null is
   meant to make.
4. **Selection is not held across the answer.** Under stable_rebuilt the item's own site-3 record fires at every answer
   position for 48 (C1) / 39 (C2) paraphrases, and at the first position only for 23 / 12; some of those still answer
   exactly because the base continues a correct first token. Selecting the record once per query and holding it (X0-05,
   DEC-034) removes that dependence.
5. **Interference at early sites is real but not yet costly.** No unrelated prompt fires anywhere, so locality held on
   this stream; the "other" firings at sites 1–2 are cross-item confusions among edited items, a near-miss risk that the
   reader's null and the near-miss endpoint must measure.

## 4. Consequences for Stage 1 and the comparative design

- Stable observations (`pccap.revision_v1.observations`, one unedited pass per prefix) are confirmed as the first
  requirement; keys must be encoded from the same observation at write time, and a key rebuild after any encoder change
  is mandatory (R1-10 delivers both; the rebuild is cheap).
- The learned reader's job is quantified: close the 0.67 → 0.94 (C1) / 0.49 → 0.94 (C2) selection gap while keeping the
  0.000 unrelated firing rate. The null decision must reject "other" records at sites 1–2, not only at site 3.
- Per-query fact selection held over all answer positions (R1-12) is required, not optional.
- A **non-learned control** falls out of this memo: v0 with stable observations (cap-off keys at write and read, everything
  else unchanged). It is the cheapest explanation of any Stage 4 gain and must be beaten by the learned reader. It joins
  the matched-update control (R1-15) as condition "v0-stable"; DEC-035.
- Cost model: the stable read adds one unedited pass per position; this is the "cached-observation variant" question
  (X0-06) — the write-time observation of a prefix can serve the read of the same prefix only within one query, so the
  extra pass is charged in every condition.

## 5. Gate

The Stage 0 gate (guide §0: "a written diagnosis that names the failure locus before any Stage 1 code is trained") is met:
the locus is observation instability first, record selection second; storage is exonerated. Stage 1 implementation
(R1-10 delivered; R1-11/12/13 next) proceeds. Codex counter-review: lane R1-X1.

## 6. Caveats

One stream, one seed and order, 100 zsRE development edits, banks far from eviction pressure (C1 362 of 6144 bytes-ceiling
slots per bank); the oracle is an upper bound with unavailable deployment information; the stable_rebuilt policy uses a
shadow key matrix and was never written into the cap (state hash asserted unchanged); the v2 zsRE calibration radii were
not re-tuned for cap-off keys, so the stable_rebuilt numbers understate what a re-calibrated fixed geometry could do — a
question for the v0-stable control, not for this memo.
