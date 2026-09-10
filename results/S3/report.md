# S3 stage report (Appendix G) — development, BP mechanism screening

Rendered 2026-09-10 02:54 UTC by `pccap report --stage S3`.

## 1. Header

- Stage: S3. Code commit: `b77f4b6a1dc73d316257f36c7af888e102de5fbc`. Numerics: A = 0.3 (DEC-012), radii per dataset (SD-17), b_m (S2-01), ε 0.01, R 5, τ 0.1.
- Cost: 0.02 local GPU-h of 16 (fixture runs are CPU).

## 2. Status

Development. S3-01 controls (results/S3/controls.md) done except PC-10; S3-02 fixture runs done; S3-03 (grammar) pending GRAM-02; S3-04 (short editing checks) pending baselines; S3-05/06 pending.

## 3. Controls

See `results/S3/controls.md` (17 pass, PC-10 pending).

## 4. Coverage

MODULAR-CONTROL: 60 items per kind (private/shared/mixed) + held-out combinations, arms C0/C1/C2/CR/CO, variants useful-sharing / no-sharing / wrong-router. Unrelated outputs unchanged (max |Δp| = 0) in every run.

## 5. Results

| variant | arm | recovery | precision [95% CI] | recall | majority-bank | multi-cause coverage | abstained |
| --- | --- | ---: | --- | ---: | ---: | --- | ---: |
| useful_sharing | C0 | 0.26 | 0.22 [0.16, 0.29] | 0.22 | 0.67 | 0/20 | 0 |
| useful_sharing | C1 | 0.99 | 0.48 [0.46, 0.51] | 1.00 | 0.67 | 20/20 | 0 |
| useful_sharing | C2 | 1.00 | 0.88 [0.83, 0.93] | 0.89 | 0.67 | 0/20 | 0 |
| useful_sharing | CR | 0.94 | 0.55 [0.51, 0.59] | 0.88 | 0.67 | 4/20 | 0 |
| useful_sharing | CO | 1.00 | 1.00 [1.00, 1.00] | 1.00 | 0.67 | 20/20 | 0 |
| no_sharing | C0 | 0.24 | 0.33 [0.26, 0.42] | 0.33 | 0.33 | 0/0 | 0 |
| no_sharing | C1 | 0.63 | 0.33 [0.33, 0.33] | 1.00 | 0.33 | 0/0 | 0 |
| no_sharing | C2 | 0.66 | 0.98 [0.94, 1.00] | 1.00 | 0.33 | 0/0 | 0 |
| no_sharing | CR | 0.54 | 0.46 [0.42, 0.51] | 0.85 | 0.33 | 0/0 | 0 |
| no_sharing | CO | 0.66 | 1.00 [1.00, 1.00] | 1.00 | 0.33 | 0/0 | 60 |
| wrong_router | C0 | 0.26 | 0.22 [0.16, 0.29] | 0.22 | 0.67 | 0/20 | 0 |
| wrong_router | C1 | 0.99 | 0.48 [0.46, 0.51] | 1.00 | 0.67 | 20/20 | 0 |
| wrong_router | C2 | 1.00 | 0.88 [0.83, 0.93] | 0.89 | 0.67 | 0/20 | 0 |
| wrong_router | CR | 0.94 | 0.55 [0.51, 0.59] | 0.88 | 0.67 | 4/20 | 0 |
| wrong_router | CO | 0.56 | 0.31 [0.27, 0.34] | 0.44 | 0.67 | 0/20 | 0 |

C2 per-latent confusion (useful sharing; delivered bank counts): private-1: {'1': 20, '2': 1, '3': 1}; private-2: {'2': 20}; private-3: {'3': 20, '2': 2}; shared: {'1': 9, '2': 57}; mixed-1: {'1': 20}; mixed-2: {'2': 20}; mixed-3: {'2': 19, '1': 1}

## 6. Mechanism evidence

Oracle (CO) reaches every planted target with exact unrelated invariance; C2's measured routing agrees with R* at precision 0.88 / recall 0.89 (PR-C band ≥ 0.8, descriptive), above the random control (0.55) and the majority-bank baseline (0.67). C2 never abstains on the fixture. Under no sharing, shared items are unfixable by any arm (0/60) and C2 precision on private/mixed rises to 0.98. C2's systematic shortcut: bank-3 mixed items are fixed through the shared path (bank 2) rather than covering bank 3 (0/20 coverage vs C1 20/20).

## 7. Optional mathematics

None.

## 8. Deviations

Fixture budget A = 1.0 with exact keys (fixture manifest); held-out transfer pass pending; last-row logits path introduced 2026-09-10 (same arithmetic per row; identity controls re-verified).

## 9. Interpretation

The apparatus recovers an identifiable case (PC-1) and C2's measured intervention scores track the constructed causal structure on private latents; the shared-path shortcut is a scientific observation about intervention-based routing (a late/shared bank can fix a mixed target without touching the private mechanism), to be classified at D2, not an implementation failure.

## 10. Reproduction

```
JAX_PLATFORMS=cpu python -m pccap.harness.stage_s3_fixture --n 60
python -m pccap.cli report --stage S3-controls && python -m pccap.cli report --stage S3
```
