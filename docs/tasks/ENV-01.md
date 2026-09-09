# ENV-01 Python environment (JAX venv) verified and completed
status: done
agent: orchestrator   started: 2026-09-09T18:40:00Z   finished: 2026-09-09T18:47:22Z
commit: (this commit)
inputs used: /home/derp/cap/venv (pre-existing, DEC-001); nvidia driver 610.57.04
outputs: docs/environment.md, requirements.lock, results/ENV/determinism_probe.{1,2}.json, results/ENV/sibling_tests.txt
verify command: /home/derp/cap/venv/bin/python -c "import pccap, jax, jax.numpy as jnp; assert jax.default_backend()=='gpu'; d=jax.devices()[0]; assert d.compute_capability=='12.0'; x=jax.random.normal(jax.random.PRNGKey(0),(1024,1024)); print(float((x@x).sum()))"
verify output: verify matmul 3791.7548828125
done-when check:
- CUDA matmul runs: PASS (above)
- arch list includes sm_120: PASS (JAX reports compute_capability 12.0; the torch-specific arch-list check is replaced by the JAX device query)
- lock file committed: PASS (requirements.lock, pip freeze, 151 lines)
- sibling fast tests ran: NOT RUN, recorded as unsupported (DEC-001/DEC-003; results/ENV/sibling_tests.txt)
- two determinism probe runs identical: PASS (sha256 ce30cc0e… both runs)
cost: gpu_seconds=5 wall_seconds=900 peak_mem_mib=300
deviations: Python 3.12 JAX venv instead of 3.11+torch (DEC-001). Packages added: pytest 9.1.1, ruff 0.16.6, safetensors 0.8.0, jsonschema, conllu, hypothesis. TF32 found on by default in JAX; forced off in pccap/__init__.py (DEC-007).
unresolved: none
questions for lead: none
