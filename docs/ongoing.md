# Ongoing work (the single current log; previous versions are dated under `docs/archive/`)

Rewritten 2026-09-11 06:55 EDT, updated 07:15 EDT (pause ended; commit `6d98f03`) by the orchestrating session for
the concurrent round of `docs/updated_plan7.md`. Previous version: `docs/archive/ongoing-2026-09-11-0630.md`. Rules §1 are
unchanged and restated in `CONTRIBUTING.md`: JAX only, sibling/FabricPC read-only, resources under
`assets/`, **no commits by agents** (the lead commits; the orchestrator commits only when the lead asks),
task records in `docs/tasks/<ID>.md`, claim rows with the status tool or a claim JSON, lease for any GPU
use > 60 s, placeholder modules are the lane's to replace, other existing files need an edit request.
Board: `docs/tasks/STATUS.md`.

**The pause is over.** Codex may start Lane B4-S, Lane V3 and Lane X now, in that order of value; Lane S3-01
after B4-S step 2. None of them waits on the lead's open decisions (D-A, D-C, D-D, D-G, D-H) or on the
orchestrator. The orchestrator's next GPU use (B4 profile, one confirm-mode smoke job against the real base, the
GPU test subset) comes after Lane B4-S lands and is announced in `docs/lead_queue.md`; short `-m gpu` tests by
either agent need no lease.

## 1. State (2026-09-11, 07:15 EDT)

- **D-B decided: (b)** — DEC-020 / SD-21. B4's PC-10 is output-level parity plus loss-trajectory values
  plus a same-framework sensitivity control. **D-F done** (commit `80ad746`): Codex's patches applied,
  V2 study complete (`logs/review_repairs_r2b.md`), ENV-05 done (real scratch install, 150/150 pins).
- **V2-01…05 repaired and re-checked** (07:05 EDT; `logs/review_repairs_r2c.md`, `results/V2/v3/`): frozen-identity
  check at stage entry with exit-2 refusals, exact experiment-id filters and no silent merges, S7-03 `--experiment-id`,
  inconsistent allowance rules refused, archived spending counted. Codex's Lane V3 confirms independently; the freeze
  request (D-A) follows.
- **07:20 EDT:** GPU window 2 done (46 GPU tests pass; the frozen-identity check verified on the real BP base,
  tokenizer, grammar weights and ePC checkpoint, negatives refused — `results/GPUWIN2/`). S7's E.2 filter pass done
  (`manifests/dev/s7_pairs_e2.json`: every stratum full except CounterFact shared at 9). Grammar cost measured on the
  GPU (0.085 s/sequence, `results/S2/grammar_timing.json`) → the projection now selects **zsRE 1000 / CounterFact 300 /
  grammar 256 per task** (26.3 of 27.0 h); the draft follows. **B4 is wired** into `harness.arms` (`GraceArm`,
  original-prompt key positions through the decoder and evaluator; GPU parity tests) — its availability in the freeze
  still waits on Lane B4-S (DEC-020). S4-02 allowance proposal and the freeze command are in `docs/lead_queue.md`.
- ePC substrate eligible; grammar provisional until tonight; P4 done; S7 harness and inventory fixed.
- **GPU idle**, lease free. Corrected B4 numbers: learned-value gaps 0.09–22.4 with 40/40 output/NLL
  agreement and loss trajectories within 3e-3 relative.

## 2. Orchestrator lane (do not touch)

