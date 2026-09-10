# Updated plan 4 — after interim report 2 (2026-09-10, day 2 evening)

Delta over [updated_plan3.md](updated_plan3.md) (which stands where not restated). Triggered by Codex's
integration review ([logs/interim_report2.md](../logs/interim_report2.md)) and the orchestrator's
verification ([logs/review_interim_report2.md](../logs/review_interim_report2.md)). No threshold,
endpoint, arm, contrast or budget changes; the PDF remains the contract.

## 1. What changed in the assessment

- **Component-green ≠ pipeline-ready.** The confirmatory path (CLI → scheduler → stage → collectors →
  paired analysis) had four defects that no component test caught: a stale completion marker had already
  fired the post-REG chain; the confirm-mode CLI validated the wrong document and bypassed the access gate;
  run directories omitted the dataset (150 jobs → 75 paths); order truncation changed the item subset per
  order. All are repaired and tested on synthetic data (DEC-019, SD-19). Lesson written into the protocol:
  every stage that will run on sealed data gets a synthetic end-to-end test before it runs for real.
- **Cost accounting is now reconcilable** (ledger deltas per item and checkpoint), but every efficiency
  number produced before 2026-09-10 afternoon is provisional (learner cost records only).
- **REG-02 is healthy** (step ≈ 5,100 of 9,766 at writing; all stage boundaries matched the sibling's
  run; no holds; prompt KL ≤ 3e-5). ETA ≈ 19:40 EDT, then REG-03 → S1-01 → ePC rows automatically.
- **Lane D is unblocked**, **DATA-02a is done**, the grammar lanes have interface guidance.

## 2. Gate before the freeze (DEC-019) — all CPU unless marked

| item | owner | status |
| --- | --- | --- |
| Synthetic end-to-end CLI study (`tests/harness/test_confirm_cli.py`): denied access opens nothing; 150 unique run paths; hashes; rerun protection; selection rule; resource stop + ledger reconciliation | orchestrator | **done** |
| Post-REG chains re-armed on a terminal-state waiter, fail-fast | orchestrator | **done** |
| Freeze writer refuses pending inputs; SD/DEC copied faithfully; schema kind for the draft | orchestrator | **done** |
| Preflight validity gate; P1 non-finite rule; P1 complete-answer initially-correct check | orchestrator | gate done; complete-answer check with the post-REG P1 run (GPU) |
| Re-profile with per-item ledger deltas (fixed setup / immediate / rescoring separated; SD-3 full drift set priced) and re-run the projection | orchestrator | first GPU window after REG-03 (≈ 40 min) |
| GPU test subset incl. baseline-arm parity (blocked by REG-02's memory) | orchestrator | next pause window |
| B4 reference parity (Lane D) → S2-05 adapter + PC-10 (orchestrator) → B4 profile | codex → orchestrator | in progress / pending |
| Grammar generator + model code with the cap interface control (Lane G′); training after PA-2 (2026-09-11 23:59 ET) | codex | pending |
| Independent review of the synthetic evidence and of the repaired runner (Lane V) | codex | pending |
| Complete cost table (measured / assumed / missing per component, κ scenarios) | orchestrator | after the re-profile |
| Lead: freeze (`freeze --final --i-am-the-lead [--accept-unavailable …]`) | lead | after the rows above; grammar/B4 may be accepted as unavailable explicitly |

Reduced-programme rule (unchanged from D2 §5): if grammar or B4 are still missing at the freeze, they are
recorded `unavailable` in the manifest and the programme is labelled reduced; adding them later requires a
versioned protocol, never a silent extension of an open analysis.

## 3. Re-sequenced critical path

```
REG-02 (running) ─┬─ auto: REG-03 preflight → S1-01 P1 → ePC P2/P3/P5/P6 → S1 report → freeze draft
                   └─ auto: S5-01 prep (error-credit GPU test, ePC calibration, SB/SE-A/SE-E smoke)
GPU window 1 (after the chains): gpu tests · re-profile C0/C1/C2/CR(learned)/B0/B1/B3 with ledger deltas · projection
Lane D → S2-05 adapter/PC-10 → B4 profile (when parity cases exist)
Lane G′ → GRAM-02 training (after PA-2, pause window) → DATA-06/07 → S3-03 → grammar rows of the projection
Gate §2 green → lead freeze (CP-E) → S4-02 scope + run allowance → S4-03/04 execution (lease queue, realization-major)
S4-05/06 as pairs complete · S5-02 when eligible (S1-01) · S7-01/02 on committed checkpoints · S7-03 · S8
```

Grammar-specific engineering before S3-03/S4 grammar jobs (R2-09): the grammar base declares `bank_blocks`
and `d`; the S4 runner and scheduler get a base/tokenizer/record abstraction for grammar streams; the
projection's grammar term is priced from GRAM-02's measured s/sequence (8 tasks, joint reference).

## 4. Interpretation notes carried into the reports (R2-10)

- C0 is the last-depth-only control (bank 3, whole ceiling). Its higher zsRE RET-GS over C2 is an open
  hypothesis (rare early routes, rejected candidates, per-bank ceilings), not a depth effect; the item-level
  paired disagreement is the first test.
- Two CR policies exist and are always named: `CR(uniform)` (SD-11 profiling) and `CR(learned)`
  (DEC-018, confirmatory). On zsRE development, `CR(learned)` 0.38 ≥ C2 0.30 — the C2-vs-CR contrast is
  kept and a valid negative outcome is accepted.
- CounterFact's exact-key gate gives an observed development GS of zero (a floor for the primary endpoint
  there); reported as a limitation, not a reason to switch endpoints.
- GPT-2's near-empty zsRE baseline means immediate ES is mostly acquisition; three realizations remain
  three clusters.
- B1/B3 at DEC-017's rate are measured references, not validity gates.

## 5. Budget and clocks

Unchanged ceilings. REG charged to S6 by DEC-014 (REG-00/01 ledgered; REG-02 added at completion).
PA-2: 2026-09-11 23:59 ET. T-CP-E: re-dated to "after §2".
