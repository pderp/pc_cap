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

- **2026-09-24 15:55** — DEC-074/074b: the queue runs through block 4 and block-5 positions 1–45 (S1_LM both datasets, S1_literal zsRE), halt trigger armed at the 270th start (≈ Saturday evening); then the PC refocus; Codex round 43 delivered (AW-R0, AW-L0/L1/L3, AW-L prereg) and superseded in priority by the PC lanes below.

- **2026-09-21 17:25** — block 3 complete (135 / 330, the whole triplet); block 4 running with two workers under bindings v2; Codex lane R1-D14d (triplet confirmatory analysis) opened ahead of the additional-work lanes.

- **2026-09-20 17:30** — block 2 complete (90 / 330, 0 failures); Q21 cutover done (drain, idle reconciliation, signed resume); queue running under bindings v2 (factor 1.7, stop-after 6) since 17:16; block-3 watcher armed. Additional work: DEC-073, `aw/` namespace, Codex lanes AW-R0 / AW-L0-L1 / AW-L3 / AW-L-prereg open.

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
  +0.006## 3. Lanes for Codex — round 41 (CPU; open now; posted 2026-09-18 15:05 EDT) — report coverage; verification lanes wait

Round 40 is committed and mirrored. New files only while the lead signs; `scripts/r1_d14_report.py` and its template are
Codex's own and not bound by the operator's digests, so they may be edited. Priority order: **R1-63o (urgent; supersedes R1-D10i) → R1-D14b → X20 (after
step 8) → HT-4f (after step 2).**

### Lane R1-63o — re-bind the ENTIRE live package to the current tree, then freeze the tree (URGENT; supersedes R1-D10i)

**Sequencing (17:30 EDT): both answered — DEC-069 (Q19: A + the t-interval secondary display) and DEC-068 (Q20: triplet-first). Proceed now.** Fold both into the same
versioned pass: protocol **D.5** (Q19: the three-cluster inference statement per review §2 — registered computation kept,
relabelled as preliminary decision summaries, every realization estimate and order dispersion shown, effects before
labels, no 95 % familywise claim; plus the assumption-labelled t-interval if the lead takes it; and §1's explicit
deferral of the unperformed factorial / PC branches) and matrix **D.5** block numbers under the amended order (Q20:
triplet across all realizations first, then matched / live, then S1, then the extension). One package, one rebind,
then the tree freeze.

The signing session (DEC-067: delegated to the orchestrator; session v9 on inputs v10) completed steps 1–5 — clearance,
RNG admission with the lead's seed, draw (100 / 100 near-miss pairs matched in every dataset × realization) — and
stopped at endpoints: `r1_d10c_endpoints construct` refuses ("review input changed: scripts/r1_d10c_endpoints.py")
because the role plan binds that script at its round-26 bytes. A recursive scan of every resource the remaining
steps read (`logs/r1_round41/stale-bindings-inventory.txt`, 1,701 resources, 93 with stale bindings) shows the drift
is package-wide: producer scripts edited after their outputs were bound — `r1_d10c_endpoints.py` (role plan, joint
evidence, historical evidence), `r1_49g_inference.py` / `r1_49g_analyze.py` (matrix D.4 and earlier), `r1_63j_production_bundle.py`
(all 27 runtime templates in `R1-63m-runtime-v2/`), `r1_58h_cost_contract.py` (cost receipts), `r1_d9_receipts.py`
(D10 evidence chain), `r1_68c_dev_cell.py` / `r1_77b_sealed_backend.py` (older candidates). Do, in one versioned pass
on the current tree: role plan v2 and joint evidence v7 (provenance refresh only; state that no row changed), matrix
D.4.1 regenerated by its producer, runtime templates v3, cost receipt v5 (same content, current producer binding),
candidate v15, inputs v11 (clearance evidence → v7, role plan → v2, matrix → D.4.1, construction inputs → v10),
forms v10 and sheet v9; verify with the orchestrator's scanner method that NO resource on the live path (inputs v11 →
everything reachable) binds a file whose bytes differ from the tree. Then **declare the tree frozen**: from that commit
until launch, no edit to any script bound anywhere in the package (list them); any further change requires a new
package version and the orchestrator's go-ahead. The orchestrator then runs a fresh session (steps 1–8) on inputs v11
with the same seed, and X20 verifies.

