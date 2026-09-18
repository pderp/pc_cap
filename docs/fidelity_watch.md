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
