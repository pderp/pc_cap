# Fixed-v5 acquisition-credit transfer

Four completed cells: two datasets, realization 0, order 100, 300 edits. Exposed, post hoc transfer check; no independent realization interval. The BP-trained base and selected v5 reader remain fixed. Only acquisition credit changes: adjoint SE-A versus corrected eight-step/rate-0.1 error credit SE-E. This does not train the reader with PC or implement expected-free-energy policy selection.

## Checkpoint 100

| Dataset | Arm | ES | RET-ES | RET-GS | LS | Near miss | Revision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | SE-A | 1 | 1 | 0.97 | 1 | 0.72 | 1 |
| zsre | SE-E | 1 | 1 | 0.97 | 1 | 0.72 | 1 |
| counterfact | SE-A | 1 | 1 | 0.825 | 1 | 1 | 1 |
| counterfact | SE-E | 1 | 1 | 0.82 | 1 | 1 | 1 |

## Checkpoint 300

| Dataset | Arm | ES | RET-ES | RET-GS | LS | Near miss | Revision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | SE-A | 1 | 1 | 0.983333 | 1 | 0.76 | 1 |
| zsre | SE-E | 1 | 1 | 0.983333 | 1 | 0.76 | 1 |
| counterfact | SE-A | 1 | 1 | 0.806667 | 1 | 1 | 1 |
| counterfact | SE-E | 1 | 1 | 0.803333 | 1 | 1 | 1 |

## Acquisition and evaluation cost

Whole-process time includes construction/lease/startup and contains stream-engine time; do not add them. Learning ledger wall time is a subset, not total cell latency.

| Dataset | Arm | Stream-engine seconds | Whole-process seconds | Learning ledger seconds | Learning reverses | Settling |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | SE-A | 311.698 | 316.111 | 38.187 | 5669 | 0 |
| zsre | SE-E | 421.652 | 426.036 | 138.777 | 29049 | 23512 |
| counterfact | SE-A | 292.922 | 297.33 | 22.3608 | 3028 | 0 |
| counterfact | SE-E | 355.034 | 359.424 | 78.2347 | 15278 | 12336 |

## Ordinary-text harm and cost

v5 inventory: 1,931 windows × 127 targets = **245,237 positions per cell**. Original = own cap-off; KL direction is reference to cap. ΔNLL is log(p_reference/p_cap); positive is worse. ES99+ is the fractional mean of the worst 1% of positive loss increases, including zeros. These are fixed, dependent positions, not independent replications. Concentration alone does not establish a power-law or other heavy-tail family.

| Dataset | Arm | Cells | Mean KL | Mean ΔNLL | Mean ES99+ | Mean of cell maxima | Largest single maximum | P(>0.01) | P(>0.1) | P(>1) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | SE-A | 1 | 0.00186062 | 0.00181293 | 0.195585 | 9.26227 | 9.26227 | 0.00117845 | 0.00112952 | 0.000619809 |
| zsre | SE-E | 1 | 0.00170361 | 0.00167283 | 0.181614 | 12.27 | 12.27 | 0.00118253 | 0.00112136 | 0.000591265 |
| counterfact | SE-A | 1 | 0.00417566 | 0.0043814 | 0.458686 | 11.7442 | 11.7442 | 0.00281768 | 0.00267904 | 0.00140272 |
| counterfact | SE-E | 1 | 0.00430833 | 0.00450374 | 0.469916 | 12.2254 | 12.2254 | 0.00284623 | 0.0026872 | 0.00145981 |

The mean of cell maxima is not the largest observed loss; both are displayed explicitly. Exceedances are fractions, not percentages.

| Dataset | r | Paired mean ΔKL | Paired mean ΔNLL | Difference of arm ES99+ | ES99+ of paired loss differences |
| --- | --- | --- | --- | --- | --- |
| zsre | 0 | -0.000157009 | -0.000140103 | -0.0139706 | 0.0160704 |
| counterfact | 0 | 0.000132678 | 0.000122341 | 0.0112291 | 0.0382164 |

Separate readout: 5004.200 process seconds (1.390 hours), charged once. The original cost receipt remains **failed** because final table generation raised KeyError('smoke'); all four arm receipts and both paired vectors pass this independent numerical reconstruction. The original cost-repair.json and wrong-caption table remain preserved. This report supplies the correct full-inventory caption.

All per-cell tail statistics, maximum locations/ties, exceedances, positive-harm half-mass counts and both references remain in the bound harm JSON and vectors. Zero total positive harm makes half-mass undefined.

## Interpretation

The endpoint differences are small, with one CounterFact paraphrase difference; that is not proof of equivalence. Average harm moves in opposite directions across the two datasets. The SE-E single-position maximum is higher on both datasets, including about 12.27 versus 9.26 nats on zsRE. Neither 'indistinguishable on every endpoint' nor 'unchanged within position noise' is justified by this one-realization design. Positions are paired observations, not an independent noise estimate. The full-inventory and legacy-v0 inventories and base models differ; do not compare their maxima as a causal effect of reader architecture.
