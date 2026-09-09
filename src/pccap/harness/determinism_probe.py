"""ENV-01 determinism probe: 100 GPT-2-shaped matmuls plus a softmax on the default device.

Two invocations must produce identical bytes (updated_plan2.md ENV-01 Done-when). Prints the
SHA-256 of the result bytes and writes it to ``results/ENV/determinism_probe.<n>.json`` when
``--out`` is given.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time

import pccap

_ = pccap.__version__  # pccap must be imported before jax initializes (determinism flags)

import jax  # noqa: E402
import jax.numpy as jnp  # noqa: E402
import numpy as np  # noqa: E402


def probe(n_matmuls: int = 100, tokens: int = 128, d: int = 768, seed: int = 0) -> np.ndarray:
    key = jax.random.PRNGKey(seed)
    k1, k2, k3 = jax.random.split(key, 3)
    x = jax.random.normal(k1, (tokens, d), dtype=jnp.float32)
    w = jax.random.normal(k2, (n_matmuls, d, d), dtype=jnp.float32) * (1.0 / np.sqrt(d))
    wv = jax.random.normal(k3, (d, 4 * d), dtype=jnp.float32) * (1.0 / np.sqrt(d))

    @jax.jit
    def run(x, w, wv):
        def body(h, wi):
            h = jax.nn.gelu(h @ wi, approximate=False) + h
            return h, None

        h, _ = jax.lax.scan(body, x, w)
        logits = h @ wv
        return jax.nn.softmax(logits, axis=-1), h

    p, h = run(x, w, wv)
    return np.concatenate([np.asarray(p).ravel(), np.asarray(h).ravel()])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    t0 = time.time()
    arr = probe()
    digest = hashlib.sha256(arr.tobytes()).hexdigest()
    rec = {
        "sha256": digest,
        "n_values": int(arr.size),
        "wall_seconds": time.time() - t0,
        "determinism": pccap.determinism_report(),
    }
    print(json.dumps(rec, indent=1))
    if args.out:
        with open(args.out, "w") as f:
            json.dump(rec, f, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
