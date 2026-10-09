"""Model construction for ext-20261009: frozen GPT-2 small, the six PC-reader caps, and saved memories.

Everything reuses the frozen study's own constructors (``construct_owner_adapter``, ``InterfaceCap``,
``load_theta``) so that the caps scored here are bit-identical to the caps that produced the frozen record.
Nothing here writes to the frozen record.
"""

from __future__ import annotations

import pccap  # noqa: F401  # isort: skip  (determinism settings before JAX)

import dataclasses
from pathlib import Path

import numpy as np

from aw.extremes.common import ASSETS, ROOT, read_json, sha
from pccap.contracts import ForwardResult

PCR = ROOT / "results/additional_work/PC-reader"
PCR_ASSETS = ASSETS / "runs/additional_work/PC-reader"

# Sealed R1_learned_ff recipes, realization 0, order 100 (the PC-reader study's population). zsRE and CounterFact
# identities are copied from aw/pc_v1_run.RECIPES; MQuAKE is the sibling sealed recipe (same realization/order).
RECIPES = {
    "zsre": ("docs/tasks/R1-final-cell-recipes/61348508e40d54351613ab14.json", "a14686a8bd0651e8e06b6bbf64b90420f175b7f77991dc5c885cd106ac340b35"),
    "counterfact": ("docs/tasks/R1-final-cell-recipes/ce0d0ffc2a58a60e27c460d9.json", "e3b541c4e5b2a5087ab6f1c8191d2caab5cadae0955d83b33d47e111cd3cba31"),
    "mquake": ("docs/tasks/R1-final-cell-recipes/43925e53c31860219a85ef90.json", None),  # pinned at first use (manifest)
}
BASE_SHA = "c4ac3fb867dad146dbddfcd4af0b9b110d8de3bce41127bb1fc11b1e533bc082"


def recipe(dataset: str) -> tuple[dict, dict]:
    name, expected = RECIPES[dataset]
    path = ROOT / name
    got = sha(path)
    if expected is not None and got != expected:
        raise ValueError(f"recipe identity differs: {path}")
    return read_json(path), dict(path=str(path), sha256=got)


def payload(dataset: str) -> tuple[dict, dict]:
    r, _ = recipe(dataset)
    p = Path(r["payload"]["path"])
    got = sha(p)
    if got != r["payload"]["sha256"]:
        raise ValueError("payload identity differs: " + str(p))
    return read_json(p), dict(path=str(p), sha256=got)


class FrozenModel:
    """GPT-2 small with no reader, no memory and no writes: ``predict`` is the bare base forward."""

    name = "frozen"

    def __init__(self, base, tokenizer):
        self.base, self.tok = base, tokenizer
        self._hash = base.checksum(recompute=True)
        self.locality_base = base

    def predict(self, ids) -> ForwardResult:
        return self.base.forward(ids, (), phase="query", last_only=True)

    def state_hash(self) -> str:
        return "frozen:" + self._hash

    def reset_queries(self) -> None:
        pass

    def checksum(self, recompute: bool = True) -> str:
        return self.base.checksum(recompute=recompute)


def load_frozen(dataset: str = "zsre"):
    """The base and tokenizer exactly as the sealed recipe constructs them (same snapshot, same hashes)."""
    from scripts.r1_61_cell_driver import construct_owner_adapter

    native, binding = recipe(dataset)
    parent, tok = construct_owner_adapter(native)
    if parent.identity() != native["adapter_identity"]:
        raise ValueError("original constructor identity differs")
    base = parent.base
    if base.checksum(recompute=True) != BASE_SHA:
        raise ValueError("frozen base digest differs from the record")
    return FrozenModel(base, tok), parent, tok, binding


def load_direct_params():
    """Independent load of the same weights through ``gpt2_jax.load_params_numpy`` (no BPBase, no ledger)."""
    from pccap.bases import gpt2_jax as g
    from pccap.bases.bp import _digest

    cfg = g.GPT2Config.from_snapshot(g.DEFAULT_SNAPSHOT)
    params_np = g.load_params_numpy(g.DEFAULT_SNAPSHOT, cfg)
    return params_np, cfg, _digest(params_np)


def training_report(rule: str, seed: int) -> dict:
    tr = read_json(PCR / f"train-{rule}-s{seed}" / "report.json")
    if tr.get("status") != "complete" or tr["rule"] != rule or tr["seed"] != seed or tr.get("profile_only"):
        raise ValueError(f"unexpected training report for {rule} seed {seed}")
    if tr["base_sha256"] != BASE_SHA:
        raise ValueError("reader was trained on a different base")
    return tr


