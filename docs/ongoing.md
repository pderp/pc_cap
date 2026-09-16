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
  +0.006## 3. Lanes for Codex — round 17 (CPU; open now; posted 2026-09-16 08:05 EDT)

Round 16 is committed (`2e7ac38`) and mirrored (all eight lanes done). The R1-68c re-profile is running on the GPU
(orchestrator); R1-64b comparator profiles and the R1-73 calibration run follow it. Priority order:
R1-68d → R1-74 → R1-75 → R1-40c → R1-49e → R1-76. Rules as before (new files only; CPU only; edit requests as patches under
`docs/tasks/`; tests under `tests/revision_v1/` must pass; no draw, seal, freeze, launch or commit).

### Lane R1-68d — identity verification once per checkpoint, not once per phase (first; your own driver file)

The R1-68c incremental re-profile (notes §"R1-68c re-profile") measured 837 s for the 300-edit zsRE v5 cell, of which
534 s is `identity_verification_seconds`: 0.87 s of `adapter.identity()` in each of the 600 edit / immediate phases,
re-hashing the base weights, reader parameters and installed inputs; model operation is 279 s and batched drift is
83 s (was 506). A 1,000-edit cell therefore spends ≈ 29 min in identity checks against ≈ 15–17 min of model time.
Change `scripts/r1_68c_dev_cell.py` (your new file; permission granted for this one file and its tests) so that the
full immutable-identity rehash runs at attempt start, at every checkpoint before its receipt, on resume and at
completion, while every phase keeps a cheap check — e.g. object identity / a small fingerprint of the parameter
containers held in memory, or the existing `state_hash` for the mutable state — recorded per phase as
`identity_check_seconds` and `identity_check_kind`. Any mismatch at a checkpoint still aborts without a receipt. Rebuild
the two v5 recipes (`R1-68d-zsre-v5-{full,incremental}.recipe.json`) since the driver source is recipe-bound, and land
the R1-74 scoring change in the same rebinding. TinyBase tests: timing fields present, identical results and checkpoint
chain to R1-68c, abort on a checkpoint identity mismatch. The orchestrator re-profiles on the real base immediately.

### Lane R1-74 — locality / near-miss scoring under DEC-053 (edit request; with R1-68d)

DEC-053 binds bounded text equality as the primary locality and near-miss convention: a pair is preserved when the
cap-on and cap-off 32-token greedy continuations are identical, terminated or not. The driver's `_Challenges.near_miss`
and `locality` in `src/pccap/revision_v1/stage4_assays.py` currently require termination as well, which on CounterFact
turns 13/50 identical truncated locality pairs and 37/100 near-miss pairs into failures (v5 CounterFact development
cell, `results/R1/stage4_dev_cells/R1_learned_ff-counterfact-development-source-bc285b69…`). Deliver an edit request
(patch, new file under `docs/tasks/`) that makes `preserved` the bounded-equality verdict and adds
`preserved_terminated` (the current rule) plus `truncated_pair` / per-side truncation flags to every row and both
counts to the checkpoint summaries; the stored rows already carry both generations, so a rescoring helper over
existing checkpoint files (new script) should reproduce 49/50 and 100/100 on that cell and 50/50 / 100/100 on the
zsRE cells. Because every src edit invalidates the identity-bound recipes, land it together with the R1-68c rebinding
step so the recipes are rebuilt once. Tests: TinyBase, both conventions.

### Lane R1-75 — stage-4 analysis tree v1 over cell directories (CPU; new files)

