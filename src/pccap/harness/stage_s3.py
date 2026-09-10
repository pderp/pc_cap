"""Stage S3 runner: development streams for the cap arms through ``pccap run --stage S3``.

Manifest (``manifests/dev/s3_*.json``): ``dataset`` (zsre | counterfact), ``n_items``,
``order_seed`` (permutation of the development pool after excluding the S0 sample), ``budget``
(A defaults to the S2-02 choice), ``radii`` (default: S2-01 per-dataset), ``bank_scales`` (default:
S2-01 pooled b_m), ``locality_prompts`` (count from the dev unrelated pool), ``drift_positions``
(sequential drift sample size, default 4,096; 0 disables), ``checkpoints``. The arm comes from the
CLI (``--arm C0|C1|C2|CR``; CO only on fixtures). Results follow ``harness.runs``.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from pccap.bases.bp import BPBase
from pccap.bases.checksum import assert_frozen
from pccap.cap.cap import Cap, CapConfig
from pccap.contracts import Budget
from pccap.data.tokenize import GPT2Tokenizer
from pccap.harness import runner
from pccap.harness.ledger import Ledger
from pccap.harness.runs import CHECKPOINTS, Evaluator, run_stream
from pccap.harness.stage_s2 import calibration, load_dev_items
from pccap.routers import make_router

ROOT = Path(__file__).resolve().parents[3]
S2 = ROOT / "results" / "S2"


def chosen_A(default: float = 0.3) -> float:
    p = S2 / "A_screening.json"
    if p.exists():
        a = json.loads(p.read_text()).get("chosen_A")
        if a is not None:
            return float(a)
    return default


def drift_sample(n_positions: int) -> np.ndarray | None:
    if n_positions <= 0:
        return None
    inv = json.loads((ROOT / "manifests" / "dev" / "lm_sets.json").read_text())
    return np.load(inv["files"]["drift_tokens"]["path"])[: n_positions + 128]


@runner.register("S3")
def run_s3(ctx: dict, run_dir: Path) -> dict:
    cfg, man = ctx["config"], ctx["manifest"]
    ds = man["dataset"]
    n = int(man.get("n_items", 100))
    ledger = Ledger()
    base = BPBase(ledger=ledger)
    tok = GPT2Tokenizer()
    b_m, radii = calibration(ds)
    if "bank_scales" in man:
        b_m = {int(k): float(v) for k, v in man["bank_scales"].items()}
    if "radii" in man:
        radii = {int(k): float(v) for k, v in man["radii"].items()}
    b = man.get("budget", {})
    budget = Budget(A=b.get("A", chosen_A()), epsilon=b.get("epsilon", 0.01), R=b.get("R", 5), tau_edit=b.get("tau_edit", 0.1))
    items, unrelated = load_dev_items(ds, n, seed=int(man.get("order_seed", 100 + cfg["perm"])))
    cap = Cap(base, CapConfig(arm=cfg["arm"], read=cfg["read"], radii=radii, bank_scales=b_m, seed=int(man.get("seed", 0)) + cfg["realization"]), ledger)
    router = make_router(cfg["arm"])
    h_before = base.checksum()
    ev = Evaluator(base, tok, unrelated[: int(man.get("locality_prompts", 200))], drift_sample(int(man.get("drift_positions", 4096))))
    metrics = run_stream(cap, items, router, budget, ev, run_dir, ledger, checkpoints=tuple(man.get("checkpoints", CHECKPOINTS)),
                         seed=int(man.get("seed", 0)), arm=cfg["arm"])
    h_after = base.checksum()
    assert_frozen(h_before, h_after)
    metrics["base_hash_before"], metrics["base_hash_after"] = h_before, h_after
    metrics["config"] = {"A": budget.A, "radii": radii, "b_m": b_m, "dataset": ds, "n_items": n, "order_seed": int(man.get("order_seed", 100 + cfg["perm"]))}
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=1, default=float))
    return {"base_hash_before": h_before, "base_hash_after": h_after, "status": metrics["status"]}
