# HT-3b review-script cleanup request

The new review script needs two mechanical fixes: import pccap before JAX as required by CONTRIBUTING.md, and bind the immediately evaluated lambda variables explicitly to pass Ruff B023. Numerical probes pass unchanged in memory. No trainer changes. This file records the proposed edit; it has not been applied.

```diff
--- a/scripts/ht3b_objective_review.py
+++ b/scripts/ht3b_objective_review.py
@@ -10,6 +10,7 @@
 import jax.numpy as jnp
 import numpy as np
 
+import pccap  # noqa: F401 -- set determinism flags before JAX
 from pccap.revision_v1.train import LossConfig, coupled_divergence, coupled_surprisal
 
 ROOT = Path(__file__).resolve().parents[1]
@@ -26,7 +27,9 @@
             assert np.isfinite(value) and value >= -1e-6
             divergences.append(value)
             match, grad = jax.value_and_grad(
-                lambda logits: coupled_divergence(lp, jax.nn.log_softmax(logits), kappa)
+                lambda logits, lp=lp, kappa=kappa: coupled_divergence(
+                    lp, jax.nn.log_softmax(logits), kappa
+                )
             )(lp)
             assert abs(float(match)) < 1e-6
             norm = float(jnp.linalg.norm(grad))
```
