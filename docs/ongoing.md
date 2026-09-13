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

**Post-freeze rule for every agent (from the moment `manifests/frozen.json` exists).** The freeze binds the hash of the
whole installed `src/pccap` tree; every confirm-mode job compares the tree at start and refuses on any difference (exit 2,
the queue stops). Therefore: no edits under `src/pccap/` after the freeze — not even in your own lane's files
(`src/pccap/baselines/grace_*.py` included). Put B4-D diagnostics and fixes in new files under `scripts/`, `logs/`,
`results/` or `docs/`, or as a proposed patch under `docs/tasks/`; a fix that must land in `src/pccap` is applied only with
a versioned manifest and `--allow-code-drift` recorded by the orchestrator (plan 4 §2). Tests under `tests/` and everything
outside `src/pccap` are unaffected.

## 1. State (2026-09-13, 06:10 EDT)

- **S8-02 done**; `docs/report.md` complete as draft 1 (every section filled); `docs/HANDOFF.md` written. Open: Codex Lanes
  P2 (final-tree reproduction audit → S8-01) and X2 (report review); the lead's T4 review and SD-22 choice. GPU idle.


- **Everything confirmatory is done and analysed**: S4 (210 runs) and S5 (60 runs); frozen paired analyses (zsRE negative,
  CounterFact floor, grammar incomplete under SD-22 + labelled supplement); D3 memo (`docs/D3_decision.md`); S5 report;
  S7 reversals on four checkpoints (`results/S7/summary.md`); analysis-tree v2 (DEC-028). **S8-02 ablations running** on
  the GPU (≈ 1 h left); **S8-03 report draft 1** in `docs/report.md` (§8 pending). Codex's round 4 is evaluated and mirrored.
- Remaining before the handoff (S8-04): fill report §8, the final-tree reproduction audit (S8-01), the lead's review of the
  D3 memo and the report (T4 / CP-F), and the lead's SD-22 choice (default (a) applied).


- **S4 and S5 complete** (270 runs, 20.4 accelerator h, no failures). Confirmatory execution is over; the post-freeze
  source rule now applies only to `src/pccap/harness`, `cap`, `bases`, `pc`, `data` (nothing may change how a run would
  have executed); the analysis tree (`src/pccap/analysis`) gets a recorded version 2 (DEC-028) for the grammar collector
  fix and the S7 checkpoint runner. Codex: its round-4 lanes stand; do not edit `src/pccap` outside `analysis/` and
  only with an edit request there.


- **S4 complete** (210/210, 11.49 accelerator h; zsRE and CounterFact classified negative on the required contrasts;
  grammar analysis pending the post-queue analysis fix). **S5 queue running** (60 jobs, ≈ 12 h). Post-freeze rule still
  in force until S5 finishes; then a recorded analysis-tree version lands the grammar collector fix and the D3 audit runs.


- **CP-E done twice.** v1 (DEC-025) was superseded before any result: the sanctioned loader refused every editing
  realization because the grammar's `.npz` resource binding failed its realization-name rule (DEC-026; repaired with a
  regression; the queue now stops on systematic failures). The lead wrote **`frozen-confirmatory-v2`** (DEC-027); the job
  list is regenerated (210 S4 + 60 S5 scheduled) and the **S4 queue is running** — first job verified (zsRE C0 r0 p0,
  300 edits), then the full queue (`results/S4/queue.jsonl`, `queue_logs/`, stop file `results/S4/queue.stop`).
- The post-freeze rule above is in force: the frozen tree is `0f20e120067b…`.


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
- **08:55 EDT — freeze pending the lead's command** (`docs/lead_queue.md`, "Freeze now"; B4 recorded unavailable under DEC-020, grammar
  available). Execution machinery ready: `pccap queue` (S4-04), the S5 jobs scheduled behind the S4 jobs with SB reused
  (S5-02, 12.8 of 18 h). `docs/updated_plan8.md` is the current plan delta. The orchestrator starts the S4 queue the moment
  `manifests/frozen.json` exists; GPU otherwise idle.
- ePC substrate eligible; grammar provisional until tonight; P4 done; S7 harness and inventory fixed (Lane X repairs in).
- **GPU idle**, lease free. Corrected B4 numbers: learned-value gaps 0.09–22.4 with 40/40 output/NLL
  agreement and loss trajectories within 3e-3 relative.

## 2. Orchestrator lane (do not touch)

(V2-01…05 repairs, B4 wiring, GPU window 2, E.2 pass, grammar pricing: done) → B4 profile (development, ledger deltas)
when Lane B4-S lands → freeze support (D-A: the lead's command is posted) →
S4-03/04 execution as run owner → S4-05/06 · S5-02 · E.2 filter pass + S7-01/02 · S7-03 · S8. Owned paths as
before (`src/pccap/{distill,pc,harness,cap,analysis,routers,transport,bases,fixtures,data}/`, `results/`
except lane-named subtrees, `manifests/`, `docs/decisions.md`, `docs/spec_defects.md`, `docs/lead_queue.md`,
`logs/` except lane reports).

## 3. Lanes for Codex — round 5 (all CPU; open now unless marked)

### Lane X2 — counter-review of the D3 memo and the report draft (read-only + `logs/review_report_draft1.md`)

Check every number in `docs/D3_decision.md` and `docs/report.md` §1–§7, §9–§10 against the results files they name
(`results/S4/partial/s4_06_*`, `results/S4/resource_views.json`, `results/S5/paired_*.json`, `results/S7/summary.json`,
run ledgers); flag any statement not supported by a file, any policy wording that drifts from `manifests/frozen.json`
(DEC-009), and any place where a floor or the SD-22 incompleteness is stated too strongly or too weakly. Propose corrections
as a patch under `docs/tasks/`; do not edit the memo or the report.

### Lane P2 — final-tree reproduction audit (after the ablations finish; the orchestrator posts "S8-02 done")

Repeat Lane P on the final tree (all CPU commands of `docs/REPRODUCE.md`, in the recreated environment, fresh shells),
plus the dry-run form of one confirm-mode job (`--dry-run`) and `python scripts/s7_summary.py`; `logs/reproduce_final.md`.
This is S8-01's reproduction audit; the orchestrator mirrors it.

### Lane B4-D2 (optional, only if you have time) — reduction probes across the committed parity cases

The bounded next step your B4-D report names: the fixed reduction probes across all 20 committed cases, measuring whether
the first-gradient reduction discrepancies predict the recorded trajectory differences. New files only; no perturbation
search; `logs/grace_reduction_survey.md`.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
