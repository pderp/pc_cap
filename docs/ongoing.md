# Ongoing work (the single current log; previous versions are dated under `docs/archive/`)

Rewritten 2026-09-11 06:55 EDT, updated 2026-09-15 15:40 EDT (round 13 committed; round 14 lanes) by the orchestrating session for
the concurrent round of `docs/updated_plan7.md`. Previous version: `docs/archive/ongoing-2026-09-15-1540.md`. Rules §1 are
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
- **Round 13 committed by Codex** (`c238f02`): register policy v5 (4,218 MQuAKE subjects), protocol v4, dev-loader and
  selection-trace modules (orchestrator wires them), R1-65/66 review (collision rate 2.1–2.3 %), R1-68 integrity components
  (partial). Clean driver profile: 1,252 s per 300-edit cell; 1,000-edit cell ≈ 49–66 min.
- **Primary condition v5** (DEC-049/050; `primary_condition_v5.json`): question-null family seed 2, averaged checkpoints 150–300;
  mean RET-GS 0.803 (zsRE 0.98 / CounterFact 0.82 / MQuAKE 0.61), ES 1.00, LS ≥ 0.98, zsRE unseen 10 / 12 / 9 % at
  100 / 300 / 1,000, near-miss 100/100, revision 100/100, full-assay drift +0.0022 nats. Driver: 1,262 s per 300-edit
  cell (overhead = per-phase clone/restore ≈ 545 s + one-at-a-time drift 506 s); the incremental profile changes nothing.
- **DEC-048 (option C)**: true-fact query presentations are not counterfactual-edit exposure; MQuAKE capacity 4,218 vs
  4,050 demand; full scope stands. **Round 12 committed by Codex** (`cee3d79`): population memo, protocol v3, matrix v4,
  MQuAKE counter-review (notes corrected). Reader status: fixed-locality readers (R1-65) keep retention (MQuAKE 0.79,
  zsRE 0.98, CounterFact 0.86) but zsRE unseen false fires stay 30–52 % at 100 records; question-form nulls (R1-66)
  bring them to 5 % at a retention cost; a 35 % rate and the clean driver profile are running.
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

- **Round 16 committed** (`2e7ac38`, 2026-09-16): R1-X12 selection review (42 candidates, 15 admissible, unique winner;
  zsRE unseen 10/100, Wilson 95 % 5.5–17.4 %; occupancy flatness unproved because the outside sets differ), R1-68c
  instrumented driver with batched drift (owner re-profile running), R1-72 schedule scenarios (331–452 GPU h vs 306
  available), HT-1b v5 tail audit (v5 zsRE mean +0.0022 nats but max 8.7 nats and 17 positions > 0.1; CounterFact
  +0.006## 3. Lanes for Codex — round 18 (CPU; open now; posted 2026-09-16 13:15 EDT)

Round 17 is committed and mirrored (all lanes done; R1-74 / R1-75 patches landed). The κ pilot is running (chain H:
ordinary, κ 0.2 and κ 0.5 × 3 seeds evaluated by 13:05; κ 0.5 seed 2 and the clipped control follow; then the R1-68d
full profile). Priority order: HT-3d → R1-64c → R1-77 → R1-63d → HT-4c. Rules as before (new files only; CPU only;
edit requests as patches under `docs/tasks/`; tests under `tests/revision_v1/` must pass; no draw, seal, freeze,
launch or commit). Result files under `results/R1/` are the orchestrator's; read them, never write there.

### Lane HT-3d — κ pilot aggregation under the v3 manifest (CPU; new files; first)

Implement the aggregation rule of `manifests/revision_v1/kappa_pilot_v3.json` exactly, as
`scripts/ht3d_pilot_aggregate.py` + tests. Inputs per arm-seed run (`r1_50_stream_sel6_text_s{0,1,2}` = ordinary;
`ht3_{kappa02,kappa05,clip2}_s{0,1,2}`): retention `results/R1/stream_eval_<run>_stepavg_rare1_null0.5[@counterfact|@mquake].json`
(RET-GS at the averaged checkpoint); unseen `results/R1/endpoints/<run>_stepavg_rare1_n100_unseen_<ds>/summary.json`
(`false_fires` of 100); tail `results/R1/drift_assay_ht3_<run>_<ds>.positions.json` (cap-on and cap-off NLL matrices,
32 windows × 127 positions; positive harm = max(on − off, 0); ES95 with fractional boundary weights and maximum, as
HT-1). Outputs: per arm-seed-dataset table; per arm the 3-seed macro means with the seed-spread separation rule
(signed differences printed); the retention floor (ordinary macro mean − 0.02) and the unseen non-increase check per
dataset; the counter-review §4 decision rule verdict per coupled arm (declared secondary condition / null result), and
the §4 "What it is not" paragraph reproduced verbatim (DEC-054 framing binding). Missing runs are reported as
missing, never imputed or dropped silently; a `failure_receipt.json` in a run directory is reported as a charged
failure. JSON + Markdown; run it on the partial data now and re-run when the chain ends.

### Lane R1-64c — comparator recipes rebound to the R1-68d tree (CPU; new files)

The 16 R1-64b comparator recipes bind the pre-R1-74 code identity and the R1-64 driver. Rebuild them for the installed
tree (`51263d99…`) and the R1-68d driver's incremental profile if that driver serves every comparator adapter
(check; if an adapter needs the full profile or the old driver, say which and why, per condition). Deliver
`docs/tasks/R1-64c-<dataset>-<condition>.recipe.json` with inspection receipts (no model), and an ordered run list
with the expected checkpoint identities so the orchestrator can profile all eight conditions on zsRE and CounterFact
in one chain. MQuAKE comparator recipes wait for the R1-73 calibration run (orchestrator).

### Lane R1-77 — block-ordered confirmatory queue runner (CPU; new files + tests)

`scripts/r1_77_queue.py`: reads `run_matrix_v5.json`, orders cells by DEC-051 block and within-block order, and runs
them one at a time through the R1-68d driver from their recipes (resume from the last certified checkpoint on
restart; refuse on identity mismatch; per-cell cost ledger and receipts; MemAvailable guard; a `--dry-run` that
prints the queue and the DEC-052 complete-block / incomplete-cell inventory from what exists on disk; `--stop-after
<block>`; a status command that prints spent and projected hours against a ceiling). No confirmatory recipes exist
yet, so test it on TinyBase cells and on the existing development cells as a development queue. The orchestrator
executes it after the freeze.

### Lane R1-63d — freeze candidate v5 (CPU; new file)

Rebind the freeze candidate to the installed tree, matrix v5, protocol v5, primary v5, register v6, `kappa_pilot_v3`
and DEC-053 / DEC-054; print the open gates with what closes each (the September 20 cost admission, the R1-73
calibration, the comparator profiles, Q5 / Q10). Dry; no freeze.

### Lane HT-4c — claim ledger v3 (after HT-3d)

Update `docs/talk_claim_ledger_v2.md` → v3 (new file): the κ pilot rows filled from HT-3d with the DEC-054 framing,
the R1-68d cost rows, the DEC-053 locality rows (both conventions), the tail rows from HT-1b including the
CounterFact supplement, and the occupancy caveat (R1-X12 / R1-76). Every row bound to a file and hash.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
