# Option R — partial extension report

Capex · saved CPU analysis · {'complete': 4, 'incomplete_by_ceiling': 1, 'deferred DEC-080': 9, 'pending': 16} out of 30 original planned cells.
Numerical record, per-order metrics/denominators and source hashes: `/home/derp/cap/pc_cap/logs/additional_work/reproductions/round60-check1/option-r/report.json`.

Realization 3 adds reserved subjects for the unchanged learned and random readers, five orders each on zsRE and CounterFact. It is supplemental to realizations 0–2. **DEC-080 defers the nine unrun stable-v0 cells; the earlier ceiling-killed stable-v0 cell remains incomplete by ceiling.** Its receipted intermediate checkpoints are descriptive evidence, not completion. No substituted condition or raised ceiling is introduced.

## Inventory, ceilings and charged attempts

| Dataset | Condition | Order | Disposition | Saved checkpoints | Dispatches | Charged process s | Ceiling s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | R1_learned_ff | 100 | complete | 100,300,1000 | 1 | 4448.585 | 7559.598 |
| zsre | R1_nonlearned | 100 | complete | 100,300,1000 | 1 | 1890.357 | 3664.722 |
| zsre | v0_stable | 100 | incomplete_by_ceiling | 100,300 | 1 | 8002.051 | 8001.942 |
| zsre | R1_learned_ff | 101 | complete | 100,300,1000 | 1 | 4281.479 | 7559.598 |
| zsre | R1_nonlearned | 101 | complete | 100,300,1000 | 1 | 1795.923 | 3664.722 |
| zsre | v0_stable | 101 | deferred DEC-080 |  | 0 | 0 | 8001.942 |
| zsre | R1_learned_ff | 102 | pending |  | 0 | 0 | 7559.598 |
| zsre | R1_nonlearned | 102 | pending |  | 0 | 0 | 3664.722 |
| zsre | v0_stable | 102 | deferred DEC-080 |  | 0 | 0 | 8001.942 |
| zsre | R1_learned_ff | 103 | pending |  | 0 | 0 | 7559.598 |
| zsre | R1_nonlearned | 103 | pending |  | 0 | 0 | 3664.722 |
| zsre | v0_stable | 103 | deferred DEC-080 |  | 0 | 0 | 8001.942 |
| zsre | R1_learned_ff | 104 | pending |  | 0 | 0 | 7559.598 |
| zsre | R1_nonlearned | 104 | pending |  | 0 | 0 | 3664.722 |
| zsre | v0_stable | 104 | deferred DEC-080 |  | 0 | 0 | 8001.942 |
| counterfact | R1_learned_ff | 100 | pending |  | 0 | 0 | 7254.731 |
| counterfact | R1_nonlearned | 100 | pending |  | 0 | 0 | 3605.04 |
| counterfact | v0_stable | 100 | deferred DEC-080 |  | 0 | 0 | 16463.04 |
| counterfact | R1_learned_ff | 101 | pending |  | 0 | 0 | 7254.731 |
| counterfact | R1_nonlearned | 101 | pending |  | 0 | 0 | 3605.04 |
| counterfact | v0_stable | 101 | deferred DEC-080 |  | 0 | 0 | 16463.04 |
| counterfact | R1_learned_ff | 102 | pending |  | 0 | 0 | 7254.731 |
| counterfact | R1_nonlearned | 102 | pending |  | 0 | 0 | 3605.04 |
| counterfact | v0_stable | 102 | deferred DEC-080 |  | 0 | 0 | 16463.04 |
| counterfact | R1_learned_ff | 103 | pending |  | 0 | 0 | 7254.731 |
| counterfact | R1_nonlearned | 103 | pending |  | 0 | 0 | 3605.04 |
| counterfact | v0_stable | 103 | deferred DEC-080 |  | 0 | 0 | 16463.04 |
| counterfact | R1_learned_ff | 104 | pending |  | 0 | 0 | 7254.731 |
| counterfact | R1_nonlearned | 104 | pending |  | 0 | 0 | 3605.04 |
| counterfact | v0_stable | 104 | deferred DEC-080 |  | 0 | 0 | 16463.04 |

