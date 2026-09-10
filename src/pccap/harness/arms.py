"""Arm registry: one place that builds the learner for an arm name (cap arms and baselines).

Cap arms ``C0/C1/C2/CR/CO`` → ``pccap.cap.cap.Cap`` with the arm's router; baselines
``B0`` (frozen), ``B1`` (Q/V LoRA, S2-03), ``B3`` (LoRA + replay reservoir, S2-04) → the Lane F
learners wrapped in a thin harness adapter that adds the batched read-only evaluation entry point
``last_logits_batch(seqs, phase)`` the evaluator uses (HARN-BATCH): a vmapped LoRA-merged forward
over one padding bucket, charged as ``query`` full forwards, parity-tested against the learner's
own sequential ``predict`` (``tests/harness/test_baseline_arms.py``). Everything else is delegated
unchanged (``update_item``, ``export_state``/``import_state``, ``state_hash``, ``memory_bytes``,
``base_checksum``), so snapshots and ItemGuard rollback are the learner's own. ``B4`` (GRACE)
is registered when S2-05 lands.
"""

from __future__ import annotations

import functools

import jax
import jax.numpy as jnp
import numpy as np

from pccap.bases import gpt2_jax as g

CAP_ARMS = ("C0", "C1", "C2", "CR", "CO")
BASELINE_ARMS = ("B0", "B1", "B3")


@functools.partial(jax.jit, static_argnames=("cfg",))
def _lora_last_logits_batch(params, adapters, ids, n, cfg):
    from pccap.baselines import lora_forward as lf

    def one(i, k):
        logits = lf.forward(params, adapters, i, cfg)
        return jax.lax.dynamic_index_in_dim(logits, k - 1, axis=0, keepdims=False)

    return jax.vmap(one)(ids, n)


class _Delegate:
    _delegated = ("update_item", "export_state", "import_state", "state_hash", "memory_bytes", "base_checksum", "predict")

    def __init__(self, learner):
        self.learner = learner
        self.base, self.ledger = learner.base, learner.ledger
        self.name = learner.name

    def __getattr__(self, item):
        if item in self._delegated or item in ("lora", "adapters", "buffer", "items_seen", "update_steps", "steps", "rank", "lr"):
            return getattr(self.learner, item)
        raise AttributeError(item)


class LoRAArm(_Delegate):
    """B1/B3 adapter: batched last-row logits through the LoRA-merged forward."""

    def _adapters(self):
        return self.learner.lora.adapters if hasattr(self.learner, "lora") else self.learner.adapters

    def last_logits_batch(self, seqs: list[np.ndarray], phase: str = "query") -> np.ndarray:
        n = np.asarray([len(s) for s in seqs], np.int32)
        T = min(g.bucket_len(int(n.max())), self.base.cfg.n_pos)
        ids = np.stack([g.pad_ids(np.asarray(s, np.int32), T, 0) for s in seqs])
        with self.ledger.call(phase, full_forwards=len(seqs), tokens=int(n.sum())) as rec:
            out = _lora_last_logits_batch(self.base.params, self._adapters(), jnp.asarray(ids), jnp.asarray(n), self.base.cfg)
            rec.outputs = out
        return np.asarray(out)


class FrozenArm(_Delegate):
    """B0 adapter: batched cap-off evaluation straight through the base."""

    def last_logits_batch(self, seqs: list[np.ndarray], phase: str = "query") -> np.ndarray:
        return self.base.last_logits_batch(seqs, phase=phase)


def make_learner(arm: str, base, ledger, *, radii=None, bank_scales=None, read: str = "h", seed: int = 0,
                 lora_lr: float = 1e-4, lora_rank: int = 8, lora_steps: int = 10):
    """Learner for ``arm`` on ``base`` (a ``BPBase``/``EPCBase`` sharing ``ledger``)."""
    if arm in CAP_ARMS:
        from pccap.cap.cap import Cap, CapConfig

        d = int(getattr(base, "d", 768))  # model-specific width (R2-09); key_dim follows the read variant inside Cap
        return Cap(base, CapConfig(arm=arm, read=read, radii=radii, bank_scales=bank_scales, seed=seed, d=d), ledger)
    if arm == "B0":
        from pccap.baselines.b0 import B0

        return FrozenArm(B0(base))
    if arm == "B1":
        from pccap.baselines.lora import LoRALearner

        return LoRAArm(LoRALearner(base, rank=lora_rank, lr=lora_lr, steps=lora_steps, seed=seed))
    if arm == "B3":
        from pccap.baselines.lora import LoRALearner
        from pccap.baselines.replay import ReplayLearner

        return LoRAArm(ReplayLearner(LoRALearner(base, rank=lora_rank, lr=lora_lr, steps=lora_steps, seed=seed), seed=seed))
    if arm == "B4":
        raise NotImplementedError("B4 (GRACE) is registered by S2-05")
    raise ValueError(f"unknown arm {arm!r}")


def router_for(arm: str, cr_distribution: dict | None = None, cr_label: str = "cr_profile_uniform"):
    """Router for a cap arm (None for baselines). ``cr_distribution`` (bank → probability) selects the
    S3-05 development-estimated CR distribution instead of the uniform profiling one (SD-11)."""
    if arm in CAP_ARMS:
        from pccap.routers import make_router

        if arm == "CR" and cr_distribution is not None:
            return make_router(arm, distribution={int(k): float(v) for k, v in cr_distribution.items()}, label=cr_label)
        return make_router(arm)
    return None


def cr_distribution_for(dataset: str, path=None) -> tuple[dict | None, str]:
    """(distribution, label) from manifests/cr_distribution.json for ``dataset``; (None, uniform) if absent."""
    import json
    from pathlib import Path

    p = Path(path) if path else Path(__file__).resolve().parents[3] / "manifests" / "cr_distribution.json"
    if not p.exists():
        return None, "cr_profile_uniform"
    d = json.loads(p.read_text())["per_dataset"].get(dataset)
    if d is None:
        return None, "cr_profile_uniform"
    return d["distribution"], d["label"]
