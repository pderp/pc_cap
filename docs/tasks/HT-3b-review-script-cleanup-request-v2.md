# HT-3b review-script cleanup request (v2)

Supersedes the first draft: Ruff would reorder its imports back incorrectly. This tested patch explicitly preserves pccap-before-JAX initialization and binds the immediately evaluated lambda variables to pass B023. Numerical probes and Ruff pass in memory. No trainer changes. Awaiting permission under the new-files-only rule.

```diff
--- a/scripts/ht3b_objective_review.py
+++ b/scripts/ht3b_objective_review.py
@@ -6,9 +6,12 @@
 import json
 from pathlib import Path
 
+# isort: off
+import pccap  # noqa: F401 -- initialize determinism before JAX
 import jax
 import jax.numpy as jnp
 import numpy as np
+# isort: on
 
 from pccap.revision_v1.train import LossConfig, coupled_divergence, coupled_surprisal
 
@@ -26,7 +29,9 @@
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