def load_reader(rule: str, seed: int, dataset: str, parent=None):
    """The PC-reader cap (rule in {bp, epc}, seed in {0,1,2}) on the sealed base, empty memory.

    Mirrors ``aw.trained_reader_eval.execute_evaluation`` construction exactly (taps, template, theta, interface).
    """
    from aw.interface import ALL, InterfaceCap, InterfaceConfig
    from aw.pc_reader_train import initial_theta, load_theta
    from pccap.revision_v1.reader import params_hash
    from pccap.revision_v1.stage4_adapters import CellAdapter
    from scripts.r1_61_cell_driver import construct_owner_adapter

    native, binding = recipe(dataset)
    if parent is None:
        parent, tok = construct_owner_adapter(native)
    else:
        parent, tok = parent
    if parent.identity() != native["adapter_identity"]:
        raise ValueError("original constructor identity differs")
    tr = training_report(rule, seed)
    cfg = dataclasses.replace(parent.learner.cfg, reader=dataclasses.replace(parent.learner.cfg.reader, taps=tuple(tr["read_taps"])))
    template = initial_theta(tr["seed"], cfg.reader, cfg.controller)
    theta = load_theta(tr["reader"], template)
    cap = InterfaceCap(parent.base, cfg, parent.ledger, params=theta, interface=InterfaceConfig(tuple(tr["read_taps"]), ALL))
    if cap.base.checksum(recompute=True) != tr["base_sha256"]:
        raise ValueError("training/evaluation bases differ")
    if params_hash(cap.params) != tr["reader"]["params_sha256"]:
        raise ValueError("loaded reader parameters differ from the training report")
    adapter = CellAdapter(cap, "R1_learned_ff", budget=parent.budget)
    return adapter, cap, tok, dict(training=dict(path=str(PCR / f"train-{rule}-s{seed}" / "report.json"), sha256=sha(PCR / f"train-{rule}-s{seed}" / "report.json")), reader=tr["reader"], recipe=binding)


def eval_dir(rule: str, seed: int, dataset: str) -> Path:
    """Frozen-record evaluation directory for zsRE/CounterFact; this study's own directory for MQuAKE."""
    if dataset in ("zsre", "counterfact"):
        return PCR / f"eval-{rule}-s{seed}-{dataset}"
    from aw.extremes.common import OUT

    return OUT / "mquake_eval" / f"eval-{rule}-s{seed}-mquake"


def snapshot_record(rule: str, seed: int, dataset: str, horizon: int) -> dict:
    cp = read_json(eval_dir(rule, seed, dataset) / "stream" / f"checkpoint-{horizon}.json")
    return cp["snapshot"]


def restore_memory(adapter, cap, record: dict) -> str:
    """Load a saved memory snapshot into the cap and verify every identity the record carries."""
    from pccap.harness.snapshot import restore
    from pccap.revision_v1.reader import params_hash

    blob = Path(record["path"]).read_bytes()
    if sha(record["path"]) != record["sha256"]:
        raise ValueError("snapshot bytes changed: " + record["path"])
    state = restore(blob, expected_hash=record["state_sha256"])
    adapter.import_state(state)
    if cap.state_hash() != record["state_sha256"]:
        raise ValueError("restored memory differs")
    if params_hash(cap.params) != record["reader_sha256"]:
        raise ValueError("snapshot was written by a different reader")
    if cap.base.checksum(recompute=True) != record["base_sha256"]:
        raise ValueError("snapshot was written on a different base")
    return record["state_sha256"]


class WriteCapture:
    """Record the write vectors and pre-write site residuals used by ``cap.predict`` calls.

    Wraps the base's ``forward`` and ``forward_from`` on the instance for the duration of a ``with`` block; the
    arithmetic is untouched, only the arguments/results are observed. ``sites`` holds the pre-write residual rows
    at the prediction position (from ``ForwardResult.sites``), ``writes`` the [3, d] write arrays actually applied
    (zeros when the cap abstained).
    """

    def __init__(self, base, d: int = 768):
        self.base, self.d = base, d
        self.sites: list[dict[int, np.ndarray]] = []
        self.writes: list[np.ndarray] = []
        self._orig_forward = base.forward
        self._orig_forward_from = base.forward_from
        self._last_sites = None

    def __enter__(self):
        capture = self

        def forward(ids, writes=(), retain_sites=False, phase="learning", last_only=False):
            fr = capture._orig_forward(ids, writes, retain_sites=retain_sites, phase=phase, last_only=last_only)
            capture._last_sites = {s.bank: np.asarray(v, np.float32) for s, v in fr.sites.items()}
            return fr

        def forward_from(bank, hidden, ids, writes=(), phase="learning", retain_sites=False, last_only=False):
            W = np.zeros((3, capture.d), np.float32)
            for w in writes:
                W[w.site.bank - 1] += np.asarray(w.vector, np.float32)
            capture.writes.append(W)
            capture.sites.append(capture._last_sites or {})
            return capture._orig_forward_from(bank, hidden, ids, writes, phase=phase, retain_sites=retain_sites, last_only=last_only)

        self.base.forward = forward
        self.base.forward_from = forward_from
        return self

    def __exit__(self, *exc):
        self.base.forward = self._orig_forward
        self.base.forward_from = self._orig_forward_from
        return False
