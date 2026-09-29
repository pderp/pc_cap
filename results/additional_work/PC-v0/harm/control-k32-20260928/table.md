Treatment: SE-E k=32, lr=0.1; SE-A unchanged

## Matched-position ordinary-text harm

Population: Legacy S5: 32 windows × 127 targets = 4,064 positions per arm. Fixed prefixes; original = cap-off for the frozen PC base. KL direction is reference || cap. ES99 is the fractional average of the worst 1% positive ΔNLL including zeros; maximum ties use first window/position. Positive-harm half mass is undefined if total harm is zero. No tail-family or independent-token inference.

| Dataset | r | order | arm | mean KL | signed ΔNLL | ES99+ | max ΔNLL | location | P(>.01) | P(>.1) | P(>1) | half-mass positions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | 100 | SE-A | 0.00209045 | 0.00251113 | 0.251113 | 5.46859 | w14:p109 | 0.00172244 | 0.00172244 | 0.000738189 | 1 |
| zsre | 0 | 100 | SE-E | 0.0057861 | 0.00542595 | 0.558956 | 8.02868 | w13:p125 | 0.00147638 | 0.00147638 | 0.00123031 | 2 |
| zsre | 1 | 100 | SE-A | 0.00162863 | 0.00146262 | 0.146262 | 3.05143 | w16:p46 | 0.000984252 | 0.000738189 | 0.000492126 | 1 |
| zsre | 1 | 100 | SE-E | 0.000460714 | 0.000644044 | 0.0644044 | 1.93976 | w23:p7 | 0.000738189 | 0.000492126 | 0.000246063 | 1 |
| zsre | 2 | 100 | SE-A | 0.00180976 | 0.000380201 | 0.0700604 | 2.43119 | w15:p36 | 0.000492126 | 0.000492126 | 0.000246063 | 1 |
| zsre | 2 | 100 | SE-E | 0.00148647 | 0.000562109 | 0.0859586 | 3.13719 | w13:p125 | 0.000492126 | 0.000492126 | 0.000246063 | 1 |
| counterfact | 0 | 100 | SE-A | 0 | 0 | 0 | 0 | w0:p1 | 0 | 0 | 0 | unavailable |
| counterfact | 0 | 100 | SE-E | 0 | 0 | 0 | 0 | w0:p1 | 0 | 0 | 0 | unavailable |
| counterfact | 1 | 100 | SE-A | 0 | 0 | 0 | 0 | w0:p1 | 0 | 0 | 0 | unavailable |
| counterfact | 1 | 100 | SE-E | 0 | 0 | 0 | 0 | w0:p1 | 0 | 0 | 0 | unavailable |
| counterfact | 2 | 100 | SE-A | 0 | 0 | 0 | 0 | w0:p1 | 0 | 0 | 0 | unavailable |
| counterfact | 2 | 100 | SE-E | 0 | 0 | 0 | 0 | w0:p1 | 0 | 0 | 0 | unavailable |


SE-E − SE-A at identical positions (positive = additional harm from SE-E); no token-level confidence intervals.

| Dataset | r | order | paired mean KL change | paired mean ΔNLL change | ES99+ of paired ΔNLL | difference of arm ES99+ |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | 100 | 0.00369565 | 0.00291483 | 0.465234 | 0.307844 |
| zsre | 1 | 100 | -0.00116792 | -0.000818578 | 0 | -0.0818578 |
| zsre | 2 | 100 | -0.000323294 | 0.000181908 | 0.0810784 | 0.0158982 |
| counterfact | 0 | 100 | 0 | 0 | 0 | 0 |
| counterfact | 1 | 100 | 0 | 0 | 0 | 0 |
| counterfact | 2 | 100 | 0 | 0 | 0 | 0 |


Readout costs are saved per arm in cost.json and at run level in cost.json; add them to the shared 8-hour readout budget, not the replication budget.
