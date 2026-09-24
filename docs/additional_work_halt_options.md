# If the queue stops at cell 225: what the remaining time and GPU could buy

2026-09-24, Claude (orchestrator), for the lead's decision between a pause and a full halt at the block-4 boundary.
Companion to Codex's `additional_work_pc_refocus.md` and my `additional_work_pc_refocus_review.md`. Nothing here is
launched; the pause trigger at the 225th start is armed and applies either way.

## 1. The budget

| item | value |
|---|---:|
| GPU free from (225 complete, drained, reconciled) | Fri Sep 25 ≈ 06:00 EDT |
| last new fits | Mon Oct 6 |
| wall-hours available Fri 06:00 → Oct 6 00:00 | ≈ 280 |
| usable after drains, reconciliation, compilation, retries (≈ 15 %) | ≈ 240 |
| R1 process-hours used / cap | 270 / 750 |

Two workers on the 12 GB card: R1 cells use ≈ 1.3 GB each; the supplemental jobs are all smaller. Contention, not
memory, limits concurrency (measured two-worker slowdown up to 1.66×).

## 2. What a full halt gives up

| remaining R1 work | cells | wall-hours (2 workers) | what it answers | if dropped |
|---|---:|---:|---|---|
| block 5: S1_LM, S1_literal continuation controls, zsRE + CounterFact | 60 | ≈ 53 | "why not just keep training the base on the edits?" — the fine-tuning baseline every reviewer asks for; registered comparator | the talk has matched-update and live-v0 comparators but no fine-tuning baseline; the D.5 contrasts with S1 are reported unavailable |
| extension: historical v2 reader | 45 | ≈ 23 | historical architecture context; **optional** in the protocol (block 6, "285 + 45 optional") | nothing the talk needs |

My view: the extension is the free saving; block 5 is not. A halt that drops block 5 removes the one comparator that
answers the most predictable objection to the cap. If the GPU is short, run block 5 on zsRE only (30 cells, ≈ 20
wall-hours) rather than none.

## 3. Menu of uses, with costs and what each buys

Costs are two-worker wall-hours, ceilings in parentheses; "prep" is CPU work that can start now in `aw/`.

| # | experiment | GPU h (ceiling) | prep | what it buys | risk |
|---|---|---:|---|---|---|
| A | **corrected SE-E vs SE-A on the original v0 cap** (Codex §2): 12 cells, 60 if the profile fits | 3–15 (24) | small runner, solver regression | the programme's original PC question, answered cleanly for the first time | none scientific; the result may be negative, which is still the answer |
| B | **PC acquisition credit with the fixed v5 reader** (Codex §4) | 12–24 (24) | 2–4 days: acquisition variant in `aw/`, parity with the v5 path | whether corrected PC credit transfers to the reader that works | implementation; cannot start on the GPU before ≈ Sep 29 |
| G | **PC-trained reader**: the v5 recipe trained with the corrected ePC surrogate instead of BP, 3 seeds each, evaluated on 300-edit streams (24 evaluations) | 30–40 (48) | `revision_v1/epc_train.py` exists; recipe pinning, parity tests | the deepest PC test on the modern system: is BP training of the reader necessary? The corrected pilot favoured BP (answer NLL 2.85 vs 4.50) at 500 steps; this is the fair, multi-seed version | ePC training ≈ 1.5× BP time; a negative result is likely and would be the honest headline |
| E | **bounded correction + stricter gate** (AW-B as pre-registered) | 12–16 (24) | done (oracle, wrapper, scorer) | the heavy-tail talk's intervention slide: efficacy versus tail, exact 2b guarantee | cheap; trade-off expected |
| I | **edit-count scaling of the tail**: primary condition, zsRE, realization 0, 3 orders, 3,000 edits with checkpoints at 1,000 / 2,000 / 3,000 | 12–15 (20) | recipe with a longer stream from the same population (needs the 3,000-item reserve; else 2,000) | whether harm concentration and the maximum grow with memory size: the porosity/interference curve the abstract implies | population size; one realization only |
| D | **Option R**: one more untouched realization of the triplet, zsRE + CounterFact | 24–30 (30) | AW-R0 allocation check (Codex) | tighter intervals on the registered contrasts (≈ 0.7 width) | fresh subjects consumed |
| F | **upper-layer interface** (AW-L core 2×2, 3 seeds) | 24–30 (48) | 3–5 days: masks, identity audit | the lead's own hypothesis; separates where harm is decided from how far it travels | implementation time competes with B and G |
| S | block 5 (or zsRE half) | 53 (20) | none | fine-tuning baseline | none |

## 4. Three portfolios that fit

| portfolio | contents | GPU h | what the talk gets |
|---|---|---:|---|
| **P1 — PC first, comparators kept** (my recommendation) | A → S (block 5, full) → B → E → I, then G if the v1 seam is late or negative-fast | 3+53+24+16+15 (+40) ≈ 111–151 | PC answered on v0 and v1, fine-tuning baseline complete, tail intervention and scaling slides |
| **P2 — full halt, PC-heavy** (Codex's direction, extended) | A → G → B → E → I → D | 15+40+24+16+15+30 ≈ 140 | three PC results (v0 credit, v1 credit, PC-trained reader), tail slides, tighter intervals; no fine-tuning baseline |
| **P3 — full halt, tail-and-interface** | A → E → I → F → D → B if time | 15+16+15+30+30+24 ≈ 130 | heavy-tail story complete, the upper-layer hypothesis tested, one PC result; no fine-tuning baseline |

All three leave ≥ 90 usable hours of slack for retries and for whichever item the first results make urgent. The
order inside each portfolio is by decisiveness per GPU-hour; A goes first everywhere because it is the cheapest and
the most overdue.

## 5. What I would not do

- Drop block 5 to fund the extension, Option R or AW-L: each of those is worth less to the talk than the fine-tuning
  baseline.
- Run a third GPU process beside the R1 workers to overlap: the 1.7× ceilings have ≈ 35 % headroom, and a third
  process could push cells past them and trigger retries that cost more than they save.
- Start a new architecture (the colleague's small-scale system, generated readers, joint distillation) inside this
  window; Codex's deferral stands.

## 6. Decisions this needs from the lead

1. Pause or halt at 225, and if halt, whether block 5 (or its zsRE half) is kept.
2. Which portfolio, or which subset of the menu, with the order.
3. Whether the talk should carry the PC results; that fixes the cut order between G, F and I.

Codex's parallel proposal and this one differ mainly on block 5 and on adding G and I; where they agree (A first, B
second, E kept small, AW-L and the extension deferred) the lead can treat the point as settled.
