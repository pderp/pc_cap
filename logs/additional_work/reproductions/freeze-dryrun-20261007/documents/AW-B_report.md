# Bounded correction: calibration and exposed-stream evaluation

## Calibration: all sixteen settings

Exposed development memories, 300 edits per dataset. Selection precedes evaluation. All means and tails below use the full 245,237-position fixed-prefix inventory. ES is a saved-memory re-query, equal to RET-ES, not immediate acquisition. RET-GS is the installed item-level paraphrase score and can include fractional item credit.

| Dataset | Setting | ES | RET-ES | RET-GS | LS | near_miss | revision | Mean KL | Mean ΔNLL | ES99+ | Max ΔNLL | Eligible on both datasets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | v5 | 0.996667 | 0.996667 | 0.973333 | 1 | 0.87 | 1 | 0.00226972 | 0.00231002 | 0.237363 | 9.94469 | reference |
| zsre | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | reference |
| zsre | clip:0.5 | 0 | 0 | 0 | 1 | 1 | 0 | 3.58605e-05 | 4.50619e-05 | 0.0112707 | 0.47582 | False |
| zsre | mixture:0.367879 | 0.996667 | 0.996667 | 0.973333 | 1 | 0.87 | 1 | 0.000707308 | 0.000711152 | 0.0760992 | 0.999918 | True |
| zsre | clip:1 | 0 | 0 | 0 | 1 | 1 | 0 | 0.000100914 | 0.00012586 | 0.022186 | 0.971916 | False |
| zsre | mixture:0.135335 | 0.996667 | 0.996667 | 0.973333 | 1 | 0.87 | 1 | 0.00126169 | 0.00127257 | 0.133141 | 1.99969 | True |
| zsre | clip:2 | 0.0233333 | 0.0233333 | 0.00333333 | 1 | 1 | 0.04 | 0.000239609 | 0.000271712 | 0.0399144 | 1.68793 | False |
| zsre | mixture:0.0183156 | 0.996667 | 0.996667 | 0.973333 | 1 | 0.87 | 1 | 0.0019108 | 0.00192328 | 0.198627 | 3.99743 | True |
| zsre | clip:4 | 0.363333 | 0.363333 | 0.33 | 1 | 0.94 | 0.36 | 0.000565227 | 0.000579856 | 0.0724626 | 3.48863 | False |
| zsre | mixture:0.000335463 | 0.996667 | 0.996667 | 0.973333 | 1 | 0.87 | 1 | 0.00224227 | 0.00227054 | 0.233414 | 7.86636 | True |
| zsre | shrink:0.25 | 0.0233333 | 0.0233333 | 0.0133333 | 1 | 1 | 0.02 | 2.52627e-05 | 3.53354e-05 | 0.0102382 | 0.838104 | False |
| zsre | shrink:0.5 | 0.686667 | 0.686667 | 0.523333 | 1 | 0.94 | 0.8 | 0.000144328 | 0.000164474 | 0.0274169 | 1.77144 | False |
| zsre | shrink:0.75 | 0.996667 | 0.996667 | 0.963333 | 1 | 0.87 | 1 | 0.000637218 | 0.000667436 | 0.0775842 | 5.16498 | False |
| zsre | gate:0.4 | 0.996667 | 0.996667 | 0.936667 | 1 | 0.89 | 1 | 0.00119372 | 0.00118687 | 0.122732 | 9.94469 | False |
| zsre | gate:0.3 | 0.996667 | 0.996667 | 0.89 | 1 | 0.89 | 1 | 0.000489537 | 0.000480396 | 0.0485787 | 7.08622 | False |
| zsre | gate:0.2 | 0.996667 | 0.996667 | 0.843333 | 1 | 0.92 | 1 | 0.000128021 | 0.000136498 | 0.0136498 | 6.25724 | False |
| counterfact | v5 | 1 | 1 | 0.753333 | 0.98 | 1 | 1 | 0.00592908 | 0.00594535 | 0.610483 | 14.0189 | reference |
| counterfact | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | reference |
| counterfact | clip:0.5 | 0 | 0 | 0 | 1 | 1 | 0 | 8.94517e-05 | 9.45276e-05 | 0.0269599 | 0.518595 | False |
| counterfact | mixture:0.367879 | 1 | 1 | 0.745 | 0.98 | 1 | 1 | 0.00160171 | 0.00161787 | 0.173316 | 0.999999 | True |
| counterfact | clip:1 | 0 | 0 | 0 | 1 | 1 | 0 | 0.000251509 | 0.000278407 | 0.0532289 | 0.955991 | False |
| counterfact | mixture:0.135335 | 1 | 1 | 0.753333 | 0.98 | 1 | 1 | 0.00292484 | 0.00294834 | 0.309255 | 1.99999 | True |
| counterfact | clip:2 | 0.06 | 0.06 | 0.035 | 1 | 1 | 0.04 | 0.000602666 | 0.000628655 | 0.0960076 | 1.75216 | False |
| counterfact | mixture:0.0183156 | 1 | 1 | 0.753333 | 0.98 | 1 | 1 | 0.00464092 | 0.0046712 | 0.482867 | 3.99996 | True |
| counterfact | clip:4 | 0.67 | 0.67 | 0.413333 | 0.98 | 1 | 0.56 | 0.00144221 | 0.00146507 | 0.18396 | 4.01473 | False |
| counterfact | mixture:0.000335463 | 1 | 1 | 0.753333 | 0.98 | 1 | 1 | 0.00576468 | 0.00580267 | 0.596211 | 7.99757 | True |
| counterfact | shrink:0.25 | 0.0366667 | 0.0366667 | 0.00666667 | 1 | 1 | 0 | 8.65975e-05 | 9.06651e-05 | 0.0273046 | 0.880767 | False |
| counterfact | shrink:0.5 | 0.826667 | 0.826667 | 0.355 | 1 | 1 | 0.86 | 0.000467657 | 0.000475792 | 0.076857 | 3.18266 | False |
| counterfact | shrink:0.75 | 1 | 1 | 0.688333 | 0.98 | 1 | 1 | 0.00186503 | 0.00187723 | 0.215754 | 7.67421 | False |
| counterfact | gate:0.4 | 1 | 1 | 0.741667 | 0.98 | 1 | 1 | 0.00406943 | 0.00411213 | 0.420645 | 10.3691 | False |
| counterfact | gate:0.3 | 0.993333 | 0.993333 | 0.711667 | 0.98 | 1 | 1 | 0.00275639 | 0.00277626 | 0.283609 | 10.1554 | False |
| counterfact | gate:0.2 | 0.856667 | 0.856667 | 0.65 | 0.98 | 1 | 0.98 | 0.00156517 | 0.0015625 | 0.159977 | 8.27882 | False |



