# Upper-layer read/write factorial — complete report

Capex · 24/24 completed evaluation cells, including 6 explicitly shared PC-reader BP controls; six planned trained readers.
Numerical source and hashes: `/home/derp/cap/pc_cap/logs/additional_work/reproductions/freeze-dryrun-20261007/aw-l/report.json`.

Read all taps {1,2,3} or upper taps {2,3}; write all sites {1,2,3} or last site {3}. Three paired training seeds; each reader serves both write arms with separately acquired fresh memory. All training uses the full-write objective. Same exposed realization 0/order 100 at 300 edits. Lower layers are not assumed to be noise. Training seeds are not subject realizations.

Only complete four-arm seed blocks enter the contrasts below. Full-read/full-write controls are the identical PC-reader BP artifacts; they are reused observations, not additional replication. The three full-read trainings also share the PC-reader controls, as allowed in AW-L5.

## Reading of the completed factorial

The last-only write mask leaves the ordinary-text firing count unchanged in all twelve paired write comparisons. Mean signed ordinary-text loss increase is greater with last-only writes in every pair; the per-pair ratio is 2.64–4.37×. The largest absolute paraphrase-retention change from the write restriction is 0.67 percentage points. This tests the deployment/acquisition interface of readers trained with the full-write objective; it does not test separately retrained last-only writers.

| Dataset | Seed | Read | Last−all RET-GS (pp) | Last−all mean ΔNLL | Mean-loss ratio |
| --- | --- | --- | --- | --- | --- |
| zsre | 0 | all | 0 | 0.0003100618 | 3.819539 |
| zsre | 0 | upper | 0 | 9.193163e-05 | 2.635521 |
| zsre | 1 | all | 0 | 0.0002989046 | 3.382472 |
| zsre | 1 | upper | 0 | 9.230497e-05 | 2.711768 |
| zsre | 2 | all | 0 | 0.0003898761 | 3.16521 |
| zsre | 2 | upper | 0 | 0.001149639 | 4.368299 |
| counterfact | 0 | all | -0.6666667 | 0.004619113 | 3.286399 |
| counterfact | 0 | upper | 0 | 0.002562541 | 2.972923 |
| counterfact | 1 | all | -0.3333333 | 0.01001728 | 2.87161 |
| counterfact | 1 | upper | -0.5 | 0.0009734975 | 3.301055 |
| counterfact | 2 | all | -0.5 | 0.002529835 | 3.138487 |
| counterfact | 2 | upper | -0.5 | 0.01504206 | 3.629792 |

Read-tap effects and interactions are shown by seed below. Do not infer that lower layers are noise from a parameter reduction or unchanged firing under a write-only intervention. Intervals described as seed ranges are descriptive minimum–maximum ranges, not confidence intervals.



## Training and reuse

| Read | Seed | Status | Shared PC reader | Parameters | Process s |
| --- | --- | --- | --- | --- | --- |
| all | 0 | complete | True | 3348228 | 866.5778 |
| upper | 0 | complete | False | 2954756 | 830.3515 |
| all | 1 | complete | True | 3348228 | 906.5266 |
| upper | 1 | complete | False | 2954756 | 863.4887 |
| all | 2 | complete | True | 3348228 | 872.0438 |
| upper | 2 | complete | False | 2954756 | 829.7237 |

## Per-cell efficacy

