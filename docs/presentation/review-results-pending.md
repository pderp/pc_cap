# Corrected predictive-coding results — PENDING scaffold

Prepared 2026-09-27 by Capex for charlie and Capstan; **no PC outcomes are populated**.
These are planned tables, not preliminary results. Capstan can fill them after the
complete paired experiments and readouts are verified. Paths below are configured
**future output locations**, not statements that files currently exist. If an
operator chooses another location, update the source register and this page together.

All relative paths below are from `/home/derp/cap/pc_cap/`. Each PENDING entry
contains a source alias and selector; the alias expands to the full path here.
Bracketed dataset, realization and arm values are row filters, not array indices
except `realizations[r]`. No incomplete cell is silently dropped or scored zero.
Use UNAVAILABLE with a reason for a completed but unscorable assay.

## Source register

| Alias | Configured future path |
| --- | --- |
| V0 | `logs/additional_work/PC-v0/report-60-20260927/report.json` |
| H0 | `results/additional_work/PC-v0/harm/replication-60-20260927/report.json` |
| V1 | `results/additional_work/PC-v1/replication-4-20260927` |
| H1 | `results/additional_work/PC-v1/harm/replication-4-20260927/report.json` |

V1 cell directories are `<dataset>-r0-o100-<arm>` beneath V1.
`cost.json` next to H0/H1 charges the readout once; nested per-arm costs are
breakdowns of that charge, not additional spend. V0 finish time includes startup,
whereas V1 `finish.json` is stream-engine time and `process.json` includes startup
and lease wait: those two V1 durations must never be added together.

## PC-v0 — primary paired behavior by realization

Exposed historical S5; zsRE 1,000 edits, CounterFact 300; three realizations,
five dependent orders each, 60 planned cells. Differences below are **SE-E − SE-A**;
higher favors SE-E for behavior. `V0:<metric>[dataset,r]` means
`aggregates[dataset,metric].realizations[r]`, the mean paired difference across
the five orders; the native `pairs` table retains every order.

| Dataset | Realization | ES | RET-ES | RET-GS | LS |
| --- | --- | --- | --- | --- | --- |
| zsre | 0 | PENDING · V0:ES[zsre,0] | PENDING · V0:RET-ES[zsre,0] | PENDING · V0:RET-GS[zsre,0] | PENDING · V0:LS[zsre,0] |
| zsre | 1 | PENDING · V0:ES[zsre,1] | PENDING · V0:RET-ES[zsre,1] | PENDING · V0:RET-GS[zsre,1] | PENDING · V0:LS[zsre,1] |
| zsre | 2 | PENDING · V0:ES[zsre,2] | PENDING · V0:RET-ES[zsre,2] | PENDING · V0:RET-GS[zsre,2] | PENDING · V0:LS[zsre,2] |
| counterfact | 0 | PENDING · V0:ES[counterfact,0] | PENDING · V0:RET-ES[counterfact,0] | PENDING · V0:RET-GS[counterfact,0] | PENDING · V0:LS[counterfact,0] |
| counterfact | 1 | PENDING · V0:ES[counterfact,1] | PENDING · V0:RET-ES[counterfact,1] | PENDING · V0:RET-GS[counterfact,1] | PENDING · V0:LS[counterfact,1] |
| counterfact | 2 | PENDING · V0:ES[counterfact,2] | PENDING · V0:RET-ES[counterfact,2] | PENDING · V0:RET-GS[counterfact,2] | PENDING · V0:LS[counterfact,2] |

### Bounded-text secondary behavior, kept separate

The same aggregate selector applies using the exact metric keys below; these
do not replace the legacy primary S5 scoring convention.