Eligibility requires RET-ES and RET-GS within ±0.02 of v5 on **both** datasets, without decreasing LS or near-miss preservation. Rank eligible arms by the **smaller** dataset reduction in maximum harm, then the **smaller** ES99 reduction; complete ties retain the declared setting order. At most one bound and one shrink/gate comparator may advance.

| Setting | Category | Eligible | Worst-dataset max reduction | Worst-dataset ES99 reduction | zsRE efficacy changes | CounterFact efficacy changes |
| --- | --- | --- | --- | --- | --- | --- |
| clip:0.5 | bound | False | 9.46887 | 0.226093 | {'RET-ES': -0.9966666666666667, 'RET-GS': -0.9733333333333334, 'LS': 0.0, 'near_miss': 0.13} | {'RET-ES': -1.0, 'RET-GS': -0.7533333333333333, 'LS': 0.020000000000000018, 'near_miss': 0.0} |
| mixture:0.367879 | bound | True | 8.94477 | 0.161264 | {'RET-ES': 0.0, 'RET-GS': 0.0, 'LS': 0.0, 'near_miss': 0.0} | {'RET-ES': 0.0, 'RET-GS': -0.008333333333333304, 'LS': 0.0, 'near_miss': 0.0} |
| clip:1 | bound | False | 8.97277 | 0.215177 | {'RET-ES': -0.9966666666666667, 'RET-GS': -0.9733333333333334, 'LS': 0.0, 'near_miss': 0.13} | {'RET-ES': -1.0, 'RET-GS': -0.7533333333333333, 'LS': 0.020000000000000018, 'near_miss': 0.0} |
| mixture:0.135335 | bound | True | 7.945 | 0.104222 | {'RET-ES': 0.0, 'RET-GS': 0.0, 'LS': 0.0, 'near_miss': 0.0} | {'RET-ES': 0.0, 'RET-GS': 0.0, 'LS': 0.0, 'near_miss': 0.0} |
| clip:2 | bound | False | 8.25676 | 0.197449 | {'RET-ES': -0.9733333333333334, 'RET-GS': -0.9700000000000001, 'LS': 0.0, 'near_miss': 0.13} | {'RET-ES': -0.94, 'RET-GS': -0.7183333333333333, 'LS': 0.020000000000000018, 'near_miss': 0.0} |
| mixture:0.0183156 | bound | True | 5.94726 | 0.038736 | {'RET-ES': 0.0, 'RET-GS': 0.0, 'LS': 0.0, 'near_miss': 0.0} | {'RET-ES': 0.0, 'RET-GS': 0.0, 'LS': 0.0, 'near_miss': 0.0} |
| clip:4 | bound | False | 6.45606 | 0.164901 | {'RET-ES': -0.6333333333333333, 'RET-GS': -0.6433333333333333, 'LS': 0.0, 'near_miss': 0.06999999999999995} | {'RET-ES': -0.32999999999999996, 'RET-GS': -0.33999999999999997, 'LS': 0.0, 'near_miss': 0.0} |
| mixture:0.000335463 | bound | True | 2.07833 | 0.00394897 | {'RET-ES': 0.0, 'RET-GS': 0.0, 'LS': 0.0, 'near_miss': 0.0} | {'RET-ES': 0.0, 'RET-GS': 0.0, 'LS': 0.0, 'near_miss': 0.0} |
| shrink:0.25 | comparator | False | 9.10658 | 0.227125 | {'RET-ES': -0.9733333333333334, 'RET-GS': -0.9600000000000001, 'LS': 0.0, 'near_miss': 0.13} | {'RET-ES': -0.9633333333333334, 'RET-GS': -0.7466666666666666, 'LS': 0.020000000000000018, 'near_miss': 0.0} |
| shrink:0.5 | comparator | False | 8.17325 | 0.209947 | {'RET-ES': -0.31000000000000005, 'RET-GS': -0.45000000000000007, 'LS': 0.0, 'near_miss': 0.06999999999999995} | {'RET-ES': -0.17333333333333334, 'RET-GS': -0.3983333333333333, 'LS': 0.020000000000000018, 'near_miss': 0.0} |
| shrink:0.75 | comparator | False | 4.77971 | 0.159779 | {'RET-ES': 0.0, 'RET-GS': -0.010000000000000009, 'LS': 0.0, 'near_miss': 0.0} | {'RET-ES': 0.0, 'RET-GS': -0.06499999999999995, 'LS': 0.0, 'near_miss': 0.0} |
| gate:0.4 | comparator | False | 0 | 0.114632 | {'RET-ES': 0.0, 'RET-GS': -0.036666666666666736, 'LS': 0.0, 'near_miss': 0.020000000000000018} | {'RET-ES': 0.0, 'RET-GS': -0.011666666666666603, 'LS': 0.0, 'near_miss': 0.0} |
| gate:0.3 | comparator | False | 2.85846 | 0.188785 | {'RET-ES': 0.0, 'RET-GS': -0.08333333333333337, 'LS': 0.0, 'near_miss': 0.020000000000000018} | {'RET-ES': -0.00666666666666671, 'RET-GS': -0.04166666666666663, 'LS': 0.0, 'near_miss': 0.0} |
| gate:0.2 | comparator | False | 3.68745 | 0.223714 | {'RET-ES': 0.0, 'RET-GS': -0.13, 'LS': 0.0, 'near_miss': 0.050000000000000044} | {'RET-ES': -0.1433333333333333, 'RET-GS': -0.10333333333333328, 'LS': 0.0, 'near_miss': 0.0} |