| Cell | Status | ES | RET-ES | RET-GS | LS | near_miss | revision | Unseen fires / observed / planned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s0 zsre read=all write=all [shared] | complete | 1 | 1 | 0.9733333 | 1 | 0.85 | 1 | 4 / 100 / 100 |
| s0 counterfact read=all write=all [shared] | complete | 1 | 1 | 0.81 | 1 | 1 | 1 | 0 / 100 / 100 |
| s0 zsre read=all write=last | complete | 1 | 1 | 0.9733333 | 1 | 0.85 | 1 | 4 / 100 / 100 |
| s0 counterfact read=all write=last | complete | 1 | 1 | 0.8033333 | 1 | 1 | 1 | 0 / 100 / 100 |
| s0 zsre read=upper write=all | complete | 1 | 1 | 0.9866667 | 1 | 0.65 | 1 | 23 / 100 / 100 |
| s0 counterfact read=upper write=all | complete | 1 | 1 | 0.7783333 | 1 | 1 | 1 | 0 / 100 / 100 |
| s0 zsre read=upper write=last | complete | 1 | 1 | 0.9866667 | 1 | 0.65 | 1 | 23 / 100 / 100 |
| s0 counterfact read=upper write=last | complete | 1 | 1 | 0.7783333 | 1 | 1 | 1 | 0 / 100 / 100 |
| s1 zsre read=all write=all [shared] | complete | 1 | 1 | 0.99 | 1 | 0.67 | 1 | 14 / 100 / 100 |
| s1 counterfact read=all write=all [shared] | complete | 0.99 | 0.99 | 0.8 | 1 | 0.99 | 0.98 | 1 / 100 / 100 |
| s1 zsre read=all write=last | complete | 1 | 1 | 0.99 | 1 | 0.67 | 1 | 14 / 100 / 100 |
| s1 counterfact read=all write=last | complete | 0.99 | 0.99 | 0.7966667 | 1 | 0.99 | 0.98 | 1 / 100 / 100 |
| s1 zsre read=upper write=all | complete | 1 | 1 | 0.97 | 1 | 0.77 | 1 | 9 / 100 / 100 |
| s1 counterfact read=upper write=all | complete | 0.9266667 | 0.93 | 0.6916667 | 1 | 0.99 | 0.92 | 0 / 100 / 100 |
| s1 zsre read=upper write=last | complete | 1 | 1 | 0.97 | 1 | 0.77 | 1 | 9 / 100 / 100 |
| s1 counterfact read=upper write=last | complete | 0.9266667 | 0.93 | 0.6866667 | 1 | 0.99 | 0.92 | 0 / 100 / 100 |
| s2 zsre read=all write=all [shared] | complete | 1 | 1 | 0.9766667 | 1 | 0.73 | 1 | 11 / 100 / 100 |
| s2 counterfact read=all write=all [shared] | complete | 1 | 1 | 0.835 | 1 | 1 | 1 | 0 / 100 / 100 |
| s2 zsre read=all write=last | complete | 1 | 1 | 0.9766667 | 1 | 0.73 | 1 | 11 / 100 / 100 |
| s2 counterfact read=all write=last | complete | 1 | 1 | 0.83 | 1 | 1 | 1 | 0 / 100 / 100 |
| s2 zsre read=upper write=all | complete | 1 | 1 | 0.9866667 | 1 | 0.64 | 1 | 23 / 100 / 100 |
| s2 counterfact read=upper write=all | complete | 1 | 1 | 0.8116667 | 1 | 0.99 | 1 | 1 / 100 / 100 |
| s2 zsre read=upper write=last | complete | 1 | 1 | 0.9866667 | 1 | 0.64 | 1 | 23 / 100 / 100 |
| s2 counterfact read=upper write=last | complete | 1 | 1 | 0.8066667 | 1 | 0.99 | 1 | 1 / 100 / 100 |

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
| s0 zsre read=all write=last | ES | 300 | 300 / 300 | complete |
| s0 zsre read=all write=last | RET-ES | 300 | 300 / 300 | complete |
| s0 zsre read=all write=last | RET-GS | 292 | 300 / 300 | complete |
| s0 zsre read=all write=last | LS | 50 | 50 / 50 | complete |
| s0 zsre read=all write=last | near_miss | 85 | 100 / 100 | complete |
| s0 zsre read=all write=last | revision | 50 | 50 / 50 | complete |
| s0 counterfact read=all write=last | ES | 300 | 300 / 300 | complete |
| s0 counterfact read=all write=last | RET-ES | 300 | 300 / 300 | complete |
| s0 counterfact read=all write=last | RET-GS | 241 | 300 / 300 | complete |
| s0 counterfact read=all write=last | LS | 50 | 50 / 50 | complete |
| s0 counterfact read=all write=last | near_miss | 100 | 100 / 100 | complete |
| s0 counterfact read=all write=last | revision | 50 | 50 / 50 | complete |
| s0 zsre read=upper write=all | ES | 300 | 300 / 300 | complete |
| s0 zsre read=upper write=all | RET-ES | 300 | 300 / 300 | complete |
| s0 zsre read=upper write=all | RET-GS | 296 | 300 / 300 | complete |
| s0 zsre read=upper write=all | LS | 50 | 50 / 50 | complete |
| s0 zsre read=upper write=all | near_miss | 65 | 100 / 100 | complete |
| s0 zsre read=upper write=all | revision | 50 | 50 / 50 | complete |
| s0 counterfact read=upper write=all | ES | 300 | 300 / 300 | complete |
| s0 counterfact read=upper write=all | RET-ES | 300 | 300 / 300 | complete |
| s0 counterfact read=upper write=all | RET-GS | 233.5 | 300 / 300 | complete |
| s0 counterfact read=upper write=all | LS | 50 | 50 / 50 | complete |
| s0 counterfact read=upper write=all | near_miss | 100 | 100 / 100 | complete |
| s0 counterfact read=upper write=all | revision | 50 | 50 / 50 | complete |
| s0 zsre read=upper write=last | ES | 300 | 300 / 300 | complete |
| s0 zsre read=upper write=last | RET-ES | 300 | 300 / 300 | complete |
| s0 zsre read=upper write=last | RET-GS | 296 | 300 / 300 | complete |
| s0 zsre read=upper write=last | LS | 50 | 50 / 50 | complete |
| s0 zsre read=upper write=last | near_miss | 65 | 100 / 100 | complete |
| s0 zsre read=upper write=last | revision | 50 | 50 / 50 | complete |
| s0 counterfact read=upper write=last | ES | 300 | 300 / 300 | complete |
| s0 counterfact read=upper write=last | RET-ES | 300 | 300 / 300 | complete |
| s0 counterfact read=upper write=last | RET-GS | 233.5 | 300 / 300 | complete |
| s0 counterfact read=upper write=last | LS | 50 | 50 / 50 | complete |
| s0 counterfact read=upper write=last | near_miss | 100 | 100 / 100 | complete |
| s0 counterfact read=upper write=last | revision | 50 | 50 / 50 | complete |
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
| s1 zsre read=all write=last | ES | 300 | 300 / 300 | complete |
| s1 zsre read=all write=last | RET-ES | 300 | 300 / 300 | complete |
| s1 zsre read=all write=last | RET-GS | 297 | 300 / 300 | complete |
| s1 zsre read=all write=last | LS | 50 | 50 / 50 | complete |
| s1 zsre read=all write=last | near_miss | 67 | 100 / 100 | complete |
| s1 zsre read=all write=last | revision | 50 | 50 / 50 | complete |
| s1 counterfact read=all write=last | ES | 297 | 300 / 300 | complete |
| s1 counterfact read=all write=last | RET-ES | 297 | 300 / 300 | complete |
| s1 counterfact read=all write=last | RET-GS | 239 | 300 / 300 | complete |
| s1 counterfact read=all write=last | LS | 50 | 50 / 50 | complete |
| s1 counterfact read=all write=last | near_miss | 99 | 100 / 100 | complete |
| s1 counterfact read=all write=last | revision | 49 | 50 / 50 | complete |
| s1 zsre read=upper write=all | ES | 300 | 300 / 300 | complete |
| s1 zsre read=upper write=all | RET-ES | 300 | 300 / 300 | complete |
| s1 zsre read=upper write=all | RET-GS | 291 | 300 / 300 | complete |
| s1 zsre read=upper write=all | LS | 50 | 50 / 50 | complete |
| s1 zsre read=upper write=all | near_miss | 77 | 100 / 100 | complete |
| s1 zsre read=upper write=all | revision | 50 | 50 / 50 | complete |
| s1 counterfact read=upper write=all | ES | 278 | 300 / 300 | complete |
| s1 counterfact read=upper write=all | RET-ES | 279 | 300 / 300 | complete |
| s1 counterfact read=upper write=all | RET-GS | 207.5 | 300 / 300 | complete |
| s1 counterfact read=upper write=all | LS | 50 | 50 / 50 | complete |
| s1 counterfact read=upper write=all | near_miss | 99 | 100 / 100 | complete |
| s1 counterfact read=upper write=all | revision | 46 | 50 / 50 | complete |
| s1 zsre read=upper write=last | ES | 300 | 300 / 300 | complete |
| s1 zsre read=upper write=last | RET-ES | 300 | 300 / 300 | complete |
| s1 zsre read=upper write=last | RET-GS | 291 | 300 / 300 | complete |
| s1 zsre read=upper write=last | LS | 50 | 50 / 50 | complete |
| s1 zsre read=upper write=last | near_miss | 77 | 100 / 100 | complete |
| s1 zsre read=upper write=last | revision | 50 | 50 / 50 | complete |
| s1 counterfact read=upper write=last | ES | 278 | 300 / 300 | complete |
| s1 counterfact read=upper write=last | RET-ES | 279 | 300 / 300 | complete |
| s1 counterfact read=upper write=last | RET-GS | 206 | 300 / 300 | complete |
| s1 counterfact read=upper write=last | LS | 50 | 50 / 50 | complete |
| s1 counterfact read=upper write=last | near_miss | 99 | 100 / 100 | complete |
| s1 counterfact read=upper write=last | revision | 46 | 50 / 50 | complete |
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
| s2 zsre read=all write=last | ES | 300 | 300 / 300 | complete |
| s2 zsre read=all write=last | RET-ES | 300 | 300 / 300 | complete |
| s2 zsre read=all write=last | RET-GS | 293 | 300 / 300 | complete |
| s2 zsre read=all write=last | LS | 50 | 50 / 50 | complete |
| s2 zsre read=all write=last | near_miss | 73 | 100 / 100 | complete |
| s2 zsre read=all write=last | revision | 50 | 50 / 50 | complete |
| s2 counterfact read=all write=last | ES | 300 | 300 / 300 | complete |
| s2 counterfact read=all write=last | RET-ES | 300 | 300 / 300 | complete |
| s2 counterfact read=all write=last | RET-GS | 249 | 300 / 300 | complete |
| s2 counterfact read=all write=last | LS | 50 | 50 / 50 | complete |
| s2 counterfact read=all write=last | near_miss | 100 | 100 / 100 | complete |
| s2 counterfact read=all write=last | revision | 50 | 50 / 50 | complete |
| s2 zsre read=upper write=all | ES | 300 | 300 / 300 | complete |
| s2 zsre read=upper write=all | RET-ES | 300 | 300 / 300 | complete |
| s2 zsre read=upper write=all | RET-GS | 296 | 300 / 300 | complete |
| s2 zsre read=upper write=all | LS | 50 | 50 / 50 | complete |
| s2 zsre read=upper write=all | near_miss | 64 | 100 / 100 | complete |
| s2 zsre read=upper write=all | revision | 50 | 50 / 50 | complete |
| s2 counterfact read=upper write=all | ES | 300 | 300 / 300 | complete |
| s2 counterfact read=upper write=all | RET-ES | 300 | 300 / 300 | complete |
| s2 counterfact read=upper write=all | RET-GS | 243.5 | 300 / 300 | complete |
| s2 counterfact read=upper write=all | LS | 50 | 50 / 50 | complete |
| s2 counterfact read=upper write=all | near_miss | 99 | 100 / 100 | complete |
| s2 counterfact read=upper write=all | revision | 50 | 50 / 50 | complete |
| s2 zsre read=upper write=last | ES | 300 | 300 / 300 | complete |
| s2 zsre read=upper write=last | RET-ES | 300 | 300 / 300 | complete |
| s2 zsre read=upper write=last | RET-GS | 296 | 300 / 300 | complete |
| s2 zsre read=upper write=last | LS | 50 | 50 / 50 | complete |
| s2 zsre read=upper write=last | near_miss | 64 | 100 / 100 | complete |
| s2 zsre read=upper write=last | revision | 50 | 50 / 50 | complete |
| s2 counterfact read=upper write=last | ES | 300 | 300 / 300 | complete |
| s2 counterfact read=upper write=last | RET-ES | 300 | 300 / 300 | complete |
| s2 counterfact read=upper write=last | RET-GS | 242 | 300 / 300 | complete |
| s2 counterfact read=upper write=last | LS | 50 | 50 / 50 | complete |
| s2 counterfact read=upper write=last | near_miss | 99 | 100 / 100 | complete |
| s2 counterfact read=upper write=last | revision | 50 | 50 / 50 | complete |

