# Upper-layer read/write factorial — partial report

Capex · 6/24 completed evaluation cells, including 6 explicitly shared PC-reader BP controls; six planned trained readers.
Numerical source and hashes: `/home/derp/cap/pc_cap/logs/additional_work/reproductions/round60-check1/aw-l/report.json`.

Read all taps {1,2,3} or upper taps {2,3}; write all sites {1,2,3} or last site {3}. Three paired training seeds; each reader serves both write arms with separately acquired fresh memory. All training uses the full-write objective. Same exposed realization 0/order 100 at 300 edits. Lower layers are not assumed to be noise. Training seeds are not subject realizations.

No complete four-arm seed block is available unless shown below. Available full-read/full-write controls are the identical PC-reader BP artifacts; they are reused observations, not additional replication. The three full-read trainings also share the PC-reader controls, as allowed in AW-L5. New factorial results cannot be inferred from those controls alone.

## Training and reuse

| Read | Seed | Status | Shared PC reader | Parameters | Process s |
| --- | --- | --- | --- | --- | --- |
| all | 0 | complete | True | 3348228 | 866.5778 |
| upper | 0 | missing | False | — | — |
| all | 1 | complete | True | 3348228 | 906.5266 |
| upper | 1 | missing | False | — | — |
| all | 2 | complete | True | 3348228 | 872.0438 |
| upper | 2 | missing | False | — | — |

## Per-cell efficacy

| Cell | Status | ES | RET-ES | RET-GS | LS | near_miss | revision | Unseen fires / observed / planned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s0 zsre read=all write=all [shared] | complete | 1 | 1 | 0.9733333 | 1 | 0.85 | 1 | 4 / 100 / 100 |
| s0 counterfact read=all write=all [shared] | complete | 1 | 1 | 0.81 | 1 | 1 | 1 | 0 / 100 / 100 |
| s0 zsre read=all write=last | missing | — | — | — | — | — | — | — |
| s0 counterfact read=all write=last | missing | — | — | — | — | — | — | — |
| s0 zsre read=upper write=all | missing | — | — | — | — | — | — | — |
| s0 counterfact read=upper write=all | missing | — | — | — | — | — | — | — |
| s0 zsre read=upper write=last | missing | — | — | — | — | — | — | — |
| s0 counterfact read=upper write=last | missing | — | — | — | — | — | — | — |
| s1 zsre read=all write=all [shared] | complete | 1 | 1 | 0.99 | 1 | 0.67 | 1 | 14 / 100 / 100 |
| s1 counterfact read=all write=all [shared] | complete | 0.99 | 0.99 | 0.8 | 1 | 0.99 | 0.98 | 1 / 100 / 100 |
| s1 zsre read=all write=last | missing | — | — | — | — | — | — | — |
| s1 counterfact read=all write=last | missing | — | — | — | — | — | — | — |
| s1 zsre read=upper write=all | missing | — | — | — | — | — | — | — |
| s1 counterfact read=upper write=all | missing | — | — | — | — | — | — | — |
| s1 zsre read=upper write=last | missing | — | — | — | — | — | — | — |
| s1 counterfact read=upper write=last | missing | — | — | — | — | — | — | — |
| s2 zsre read=all write=all [shared] | complete | 1 | 1 | 0.9766667 | 1 | 0.73 | 1 | 11 / 100 / 100 |
| s2 counterfact read=all write=all [shared] | complete | 1 | 1 | 0.835 | 1 | 1 | 1 | 0 / 100 / 100 |
| s2 zsre read=all write=last | missing | — | — | — | — | — | — | — |
| s2 counterfact read=all write=last | missing | — | — | — | — | — | — | — |
| s2 zsre read=upper write=all | missing | — | — | — | — | — | — | — |
| s2 counterfact read=upper write=all | missing | — | — | — | — | — | — | — |
| s2 zsre read=upper write=last | missing | — | — | — | — | — | — | — |
| s2 counterfact read=upper write=last | missing | — | — | — | — | — | — | — |