The selected bound is **mixture ρ = exp(−1)**, with 1−ρ ≈ 0.6321 multiplying the cap distribution. No shrink/gate comparator is eligible, so evaluation contains three arms rather than filling the missing slot with an ineligible comparator.

Every clip setting fails retention eligibility. Its symmetric log-ratio restriction limits increases as well as decreases relative to the base; after normalization, no token can gain more than 2b nats relative to that base. This is consistent with suppressing strong edited-answer corrections, although aggregate scores alone do not isolate every decoding cause. Mixture instead preserves a base-probability floor while permitting large increases for tokens the base considers unlikely. It does **not** generally guarantee unchanged greedy answers: the measured CounterFact RET-GS falls from 0.753333 to 0.745000 (−0.8333 percentage points), inside the registered tolerance. zsRE scores are unchanged.

The calibration mixture brings zsRE mean KL below 0.001, but CounterFact remains above that line. No κ or coupled-free-energy objective is used here. Without an eligible shrink/gate comparator, this experiment cannot establish superiority to an efficacy-matched weakening control.

Calibration cost: 19467.922 process seconds (5.408 h), including construction, wrapper scoring, efficacy and temporary endpoint teaching. Thirteen numerical settings share one pass; the three gates use separate passes. No repeated per-setting pass times are summed as extra work.