Closed execution segments total 2.9244 wall-hours of the existing 30-hour ceiling; 0 segments are open and have unclosed cost. Dispatch receipts total 5.6718 process-hours. Overlapping workers explain the difference; do not add these totals or charge idle time between resumes. Parent process envelopes already include driver work, including the killed attempt; the reconciliation adds no charge. Unknown attempts: 0.

| Segment | Status | Wall s | Finish reason |
| --- | --- | --- | --- |
| /home/derp/cap/pc_cap/logs/additional_work/R/queue/20260929T174143/session-start.json | stopped | 10527.93 | ValueError('unknown/torn attempt cost; reconcile before resuming') |

## Behavior at 100, 300 and 1,000 edits

Each value averages the available receipted orders within one subject realization. The fraction is available orders / five planned; an incomplete row is not the planned five-order mean. Denominators and raw order values remain in JSON. Intermediate checkpoints from the ceiling-killed cell are retained here only; no incomplete cell enters the four-realization sensitivity.

| Dataset | r | Condition | Edits | Orders/5 (ES,RET-ES,RET-GS,LS) | ES | RET-ES | RET-GS | LS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | R1_learned_ff | 100 | 5/5/5/5 | 1 | 1 | 0.986 | 1 |
| zsre | 0 | R1_learned_ff | 300 | 5/5/5/5 | 1 | 1 | 0.984 | 1 |
| zsre | 0 | R1_learned_ff | 1000 | 5/5/5/5 | 0.9936 | 0.977 | 0.955 | 1 |
| zsre | 0 | R1_nonlearned | 100 | 5/5/5/5 | 1 | 1 | 0.626 | 1 |
| zsre | 0 | R1_nonlearned | 300 | 5/5/5/5 | 1 | 1 | 0.566 | 0.996 |
| zsre | 0 | R1_nonlearned | 1000 | 5/5/5/5 | 1 | 1 | 0.502 | 0.98 |
| zsre | 0 | v0_stable | 100 | 5/5/5/5 | 1 | 0.996 | 0.464 | 0.988 |
| zsre | 0 | v0_stable | 300 | 5/5/5/5 | 1 | 0.9886667 | 0.3306667 | 1 |
| zsre | 0 | v0_stable | 1000 | 5/5/5/5 | 1 | 0.66 | 0.1842 | 1 |
| zsre | 1 | R1_learned_ff | 100 | 5/5/5/5 | 1 | 1 | 0.98 | 1 |
| zsre | 1 | R1_learned_ff | 300 | 5/5/5/5 | 1 | 0.9993333 | 0.9773333 | 1 |
| zsre | 1 | R1_learned_ff | 1000 | 5/5/5/5 | 0.9948 | 0.985 | 0.965 | 1 |
| zsre | 1 | R1_nonlearned | 100 | 5/5/5/5 | 1 | 1 | 0.66 | 1 |
| zsre | 1 | R1_nonlearned | 300 | 5/5/5/5 | 1 | 1 | 0.5826667 | 1 |
| zsre | 1 | R1_nonlearned | 1000 | 5/5/5/5 | 1 | 1 | 0.53 | 1 |
| zsre | 1 | v0_stable | 100 | 5/5/5/5 | 1 | 0.994 | 0.422 | 0.972 |
| zsre | 1 | v0_stable | 300 | 5/5/5/5 | 1 | 0.9813333 | 0.3073333 | 0.924 |
| zsre | 1 | v0_stable | 1000 | 5/5/5/5 | 0.9996 | 0.6474 | 0.1774 | 0.936 |
| zsre | 2 | R1_learned_ff | 100 | 5/5/5/5 | 1 | 1 | 0.99 | 1 |
| zsre | 2 | R1_learned_ff | 300 | 5/5/5/5 | 1 | 1 | 0.9826667 | 1 |
| zsre | 2 | R1_learned_ff | 1000 | 5/5/5/5 | 0.9948 | 0.985 | 0.961 | 1 |
| zsre | 2 | R1_nonlearned | 100 | 5/5/5/5 | 1 | 1 | 0.68 | 1 |
| zsre | 2 | R1_nonlearned | 300 | 5/5/5/5 | 1 | 1 | 0.6073333 | 1 |
| zsre | 2 | R1_nonlearned | 1000 | 5/5/5/5 | 1 | 1 | 0.54 | 1 |
| zsre | 2 | v0_stable | 100 | 5/5/5/5 | 1 | 0.992 | 0.426 | 0.988 |
| zsre | 2 | v0_stable | 300 | 5/5/5/5 | 1 | 0.986 | 0.3286667 | 0.996 |
| zsre | 2 | v0_stable | 1000 | 5/5/5/5 | 1 | 0.693 | 0.1952 | 0.976 |
| zsre | 3 | R1_learned_ff | 100 | 2/2/2/2 | 1 | 1 | 0.985 | 1 |
| zsre | 3 | R1_learned_ff | 300 | 2/2/2/2 | 1 | 1 | 0.9783333 | 1 |
| zsre | 3 | R1_learned_ff | 1000 | 2/2/2/2 | 0.997 | 0.989 | 0.969 | 1 |
| zsre | 3 | R1_nonlearned | 100 | 2/2/2/2 | 1 | 1 | 0.655 | 1 |
| zsre | 3 | R1_nonlearned | 300 | 2/2/2/2 | 1 | 1 | 0.575 | 1 |
| zsre | 3 | R1_nonlearned | 1000 | 2/2/2/2 | 1 | 1 | 0.515 | 1 |
| zsre | 3 | v0_stable | 100 | 1/1/1/1 | 1 | 0.98 | 0.46 | 1 |
| zsre | 3 | v0_stable | 300 | 1/1/1/1 | 1 | 0.97 | 0.3066667 | 0.98 |
| zsre | 3 | v0_stable | 1000 | 0/0/0/0 | — | — | — | — |
| counterfact | 0 | R1_learned_ff | 100 | 5/5/5/5 | 1 | 1 | 0.807 | 0.996 |
| counterfact | 0 | R1_learned_ff | 300 | 5/5/5/5 | 0.9993333 | 0.9993333 | 0.767 | 0.996 |
| counterfact | 0 | R1_learned_ff | 1000 | 5/5/5/5 | 0.9914 | 0.974 | 0.6915 | 1 |
| counterfact | 0 | R1_nonlearned | 100 | 5/5/5/5 | 1 | 1 | 0.194 | 0.084 |
| counterfact | 0 | R1_nonlearned | 300 | 5/5/5/5 | 1 | 1 | 0.1323333 | 0.024 |
| counterfact | 0 | R1_nonlearned | 1000 | 5/5/5/5 | 1 | 1 | 0.126 | 0.02 |
| counterfact | 0 | v0_stable | 100 | 5/5/5/5 | 1 | 1 | 0 | 1 |
| counterfact | 0 | v0_stable | 300 | 5/5/5/5 | 1 | 1 | 0 | 1 |
| counterfact | 0 | v0_stable | 1000 | 5/5/5/5 | 1 | 1 | 0 | 1 |
| counterfact | 1 | R1_learned_ff | 100 | 5/5/5/5 | 1 | 1 | 0.742 | 1 |
| counterfact | 1 | R1_learned_ff | 300 | 5/5/5/5 | 1 | 0.9986667 | 0.7313333 | 0.992 |
| counterfact | 1 | R1_learned_ff | 1000 | 5/5/5/5 | 0.9936 | 0.981 | 0.666 | 1 |
| counterfact | 1 | R1_nonlearned | 100 | 5/5/5/5 | 1 | 1 | 0.182 | 0.096 |
| counterfact | 1 | R1_nonlearned | 300 | 5/5/5/5 | 1 | 1 | 0.1353333 | 0.02 |
| counterfact | 1 | R1_nonlearned | 1000 | 5/5/5/5 | 1 | 1 | 0.121 | 0 |
| counterfact | 1 | v0_stable | 100 | 5/5/5/5 | 1 | 1 | 0 | 1 |
| counterfact | 1 | v0_stable | 300 | 5/5/5/5 | 1 | 1 | 0 | 1 |
| counterfact | 1 | v0_stable | 1000 | 5/5/5/5 | 1 | 1 | 0 | 1 |
| counterfact | 2 | R1_learned_ff | 100 | 5/5/5/5 | 1 | 1 | 0.789 | 0.996 |
| counterfact | 2 | R1_learned_ff | 300 | 5/5/5/5 | 1 | 1 | 0.7503333 | 0.988 |
| counterfact | 2 | R1_learned_ff | 1000 | 5/5/5/5 | 0.9938 | 0.976 | 0.6765 | 0.96 |
| counterfact | 2 | R1_nonlearned | 100 | 5/5/5/5 | 1 | 1 | 0.159 | 0.188 |
| counterfact | 2 | R1_nonlearned | 300 | 5/5/5/5 | 1 | 1 | 0.148 | 0.016 |
| counterfact | 2 | R1_nonlearned | 1000 | 5/5/5/5 | 1 | 1 | 0.1145 | 0 |
| counterfact | 2 | v0_stable | 100 | 5/5/5/5 | 1 | 1 | 0 | 1 |
| counterfact | 2 | v0_stable | 300 | 5/5/5/5 | 1 | 1 | 0 | 1 |
| counterfact | 2 | v0_stable | 1000 | 5/5/5/5 | 1 | 1 | 0 | 1 |
| counterfact | 3 | R1_learned_ff | 100 | 0/0/0/0 | — | — | — | — |
| counterfact | 3 | R1_learned_ff | 300 | 0/0/0/0 | — | — | — | — |
| counterfact | 3 | R1_learned_ff | 1000 | 0/0/0/0 | — | — | — | — |
| counterfact | 3 | R1_nonlearned | 100 | 0/0/0/0 | — | — | — | — |
| counterfact | 3 | R1_nonlearned | 300 | 0/0/0/0 | — | — | — | — |
| counterfact | 3 | R1_nonlearned | 1000 | 0/0/0/0 | — | — | — | — |
| counterfact | 3 | v0_stable | 100 | 0/0/0/0 | — | — | — | — |
| counterfact | 3 | v0_stable | 300 | 0/0/0/0 | — | — | — | — |
| counterfact | 3 | v0_stable | 1000 | 0/0/0/0 | — | — | — | — |