## Fidelity and ordinary-text gate telemetry

Own cap-off reference; original-base summaries and full exceedance records are also retained in the JSON. Mean KL .001 is a descriptive fidelity watch, not data-integrity status. Harmful changes and gate firings are different quantities.

| Cell | Mean KL | Mean ΔNLL | ES99+ | Max ΔNLL | Δ>.01 / >.1 / >1 | Fired / hard null / positions |
| --- | --- | --- | --- | --- | --- | --- |
| s0 zsre read=all write=all [shared] | 0.0001107215 | 0.000109969 | 0.01170186 | 6.506296 | 15/14/9 | 18 / 245219 / 245237 |
| s0 counterfact read=all write=all [shared] | 0.002012263 | 0.002020257 | 0.2070025 | 8.51933 | 227/217/149 | 256 / 244981 / 245237 |
| s0 zsre read=all write=last | 0.0004108 | 0.0004200308 | 0.04255439 | 14.68067 | 17/17/16 | 18 / 245219 / 245237 |
| s0 counterfact read=all write=last | 0.006647355 | 0.00663937 | 0.6640323 | 22.09975 | 252/249/224 | 256 / 244981 / 245237 |
| s0 zsre read=upper write=all | 4.191439e-05 | 5.620939e-05 | 0.005620939 | 7.317423 | 4/4/3 | 4 / 245233 / 245237 |
| s0 counterfact read=upper write=all | 0.001236585 | 0.001298855 | 0.1334786 | 12.36299 | 129/127/87 | 149 / 245088 / 245237 |
| s0 zsre read=upper write=last | 0.0001326645 | 0.000148141 | 0.0148141 | 17.57102 | 4/4/4 | 4 / 245233 / 245237 |
| s0 counterfact read=upper write=last | 0.003826573 | 0.003861396 | 0.3871477 | 16.02102 | 144/140/129 | 149 / 245088 / 245237 |
| s1 zsre read=all write=all [shared] | 0.0001344412 | 0.0001254599 | 0.01273685 | 7.922522 | 12/12/9 | 13 / 245224 / 245237 |
| s1 counterfact read=all write=all [shared] | 0.005166184 | 0.005352227 | 0.5512697 | 12.50178 | 567/548/363 | 660 / 244577 / 245237 |
| s1 zsre read=all write=last | 0.0004360852 | 0.0004243645 | 0.04243645 | 13.62474 | 13/13/12 | 13 / 245224 / 245237 |
| s1 counterfact read=all write=last | 0.01511425 | 0.01536951 | 1.541401 | 22.09975 | 637/621/541 | 660 / 244577 / 245237 |
| s1 zsre read=upper write=all | 4.662775e-05 | 5.392375e-05 | 0.005392375 | 7.46792 | 4/4/3 | 4 / 245233 / 245237 |
| s1 counterfact read=upper write=all | 0.0004301236 | 0.0004230657 | 0.04546747 | 7.84322 | 68/63/35 | 84 / 245153 / 245237 |
| s1 zsre read=upper write=last | 0.0001322909 | 0.0001462287 | 0.01462287 | 16.50384 | 4/4/4 | 4 / 245233 / 245237 |
| s1 counterfact read=upper write=last | 0.001419704 | 0.001396563 | 0.1407495 | 12.118 | 75/74/57 | 84 / 245153 / 245237 |
| s2 zsre read=all write=all [shared] | 0.000169764 | 0.0001800639 | 0.01832748 | 10.57568 | 19/19/15 | 21 / 245216 / 245237 |
| s2 counterfact read=all write=all [shared] | 0.001119561 | 0.001183002 | 0.1207727 | 9.864664 | 138/136/83 | 149 / 245088 / 245237 |
| s2 zsre read=all write=last | 0.0005571385 | 0.00056994 | 0.056994 | 13.38525 | 21/21/20 | 21 / 245216 / 245237 |
| s2 counterfact read=all write=last | 0.003692244 | 0.003712836 | 0.3717623 | 16.96916 | 145/142/129 | 149 / 245088 / 245237 |
| s2 zsre read=upper write=all | 0.0003402999 | 0.0003413116 | 0.03444844 | 7.151059 | 48/46/23 | 54 / 245183 / 245237 |
| s2 counterfact read=upper write=all | 0.005567036 | 0.005719867 | 0.5844001 | 9.842957 | 724/700/451 | 798 / 244439 / 245237 |
| s2 zsre read=upper write=last | 0.001491346 | 0.001490951 | 0.1490951 | 12.17346 | 54/54/53 | 54 / 245183 / 245237 |
| s2 counterfact read=upper write=last | 0.02055363 | 0.02076193 | 2.078361 | 15.73257 | 782/774/727 | 798 / 244439 / 245237 |