## Exposed sealed-stream evaluation

Realization 0, five paired orders, two datasets, restored original 300-edit memories. These are already-exposed populations. No result here enters parameter selection. All per-order values and differences remain visible; positions and orders are not independent realizations.

| Memory | Setting | ES | RET-ES | RET-GS | LS | near_miss | revision | Mean KL | Mean ΔNLL | ES99+ | Max ΔNLL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre-o103 | v5 | 1 | 1 | 0.983333 | 1 | 0.83 | 1 | 0.00146107 | 0.00156859 | 0.162834 | 9.26227 |
| zsre-o103 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| zsre-o103 | mixture:0.367879 | 1 | 1 | 0.983333 | 1 | 0.83 | 1 | 0.000452492 | 0.000480151 | 0.0522019 | 0.999837 |
| zsre-o100 | v5 | 1 | 1 | 0.983333 | 1 | 0.76 | 1 | 0.00186062 | 0.00181293 | 0.195585 | 9.26227 |
| zsre-o100 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| zsre-o100 | mixture:0.367879 | 1 | 1 | 0.983333 | 1 | 0.76 | 1 | 0.000583378 | 0.00054405 | 0.0653418 | 0.999837 |
| counterfact-o102 | v5 | 1 | 1 | 0.748333 | 1 | 1 | 1 | 0.00690961 | 0.0068986 | 0.71135 | 15.3818 |
| counterfact-o102 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o102 | mixture:0.367879 | 1 | 1 | 0.741667 | 1 | 1 | 1 | 0.0019479 | 0.00195307 | 0.211755 | 1 |
| counterfact-o103 | v5 | 0.996667 | 0.996667 | 0.758333 | 1 | 1 | 1 | 0.00532 | 0.00547311 | 0.564284 | 11.7442 |
| counterfact-o103 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o103 | mixture:0.367879 | 0.996667 | 0.996667 | 0.748333 | 1 | 1 | 1 | 0.0014471 | 0.0014848 | 0.1609 | 0.999986 |
| zsre-o101 | v5 | 1 | 1 | 0.993333 | 1 | 0.8 | 1 | 0.00176972 | 0.00186703 | 0.195796 | 12.2931 |
| zsre-o101 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| zsre-o101 | mixture:0.367879 | 1 | 1 | 0.993333 | 1 | 0.8 | 1 | 0.000580211 | 0.000601304 | 0.0667045 | 0.999992 |
| zsre-o102 | v5 | 1 | 1 | 0.983333 | 1 | 0.77 | 1 | 0.00186937 | 0.00186419 | 0.194865 | 8.30384 |
| zsre-o102 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| zsre-o102 | mixture:0.367879 | 1 | 1 | 0.983333 | 1 | 0.77 | 1 | 0.000582556 | 0.000575304 | 0.0635293 | 0.999575 |
| counterfact-o104 | v5 | 1 | 1 | 0.795 | 0.98 | 1 | 1 | 0.00641211 | 0.00662269 | 0.690296 | 11.7442 |
| counterfact-o104 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o104 | mixture:0.367879 | 1 | 1 | 0.783333 | 0.98 | 1 | 1 | 0.00193711 | 0.00195718 | 0.216662 | 0.999986 |
| counterfact-o101 | v5 | 1 | 1 | 0.726667 | 1 | 1 | 1 | 0.00491337 | 0.0050381 | 0.51939 | 15.3818 |
| counterfact-o101 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o101 | mixture:0.367879 | 1 | 1 | 0.716667 | 1 | 1 | 1 | 0.00133934 | 0.00138617 | 0.149813 | 1 |
| zsre-o104 | v5 | 1 | 1 | 0.976667 | 1 | 0.78 | 1 | 0.00202264 | 0.00196767 | 0.212105 | 12.2931 |
| zsre-o104 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| zsre-o104 | mixture:0.367879 | 1 | 1 | 0.976667 | 1 | 0.78 | 1 | 0.000653194 | 0.000610924 | 0.0723994 | 0.999992 |
| counterfact-o100 | v5 | 1 | 1 | 0.806667 | 1 | 1 | 1 | 0.00417566 | 0.0043814 | 0.458686 | 11.7442 |
| counterfact-o100 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o100 | mixture:0.367879 | 1 | 1 | 0.795 | 1 | 1 | 1 | 0.00126503 | 0.00132888 | 0.147613 | 0.999986 |



