# Round 48 — Capex handoff

2026-09-27. CPU work complete in PC-7, PRES-4 and HT-15b. PC-8 awaits the live
experiment and Capstan's harm readout. No GPU was used; no commit or staging was
performed. No file under `scripts/` or `src/pccap/` was added or edited, and the
running `aw/pc_v0.py` remains unchanged.

| Lane | Delivered | Next step |
| --- | --- | --- |
| [PC-7](PC-7.md) | Fixed-v5 paired driver; native R1 assays; 100/300 snapshots; fresh-memory paired checks; ten-item development profile gate; actual CPU smoke | Capstan profiles four development cells, inspects phase costs, then runs the four exposed cells after the PC-v0/harm chain |
| [PRES-4](PRES-4.md) | Slides 9/10 and closing PC slot; complete-source result resolution; twelve-slide export; active inference/PC/tail framing retained | Re-export with completed result sources; author reviews wording |
| [HT-15b](HT-15b.md) | Receipt-filtered 270-cell tails, refreshed page/table/CSV/JSON, three-realization spread | Available now for the presentation |
| [PC-8](PC-8.md) | Completion check and publication checklist | Wait for all 60 cells and harm; 21/60 completed at 07:13 EDT |

PC-7 GPU commands and explicitly proposed new output paths are in its task
record. Lead queue 121 lifted the earlier Monday hold. The original BP tensors,
selected v5 reader, gates, calibration and seed are identical across arms; only
acquisition credit changes. CPU validation does not establish GPU speed or real
300-item efficacy. Both 100/300 challenge passes and the separate full-text harm
readout must be included in the cost forecast. PC-6 supplies the readout adapter;
Capstan still owns its production GPU integration and the shared harm allowance.

One small pre-launch integration repair: `aw/pc_harm_readout.py` now imports the
same owner-approved occupancy classifier as PC-v0/PC-7, records other contexts,
and refuses occupancy-query failures. It previously blocked on desktop contexts.
Its scoring and vectors are unchanged. The helper relies on readable commands
and does not classify inaccessible PIDs or non-Python compute outside the project
as blockers; review note is in PC-7. The source-bound active runner was not edited.

Verification: **96 CPU tests passed, two slow fixtures deselected**; scoped lint
passes. The persistent paired tiny-model run is
`results/additional_work/PC-v1/cpu-smoke-round48/`; its checkpoints are under
`assets/runs/additional_work/PC-v1/cpu-smoke-round48/`. It is implementation
evidence, not a research result. Historical smoke outputs remain unchanged.
Tests now generate current-source smoke evidence instead of trusting an old
runner hash; the occupancy test uses controlled process commands instead of
assuming that PID 1 is system init. Logs and final validation records are under
`logs/additional_work/round48/`.

The reviewed slide export is
`assets/presentation-materials/deck_v3/round48-reviewed/`. All twelve slides have
valid claim references and no detected text overflow; slides 9/10/12 were visually
reviewed. PC values remain visibly pending. The refreshed tail page reports
S1_literal zsRE ES99 mean 0.179435633 nats and three-realization range
0.132983454–0.213079580; all 262 earlier cell records are unchanged.

Live PC-v0 result/log changes and final-queue logs visible in `git status` belong
to ongoing operations, not this CPU handoff. They were neither edited nor staged.
