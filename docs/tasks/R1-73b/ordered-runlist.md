# R1-73b MQuAKE development comparator run list

MQuAKE v0-style conditions use the declared radius-zero exact-key (exact-prompt) fallback on all three banks; no paraphrase radius was admitted. Exact-prompt presentation is not a guarantee of acquisition or retention; RET-GS still scores every planned paraphrase.

Owner GPU execution only; acquire the lease and retain every failure cost.
300 attempts: 100 v3b development plus 200 exposed training fillers. This is not the DEC-056 unseen-population diagnostic.
Near-miss/revision shortfalls are explicit; zero-row phases cannot price the final inventories.

| Order | Condition | Integrity | Drift |
|---:|---|---|---|
| 1 | R1_nonlearned | incremental | profile_default |
| 2 | v0_stable | full | v0_batched_v1 |
| 3 | matched_update | full | v0_batched_v1 |
| 4 | v0_live_C1 | full | v0_batched_v1 |
| 5 | v0_live_C2 | full | v0_batched_v1 |
| 6 | S1_LM | full | v0_batched_v1 |
| 7 | S1_literal | full | v0_batched_v1 |
| 8 | R1_learned_ff_v2 | incremental | profile_default |

R1_nonlearned — inspect; append `--execute` only for owner execution:

```bash
../venv/bin/python -m scripts.r1_73b_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73b/R1-73b-mquake-R1_nonlearned.recipe.json --manifest-sha256 86ea65fca6c5cf8ed2cd9c06a30fcabd54d61773a8b42d3a2343bceade934d94
```

v0_stable — inspect; append `--execute` only for owner execution:

```bash
../venv/bin/python -m scripts.r1_73b_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73b/R1-73b-mquake-v0_stable.recipe.json --manifest-sha256 42b440bf74dcac67c62cd03129b8d631e6770276f26282478eecc1d662ea75d8
```

matched_update — inspect; append `--execute` only for owner execution:

```bash
../venv/bin/python -m scripts.r1_73b_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73b/R1-73b-mquake-matched_update.recipe.json --manifest-sha256 5410c7e99390347ed3da7544e9f814aa9238948efdcc2e1b69615875d90417e1
```

v0_live_C1 — inspect; append `--execute` only for owner execution:

```bash
../venv/bin/python -m scripts.r1_73b_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73b/R1-73b-mquake-v0_live_C1.recipe.json --manifest-sha256 90dea80e3a2d77a1a84126f48e374208ee92fa98481f19ba6b16eaea9800dd71
```

v0_live_C2 — inspect; append `--execute` only for owner execution:

```bash
../venv/bin/python -m scripts.r1_73b_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73b/R1-73b-mquake-v0_live_C2.recipe.json --manifest-sha256 a86bdd6b243cd9ebb238fd556ae9715b64461d407804626c9e4b86913903fe2d
```

S1_LM — inspect; append `--execute` only for owner execution:

```bash
../venv/bin/python -m scripts.r1_73b_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73b/R1-73b-mquake-S1_LM.recipe.json --manifest-sha256 69cb1739acc6c46bf930ba27dc5fbb082318c87c31c3c777fb3bd3b5a4cff7b1
```

S1_literal — inspect; append `--execute` only for owner execution:

```bash
../venv/bin/python -m scripts.r1_73b_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73b/R1-73b-mquake-S1_literal.recipe.json --manifest-sha256 05231c6c48ea5e6fa6e50f3d8cfc0373061b0ac0a2c16ed0793d4d3be46f62c4
```

R1_learned_ff_v2 — inspect; append `--execute` only for owner execution:

```bash
../venv/bin/python -m scripts.r1_73b_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73b/R1-73b-mquake-R1_learned_ff_v2.recipe.json --manifest-sha256 361142ef427626358a1856d6afd29fb845da060a0dcf620f345ce5eedfa4c623
```