Paired differences, setting minus v5 (loss lower is better):

| Memory | Setting | ΔES | ΔRET-ES | ΔRET-GS | ΔLS | Δnear_miss | Δrevision | Δmean KL | Δmean NLL | ΔES99+ | Δmaximum |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre-o103 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| zsre-o103 | capoff | -1 | -1 | -0.983333 | 0 | 0.17 | -1 | -0.00146107 | -0.00156859 | -0.162834 | -9.26227 |
| zsre-o103 | mixture:0.367879 | 0 | 0 | 0 | 0 | 0 | 0 | -0.00100858 | -0.00108844 | -0.110632 | -8.26243 |
| zsre-o100 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| zsre-o100 | capoff | -1 | -1 | -0.983333 | 0 | 0.24 | -1 | -0.00186062 | -0.00181293 | -0.195585 | -9.26227 |
| zsre-o100 | mixture:0.367879 | 0 | 0 | 0 | 0 | 0 | 0 | -0.00127724 | -0.00126888 | -0.130243 | -8.26243 |
| counterfact-o102 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o102 | capoff | -1 | -1 | -0.748333 | 0 | 0 | -1 | -0.00690961 | -0.0068986 | -0.71135 | -15.3818 |
| counterfact-o102 | mixture:0.367879 | 0 | 0 | -0.00666667 | 0 | 0 | 0 | -0.00496172 | -0.00494554 | -0.499595 | -14.3818 |
| counterfact-o103 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o103 | capoff | -0.996667 | -0.996667 | -0.758333 | 0 | 0 | -1 | -0.00532 | -0.00547311 | -0.564284 | -11.7442 |
| counterfact-o103 | mixture:0.367879 | 0 | 0 | -0.01 | 0 | 0 | 0 | -0.00387291 | -0.0039883 | -0.403384 | -10.7443 |
| zsre-o101 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| zsre-o101 | capoff | -1 | -1 | -0.993333 | 0 | 0.2 | -1 | -0.00176972 | -0.00186703 | -0.195796 | -12.2931 |
| zsre-o101 | mixture:0.367879 | 0 | 0 | 0 | 0 | 0 | 0 | -0.00118951 | -0.00126573 | -0.129092 | -11.2931 |
| zsre-o102 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| zsre-o102 | capoff | -1 | -1 | -0.983333 | 0 | 0.23 | -1 | -0.00186937 | -0.00186419 | -0.194865 | -8.30384 |
| zsre-o102 | mixture:0.367879 | 0 | 0 | 0 | 0 | 0 | 0 | -0.00128681 | -0.00128888 | -0.131336 | -7.30426 |
| counterfact-o104 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o104 | capoff | -1 | -1 | -0.795 | 0.02 | 0 | -1 | -0.00641211 | -0.00662269 | -0.690296 | -11.7442 |
| counterfact-o104 | mixture:0.367879 | 0 | 0 | -0.0116667 | 0 | 0 | 0 | -0.004475 | -0.00466551 | -0.473634 | -10.7443 |
| counterfact-o101 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o101 | capoff | -1 | -1 | -0.726667 | 0 | 0 | -1 | -0.00491337 | -0.0050381 | -0.51939 | -15.3818 |
| counterfact-o101 | mixture:0.367879 | 0 | 0 | -0.01 | 0 | 0 | 0 | -0.00357403 | -0.00365193 | -0.369578 | -14.3818 |
| zsre-o104 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| zsre-o104 | capoff | -1 | -1 | -0.976667 | 0 | 0.22 | -1 | -0.00202264 | -0.00196767 | -0.212105 | -12.2931 |
| zsre-o104 | mixture:0.367879 | 0 | 0 | 0 | 0 | 0 | 0 | -0.00136945 | -0.00135674 | -0.139705 | -11.2931 |
| counterfact-o100 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o100 | capoff | -1 | -1 | -0.806667 | 0 | 0 | -1 | -0.00417566 | -0.0043814 | -0.458686 | -11.7442 |
| counterfact-o100 | mixture:0.367879 | 0 | 0 | -0.0116667 | 0 | 0 | 0 | -0.00291063 | -0.00305252 | -0.311073 | -10.7443 |



