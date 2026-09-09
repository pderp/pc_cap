# Environment (ENV-01, measured 2026-09-09)

Lead directive DEC-001: the project environment is the pre-existing JAX venv. No PyTorch.

| Item | Value |
| --- | --- |
| Host | Linux 7.1.12-200.fc44.x86_64 (Fedora 44) |
| CPU | AMD Ryzen 7 9700F, 8 cores / 16 threads |
| RAM | 30 GiB (≈22 GiB available at inspection) |
| Disk | 869 GiB free on `/home` |
| GPU | NVIDIA GeForce RTX 5070, 12,227 MiB, compute capability 12.0 (Blackwell, `sm_120`) |
| Driver | 610.57.04 (open kernel module) |
| CUDA runtime seen by JAX | 13.4 (`jax-cuda13-plugin 0.11.1`, `nvidia-cuda-runtime 13.4.49`), cuDNN 9.25.1 |
| GPU memory in use by desktop processes | ≈2.25 GiB (`kwin_wayland` 70 MiB, Chrome GPU process 244 MiB, `swipl` 1,526 MiB) — see the throughput caveat in plan §11 |
| Python | 3.12.14 at `/home/derp/cap/venv/bin/python` |
| JAX | `jax 0.11.1`, `jaxlib 0.11.1`, backend `gpu`, device `CudaDevice(id=0)` |
| FabricPC | `fabricpc 0.5.2` (installed copy byte-identical to `/home/derp/cap/FabricPC` at `6b946820…`, MIT) |
| Other | `optax 0.2.8`, `orbax-checkpoint 0.12.4`, `numpy 2.5.3`, `scipy 1.18.1`, `tokenizers 0.23.2`, `huggingface_hub 1.30.0`, `safetensors 0.8.0`, `pyarrow 25.0.1`, `pandas 3.0.5` |
| Added at ENV-01 | `pytest 9.1.1`, `ruff 0.16.6`, `safetensors 0.8.0`, `jsonschema`, `conllu`, `hypothesis` |
| Lock | `requirements.lock` = `pip freeze` of the venv (151 lines), SHA-256 prefix `b8bc3a542813e294` |
| `uv` | present at `~/.local/bin/uv` (used only for the auxiliary CPU environments under `assets/envs/`) |
| `pdftotext` | `/usr/bin/pdftotext` (produced `docs/pdf_text/plan.txt`, 1,801 lines, from the PDF with SHA-256 `9a2b6468…3359080`) |

## Determinism flags (plan §4.5 rule 7, translated to JAX; DEC-007)

Applied by `import pccap` before the XLA backend initializes:

```
XLA_FLAGS=--xla_gpu_deterministic_ops=true --xla_gpu_autotune_level=0
OMP_NUM_THREADS=16
TF_CUDNN_DETERMINISTIC=1
XLA_PYTHON_CLIENT_PREALLOCATE=false
jax_default_matmul_precision = highest      # TF32 off
jax_enable_x64 = False
jax_threefry_partitionable = False
```

Measurement motivating `highest`: on a 1024×1024 fp32 product the JAX default precision on
this GPU (TF32) differs from a float64 reference by max 5.1e-2; `highest` differs by 9.3e-5.

Dropout: the GPT-2 wrapper has no dropout path at all (weights only). Seeds come from manifests
via `jax.random.PRNGKey`.

## Determinism probe (ENV-01 Done-when)

`python -m pccap.harness.determinism_probe` (100 GPT-2-shaped 768×768 matmuls with GELU and
residual on a 128-token block, a 768→3072 projection and a softmax) run twice:

| run | SHA-256 of the result bytes |
| --- | --- |
| 1 | `ce30cc0e6897ebf8148906d05d12ebdb3c4f6fb9f1ce965a95b51e427015845c` |
| 2 | `ce30cc0e6897ebf8148906d05d12ebdb3c4f6fb9f1ce965a95b51e427015845c` |

Identical. Records: `results/ENV/determinism_probe.{1,2}.json`.

## Sibling fast tests (plan ENV-01 step)

Not run: the sibling requires `torch`, which is absent by DEC-001, and the sibling is read-only
reference material (DEC-003). Recorded as `unsupported` in `results/ENV/sibling_tests.txt`.

## Verify command

```
/home/derp/cap/venv/bin/python -c "import pccap, jax, jax.numpy as jnp; \
  assert jax.default_backend()=='gpu'; d=jax.devices()[0]; assert d.compute_capability=='12.0'; \
  x=jax.random.normal(jax.random.PRNGKey(0),(1024,1024)); print(float((x@x).sum()))"
```
