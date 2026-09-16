# HT-3d κ pilot aggregation

development pilot, no confirmatory p-values or causal heavy-tail claim.
Complete rows: 34/36. Snapshot: 2026-09-16T19:05:31.584817+00:00.

**What it is not.** It is not the coupled free energy of Nelson et al. (no coupled expectation, no changed
inference distribution), not a coupled Markov blanket, and not a test of the one-κ conjecture that porosity and
interference are the same parameter. It is the first controlled measurement of what a loss-level coupling does on
this substrate, which is the honest thing to bring to a session chaired by the people who defined κ.

Each coupled arm requires all its own and ordinary seed/dataset rows; missing clipped-control rows leave the descriptive control comparison pending. Whole-pilot completion is reported separately.

| Arm | Seed | Dataset | RET-GS | LS (legacy complete-answer) | Unseen FF/100 | ES95 harm | Max harm | Status |
|---|---:|---|---:|---:|---:|---:|---:|---|
| ordinary | 0 | zsre | 0.98 | 1 | 19 | 0.363503513 | 7.49131606 | complete |
| ordinary | 0 | counterfact | 0.785 | 0.98 | 0 | 0.691900142 | 6.45543346 | complete |
| ordinary | 0 | mquake | 0.77 | 1 | 0 | 0.295896009 | 6.93880304 | complete |
| ordinary | 1 | zsre | 0.94 | 1 | 6 | 8.56391104e-05 | 0.000167349399 | complete |
| ordinary | 1 | counterfact | 0.72 | 1 | 0 | 0.136296175 | 5.49101949 | complete |
| ordinary | 1 | mquake | 0.56 | 1 | 0 | 0.0525036053 | 2.07643866 | complete |
| ordinary | 2 | zsre | 0.98 | 1 | 10 | 0.111858747 | 8.68599724 | complete |
| ordinary | 2 | counterfact | 0.82 | 0.98 | — | 0.273591762 | 6.45543346 | unavailable |
| ordinary | 2 | mquake | 0.61 | 1 | — | 0.0806601855 | 3.77851409 | unavailable |
| kappa02 | 0 | zsre | 0.96 | 1 | 6 | 8.56391104e-05 | 0.000167349399 | complete |
| kappa02 | 0 | counterfact | 0.795 | 1 | 0 | 0.103252111 | 5.07467067 | complete |
| kappa02 | 0 | mquake | 0.69 | 1 | 0 | 0.0260187542 | 1.23378496 | complete |
| kappa02 | 1 | zsre | 0.93 | 1 | 6 | 8.56391104e-05 | 0.000167349399 | complete |
| kappa02 | 1 | counterfact | 0.77 | 1 | 0 | 0.381276803 | 6.45543346 | complete |
| kappa02 | 1 | mquake | 0.67 | 1 | 0 | 0.0591808885 | 2.98958289 | complete |
| kappa02 | 2 | zsre | 0.89 | 1 | 3 | 8.56391104e-05 | 0.000167349399 | complete |
| kappa02 | 2 | counterfact | 0.735 | 1 | 0 | 0.146065707 | 6.45543346 | complete |
| kappa02 | 2 | mquake | 0.35 | 1 | 0 | 0.0366673494 | 2.09820167 | complete |
| kappa05 | 0 | zsre | 0.95 | 1 | 6 | 8.56391104e-05 | 0.000167349399 | complete |
| kappa05 | 0 | counterfact | 0.785 | 1 | 0 | 0.176356606 | 6.42988206 | complete |
| kappa05 | 0 | mquake | 0.73 | 1 | 0 | 0.00956637045 | 1.07829324 | complete |
| kappa05 | 1 | zsre | 0.92 | 1 | 3 | 8.56391104e-05 | 0.000167349399 | complete |
| kappa05 | 1 | counterfact | 0.655 | 1 | 0 | 0.0902480365 | 4.45634799 | complete |
| kappa05 | 1 | mquake | 0.6 | 1 | 0 | 0.0220453344 | 1.23378496 | complete |
| kappa05 | 2 | zsre | 0.88 | 1 | 3 | 8.56391104e-05 | 0.000167349399 | complete |
| kappa05 | 2 | counterfact | 0.69 | 1 | 0 | 0.183982922 | 6.45543346 | complete |
| kappa05 | 2 | mquake | 0.52 | 1 | 0 | 0.0888275945 | 3.77851409 | complete |
| clip2 | 0 | zsre | 0.92 | 1 | 3 | 8.56391104e-05 | 0.000167349399 | complete |
| clip2 | 0 | counterfact | 0.78 | 0.98 | 1 | 0.260649332 | 6.42988206 | complete |
| clip2 | 0 | mquake | 0.71 | 1 | 0 | 0.0359984269 | 5.04782017 | complete |
| clip2 | 1 | zsre | 0.94 | 1 | 8 | 8.56391104e-05 | 0.000167349399 | complete |
| clip2 | 1 | counterfact | 0.78 | 1 | 0 | 0.358228228 | 6.56086681 | complete |
| clip2 | 1 | mquake | 0.79 | 1 | 0 | 0.0787036211 | 6.93880304 | complete |
| clip2 | 2 | zsre | 0.89 | 1 | 3 | 8.56391104e-05 | 0.000167349399 | complete |
| clip2 | 2 | counterfact | 0.7 | 1 | 0 | 0.188715514 | 6.45543346 | complete |
| clip2 | 2 | mquake | 0.5 | 1 | 0 | 0.00683779539 | 1.1538076 | complete |

Equal dataset weights within seed, then equal weights across all three seeds; no missing-value averaging.

