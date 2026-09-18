# R1-64f — owner run list

Four exposed-development cells; 300 edits, checkpoints 100/300, near100/revision50.
Inspect on CPU with the commands below; owner execution adds --execute in a CUDA/JAX environment with the GPU lease.
Keep /usr/bin/time -v or equivalent process RSS/envelope telemetry; JAX device peak alone does not measure host RSS.
128-window drift is a development assay, not the full validation split. Never resume another recipe identity.

## zsre / R1_learned_ff

```bash
../venv/bin/python -m scripts.r1_68c_dev_cell --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64f/R1-64f-zsre-R1_learned_ff.recipe.json --manifest-sha256 5be1b5001397174b2174cbfc0163165fb0c97c51326561d6f0da7001756121ac
```

## zsre / v0_stable

```bash
../venv/bin/python -m scripts.r1_68c_dev_cell --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64f/R1-64f-zsre-v0_stable.recipe.json --manifest-sha256 de5e8754e033c4ed61f0ce7f0a914380ab4a58efc234958db8ccc13d82427e01
```

## mquake / R1_learned_ff

```bash
../venv/bin/python -m scripts.r1_68c_dev_cell --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64f/R1-64f-mquake-R1_learned_ff.recipe.json --manifest-sha256 461b2c9e259dc6d3f80379db902014ab6d16c3ec5c8375973fb9bfe391a73895
```

## mquake / v0_stable

```bash
../venv/bin/python -m scripts.r1_68c_dev_cell --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64f/R1-64f-mquake-v0_stable.recipe.json --manifest-sha256 ceec274bc6da50d0c7fc0b159f022e0b56fc99944e5dac74a44f0a00f282ca58
```