| Dataset | Realization | bounded_es_immediate | bounded_ret_es_end | bounded_ret_gs_end | bounded_ls_end |
| --- | --- | --- | --- | --- | --- |
| zsre | 0 | PENDING · V0:bounded_es_immediate[zsre,0] | PENDING · V0:bounded_ret_es_end[zsre,0] | PENDING · V0:bounded_ret_gs_end[zsre,0] | PENDING · V0:bounded_ls_end[zsre,0] |
| zsre | 1 | PENDING · V0:bounded_es_immediate[zsre,1] | PENDING · V0:bounded_ret_es_end[zsre,1] | PENDING · V0:bounded_ret_gs_end[zsre,1] | PENDING · V0:bounded_ls_end[zsre,1] |
| zsre | 2 | PENDING · V0:bounded_es_immediate[zsre,2] | PENDING · V0:bounded_ret_es_end[zsre,2] | PENDING · V0:bounded_ret_gs_end[zsre,2] | PENDING · V0:bounded_ls_end[zsre,2] |
| counterfact | 0 | PENDING · V0:bounded_es_immediate[counterfact,0] | PENDING · V0:bounded_ret_es_end[counterfact,0] | PENDING · V0:bounded_ret_gs_end[counterfact,0] | PENDING · V0:bounded_ls_end[counterfact,0] |
| counterfact | 1 | PENDING · V0:bounded_es_immediate[counterfact,1] | PENDING · V0:bounded_ret_es_end[counterfact,1] | PENDING · V0:bounded_ret_gs_end[counterfact,1] | PENDING · V0:bounded_ls_end[counterfact,1] |
| counterfact | 2 | PENDING · V0:bounded_es_immediate[counterfact,2] | PENDING · V0:bounded_ret_es_end[counterfact,2] | PENDING · V0:bounded_ret_gs_end[counterfact,2] | PENDING · V0:bounded_ls_end[counterfact,2] |

### Between-realization summary

Each cell selects `V0:aggregates[dataset,metric].<column>`; min/max are the range
of the three realization means, not a confidence interval.

| Dataset | Metric | Mean | Minimum | Maximum |
| --- | --- | --- | --- | --- |
| zsre | ES | PENDING · V0:aggregates[zsre,ES].mean | PENDING · V0:aggregates[zsre,ES].minimum | PENDING · V0:aggregates[zsre,ES].maximum |
| zsre | RET-ES | PENDING · V0:aggregates[zsre,RET-ES].mean | PENDING · V0:aggregates[zsre,RET-ES].minimum | PENDING · V0:aggregates[zsre,RET-ES].maximum |
| zsre | RET-GS | PENDING · V0:aggregates[zsre,RET-GS].mean | PENDING · V0:aggregates[zsre,RET-GS].minimum | PENDING · V0:aggregates[zsre,RET-GS].maximum |
| zsre | LS | PENDING · V0:aggregates[zsre,LS].mean | PENDING · V0:aggregates[zsre,LS].minimum | PENDING · V0:aggregates[zsre,LS].maximum |
| counterfact | ES | PENDING · V0:aggregates[counterfact,ES].mean | PENDING · V0:aggregates[counterfact,ES].minimum | PENDING · V0:aggregates[counterfact,ES].maximum |
| counterfact | RET-ES | PENDING · V0:aggregates[counterfact,RET-ES].mean | PENDING · V0:aggregates[counterfact,RET-ES].minimum | PENDING · V0:aggregates[counterfact,RET-ES].maximum |
| counterfact | RET-GS | PENDING · V0:aggregates[counterfact,RET-GS].mean | PENDING · V0:aggregates[counterfact,RET-GS].minimum | PENDING · V0:aggregates[counterfact,RET-GS].maximum |
| counterfact | LS | PENDING · V0:aggregates[counterfact,LS].mean | PENDING · V0:aggregates[counterfact,LS].minimum | PENDING · V0:aggregates[counterfact,LS].maximum |

### Replication cost by realization

Each entry is the sum of `V0:cells[dataset,realization,arm].finish.elapsed_process_seconds`
over the five planned orders, retaining the ledger in the native report.

| Dataset | Realization | SE-A process seconds | SE-E process seconds |
| --- | --- | --- | --- |
| zsre | 0 | PENDING · V0:cells[zsre,0,SE-A].finish.elapsed_process_seconds (sum) | PENDING · V0:cells[zsre,0,SE-E].finish.elapsed_process_seconds (sum) |
| zsre | 1 | PENDING · V0:cells[zsre,1,SE-A].finish.elapsed_process_seconds (sum) | PENDING · V0:cells[zsre,1,SE-E].finish.elapsed_process_seconds (sum) |
| zsre | 2 | PENDING · V0:cells[zsre,2,SE-A].finish.elapsed_process_seconds (sum) | PENDING · V0:cells[zsre,2,SE-E].finish.elapsed_process_seconds (sum) |
| counterfact | 0 | PENDING · V0:cells[counterfact,0,SE-A].finish.elapsed_process_seconds (sum) | PENDING · V0:cells[counterfact,0,SE-E].finish.elapsed_process_seconds (sum) |
| counterfact | 1 | PENDING · V0:cells[counterfact,1,SE-A].finish.elapsed_process_seconds (sum) | PENDING · V0:cells[counterfact,1,SE-E].finish.elapsed_process_seconds (sum) |
| counterfact | 2 | PENDING · V0:cells[counterfact,2,SE-A].finish.elapsed_process_seconds (sum) | PENDING · V0:cells[counterfact,2,SE-E].finish.elapsed_process_seconds (sum) |