## Learned minus random: four-realization sensitivity

First average the five paired order differences within each realization; then average four realization means. Display estimate ± t(3, .975) × sample SD / √4, with t=3.1824463. Orders are dependent and are not 20 independent replications. The interval is a small-cluster sensitivity, not newly established coverage. **No registered family is rerun and no classifier labels are reissued.** Until all five pairs in all four realizations are complete, the t(3) estimate and interval are withheld; available-order differences stay in JSON.

| Dataset | Edits | Metric | Paired orders per r0/r1/r2/r3 | Estimate | 95% t(3) display | Status |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 100 | ES | 5/5/5/2 | — | — | withheld: incomplete five-order pairing |
| zsre | 100 | RET-ES | 5/5/5/2 | — | — | withheld: incomplete five-order pairing |
| zsre | 100 | RET-GS | 5/5/5/2 | — | — | withheld: incomplete five-order pairing |
| zsre | 100 | LS | 5/5/5/2 | — | — | withheld: incomplete five-order pairing |
| zsre | 300 | ES | 5/5/5/2 | — | — | withheld: incomplete five-order pairing |
| zsre | 300 | RET-ES | 5/5/5/2 | — | — | withheld: incomplete five-order pairing |
| zsre | 300 | RET-GS | 5/5/5/2 | — | — | withheld: incomplete five-order pairing |
| zsre | 300 | LS | 5/5/5/2 | — | — | withheld: incomplete five-order pairing |
| zsre | 1000 | ES | 5/5/5/2 | — | — | withheld: incomplete five-order pairing |
| zsre | 1000 | RET-ES | 5/5/5/2 | — | — | withheld: incomplete five-order pairing |
| zsre | 1000 | RET-GS | 5/5/5/2 | — | — | withheld: incomplete five-order pairing |
| zsre | 1000 | LS | 5/5/5/2 | — | — | withheld: incomplete five-order pairing |
| counterfact | 100 | ES | 5/5/5/0 | — | — | withheld: incomplete five-order pairing |
| counterfact | 100 | RET-ES | 5/5/5/0 | — | — | withheld: incomplete five-order pairing |
| counterfact | 100 | RET-GS | 5/5/5/0 | — | — | withheld: incomplete five-order pairing |
| counterfact | 100 | LS | 5/5/5/0 | — | — | withheld: incomplete five-order pairing |
| counterfact | 300 | ES | 5/5/5/0 | — | — | withheld: incomplete five-order pairing |
| counterfact | 300 | RET-ES | 5/5/5/0 | — | — | withheld: incomplete five-order pairing |
| counterfact | 300 | RET-GS | 5/5/5/0 | — | — | withheld: incomplete five-order pairing |
| counterfact | 300 | LS | 5/5/5/0 | — | — | withheld: incomplete five-order pairing |
| counterfact | 1000 | ES | 5/5/5/0 | — | — | withheld: incomplete five-order pairing |
| counterfact | 1000 | RET-ES | 5/5/5/0 | — | — | withheld: incomplete five-order pairing |
| counterfact | 1000 | RET-GS | 5/5/5/0 | — | — | withheld: incomplete five-order pairing |
| counterfact | 1000 | LS | 5/5/5/0 | — | — | withheld: incomplete five-order pairing |