Predeclared usefulness requires smaller maximum and ES99+, with both retention scores within ±0.02, in every dataset/order. This is a conjunction across the declared cells, not an aggregate-average claim.

| Setting | Every coordinate passes |
| --- | --- |
| capoff | False |
| mixture:0.367879 | True |
| v5 | False |



Evaluation process time: 21083.167 seconds (5.856 h), separate from calibration.

## What the one-nat guarantee says

For the same fixed prefix h and target token y, let p₀ be the unchanged base distribution and p₁ the cap distribution. The selected mixture is q = ρp₀ + (1−ρ)p₁ with ρ = exp(−1). Since q(y|h) ≥ ρp₀(y|h),

    ΔNLL(y|h) = log[p₀(y|h) / q(y|h)] ≤ −log ρ = 1 nat.

This is a per-token likelihood-ratio bound relative to the specified base, at the same prefix. It is **not** a one-nat bound on total sequence loss, generated-text loss on different prefixes, semantic harm, or greedy-answer preservation. Along a shared teacher-forced sequence of N prefixes, the bounds sum to at most N nats, not one. The mixture also implies KL(p₀ || q) ≤ 1 nat, which is much weaker than the unchanged 0.001 mean-KL benchmark. No bound is asserted relative to another independently trained base.

Survival curves use P(ΔNLL > x), including zero and beneficial positions in the denominator. The one-nat ceiling is shown explicitly. Apparent concentration or a truncated observed tail does not prove a heavy-tail family. This query-time intervention tests a way of limiting extreme prediction loss in the active-inference testbed; it introduces neither PC acquisition nor autonomous policy inference.