## Evaluation costs and allocated storage

Process seconds include construction, acquisition, endpoints and harm. Stream and harm are subsets, not extra charges. Inactive dense write slots remain charged; active-coordinate bytes are not a storage saving.

| Cell | Process s | Stream s (subset) | Harm s (subset) | Parameters | Delta allocated bytes | Delta active bytes | Total allocated bytes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| s0 zsre read=all write=all [shared] | 1716.045 | 511.6396 | 1200.518 | 3348228 | 10229760 | 10229760 | 24288920 |
| s0 counterfact read=all write=all [shared] | 1696.773 | 508.0424 | 1184.849 | 3348228 | 5529600 | 5529600 | 19584784 |
| s0 zsre read=all write=last | 1739.516 | 517.1415 | 1218.411 | 3348228 | 10229760 | 3409920 | 24288920 |
| s0 counterfact read=all write=last | 1712.29 | 513.5792 | 1194.786 | 3348228 | 5511168 | 1837056 | 19566352 |
| s0 zsre read=upper write=all | 1724.225 | 509.1913 | 1211.12 | 2954756 | 10229760 | 10229760 | 22715032 |
| s0 counterfact read=upper write=all | 1693.274 | 505.4162 | 1183.962 | 2954756 | 5529600 | 5529600 | 18010896 |
| s0 zsre read=upper write=last | 1722.826 | 512.0585 | 1206.818 | 2954756 | 10229760 | 3409920 | 22715032 |
| s0 counterfact read=upper write=last | 1699.495 | 507.7773 | 1187.726 | 2954756 | 5529600 | 1843200 | 18010896 |
| s1 zsre read=all write=all [shared] | 1717.861 | 513.0456 | 1200.929 | 3348228 | 10229760 | 10229760 | 24288920 |
| s1 counterfact read=all write=all [shared] | 1696.976 | 509.1746 | 1183.908 | 3348228 | 5529600 | 5529600 | 19584784 |
| s1 zsre read=all write=last | 1739.224 | 517.8272 | 1217.469 | 3348228 | 10229760 | 3409920 | 24288920 |
| s1 counterfact read=all write=last | 1709.842 | 514.9895 | 1190.942 | 3348228 | 5529600 | 1843200 | 19584784 |
| s1 zsre read=upper write=all | 1726.377 | 506.6126 | 1215.862 | 2954756 | 10229760 | 10229760 | 22715032 |
| s1 counterfact read=upper write=all | 1710.525 | 511.5811 | 1195.051 | 2954756 | 5529600 | 5529600 | 18010896 |
| s1 zsre read=upper write=last | 1723.047 | 509.5138 | 1209.616 | 2954756 | 10229760 | 3409920 | 22715032 |
| s1 counterfact read=upper write=last | 1707.013 | 515.1225 | 1187.981 | 2954756 | 5529600 | 1843200 | 18010896 |
| s2 zsre read=all write=all [shared] | 1725.536 | 513.0481 | 1208.589 | 3348228 | 10229760 | 10229760 | 24288920 |
| s2 counterfact read=all write=all [shared] | 1686.338 | 507.0371 | 1175.395 | 3348228 | 5529600 | 5529600 | 19584784 |
| s2 zsre read=all write=last | 1733.031 | 516.2637 | 1212.797 | 3348228 | 10211328 | 3403776 | 24270488 |
| s2 counterfact read=all write=last | 1708.741 | 512.4377 | 1192.389 | 3348228 | 5529600 | 1843200 | 19584784 |
| s2 zsre read=upper write=all | 1726.175 | 509.7677 | 1212.504 | 2954756 | 10229760 | 10229760 | 22715032 |
| s2 counterfact read=upper write=all | 1701.188 | 502.7782 | 1194.52 | 2954756 | 5529600 | 5529600 | 18010896 |
| s2 zsre read=upper write=last | 1721.166 | 510.8099 | 1206.458 | 2954756 | 10229760 | 3409920 | 22715032 |
| s2 counterfact read=upper write=last | 1697.738 | 506.6935 | 1187.137 | 2954756 | 5529600 | 1843200 | 18010896 |

