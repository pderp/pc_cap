# Research freeze, 9 October 2026 17:00 EDT — handoff draft (dry run of 7 October)

Prepared by Capstan on 7 October 2026 (FIN-2, DEC-083). This is the document the lead reads and signs on 9 October. Every
item of `docs/freeze_checklist_20261009.md` was executed today except the signature; the signature block at the end is
blank. If anything in the record changes between now and 9 October, the dry run is repeated and this document is
regenerated with a new date. Paths are relative to `/home/derp/cap/pc_cap` unless they start with `assets/`.

## 1. Inventory of the closed experimental portfolio (DEC-083)

| study | planned | complete | not complete | authority |
|---|---:|---:|---|---|
| Stage-4 confirmatory matrix | 330 | 270 | 60 unrun by decision (DEC-074b: S1_literal CounterFact 15, optional extension 45); contrasts reported unavailable | DEC-071, DEC-074/074b |
| PC-v0 corrected credit (SE-E vs SE-A) | 60 | 60 | — | DEC-074 |
| PC-v0 controls: settling depth 1 / 32 | 12 / 12 | 12 / 12 | — | DEC-075 |
| PC-v0 control: random-direction credit | 12 | 1 pair (random cell stopped by rule at 993/1,000) | 11 not run; closed as informative | DEC-075, DEC-079 |
| PC-v0 control: compute-matched adjoint | 12 | 12 | budget offered, not consumed (weak by construction, stated) | DEC-075 |
| Fixed-v5 credit (default) + harm | 4 | 4 | table writer failed once; table regenerated from the unchanged report | DEC-074 |
| Fixed-v5 credit settings (k32, lr 0.05, lr 0.2) + harm | 12 | 12 | three first harm launches failed, reran; durations of the failures unreceipted | DEC-077 |
| AW-B bounded correction: calibration + evaluation | 16 configs + 30 cells | all | — | DEC-076/076a, DEC-078 |
| PC-trained reader (BP ×3, ePC ×3; 12 evaluations) | 12 | 12 | — | DEC-077 |
| Option R, realization 3 | 30 | 20 | 1 incomplete by ceiling (v0_stable zsRE o100), 9 v0_stable deferred | DEC-077, DEC-080 |
| Upper-layer interface 2×2 (6 readers, 24 evaluations) | 24 | 24 (6 shared PC-reader controls) | — | DEC-077 |
| 3,000-edit scaling | — | — | cut: population insufficient (HT-16) | DEC-077 |
| κ-pilot full readout | — | — | closed without execution (KP-1 no-go) | DEC-082 |

Last GPU step finished 2026-10-04 01:17 EDT (AW-L5 chain). No GPU process has run since; the GPU is idle. No fit was
started on or after 6 October.

## 2. Receipt closure

- Every completed cell above has its finish/cost receipt with status complete; partial and failed work keeps its own
  receipt (Option R cell `61eb6d08…` incomplete by ceiling, 8,002 s charged once; random-control run stopped by rule;
  the three failed fixed-v5 harm launches have logs but no duration receipts). Nothing was retried without a receipt;
  no nested cost is counted twice (FIN-1 accounting, `logs/additional_work/final-assembly-20261005/`).
- Post-halt compute by study, from 101 non-overlapping enclosing receipts (process-envelope seconds of GPU-bound
  processes; **lower bound**, see exception E1):

  | study group | process-hours |
  |---|---:|
  | PC-trained reader (profiles, 6 trainings, 12 evaluations) | 79.6 |
  | Option R (both session segments) | 19.6 |
  | PC-v0 default (60 cells + harm) | 14.3 |
  | AW-L new work (profile, dev evaluations, 3 trainings, 18 evaluations) | 9.7 |
  | Fixed-v5 settings (+ harm) | 5.9 |
  | AW-B evaluation | 5.9 |
  | AW-B calibration | 5.4 |
  | PC-v0 depth 32 / depth 1 / offered-budget / random | 3.8 / 2.7 / 2.5 / 1.5 |
  | Fixed-v5 default (+ harm) | 1.9 |
  | **total** | **152.7** |

- GPU occupancy over the same period, as the union of the 85 start/exit intervals in the owner's chain log
  (`logs/additional_work/PC-v0/chain.log`, 2026-09-26 23:48 → 2026-10-04 01:17): **136.0 hours** of a 169.5-hour span
  (80 %). The difference from 152.7 is the two-worker Option R sessions and profile/readout overlaps that the receipts
  count per process.

