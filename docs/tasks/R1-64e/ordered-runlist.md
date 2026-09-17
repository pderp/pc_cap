# Post-R1-77d development recipes

CPU inspection below. Owner-only execution adds `--execute` with the lease.
New attempt identities; do not resume historical attempts.

zsre / R1_nonlearned

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-zsre-R1_nonlearned.recipe.json --manifest-sha256 ec8902c24a956d0ede0fb7ba37818f537b433f4b9aac57f08d57dbe614f115b8
```

zsre / v0_stable

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-zsre-v0_stable.recipe.json --manifest-sha256 283f7cdd1aa15b8260b50ed73a590d12558cab549fd88f4bddcb82fe8f2e13df
```

zsre / matched_update

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-zsre-matched_update.recipe.json --manifest-sha256 17e972d9a7e5f3f79d2137299e7888d3be8c594aadab7b5db4840386a9d5a5a2
```

zsre / v0_live_C1

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-zsre-v0_live_C1.recipe.json --manifest-sha256 8e242e576784f88f599255340552ed833a0f5394d7bff71cfaf58bcd240c443b
```

zsre / v0_live_C2

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-zsre-v0_live_C2.recipe.json --manifest-sha256 6aac8f2a7db5e227f76373242881e707c9a19b389fd20ccd23356b130fa45d68
```

zsre / S1_LM

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-zsre-S1_LM.recipe.json --manifest-sha256 3729ca8b336a81b7c2823d98311cc19c1b8e9b330fb93f6ae676c40f826e011f
```

zsre / S1_literal

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-zsre-S1_literal.recipe.json --manifest-sha256 08150f20f5d2f7584cae00eaa8df0dfd2c5b4822d5b49253f901258cf98ffcd3
```

zsre / R1_learned_ff_v2

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-zsre-R1_learned_ff_v2.recipe.json --manifest-sha256 e282255f66c8955a7acc909d5b0105a48e7507ccda954f8cfc2cd8fc789d380f
```

counterfact / R1_nonlearned

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-counterfact-R1_nonlearned.recipe.json --manifest-sha256 7a81b5e00267e240994bca9aee1d8cdf65639468bd13db88a92aa632459e0246
```

counterfact / v0_stable

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-counterfact-v0_stable.recipe.json --manifest-sha256 96e7678c6b43d22d52a2f56d58a03cecade022b7863ba690b23769c5c0308399
```

counterfact / matched_update

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-counterfact-matched_update.recipe.json --manifest-sha256 75792e906242246da06dc61cba776c6e74132f1bae8cff8a23e8261057680601
```

counterfact / v0_live_C1

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-counterfact-v0_live_C1.recipe.json --manifest-sha256 12a4d7a9d7490733ea28b92c2e4539a677d3861af714669b5596a5370bcec1df
```

counterfact / v0_live_C2

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-counterfact-v0_live_C2.recipe.json --manifest-sha256 c934a0b24c399a432f315cebaac99768d40d7275915becb094cd9d920d6515da
```

counterfact / S1_LM

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-counterfact-S1_LM.recipe.json --manifest-sha256 8be717ebc59d80e93f3ea93ea486eba9dc2e80bdd586619404c449eba4dedf7a
```

counterfact / S1_literal

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-counterfact-S1_literal.recipe.json --manifest-sha256 9309a9c3184a06c8ad3585e9efaa2d8025861bab3c07f9514c4e0060280ea3c6
```

counterfact / R1_learned_ff_v2

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-counterfact-R1_learned_ff_v2.recipe.json --manifest-sha256 0a5eea6dbd20142f1e903ef5b8551d9cb40d181337b0bcd9f35e72760540f99e
```

zsre / R1_learned_ff

```bash
../venv/bin/python -m scripts.r1_68c_dev_cell --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64e/R1-64e-zsre-primary-v5.recipe.json --manifest-sha256 96b814492e8229f10c15478cc6eb52d86b6a24a617a6e2e17fe674f81ade74c9
```