## Paired read, write and interaction effects

Let A=all/all, B=all/last, C=upper/all and D=upper/last. Read effect=((C−A)+(D−B))/2; write effect=((B−A)+(D−C))/2; interaction=(D−C)−(B−A). Behavior increases favor the first-named upper/last intervention; increases in harm mean worse fidelity. Every term comes from one seed/dataset; unavailable arms withhold that block's effects.

| Dataset | Seed | Complete 2×2 block |
| --- | --- | --- |
| zsre | 0 | True |
| counterfact | 0 | True |
| zsre | 1 | True |
| counterfact | 1 | True |
| zsre | 2 | True |
| counterfact | 2 | True |

| Dataset | Seed | Metric | Read effect | Write effect | Interaction |
| --- | --- | --- | --- | --- | --- |
| zsre | 0 | ES | 0 | 0 | 0 |
| zsre | 0 | RET-ES | 0 | 0 | 0 |
| zsre | 0 | RET-GS | 0.01333333 | 0 | 0 |
| zsre | 0 | LS | 0 | 0 | 0 |
| zsre | 0 | near_miss | -0.2 | 0 | 0 |
| zsre | 0 | revision | 0 | 0 | 0 |
| zsre | 0 | mean_kl | -0.0001734713 | 0.0001954143 | -0.0002093284 |
| zsre | 0 | mean_delta_nll | -0.0001628247 | 0.0002009967 | -0.0002181302 |
| zsre | 0 | es99_positive | -0.0169106 | 0.02002284 | -0.02165936 |
| zsre | 0 | maximum_positive | 1.850739 | 9.213986 | 2.079222 |
| zsre | 0 | fired | -14 | 0 | 0 |
| counterfact | 0 | ES | 0 | 0 | 0 |
| counterfact | 0 | RET-ES | 0 | 0 | 0 |
| counterfact | 0 | RET-GS | -0.02833333 | -0.003333333 | 0.006666667 |
| counterfact | 0 | LS | 0 | 0 | 0 |
| counterfact | 0 | near_miss | 0 | 0 | 0 |
| counterfact | 0 | revision | 0 | 0 | 0 |
| counterfact | 0 | mean_kl | -0.00179823 | 0.00361254 | -0.002045103 |
| counterfact | 0 | mean_delta_nll | -0.001749688 | 0.003590827 | -0.002056572 |
| counterfact | 0 | es99_positive | -0.1752043 | 0.3553494 | -0.2033607 |
| counterfact | 0 | maximum_positive | -1.117531 | 8.61922 | -9.922391 |
| counterfact | 0 | fired | -107 | 0 | 0 |
| zsre | 1 | ES | 0 | 0 | 0 |
| zsre | 1 | RET-ES | 0 | 0 | 0 |
| zsre | 1 | RET-GS | -0.02 | 0 | 0 |
| zsre | 1 | LS | 0 | 0 | 0 |
| zsre | 1 | near_miss | 0.1 | 0 | 0 |
| zsre | 1 | revision | 0 | 0 | 0 |
| zsre | 1 | mean_kl | -0.0001958039 | 0.0001936536 | -0.0002159809 |
| zsre | 1 | mean_delta_nll | -0.0001748359 | 0.0001956048 | -0.0002065996 |
| zsre | 1 | es99_positive | -0.01757902 | 0.01946505 | -0.0204691 |
| zsre | 1 | maximum_positive | 1.212249 | 7.36907 | 3.333703 |
| zsre | 1 | fired | -9 | 0 | 0 |
| counterfact | 1 | ES | -0.06333333 | 0 | 0 |
| counterfact | 1 | RET-ES | -0.06 | 0 | 0 |
| counterfact | 1 | RET-GS | -0.1091667 | -0.004166667 | -0.001666667 |
| counterfact | 1 | LS | 0 | 0 | 0 |
| counterfact | 1 | near_miss | 0 | 0 | 0 |
| counterfact | 1 | revision | -0.06 | 0 | 0 |
| counterfact | 1 | mean_kl | -0.009215301 | 0.005468821 | -0.008958481 |
| counterfact | 1 | mean_delta_nll | -0.009451054 | 0.00549539 | -0.009043785 |
| counterfact | 1 | es99_positive | -0.9532269 | 0.5427068 | -0.8948494 |
| counterfact | 1 | maximum_positive | -7.320155 | 6.936372 | -5.323184 |
| counterfact | 1 | fired | -576 | 0 | 0 |
| zsre | 2 | ES | 0 | 0 | 0 |
| zsre | 2 | RET-ES | 0 | 0 | 0 |
| zsre | 2 | RET-GS | 0.01 | 0 | 0 |
| zsre | 2 | LS | 0 | 0 | 0 |
| zsre | 2 | near_miss | -0.09 | 0 | 0 |
| zsre | 2 | revision | 0 | 0 | 0 |
| zsre | 2 | mean_kl | 0.0005523717 | 0.0007692103 | 0.0007636714 |
| zsre | 2 | mean_delta_nll | 0.0005411292 | 0.0007697577 | 0.0007597632 |
| zsre | 2 | es99_positive | 0.05411102 | 0.07665659 | 0.07598012 |
| zsre | 2 | maximum_positive | -2.318207 | 3.915985 | 2.212825 |
| zsre | 2 | fired | 33 | 0 | 0 |
| counterfact | 2 | ES | 0 | 0 | 0 |
| counterfact | 2 | RET-ES | 0 | 0 | 0 |
| counterfact | 2 | RET-GS | -0.02333333 | -0.005 | 0 |
| counterfact | 2 | LS | 0 | 0 | 0 |
| counterfact | 2 | near_miss | -0.01 | 0 | 0 |
| counterfact | 2 | revision | 0 | 0 | 0 |
| counterfact | 2 | mean_kl | 0.01065443 | 0.00877964 | 0.01241391 |
| counterfact | 2 | mean_delta_nll | 0.01079298 | 0.008785946 | 0.01251222 |
| counterfact | 2 | es99_positive | 1.085113 | 0.8724751 | 1.242971 |
| counterfact | 2 | maximum_positive | -0.6291481 | 6.497056 | -1.214881 |
| counterfact | 2 | fired | 649 | 0 | 0 |

