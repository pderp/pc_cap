# Slide 6 — How often, and how severe?

**Draft speaker text for charlie's review; updated October 1, 2026.**

**On screen:** HT-17 frequency versus conditional severity; both datasets, own-cap-off reference. The survival curves are backup.

## Speaker text

“An average can conceal a small number of large unintended changes. We measure delta NLL: the increase in negative log probability of the actual next token when the cap is enabled at the same prefix. One nat means that token becomes a factor of e less probable. This is a prediction-loss measure, not human harm or the preference term of expected free energy.” [`HT-readout`]

“The horizontal axis asks how often the increase exceeds 0.01 nat. Its denominator includes every scored position, including improvements and unchanged predictions. The vertical axis asks how large the increase is, on average, among positions exceeding that threshold. Neither axis is the gate firing rate: an activated correction need not cause harmful change.” [`HT17-tails`]

“On zsRE, learned v5 has harmful changes at 0.1594 percent of positions with conditional severity 1.630 nats. Stable v0 has 0.1041 percent and 1.716 nats. On CounterFact, learned v5 has 0.2984 percent and 1.913 nats; the random reader has 2.0450 percent and 3.486 nats. Stable v0 has no observed harmful changes there, but also zero paraphrase retention. Its conditional severity is undefined, not zero.” [`HT17-tails`]

“These are fifteen cells per condition and dataset: three subject realizations and five dependent orders, at a thousand edits. Every cell reuses the same 245,237 ordinary-text positions. The intervals resample matching window identities jointly, conditional on the observed cells. They do not account for subject or seed uncertainty, and independence between windows is unverified.” [`HT17-tails`]

“Expected shortfall asks another question: ES99 averages positive loss within the worst one percent of all positions, with zeros and a fractional boundary retained. The maximum is the single largest observed event. Learned v5 on zsRE has a lower maximum than stable v0, 11.05 versus 27.68 nats, but a higher average cell ES99, 0.260 versus 0.179. No single summary orders every kind of risk.” [`HT17-tails`, `HT-readout`]

## Sources and backup

[HT-17 report](../../additional_work/HT-17_report.md); source snapshot `logs/additional_work/HT-17/snapshot-20261004-complete/report.json`.

Figure: `assets/presentation-materials/figures/tails_ht17/round61-seed1/frequency-severity-stage4.png`. The original six-panel frequency/severity figure, including AW-B and partial reader seeds, remains backup. These replace the HT-13 main-screen slots; the earlier 270-cell empirical report remains valid at its stated scope.