## Fixed-v5 — the four planned cells

Post hoc transfer check on exposed R1 realization 0, order 100, first 300 edits;
the same BP-trained base and selected reader in both arms, fresh memory per cell.
These four cells are not three independent replications and do not test PC reader
training. Use R1's installed endpoint semantics, including semantic revision.

### Checkpoint 100

| Dataset | Arm | ES | RET-ES | RET-GS | LS | near_miss | revision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | SE-A | PENDING · V1/zsre-r0-o100-SE-A/checkpoint-100.json:metrics.ES.value | PENDING · V1/zsre-r0-o100-SE-A/checkpoint-100.json:metrics.RET-ES.value | PENDING · V1/zsre-r0-o100-SE-A/checkpoint-100.json:metrics.RET-GS.value | PENDING · V1/zsre-r0-o100-SE-A/checkpoint-100.json:metrics.LS.value | PENDING · V1/zsre-r0-o100-SE-A/checkpoint-100.json:metrics.near_miss.value | PENDING · V1/zsre-r0-o100-SE-A/checkpoint-100.json:metrics.revision.value |
| zsre | SE-E | PENDING · V1/zsre-r0-o100-SE-E/checkpoint-100.json:metrics.ES.value | PENDING · V1/zsre-r0-o100-SE-E/checkpoint-100.json:metrics.RET-ES.value | PENDING · V1/zsre-r0-o100-SE-E/checkpoint-100.json:metrics.RET-GS.value | PENDING · V1/zsre-r0-o100-SE-E/checkpoint-100.json:metrics.LS.value | PENDING · V1/zsre-r0-o100-SE-E/checkpoint-100.json:metrics.near_miss.value | PENDING · V1/zsre-r0-o100-SE-E/checkpoint-100.json:metrics.revision.value |
| counterfact | SE-A | PENDING · V1/counterfact-r0-o100-SE-A/checkpoint-100.json:metrics.ES.value | PENDING · V1/counterfact-r0-o100-SE-A/checkpoint-100.json:metrics.RET-ES.value | PENDING · V1/counterfact-r0-o100-SE-A/checkpoint-100.json:metrics.RET-GS.value | PENDING · V1/counterfact-r0-o100-SE-A/checkpoint-100.json:metrics.LS.value | PENDING · V1/counterfact-r0-o100-SE-A/checkpoint-100.json:metrics.near_miss.value | PENDING · V1/counterfact-r0-o100-SE-A/checkpoint-100.json:metrics.revision.value |
| counterfact | SE-E | PENDING · V1/counterfact-r0-o100-SE-E/checkpoint-100.json:metrics.ES.value | PENDING · V1/counterfact-r0-o100-SE-E/checkpoint-100.json:metrics.RET-ES.value | PENDING · V1/counterfact-r0-o100-SE-E/checkpoint-100.json:metrics.RET-GS.value | PENDING · V1/counterfact-r0-o100-SE-E/checkpoint-100.json:metrics.LS.value | PENDING · V1/counterfact-r0-o100-SE-E/checkpoint-100.json:metrics.near_miss.value | PENDING · V1/counterfact-r0-o100-SE-E/checkpoint-100.json:metrics.revision.value |

### Checkpoint 300