(V2-01…05 repairs, B4 wiring, GPU window 2, E.2 pass, grammar pricing: done) → B4 profile (development, ledger deltas)
when Lane B4-S lands → freeze support (D-A: the lead's command is posted) →
S4-03/04 execution as run owner → S4-05/06 · S5-02 · E.2 filter pass + S7-01/02 · S7-03 · S8. Owned paths as
before (`src/pccap/{distill,pc,harness,cap,analysis,routers,transport,bases,fixtures,data}/`, `results/`
except lane-named subtrees, `manifests/`, `docs/decisions.md`, `docs/spec_defects.md`, `docs/lead_queue.md`,
`logs/` except lane reports).

## 3. Lanes for Codex (independent of §2 and of each other; none needs the GPU lease)

### Lane B4-S — S2-05 completion under DEC-020 (CPU; highest value; deadline 2026-09-12 12:00 EDT)

Owned: `src/pccap/baselines/{grace_jax,grace_parity,grace_adapter}.py` (the placeholder is now yours to
replace with a re-export of `GraceLearner`), `tests/baselines/test_grace_jax.py`,
`tests/controls/test_pc10_parity.py`, `scripts/grace_sensitivity.py` (new), `results/S2/grace_jax/`,
`docs/baselines/grace_adapter.md`, `docs/tasks/S2-05.md`.
1. **Sensitivity control** (state the verdict rule before running): the JAX adapter against itself on the
   20 cases under (i) a 1e-7 perturbation of the cold initial value and (ii) a mathematically equal but
   differently associated hook-suffix computation (or batched vs unbatched path); Adam, lr, steps, seeds
   identical. Report per case at steps 1/10/100: max |Δvalue|, loss difference (absolute and relative),
   greedy/NLL agreement — the same columns as `trace_comparison.json`. Verdict: value gaps of the same
   order as the cross-framework ones (up to O(10)) with equal outputs and losses ⇒ divergence class
   reproduced ⇒ the (b) label applies; gaps ≤ 1e-3 ⇒ the adapter differs, keep diagnosing, B4 stays
   unregistered.
2. **PC-10 in form (b)**: keys/radii/labels exact within the existing tolerances; greedy ids and NLL as
   now; values compared by loss trajectory at steps 1/10/100 with a stated tolerance justified from the
   sensitivity run (never widened to fit); the element-wise value max-abs stays in the result file as a
   reported, non-gating quantity; the sensitivity verdict recorded in `pc10.json`. Both isolated and
   sequential cases.
3. **Adapter surface for the harness**: `last_logits_batch(seqs, phase)` (vmapped forward with the
   codebook lookup), `export_state/import_state/state_hash/memory_bytes/base_checksum` as Lane F,
   the explicit original-prompt boundary for decoding documented (the orchestrator wires it in `harness.arms`).
4. Doc and task record updated with the DEC-020 label text.

### Lane V3 — independent re-check of the V2-01…05 repairs (CPU; open now — "repairs landed" is posted)

The orchestrator already reran your study driver against the repaired tree (`logs/review_repairs_r2c.md`,
`results/V2/v3/`) and, to do so, updated the driver's *expectations* (not its inputs) and made the synthetic freeze
bind the synthetic base/tokenizer identities; the pre-V3 driver is preserved at
`results/V2/review_repairs_r2b_study.pre-v3.py`. Your lane: rerun from a fresh fixture root, confirm or dispute each
row of the before/after table in that report, add the conflicting-outcome two-experiment control you proposed, and
write `logs/review_repairs_r2d.md`. If you disagree with any expectation change, say so there — the driver is yours.

### Lane X — counter-review of P4 and S7-prep (read-only + `logs/review_p4_s7.md`)

As in the archived version: recompute P4 on a fresh seed block (`--n 2048`, CPU) and compare with
`results/S1/P4_gram.json` within resampling noise; verify the S7 inventory's independence claims from
subject lists only (never opening sealed payloads); judge the strata against D.9's wording.

### Lane S3-01 — full control-suite table (CPU, documentation; after Lane B4-S step 2)

`docs/controls.md`: PC-1…PC-10 with test paths, last run, status (PC-10 in form (b) per DEC-020), the
development run matrix references, the "full before S7" items; `docs/tasks/S3-01.md`.

### Optional (not before the freeze; only if S8-02's ablation list names them)

CAP-09 difficulty weight (CPU); CAP-08 read variants (GPU short).

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
