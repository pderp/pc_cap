# Ongoing work (the single current log; previous versions are dated under `docs/archive/`)

Rewritten 2026-09-11 06:30 EDT by the orchestrating session during the counter-review pause
(`docs/updated_plan6.md`). Previous version: `docs/archive/ongoing-2026-09-11-0620.md`. Rules §1 are
unchanged and restated in `CONTRIBUTING.md`: JAX only, sibling/FabricPC read-only, resources under
`assets/`, **no commits by agents** (the lead commits; the orchestrator commits only when the lead asks),
task records in `docs/tasks/<ID>.md`, claim rows with the status tool or a claim JSON, lease for any GPU
use > 60 s, placeholder modules are the lane's to replace, other existing files need an edit request.
Board: `docs/tasks/STATUS.md`.

**Codex is paused.** Nothing in §3 starts until the counter-reviews conclude and the lead writes the
decisions of `updated_plan6.md` §5. Until then the only permitted activity is reviewing (a
`docs/<reviewer>_review<N>.md` or a `logs/` report) — no code, no results.

## 1. State (2026-09-11 morning)

- **Freeze draft complete** (no pending inputs, schema-valid); the freeze and the S4-02 allowances are
  the lead's (D-A). Projection: 20.5 of 27.0 local GPU-h for zsRE 1000 / CounterFact 300 / grammar 10,000.
- **REG-02/03, S1-01, S5-01 done**: the regenerated ePC substrate is eligible; SB/SE-A/SE-E arms ready.
- **Grammar** (GRAM-01/02, DATA-06/07, S3-03 dev matrix, SD-20) provisional until PA-2 passes tonight.
- **P4 (S1-04) done** in the D.4 error space; **S7-prep partial** (harness + fixed inventory; CounterFact
  shared stratum short at 9 pairs; E.2 filter pass and checkpoint runs after S4-04). Orchestrator.
- **B4 (S2-05, Codex): PC-10 value parity fails** while outputs, NLL, keys, radii and labels match;
  diagnosis in `docs/baselines/grace_adapter.md`; SD-21 proposed (plan 6 §2.1); lead decision D-B.
- **Lane R (ENV-05, Codex) partial**: resolution verified, real install waits on D-F.
- **Lane V2 (Codex) in progress**: 150/150 synthetic S4 jobs and the nine CLI controls pass on the
  repaired tree; the expanded study waits on the review-tools v2 patch (D-F); three observations
  (V2-01…03) become orchestrator repairs.
- **GPU idle**; no chains armed; `results/.gpu_lease` free. Last commit `0f1f9d5` plus the
  orchestrator's own-work commit made during this pause.

## 2. Orchestrator lane (do not touch)

After the reviews: V2-01…03 repairs with synthetic negative controls (CPU) → E.2 filter pass over the S7
candidates (GPU, minutes, after the freeze) → freeze support and S4-02 → S4-03/04 execution as run owner
(lease queue, realization-major) → S4-05/06 as pairs complete → S5-02 → S7-01/02 on committed
checkpoints → S7-03 JS part → S8. Owned paths as before (`src/pccap/{distill,pc,harness,cap,analysis,
routers,transport,bases,fixtures,data}/`, `results/`, `manifests/`, `docs/decisions.md`,
`docs/spec_defects.md`, `docs/lead_queue.md`, `logs/`).

## 3. Lanes for Codex — proposed; pick one after the lead confirms direction

Ordered by value. Each is independent of §2 and of the others; none needs the GPU lease.

### Lane B4-S — the PC-10 sensitivity control (CPU, ≈ 2 h; decides SD-21)

