# Additional experiments before October 9 — final plan

2026-09-20, Claude (orchestrator), consolidating Codex's plan (`additional_work_plan.md`), my review
(`additional_work_plan2.md`) and Codex's response (`additional_work_plan3.md`). Where the three disagree, this
document says which position is adopted and why. It is the working plan; each lane also gets a one-page
pre-registration under `docs/additional_work/` before its first GPU call, reviewed by the lead. No signing machinery.

**Constraints confirmed by the lead (via Codex, plan 3):** everything runs locally on this machine in the existing JAX
venv; no Colab or remote execution; no PyTorch execution (PyTorch source is read-only reference); porting and validation
time count against the schedule. The primary run, its lock and its budget are untouched; supplemental GPU work waits
for the queue's release and never competes with it.

## 1. Portfolio (adopted)

| # | lane | what | GPU stop ceiling | earliest GPU start |
|---|---|---|---:|---|
| 1 | **AW-B** bounded correction + stricter gate | clip / matched mixture / shrinkage / lower null threshold, calibrated on development streams, evaluated on paired supplemental streams; tail and efficacy together | 24 h (12 h target) | release + 0 d |
| 2 | **AW-L0/L2** frozen diagnostics | tap-removal re-encoding and `single_site` deployment ablation on copies of the sealed realization-0 triplet memories; labelled post hoc | 4 h | release + 0 d |
| 3 | **AW-L** trained core | 2 read sets {1,2,3},{2,3} × 2 write sets {1,2,3},{3} × 3 seeds = 6 trained readers, 24 evaluations on zsRE and CounterFact, 300 edits, one order | 48 h | release + 1 d |
| 4 | **Option R** | one additional untouched realization of the primary triplet on zsRE and CounterFact (30 cells), same selected artifact, no reader retraining; separate extension matrix and receipt root; reported beside, never inside, DEC-069 | 30 h | after 1–2 and the allocation check |
| 5 | AW-L optional read sets {3},{2} | only after 1–4 are secure; each with both write sets or explicitly as an incomplete factor | 24 h | after 4 |
| — | reserve (retries, re-runs) | | 20 h | |
| | **ceiling** | | **150 h** | |

One ceiling, reconciling my "200" and Codex's "116–126": 150 GPU wall-hours, of which the first three lanes need at
most 76. About 290 wall-hours exist between the forecast release (September 26–27) and the October 9 17:00 freeze; the
difference is deliberately unallocated for primary-study completion work, host and review time.

Cut order if time or data become tight: 5, then 4, then reduce AW-L to the read factor only (never below three seeds),
then AW-B to the exploratory ≤ 8 h version on known checkpoints. AW-G and AW-D stay deferred.

## 2. Corrections adopted from Codex's response

- **Option R: one realization, not two**, and only zsRE/CounterFact. Certified margins (R1-D10h) are 2,034 / 2,071 /
  211 subjects; one full realization needs 1,350 and roles are subject-disjoint; MQuAKE cannot fit. A realization of
  the registered condition reuses the selected reader artifact, so no retraining. The halving of interval widths holds
  only for an unchanged sample standard deviation and is reported as a sensitivity, not as new coverage.
- **AW-B: the proxy is descriptive only.** Clipping every token's log-ratio and renormalising is not scalar KL
  truncation (Codex's three-token example: KL 4.50 → 0.007 at b = 0.5, which the oracle's tests now reproduce). No
  prediction about whether the old 0.001 line is met is registered; the registered expectation is a trade-off, and both
  tails and mean KL are measured. "Fired" in my pre-analysis is the changed-distribution fraction; gate telemetry will
  be logged separately.
- **AW-B success rule:** retention tolerance 0.02 on RET-GS/RET-ES kept; tail thresholds are *not* carried over from
  the κ pilot (ES95 on 4,064 positions is a different population). Endpoints and the selection rule are fixed in the
  pre-registration on the actual supplemental population before any scoring: paired maximum, ES99 (zero mass included),
  exceedance at 0.01 / 0.1 / 1 nat, mean KL and signed ΔNLL, with paired stream/seed differences shown and no
  token-level independence claims.
- **Stricter gate means lowering `null_threshold`** (hard null when `null_mass ≥ threshold`); other rejection rules
  unchanged and their interaction recorded.