## Fidelity watch

Final full ordinary-text assay: 245,237 positions per completed cell. Mean KL .001 is a labelled secondary benchmark, not an integrity veto; original and own-cap-off references remain separate. The watch observations and all alert records are retained in JSON.

| Dataset | Condition | Order | Reference | Mean KL | Mean ΔNLL | KL≤.001 | Watch recorded |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | R1_learned_ff | 100 | capoff | 0.002283354 | 0.002442997 | False | True |
| zsre | R1_learned_ff | 100 | original | 0.002283354 | 0.002442997 | False | True |
| zsre | R1_nonlearned | 100 | capoff | 0.0002066747 | 0.0001902784 | True | True |
| zsre | R1_nonlearned | 100 | original | 0.0002066747 | 0.0001902784 | True | True |
| zsre | R1_learned_ff | 101 | capoff | 0.002283354 | 0.002442997 | False | True |
| zsre | R1_learned_ff | 101 | original | 0.002283354 | 0.002442997 | False | True |
| zsre | R1_nonlearned | 101 | capoff | 0.0002066747 | 0.0001902784 | True | True |
| zsre | R1_nonlearned | 101 | original | 0.0002066747 | 0.0001902784 | True | True |

Historical comparison source: `/home/derp/cap/pc_cap/logs/R1/reports/triplet/analysis.json`. The extension does not test PC credit or interventions developed from earlier populations. It supplies one additional subject realization, not extra independent evidence from every order/token.

Refresh after the owner's resumed queue finishes (new report directory):

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
../venv/bin/python -m aw.r_report --output logs/additional_work/R/report-NEW
```

The generator uses the existing read-only `status`/`resume_inventory` and native receipt/checkpoint summarizer. It never dispatches, repairs a run, writes watch state or calls a model. Unclosed segments remain unknown. Original 30-hour ceiling, one retry, fixed scientific recipes and October 9 at 17:00 EDT cutoff remain unchanged.