Values use planned denominators; no unavailable slot is reinterpreted as a correct answer. ES is immediate acquisition success; RET-ES/RET-GS are retained own-prompt/paraphrase scores.

| Cell | Endpoint | Numerator | Scored / planned | Status |
| --- | --- | --- | --- | --- |
| s0 zsre read=all write=all [shared] | ES | 300 | 300 / 300 | complete |
| s0 zsre read=all write=all [shared] | RET-ES | 300 | 300 / 300 | complete |
| s0 zsre read=all write=all [shared] | RET-GS | 292 | 300 / 300 | complete |
| s0 zsre read=all write=all [shared] | LS | 50 | 50 / 50 | complete |
| s0 zsre read=all write=all [shared] | near_miss | 85 | 100 / 100 | complete |
| s0 zsre read=all write=all [shared] | revision | 50 | 50 / 50 | complete |
| s0 counterfact read=all write=all [shared] | ES | 300 | 300 / 300 | complete |
| s0 counterfact read=all write=all [shared] | RET-ES | 300 | 300 / 300 | complete |
| s0 counterfact read=all write=all [shared] | RET-GS | 243 | 300 / 300 | complete |
| s0 counterfact read=all write=all [shared] | LS | 50 | 50 / 50 | complete |
| s0 counterfact read=all write=all [shared] | near_miss | 100 | 100 / 100 | complete |
| s0 counterfact read=all write=all [shared] | revision | 50 | 50 / 50 | complete |
| s1 zsre read=all write=all [shared] | ES | 300 | 300 / 300 | complete |
| s1 zsre read=all write=all [shared] | RET-ES | 300 | 300 / 300 | complete |
| s1 zsre read=all write=all [shared] | RET-GS | 297 | 300 / 300 | complete |
| s1 zsre read=all write=all [shared] | LS | 50 | 50 / 50 | complete |
| s1 zsre read=all write=all [shared] | near_miss | 67 | 100 / 100 | complete |
| s1 zsre read=all write=all [shared] | revision | 50 | 50 / 50 | complete |
| s1 counterfact read=all write=all [shared] | ES | 297 | 300 / 300 | complete |
| s1 counterfact read=all write=all [shared] | RET-ES | 297 | 300 / 300 | complete |
| s1 counterfact read=all write=all [shared] | RET-GS | 240 | 300 / 300 | complete |
| s1 counterfact read=all write=all [shared] | LS | 50 | 50 / 50 | complete |
| s1 counterfact read=all write=all [shared] | near_miss | 99 | 100 / 100 | complete |
| s1 counterfact read=all write=all [shared] | revision | 49 | 50 / 50 | complete |
| s2 zsre read=all write=all [shared] | ES | 300 | 300 / 300 | complete |
| s2 zsre read=all write=all [shared] | RET-ES | 300 | 300 / 300 | complete |
| s2 zsre read=all write=all [shared] | RET-GS | 293 | 300 / 300 | complete |
| s2 zsre read=all write=all [shared] | LS | 50 | 50 / 50 | complete |
| s2 zsre read=all write=all [shared] | near_miss | 73 | 100 / 100 | complete |
| s2 zsre read=all write=all [shared] | revision | 50 | 50 / 50 | complete |
| s2 counterfact read=all write=all [shared] | ES | 300 | 300 / 300 | complete |
| s2 counterfact read=all write=all [shared] | RET-ES | 300 | 300 / 300 | complete |
| s2 counterfact read=all write=all [shared] | RET-GS | 250.5 | 300 / 300 | complete |
| s2 counterfact read=all write=all [shared] | LS | 50 | 50 / 50 | complete |
| s2 counterfact read=all write=all [shared] | near_miss | 100 | 100 / 100 | complete |
| s2 counterfact read=all write=all [shared] | revision | 50 | 50 / 50 | complete |

## Fidelity and ordinary-text gate telemetry

Own cap-off reference; original-base summaries and full exceedance records are also retained in the JSON. Mean KL .001 is a descriptive fidelity watch, not data-integrity status. Harmful changes and gate firings are different quantities.

