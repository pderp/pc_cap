# Revision v1 Stage 4: correction, interference and concentrated harm

**Assembled confirmatory-study report — reconciled DEC-074b halt, September 27, 2026.** This is the single report entry point, following the registered skeleton [S]; its complete filled tables remain in the [native appendix][A]. Lettered citations identify the source file; full SHA256 hashes and table selections are in the [source registry](../stage4/sources.md). This assembly introduces no model execution, re-scoring, inferential calculation or new classifier label. Receipt sums and formatting are the only derived displays.

## Abstract and research question

The learned memory reader improves paraphrase retention over the tested controls, while failing the declared cap-fidelity benchmark. Published final RET-GS means are **0.96033 zsRE, 0.67800 CounterFact and 0.71556 MQuAKE**; the latter ends at 300 edits and is descriptive. All **45 learned-reader cells** exceed mean KL 0.001; their largest positive token loss increase is **17.06053 nats**. Useful editing and concentrated unintended changes coexist. These observations test a BP-trained correction system; predictive-coding credit and active policy choice are separate supplemental/proposed work. [T] [C] [D]

## Methods and populations

The frozen D.5 inventory declares **285 core + 45 optional cells**, three realization clusters and five paired orders per cluster. zsRE/CounterFact use checkpoints 100/300/1,000; MQuAKE uses 100/300. ES measures immediate edit success, RET-GS retained paraphrase answers, and LS exact bounded locality-text agreement with the original base. Near-miss challenges preserve the neighbour's own cap-off response and use distinct-subject relation/template families, not semantic nearest neighbours. The full text assay covers **1,931 windows / 245,237 positions**; the fixed descriptive prefix covers **128 windows / 16,256 positions**. The complete methods, denominators, termination diagnostics and endpoint contracts are retained in [S] [A] [M].

DEC-069 keeps the **63 metric slots** and registered labels, but treats the three-realization ranges as preliminary decision summaries. Orders and tokens are not extra independent realizations; no demonstrated 95% familywise guarantee is claimed. Pointwise Student-t sensitivity assumes independent normal realization errors, has **2 degrees of freedom**, and never changes classification. [P] [D]

## Execution disposition and DEC-052 inventory

**270 completed cells out of 330 declared**, with zero failed attempts and zero retries; **60 scheduled cells** remain unrun by decision, not technical failure. The blocks and all excluded coordinates remain visible. [B] [K] [R]

| Block | Completed / declared | Disposition |
| --- | --- | --- |
| 1 | 45/45 | complete |
| 2 | 45/45 | complete |
| 3 | 45/45 | complete |
| 4 | 90/90 | complete |
| 5 | 45/60 | partially/unrun by DEC-074b |
| 6 | 0/45 | partially/unrun by DEC-074b |

The published omission CSV has **11 rows**: **eight unavailable primary contrasts** (24 metric slots) plus **three dataset entries for the optional extension**. The extension's native secondary table retains eight comparisons / 24 metric rows; these are a different denominator. The **75 prospectively omitted MQuAKE comparator coordinates** under DEC-066 are outside the reduced 330-cell execution matrix and must not be added to its 60 unrun cells. [U] [A] [M]

| Dataset | Unavailable inventory entry | Reason |
| --- | --- | --- |
| counterfact | primary-vs-S1_literal | Not run under DEC-074b: stop at 270 excludes S1_literal CounterFact. |
| mquake | primary-vs-R1_nonlearned | MQuAKE ends at 300; registered 1000-edit contrast unavailable (DEC-066); no substitution. |
| mquake | primary-vs-v0_stable | MQuAKE ends at 300; registered 1000-edit contrast unavailable (DEC-066); no substitution. |
| mquake | primary-vs-matched_update | MQuAKE comparator prospectively omitted under DEC-066 (zero calibrated radius); retained as unavailable. |
| mquake | primary-vs-v0_live_C1 | MQuAKE comparator prospectively omitted under DEC-066 (zero calibrated radius); retained as unavailable. |
| mquake | primary-vs-v0_live_C2 | MQuAKE comparator prospectively omitted under DEC-066 (zero calibrated radius); retained as unavailable. |
| mquake | primary-vs-S1_LM | MQuAKE comparator prospectively omitted under DEC-066 (zero calibrated radius); retained as unavailable. |
| mquake | primary-vs-S1_literal | MQuAKE comparator prospectively omitted under DEC-066 (zero calibrated radius); retained as unavailable. |
| zsre | historical-v2 extension (secondary) | Optional 45-cell block 6 not run under DEC-074b; outside the 63 primary metric slots. |
| counterfact | historical-v2 extension (secondary) | Optional 45-cell block 6 not run under DEC-074b; outside the 63 primary metric slots. |
| mquake | historical-v2 extension (secondary) | Optional 45-cell block 6 not run under DEC-074b; outside the 63 primary metric slots. |

