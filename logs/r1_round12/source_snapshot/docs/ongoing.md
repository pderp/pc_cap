# Ongoing work (the single current log; previous versions are dated under `docs/archive/`)

Rewritten 2026-09-11 06:55 EDT, updated 2026-09-15 01:00 EDT (round 11 committed; round 12 lanes) by the orchestrating session for
the concurrent round of `docs/updated_plan7.md`. Previous version: `docs/archive/ongoing-2026-09-15-0100.md`. Rules §1 are
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

**Post-freeze rule for every agent (from the moment `manifests/frozen.json` exists).** The freeze binds the hash of the
whole installed `src/pccap` tree; every confirm-mode job compares the tree at start and refuses on any difference (exit 2,
the queue stops). Therefore: no edits under `src/pccap/` after the freeze — not even in your own lane's files
(`src/pccap/baselines/grace_*.py` included). Put B4-D diagnostics and fixes in new files under `scripts/`, `logs/`,
`results/` or `docs/`, or as a proposed patch under `docs/tasks/`; a fix that must land in `src/pccap` is applied only with
a versioned manifest and `--allow-code-drift` recorded by the orchestrator (plan 4 §2). Tests under `tests/` and everything
outside `src/pccap` are unaffected.

**(17:56 EDT) The hold on `src/pccap/` is lifted: the v3 grammar rerun is finished and no confirm-mode job remains. New
modules go under `src/pccap/revision_v1/` as planned; anything drafted under `revision_v1_staging/` can move in.**

## 1. State (2026-09-14, 17:20 EDT)

- **v0 closed** (close-out identity `cb04d5e`); the lead's T4 review of the report/memo is still outstanding.
- **Revision v1, Stage 2 is done on the development side.** The learned reader (tied cosine + pairwise null + lexical
  overlap, stable observations, per-position deltas) with ordinary-text null training is reference condition v2; with the
  R1-56 rare-token overlap gate it is the proposed v3 (DEC-043). Development streams, three seeds: zsRE RET-GS 0.96–0.98,
  CounterFact 0.715–0.85, ES / RET-ES / LS 1.00; drift 0.000 / +0.012 nats; near-miss 100/100, revision 100/100; unseen
  edit-prompt false fires zsRE 10–11 % at 1,000 records (45 % without the gate), CounterFact 0 %. Report:
  `docs/R1_stage2_report.md`; running log `docs/R1_stage2_notes.md`; identities `manifests/revision_v1/primary_condition_v{1,2,3}.json`.
- **Costs measured on the real base** (R1-55, `results/R1/p1_profile/`): 1,000 records use 51–74 % of the state
  ceiling with exact restore; edit 0.07–0.13 s; query 10–15 ms; a full 1,000-edit cell with every endpoint at three
  checkpoints ≈ 1,150 s. Codex's 240-cell matrix v3 ≈ 92 h against the 15 h envelope; the lead keeps the full scope (DEC-044);
  ceilings will be set from the measured components.
- **Round 11 committed** (`8f82316`): self-contained MQuAKE slices (train 500 / dev 100, v3), development payload builder and
  execution mode for the cell driver (materialized base copy, checkpoint-identity helper), exposure trace audit (no
  certified releases; MQuAKE ≤ 2,829 subjects even if every review candidate cleared), freeze candidate v1 (dry).
- **Round 10 committed** (`3e8a980`): register v4 + MQuAKE exposure supplement, composition endpoint module, Stage 4 cell
  driver with all comparator adapters, three-dataset analysis. MQuAKE capacity deficit found (2,100 distinct candidate
  subjects vs 4,050 needed under conservative reservations) → R1-D4b.
- **MQuAKE reader**: proposed primary v4 (three pools; `primary_condition_v4.json`): zsRE 0.95–0.98, CounterFact 0.76–0.83,
  MQuAKE 0.56–0.79 (seed-sensitive); DEC-046/047 proposed defaults.
- **Round 9 committed by Codex** (`678c703`): analysis adapter (R1-57), draw recipe dry-run (R1-58), protocol v2 (R1-59, 360 cells),
  counter-review (R1-X8; cache repair applied), MQuAKE preparation (R1-D4: 6,043 items, composition inventory).
- **Round 8 committed** (`c401f55`): Stage 4 protocol draft (R1-49, gates U01–U18), frozen register binding
  (R1-D1f, `exclusions_frozen_v3.json`), ordinary-text null spec (R1-50b), R1-24 review (R1-X7; qualifications applied
  to the notes).