| Cell | Mean KL | Mean ΔNLL | ES99+ | Max ΔNLL | Δ>.01 / >.1 / >1 | Fired / hard null / positions |
| --- | --- | --- | --- | --- | --- | --- |
| s0 zsre read=all write=all [shared] | 0.0001107215 | 0.000109969 | 0.01170186 | 6.506296 | 15/14/9 | 18 / 245219 / 245237 |
| s0 counterfact read=all write=all [shared] | 0.002012263 | 0.002020257 | 0.2070025 | 8.51933 | 227/217/149 | 256 / 244981 / 245237 |
| s1 zsre read=all write=all [shared] | 0.0001344412 | 0.0001254599 | 0.01273685 | 7.922522 | 12/12/9 | 13 / 245224 / 245237 |
| s1 counterfact read=all write=all [shared] | 0.005166184 | 0.005352227 | 0.5512697 | 12.50178 | 567/548/363 | 660 / 244577 / 245237 |
| s2 zsre read=all write=all [shared] | 0.000169764 | 0.0001800639 | 0.01832748 | 10.57568 | 19/19/15 | 21 / 245216 / 245237 |
| s2 counterfact read=all write=all [shared] | 0.001119561 | 0.001183002 | 0.1207727 | 9.864664 | 138/136/83 | 149 / 245088 / 245237 |

## Evaluation costs and allocated storage

Process seconds include construction, acquisition, endpoints and harm. Stream and harm are subsets, not extra charges. Inactive dense write slots remain charged; active-coordinate bytes are not a storage saving.

| Cell | Process s | Stream s (subset) | Harm s (subset) | Parameters | Delta allocated bytes | Delta active bytes | Total allocated bytes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| s0 zsre read=all write=all [shared] | 1716.045 | 511.6396 | 1200.518 | 3348228 | 10229760 | 10229760 | 24288920 |
| s0 counterfact read=all write=all [shared] | 1696.773 | 508.0424 | 1184.849 | 3348228 | 5529600 | 5529600 | 19584784 |
| s0 zsre read=all write=last | — | — | — | — | — | — | — |
| s0 counterfact read=all write=last | — | — | — | — | — | — | — |
| s0 zsre read=upper write=all | — | — | — | — | — | — | — |
| s0 counterfact read=upper write=all | — | — | — | — | — | — | — |
| s0 zsre read=upper write=last | — | — | — | — | — | — | — |
| s0 counterfact read=upper write=last | — | — | — | — | — | — | — |
| s1 zsre read=all write=all [shared] | 1717.861 | 513.0456 | 1200.929 | 3348228 | 10229760 | 10229760 | 24288920 |
| s1 counterfact read=all write=all [shared] | 1696.976 | 509.1746 | 1183.908 | 3348228 | 5529600 | 5529600 | 19584784 |
| s1 zsre read=all write=last | — | — | — | — | — | — | — |
| s1 counterfact read=all write=last | — | — | — | — | — | — | — |
| s1 zsre read=upper write=all | — | — | — | — | — | — | — |
| s1 counterfact read=upper write=all | — | — | — | — | — | — | — |
| s1 zsre read=upper write=last | — | — | — | — | — | — | — |
| s1 counterfact read=upper write=last | — | — | — | — | — | — | — |
| s2 zsre read=all write=all [shared] | 1725.536 | 513.0481 | 1208.589 | 3348228 | 10229760 | 10229760 | 24288920 |
| s2 counterfact read=all write=all [shared] | 1686.338 | 507.0371 | 1175.395 | 3348228 | 5529600 | 5529600 | 19584784 |
| s2 zsre read=all write=last | — | — | — | — | — | — | — |
| s2 counterfact read=all write=last | — | — | — | — | — | — | — |
| s2 zsre read=upper write=all | — | — | — | — | — | — | — |
| s2 counterfact read=upper write=all | — | — | — | — | — | — | — |
| s2 zsre read=upper write=last | — | — | — | — | — | — | — |
| s2 counterfact read=upper write=last | — | — | — | — | — | — | — |

