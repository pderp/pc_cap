## Matched-position ordinary-text harm

CPU fixture only; not an experimental result.

Population: six synthetic positions per arm. Fixed prefixes; original = cap-off for the frozen PC base. KL direction is reference || cap. ES99 is the fractional average of the worst 1% positive ΔNLL including zeros; maximum ties use first window/position. Positive-harm half mass is undefined if total harm is zero. No tail-family or independent-token inference.

| Dataset | r | order | arm | mean KL | signed ΔNLL | ES99+ | max ΔNLL | location | P(>.01) | P(>.1) | P(>1) | half-mass positions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | 100 | SE-A | 0.00112306 | -0.0613685 | 0.0262762 | 0.0262762 | w1:p3 | 0.166667 | 0 | 0 | 1 |
| zsre | 0 | 100 | SE-E | 0.000735694 | -0.056009 | 0.0292625 | 0.0292625 | w1:p3 | 0.166667 | 0 | 0 | 1 |


SE-E − SE-A at identical positions (positive = additional harm from SE-E); no token-level confidence intervals.

| Dataset | r | order | paired mean KL change | paired mean ΔNLL change | ES99+ of paired ΔNLL | difference of arm ES99+ |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | 100 | -0.000387368 | 0.00535946 | 0.0145572 | 0.00298624 |


Readout costs are saved per arm in cost.json and at run level in cost.json; add them to the shared 8-hour readout budget, not the replication budget.
