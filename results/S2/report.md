# S2 stage report (Appendix G) — development

Rendered 2026-09-09 23:28 UTC by `pccap report --stage S2`.

## 1. Header

- Stage: S2 calibration, baselines, throughput. Code commit: `983236b168ebac51d3abaae4e8f6a410d75cf95a`. Development pools: `manifests/dev/{zsre,counterfact}_dev.json` (300 edits + ≥ 1,000 unrelated prompts each; DATA-01).
- Cost: 0.00 local GPU-h = 0.00 A100-eq h of 12 (κ 1.0 provisional).

## 2. Status

Development. S2-01 and S2-02 complete where files exist; S2-03/04/05 (baselines) and S2-06/07 (throughput, D1) pending.

## 3. Controls

S0 controls unchanged. Every configuration tried is logged (Op. rule 3): A ∈ {0.03, 0.1, 0.3} only.

## 4. Coverage

**S2-01.** b_m (pooled medians): bank 1: 70.70, bank 2: 106.58, bank 3: 425.57.

| dataset | bank | radius | coverage | false-fire | note |
| --- | ---: | ---: | ---: | ---: | --- |
| zsre | 1 | 0.281 | 0.87 | 0.000 | largest admissible radius (false-fire <= 1%), ties by covera |
| zsre | 2 | 0.414 | 0.87 | 0.000 | largest admissible radius (false-fire <= 1%), ties by covera |
| zsre | 3 | 0.189 | 0.87 | 0.000 | largest admissible radius (false-fire <= 1%), ties by covera |
| counterfact | 1 | 0.000 | 0.00 | 0.000 | no positive radius meets the 1% false-fire criterion: exact- |
| counterfact | 2 | 0.000 | 0.00 | 0.000 | no positive radius meets the 1% false-fire criterion: exact- |
| counterfact | 3 | 0.000 | 0.00 | 0.000 | no positive radius meets the 1% false-fire criterion: exact- |

## 5. Results

## 6. Mechanism evidence

None at S2 (routing arms are screened in S3).

## 7. Optional mathematics

None.

## 8. Deviations

SD-17 radii per dataset; CounterFact exact-key pilot (CR-4); zsRE teacher answers are mostly empty (DATA-01 record).

## 9. Interpretation

Calibration and numerics only; no scientific claim. Immediate ES on zsRE is acquisition from an empty baseline answer.

## 10. Reproduction

```
python -m pccap.data.streams --build && python -m pccap.data.streams --audit
python -m pccap.cap.calibrate
python -m pccap.harness.stage_s2 --n 100
python -m pccap.cli report --stage S2
```