## Registered primary comparisons

The following copies the published RET-GS row of each available contrast; values are learned minus control. Every ES/LS row, both registered interval columns, all five order differences within each realization and their dispersion remain in [P] [A]. The jointly classified comparisons comprise **9 preliminary positive** and **4 inconclusive**, plus **8 unavailable**. A label is not a new efficacy guarantee. [P]

| Dataset | Control | RET-GS difference | r0, r1, r2 | Registered range | t sensitivity | Existing joint class |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | R1_nonlearned | 0.43633333 | 0.453000, 0.435000, 0.421000 | 0.421000, 0.453000 | 0.396484, 0.476183 | positive |
| zsre | v0_stable | 0.77473333 | 0.770800, 0.787600, 0.765800 | 0.765800, 0.787600 | 0.746365, 0.803102 | positive |
| zsre | matched_update | 0.77666667 | 0.774600, 0.784800, 0.770600 | 0.770600, 0.784800 | 0.758478, 0.794856 | positive |
| zsre | v0_live_C1 | 0.82993333 | 0.829200, 0.838000, 0.822600 | 0.822600, 0.838000 | 0.810741, 0.849126 | positive |
| zsre | v0_live_C2 | 0.85306667 | 0.858200, 0.861600, 0.839400 | 0.839400, 0.861600 | 0.823363, 0.882770 | positive |
| zsre | S1_LM | 0.77373333 | 0.765000, 0.787400, 0.768800 | 0.765000, 0.787400 | 0.743955, 0.803511 | positive |
| zsre | S1_literal | 0.7716 | 0.765600, 0.788000, 0.761200 | 0.761200, 0.788000 | 0.735897, 0.807303 | positive |
| counterfact | R1_nonlearned | 0.5575 | 0.565500, 0.545000, 0.562000 | 0.545000, 0.565500 | 0.530259, 0.584741 | positive |
| counterfact | v0_stable | 0.678 | 0.691500, 0.666000, 0.676500 | 0.666000, 0.691500 | 0.646163, 0.709837 | inconclusive |
| counterfact | matched_update | 0.678 | 0.691500, 0.666000, 0.676500 | 0.666000, 0.691500 | 0.646163, 0.709837 | inconclusive |
| counterfact | v0_live_C1 | 0.678 | 0.691500, 0.666000, 0.676500 | 0.666000, 0.691500 | 0.646163, 0.709837 | inconclusive |
| counterfact | v0_live_C2 | 0.678 | 0.691500, 0.666000, 0.676500 | 0.666000, 0.691500 | 0.646163, 0.709837 | inconclusive |
| counterfact | S1_LM | 0.678 | 0.691500, 0.666000, 0.676500 | 0.666000, 0.691500 | 0.646163, 0.709837 | positive |

CounterFact versus stable v0, matched update and both live-v0 arms remains inconclusive because the learned reader's locality reaches **48/50** in realization 2, despite retained paraphrase gains. CounterFact versus S1_LM is positive under the installed classifier because that control also loses locality. All three metrics, rather than RET-GS alone, determine these labels. [T] [C] [P]

## Secondary behavior and specificity

zsRE learned-reader near-miss preservation is **86/100, 92/100 and 87/100** across realizations despite perfect ordinary locality. Its unseen-prompt false-fire rates at 1,000 records are **0.09, 0.13 and 0.16**; the published macro 0.12666667 passes the secondary 0.15 threshold, but that does not erase the failing realization's cells. Revision semantics, planned/scored/missing counts, the historical-v2 table and full checkpoint trajectories remain separate in the appendix; composition and compatible resource-ratio reporting remain unavailable. [T] [Q] [A]

## MQuAKE at 300 edits and prospective omissions

The published learned-reader realization RET-GS values are **0.703333, 0.723333 and 0.720000**. Its actual-occupancy 300-record outside-fire measurements and descriptive Wilson reference intervals are reported in the appendix, without importing a 1,000-record threshold. All **seven registered MQuAKE contrasts / 21 metric slots** at 1,000 stay unavailable: the two triplet controls lack that endpoint, and the five additional controls were prospectively omitted under DEC-066. [T] [P] [U] [A]