### Lane R1-D10i — clearance evidence re-bound to the current endpoint constructor (URGENT; blocks the lead's step 3)

The lead's `clearance --execute` refuses with `exhaustive_clearance_review: clearance evidence binding changed`: the
operative joint evidence (`assets/runs/pc_cap/R1/r1_d9e/round26_final/joint_evidence_DEC061.json`) lists
`scripts/r1_d10c_endpoints.py` at its round-26 bytes (sha a2c968b4…) among its `evidence_bindings`, and round 31
changed that file (now 9afe6221…; full-validation contract) — the dry run does not check the bindings, the execute
path (`r1_d9_receipts.clearance_value`) does. The clearance rows themselves are untouched. Emit evidence v6 = v5 with
that binding refreshed (and any other stale producer binding — run the check over all 865), a statement that the
D10c edits since round 26 do not affect clearance, inputs v10 binding evidence v6, candidate v15, and say explicitly
whether the signed step-1 / step-2 receipts stay valid under inputs v10 (see the orchestrator's finding on what the
receipts bind, lead queue item 94) or must be re-signed. New files only; the lead's session is paused at step 3.

### Lane R1-D14b — apply X21's four coverage gaps to the report formatter (first)

G1: the remaining v5.1 §5.2 / D.2 tail fields (exp(mean ΔNLL) with overflow handling, signed maximum with position
and tie convention, zero-mass atoms; KL counterparts; sample fields bound from the analysis JSON, never invented);
G2: the joint cap-fidelity benchmark flag beside the per-reference labels, with unavailable ≠ false; G3: the
secondary historical-v2 package comparison table (eight secondary-role contrasts, 24 metric rows, `secondary_descriptive`,
the 63-interval family untouched); G4: the DEC-052 execution-accounting section bound to a verified D11 / D13 report
(process spend, unknown-cost records, retries, host failures, block reconciliation) or an explicit "unavailable"
section. Acceptance fixtures as X21 lists; the 63 primary rows and classifiers identical before / after; the skeleton
refilled from the synthetic output with no unbound placeholder.

## Round 43 — additional work (DEC-073), Codex lanes (2026-09-20)