The JSON includes effect means, ranges and sample SD across completed paired seeds; no confidence or superiority claim is assigned to a three-seed range.

## Descriptive retention tolerance

The 0.02 tolerance means neither RET-ES nor RET-GS drops by more than two percentage points versus all-read/all-write in the same seed and dataset. This is a descriptive comparison, **not an inferential noninferiority result or a new classifier**. A baseline row meets its own tolerance by definition and is not evidence for upper layers. Fidelity remains beside efficacy, regardless of this column.

| Dataset | Seed | Read | Write | Δ RET-ES | Δ RET-GS | Within .02 | Baseline |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | all | all | 0 | 0 | True | True |
| zsre | 0 | all | last | 0 | 0 | True | False |
| zsre | 0 | upper | all | 0 | 0.01333333 | True | False |
| zsre | 0 | upper | last | 0 | 0.01333333 | True | False |
| counterfact | 0 | all | all | 0 | 0 | True | True |
| counterfact | 0 | all | last | 0 | -0.006666667 | True | False |
| counterfact | 0 | upper | all | 0 | -0.03166667 | False | False |
| counterfact | 0 | upper | last | 0 | -0.03166667 | False | False |
| zsre | 1 | all | all | 0 | 0 | True | True |
| zsre | 1 | all | last | 0 | 0 | True | False |
| zsre | 1 | upper | all | 0 | -0.02 | True | False |
| zsre | 1 | upper | last | 0 | -0.02 | True | False |
| counterfact | 1 | all | all | 0 | 0 | True | True |
| counterfact | 1 | all | last | 0 | -0.003333333 | True | False |
| counterfact | 1 | upper | all | -0.06 | -0.1083333 | False | False |
| counterfact | 1 | upper | last | -0.06 | -0.1133333 | False | False |
| zsre | 2 | all | all | 0 | 0 | True | True |
| zsre | 2 | all | last | 0 | 0 | True | False |
| zsre | 2 | upper | all | 0 | 0.01 | True | False |
| zsre | 2 | upper | last | 0 | 0.01 | True | False |
| counterfact | 2 | all | all | 0 | 0 | True | True |
| counterfact | 2 | all | last | 0 | -0.005 | True | False |
| counterfact | 2 | upper | all | 0 | -0.02333333 | False | False |
| counterfact | 2 | upper | last | 0 | -0.02833333 | False | False |