## Fidelity benchmarks, watch and concentrated harm

Mean KL **≤0.001** and mean signed ΔNLL **≤0.01 nats** are secondary benchmarks under DEC-064; artifact integrity and scientific admission do not imply benchmark success. Original-base and own-cap-off references remain separate, particularly for continued-base controls. The appendix retains every cell's mean, fractional ES95/ES99, maxima/location/ties, strict exceedances, zero atoms and concentration; no heavy-tail family or power-law exponent is established. [S] [A] [D]

For example, the completed S1_literal zsRE group has positive-harm ES99 mean **0.179435633 nats**, with three-realization range **0.132983454–0.213079580**; mean per-cell half-mass count is **19.133333 positions**. This is the cap-versus-own-cap-off contrast; it does not describe the continued base's change from the original model. Realization ranges are descriptive, and repeated positions are not independent replicates. [F]

The journal has 274 observations (270 confirmation, four development), 163 breach entries and 32 creep alerts. These totals include development entries; no alert is an admission veto. Watch generation does not certify that a human received a notification. [W]

## Execution history and resource accounting

The freeze was published **September 18** (DEC-071); first dispatch followed that day. The **September 20** Q21 drain at the block-2 boundary changed only the effective two-worker ceiling multiplier, **1.15 → 1.7**, preserving solo ceilings, scientific recipes, the **750 process-hour** shared cap and the October 9 stop. Bindings v1 apply to cells 1–90, v2 thereafter. At the approved **270th start**, the September 26 **22:18:59 EDT** halt trigger fired; the two active processes completed and the scheduler exited **23:43:25 EDT**. [D] [V] [R]

Four parent decisions are absent: stable-v0 MQuAKE realization 1 orders 103/104 at Q21, and S1_literal zsRE realization 2 orders 103/104 at the final halt. Their completed starts/finishes and driver outputs remain charged; the owner recorded the missing watch updates after reconciliation. No parent decision was manufactured. [K] [R]

Measured execution charges total **392.419650444 process-hours**, matching the halt ledger, with **0 unknown-cost records** and zero uncovered driver time. Concurrent process envelopes are summed once; nested driver timings are not added. These are not GPU elapsed hours and exclude development, continuation training and the separate PC supplement. The halt report's **308.369269 boundary hours** cover the last *complete block* (block 4), not the whole 270-cell spend; block 5 is intentionally partial. Repricing proposals in that report are not new measured costs or launch approvals. [H] [K]

| Condition | zsRE process-hours | CounterFact process-hours | MQuAKE process-hours |
| --- | --- | --- | --- |
| R1_learned_ff | 18.367340 | 17.796612 | 8.806084 |
| R1_nonlearned | 9.047291 | 8.931926 | 5.606416 |
| v0_stable | 19.746292 | 40.501561 | 12.167088 |
| matched_update | 17.418466 | 39.044156 | not run |
| v0_live_C1 | 19.692800 | 40.398012 | not run |
| v0_live_C2 | 17.553194 | 33.292030 | not run |
| S1_LM | 21.213483 | 41.485509 | not run |
| S1_literal | 21.351390 | not run | not run |

The table groups the existing per-cell charges by condition/dataset, with only summation and seconds-to-hours conversion. Full process records, coverage of driver attempts, failures and missing decisions are in [H] [K].

## Continued-base controls and interpretation

S1_LM was measured for both main datasets; S1_literal only for zsRE. These are package comparisons, not a factorial isolation of every cap component, and there is no direct fine-tuning-on-edits control. CounterFact retains its approved source exception. The predominance of initially unanswered zsRE prompts limits an interpretation solely as correction of answered facts. The κ pilot, PC refocus and coupled-free-energy/active-inference programme do not become confirmatory arms by being discussed alongside this report. [C] [S] [D]

## Figure inventory and complete tables

The native filled skeleton [A] supplies all registered table categories and figure-data pointers. Existing comparator and triplet figures are linked in [C] [T]; the updated per-cell tail table [F] adds descriptive realization spread. No fresh plot or experimental measurement is required for this assembly. In the historical native appendix the generic execution-accounting adapter still says unavailable because it was not supplied there; the verified halt and selected-process records [H] [K] above explicitly supply that section for this assembled report.