- **AW-L arm counts** as in Codex's table: core = 6 readers / 24 evaluations; the optional read sets add 6 readers each
  way and are a separate, later lane. Three seeds are not traded for variants.
- **Runtime figures are targets, ceilings stand.** The 351/368 s trainings are the earlier text-null readers; the v5
  recipe with changed taps and its caches is profiled in L4 before any promise. Option R uses per-condition costs from
  the finished cells, not block-1's three-dataset mix.
- **Framing** of the GT connection stays a connection: R1 is a stronger-base cap study related to stage-B questions,
  not a matched-compute adapter comparison or a test of CD readers or PC learning; our KL assay is behaviour on a
  declared population, not the report's worst-case distance; the memory-versus-access analogy is an analogy.

## 3. Population allocation — decided: A (lead, 2026-09-20; DEC-073)

The certified margins are the same pool for Option R and for fresh AW-L/AW-B evaluation streams. After Option R takes
1,350 per dataset, about 684 zsRE and 721 CounterFact subjects remain before further exclusions, which cannot supply
three fresh 300-edit streams plus endpoint roles. The choices:

- **A (recommended).** Fresh subjects go to Option R. AW-B is calibrated on the existing development payloads
  (`r16_*_v5`) and AW-L/AW-B are *evaluated* on the sealed realization-0 confirmatory streams of the triplet, which the
  selected artifact has already seen: labelled "post hoc evaluation on exposed confirmatory populations", paired cell
  for cell with the block-1 report, no selection performed on them. Strengthens the registered result and keeps the
  interventions directly comparable to the primary cells.
- **B.** Fresh subjects go to AW-L/AW-B streams; Option R is dropped. Interventions get a fresh-population claim; the
  primary inference stays at three realizations.
- **C.** Split: shorter fresh streams (100 edits × 3) for the interventions and no Option R, or Option R plus
  interventions on development streams only (exploratory operating curves). Weakest of the three for the talk.

Adopted: A. Manifests are built accordingly.

## 4. Implementation plan and status

Namespace `aw/` (package), `aw/tests/`, `manifests/additional_work/`, `results/additional_work/`,
`logs/additional_work/`, large artefacts under `/home/derp/cap/assets/pc_cap/additional_work/`. Nothing under
`scripts/` or `src/pccap/` changes (the lock verifier inventories those trees). CPU only until release; JAX backend
forced to CPU in every test; no large cache builds while R1 runs.

| step | owner | status |
|---|---|---|
| B1 oracle: `aw/bounded.py` (clip, matched mixture, shrinkage, exact full-vocabulary normalisation) + `aw/tests/test_bounded.py` (normalisation, limits, extreme logits, 2b per-token bound for every token, mixture bound, Codex's example, no top-k shortcut) | Claude | **done, tests pass** |
| B2 wrapper: `aw/wrapper.py` subclassing `RevisionCap.predict` to return base and cap logits from the same call (the base pass `fr.logits` is already computed before the corrected pass) and apply a wrapper or a threshold override; unrestricted = v5 to the bit, hard-null = base | Claude | next (CPU tests with a fixture base) |
| B3 scorer: streamed full-validation pass computing all wrappers from one base/cap pair per position, writing per-position vectors in the 68f layout plus one block per wrapper; generation per wrapper for ES/RET endpoints | Claude | after B2 |
| L0/L1 identity audit and cheap tap screen on cached development observations | Codex or Claude, lead's call | after B2 |
| L3 masks: explicit read/write sets in `aw/interface.py`; acquisition, controller, deltas, deployment and memory accounting obey one mask; tests: inactive writes exactly zero, all-site reproduces the baseline | second agent | after L0 |
| R0 allocation check for the whole portfolio with the population constructor; extension matrix for one realization built with the existing builders | Codex | when assigned |
| pre-registrations `docs/additional_work/{AW-B,AW-L,R}.md` | Claude drafts, lead reviews | before first GPU call |

Calendar: September 21–25 CPU work above; September 26–27 release and D13 reconciliation; then AW-B and L2 on the
GPU; September 28–October 2 AW-L core; October 1–5 Option R; October 6 last new fits; October 7–8 evaluation and
figures; October 9 17:00 freeze. Dispatch rule for every lane: conservative projected completion plus validation time
must precede the cutoff, recorded per job.
