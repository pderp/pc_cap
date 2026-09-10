"""Determinism configuration is verified at runtime, not only applied at import (derp_review2 #8)."""

import os
import subprocess
import sys

import pccap


def test_assert_determinism_passes_in_process():
    rep = pccap.assert_determinism()
    assert rep["jax_default_matmul_precision"] == "highest"


def test_import_after_backend_initialization_is_refused():
    code = ("import jax, jax.numpy as jnp; jnp.zeros(1).block_until_ready()\n"
            "try:\n    import pccap\nexcept RuntimeError as e:\n    print('REFUSED', e)\nelse:\n    print('ACCEPTED')")
    env = dict(os.environ, JAX_PLATFORMS="cpu", XLA_FLAGS="")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, timeout=120).stdout
    assert "REFUSED" in out, out


def test_tampered_precision_is_detected():
    import jax
    import pytest

    jax.config.update("jax_default_matmul_precision", "default")
    try:
        with pytest.raises(RuntimeError):
            pccap.assert_determinism()
    finally:
        jax.config.update("jax_default_matmul_precision", "highest")
