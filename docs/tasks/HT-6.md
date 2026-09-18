# HT-6 — full-validation fidelity and tail report

- Status: report generator and CPU checks complete; final four-cell report pending chain S. Latest saved output is an explicitly partial **2/4 preview** (round 33, below).
- Agent: Codex, rounds 32–33.
- Inputs: the four R1-64g recipes, completed immutable checkpoint/result/vector/GNU-time evidence, DEC-063 populations, DEC-054 framing and R1-49l's separate scope audit.
- Outputs: `scripts/ht6_full_validation_report.py`, `scripts/ht6_plot.py`, `tests/revision_v1/test_ht6_full_validation_report.py`, `logs/r1_round32/ht6-partial-preview-v2/{report.json,report.md,curve-series.json,tail-survival.png,tail-survival.pdf,plot-environment.json}`.

The generator independently audits completed measurements via R1-58l/R1-63l, then reports both references and both populations: signed mean NLL change and KL, positive-harm ES95/ES99/max, strict .01/.1/1-nat exceedances, coverage, overlap and phase costs. JSON also retains zero mass, negative changes, positive-harm concentration, locations, sample-minus-full differences and complement means. Completed cost evidence is not automatically cost admission or a scientific classifier verdict.

**Sample provenance matters.** Historical sampled drift saved three NLLs per position, not KL. Sample NLL uses those independently saved rows. The 128-window sample's KL is the corresponding slice of the full-vector KL array, explicitly labelled as derived; it is not an independently repeated sampled KL measurement. Loss agreement and matching exceedance counts verify common-position numerical consistency. The ordered first 128 windows are not an iid random sample, and agreement on common positions does not imply equal means/tails over different populations.

## First-cell preview

For learned-reader MQuAKE at checkpoint 300, original and own-cap-off references coincide:

| Quantity | Full: 245,237 positions | Fixed prefix: 16,256 positions |
|---|---:|---:|
| Mean signed NLL increase | .0056009764 | .0075309430 |
| Mean KL(reference || cap) | .0055436876 | .0076691941 (derived prefix) |
| ES95 positive NLL harm | .1144675627 | 0.1531302307 |
| ES99 positive NLL harm | .5723378136 | 0.7656511536 |
| Maximum positive NLL harm | 8.1875503498 | 5.6402928312 |
| NLL increase > .01 / .1 / 1 nat | 817 / 768 / 485 | 88 / 82 / 44 |

The full population has 244,333 exact zero loss changes, 84 negative changes and 820 positive changes. All positive loss harm falls within the empirical worst 1% because fewer than 1% of positions have positive harm. This describes a concentration in this fixed development result; it does not establish a power law, a tail exponent, iid uncertainty, or a κ treatment effect. The whole-population maximum exceeds the prefix maximum even though the prefix mean is higher. Full/sample overlapping losses agree within 1.4211e-14 nats and all three loss-exceedance counts match.

Full outer phase 1,298.987703 s; inner full assay 1,298.958067 s; both sampled phases combined 138.931263 s. Full coverage uses 1,931 complete 128-token windows, context resets, and 121 trailing tokens dropped. The report keeps the D.2 numerical fidelity flags as recorded implementation output and explicitly leaves their cap-admission meaning to R1-49l/Q17.

## Reproduce and complete

From `pc_cap`, after all four completed measurements are available:

```sh
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.ht6_full_validation_report --output logs/r1_round32/ht6-final
```

The command refuses incomplete evidence by default and refuses overwriting an existing output directory. For a disclosed preview only, add `--allow-partial` and choose a new output directory. Recheck chain-S completion and source identities before calling a report final. All pending/invalid cells remain visible.

Numerical analysis stays in the project venv. Rendering runs the existing `assets/envs/status-paper-20260911` environment as a separate process that reads precomputed curves and imports no JAX. Matplotlib's cache is under assets; no environment or dependency was installed. The initial preview attempt found matplotlib absent from the JAX venv; its JSON/Markdown remain as an incomplete historical attempt, superseded by `ht6-partial-preview-v2`.

- Verify command: `PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m pytest -q tests/revision_v1/test_ht6_full_validation_report.py`.
- Verify output: **8 passed**; **13 passed** combined with R1-49l (`logs/r1_round32/final-tests.txt`); Ruff passes. PNG inspected visually; PDF rendered. CCDF tests cover strict inequality, ties, the zero atom and the step direction. Sample tests reject missing/reordered/nonfinite/mismatched rows and exceedance mismatches within the loss tolerance. A final report refuses partial input.
- Done-when: all four audited cell reports, full/sample comparison, costs and qualified talk reading exist. Final four-cell completion not reached.
- Cost: CPU only, GPU seconds 0, model calls 0.
- Deviations: prepared the report pipeline and one-cell preview while the three remaining owner runs continue. No missing outcomes were inferred.
- Unresolved: completion of chain S. Q17 is now resolved by DEC-064; cost admission and confirmatory classifier decisions are not performed by this lane.
- Questions for lead: none additional to the R1-49l handoff.

## Round 33 update — DEC-064 and HT-7

The latest preview is `logs/r1_round33/ht6-partial-preview-v2/`: both completed MQuAKE cells, both references, full and sampled results, benchmark labels, full HT-7 concentration, sampled/full overlap, PNG/PDF and the plotting-environment record. All four donors remain mandatory for the default final report. The learned-reader cell fails the KL benchmark and passes NLL; v0 has zero observed loss/KL changes and passes both. Under DEC-064 these labels do not veto primary comparisons; development status remains unchanged.

The plot now explicitly labels the all-zero survival case instead of leaving an apparently empty logarithmic panel. Its step direction remains the tested strict empirical survival definition. Visual inspection and the 79-test round-33 regression passed. The earlier round-33 preview remains an intermediate artifact; **v2** is the reviewed preview.

After the other two profiles finish, build with no `--allow-partial`, inspect the four-cell report and figure, and copy the final figure plus a two-sentence qualified result to `assets/presentation-materials/`. That final export has not yet happened. See `HT-7.md` and `R1-round33-handoff.md`.
