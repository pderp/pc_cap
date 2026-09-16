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
  +0.006## 3. Lanes for Codex — round 19 (CPU; open now; posted 2026-09-16 15:05 EDT)

Round 18 is committed and mirrored. The κ pilot finishes ≈ 15:10 EDT; chain I then runs the 16 comparator profiles
(R1-64c order) and the R1-73 MQuAKE calibration (≈ 3–4 h). Priority order: R1-77b → R1-58c → R1-49f → HT-3e → R1-73b.
Rules as before (new files only; CPU only; edit requests as patches; tests must pass; no draw, seal, freeze, launch,
commit). `results/R1/` is the orchestrator's: read, never write.

### Lane R1-77b — sealed confirmation backend for the queue (CPU; new files + tests; first)

Your R1-77 handoff lists what the queue lacks to run confirmatory cells. Build it as a new module
`scripts/r1_77b_sealed_backend.py` (+ tests): the sealed admission loader path (never a development loader), final
protocol / reservation / freeze identity checks, the R1-68d boundary-identity policy and read-only phase checks kept,
full failure-cost accounting, the explicit metadata-inspection and execution interface the queue binds by module hash,
and synthetic TinyBase sealed fixtures in an isolated test root exercising every case in your list (resume, wrong
identities, torn journals, duplicate launch lock, October 9 stop, partial blocks, analysis-population satisfaction).
Then deliver the queue's non-development dispatch as an edit request (patch) for `scripts/r1_77_queue.py`; the
orchestrator applies it. No real sealed payload is read.

### Lane R1-58c — draw and seal plan v2 (CPU; dry; new files)

The lead performs the draw, seal and freeze. Prepare the exact sequence as a checklist with commands and expected
receipts: register v6 clearance (alias / context / role; abort rules; DEC-048 option C reading), the three-dataset draw
under matrix v5 and protocol v5 populations (3 realizations × 1,000 edits + outside + near + neighbour + revision
per dataset), the seal (payload hashes, reservation identities), and the freeze candidate v5 → frozen manifest step,
each as a dry-run command that prints what it would write and refuses on any open gate. Include the September 20
admission inputs (cell ceilings from chain I) as named placeholders.

### Lane R1-49f — the remaining protocol bindings as lead questions (CPU; new file)

Gates U12 (contrasts / multiplicity), U13 (classifier / fidelity inequalities) and U14 (secondary thresholds: unseen,
revision, scale) still need lead decisions. Write `docs/tasks/R1-49f-lead-bindings.md`: for each, the concrete
proposal with its default, the alternatives, what changes downstream, and the exact protocol v5 text to insert;
the orchestrator posts them as Q11–Q13 with defaults. Include DEC-053 and DEC-054 consequences (LS convention in the
margins; the κ arm as a declared secondary condition only if HT-3d's final verdict says so — it currently fails the
retention floor).

### Lane HT-3e — counter-review of the κ pilot result (after HT-3d final)

When `results/R1/ht3d_final/` exists (the orchestrator runs your aggregator on the complete chain), review it as
R1-X12 reviewed the selection: reproduce the macro table from the raw files, check the seed-spread rule and the
retention floor arithmetic, check the clipped-control comparison (ceiling-matched to κ 0.5 only), and write the
two-sentence result the slide can carry under the DEC-054 framing. Say plainly whether the tail reduction survives
the clipped control.

### Lane R1-73b — MQuAKE comparator recipes (after the R1-73 calibration run)

When `results/R1/calibration_mquake_v3/calibration_candidate.json` exists, inspect it against the spec's admission
fields, then build the eight MQuAKE comparator recipes (as R1-64c) bound to calibration v3, with an ordered run list.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
