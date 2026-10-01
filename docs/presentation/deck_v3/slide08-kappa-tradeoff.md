# Slide 8 — Two interventions against extreme prediction loss

**Draft speaker text for charlie's review, updated October 1. Measured results; distinct populations.**

**On screen:** AW-B survival curves, with the one-nat boundary. Keep the κ trade-off
figure as backup. Claims: `kappa-design`, `AW-B`. DEC-078 treats the mixture as an
intervention beside the κ pilot, not a recommended cap configuration.

## Speaker text

“The kappa pilot changed the reader's training loss. Both kappa settings reduced a development tail statistic but lost too much retention and failed the declared success rule. Clipping also reduced that tail descriptively. These remain preliminary trade-offs, without evidence of a special coupling advantage.” [`kappa-design`]

“AW-B asks a different question: can we limit the correction at query time? We calibrated sixteen settings on development memories, requiring retention within two percentage points on both datasets and no worsening of locality or near-miss preservation. Every symmetric clip failed retention eligibility. The selected mixture keeps about thirty-seven percent of the original base distribution and sixty-three percent of the cap distribution. No shrink or gate comparator qualified.” [`AW-B`]

“Evaluation then used ten already-exposed memories: five orders on each dataset, at three hundred edits. All ten met the declared rule: smaller maximum loss and worst-one-percent average, with retention inside tolerance. zsRE endpoints were unchanged. CounterFact paraphrase retention changed by {{awb.counterfact.gs_change}}, a loss of roughly 0.7 to 1.2 percentage points. The largest observed token losses fell from as much as fifteen nats to one.” [`AW-B`]

“The survival curves include all 245,237 fixed-prefix positions per memory, including unchanged and improved predictions. Thin curves are orders, not independent datasets. The mixture moves zsRE mean KL below the original 0.001 line in every order; CounterFact remains above it. Calibration and evaluation together cost {{awb.hours}} process-hours. The pilot's ES95 on 4,064 positions is a different quantity and population from AW-B's ES99.” [`AW-B`, `kappa-design`]

“The guarantee has a precise scope. At the same prefix, mixing in a base share of exp minus one ensures the target probability never falls below that share of the base probability. Its extra negative log likelihood is therefore at most one nat per token. That does not bound a whole generated answer by one nat, preserve every greedy answer, or establish a heavy-tail family. It also does not implement coupled free energy or autonomous action selection.” [`AW-B`, `AI-testbed`]

## Sources and backup

- [AW-B report](../../additional_work/AW-B_report.md): all settings, selection, per-order differences, costs and proof.
- Survival plot: `assets/presentation-materials/figures/aw_b/evaluation-survival.png` (PDF/SVG and source manifest beside it).
- κ backup: `pc_cap/logs/r1_round37/presentation-figures-v2/kappa-tradeoff.png`; ordinary/κ.2/κ.5/clip2 retention 0.796/0.754/0.748/0.779, ES95 0.223/0.084/0.063/0.103 nats. Three development datasets × three training seeds; no κ claim is upgraded by AW-B.