- **DEC-045**: MQuAKE-CF is the third dataset (`assets/data/raw/mquake/`); CounterFact stays (which needs the DEC-042
  exception). DEC-043 accepted, DEC-044 keeps the full matrix (now 360 cells). Then the freeze (R1-41). No draw, seal or launch before those.
- Rules unchanged (§ top); Codex: new files only, CPU only, no sealed payloads, no real-base execution; edit requests
  as patches under `docs/tasks/`. Tests under `tests/revision_v1/` (CPU) must pass.

## 2. Orchestrator lane (do not touch)

v0 close-out (tonight) → R1-01/02/03 diagnostics (GPU, ≈ 2 h) → `docs/R1_diagnosis.md` → Stage 1 core modules
(`revision_v1/{contracts,observations,memory,reader,controller,adapt,evaluate}.py`) with the gates → Stage 2 reference and
surrogates → Stage 4 runs and the revision freeze support. Owned: `src/pccap/revision_v1/` except the files named in §3,
`results/R1/`, `manifests/revision_v1/`, the registers, `docs/lead_queue.md`.

## 3. Lanes for Codex — round 12 (CPU; open now)

Round 11 is committed (`8f82316`) and mirrored. The orchestrator is now retraining on the self-contained MQuAKE
slices (v3) and validating/profiling the development cell driver on the real base. Rules as before.

### Lane R1-D7 — MQuAKE population options memo (for the lead's decision)

`docs/tasks/R1-D7.md` + a count script: the lead must choose how MQuAKE reaches a confirmatory population. Lay out,
with exact counts from the register v4 supplements and the R1-X9 audit, the options and what each requires: (a) the
conservative cumulative reading (2,100 subjects) with a MQuAKE-specific scope amendment — how many realizations ×
edits fit (e.g. 2 × 1,000, or 3 × 650) and the consequence for the paired analysis; (b) the executed-only reading
(≤ 2,829 with every review candidate cleared) — what remains to clear, per subject class; (c) a policy reading in
which a locality/unrelated presentation of a subject's TRUE fact during reader training or development evaluation is
not exposure for a later COUNTERFACTUAL edit of that subject (the prospective 4,818 figure) — state precisely what the
reader saw and did not see, and what a reviewer could object to; (d) an additional MQuAKE-like source (MQuAKE-T, 1,825
temporal instances, is on disk under `assets/data/raw/mquake/`; say whether its items are admissible as counterfactual
edits or only as a separate population). Recommend one with a default. No draw.

### Lane R1-49c — Stage 4 protocol draft v3

`docs/R1_stage4_protocol_draft_v3.md`: incorporate DEC-043–047 (gate, full scope, MQuAKE, DEC-046 slices, S1_LM at
lr 1e-8), primary condition v4 and the v3 fallback, the composition floor (R1-60: base 0/897 — composition stays
descriptive), the MQuAKE capacity question (reference R1-D7's options; do not decide), the register v4 + supplements,
and placeholders that the orchestrator's real-base driver profile will fill (per-cell wall time per condition and
dataset, checkpoint costs, watchdog ceilings). Update U01–U18 statuses; keep the 360-cell scope.

### Lane R1-40d — run matrix v4 (three datasets)

A new builder `scripts/r1_40d_matrix.py` + tests producing `manifests/revision_v1/run_matrix_draft_v4.json`: 8
conditions × 3 datasets × 3 realizations × 5 orders (360 cells) plus the declared 45-cell v2 extension as a separate
block; checkpoints 100/300/1,000; every cell bound to condition identities from `primary_condition_v4.json` (v3 for the
no-gate comparison), the S1 bases (`r1_24_control_v3`, `r1_24_control_lm_v3_lr1e-8`), and per-cell ceiling fields left
null with a named source (`results/R1/stage4_dev_cells/<profile tag>/`) that the orchestrator will fill; refuse to
build if any identity file is missing. Launch flags false.

### Lane R1-X10 — counter-review of the orchestrator's MQuAKE and composition work

Review `scripts/r1_d5_mquake_teacher.py`, `scripts/r1_d6_mquake_split.py`, `scripts/r1_60_composition_run.py`, the
`--dev-manifest` path in `scripts/r1_13_stream_eval.py`, the lex_idf feature (`reader.idf_weights`,
`learner._lex_weights`) and the notes sections "MQuAKE on the real base", "R1-57c result", "R1-60 composition
endpoint" against the result files. Questions: are the split's exposure claims consistent with the supplements; is
the composition floor claim (base 0/897) sound and correctly denominated; does the lex_idf training path compute
weights over the same population at training and deployment; is anything in `primary_condition_v4.json` stated
beyond its evidence. Output `logs/review_r1_mquake.md` with edit requests.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