| Dataset | Arm | ES | RET-ES | RET-GS | LS | near_miss | revision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | SE-A | PENDING · V1/zsre-r0-o100-SE-A/checkpoint-300.json:metrics.ES.value | PENDING · V1/zsre-r0-o100-SE-A/checkpoint-300.json:metrics.RET-ES.value | PENDING · V1/zsre-r0-o100-SE-A/checkpoint-300.json:metrics.RET-GS.value | PENDING · V1/zsre-r0-o100-SE-A/checkpoint-300.json:metrics.LS.value | PENDING · V1/zsre-r0-o100-SE-A/checkpoint-300.json:metrics.near_miss.value | PENDING · V1/zsre-r0-o100-SE-A/checkpoint-300.json:metrics.revision.value |
| zsre | SE-E | PENDING · V1/zsre-r0-o100-SE-E/checkpoint-300.json:metrics.ES.value | PENDING · V1/zsre-r0-o100-SE-E/checkpoint-300.json:metrics.RET-ES.value | PENDING · V1/zsre-r0-o100-SE-E/checkpoint-300.json:metrics.RET-GS.value | PENDING · V1/zsre-r0-o100-SE-E/checkpoint-300.json:metrics.LS.value | PENDING · V1/zsre-r0-o100-SE-E/checkpoint-300.json:metrics.near_miss.value | PENDING · V1/zsre-r0-o100-SE-E/checkpoint-300.json:metrics.revision.value |
| counterfact | SE-A | PENDING · V1/counterfact-r0-o100-SE-A/checkpoint-300.json:metrics.ES.value | PENDING · V1/counterfact-r0-o100-SE-A/checkpoint-300.json:metrics.RET-ES.value | PENDING · V1/counterfact-r0-o100-SE-A/checkpoint-300.json:metrics.RET-GS.value | PENDING · V1/counterfact-r0-o100-SE-A/checkpoint-300.json:metrics.LS.value | PENDING · V1/counterfact-r0-o100-SE-A/checkpoint-300.json:metrics.near_miss.value | PENDING · V1/counterfact-r0-o100-SE-A/checkpoint-300.json:metrics.revision.value |
| counterfact | SE-E | PENDING · V1/counterfact-r0-o100-SE-E/checkpoint-300.json:metrics.ES.value | PENDING · V1/counterfact-r0-o100-SE-E/checkpoint-300.json:metrics.RET-ES.value | PENDING · V1/counterfact-r0-o100-SE-E/checkpoint-300.json:metrics.RET-GS.value | PENDING · V1/counterfact-r0-o100-SE-E/checkpoint-300.json:metrics.LS.value | PENDING · V1/counterfact-r0-o100-SE-E/checkpoint-300.json:metrics.near_miss.value | PENDING · V1/counterfact-r0-o100-SE-E/checkpoint-300.json:metrics.revision.value |

### Fixed-v5 cost

| Dataset | Arm | Stream-engine seconds | Whole-process seconds |
| --- | --- | --- | --- |
| zsre | SE-A | PENDING · V1/zsre-r0-o100-SE-A/finish.json:elapsed_process_seconds | PENDING · V1/zsre-r0-o100-SE-A/process.json:elapsed_process_seconds |
| zsre | SE-E | PENDING · V1/zsre-r0-o100-SE-E/finish.json:elapsed_process_seconds | PENDING · V1/zsre-r0-o100-SE-E/process.json:elapsed_process_seconds |
| counterfact | SE-A | PENDING · V1/counterfact-r0-o100-SE-A/finish.json:elapsed_process_seconds | PENDING · V1/counterfact-r0-o100-SE-A/process.json:elapsed_process_seconds |
| counterfact | SE-E | PENDING · V1/counterfact-r0-o100-SE-E/finish.json:elapsed_process_seconds | PENDING · V1/counterfact-r0-o100-SE-E/process.json:elapsed_process_seconds |

## Ordinary-text harm — per-arm and paired summaries

H0: final snapshots, 4,064 fixed target positions per cell; H1: final 300-edit
snapshots, 245,237 fixed target positions per cell. These inventories differ and
must not be pooled. Positive signed changes are worse. Both arms use identical
positions and the same original reference within each paired study.

For H0 realization rows, average the **five cell summaries**, and keep every
order in the native readout; do not recalculate a pooled tail and call it their
mean. H1 has one order per dataset. `S[dataset,r,arm]` expands to
`cells[dataset,realization,arm].readout.summary.original`; `P[dataset,r]` expands
to `pairs[dataset,realization]`. Every following entry identifies H0 or H1.
The maximum shown is a mean of cell maxima where five orders exist, not a pooled
maximum; the native report retains the actual maxima and position locations.

### H0 arm summaries

