"""Stage S5 runner: one substrate-comparison stream (plan §6.11 S5-02; PDF S5).

``pccap run --stage S5 --arm SB|SE-A|SE-E --realization r --perm o --manifest <confirm manifest>
--mode confirm`` (or a development manifest in dev mode). Arms come from
``manifests/dev/s5_arms.json``: base BP or the regenerated ePC checkpoint (``EPCBase.from_npz``),
credit ``adjoint`` or ``error`` (``CapConfig.credit``), router C1, read R-h; radii and b_m per base from
``results/S2/{radius_calibration,residual_scales}[_EPC].json``; everything else as the S4 runner.
The SB run may be shared with S4's C1 run only when every frozen field matches (S5-02) — this runner
always executes; provenance for reuse is recorded by the scheduler.
"""

from __future__ import annotations

import json
from pathlib import Path

from pccap.bases.bp import BPBase
from pccap.bases.checksum import assert_frozen
from pccap.bases.epc import EPCBase
from pccap.cap.cap import Cap, CapConfig
from pccap.contracts import Budget
from pccap.data.selection import stream_items
from pccap.data.tokenize import GPT2Tokenizer
from pccap.harness.ledger import Ledger
from pccap.harness.runner import RUNNERS
from pccap.harness.runs import CHECKPOINTS, Evaluator, run_stream
from pccap.harness.stage_s2 import load_dev_items
from pccap.harness.stage_s3 import chosen_A, drift_sample
from pccap.harness.stage_s4 import _items_from
from pccap.routers import make_router

ROOT = Path(__file__).resolve().parents[3]
ARMS = json.loads((ROOT / "manifests" / "dev" / "s5_arms.json").read_text())["arms"]


def calibration_for(label: str, ds: str) -> tuple[dict, dict]:
    suffix = "" if label == "BP" else f"_{label}"
    rc = json.loads((ROOT / "results" / "S2" / f"radius_calibration{suffix}.json").read_text())
    rs = json.loads((ROOT / "results" / "S2" / f"residual_scales{suffix}.json").read_text())
    radii = {int(m): float(rc["per_dataset"][ds][str(m)]["radius"]) for m in (1, 2, 3)}
    b_m = {int(m): float(v) for m, v in rs["pooled_b_m"].items()}
    return b_m, radii


def epc_weights() -> str:
    a = json.loads((ROOT / "manifests" / "assets.json").read_text())["assets"]["epc_checkpoint"]
    if a.get("status") != "regenerated" or not a.get("path"):
        raise RuntimeError("no regenerated ePC checkpoint recorded (REG-03)")
    return a["path"]


def run_s5(ctx: dict, run_dir: Path) -> dict:
    cfg, man = ctx["config"], ctx["manifest"]
    arm = cfg["arm"]
    spec = ARMS[arm]
    ledger = Ledger()
    base = BPBase(ledger=ledger) if spec["base"] == "BP" else EPCBase.from_npz(epc_weights(), ledger=ledger)
    tok = GPT2Tokenizer()
    if cfg.get("mode") == "confirm":
        from pccap.data.confirm import load as load_confirm

        frozen = ctx.get("frozen") or json.loads((ROOT / "manifests" / "frozen.json").read_text())
        man = load_confirm(Path(cfg["manifest"]), frozen=ROOT / "manifests" / "frozen.json")
        ds, oseed = man["dataset"], frozen["order_seeds"][int(cfg["perm"])]
        if ds != cfg.get("dataset") or int(man["realization"]) != int(cfg["realization"]):
            raise ValueError("CLI identity does not match the realization manifest")
        seeds = man["named_seeds"][str(oseed)]
        items = _items_from(stream_items(man, oseed, int(frozen["stream_lengths"][ds])))
        sub = frozen.get("substrate_arms") or {}
        if arm in sub:
            spec = sub[arm]  # frozen definitions, not the mutable development file (R2-08)
        budget = Budget(A=float(frozen["A"]), epsilon=float(frozen["epsilon"]), R=int(frozen["R"]), tau_edit=float(frozen["tau_edit"]))
        cap_seed, router_seed = int(seeds["seed_cap_init"]), int(seeds["seed_router"])
        n_loc, drift_n = 200, 4096
    else:
        ds = man["dataset"]
        items, _ = load_dev_items(ds, int(man.get("n_items", 100)), seed=int(man.get("order_seed", 100 + cfg["perm"])))
        b = man.get("budget", {})
        budget = Budget(A=b.get("A", chosen_A()), epsilon=b.get("epsilon", 0.01), R=b.get("R", 5), tau_edit=b.get("tau_edit", 0.1))
        cap_seed = router_seed = int(man.get("seed", 0)) + cfg["realization"]
        n_loc, drift_n = int(man.get("locality_prompts", 200)), int(man.get("drift_positions", 4096))
    b_m, radii = calibration_for(spec["base"], ds)
    cap = Cap(base, CapConfig(arm="C1", read="h", radii=radii, bank_scales=b_m, seed=cap_seed, credit=spec["credit"],
                              credit_iters=int(spec.get("credit_iters", 8))), ledger)
    _, unrelated = load_dev_items(ds, 1, seed=router_seed)
    h_before = base.checksum()
    ev = Evaluator(base, tok, unrelated[:n_loc], drift_sample(drift_n))
    metrics = run_stream(cap, items, make_router("C1"), budget, ev, run_dir, ledger, checkpoints=tuple(CHECKPOINTS), seed=router_seed, arm=arm)
    h_after = base.checksum()
    assert_frozen(h_before, h_after)
    metrics["base_hash_before"], metrics["base_hash_after"] = h_before, h_after
    metrics["config"] = {"dataset": ds, "realization": cfg["realization"], "perm": cfg["perm"], "substrate_arm": arm, "base": spec["base"],
                         "weights": getattr(base, "weights_label", "bp_teacher"), "credit": spec["credit"], "credit_iters": spec.get("credit_iters"),
                         "A": budget.A, "radii": radii, "b_m": b_m, "n_items": len(items)}
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=1, default=float))
    return metrics


RUNNERS["S5"] = run_s5
