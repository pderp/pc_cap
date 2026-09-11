# Ongoing work (the single current log; previous versions are dated under `docs/archive/`)

Rewritten 2026-09-11 06:55 EDT, updated 08:10 EDT (round 3 evaluated; round 4 lanes) by the orchestrating session for
the concurrent round of `docs/updated_plan7.md`. Previous version: `docs/archive/ongoing-2026-09-11-0715.md`. Rules §1 are
unchanged and restated in `CONTRIBUTING.md`: JAX only, sibling/FabricPC read-only, resources under
`assets/`, **no commits by agents** (the lead commits; the orchestrator commits only when the lead asks),
task records in `docs/tasks/<ID>.md`, claim rows with the status tool or a claim JSON, lease for any GPU
use > 60 s, placeholder modules are the lane's to replace, other existing files need an edit request.
Board: `docs/tasks/STATUS.md`.

**Round 3 is evaluated (08:10 EDT).** V3 confirmed the five repairs; Lane X's P4 reproduction holds and its S7
findings are repaired; B4-S ran the sensitivity control, which did not reproduce the divergence class, so B4 stays
unregistered (DEC-020) while Codex localizes the first cross-framework gradient difference. Codex's round-4 lanes are
in §3 (B4-D in progress; S3-01, V4, P open). The lead has accepted the defaults for D-A/C/D/G/H (DEC-021…024); the
freeze command is posted in `docs/lead_queue.md` and waits only on the B4 deadline (2026-09-12 12:00 EDT). The orchestrator's next GPU use (B4 profile, one confirm-mode smoke job against the real base, the
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

## 3. Lanes for Codex — round 4 (independent of §2 and of each other; none needs the GPU lease)

### Lane B4-D — localize the first cross-framework gradient difference (CPU; in progress; deadline 2026-09-12 12:00 EDT)

Owned: the B4 files (`src/pccap/baselines/{grace_jax,grace_batch,grace_parity,grace_adapter}.py`, `tests/baselines/`,
`scripts/grace_*.py`, `results/S2/grace_jax/`, `docs/baselines/grace_adapter.md`, `docs/tasks/S2-05.md`) and a new
`logs/grace_gradient_localization.md`. Fixed inputs, vector-Jacobian products compared at successive boundaries (hook
suffix → GELU → residual add → later blocks → `ln_f` → head → loss reduction), masks and prompt indexing checked alongside
kernels. Known facts to rule in or out first: both sides use `gelu_new` and ε = 1e-5 (checked); the JAX side runs at
`highest` matmul precision; the reference runs PyTorch-CPU fp32 — a 1e-4 relative first-gradient gap is large for that
pairing (SD-14's logit gap was ≤ 1e-3 absolute), so a real difference is plausible. If a genuine implementation
difference is found and fixed in your files, rerun PC-10 (form (b) test rewrite) and the sensitivity control from the
preregistered policy; if none is found by the deadline, write that finding and B4 is accepted unavailable at the freeze.

### Lane S3-01 — the full control-suite table (CPU, documentation; open now)

`docs/controls.md` with PC-1…PC-10, test paths, last run, status; the development run matrix references; the "full
before S7" items; `docs/tasks/S3-01.md`. PC-10 is recorded exactly as it stands (output-level agreement, element-wise
value parity failed, sensitivity prerequisite unmet, B4 unregistered) — an accurate table, not a passing one. The
orchestrator reviews and mirrors the board row.

### Lane V4 — re-check of the S7 repairs (CPU; open now)

Rerun `scripts/review_s7_inventory.py` (your counterexamples are now regressions in `tests/analysis/test_s7_01.py`)
against the repaired `s7_01` and the rebuilt inventory (grammar seed block 5,000,000+, `strata_qualification` text);
confirm findings 1–3 closed and the E.2 selection regenerated consistently (sha in both files); write
`logs/review_p4_s7_r2.md`. New files only.

### Lane P — reproduction pre-audit (CPU; optional, after the above)

Run every CPU command in `docs/REPRODUCE.md` from a fresh shell in the recreated ENV-05 environment
(`assets/envs/venv-check-plan6-df`), record which succeed, which need the GPU, and which are stale (S8-01 will repeat
this on the final tree); `logs/reproduce_preaudit.md`.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