## Cost and development availability

Unique attributed process time: 13.2489 hours; new work in the AW-L namespace: 9.6698 hours. Shared PC-reader cost is not charged a second time across portfolios. All dense allocated delta bytes, including zeroed inactive sites, remain charged. Cost components are subsets of parent receipts.

6 AW-L development evaluations are available in this snapshot. The AW-L directory currently has no delivered development outputs if this count is zero; the report does not invent them or substitute profile scores into the 300-edit table. The parser is tested on a synthetic development/production tree; development rows and their different denominators are retained separately in JSON when they arrive.



### Historical budget-check defect

The saved profile projection was **17.98 process-hours**, below the shell's 40-hour gate and the declared 48-hour wall ceiling. It projected the full six-reader/24-cell design, including shared controls; it is not a forecast of incremental work alone. The shell gate did **not** enforce its check: it searched the wrong path and defaulted to 0.0. Actual new AW-L parent receipts sum to **9.670 process-hours**; the owner reports about 9.7 wall-hours for the serial chain. Shared controls contribute to the attributed total above but are not new GPU work. Being under budget retrospectively does not mean the admission check worked. The original chain and projection are preserved; future reuse must read the exact file/field and reject missing or invalid input. No experiment was rerun.

Reproduce the saved results (new directory each time):

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 \
../venv/bin/python -m aw.aw_l_report --output logs/additional_work/AW-L/report-NEW
```

Scientific design: [AW-L.md](AW-L.md); execution commands: [reader-runners-owner-commands.md](../tasks/reader-runners-owner-commands.md). No GPU or model work is performed by this generator. October 9 at 17:00 EDT remains the experimental cutoff.
