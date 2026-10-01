# AW-B4 — bounded-correction final report

Status: done. Agent: Capex. Updated October 1, 2026. CPU analysis only; no new GPU/model calls.

Inputs: completed calibration-20260929 and evaluation-20260929. The existing
report generator independently reconstructed **62 dataset/setting records**:
32 development records plus 30 final evaluation records. Full vectors, endpoint
scores, identities, selection and success conjunction verify.

Outputs: `docs/additional_work/AW-B_report.md`; report JSON/publication receipt
under `logs/additional_work/AW-B/report-20260929/`; final survival PNG/PDF/SVG and
manifest in `assets/presentation-materials/figures/aw_b/`; AW-B ledger row,
reviewer table and slide 8. All sixteen development settings, selection reasons,
per-order differences and separate calibration/evaluation costs are included.

The selected exp(-1) base mixture passes in all ten evaluation memories. zsRE
endpoints are unchanged; CounterFact RET-GS loses 0.006667–0.011667. Mean KL clears
0.001 for zsRE but not CounterFact. The bound is **one nat per token at the same
prefix versus the same base**. It does not ensure unchanged greedy answers or
one-nat sequence/generated-text loss. No shrink/gate comparator qualified.
DEC-078 framing remains an intervention beside the κ pilot, not a recommended
configuration or proof of a heavy-tail family.

Verification: `python -m aw.aw_b_report --final`, then system Python
`-m aw.aw_b_tail_figure --report logs/additional_work/AW-B/report-20260929/report.json`.
Part of 30 passing targeted CPU tests; strict survival steps, complete population,
partial-result refusal and dataset-specific slide qualification tested. Final
figure visually inspected. Logs: `logs/additional_work/round55/tests.txt`.

Done-when: all final report/figure/claim/reviewer outputs published — met.
Dependencies: PRES-6 delivered. Questions/deviations: none. No commit by Capex.