| Dataset | Realization | Arm | kl.mean_signed | loss.mean_signed | loss.es99_positive | loss.maximum_signed |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | SE-A | PENDING · H0:S[zsre,0,SE-A].kl.mean_signed | PENDING · H0:S[zsre,0,SE-A].loss.mean_signed | PENDING · H0:S[zsre,0,SE-A].loss.es99_positive | PENDING · H0:S[zsre,0,SE-A].loss.maximum_signed |
| zsre | 0 | SE-E | PENDING · H0:S[zsre,0,SE-E].kl.mean_signed | PENDING · H0:S[zsre,0,SE-E].loss.mean_signed | PENDING · H0:S[zsre,0,SE-E].loss.es99_positive | PENDING · H0:S[zsre,0,SE-E].loss.maximum_signed |
| zsre | 1 | SE-A | PENDING · H0:S[zsre,1,SE-A].kl.mean_signed | PENDING · H0:S[zsre,1,SE-A].loss.mean_signed | PENDING · H0:S[zsre,1,SE-A].loss.es99_positive | PENDING · H0:S[zsre,1,SE-A].loss.maximum_signed |
| zsre | 1 | SE-E | PENDING · H0:S[zsre,1,SE-E].kl.mean_signed | PENDING · H0:S[zsre,1,SE-E].loss.mean_signed | PENDING · H0:S[zsre,1,SE-E].loss.es99_positive | PENDING · H0:S[zsre,1,SE-E].loss.maximum_signed |
| zsre | 2 | SE-A | PENDING · H0:S[zsre,2,SE-A].kl.mean_signed | PENDING · H0:S[zsre,2,SE-A].loss.mean_signed | PENDING · H0:S[zsre,2,SE-A].loss.es99_positive | PENDING · H0:S[zsre,2,SE-A].loss.maximum_signed |
| zsre | 2 | SE-E | PENDING · H0:S[zsre,2,SE-E].kl.mean_signed | PENDING · H0:S[zsre,2,SE-E].loss.mean_signed | PENDING · H0:S[zsre,2,SE-E].loss.es99_positive | PENDING · H0:S[zsre,2,SE-E].loss.maximum_signed |
| counterfact | 0 | SE-A | PENDING · H0:S[counterfact,0,SE-A].kl.mean_signed | PENDING · H0:S[counterfact,0,SE-A].loss.mean_signed | PENDING · H0:S[counterfact,0,SE-A].loss.es99_positive | PENDING · H0:S[counterfact,0,SE-A].loss.maximum_signed |
| counterfact | 0 | SE-E | PENDING · H0:S[counterfact,0,SE-E].kl.mean_signed | PENDING · H0:S[counterfact,0,SE-E].loss.mean_signed | PENDING · H0:S[counterfact,0,SE-E].loss.es99_positive | PENDING · H0:S[counterfact,0,SE-E].loss.maximum_signed |
| counterfact | 1 | SE-A | PENDING · H0:S[counterfact,1,SE-A].kl.mean_signed | PENDING · H0:S[counterfact,1,SE-A].loss.mean_signed | PENDING · H0:S[counterfact,1,SE-A].loss.es99_positive | PENDING · H0:S[counterfact,1,SE-A].loss.maximum_signed |
| counterfact | 1 | SE-E | PENDING · H0:S[counterfact,1,SE-E].kl.mean_signed | PENDING · H0:S[counterfact,1,SE-E].loss.mean_signed | PENDING · H0:S[counterfact,1,SE-E].loss.es99_positive | PENDING · H0:S[counterfact,1,SE-E].loss.maximum_signed |
| counterfact | 2 | SE-A | PENDING · H0:S[counterfact,2,SE-A].kl.mean_signed | PENDING · H0:S[counterfact,2,SE-A].loss.mean_signed | PENDING · H0:S[counterfact,2,SE-A].loss.es99_positive | PENDING · H0:S[counterfact,2,SE-A].loss.maximum_signed |
| counterfact | 2 | SE-E | PENDING · H0:S[counterfact,2,SE-E].kl.mean_signed | PENDING · H0:S[counterfact,2,SE-E].loss.mean_signed | PENDING · H0:S[counterfact,2,SE-E].loss.es99_positive | PENDING · H0:S[counterfact,2,SE-E].loss.maximum_signed |

