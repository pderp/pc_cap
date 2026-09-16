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

## 2. Orchestrator lane (do not touch)

v0 close-out (tonight) → R1-01/02/03 diagnostics (GPU, ≈ 2 h) → `docs/R1_diagnosis.md` → Stage 1 core modules
(`revision_v1/{contracts,observations,memory,reader,controller,adapt,evaluate}.py`) with the gates → Stage 2 reference and
surrogates → Stage 4 runs and the revision freeze support. Owned: `src/pccap/revision_v1/` except the files named in §3,
`results/R1/`, `manifests/revision_v1/`, the registers, `docs/lead_queue.md`.

## 3. Lanes for Codex — round 15 (CPU; open now)

Round 14 and the heavy-tail lanes are committed (`9038b9a`) and mirrored; your HT-3 review was right and the
preservation term is repaired (f-divergence Σ p ln_κ(p/q); expm1 branch; finite validation; reference-trainer parity —
see `src/pccap/revision_v1/train.py::coupled_divergence` and the rewritten `tests/revision_v1/test_ht_kappa_actual.py`).
The DEC-049/050 selection over six readers × six checkpoints (+ averaged checkpoints) is running on the GPU. Rules as
before.

### Lane R1-D1i — register rebinding against a frozen decisions snapshot

R1-58b/R1-63b refused correctly: register v5 binds the live `docs/decisions.md`, which changes with every accepted
decision. Produce register v6 = v5 content unchanged, bound to a frozen snapshot `manifests/revision_v1/decisions_snapshot_v6.md`
(a copy of `docs/decisions.md` at the binding time, with its sha256) rather than to the live file, plus the DEC-049/050
rows; rerun the draw-plan dry run and the freeze-candidate assembler against v6 (both should now emit their outputs);
report the MQuAKE slack (168 nominal) and what each pending clearance step could remove. No draw.

### Lane HT-3b — re-review of the repaired κ objective

Re-run your HT-3 probes against the installed trainers: non-negativity and stationarity of the repaired preservation
divergence, the expm1 small-κ branch, config validation, reference/fast parity at κ = 0.5, the Q = −κ surprisal
mapping to Nelson–Umarov (state it in the manifest), the clipped-comparator ceiling question (c = 2 vs κ-specific
ceilings: propose the exact aggregation rule and the arm list, keeping the 9 + 3 design or stating the change), and
the "κ does not fix the rejection boundary" caveat. Issue `manifests/revision_v1/kappa_pilot_v2.json` if the objective
passes, with its blockers cleared or listed; the lead's Q4 go/no-go follows.

### Lane HT-5 — stress-panel driver (development mode)

Implement the six-cell stress panel runner the HT-2 contract needs, as a development-mode recipe family for the R1-64
driver: clustered vs shuffled schedules from the manifest, probes at the 20/60/70/80/100 cadence, the fixed old-fact
probe set, recovery band and censoring rule, outputs under `results/R1/stage4_dev_cells/ht_panel/`. TinyBase tests; the
orchestrator runs it after the primary is selected and Q5 is answered.

### Lane R1-X12 — RELEASED: counter-review of the primary selection

`manifests/revision_v1/primary_selection_v2.json` and `primary_condition_v5.json` exist. Review: the populations are
common across candidates; the rule was applied as confirmed (DEC-050); the winner's admissibility sits at the 10 % limit
with n = 100 (state the uncertainty honestly: binomial interval, and what a 300-record or pool-source population would
show — those runs are the orchestrator's next GPU work); checkpoint averaging is a legitimate candidate (uniform weights,
steps 150–300) and its identity is bound; the retention–rejection curve as the talk's central figure. Output
`logs/review_r1_selection.md` with edit requests.

### Lane R1-68c — remove the per-phase clone/restore cost and batch the drift assay

Measured on v5 (notes §"Driver profiles on the primary v5 reader"): the incremental integrity profile is byte-identical
and only 16 s faster than the full profile (1,246 vs 1,262 s), so the ≈ 0.9 s of non-model time per edit and per
immediate phase is the clone/restore/verification around each phase, not the hashing. (1) Instrument the phase wrapper
to split verification / clone / restore / file-write time, then remove clone+restore for phases that the cap's
read-only contract already guarantees (immediate check, retention, locality, unseen, drift: `predict` is gate-tested
not to mutate state; keep a state-hash compare before/after instead of a clone). (2) Batch the drift assay:
`stage4_assays.py` decodes 16,256 prefixes one at a time (31 ms each, 506 s); use the learner's `last_logits_batch`
with per-position selection preserved (one `selection_for` per prefix, batched forwards), and prove equality of the
per-position NLLs against the current assay on TinyBase. Both changes behind the recipe's `integrity_profile`
switch so the full profile stays available; TinyBase parity tests; the orchestrator re-profiles.

### Lane HT-1b — tail audit on the primary v5 cells

Run `scripts/ht_audit_existing.py` over the two v5 driver cells (full and incremental, identical rows) and the v5
endpoint files (`results/R1/endpoints/v5_rare1*`, `unseen_v5_rare1_*`, `drift_assay_v5_*`); report the same
statistics as HT-1 and the comparison with the v4 cell; mark which populations are shared.

### Lane R1-63c — freeze candidate v4 (after R1-X12)

Rebind the freeze candidate to primary_condition_v5, register v6, matrix v4 and the selection manifest; print the open gates.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