## 3. Final CPU refresh in dependency order (executed 7 October, 10:51–10:56 UTC)

`aw.refresh_reports --output logs/additional_work/reproductions/freeze-dryrun-20261007`: 16 of 16 steps complete in
279 s, zero GPU seconds, zero model calls; 198 output files hashed in `refresh.json`; inputs unchanged during the
refresh. Staged figures and deck under `assets/presentation-materials/reproductions/freeze-dryrun-20261007/`. The
staged outputs reproduce the canonical reports; the canonical paths below are the record.

| record | canonical path | last inputs |
|---|---|---|
| Stage-4 assembled report (+ triplet, comparators) | `docs/R1_stage4_report.md`, `_triplet.md`, `_comparators.md`; `logs/R1/reports/stage4-assembled/` | 270-cell halt; S4-LIM caveats (round 58) |
| Consolidated supplemental report | `docs/additional_work_report.md`; `logs/additional_work/final-assembly-20261005/` | FIN-1 (5 Oct) |
| PC-v0 / PC-v1 / controls / matched reports | `docs/additional_work/PC-v0_report.md`, `PC-v1_report.md`, `PC-controls_report.md`, `PC-matched-control_report.md` | complete 29 Sep – 1 Oct |
| AW-B report | `docs/additional_work/AW-B_report.md` | 1 Oct |
| PC-reader report (12/12) | `docs/additional_work/PC-reader_report.md`; `logs/additional_work/PC-reader/report-round63-final/` | 4 Oct |
| Option R report (realizations 0–3) | `docs/additional_work/R_report.md`; `logs/additional_work/R/report-round63-final/` | 4 Oct |
| Upper-layer 2×2 report | `docs/additional_work/AW-L_report.md`; `logs/additional_work/AW-L/report-round63-final/` | 4 Oct |
| HT-17 tail analysis | `docs/additional_work/HT-17_report.md`; `logs/additional_work/HT-17/snapshot-20261004-complete/` | 4 Oct (303 cells) |
| Tail figures (HT-13/15) | `assets/presentation-materials/tails_v1.md`, `figures/tails/`, `figures/tails_ht17/` | 27 Sep; 4 Oct |
| Claim ledger | `docs/talk_claim_ledger_v7.md` | round 63 |
| Reproduction guide | `docs/REPRODUCE_additional_work.md` | round 65 |

## 4. Audits (7 October)

- **X25** supplemental receipt-and-hash audit, rerun inside the refresh: **PASS, 25 groups, 6,221 unique files hashed**
  (`logs/additional_work/reproductions/freeze-dryrun-20261007/audit/X25/`).
- **X26** spoken-number inventory: rerun (`…/audit/X26/review.md`); no unmatched literal from an intermediate source;
  the known approximate phrasings ("roughly one-third"; rounded deficits) are listed as review items, as before.
- Stage-4 receipt audits X22/X23/X24 (PASS) unchanged since the halt.
- Test suite: 274 passed; ruff clean.

## 5. Deck archive (dry-run snapshot)

`assets/presentation-materials/deck_v3/freeze-dryrun-20261007/` with `MANIFEST.sha256` (45 files): the canonical
rehearsal pack (twelve slide drafts and SVGs, both timed scripts, Q&A, numbers sheet, backups), the short deck PDF of
4 Oct, the colleague long-talk PDF and its speaker notes of 4 Oct. The presentation is still being edited by the lead
with Capex (deck v4 long, slide 10, support-field explanations, uncommitted on 7 Oct); **the final archive is taken on
9 October after those edits are committed**, as `deck_v3/freeze-20261009/`. The freeze fixes the experimental evidence
and the claim ledger; slide wording may change until the talk provided every spoken number keeps its ledger source
(X26 is rerun on the final pack).

## 6. Disclosed exceptions register (for the lead's acceptance)