| Arm | RET-GS macro | ES95 seed macros | ES95 macro | Maximum seed macros | Maximum macro |
|---|---:|---|---:|---|---:|
| ordinary | 0.796111111 | 0.450433221, 0.0629618065, 0.155370232 | 0.222921753 | 6.96185085, 2.52254184, 6.30664826 | 5.26368032 |
| kappa02 | 0.754444444 | 0.0431188349, 0.146847777, 0.060939565 | 0.0836353922 | 2.10287433, 3.14839457, 2.85126749 | 2.70084546 |
| kappa05 | 0.747777778 | 0.0620028719, 0.03745967, 0.0909653852 | 0.0634759757 | 2.50278088, 1.89676677, 3.41137163 | 2.60363976 |
| clip2 | 0.778888889 | 0.0989111328, 0.145672496, 0.0652129828 | 0.103265537 | 3.82595653, 4.49994573, 2.53646947 | 3.62079058 |

## kappa02: unavailable

Retention floor: 0.776111111; passes: False.
Unseen non-increase by dataset: {"counterfact": {"candidate": 0.0, "nonincrease": null, "ordinary": null}, "mquake": {"candidate": 0.0, "nonincrease": null, "ordinary": null}, "zsre": {"candidate": 0.049999999999999996, "nonincrease": true, "ordinary": 0.11666666666666665}}.
Tail contrasts (signed candidate − ordinary): {"es95": {"seed_spread_threshold": 0.38747141495854265, "separated": false, "separated_decrease": false, "signed_difference": -0.13928636090905053}, "maximum": {"seed_spread_threshold": 4.439309019001485, "separated": false, "separated_decrease": false, "signed_difference": -2.5628348569174335}}.
Eligible for a robustness-improvement description: False. An increase can separate but is not an improvement.
- r1_50_stream_sel6_text_s2/counterfact: unavailable
- r1_50_stream_sel6_text_s2/mquake: unavailable
- counterfact: unseen_population incomplete or unequal
- mquake: unseen_population incomplete or unequal

## kappa05: unavailable

Retention floor: 0.776111111; passes: False.
Unseen non-increase by dataset: {"counterfact": {"candidate": 0.0, "nonincrease": null, "ordinary": null}, "mquake": {"candidate": 0.0, "nonincrease": null, "ordinary": null}, "zsre": {"candidate": 0.04, "nonincrease": true, "ordinary": 0.11666666666666665}}.
Tail contrasts (signed candidate − ordinary): {"es95": {"seed_spread_threshold": 0.38747141495854265, "separated": false, "separated_decrease": false, "signed_difference": -0.15944577744018976}, "maximum": {"seed_spread_threshold": 4.439309019001485, "separated": false, "separated_decrease": false, "signed_difference": -2.660040557869831}}.
Eligible for a robustness-improvement description: False. An increase can separate but is not an improvement.
- r1_50_stream_sel6_text_s2/counterfact: unavailable
- r1_50_stream_sel6_text_s2/mquake: unavailable
- counterfact: unseen_population incomplete or unequal
- mquake: unseen_population incomplete or unequal

## clip2: unavailable

Retention floor: 0.776111111; passes: True.
Unseen non-increase by dataset: {"counterfact": {"candidate": 0.0033333333333333335, "nonincrease": null, "ordinary": null}, "mquake": {"candidate": 0.0, "nonincrease": null, "ordinary": null}, "zsre": {"candidate": 0.04666666666666667, "nonincrease": true, "ordinary": 0.11666666666666665}}.
Tail contrasts (signed candidate − ordinary): {"es95": {"seed_spread_threshold": 0.38747141495854265, "separated": false, "separated_decrease": false, "signed_difference": -0.11965621589492835}, "maximum": {"seed_spread_threshold": 4.439309019001485, "separated": false, "separated_decrease": false, "signed_difference": -1.6428897424808149}}.
Eligible for a robustness-improvement description: False. An increase can separate but is not an improvement.
- r1_50_stream_sel6_text_s2/counterfact: unavailable
- r1_50_stream_sel6_text_s2/mquake: unavailable
- counterfact: unseen_population incomplete or unequal
- mquake: unseen_population incomplete or unequal

## Clipped control

clip2 ceiling-matches kappa05 only. kappa02 is a secondary unmatched dose. Ceiling-matching both requires clip5 and 15 total trainings, a separate scope/budget amendment.
κ0.5 minus clip2, descriptive: {"es95": -0.03978956154526141, "ls_complete_answer": 0.0022222222222222365, "maximum": -1.0171508153890163, "ret_gs": -0.03111111111111109, "unseen_rate": -0.0033333333333333322}

## Missingness, failures and provenance

Legacy tail files contain no explicit token IDs: fixed 32x127 positions from the manifest-bound producer and identical ordered cap-off NLLs are compared. This is reconstructed population identity, not a historical embedded token-hash receipt.
Legacy LS is printed as recorded; it is not silently converted to the DEC-053 driver convention.
Charged failures: 0; receipts and costs are retained in JSON.
Input paths and SHA-256 values are in the companion JSON. Raw owner files were never modified.

- r1_50_stream_sel6_text_s2/counterfact: unseen: FileNotFoundError: [Errno 2] No such file or directory: '/home/derp/cap/pc_cap/results/R1/endpoints/r1_50_stream_sel6_text_s2_stepavg_rare1_n100_unseen_counterfact/summary.json'
- r1_50_stream_sel6_text_s2/mquake: unseen: FileNotFoundError: [Errno 2] No such file or directory: '/home/derp/cap/pc_cap/results/R1/endpoints/r1_50_stream_sel6_text_s2_stepavg_rare1_n100_unseen_mquake/summary.json'
