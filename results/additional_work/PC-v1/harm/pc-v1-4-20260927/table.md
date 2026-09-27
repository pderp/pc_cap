## Matched-position ordinary-text harm

Population: Legacy S5: 32 windows × 127 targets = 4,064 positions per arm. Fixed prefixes; original = cap-off for the frozen PC base. KL direction is reference || cap. ES99 is the fractional average of the worst 1% positive ΔNLL including zeros; maximum ties use first window/position. Positive-harm half mass is undefined if total harm is zero. No tail-family or independent-token inference.

| Dataset | r | order | arm | mean KL | signed ΔNLL | ES99+ | max ΔNLL | location | P(>.01) | P(>.1) | P(>1) | half-mass positions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| counterfact | 0 | 100 | SE-A | 0.00417566 | 0.0043814 | 0.458686 | 11.7442 | w994:p63 | 0.00281768 | 0.00267904 | 0.00140272 | 110 |
| counterfact | 0 | 100 | SE-E | 0.00430833 | 0.00450374 | 0.469916 | 12.2254 | w994:p63 | 0.00284623 | 0.0026872 | 0.00145981 | 110 |
| zsre | 0 | 100 | SE-A | 0.00186062 | 0.00181293 | 0.195585 | 9.26227 | w860:p44 | 0.00117845 | 0.00112952 | 0.000619809 | 53 |
| zsre | 0 | 100 | SE-E | 0.00170361 | 0.00167283 | 0.181614 | 12.27 | w1314:p20 | 0.00118253 | 0.00112136 | 0.000591265 | 49 |


SE-E − SE-A at identical positions (positive = additional harm from SE-E); no token-level confidence intervals.

| Dataset | r | order | paired mean KL change | paired mean ΔNLL change | ES99+ of paired ΔNLL | difference of arm ES99+ |
| --- | --- | --- | --- | --- | --- | --- |
| counterfact | 0 | 100 | 0.000132678 | 0.000122341 | 0.0382164 | 0.0112291 |
| zsre | 0 | 100 | -0.000157009 | -0.000140103 | 0.0160704 | -0.0139706 |


Readout costs are saved per arm in cost.json and at run level in cost.json; add them to the shared 8-hour readout budget, not the replication budget.