| Dataset | Realization | Arm | loss.exceedance['0.01'].fraction | loss.exceedance['0.1'].fraction | loss.exceedance['1.0'].fraction | loss.half_mass_positions |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | SE-A | PENDING · H0:S[zsre,0,SE-A].loss.exceedance['0.01'].fraction | PENDING · H0:S[zsre,0,SE-A].loss.exceedance['0.1'].fraction | PENDING · H0:S[zsre,0,SE-A].loss.exceedance['1.0'].fraction | PENDING · H0:S[zsre,0,SE-A].loss.half_mass_positions |
| zsre | 0 | SE-E | PENDING · H0:S[zsre,0,SE-E].loss.exceedance['0.01'].fraction | PENDING · H0:S[zsre,0,SE-E].loss.exceedance['0.1'].fraction | PENDING · H0:S[zsre,0,SE-E].loss.exceedance['1.0'].fraction | PENDING · H0:S[zsre,0,SE-E].loss.half_mass_positions |
| zsre | 1 | SE-A | PENDING · H0:S[zsre,1,SE-A].loss.exceedance['0.01'].fraction | PENDING · H0:S[zsre,1,SE-A].loss.exceedance['0.1'].fraction | PENDING · H0:S[zsre,1,SE-A].loss.exceedance['1.0'].fraction | PENDING · H0:S[zsre,1,SE-A].loss.half_mass_positions |
| zsre | 1 | SE-E | PENDING · H0:S[zsre,1,SE-E].loss.exceedance['0.01'].fraction | PENDING · H0:S[zsre,1,SE-E].loss.exceedance['0.1'].fraction | PENDING · H0:S[zsre,1,SE-E].loss.exceedance['1.0'].fraction | PENDING · H0:S[zsre,1,SE-E].loss.half_mass_positions |
| zsre | 2 | SE-A | PENDING · H0:S[zsre,2,SE-A].loss.exceedance['0.01'].fraction | PENDING · H0:S[zsre,2,SE-A].loss.exceedance['0.1'].fraction | PENDING · H0:S[zsre,2,SE-A].loss.exceedance['1.0'].fraction | PENDING · H0:S[zsre,2,SE-A].loss.half_mass_positions |
| zsre | 2 | SE-E | PENDING · H0:S[zsre,2,SE-E].loss.exceedance['0.01'].fraction | PENDING · H0:S[zsre,2,SE-E].loss.exceedance['0.1'].fraction | PENDING · H0:S[zsre,2,SE-E].loss.exceedance['1.0'].fraction | PENDING · H0:S[zsre,2,SE-E].loss.half_mass_positions |
| counterfact | 0 | SE-A | PENDING · H0:S[counterfact,0,SE-A].loss.exceedance['0.01'].fraction | PENDING · H0:S[counterfact,0,SE-A].loss.exceedance['0.1'].fraction | PENDING · H0:S[counterfact,0,SE-A].loss.exceedance['1.0'].fraction | PENDING · H0:S[counterfact,0,SE-A].loss.half_mass_positions |
| counterfact | 0 | SE-E | PENDING · H0:S[counterfact,0,SE-E].loss.exceedance['0.01'].fraction | PENDING · H0:S[counterfact,0,SE-E].loss.exceedance['0.1'].fraction | PENDING · H0:S[counterfact,0,SE-E].loss.exceedance['1.0'].fraction | PENDING · H0:S[counterfact,0,SE-E].loss.half_mass_positions |
| counterfact | 1 | SE-A | PENDING · H0:S[counterfact,1,SE-A].loss.exceedance['0.01'].fraction | PENDING · H0:S[counterfact,1,SE-A].loss.exceedance['0.1'].fraction | PENDING · H0:S[counterfact,1,SE-A].loss.exceedance['1.0'].fraction | PENDING · H0:S[counterfact,1,SE-A].loss.half_mass_positions |
| counterfact | 1 | SE-E | PENDING · H0:S[counterfact,1,SE-E].loss.exceedance['0.01'].fraction | PENDING · H0:S[counterfact,1,SE-E].loss.exceedance['0.1'].fraction | PENDING · H0:S[counterfact,1,SE-E].loss.exceedance['1.0'].fraction | PENDING · H0:S[counterfact,1,SE-E].loss.half_mass_positions |
| counterfact | 2 | SE-A | PENDING · H0:S[counterfact,2,SE-A].loss.exceedance['0.01'].fraction | PENDING · H0:S[counterfact,2,SE-A].loss.exceedance['0.1'].fraction | PENDING · H0:S[counterfact,2,SE-A].loss.exceedance['1.0'].fraction | PENDING · H0:S[counterfact,2,SE-A].loss.half_mass_positions |
| counterfact | 2 | SE-E | PENDING · H0:S[counterfact,2,SE-E].loss.exceedance['0.01'].fraction | PENDING · H0:S[counterfact,2,SE-E].loss.exceedance['0.1'].fraction | PENDING · H0:S[counterfact,2,SE-E].loss.exceedance['1.0'].fraction | PENDING · H0:S[counterfact,2,SE-E].loss.half_mass_positions |