| id | exception | where recorded | proposed disposition |
|---|---|---|---|
| E1 | Three initial fixed-v5 harm launches (k32, lr 0.05, lr 0.2; 29 Sep) failed and were rerun; their failure logs exist but no duration receipts, so the 152.7 process-hour total is a lower bound | `logs/additional_work/PC-v1/harm-{k32,lr0.05,lr0.2}.log`; FIN-1 §"Measured post-halt compute" | accept as stated: total reported as a lower bound; the successful reruns are fully receipted |
| E2 | The AW-L5 chain's shell cost gate read 0.0 because the projection is an extensionless file; it did not bind. The projection held 17.98 process-hours (under the 40-h gate); measured new AW-L cost 9.7 process-hours | item 162/163; `logs/additional_work/round65-cost-gate.json` (retrospective check with `aw/cost_gate.py`) | accept: no decision depended on the gate; the defect and the fix are on record |
| E3 | Ceiling reconciliation. DEC-073 set a 150 GPU-hour stop ceiling for the supplemental portfolio (AW-B, AW-L, Option R) and DEC-077 reframed the whole post-halt programme as "≈ 160 wall-hours to October 6". Measured: 152.7 process-hours (receipt envelopes, lower bound) and 136.0 hours of GPU occupancy (union of logged intervals). The DEC-073 items alone (AW-B 11.3, AW-L 9.7, Option R 19.6) total 40.6 process-hours. The PC refocus and the reader study were authorised separately (DEC-074/075/077) | §2 above | the lead decides whether the 150-h ceiling applied to the DEC-073 items only (comfortably under) or to all post-halt work (136 h occupancy under; 152.7 process-hours over by 2.7 h on the envelope measure); Capstan's reading: the ceiling named the DEC-073 portfolio, and the binding constraint on the whole programme was the 6 October last-fits line, which was met |
| E4 | Option R: one v0_stable cell incomplete by ceiling (execution-path mismatch: scalar drift assay), nine v0_stable cells deferred; realization 3 supports the learned-vs-random contrast only; the t(3) sensitivity is labelled and unadjusted, no classifier reissued | DEC-080; `docs/additional_work/R_report.md`; `docs/tasks/R-2.md` | accept as stated |
| E5 | Random-direction control stopped by the historical compute allowance after 993/1,000 items (ES 0.003); eleven cells not run; reported as stopped by rule with partial metrics | DEC-079; `PC-controls_report.md` | accept as stated |
| E6 | Compute-matched control is weak by construction (budget offered, not consumed) | `PC-controls_report.md` | accept; the report says so |
| E7 | Stage-4: S1_literal CounterFact (15) and the optional extension (45) unrun; eight registered contrasts unavailable; the registered inference rests on three realizations (DEC-069) | DEC-074b; `docs/R1_stage4_report.md` | accept as stated |
| E8 | All 45 learned-reader cells fail the secondary mean-KL ≤ 0.001 benchmark (not a veto, DEC-064a) | Stage-4 report; HT-13/17 | accept; central to the talk's tail theme |
| E9 | Base is GPT-2 small (124M); transfer to production-scale models not established; most supplemental populations are exposed | S4-LIM caveat in every report | accept |
| E10 | Reporting resolver patch of 7 October (this dry run): after LINT-1's lint-only edit of `aw/scoring.py`, four report generators still checked live sources against the hashes recorded in the saved reports and failed; they now use the archive-aware resolver, with their exact prior bytes preserved in `docs/tasks/round66-source-archive/` (manifest keyed by path and hash). No report content changed; runtime code untouched | commit of 7 Oct; `aw/reporting_sources.py` | accept: reporting-only change, verified by the 274-test suite, the refresh and X25 |

## 7. Open items before 9 October

1. Lead and Capex commit the presentation edits in progress (deck v4 long, slide 10, support-field explanations).
2. Capstan reruns the dry run on 9 October morning (refresh, X25, X26 on the final rehearsal pack, deck archive
   `freeze-20261009/`) and regenerates this document with the final hashes.
3. Lead signs below.

## 8. What the lead signs

> I approve the scientific scope and wording of the frozen record as stated in `docs/R1_stage4_report.md`,
> `docs/additional_work_report.md` and `docs/talk_claim_ledger_v7.md`: active inference is a proposed policy loop;
> predictive-coding evidence includes its adverse and null findings and measured cost; tails are finite-range fits,
> not complexity classes or W(N); the base is GPT-2 small and populations are limited. I have reviewed the closed
> inventory (§1), the receipts and compute (§2), the refresh and audits (§3–4), and the deck archive (§5). I accept the
> disclosed exceptions E1–E10 with the following dispositions: ______________________________________________.
> Post-cutoff experiments belong to a later study.
>
> Signed: ______________________ (charlie derr)   Date/time: ______________________ (America/New_York)
>
> Witnessed by the orchestrator's record: Capstan, commit ______________ (pc_cap), ______________ (assets).