## Paired read, write and interaction effects

Let A=all/all, B=all/last, C=upper/all and D=upper/last. Read effect=((C−A)+(D−B))/2; write effect=((B−A)+(D−C))/2; interaction=(D−C)−(B−A). Behavior increases favor the first-named upper/last intervention; increases in harm mean worse fidelity. Every term comes from one seed/dataset; unavailable arms withhold that block's effects.

| Dataset | Seed | Complete 2×2 block |
| --- | --- | --- |
| zsre | 0 | False |
| counterfact | 0 | False |
| zsre | 1 | False |
| counterfact | 1 | False |
| zsre | 2 | False |
| counterfact | 2 | False |

| Dataset | Seed | Metric | Read effect | Write effect | Interaction |
| --- | --- | --- | --- | --- | --- |

The JSON includes effect means, ranges and sample SD across completed paired seeds; no confidence or superiority claim is assigned to a three-seed range.

## Descriptive retention tolerance

The 0.02 tolerance means neither RET-ES nor RET-GS drops by more than two percentage points versus all-read/all-write in the same seed and dataset. This is a descriptive comparison, **not an inferential noninferiority result or a new classifier**. A baseline row meets its own tolerance by definition and is not evidence for upper layers. Fidelity remains beside efficacy, regardless of this column.

| Dataset | Seed | Read | Write | Δ RET-ES | Δ RET-GS | Within .02 | Baseline |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | all | all | 0 | 0 | True | True |
| zsre | 0 | all | last | — | — | — | False |
| zsre | 0 | upper | all | — | — | — | False |
| zsre | 0 | upper | last | — | — | — | False |
| counterfact | 0 | all | all | 0 | 0 | True | True |
| counterfact | 0 | all | last | — | — | — | False |
| counterfact | 0 | upper | all | — | — | — | False |
| counterfact | 0 | upper | last | — | — | — | False |
| zsre | 1 | all | all | 0 | 0 | True | True |
| zsre | 1 | all | last | — | — | — | False |
| zsre | 1 | upper | all | — | — | — | False |
| zsre | 1 | upper | last | — | — | — | False |
| counterfact | 1 | all | all | 0 | 0 | True | True |
| counterfact | 1 | all | last | — | — | — | False |
| counterfact | 1 | upper | all | — | — | — | False |
| counterfact | 1 | upper | last | — | — | — | False |
| zsre | 2 | all | all | 0 | 0 | True | True |
| zsre | 2 | all | last | — | — | — | False |
| zsre | 2 | upper | all | — | — | — | False |
| zsre | 2 | upper | last | — | — | — | False |
| counterfact | 2 | all | all | 0 | 0 | True | True |
| counterfact | 2 | all | last | — | — | — | False |
| counterfact | 2 | upper | all | — | — | — | False |
| counterfact | 2 | upper | last | — | — | — | False |

## Cost and development availability

Unique attributed process time: 3.5791 hours; new work in the AW-L namespace: 0.0000 hours. Shared PC-reader cost is not charged a second time across portfolios. All dense allocated delta bytes, including zeroed inactive sites, remain charged. Cost components are subsets of parent receipts.

0 AW-L development evaluations are available in this snapshot. The AW-L directory currently has no delivered development outputs if this count is zero; the report does not invent them or substitute profile scores into the 300-edit table. The parser is tested on a synthetic development/production tree; development rows and their different denominators are retained separately in JSON when they arrive.

Refresh after the queued cells land (new directory each time):

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 \
../venv/bin/python -m aw.aw_l_report --output logs/additional_work/AW-L/report-NEW
```

Scientific design: [AW-L.md](AW-L.md); execution commands: [reader-runners-owner-commands.md](../tasks/reader-runners-owner-commands.md). No GPU or model work is performed by this generator. October 9 at 17:00 EDT remains the experimental cutoff.