### H0 matched differences — SE-E minus SE-A

| Dataset | Realization | positionwise.original.kl.mean_signed | positionwise.original.loss.mean_signed | positionwise.original.loss.es99_positive | difference_of_arm_es99.original |
| --- | --- | --- | --- | --- | --- |
| zsre | 0 | PENDING · H0:P[zsre,0].positionwise.original.kl.mean_signed | PENDING · H0:P[zsre,0].positionwise.original.loss.mean_signed | PENDING · H0:P[zsre,0].positionwise.original.loss.es99_positive | PENDING · H0:P[zsre,0].difference_of_arm_es99.original |
| zsre | 1 | PENDING · H0:P[zsre,1].positionwise.original.kl.mean_signed | PENDING · H0:P[zsre,1].positionwise.original.loss.mean_signed | PENDING · H0:P[zsre,1].positionwise.original.loss.es99_positive | PENDING · H0:P[zsre,1].difference_of_arm_es99.original |
| zsre | 2 | PENDING · H0:P[zsre,2].positionwise.original.kl.mean_signed | PENDING · H0:P[zsre,2].positionwise.original.loss.mean_signed | PENDING · H0:P[zsre,2].positionwise.original.loss.es99_positive | PENDING · H0:P[zsre,2].difference_of_arm_es99.original |
| counterfact | 0 | PENDING · H0:P[counterfact,0].positionwise.original.kl.mean_signed | PENDING · H0:P[counterfact,0].positionwise.original.loss.mean_signed | PENDING · H0:P[counterfact,0].positionwise.original.loss.es99_positive | PENDING · H0:P[counterfact,0].difference_of_arm_es99.original |
| counterfact | 1 | PENDING · H0:P[counterfact,1].positionwise.original.kl.mean_signed | PENDING · H0:P[counterfact,1].positionwise.original.loss.mean_signed | PENDING · H0:P[counterfact,1].positionwise.original.loss.es99_positive | PENDING · H0:P[counterfact,1].difference_of_arm_es99.original |
| counterfact | 2 | PENDING · H0:P[counterfact,2].positionwise.original.kl.mean_signed | PENDING · H0:P[counterfact,2].positionwise.original.loss.mean_signed | PENDING · H0:P[counterfact,2].positionwise.original.loss.es99_positive | PENDING · H0:P[counterfact,2].difference_of_arm_es99.original |

### H1 arm summaries

| Dataset | Realization | Arm | kl.mean_signed | loss.mean_signed | loss.es99_positive | loss.maximum_signed |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | SE-A | PENDING · H1:S[zsre,0,SE-A].kl.mean_signed | PENDING · H1:S[zsre,0,SE-A].loss.mean_signed | PENDING · H1:S[zsre,0,SE-A].loss.es99_positive | PENDING · H1:S[zsre,0,SE-A].loss.maximum_signed |
| zsre | 0 | SE-E | PENDING · H1:S[zsre,0,SE-E].kl.mean_signed | PENDING · H1:S[zsre,0,SE-E].loss.mean_signed | PENDING · H1:S[zsre,0,SE-E].loss.es99_positive | PENDING · H1:S[zsre,0,SE-E].loss.maximum_signed |
| counterfact | 0 | SE-A | PENDING · H1:S[counterfact,0,SE-A].kl.mean_signed | PENDING · H1:S[counterfact,0,SE-A].loss.mean_signed | PENDING · H1:S[counterfact,0,SE-A].loss.es99_positive | PENDING · H1:S[counterfact,0,SE-A].loss.maximum_signed |
| counterfact | 0 | SE-E | PENDING · H1:S[counterfact,0,SE-E].kl.mean_signed | PENDING · H1:S[counterfact,0,SE-E].loss.mean_signed | PENDING · H1:S[counterfact,0,SE-E].loss.es99_positive | PENDING · H1:S[counterfact,0,SE-E].loss.maximum_signed |