Owned: `scripts/grace_sensitivity.py` (new), `results/S2/grace_jax/sensitivity.json`, a section in
`docs/baselines/grace_adapter.md` (yours), an addendum to `docs/tasks/S2-05.md`.
- Run the JAX adapter's value optimization against itself under a mathematically equal but numerically
  different computation on the same 20 cases: (i) initial value perturbed by 1e-7 (fp32 ulp scale);
  (ii) a different matmul association in the hook suffix (e.g. `(h @ W1) @ W2` vs `h @ (W1 @ W2)` where
  the source does one of them) or the batched vs unbatched path; keep Adam, lr, steps, seeds identical.
- Report per case and step (1, 10, 100): max |Δvalue|, loss-before-step difference, greedy/NLL agreement —
  the same columns as `trace_comparison.json`, so the two tables read side by side.
- Verdict rule, stated before running: if the same-framework perturbations produce value differences of
  the same order as the cross-framework ones (O(0.1)) with equal losses and outputs, the gap is a
  conditioning property of GRACE's optimization (flat valley, lr 1.0) and SD-21 option (b) is supported;
  if they stay ≤ 1e-3, the adapter differs and the diagnosis continues. No tolerance is widened; nothing
  is tuned to the reference.

### Lane V2 — finish the independent study (CPU; after D-F applies your patch)

Rerun `scripts/review_repairs_r2b_study.py` from a fresh fixture root; complete the remaining controls
you listed (valid and invalid frozen S5 authority, forced rerun with different learned state and preserved
external checkpoint bytes, two-experiment and unknown-experiment filtering, stage limits incl. missing
per-run allowance, source/evidence provenance); write `logs/review_repairs_r2b.md`. Record V2-01…03 as
findings with your evidence; the orchestrator repairs them (plan 6 §2.2) and you re-check.

### Lane R — ENV-05 real installation (CPU/network; after D-F)

Run the non-dry install into a fresh scratch destination, `pip check`, the CPU determinism report;
complete `docs/tasks/ENV-05.md`; the documentation patch is applied by the lead or by the orchestrator on
the lead's word.

### Lane X — counter-review of the orchestrator's pause work (read-only + new files)

Independent check of `src/pccap/analysis/s1_p4.py` and `s7_01.py` against PDF D.4 and D.9:
(i) recompute P4 on a fresh seed block (`--n 2048` on the CPU) and compare the overlap matrix and the
held-out/cross-capture contrast with `results/S1/P4_gram.json` (values within resampling noise, no
new insufficient-rank case); (ii) verify the S7 inventory's independence claims *without opening sealed
payloads*: every zsRE pair subject is absent from the two development pools, the S0 sample and the
sealed pools' subject lists (`assets/data/prepared/editing/*_eligible.jsonl` — subject field only), and
every CounterFact member is a development item or a reserved-subject sibling; (iii) note whether the
strata definitions match D.9's "shared-mechanism / independent-private / near-neighbour" reading.
Output `logs/review_p4_s7.md` only.

### Lane S3-01 — the full control-suite table (CPU, documentation; after D-B)

`docs/controls.md` completion: PC-1…PC-10 with test paths, last run, status (PC-10 per the D-B
outcome), the development run matrix references, and the "full before S7" items; `docs/tasks/S3-01.md`.
The orchestrator reviews and mirrors.

### Optional, only if S8-02's ablation list names them (not before the freeze)

CAP-09 difficulty weight (CPU); CAP-08 read variants R-h0/R-g/R-e (GPU short). Do not start on your own.

## 4. Interfaces and coordination

As in the archived version §4: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`,
`pccap.harness.arms.make_learner/router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`,
`pccap.data.tokenize`, `pccap.data.decode`, `pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`,
`pccap.fixtures.grammar_generator/grammar_model`, `pccap.data.grammar_streams`, and now
`pccap.analysis.s7_01` (`materialize`, `evaluation_set`, `reversal`, `damage_matrix`) and
`pccap.analysis.s1_p4` (`ErrorSampler`, `basis`, `overlap`). Questions for the orchestrator: a dated line
under "## Agent questions" in `docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors
completion records it finds — S2-05 and ENV-05 were mirrored in this pause).
