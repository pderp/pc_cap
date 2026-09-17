# Post-R1-77d development recipes

CPU inspection below. Owner-only execution adds `--execute` with the lease.
New attempt identities; do not resume historical attempts.

mquake / R1_nonlearned

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d-post77d/R1-73d-mquake-R1_nonlearned.recipe.json --manifest-sha256 bcda6182cba9b4230d3c7925de62461b49c10a9d0026a3c26d4b7eaf90f5d961
```

mquake / v0_stable

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d-post77d/R1-73d-mquake-v0_stable.recipe.json --manifest-sha256 75078c3e3ab790817fc4fb8aeb9c329d29b6b4facdcf31b54c1b04227bc2c1c2
```

mquake / matched_update

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d-post77d/R1-73d-mquake-matched_update.recipe.json --manifest-sha256 4ce23ea28eb3578adc5e4a05075e8bb0c6af656d4574b11e7f61b639f5ed07a7
```

mquake / v0_live_C1

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d-post77d/R1-73d-mquake-v0_live_C1.recipe.json --manifest-sha256 18715d85448d106a2b5658f8b0f3799f171f621389e45fdd556a9b372c796221
```

mquake / v0_live_C2

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d-post77d/R1-73d-mquake-v0_live_C2.recipe.json --manifest-sha256 e1fe4143c668bc7e449b20841b7fefffe158c9b0afa3095c548aefdf409af383
```

mquake / S1_LM

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d-post77d/R1-73d-mquake-S1_LM.recipe.json --manifest-sha256 a2ac0bec446eecd721e6ad434a128c5e834f2622efe882bd73661dc04cb71591
```

mquake / S1_literal

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d-post77d/R1-73d-mquake-S1_literal.recipe.json --manifest-sha256 e6ae743f81b88f6a8de625434f98b934fdaa4773a8a12e0249bf9bdc222eb6fc
```

mquake / R1_learned_ff_v2

```bash
../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest /home/derp/cap/pc_cap/docs/tasks/R1-73d-post77d/R1-73d-mquake-R1_learned_ff_v2.recipe.json --manifest-sha256 cafcbc18924c10c12857dfa1301280747e628b1762878a42da66168dde38ab8a
```
