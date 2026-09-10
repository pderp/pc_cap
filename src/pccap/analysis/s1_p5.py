"""S1-05: P5 write locality (PDF D.5; plan §6.7; SD-2).

Q = 200 development edit prompts and U = 200 unrelated prompts, manifest-fixed
(``manifests/dev/p5_subsets.json``, seed 17, 100 per dataset). At each bank site, with the BP
adjoint credit rule (ePC rules pending REG-03): the unit descent direction ``d_m`` at the last
prompt position for the target = first gold answer token; a bounded geometric search for a 50%
reduction of the current-token loss: forced writes ``a·b_m·d_m`` with ``a`` on the CAP-06 grid at
A = 0.1 scaled up by up to 8 doublings (``a ∈ {0.1/8, …, 0.1} × 2^k, k = 0..8``, 36 candidates,
smallest ``a`` reaching the target wins); recorded: achieved improvement, normalized write norm
``‖Δ‖/b_m``, ``unreachable`` when no candidate reaches 50%. Unconditional collateral
``C_q = mean_u KL(p_u(0) ‖ p_u(v_q))`` applying the *same* write at every u's prediction position
(the write that achieved the target, else the best candidate). The gated cap's behaviour on U
(firing rate, complete-answer changes) is measured separately from the S2-02 A = 0.3 screening
caps (deployed-gate false-fire). Improvement/collateral ratio: undefined at 0/0, right-unbounded
(``unreachable`` status with operands) when collateral is 0 and improvement > 0.

    python -m pccap.analysis.s1_p5      # GPU lease
→ results/S1/P5_bp.json, manifests/dev/p5_subsets.json, coverage row.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from pccap.bases import gpt2_jax as g
from pccap.bases.bp import BPBase
from pccap.contracts import SiteId, Write, metric
from pccap.data.tokenize import GPT2Tokenizer
from pccap.harness.ledger import Ledger
from pccap.metrics.divergence import kl
from pccap.transport.transport import Transport

ROOT = Path(__file__).resolve().parents[3]
DEV = ROOT / "manifests" / "dev"
S1 = ROOT / "results" / "S1"
S2 = ROOT / "results" / "S2"
SUBSETS = DEV / "p5_subsets.json"
GRID_BASE = (0.1 / 8, 0.1 / 4, 0.1 / 2, 0.1)
DOUBLINGS = 8
TARGET_REDUCTION = 0.5


def make_subsets(seed: int = 17, per_dataset: int = 100) -> dict:
    rng = np.random.default_rng(seed)
    out = {"seed": seed, "Q": [], "U": []}
    for ds in ("zsre", "counterfact"):
        man = json.loads((DEV / f"{ds}_dev.json").read_text())
        qi = rng.permutation(len(man["items"]))[:per_dataset]
        out["Q"] += [{"dataset": ds, "item_id": man["items"][i]["item_id"], "prompt": man["items"][i]["prompt"],
                      "prompt_ids": man["items"][i]["prompt_ids"], "target": man["items"][i]["answer_ids"][0]} for i in sorted(qi)]
        ui = rng.permutation(len(man["unrelated_prompts"]))[:per_dataset]
        out["U"] += [{"dataset": ds, "prompt": man["unrelated_prompts"][i]} for i in sorted(ui)]
    SUBSETS.write_text(json.dumps(out, indent=1) + "\n")
    return out


def softmax(row: np.ndarray) -> np.ndarray:
    r = row.astype(np.float64)
    r = r - r.max()
    e = np.exp(r)
    return e / e.sum()


def search_site(base: BPBase, ids: np.ndarray, target: int, site: SiteId, direction: np.ndarray, b_m: float, L0: float) -> dict:
    cands = []
    best = None
    for k in range(DOUBLINGS + 1):
        for a0 in GRID_BASE:
            a = a0 * (2**k)
            v = (a * b_m * direction).astype(np.float32)
            L, _ = base.loss(ids, target, [Write(site, v)], phase="query")
            imp = L0 - L
            cands.append({"a": a, "loss": L, "improvement": imp, "normalized_norm": float(np.linalg.norm(v) / b_m)})
            if best is None or imp > best["improvement"]:
                best = cands[-1] | {"vector": v}
            if imp >= TARGET_REDUCTION * L0:
                return {"status": "ok", "a": a, "loss": L, "improvement": imp, "normalized_norm": float(np.linalg.norm(v) / b_m),
                        "vector": v, "candidates": cands}
    return {"status": "unreachable", "a": best["a"], "loss": best["loss"], "improvement": best["improvement"],
            "normalized_norm": best["normalized_norm"], "vector": best["vector"], "candidates": cands}


def collateral(base: BPBase, u_ids: list[np.ndarray], site_bank: int, v: np.ndarray, p0: list[np.ndarray]) -> float:
    kls = []
    for ids, p_base in zip(u_ids, p0):
        p = len(ids) - 1
        fr = base.forward(ids, [Write(SiteId(site_bank, g.BANK_BLOCK[site_bank], p), v)], phase="query")
        kls.append(kl(p_base, softmax(np.asarray(fr.logits[p])))["value"])
    return float(np.mean(kls))


def ratio_metric(imp: float, coll: float) -> dict:
    if imp == 0 and coll == 0:
        return metric(None, units="nats/nats", numerator=imp, denominator=coll, status="undefined")
    if coll == 0:
        return metric(None, units="nats/nats", numerator=imp, denominator=coll, status="unreachable", exclusions=["right-unbounded: collateral 0 with positive improvement"])
    return metric(imp / coll, units="nats/nats", numerator=imp, denominator=coll, n=1)


def run(label: str = "bp") -> dict:
    from pccap.harness.lease import gpu_lease

    S1.mkdir(parents=True, exist_ok=True)
    subs = json.loads(SUBSETS.read_text()) if SUBSETS.exists() else make_subsets()
    b_m = {int(k): float(v) for k, v in json.loads((S2 / "residual_scales.json").read_text())["pooled_b_m"].items()}
    tok = GPT2Tokenizer()
    tr = Transport()
    with gpu_lease("S1-05", stage="S1", projected_seconds=3600) as lease:
        ledger = Ledger()
        base = BPBase(ledger=ledger)
        u_ids = [tok.encode(u["prompt"]) for u in subs["U"]]
        p0 = [softmax(np.asarray(base.forward(ids, phase="query").logits[len(ids) - 1])) for ids in u_ids]
        rows = []
        for q in subs["Q"]:
            ids = np.asarray(q["prompt_ids"], np.int32)
            p = len(ids) - 1
            target = int(q["target"])
            grads, L0, _ = base.adjoint(ids, target, [], return_loss=True)
            row = {"item_id": q["item_id"], "dataset": q["dataset"], "loss0": L0, "sites": {}}
            for m in (1, 2, 3):
                site = SiteId(m, g.BANK_BLOCK[m], p)
                d = tr.direction(np.asarray(grads[site], np.float32), site)
                if d.status != "ok":
                    row["sites"][str(m)] = {"status": "no_direction"}
                    continue
                s = search_site(base, ids, target, site, np.asarray(d.direction), b_m[m], L0)
                c = collateral(base, u_ids, m, s["vector"], p0)
                row["sites"][str(m)] = {"status": s["status"], "a": s["a"], "improvement": s["improvement"], "achieved_fraction": s["improvement"] / L0 if L0 > 0 else None,
                                        "normalized_norm": s["normalized_norm"], "collateral_kl": c, "ratio": ratio_metric(s["improvement"], c),
                                        "candidates_tried": len(s["candidates"])}
            rows.append(row)
        # aggregates per site
        agg = {}
        for m in ("1", "2", "3"):
            ok = [r["sites"][m] for r in rows if r["sites"][m].get("status") == "ok"]
            unr = [r["sites"][m] for r in rows if r["sites"][m].get("status") == "unreachable"]
            nod = sum(r["sites"][m].get("status") == "no_direction" for r in rows)
            allr = ok + unr
            agg[f"bank{m}_reached_50pct"] = metric(len(ok) / len(rows), units="fraction", numerator=len(ok), denominator=len(rows), n=len(rows))
            agg[f"bank{m}_unreachable"] = metric(len(unr), units="count", n=len(rows), strata={"no_direction": nod})
            agg[f"bank{m}_norm_at_target_median"] = metric(float(np.median([s["normalized_norm"] for s in ok])) if ok else None, units="normalized write norm", n=len(ok), status="ok" if ok else "unreachable")
            agg[f"bank{m}_collateral_kl_mean"] = metric(float(np.mean([s["collateral_kl"] for s in allr])) if allr else None, units="nats", n=len(allr), status="ok" if allr else "undefined")
            agg[f"bank{m}_collateral_kl_at_target_mean"] = metric(float(np.mean([s["collateral_kl"] for s in ok])) if ok else None, units="nats", n=len(ok), status="ok" if ok else "unreachable")
            agg[f"bank{m}_improvement_mean"] = metric(float(np.mean([s["improvement"] for s in allr])) if allr else None, units="nats", n=len(allr), status="ok" if allr else "undefined")
        gated = {}
        for A in ("0.3",):
            for ds in ("zsre", "counterfact"):
                mp = S2 / "screen" / f"A{A}" / ds / "metrics.json"
                if mp.exists():
                    mm = json.loads(mp.read_text())
                    gated[f"{ds}_A{A}"] = {"false_fire": mm["false_fire"], "source": str(mp), "note": "deployed gate after 100 learned edits (S2-02)"}
        out = {"stage": "S1", "property": "P5", "base": label, "credit_rule": "BP adjoint", "Q": len(subs["Q"]), "U": len(subs["U"]),
               "search": {"grid": "CAP-06 grid at A=0.1 scaled by 2^k, k=0..8", "target": "50% current-token loss reduction"},
               "b_m": b_m, "metrics": agg, "gated_cap_on_U": gated, "rows": rows,
               "retrieval_drift": "pending (needs saved learner checkpoints from S3/S4 runs; tracked in results/S1/drift_*.json when produced)",
               "lease": lease.report, "ledger": ledger.totals(), "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    (S1 / f"P5_{label}.json").write_text(json.dumps(out, indent=1, default=float))
    from pccap.analysis.s1_p6 import update_coverage

    update_coverage({"P5": {"bp_adjoint": "complete", "epc_adjoint": "pending (REG-03)", "epc_error": "pending (REG-03)", "retrieval_drift": "pending (S3/S4 checkpoints)"}})
    return out


if __name__ == "__main__":
    o = run()
    print(json.dumps({k: v["value"] for k, v in o["metrics"].items()}, indent=1))
