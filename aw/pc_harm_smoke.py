"""Tiny checkpoint readout fixture; production batched kernels with vocabulary-safe padding."""

import pccap  # noqa: F401 # isort: skip

# isort: split

import jax.numpy as jnp
import numpy as np

from aw.tests.test_pc_v0 import TinyEPC
from pccap.bases import gpt2_jax as g


class TinyBatchEPC(TinyEPC):
    def forward_batch(self, seqs, phase="query"):
        n = np.int32([len(s) for s in seqs])
        width = g.bucket_len(int(n.max()))
        ids = np.stack([np.pad(s, (0, width - len(s)), constant_values=0) for s in seqs])
        logits, rows, hidden = g.forward_batch_jit(
            self.params,
            jnp.asarray(ids),
            jnp.asarray(n),
            jnp.zeros((len(seqs), 3, self.d)),
            self.cfg,
        )
        return logits, rows, hidden, n
