# R1-73d — corrected MQuAKE development run list

First 50 distinct v3b unrelated source prompts excluding every prompt/paraphrase in the full 300-edit stream; exposed development/training data, not fresh confirmation.

Inspect on CPU first. Owner GPU execution adds `--execute` at the scheduled boundary, with the usual lease. These are new attempt identities; do not resume old Chain M results.

R1_nonlearned:

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d/R1-73d-mquake-R1_nonlearned.recipe.json --manifest-sha256 f82d7f2e297139db05ccd5ee6060a03b2fdf756b54bea5aa53980f895fbdbf73
```

v0_stable:

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d/R1-73d-mquake-v0_stable.recipe.json --manifest-sha256 d00f0c3a2b8d0c0b214b4cc7580f977e877f23e492793578ac22874f9265ff08
```

matched_update:

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d/R1-73d-mquake-matched_update.recipe.json --manifest-sha256 df8ed849e4e5613039b6b089da5791b0743d4e7c5661cbd7aa0a0ad3e01d62f3
```

v0_live_C1:

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d/R1-73d-mquake-v0_live_C1.recipe.json --manifest-sha256 a146d83eabd4aeb85dbddb4d948e6dc46fdeae7452c9717960fdacd8088a4503
```

v0_live_C2:

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d/R1-73d-mquake-v0_live_C2.recipe.json --manifest-sha256 359bfdb724128756dc33aef2f16be2255f26e8e0fd202aff0d61ee162d31f0a6
```

S1_LM:

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d/R1-73d-mquake-S1_LM.recipe.json --manifest-sha256 08c1f60a00683dc8cc4fc71cdfa574df325ac4896b5bee6cc94b5a67ee08aba8
```

S1_literal:

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d/R1-73d-mquake-S1_literal.recipe.json --manifest-sha256 426bb140d601e4a6a37a689220d7f900fe874ff3178d9279669e20afa46af715
```

R1_learned_ff_v2:

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d/R1-73d-mquake-R1_learned_ff_v2.recipe.json --manifest-sha256 cd89beee9efaa4442475a367cbbb2901ca8fe55acb74f4f702145165e02dc1c1
```