## Completion, limitations and reproducibility

The base is GPT-2 small (124M parameters); transfer of these findings to production-scale models has not been established. DEC-074b left S1_literal CounterFact and the original optional extension unavailable. The later supplemental Option R study is separate; its stable-v0 class is deferred under DEC-080.

The main run is complete to the lead's reduced halt scope, while omitted comparisons remain unavailable. Experiments stop **October 9 at 17:00 ET**, with the **October 15** presentation later; preparation time is not experimental time. Development selection, three realization clusters, dependent orders, source-population exceptions and incomplete architectural/control coverage constrain generalization. PC-v0 and fixed-v5 supplemental findings are outside this main-study report until independently completed. [D] [T] [R]

Reproduce this assembly with `python -m aw.stage4_assembly --output NEW_ASSEMBLY_DIRECTORY --document NEW_REPORT.md` (explicit new-path placeholders). The [source registry](../stage4/sources.md) and [assembly record](../stage4/assembly.json) bind all cited files, unchanged copied primary rows and accounting arithmetic. The original registered analyzer and classifier were not rerun or altered.

[S]: ../../../../../docs/R1_stage4_report_skeleton.md "SHA256 944c5d935c048f4d556d90807db32d69ffa1a6f9ce0d070be627d7999d9cbd05"

[T]: ../../../../../docs/R1_stage4_report_triplet.md "SHA256 a1b2ed533422d7d563354b7f827e0c168e1808abf43e133f8f325a28c264b964"

[C]: ../../../../../docs/R1_stage4_report_comparators.md "SHA256 5ec5887173889aaefc97e8be5328613bd31863a1ddd5981119a86e1aba740afc"

[P]: ../../../../R1/reports/comparators-270/appendix/primary.csv "SHA256 c3ca7f3a1dcdbd4fc16263654a76f4447290185632abc6c662f76175be8f1a58"

[A]: ../../../../R1/reports/comparators-270/appendix/report.md "SHA256 ea7e85a8c7b94f3848af691f1bd34f311efe41766469310491ae0a19e27ba714"

[U]: ../../../../R1/reports/comparators-270/unavailable.csv "SHA256 91e16240c675c92230fbf3da1eca416f6e5006fff9c8ee0c0ad10e6e50def208"

[B]: ../../../../R1/reports/comparators-270/appendix/blocks.csv "SHA256 fa90b6e8ff6b880fc944582759782287c2715272cd7db4eddb61ae0c496d6d64"

[Q]: ../../../../R1/reports/comparators-270/appendix/secondary_macros.csv "SHA256 5b8a46125d31675b1f9a6614c75b71645b850ebf6e24d65c3bf316e398c9fed4"

[H]: ../../../../R1/operations/HALT_REPORT/d11-report.json "SHA256 b1550760d9e5b1807c59a604e8a4c91155d7e6e3ce62e58be04d7b1ac12f8d8a"

[K]: ../../../../R1/reports/comparators-270/accounting.json "SHA256 9d94304045c4e3cc8630ccedc6a37baeabe49aeead180ee5606a0fef50d4f923"

[W]: ../../../../R1/reports/comparators-270/appendix/watch_summary.csv "SHA256 194cb8a9f8a6d4c892d73a783234ec73f586210d69187f1091710c6e1d0207a2"

[R]: ../../../../R1/operations/Q21_cutover/halt-reconciliation.md "SHA256 5d15ca4616264073fa2d746eb33d638c0b3da32b80414411cb335e454e7087c4"

[V]: ../../../../../docs/tasks/R1-final-queue-bindings-v2.json "SHA256 c6f88c56814f3ff265401cefce2c51773de49e0fbb7ddb4e0cbbbdda75eb721c"

[D]: ../../../../../docs/decisions.md "SHA256 25f4f95524df9065957b7dec879ee57ad2503426ab06ad0124e24defe32983a7"

[M]: ../../../../../manifests/revision_v1/run_matrix_final.json "SHA256 06fa8b3b3f3d734c12d47ac2b1b09d8dcd0c35c203013456c9409590329d56bb"

[F]: ../ht15/cell_tails.json "SHA256 d0e2da3a65779d8495f1e9f318b3c557592be799c1a39dfcb96651e8059605c4"

[G]: ../../../../R1/reports/comparators-270/report.json "SHA256 739034d75b489bf553bb852cf464021e7a78fd63c51c05a4eefcfc01bc721814"
