"""pccap: continual-learning predictive-coding caps on GPT-2-scale transformers.

Importing this package applies the determinism settings of updated_plan2.md §4.5 rule 7,
translated to JAX (lead directive DEC-001: all GPU code is JAX):

* XLA deterministic ops (``--xla_gpu_deterministic_ops=true``) and no autotuning of GEMM
  algorithms, so repeated runs pick the same kernels;
* matmul precision ``highest`` (TF32 off: on Blackwell the JAX default for fp32 matmuls is
  TF32, measured error 5e-2 vs 9e-5 on a 1024x1024 product at ENV-01);
* float64 disabled (fp32 is the declared dtype; metrics that need f64 use NumPy);
* ``OMP_NUM_THREADS=16``;
* the ``threefry2x32`` PRNG implementation with partitionable RNG off (so streams are stable
  across shard layouts).

These must be set before the XLA backend initializes, so ``pccap`` has to be imported before
any ``jax`` computation runs. ``pccap.determinism_report()`` returns the effective settings.
"""

from __future__ import annotations

import os

_XLA_DETERMINISM = "--xla_gpu_deterministic_ops=true --xla_gpu_autotune_level=0"
_prev = os.environ.get("XLA_FLAGS", "")
if "xla_gpu_deterministic_ops" not in _prev:
    os.environ["XLA_FLAGS"] = (_prev + " " + _XLA_DETERMINISM).strip()
os.environ.setdefault("OMP_NUM_THREADS", "16")
os.environ.setdefault("TF_CUDNN_DETERMINISTIC", "1")
os.environ.setdefault("XLA_PYTHON_CLIENT_PREALLOCATE", "false")
os.environ.setdefault("HF_HOME", "/home/derp/cap/assets/hf_cache")

import sys as _sys  # noqa: E402

# Runtime guard (derp_review2 #8): the XLA flags above only take effect if no XLA backend exists yet.
# ``jax`` may already be imported (the flags are read at backend initialization, not at import), but an
# already-initialized backend cannot be reconfigured — refuse loudly instead of running non-deterministically.
if "jax" in _sys.modules:
    _jx = _sys.modules["jax"]
    try:
        _initialized = bool(getattr(_jx._src.xla_bridge, "_backends", {}))  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - private API drift
        _initialized = False
    if _initialized:
        raise RuntimeError("pccap must be imported before any JAX backend is initialized (determinism flags, DEC-007)")

import jax  # noqa: E402

jax.config.update("jax_default_matmul_precision", "highest")
jax.config.update("jax_enable_x64", False)
jax.config.update("jax_threefry_partitionable", False)


def assert_determinism() -> dict:
    """Verify at runtime that the determinism configuration is in force (call after the lease, before any
    GPU work): XLA deterministic-ops flag present, matmul precision ``highest``, x64 off. Returns the
    report; raises ``RuntimeError`` otherwise."""
    problems = []
    if "--xla_gpu_deterministic_ops=true" not in os.environ.get("XLA_FLAGS", ""):
        problems.append("XLA_FLAGS lacks --xla_gpu_deterministic_ops=true")
    if jax.config.jax_default_matmul_precision != "highest":
        problems.append(f"jax_default_matmul_precision = {jax.config.jax_default_matmul_precision!r}")
    if jax.config.jax_enable_x64:
        problems.append("jax_enable_x64 is on")
    if problems:
        raise RuntimeError("determinism configuration not in force: " + "; ".join(problems))
    return determinism_report()

__version__ = "0.0.1"

ASSETS_ROOT = os.environ.get("PCCAP_ASSETS", "/home/derp/cap/assets")


def determinism_report() -> dict:
    """Effective determinism settings, recorded into every run's config.json."""
    return {
        "xla_flags": os.environ.get("XLA_FLAGS", ""),
        "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
        "jax_default_matmul_precision": jax.config.jax_default_matmul_precision,
        "jax_enable_x64": jax.config.jax_enable_x64,
        "jax_threefry_partitionable": jax.config.jax_threefry_partitionable,
        "jax_version": jax.__version__,
        "backend": jax.default_backend(),
        "devices": [str(d) for d in jax.devices()],
    }
