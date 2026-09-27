# HT-15 — cell tails and realization spread

Snapshot: 2026-09-26T23:20:29.456477+00:00; 262 successfully finished cells. CPU analysis of saved vectors.

Reference: each cap's own cap-off base. S1 base-continuation effects are outside this contrast. Each cell has 245,237 repeated ordinary-text positions; they are not independent replicates. ES99+ is the fractional average over the worst 1% of positive-part losses, zeros retained. Ranges below are descriptive ranges of three realization means, not confidence intervals. Within each realization five dependent stream orders are averaged. Incomplete groups have no full range. Zero positive mass leaves half-mass concentration undefined. Cell CSV includes maximum locations; all indices are zero-based, and target_token_offset starts at 1 because the first token supplies context.

| Condition | Dataset | Cells / 15 | Metric | Mean over observed cells | r0 (n) | r1 (n) | r2 (n) | Full r range |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| R1_learned_ff | counterfact | 15 | mean_signed | 0.00549791 | 0.00584963 (5) | 0.0046208 (5) | 0.00602332 (5) | 0.0046208 to 0.00602332 |
| R1_learned_ff | counterfact | 15 | es99_positive | 0.570613 | 0.61007 (5) | 0.479876 (5) | 0.621891 (5) | 0.479876 to 0.621891 |
| R1_learned_ff | counterfact | 15 | maximum | 13.5928 | 15.3818 (5) | 11.3658 (5) | 14.0308 (5) | 11.3658 to 15.3818 |
| R1_learned_ff | counterfact | 15 | exceed_0.01 | 0.00298351 | 0.00298079 (5) | 0.00263419 (5) | 0.00333555 (5) | 0.00263419 to 0.00333555 |
| R1_learned_ff | counterfact | 15 | exceed_1 | 0.00165146 | 0.00168001 (5) | 0.00145573 (5) | 0.00181865 (5) | 0.00145573 to 0.00181865 |
| R1_learned_ff | counterfact | 15 | exceed_5 | 0.000270487 | 0.000326215 (5) | 0.000207962 (5) | 0.000277283 (5) | 0.000207962 to 0.000326215 |
| R1_learned_ff | counterfact | 15 | half_mass_positions | 127.667 | 123 (5) | 114 (5) | 146 (5) | 114 to 146 |
| R1_learned_ff | mquake | 15 | mean_signed | 0.00607367 | 0.00714616 (5) | 0.00693902 (5) | 0.00413585 (5) | 0.00413585 to 0.00714616 |
| R1_learned_ff | mquake | 15 | es99_positive | 0.620475 | 0.730636 (5) | 0.710095 (5) | 0.420694 (5) | 0.420694 to 0.730636 |
| R1_learned_ff | mquake | 15 | maximum | 13.486 | 13.1443 (5) | 17.0605 (5) | 10.2532 (5) | 10.2532 to 17.0605 |
| R1_learned_ff | mquake | 15 | exceed_0.01 | 0.00313302 | 0.00362099 (5) | 0.00348235 (5) | 0.00229574 (5) | 0.00229574 to 0.00362099 |
| R1_learned_ff | mquake | 15 | exceed_1 | 0.00194098 | 0.00223865 (5) | 0.0021938 (5) | 0.00139049 (5) | 0.00139049 to 0.00223865 |
| R1_learned_ff | mquake | 15 | exceed_5 | 0.000225632 | 0.000256894 (5) | 0.000289516 (5) | 0.000130486 (5) | 0.000130486 to 0.000289516 |
| R1_learned_ff | mquake | 15 | half_mass_positions | 156.667 | 185 (5) | 171 (5) | 114 (5) | 114 to 185 |
| R1_learned_ff | zsre | 15 | mean_signed | 0.00248586 | 0.00245023 (5) | 0.00255302 (5) | 0.00245432 (5) | 0.00245023 to 0.00255302 |
| R1_learned_ff | zsre | 15 | es99_positive | 0.259815 | 0.258806 (5) | 0.266315 (5) | 0.254325 (5) | 0.254325 to 0.266315 |
| R1_learned_ff | zsre | 15 | maximum | 9.75467 | 9.26227 (5) | 8.95399 (5) | 11.0477 (5) | 8.95399 to 11.0477 |
| R1_learned_ff | zsre | 15 | exceed_0.01 | 0.00159438 | 0.00161069 (5) | 0.00163923 (5) | 0.00153321 (5) | 0.00153321 to 0.00163923 |
| R1_learned_ff | zsre | 15 | exceed_1 | 0.000796508 | 0.000803305 (5) | 0.000815538 (5) | 0.000770683 (5) | 0.000770683 to 0.000815538 |
| R1_learned_ff | zsre | 15 | exceed_5 | 8.56315e-05 | 8.56315e-05 (5) | 0.000101942 (5) | 6.93207e-05 (5) | 6.93207e-05 to 0.000101942 |
| R1_learned_ff | zsre | 15 | half_mass_positions | 68.6667 | 69 (5) | 70 (5) | 67 (5) | 67 to 70 |
| R1_nonlearned | counterfact | 15 | mean_signed | 0.0706286 | 0.0595273 (5) | 0.0882374 (5) | 0.0641211 (5) | 0.0595273 to 0.0882374 |
| R1_nonlearned | counterfact | 15 | es99_positive | 5.45373 | 5.02336 (5) | 6.14514 (5) | 5.19268 (5) | 5.02336 to 6.14514 |
| R1_nonlearned | counterfact | 15 | maximum | 18.0114 | 20.2834 (5) | 17.4515 (5) | 16.2994 (5) | 16.2994 to 20.2834 |
| R1_nonlearned | counterfact | 15 | exceed_0.01 | 0.0204499 | 0.0180446 (5) | 0.0234182 (5) | 0.0198869 (5) | 0.0180446 to 0.0234182 |
| R1_nonlearned | counterfact | 15 | exceed_1 | 0.0170488 | 0.0147653 (5) | 0.0202865 (5) | 0.0160946 (5) | 0.0147653 to 0.0202865 |
| R1_nonlearned | counterfact | 15 | exceed_5 | 0.00521944 | 0.00410215 (5) | 0.00704217 (5) | 0.004514 (5) | 0.00410215 to 0.00704217 |
| R1_nonlearned | counterfact | 15 | half_mass_positions | 1259.33 | 1077 (5) | 1552 (5) | 1149 (5) | 1077 to 1552 |
| R1_nonlearned | mquake | 15 | mean_signed | 0.0121018 | 0.0120472 (5) | 0.0120871 (5) | 0.0121709 (5) | 0.0120472 to 0.0121709 |
| R1_nonlearned | mquake | 15 | es99_positive | 1.22449 | 1.21908 (5) | 1.22397 (5) | 1.23044 (5) | 1.21908 to 1.23044 |
| R1_nonlearned | mquake | 15 | maximum | 14.239 | 15.0722 (5) | 12.7709 (5) | 14.8738 (5) | 12.7709 to 15.0722 |
| R1_nonlearned | mquake | 15 | exceed_0.01 | 0.00408856 | 0.00414293 (5) | 0.00404914 (5) | 0.00407361 (5) | 0.00404914 to 0.00414293 |
| R1_nonlearned | mquake | 15 | exceed_1 | 0.0033573 | 0.00337225 (5) | 0.00333555 (5) | 0.00336409 (5) | 0.00333555 to 0.00337225 |
| R1_nonlearned | mquake | 15 | exceed_5 | 0.000686411 | 0.000701362 (5) | 0.000701362 (5) | 0.000656508 (5) | 0.000656508 to 0.000701362 |
| R1_nonlearned | mquake | 15 | half_mass_positions | 255 | 254 (5) | 258 (5) | 253 (5) | 253 to 258 |
| R1_nonlearned | zsre | 15 | mean_signed | 0.000469895 | 0.000316561 (5) | 0.000716578 (5) | 0.000376546 (5) | 0.000316561 to 0.000716578 |
| R1_nonlearned | zsre | 15 | es99_positive | 0.0481189 | 0.0324633 (5) | 0.0735695 (5) | 0.038324 (5) | 0.0324633 to 0.0735695 |
| R1_nonlearned | zsre | 15 | maximum | 6.16107 | 5.66083 (5) | 7.00099 (5) | 5.82137 (5) | 5.66083 to 7.00099 |
| R1_nonlearned | zsre | 15 | exceed_0.01 | 0.000266409 | 0.000216117 (5) | 0.000395536 (5) | 0.000187574 (5) | 0.000187574 to 0.000395536 |
| R1_nonlearned | zsre | 15 | exceed_1 | 0.000172622 | 0.000114175 (5) | 0.000248739 (5) | 0.000154952 (5) | 0.000114175 to 0.000248739 |
| R1_nonlearned | zsre | 15 | exceed_5 | 9.51461e-06 | 4.07769e-06 (5) | 2.03884e-05 (5) | 4.07769e-06 (5) | 4.07769e-06 to 2.03884e-05 |
| R1_nonlearned | zsre | 15 | half_mass_positions | 15.6667 | 12 (5) | 22 (5) | 13 (5) | 12 to 22 |
| S1_LM | counterfact | 15 | mean_signed | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| S1_LM | counterfact | 15 | es99_positive | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| S1_LM | counterfact | 15 | maximum | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| S1_LM | counterfact | 15 | exceed_0.01 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| S1_LM | counterfact | 15 | exceed_1 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| S1_LM | counterfact | 15 | exceed_5 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| S1_LM | counterfact | 15 | half_mass_positions | undefined / incomplete | undefined / incomplete (5) | undefined / incomplete (5) | undefined / incomplete (5) | — |
| S1_LM | zsre | 15 | mean_signed | 0.00155872 | 0.00108663 (5) | 0.0019292 (5) | 0.00166032 (5) | 0.00108663 to 0.0019292 |
| S1_LM | zsre | 15 | es99_positive | 0.180511 | 0.132904 (5) | 0.216925 (5) | 0.191705 (5) | 0.132904 to 0.216925 |
| S1_LM | zsre | 15 | maximum | 25.3032 | 26.9174 (5) | 26.2938 (5) | 22.6986 (5) | 22.6986 to 26.9174 |
| S1_LM | zsre | 15 | exceed_0.01 | 0.00104933 | 0.00100148 (5) | 0.00114501 (5) | 0.00100148 (5) | 0.00100148 to 0.00114501 |
| S1_LM | zsre | 15 | exceed_1 | 0.000335458 | 0.000247923 (5) | 0.00034905 (5) | 0.0004094 (5) | 0.000247923 to 0.0004094 |
| S1_LM | zsre | 15 | exceed_5 | 9.59616e-05 | 5.79032e-05 (5) | 0.000127224 (5) | 0.000102758 (5) | 5.79032e-05 to 0.000127224 |
| S1_LM | zsre | 15 | half_mass_positions | 19.4 | 15 (5) | 19.8 (5) | 23.4 (5) | 15 to 23.4 |
| S1_literal | zsre | 7 | mean_signed | 0.0013972 | 0.00108576 (5) | 0.0021758 (2) | undefined / incomplete (0) | — |
| S1_literal | zsre | 7 | es99_positive | 0.165132 | 0.132983 (5) | 0.245505 (2) | undefined / incomplete (0) | — |
| S1_literal | zsre | 7 | maximum | 26.7776 | 26.951 (5) | 26.3442 (2) | undefined / incomplete (0) | — |
| S1_literal | zsre | 7 | exceed_0.01 | 0.00111962 | 0.00100393 (5) | 0.00140884 (2) | undefined / incomplete (0) | — |
| S1_literal | zsre | 7 | exceed_1 | 0.000283691 | 0.000251186 (5) | 0.000364953 (2) | undefined / incomplete (0) | — |
| S1_literal | zsre | 7 | exceed_5 | 8.03887e-05 | 5.70876e-05 (5) | 0.000138641 (2) | undefined / incomplete (0) | — |
| S1_literal | zsre | 7 | half_mass_positions | 16.8571 | 15.2 (5) | 21 (2) | undefined / incomplete (0) | — |
| matched_update | counterfact | 15 | mean_signed | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| matched_update | counterfact | 15 | es99_positive | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| matched_update | counterfact | 15 | maximum | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| matched_update | counterfact | 15 | exceed_0.01 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| matched_update | counterfact | 15 | exceed_1 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| matched_update | counterfact | 15 | exceed_5 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| matched_update | counterfact | 15 | half_mass_positions | undefined / incomplete | undefined / incomplete (5) | undefined / incomplete (5) | undefined / incomplete (5) | — |
| matched_update | zsre | 15 | mean_signed | 0.00151316 | 0.00105644 (5) | 0.0017856 (5) | 0.00169745 (5) | 0.00105644 to 0.0017856 |
| matched_update | zsre | 15 | es99_positive | 0.176639 | 0.130173 (5) | 0.204576 (5) | 0.195167 (5) | 0.130173 to 0.204576 |
| matched_update | zsre | 15 | maximum | 22.1265 | 24.6112 (5) | 21.5077 (5) | 20.2605 (5) | 20.2605 to 24.6112 |
| matched_update | zsre | 15 | exceed_0.01 | 0.00105313 | 0.00102595 (5) | 0.00111158 (5) | 0.00102187 (5) | 0.00102187 to 0.00111158 |
| matched_update | zsre | 15 | exceed_1 | 0.000338448 | 0.000251186 (5) | 0.000346603 (5) | 0.000417555 (5) | 0.000251186 to 0.000417555 |
| matched_update | zsre | 15 | exceed_5 | 9.21558e-05 | 6.36119e-05 (5) | 0.000106835 (5) | 0.00010602 (5) | 6.36119e-05 to 0.000106835 |
| matched_update | zsre | 15 | half_mass_positions | 20.4667 | 17.6 (5) | 19.8 (5) | 24 (5) | 17.6 to 24 |
| v0_live_C1 | counterfact | 15 | mean_signed | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C1 | counterfact | 15 | es99_positive | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C1 | counterfact | 15 | maximum | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C1 | counterfact | 15 | exceed_0.01 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C1 | counterfact | 15 | exceed_1 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C1 | counterfact | 15 | exceed_5 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C1 | counterfact | 15 | half_mass_positions | undefined / incomplete | undefined / incomplete (5) | undefined / incomplete (5) | undefined / incomplete (5) | — |
| v0_live_C1 | zsre | 15 | mean_signed | 0.00189612 | 0.00143227 (5) | 0.00261712 (5) | 0.00163895 (5) | 0.00143227 to 0.00261712 |
| v0_live_C1 | zsre | 15 | es99_positive | 0.209756 | 0.162794 (5) | 0.277351 (5) | 0.189121 (5) | 0.162794 to 0.277351 |
| v0_live_C1 | zsre | 15 | maximum | 19.3169 | 26.9542 (5) | 12.2902 (5) | 18.7064 (5) | 12.2902 to 26.9542 |
| v0_live_C1 | zsre | 15 | exceed_0.01 | 0.0009588 | 0.000870179 (5) | 0.00105286 (5) | 0.000953363 (5) | 0.000870179 to 0.00105286 |
| v0_live_C1 | zsre | 15 | exceed_1 | 0.000457788 | 0.000291962 (5) | 0.000649168 (5) | 0.000432235 (5) | 0.000291962 to 0.000649168 |
| v0_live_C1 | zsre | 15 | exceed_5 | 0.000125321 | 8.07382e-05 (5) | 0.000181049 (5) | 0.000114175 (5) | 8.07382e-05 to 0.000181049 |
| v0_live_C1 | zsre | 15 | half_mass_positions | 34.5333 | 18.6 (5) | 54.6 (5) | 30.4 (5) | 18.6 to 54.6 |
| v0_live_C2 | counterfact | 15 | mean_signed | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C2 | counterfact | 15 | es99_positive | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C2 | counterfact | 15 | maximum | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C2 | counterfact | 15 | exceed_0.01 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C2 | counterfact | 15 | exceed_1 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C2 | counterfact | 15 | exceed_5 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C2 | counterfact | 15 | half_mass_positions | undefined / incomplete | undefined / incomplete (5) | undefined / incomplete (5) | undefined / incomplete (5) | — |
| v0_live_C2 | zsre | 15 | mean_signed | 0.00319807 | 0.00241095 (5) | 0.0034409 (5) | 0.00374234 (5) | 0.00241095 to 0.00374234 |
| v0_live_C2 | zsre | 15 | es99_positive | 0.32128 | 0.242571 (5) | 0.345971 (5) | 0.375299 (5) | 0.242571 to 0.375299 |
| v0_live_C2 | zsre | 15 | maximum | 43.1129 | 38.7553 (5) | 41.1178 (5) | 49.4658 (5) | 38.7553 to 49.4658 |
| v0_live_C2 | zsre | 15 | exceed_0.01 | 0.000186758 | 0.00017371 (5) | 0.00017371 (5) | 0.000212855 (5) | 0.00017371 to 0.000212855 |
| v0_live_C2 | zsre | 15 | exceed_1 | 0.000159574 | 0.00014435 (5) | 0.00014435 (5) | 0.00019002 (5) | 0.00014435 to 0.00019002 |
| v0_live_C2 | zsre | 15 | exceed_5 | 0.000150331 | 0.00012967 (5) | 0.000140272 (5) | 0.000181049 (5) | 0.00012967 to 0.000181049 |
| v0_live_C2 | zsre | 15 | half_mass_positions | 12.5333 | 10.8 (5) | 12.6 (5) | 14.2 (5) | 10.8 to 14.2 |
| v0_stable | counterfact | 15 | mean_signed | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | counterfact | 15 | es99_positive | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | counterfact | 15 | maximum | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | counterfact | 15 | exceed_0.01 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | counterfact | 15 | exceed_1 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | counterfact | 15 | exceed_5 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | counterfact | 15 | half_mass_positions | undefined / incomplete | undefined / incomplete (5) | undefined / incomplete (5) | undefined / incomplete (5) | — |
| v0_stable | mquake | 15 | mean_signed | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | mquake | 15 | es99_positive | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | mquake | 15 | maximum | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | mquake | 15 | exceed_0.01 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | mquake | 15 | exceed_1 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | mquake | 15 | exceed_5 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | mquake | 15 | half_mass_positions | undefined / incomplete | undefined / incomplete (5) | undefined / incomplete (5) | undefined / incomplete (5) | — |
| v0_stable | zsre | 15 | mean_signed | 0.00154124 | 0.00108652 (5) | 0.00189493 (5) | 0.00164227 (5) | 0.00108652 to 0.00189493 |
| v0_stable | zsre | 15 | es99_positive | 0.178654 | 0.132148 (5) | 0.213499 (5) | 0.190313 (5) | 0.132148 to 0.213499 |
| v0_stable | zsre | 15 | maximum | 25.3134 | 26.9542 (5) | 26.2876 (5) | 22.6985 (5) | 22.6985 to 26.9542 |
| v0_stable | zsre | 15 | exceed_0.01 | 0.0010409 | 0.000999034 (5) | 0.00113278 (5) | 0.000990878 (5) | 0.000990878 to 0.00113278 |
| v0_stable | zsre | 15 | exceed_1 | 0.000334914 | 0.000247923 (5) | 0.000349866 (5) | 0.000406953 (5) | 0.000247923 to 0.000406953 |
| v0_stable | zsre | 15 | exceed_5 | 9.43305e-05 | 5.70876e-05 (5) | 0.000123962 (5) | 0.000101942 (5) | 5.70876e-05 to 0.000123962 |
| v0_stable | zsre | 15 | half_mass_positions | 19 | 15 (5) | 19.2 (5) | 22.8 (5) | 15 to 22.8 |

A mean of cell ES99s is not ES99 of pooled positions; a mean of cell maxima is not a pooled maximum. A mean half-mass count is per cell and cannot be compared directly with a pooled count. Unavailable condition/dataset groups are not zero-valued observations. No claim of an asymptotic heavy-tail family follows.
