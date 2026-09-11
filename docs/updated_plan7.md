# Updated plan 7 — 2026-09-11, day 3 (06:50 EDT), start of the next concurrent round

Delta over [updated_plan6.md](updated_plan6.md) (which stands where not restated). Inputs since plan 6:
the lead's decision D-B = (b) (DEC-020, SD-21) and D-F executed; Codex's D-F execution and review
(`docs/updated_plan6_review.md`), the completed independent study (`logs/review_repairs_r2b.md`, V2-01…05),
the real ENV-05 recreation (`docs/tasks/ENV-05.md`, done), and the orchestrator's own commit `69acace`
(P4, S7-prep, plan 6). `docs/derp_review3.md` is still the title line only. No threshold, endpoint,
arm, contrast or budget changes.

## 1. Corrections to plan 6 (accepted from Codex's review)

1. **B4 value gap magnitude.** Plan 6 quoted case 0 (0.35). Over the 20 isolated cases the learned-value
   max-abs gap ranges 0.09–**22.4** (`results/S2/grace_jax/pc10.json`), and the loss trajectories agree to
   ≤ 3e-3 *relative* (not 1e-5). The conclusion is unchanged — outputs, NLL, keys, radii and labels match at
   40/40 while element-wise values do not — but the numbers in SD-21 are the corrected ones.
2. **Cause narrowed, not proved.** The fp32-sensitivity explanation is supported (exact init, fixed-gradient
   Adam replay to 3e-7) but not established; a coexisting adapter difference is not excluded. DEC-020
   therefore makes the same-framework sensitivity control a *condition* of the (b) label, not a formality.
3. **"Ready for confirmation" was premature.** Lane V2 measured five defects on the confirmatory path
   (§2). They are repaired and independently re-checked before the freeze request stands.

## 2. Repairs before the freeze (orchestrator; CPU; today)

| id | measured defect | repair | control |
| --- | --- | --- | --- |
| V2-01 | Inconsistent frozen BP digest / tokenizer hash accepted (exit 0) | at confirm-mode stage entry compare the loaded base's parameter digest and the tokenizer file hash with the frozen manifest; refuse with exit 2 before any edit or evaluation | the two negative probes, unchanged |
| V2-02 | Runs with no `experiment_id` match a specific filter | in `s4_05.discover`, `s4_06.collect_rows`, `s7_03.load_runs`: a specific filter requires an exact id; unknown-identity runs are listed in a diagnostic and excluded | the legacy-run probe (one run / eight rows) |
| V2-03 | S7-03 CLI has no experiment filter; unfiltered loading collapses two experiments into one cell | `--experiment-id` on the S7-03 and S4-05 CLIs; without it, more than one id in the discovered runs is an error, never a silent replacement | the two-experiment probe |
| V2-04 | `stage_allowance_seconds` finite with `run_allowance_seconds = None` labelled enforced, no run limit applied | refuse the inconsistent configuration at admission (exit 2) unless the stage rule derives the run allowance from the remaining stage budget explicitly (recorded in the run config) | the 0.01-second probe |
| V2-05 | Archived (forced) attempts excluded from the stage spending total | spending counts every attempt's ledger, superseded or not; analysis still excludes superseded results | the two-attempt fixture (14.4 vs 7.2 synthetic seconds) |
| (V2 note) | S5 missing-calibration / checkpoint-hash mismatch exits 1 (`correctness_failure`) not 2 | classify as preflight refusal (exit 2) — same stop point, correct code | existing S5 probes |

Then Codex's Lane V3 re-runs the study driver with the unchanged negative inputs and writes
`logs/review_repairs_r2c.md`. The freeze request to the lead stands only after V3 is green.

## 3. B4 under DEC-020 — what lands where

- **Codex (Lane B4-S, owns the B4 files):** `scripts/grace_sensitivity.py` and `results/S2/grace_jax/sensitivity.json`
  (verdict rule stated before running); `tests/controls/test_pc10_parity.py` rewritten to form (b);
  `pccap.baselines.grace_adapter` replaced by the real adapter (re-export of `grace_jax.GraceLearner`);
  `last_logits_batch(seqs, phase)` for the batched evaluator; the adapter document updated with the
  label text. Deadline for the freeze: **2026-09-12 12:00 EDT**.
- **Orchestrator:** registration of B4 in `harness.arms` (interface as Lane F), the B4 profile
  (development, GPU short, ledger deltas), the projection rerun with a measured B4 row, and the manifest
  label. If Codex's lane is not green by the deadline, the freeze goes ahead with B4 `unavailable`
  (`--accept-unavailable B4`) and a later addition needs a versioned protocol (plan 4 §2 rule).

## 4. Sequence for this round

```
orchestrator: V2-01..05 repairs + controls (CPU, today) ──► Codex V3 re-check ──► freeze request stands (D-A)
Codex: B4-S sensitivity + PC-10 form (b) + adapter/batch ──► orchestrator: B4 registration + profile + projection
Codex: Lane X counter-review of P4/S7 (read-only + logs/)
PA-2 passes tonight ──► grammar promoted (D-E default)
lead: freeze + S4-02 allowances ──► S4-03/04 execution (lease, realization-major; ≈ 20.5 accelerator h + B4)
──► S4-05/06 · S5-02 · E.2 filter pass + S7-01/02 · S7-03 · S8 · T4
```

Codex's Lane S3-01 (the full control-suite table) starts once the PC-10 form (b) test is in.

## 5. Decisions — state after this exchange

| # | decision | state |
| --- | --- | --- |
| D-A | freeze + S4-02 allowances | open; requested only after V3 |
| D-B | B4 parity form | **decided: (b)** — DEC-020, SD-21 |
| D-C | `pytest-cov` in the venv | open (default: test counts) |
| D-D | S6 closed for the month | open (default: closed) |
| D-E | PA-2 promotion | passes automatically tonight 23:59 ET |
| D-F | Codex's patches, ENV-05 doc, real install | **done** (commit `80ad746`) |
| D-G | S7 CounterFact shared stratum short | open (default: reported short) |
| D-H | S1 report accepted | open |

## 6. Board after this exchange

ENV-05 done (Codex). S2-05 in progress (Codex, under DEC-020). S1-04 done, S7-01 partial (orchestrator).
61 done, 8 partial, 5 ready, 14 pending of 89 rows plus the ENV-05 row.
