Treatment: SE-E k=1, lr=0.1; SE-A unchanged

## Matched-position ordinary-text harm

Population: Legacy S5: 32 windows × 127 targets = 4,064 positions per arm. Fixed prefixes; original = cap-off for the frozen PC base. KL direction is reference || cap. ES99 is the fractional average of the worst 1% positive ΔNLL including zeros; maximum ties use first window/position. Positive-harm half mass is undefined if total harm is zero. No tail-family or independent-token inference.

| Dataset | r | order | arm | mean KL | signed ΔNLL | ES99+ | max ΔNLL | location | P(>.01) | P(>.1) | P(>1) | half-mass positions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | 100 | SE-A | 0.00209045 | 0.00251113 | 0.251113 | 5.46859 | w14:p109 | 0.00172244 | 0.00172244 | 0.000738189 | 1 |
| zsre | 0 | 100 | SE-E | 0.0020905 | 0.00251125 | 0.251125 | 5.46857 | w14:p109 | 0.00172244 | 0.00172244 | 0.000738189 | 1 |
| zsre | 1 | 100 | SE-A | 0.00162863 | 0.00146262 | 0.146262 | 3.05143 | w16:p46 | 0.000984252 | 0.000738189 | 0.000492126 | 1 |
| zsre | 1 | 100 | SE-E | 0.00162864 | 0.00146262 | 0.146262 | 3.05141 | w16:p46 | 0.000984252 | 0.000738189 | 0.000492126 | 1 |
| zsre | 2 | 100 | SE-A | 0.00180976 | 0.000380201 | 0.0700604 | 2.43119 | w15:p36 | 0.000492126 | 0.000492126 | 0.000246063 | 1 |
| zsre | 2 | 100 | SE-E | 0.00180977 | 0.000380221 | 0.0700616 | 2.43123 | w15:p36 | 0.000492126 | 0.000492126 | 0.000246063 | 1 |
| counterfact | 0 | 100 | SE-A | 0 | 0 | 0 | 0 | w0:p1 | 0 | 0 | 0 | unavailable |
| counterfact | 0 | 100 | SE-E | 0 | 0 | 0 | 0 | w0:p1 | 0 | 0 | 0 | unavailable |
| counterfact | 1 | 100 | SE-A | 0 | 0 | 0 | 0 | w0:p1 | 0 | 0 | 0 | unavailable |
| counterfact | 1 | 100 | SE-E | 0 | 0 | 0 | 0 | w0:p1 | 0 | 0 | 0 | unavailable |
| counterfact | 2 | 100 | SE-A | 0 | 0 | 0 | 0 | w0:p1 | 0 | 0 | 0 | unavailable |
| counterfact | 2 | 100 | SE-E | 0 | 0 | 0 | 0 | w0:p1 | 0 | 0 | 0 | unavailable |


SE-E − SE-A at identical positions (positive = additional harm from SE-E); no token-level confidence intervals.

| Dataset | r | order | paired mean KL change | paired mean ΔNLL change | ES99+ of paired ΔNLL | difference of arm ES99+ |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | 100 | 4.11364e-08 | 1.20774e-07 | 1.30781e-05 | 1.20774e-05 |
| zsre | 1 | 100 | 4.69346e-09 | -3.53038e-09 | 5.0634e-07 | -3.53038e-07 |
| zsre | 2 | 100 | 3.56836e-09 | 2.02868e-08 | 2.0619e-06 | 1.17391e-06 |
| counterfact | 0 | 100 | 0 | 0 | 0 | 0 |
| counterfact | 1 | 100 | 0 | 0 | 0 | 0 |
| counterfact | 2 | 100 | 0 | 0 | 0 | 0 |


Readout costs are saved per arm in cost.json and at run level in cost.json; add them to the shared 8-hour readout budget, not the replication budget.