Ground rules for every lane: CPU only (`JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=`), no file under `scripts/` or
`src/pccap/` is added or edited (content lock; the resume consumer re-verifies it), no large cache builds while the
queue runs, Codex-owned files only (listed per lane; `aw/bounded.py`, `aw/wrapper.py`, `aw/scoring.py` and
`docs/additional_work/{AW-B,R}.md` are the orchestrator's), task record `docs/tasks/AW-<lane>.md` + completion JSON as
usual. Plans: `docs/additional_work_plan_final.md` (binding), `additional_work_plan{,2,3}.md` (history).

## Round 44 — PC refocus (DEC-074a), Codex lanes (2026-09-24)

Same ground rules as round 43 (CPU only; nothing under `scripts/` or `src/pccap/`; Codex-owned files only; the
orchestrator owns `aw/bounded.py`, `aw/wrapper.py`, `aw/scoring.py`, the S1 caveat execution, drains/resumes, and
`docs/additional_work/PC-v0.md`). Specification of record: `docs/additional_work_pc_refocus.md` §§2–5 with
`_review.md` §3 sequencing and `_response.md`; decisions DEC-074/074a.

### Lane PC-1 — v0 corrected-credit runner and the actual-solver regression (first)

`aw/pc_v0.py`: a small runner that builds the original v0 C1 cap on the regenerated ePC checkpoint
(`EPCBase.from_npz` on `assets/models/epc/epc-50m/checkpoints/final-009766/params.npz`, SHA-256 `ea4c561d…`; never
the default constructor), with `credit="adjoint"` (SE-A) or `credit="error"`, `credit_iters=8`, error lr 0.1 (SE-E,
corrected energy), fresh empty memory per arm, the archived S5 v2 calibration and stream-selection rules, old S5
scoring (ES, RET-ES, RET-GS, LS) plus the bounded-text score as a separate secondary column, cost counters (nine
forwards + nine reverses per eight-step credit), new output directories under `results/additional_work/PC-v0/`.
Tests in `aw/tests/test_pc_v0.py` against the **real solver** on the tiny base: with nonzero writes, the one-step site
error from zero error equals −0.1 × adjoint within tolerance (the check that catches SD-24); zero-error forward
identity; unchanged base weights; independent empty memories; target clamped only for the taught support answer.
Deliver also the 1/8/32-iteration diagnostic (energy, gradient residual, cosine, norm) on a fixed development prefix
sample, and a timing-profile command for the 12-cell scope (two credit rules × zsRE, CounterFact × realizations 0–2 ×
one preselected order; 1,000 / 300 edits). No GPU: the profile runs after release under the orchestrator.

### Lane PC-2 — fixed-v5 acquisition-credit seam (second)

`aw/pc_v1_acquire.py`: an isolated variant of `revision_v1/adapt.py`'s delta acquisition that replaces the adjoint
direction by the corrected eight-step error credit while keeping the real feedforward loss for acceptance,
initialisation, bounds, stopping and cost accounting (no hard-coded one-reverse cost); adjoint mode must reproduce
the v5 path to the bit on the tiny base (cf. `aw/tests/test_wrapper.py` for the pattern). Populations: the exposed
realization-0 zsRE/CounterFact streams, 300 edits, one order, paired arms. Tests in `aw/tests/test_pc_v1_acquire.py`.

### Lane R1-D14d — triplet confirmatory analysis (retained; after PC-1)

### Lane R1-D14d — triplet confirmatory analysis on complete data (see round 44)

Blocks 1–3 are complete: `R1_learned_ff`, `R1_nonlearned`, `v0_stable` × zsRE, CounterFact, MQuAKE × realizations
0–2 × five orders (135 cells). Run the registered D.5 analysis exactly as frozen (R1-49g / R1-75 / the D14 skeleton)
on those cells: the primary contrasts with the registered DEC-057/058 computations and classifier labels kept as
preliminary decision summaries, the DEC-069 t-interval (2 d.f.) secondary display beside the min–max bootstrap, every
realization visible, the cap-fidelity benchmark and concentration statistics per cell, the DEC-052 inventory, the
watch summary, and the comparator slots marked unavailable until blocks 4–5 finish. Read-only on the run and on the
sealed cells; no re-scoring. Output `logs/R1/reports/triplet/` + `docs/R1_stage4_report_triplet.md`, figures worth a
slide to `assets/presentation-materials/figures/triplet/`. Supersedes the block-1 partial report's tables where the
triplet is complete; say what changed between r0-only and r0–r2.

### Lane AW-R0 — portfolio allocation check and the Option R extension matrix (first)

Under DEC-073 the certified fresh subjects go to Option R: one additional untouched realization (index 3) of the
primary triplet (`R1_learned_ff`, `R1_nonlearned`, `v0_stable`) on zsRE and CounterFact, five orders each = 30 cells,
1,000 edits, the selected artifact unchanged (no reader retraining). Deliver: (1) the allocation check with the real
population constructor and the frozen exclusions — subject-disjointness from realizations 0–2 and from every training,
selection and development identity, template-family feasibility, all endpoint roles (outside, near-support,
near-neighbour, revision, locality per DEC-070, question-null family per DEC-061/062) — with a plain yes/no per dataset
and the remaining margin after allocation; (2) if yes, the sealed realization-3 populations and payloads under
`assets/runs/pc_cap/R1/additional_work/R/` and an extension matrix `manifests/additional_work/run_matrix_R_v1.json`
built with the existing builders (recipes identity-bound as in R1, new receipt root `logs/additional_work/R/`,
`block_number` 6, ceilings from the per-condition means of the finished R1 cells under the 1.7 factor), plus the
cell recipes under `docs/tasks/AW-R-cell-recipes/`; (3) a one-page note on what the extension can and cannot say
(reported beside DEC-069, never inside it). No launch, no GPU. Files: `docs/tasks/AW-R0*.md`, the manifests above,
`aw/r_extension.py` if code is needed.

### Lane AW-L0 / AW-L1 — identity audit and cheap tap screen (second)

L0: inspect the frozen constructor and the saved v5 reader metadata; record tap indices (banks after blocks 4, 8, 12;
bank 3 pre-`ln_f`), pre/post-normalisation convention, write sites, the acquisition rule and the active `single_site`
value; verify all-site reconstruction of a saved development checkpoint (prediction agreement on 64 development
prefixes). L1: on cached development observations (existing caches only; no new cache build), per-tap norm/variance
and retrieval/null discrimination for read sets {1,2,3}, {2,3}, {3}, {2}, identical small probes split by
subject/template family, the lexical-only feature as a diagnostic control; paired retrieval/false-fire tables with the
explicit caveat that probe quality is not editing quality. Files: `docs/tasks/AW-L0.md`, `docs/tasks/AW-L1.md`,
`aw/tap_screen.py`, `aw/tests/test_tap_screen.py`, results under `results/additional_work/L1/`.

### Lane AW-L3 — explicit read/write sets (third)

`aw/interface.py`: a supplemental learner configuration with explicit `read_taps` and `write_sites` such that
acquisition (`adapt.py`'s delta routine), the fallback controller writes, stored deltas, deployment and memory
accounting all obey one mask — masked before gradient normalisation, updates and projection; inactive sites exactly
zero throughout; the aggregate write allowance and the five-step acquisition budget unchanged for every write set (no
budget multiplication when sites are removed); query/JIT caches cleared on identity change. Subclass or wrap, never
edit, the locked modules. Tests in `aw/tests/test_interface.py` on the tiny base: inactive writes are exactly zero in
acquisition and deployment; `{1,2,3}`/`{1,2,3}` reproduces `RevisionCap` to the bit (logits and cost counters,
cf. `aw/tests/test_wrapper.py`); dropping a read tap removes the corresponding projection parameters and the count is
reported. Files: `aw/interface.py`, `aw/tests/test_interface.py`, `docs/tasks/AW-L3.md`.

### Lane AW-L-prereg — AW-L pre-registration draft (fourth)

`docs/additional_work/AW-L.md`, one page: hypothesis, the 2×2 arms (read {1,2,3},{2,3} × write {1,2,3},{3}), three
paired reader-training seeds, zsRE and CounterFact, 300 edits, one order, the sealed realization-0 confirmatory
streams as the evaluation population (DEC-073, labelled post hoc/exposed), endpoints (ES, RET-ES, RET-GS, LS,
near-miss, revision at 100 and 300; full ordinary-text fidelity at 300 with the tail statistics of the final plan),
the descriptive 0.02 tolerance rule, resource accounting (training, acquisition, corrected-pass cost per fired query,
observation pass), the L4 pilot gate and the 48-hour ceiling. Draft for the lead's review; the orchestrator writes
`AW-B.md` and `R.md`.

### Lane R1-D14c — first partial confirmatory report from block 1 (done, 2026-09-20; `docs/R1_stage4_report_block1_partial.md`)

Run the D.5 analysis (`r1_49g_analyze` / R1-75 / the D14 report) on the 45 completed block-1 cells (the triplet on
realization 0, three datasets): every table and figure the skeleton promises, filled where data exist and marked
unavailable where not (no classifier labels without three realizations; the primary contrasts as realization-0
estimates with order dispersion only; fidelity benchmarks and concentration statistics per cell; the DEC-052
inventory; the watch summary). Output under `logs/R1/reports/block1/` + `docs/R1_stage4_report_block1_partial.md`; a copy
of any figure worth a slide to `assets/presentation-materials/figures/block1/`. Read-only on the run.

### Lane HT-4f — claim ledger v6 (done, 2026-09-20: v6 was already published against the v8 cost; a session-v10 supplement was delivered instead, `docs/talk_claim_ledger_v6_session_v10.md`)

### Lane X22 — block-1 receipt-chain audit (done, 2026-09-20: PASS, all 45 cells; 46.805 h charged, matching the D11 block-1 report)

Every finish / decision / receipt under `logs/R1/final_queue/` for the 45 cells against the frozen recipes, the sealed
payload hashes, the checkpoint receipts in `results/R1/stage4_sealed_cells/`, the charged process time (no double
counting) and the fidelity-watch observations; a plain integrity statement or the exact defect. Read-only.

### Lane R1-77g — post-freeze ceilings amendment (delivered; Q21 answered A, DEC-072; the orchestrator is executing the drain-and-resume at the block-2 boundary — no Codex action)

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