| Dataset | Realization | Arm | loss.exceedance['0.01'].fraction | loss.exceedance['0.1'].fraction | loss.exceedance['1.0'].fraction | loss.half_mass_positions |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | SE-A | PENDING · H1:S[zsre,0,SE-A].loss.exceedance['0.01'].fraction | PENDING · H1:S[zsre,0,SE-A].loss.exceedance['0.1'].fraction | PENDING · H1:S[zsre,0,SE-A].loss.exceedance['1.0'].fraction | PENDING · H1:S[zsre,0,SE-A].loss.half_mass_positions |
| zsre | 0 | SE-E | PENDING · H1:S[zsre,0,SE-E].loss.exceedance['0.01'].fraction | PENDING · H1:S[zsre,0,SE-E].loss.exceedance['0.1'].fraction | PENDING · H1:S[zsre,0,SE-E].loss.exceedance['1.0'].fraction | PENDING · H1:S[zsre,0,SE-E].loss.half_mass_positions |
| counterfact | 0 | SE-A | PENDING · H1:S[counterfact,0,SE-A].loss.exceedance['0.01'].fraction | PENDING · H1:S[counterfact,0,SE-A].loss.exceedance['0.1'].fraction | PENDING · H1:S[counterfact,0,SE-A].loss.exceedance['1.0'].fraction | PENDING · H1:S[counterfact,0,SE-A].loss.half_mass_positions |
| counterfact | 0 | SE-E | PENDING · H1:S[counterfact,0,SE-E].loss.exceedance['0.01'].fraction | PENDING · H1:S[counterfact,0,SE-E].loss.exceedance['0.1'].fraction | PENDING · H1:S[counterfact,0,SE-E].loss.exceedance['1.0'].fraction | PENDING · H1:S[counterfact,0,SE-E].loss.half_mass_positions |

### H1 matched differences — SE-E minus SE-A

| Dataset | Realization | positionwise.original.kl.mean_signed | positionwise.original.loss.mean_signed | positionwise.original.loss.es99_positive | difference_of_arm_es99.original |
| --- | --- | --- | --- | --- | --- |
| zsre | 0 | PENDING · H1:P[zsre,0].positionwise.original.kl.mean_signed | PENDING · H1:P[zsre,0].positionwise.original.loss.mean_signed | PENDING · H1:P[zsre,0].positionwise.original.loss.es99_positive | PENDING · H1:P[zsre,0].difference_of_arm_es99.original |
| counterfact | 0 | PENDING · H1:P[counterfact,0].positionwise.original.kl.mean_signed | PENDING · H1:P[counterfact,0].positionwise.original.loss.mean_signed | PENDING · H1:P[counterfact,0].positionwise.original.loss.es99_positive | PENDING · H1:P[counterfact,0].difference_of_arm_es99.original |

**Keep the last two paired columns distinct:** the ES99 of positive
positionwise loss differences is not the difference of arm ES99 values. The
latter is the efficacy–harm slide slot; the former is additional paired detail.
Retain zero positions and the fractional expected-shortfall boundary.

| Readout | Charged readout process seconds |
| --- | --- |
| H0 | PENDING · H0:../cost.json:elapsed_process_seconds |
| H1 | PENDING · H1:../cost.json:elapsed_process_seconds |

## Completion notes for Capstan

Require all 60 v0 and all four fixed-v5 cells, both final readouts, matching
source/model/data/position identities and complete cost receipts before filling
their respective result tables. Record the actual source file hashes and report
locations; no CPU-smoke outputs or partial-run effects belong here. Preserve
every unfavorable, null and unavailable result. Present effect sizes and the
three v0 realization values before choosing the spoken interpretation.

The claim ledger and timed talk scripts remain pending at their PC slots until
these complete reports exist. The supplied streams are exposed; token positions
and five orders are not independent experimental replicates. Empirical severe
loss and concentration do not establish a power law, a heavy-tail family,
autonomous active inference, or robustness to unseen extremes.
