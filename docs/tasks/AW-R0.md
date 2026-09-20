# AW-R0 — fresh realization and extension preparation

**Status:** complete for CPU allocation/content preparation; execution is not admitted. **Agent:** Codex. **Date:** 2026-09-20. Authority: DEC-073 allocation A; ongoing round 43.

## Result

| Dataset | Full allocation possible? | Eligible after prior reservations | Allocated | Remaining | Near pairs / distinct selected families | Locality |
|---|---|---:|---:|---:|---:|---:|
| zsRE | **Yes** | 2,034 | 1,350 | 684 | 100 / 82 | 50/50 |
| CounterFact | **Yes** | 2,071 | 1,350 | 721 | 100 / 30 | 50/50 |

Each allocation includes 1,000 edits, 100 outside subjects, 100 near-support subjects, 100 near-neighbour subjects and 50 revision subjects. Locality uses existing outside rows, so adds no subjects. All endpoint slots are present; no redraw, seed retry, model call, outcome-guided replacement or shortfall. After reserving the independent edit/outside/revision backbone, 303/452 disjoint near-family pair units were available in zsRE/CounterFact, covering 205/34 families. Multiple pairs per family follow DEC-062. Question-template/relation matching follows DEC-061. DEC-070 selects the first 50 distinct nonoverlapping locality prompts; this draw had no edit/paraphrase locality collision.

## Inputs and verification

The frozen v6 exclusions, v15 joint evidence v7, role plan v2 and original content-sealed reservations are verified by their bound hashes. The real R1 clearance constructor revalidates exposure/alias/teacher/role evidence; every prior reservation across all roles and realizations 0–2 is then removed by item, fact, global entity **and** canonical subject. Every chosen identity passes the same checks again. “Fresh” means certified against these bound training/selection/development exposure records; no claim that a language model has never encountered the fact during pretraining.

`aw/r_extension.py` contains explicit, inspectable adaptations of the frozen allocation, family allocation, endpoint construction and seal-validation routines. They change the layout seam to two datasets and explicit realization 3, keeping the imported clearance, Hall-capacity, stratum quota, RNG, pairing, locality and payload validators. No monkeypatch or change to the primary builders. The original master seed is reused with new realization-3 substreams, recorded initial/final PCG64 states, and five paired orders 100–104. Source ordering and roles are restored explicitly when reading sorted-key JSON. Complete endpoint/population identities are equal across treatment arms and endpoint identities across orders.

Inputs/outputs and all counts: `logs/additional_work/R/preparation-v1.json`. Payloads, reservations and analysis population: `/home/derp/cap/assets/runs/pc_cap/R1/additional_work/R/v1/`. Matrix: `manifests/additional_work/run_matrix_R_v1.json`. Thirty hash-bound recipes: `docs/tasks/AW-R-cell-recipes/`; block 6; separate `logs/additional_work/R/` receipts and `results/additional_work/R/` results. Selected reader weights, constructor, full validation and acquisition budget match each parent primary recipe. No MQuAKE allocation.

Verify: `JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /home/derp/cap/venv/bin/python -m aw.r_extension --prepare`. Final replay: `logs/additional_work-R-prepare-final.log`; reruns must reproduce every published byte. Tests: `aw/tests/test_r_extension.py`, included in `logs/additional_work-round43-tests-final.txt`. The pre-handoff producer-format/layout-readback cleanup changed only producer/dependent metadata bindings; `metadata-finalization.json` records this, and the final replay verifies identical population/payload bytes.

## Costs, scope and handoff

Ceilings use the six condition × dataset means from the 30 completed block-1 donor processes (five per class), verified through bound finish receipts. This fixes the cost sample while the live queue proceeds. **Mean projected summed process time: 38.030 h; summed 1.7-factor ceilings: 64.651 h.** The factor is applied once, with no inherited concurrency multiplier. These are process charges, not measured GPU-active time; concurrent processes can overlap in elapsed time. The 30-hour Option R portfolio allowance therefore needs an explicit schedule/accounting review before dispatch. No budget is silently increased. Cost detail: `AW-R0-interpretation.md`.

The frozen primary execution backend rejects the supplemental recipe mode/realization because its inventory admits only its original cells. These files are **content sealed, not primary launch-authorized**. A supplemental execution consumer and portfolio admission remain owner work before launching; no fabricated freeze/lead authorization is supplied. This is a concrete new namespace limitation, not a defect in the prepared subject allocation. Done-when: all CPU deliverables produced and replayed; no GPU call. CPU execution only, zero GPU seconds. Questions for lead/Claude: review the 30-hour allowance and schedule the supplemental consumer after primary release. No commit made.
