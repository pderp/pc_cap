# R1-64g — full-validation cost measurements

Four new development identities. Keep the R1-64f payloads, weights and challenge sets.
Sample at 100 and 300 edits; full validation only at 300. Never resume an older identity.
Inspect on CPU below. The orchestrator adds --execute under the GPU lease.
Wrap each execution in /usr/bin/time -v with a separate .time log; retain the memory monitor.
Read full_validation:300 outer phase wall and NPZ-bound endpoint metadata for cost v4.

mquake / R1_learned_ff

```bash
../venv/bin/python -m scripts.r1_68c_dev_cell --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64g/R1-64g-mquake-R1_learned_ff.recipe.json --manifest-sha256 5725a90c071fc5b6d91570ab5a78ecd2c65cefc4bd3cc9ef13894fac92b1fb41
```

mquake / v0_stable

```bash
../venv/bin/python -m scripts.r1_68c_dev_cell --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64g/R1-64g-mquake-v0_stable.recipe.json --manifest-sha256 296730e0dda98ef7ed84a185ed7259dc21cecad342da3143bbba888443b47d52
```

zsre / R1_learned_ff

```bash
../venv/bin/python -m scripts.r1_68c_dev_cell --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64g/R1-64g-zsre-R1_learned_ff.recipe.json --manifest-sha256 4b29cd82cd685e8f674abb5c5540c5273e96c1da7a9fae95b0eecfabe42db39d
```

zsre / v0_stable

```bash
../venv/bin/python -m scripts.r1_68c_dev_cell --manifest /home/derp/cap/pc_cap/docs/tasks/R1-64g/R1-64g-zsre-v0_stable.recipe.json --manifest-sha256 74ad788629b880d3296a5de87732c85898b9828eee5471b5e192f00487eba5e7
```
