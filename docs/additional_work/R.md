# Option R — one additional untouched realization of the primary triplet: pre-registration (draft)

Drafted 2026-09-21 by Claude (orchestrator). Binding plan: `docs/additional_work_plan_final.md` (DEC-073). Status:
**draft; depends on AW-R0's allocation check; no GPU call before the lead's review.**

## What

Realization 3 of the registered primary triplet, `R1_learned_ff` (the selected v5 artifact, unchanged),
`R1_nonlearned` and `v0_stable`, on zsRE and CounterFact, five orders each: **30 cells**, 1,000 edits, the frozen
checkpoints (100, 300, 1,000), the same recipes, scoring, full validation and fidelity watch as R1. No reader
retraining (the realization varies populations and orders, not the artifact). MQuAKE is excluded: its certified
margin (211 subjects) cannot supply a realization.

## Why

The registered inference rests on three realizations (DEC-069). A fourth is the only item in the supplemental
portfolio that strengthens the primary claims themselves. With an unchanged sample standard deviation, a t-interval
on four realizations is about 0.7 the width of one on three (t(3)/√4 vs t(2)/√3); this is a sensitivity, not new
coverage, and the registered analysis is not re-run.

## Entry conditions (AW-R0, Codex)

1. The portfolio-wide allocation check passes for both datasets: 1,350 subjects each, disjoint from realizations 0–2
   and from every training, selection and development identity, with template families and all endpoint roles
   allocable (outside, near-support, near-neighbour, revision; locality per DEC-070; question-null family per
   DEC-061/062).
2. Sealed populations and payloads under `assets/runs/pc_cap/R1/additional_work/R/`; extension matrix
   `manifests/additional_work/run_matrix_R_v1.json` built with the existing builders, `block_number` 6, ceilings from
   the per-condition means of the finished R1 cells under the 1.7 two-worker factor; recipes identity-bound as in R1.
3. The primary queue has released the GPU and its lock; AW-B and the frozen AW-L diagnostics have run first.

## Execution

Own receipt root `logs/additional_work/R/`, two workers, the 6,144 MiB memory floor, one retry then incomplete, stop
ceiling 30 GPU wall-hours, October 9 17:00 stop. Dispatch rule: conservative projected completion plus validation
time before the cutoff.

## Reporting

A separate extension report beside the confirmatory report: every realization visible; the registered contrasts
recomputed on realizations 0–3 as a labelled sensitivity with the t(3) display; classifier labels and the DEC-057/058
computations of the registered family are **not** re-issued. Fidelity-watch entries and alerts relayed as for R1.
The report states what the extension cannot say: it is not a fifth or sixth realization, not a fresh-population test
of any intervention, and not part of the frozen decision.
