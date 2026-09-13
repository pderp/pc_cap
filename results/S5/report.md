# S5 report — controlled substrate comparison (S5-04)

Written 2026-09-13 ≈ 04:10 EDT by the orchestrator from `results/S5/paired_{zsre,counterfact}.json`, the S5 run records
(`results/S5/frozen-confirmatory-v2-84126123/`), the reused S4 C1 runs (SB) and `results/S5/projection.json`. Policy and
margins as frozen (DEC-009, `frozen-confirmatory-v2`). No independent-replicate language: the three realizations are three
sealed data draws with five committed orders each, and the substrate arms ran on exactly the same items and orders as SB.

## 1. Eligibility

The matched-fidelity comparison is eligible (S1-01, REG-03): the regenerated ePC checkpoint's mean teacher–student KL on H
is 2.9e-5 nats per token (rule ≤ 1e-3), with the ePC rows of P2/P3/P5/P6 equal to the BP rows to three decimals. The ePC
radius calibration by the S2-01 procedure is identical to BP's to the calibration grid's resolution (S5-01).

## 2. Arms and what changes between them

| arm | base | credit at the write sites | changes vs the previous arm |
| --- | --- | --- | --- |
| SB | BP teacher | adjoint | — (the S4 C1 runs, reused; identical frozen fields) |
| SE-A | regenerated ePC | adjoint | base only |
| SE-E | regenerated ePC | settled error, 8 iterations (SD-6, "finite-iteration error credit", P6) | credit rule only |

Common: router C1 (the fixed three-site schedule: writes at all three banks every round; the results overview's documentation correction), read R-h, per-base radii and scales from the frozen calibration, A = 0.3, byte ceiling B_cap,
the same 3 × 5 streams at the frozen scope (zsRE 1000, CounterFact 300).

## 3. Paired outcomes (Δ = first arm − second; 97.5% paired-cluster bootstrap over realizations, orders kept together)

| dataset | contrast | Δ RET-GS | interval | Δ ES | Δ LS | policy classification |
| --- | --- | ---: | --- | ---: | ---: | --- |
| zsRE | SE-A − SB | −0.002 | [−0.004, −0.000] | +0.000 | −0.021 [−0.041, +0.004] | negative (no practical gain) |
| zsRE | SE-E − SE-A | +0.019 | [+0.012, +0.025] | −0.336 [−0.344, −0.324] | +0.019 [−0.003, +0.032] | negative (below the 0.02 margin; ES non-inferiority fails) |
| CounterFact | SE-A − SB | 0.000 | [0, 0] | 0.000 | 0.000 | negative (exact-key floor) |
| CounterFact | SE-E − SE-A | 0.000 | [0, 0] | 0.000 | 0.000 | negative (exact-key floor) |

Per-arm means over the 15 zsRE runs: SB ES 0.998 / RET-ES 0.524 / RET-GS 0.139 / LS 0.985; SE-A 0.999 / 0.522 / 0.137 / 0.963;
SE-E 0.662 / 0.366 / 0.156 / 0.983. On CounterFact all three arms: ES 1.000, RET-ES 1.000, RET-GS 0.000, LS 1.000.

## 4. Readings

1. **Base conversion is neutral under a common credit rule.** SE-A reproduces SB on every measure to within 0.002 on the
   primary endpoint and within noise on acquisition; the small locality difference (−0.021, interval spanning zero) is not
   distinguishable from order-to-order variation. This is the matched-fidelity result the regeneration (DEC-014/015,
   12.3 GPU-h) was meant to enable: the ePC substrate is not a worse host for the cap.
2. **The credit rule trades acquisition for retention.** With the eight-iteration settled-error credit, a third of the
   edits do not reach the acquisition threshold within the frozen round budget (ES 0.66 vs 1.00), while the edits it
   does hold retain paraphrase generalization about two points better (RET-GS +0.019, interval excluding zero) and
   locality is at least as good. The retention gain is real but below the pre-registered practical margin, and the
   acquisition loss fails non-inferiority, so the contrast is negative by policy; scientifically it is a trade-off,
   consistent with P6's finding that eight iterations give a finite-iteration credit rather than a settled one.
3. **CounterFact is uninformative** for all substrate contrasts (exact keys; SD-18/SD-20 floor), as for the BP arms.

## 5. Cost frontier

| arm | zsRE accel s / run | CounterFact accel s / run | ratio to SB |
| --- | ---: | ---: | ---: |
| SB (= C1) | 503 | 259 | 1.00 |
| SE-A | 499 | 260 | 0.99 |
| SE-E | 1,046 | 328 | 2.08 (zsRE), 1.27 (CounterFact) |

S5 used 8.89 accelerator hours of the 18.0 available after headroom; the SE-E factor on zsRE (2.1×) exceeded the smoke
estimate (1.36×) because the error solver's cost scales with the number of rounds the harder edits consume.

## 6. Limits

The comparison establishes equivalence of the converted base under the adjoint credit and a retention/acquisition
trade-off for the error credit at one round budget; it does not establish superiority of either substrate. Optional S5-03
repeats and read variants were not run (D3 budget kept for S7/S8). S6 was closed for the month (DEC-022).
