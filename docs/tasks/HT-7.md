# HT-7 — declared descriptive fidelity concentration

- Status: implemented and verified; final four-cell presentation report remains HT-6's dependency.
- Agent: Codex, round 33, September 18, 2026.
- Inputs: HT-7 specification in `docs/R1_stage2_notes.md`, `docs/lead_queue.md` item 77 and `assets/presentation-materials/fidelity_concentration_v5.md`; DEC-064; exact full-validation NPZ bindings.
- Outputs: `scripts/ht7_concentration.py`; D.3 definitions/policy binding; independent analysis hook; HT-6 integration; `tests/revision_v1/test_ht7_concentration.py`; `logs/r1_round33/ht6-partial-preview-v2/`.
- Verify command: CPU pytest command in the round-33 handoff; preview command below.
- Verify output: concentration tests pass within the **79-test** suite. Independently verified real vectors reproduce 171 positions carrying half the learned-reader MQuAKE KL, 1,612/1,931 windows within .001, and position Gini .998188. Both references coincide for these two completed original-base conditions.

The implementation reports near-zero target NLL change (<1e-6 absolute), integer minimum positions reaching half KL, position fractions and top .1%/1% KL shares, population Gini, per-window mean-KL benchmark/exceedance counts, median/p90/p99/max and top 1%/5%/10% window shares. Positive-NLL position concentration is also retained in JSON. Fractional top-mass boundaries include zero observations; all-zero shares, half-mass counts/fractions and Gini are null, not invented concentration. Equality passes the benchmark and does not pass strict exceedances.

Tests use direct pairwise Gini as an independent calculation, tied observations, fractional boundaries, zero harm, different references, negative signed NLL changes, invalid/nonfinite observations and changed vector bytes. Report text distinguishes nearly unchanged target-token loss from unchanged full predictions or a measured reader-firing mechanism. No power law, κ benefit, iid uncertainty or causal interpretation is inferred.

The two-cell preview has **both** full (245,237 positions) and fixed-prefix (16,256 positions) statistics. Prefix KL is explicitly sliced from the full vectors; saved sampled loss rows are independently checked. The completed v0 MQuAKE cell has all-zero loss/KL changes on this population; its zero-survival panel is labelled, with no artificial positive ordinate on the logarithmic axis. The two zsRE panels remain “Measurement pending.” The updated figure was visually inspected.

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m scripts.ht6_full_validation_report --allow-partial \
  --output logs/r1_round33/<new-preview-directory>
```

- Done-when: descriptive definitions, both-reference implementation, independent tests and report integration delivered. Reached.
- Cost: CPU reads only; GPU seconds 0; model calls 0; existing plotting environment reused.
- Deviations: clarified presentation shorthand “unchanged prediction” to “near-zero target-token loss change”; no measured value altered. Earlier rounded window shares need not exactly match the new explicit fractional-boundary definition.
- Unresolved: four completed cells are required for final HT-6 and its presentation export. No partial preview was published as final or copied over presentation material.
- Questions for lead: none.
