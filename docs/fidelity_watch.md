# Fidelity watch (DEC-064a)

Every completed cell whose cap fidelity on the full validation split would have failed the formerly critical bounds
(mean KL > 0.001 nats or mean NLL increase > 0.01, either reference) is listed here with its numbers; the running
maximum per condition × dataset is kept so the lead can see whether it creeps. Entries are appended by the watch
(HT-8) after each cell; the orchestrator reports new entries at block boundaries and creep alerts immediately.
Labels are the DEC-064 secondary benchmark; nothing here vetoes a primary comparison.

| date | cell | dataset | condition | records | realization | KL (orig ‖ cap) | NLL Δ | ES95 | max | positions for 50 % KL | untouched | creep |
| --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2026-09-18 | R1-64g mquake R1_learned_ff (chain S) | MQuAKE | R1_learned_ff (primary v5) | 300 | development | 0.00554 | +0.00560 | 0.114 | 8.19 | 171 (0.07 %) | 99.6 % | first entry; development reference |

Running maxima (KL): MQuAKE · R1_learned_ff 0.00554.

No-breach log: 2026-09-18 R1-64g mquake v0_stable (chain S, 300 records, development): zero observed loss / KL change on all 245,237 positions (radius-0 cap never fires on ordinary text) — no entry.

<!-- HT-8 managed watch: begin -->

## Automated verified watch (HT-8)

Manual notes above are preserved. This source-bound table is regenerated from the locked journal; one entry per recipe cell. Both references are shown. Near-zero target-token loss does not establish unchanged predictions or reader inactivity.

Audited cells: 4; breaching cells: 2; creep alerts: 0. Development and confirmatory observations remain labelled; benchmarks never veto primary comparisons.

| Cell identity / scope | Condition / dataset / realization / order | Actual records / checkpoint | Reference | Mean KL | NLL increase | ES95 loss | Max loss | Positions for half KL | Near-zero loss fraction | Creep |
|---|---|---|---|---:|---:|---:|---:|---|---:|---|
| `e71244c94a79d03e28e59d421680063cf1a96e822a1c36f077c4d1289670fbe4` / development | R1_learned_ff / mquake / development_full_endpoints_R164f / seed64028 | 300 / 300 | capoff | 0.00554368762 | 0.00560097637 | 0.114467563 | 8.18755035 | 171 | 0.99631377 | none |
| `e71244c94a79d03e28e59d421680063cf1a96e822a1c36f077c4d1289670fbe4` / development | R1_learned_ff / mquake / development_full_endpoints_R164f / seed64028 | 300 / 300 | original | 0.00554368762 | 0.00560097637 | 0.114467563 | 8.18755035 | 171 | 0.99631377 | none |
| `b66aedc82924b7a83016a07aa0723803bfd8ff1360f4a2aebbd4acb4f624a8a1` / development | R1_learned_ff / zsre / development_full_endpoints_R164f / seed64028 | 300 / 300 | capoff | 0.0022697245 | 0.00231001529 | 0.0474726905 | 9.94468865 | 64 | 0.99857689 | none |
| `b66aedc82924b7a83016a07aa0723803bfd8ff1360f4a2aebbd4acb4f624a8a1` / development | R1_learned_ff / zsre / development_full_endpoints_R164f / seed64028 | 300 / 300 | original | 0.0022697245 | 0.00231001529 | 0.0474726905 | 9.94468865 | 64 | 0.99857689 | none |

### Running maxima (all audited cells, including no-breach cells)

| Condition : dataset | Reference | Maximum KL | Maximum signed NLL increase | Development reference cell |
|---|---|---:|---:|---|
| R1_learned_ff:mquake | capoff | 0.00554368762 | 0.00560097637 | `e71244c94a79d03e28e59d421680063cf1a96e822a1c36f077c4d1289670fbe4` |
| R1_learned_ff:mquake | original | 0.00554368762 | 0.00560097637 | `e71244c94a79d03e28e59d421680063cf1a96e822a1c36f077c4d1289670fbe4` |
| R1_learned_ff:zsre | capoff | 0.0022697245 | 0.00231001529 | `b66aedc82924b7a83016a07aa0723803bfd8ff1360f4a2aebbd4acb4f624a8a1` |
| R1_learned_ff:zsre | original | 0.0022697245 | 0.00231001529 | `b66aedc82924b7a83016a07aa0723803bfd8ff1360f4a2aebbd4acb4f624a8a1` |
| v0_stable:mquake | capoff | 0 | 0 | `29efe01659d59eafa4daf6c07dbbd45ba7ef97f1aee549ca95763aa0df8eba61` |
| v0_stable:mquake | original | 0 | 0 | `29efe01659d59eafa4daf6c07dbbd45ba7ef97f1aee549ca95763aa0df8eba61` |
| v0_stable:zsre | capoff | 0.000788590677 | 0.000855162037 | `d9cbf00f433af01b870b7e6a880e41c74689ecef4ac9e8ebcf90be639735fd77` |
| v0_stable:zsre | original | 0.000788590677 | 0.000855162037 | `d9cbf00f433af01b870b7e6a880e41c74689ecef4ac9e8ebcf90be639735fd77` |

### Creep alerts — orchestrator delivery queue

No creep alerts observed.

<!-- HT-8 managed watch: end -->