The confirmatory matrix will be a set of driver cell directories (`results/R1/stage4_dev_cells/<cell>/attempt-*/`
today; the confirmatory root will differ only by path) with `checkpoint-{100,300,1000}.json`, receipts, `phases/` and
`result.json`. Build `src/pccap/revision_v1/analysis_stage4_v1.py` (or extend under a new module name; the existing
`analysis_stage4.py` is Codex's R1-57 adapter and may be reused, not edited) plus `scripts/r1_75_analyze_cells.py` that:
(a) inventories cells by identity (condition, dataset, realization, order, checkpoint) against a matrix file and
reports complete blocks and the explicit incomplete-cell list in the DEC-051 block order (DEC-052 reporting);
(b) computes per cell and checkpoint ES, RET-GS, LS under both conventions (DEC-053 primary = bounded text equality;
termination-qualified and truncation counts alongside), unseen false-fire rate with Wilson intervals, near-miss and
revision counts, drift mean and tail (max, count > 0.1 nats, expected shortfall over the top 1 %) from the stored rows;
(c) forms the pre-registered paired contrasts against the controls with the DEC-033 margins (RET-GS +0.05, ES −0.02,
LS −0.01) per dataset, with the multiplicity structure of protocol v4 §U12, missing pairs never imputed;
(d) writes one JSON and one Markdown table per matrix, reproducible from the cell files alone. Validate on the
existing v5 zsRE and CounterFact development cells (expected: CounterFact LS 49/50 bounded / 36/50 terminated,
near-miss 100/100 / 63/100) and on TinyBase cells from the driver tests. Done-when: tests pass; the two development
cells reproduce the numbers in `docs/R1_stage2_notes.md`.

### Lane R1-40c — successor run matrix v5 and execution binding (CPU; new files)

Freeze gate U17: matrix v4 predates primary v5. Write `manifests/revision_v1/run_matrix_v5.json` and its generator:
360 core cells (8 conditions × 3 datasets × 3 realizations × 5 orders; checkpoints 100/300/1,000) plus the 45-cell
no-gate extension, each cell with a stable identity (condition, dataset, realization, order), the recipe family it
is built from (R1-64 / R1-64b / R1-73-calibrated for the v0-style MQuAKE cells), its DEC-051 block number and
within-block order, and a placeholder for the measured ceiling. Include the queue/retry/resume rules the driver
already implements (attempt directories, checkpoint resume, refusal on identity mismatch) as explicit fields, and a
CPU validator that checks the matrix against the freeze candidate's bindings. No costs are admitted here; the
orchestrator fills the ceilings after the September 20 re-measurement.

### Lane R1-49e — protocol draft v5 (CPU; new file)

`docs/R1_stage4_protocol_draft_v5.md`: v4 with DEC-050 (selection rule), DEC-051 (block order), DEC-052 (feasibility
and incomplete reporting), DEC-053 (LS / near-miss convention: bounded text equality primary, termination-qualified and
truncation alongside) written into §6 and the U10 / U13 / U14 gates; the unseen, revision and scale decision rules
stated as explicit inequalities with their denominators (U14); the occupancy caveat from R1-X12 (outside populations
differ across 100 / 300 / 1,000) stated where unseen rates are compared; and a change log against v4. Do not resolve
open lead items (Q4, Q5); mark them.

### Lane R1-76 — unseen occupancy with a common outside population, and the MQuAKE gap (CPU; new files + memo)

R1-X12 found that the zsRE 100 / 300 / 1,000-record unseen rates use different outside sets, so flatness is unproved;
and the MQuAKE 300 / 1,000 points cannot be run (no reader-unseen filler beyond the 500-item pool). Deliver
(a) `scripts/r1_76_unseen_common.py`: a variant of `r1_44_unseen_run.py` (new file; the old runner is untouched) that
fixes one outside set of 100 prompts per dataset, disjoint from every filler at the largest occupancy, and evaluates
it after 100, 300 and 1,000 records in one run so the three rates share a population; CPU/TinyBase tests;
(b) a short memo `docs/tasks/R1-76-mquake-occupancy.md` on where a reader-unseen MQuAKE filler population could come
from without touching the confirmatory reservation (the 4,218-subject register-v6 clearance leaves ≈ 168 nominal
slack; the 6,043-item pool minus reservations; or none) with the exposure consequences of each, for the lead
(question Q10 in `docs/lead_queue.md`, which the orchestrator posts). No execution.

cs/tasks/`) that makes `preserved` the bounded-equality verdict and adds
`preserved_terminated` (the current rule) plus `truncated_pair` / per-side truncation flags to every row and both
counts to the checkpoint summaries; the stored rows already carry both generations, so a rescoring helper over
existing checkpoint files (new script) should reproduce 49/50 and 100/100 on that cell and 50/50 / 100/100 on the
zsRE cells. Because every src edit invalidates the identity-bound recipes, land it together with the R1-68c rebinding
step so the recipes are rebuilt once. Tests: TinyBase, both conventions.

### Lane R1-63c — freeze candidate v4 (after R1-X12)

Rebind the freeze candidate to primary_condition_v5, register v6, matrix v4 and the selection manifest; print the open gates.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
