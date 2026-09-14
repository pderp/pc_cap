"""R1-22 diagnostic: cosine between the ePC surrogate write gradient (−descent_sign · settled site error) and the exact
adjoint dL/dW at the three sites, on real episode prefixes with the controller's writes, for several settling iteration
counts. Answers whether the surrogate carries a descent direction for the answer loss at all.
    python scripts/r1_22_surrogate_check.py [--episodes 4] [--iters 8,32,64] [--no-lease] → results/R1/pilot/surrogate_check.json"""

from __future__ import annotations

import argparse
import contextlib
import json
from pathlib import Path

import jax
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "R1" / "pilot"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=4)
    ap.add_argument("--iters", default="8,32,64")
    ap.add_argument("--no-lease", action="store_true")
    args = ap.parse_args()
    import pccap  # noqa: F401
    from pccap.bases.epc import EPCBase
    from pccap.contracts import SiteId, Write
    from pccap.harness.lease import gpu_lease
    from pccap.harness.ledger import Ledger
    from pccap.revision_v1.controller import ControllerConfig, init_controller
    from pccap.revision_v1.epc_train import EPCWriteGradients, prefix_writes
    from pccap.revision_v1.episodes import synthetic_episode
    from pccap.revision_v1.observations import ObservationEncoder
    from pccap.revision_v1.reader import ReaderConfig, init_reader
    from pccap.revision_v1.train import ANSWER_ROLES, featurize

    frozen = json.loads((ROOT / "manifests" / "archive" / "frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json").read_text())
    b_m = tuple(float(frozen["b_m"][k]) for k in ("1", "2", "3"))
    rc, cc = ReaderConfig(), ControllerConfig(A=float(frozen["A"]), bank_scales=b_m)
    iters = [int(x) for x in args.iters.split(",")]
    with (contextlib.nullcontext() if args.no_lease else gpu_lease("R1:surrogate_check", stage="R1", projected_seconds=1800.0)):
        ledger = Ledger()
        base = EPCBase(ledger=ledger)
        enc = ObservationEncoder(base, taps=rc.taps)
        k1, k2 = jax.random.split(jax.random.PRNGKey(0))
        theta = {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)}
        rows = []
        for e in range(args.episodes):
            feats = featurize(base, enc, synthetic_episode(1000 + e, "train"), rc)
            for qi, q in enumerate(feats.queries):
                if q.role not in ANSWER_ROLES:
                    continue
                for ti, pf in enumerate(q.prefixes):
                    W = np.asarray(prefix_writes(theta, rc, cc, feats, qi, ti))
                    ids = pf.ids[: pf.n]
                    p = pf.n - 1
                    wl = [Write(SiteId(m, base.blocks[m] if hasattr(base, "blocks") else {1: 3, 2: 7, 3: 11}[m], p), W[m - 1]) for m in (1, 2, 3)]
                    grads, loss, _ = base.adjoint(ids, int(pf.target), wl, return_loss=True)
                    exact = np.stack([np.asarray(grads[s]) for s in sorted(grads, key=lambda s: s.bank)])
                    row = {"episode": e, "query": qi, "t": ti, "loss": float(loss), "exact_norm": [float(np.linalg.norm(x)) for x in exact]}
                    for it in iters:
                        wg = EPCWriteGradients(base, iters=it)
                        g, l_settled, diag = wg(ids, int(pf.target), W, q.role)
                        cos = [float(np.dot(g[m], exact[m]) / (np.linalg.norm(g[m]) * np.linalg.norm(exact[m]) + 1e-12)) for m in range(3)]
                        row[f"iters_{it}"] = {"cos": cos, "sur_norm": [float(np.linalg.norm(x)) for x in g], "r_k": diag["r_k"], "settled_ce": l_settled}
                    rows.append(row)
        summary = {"n": len(rows), "iters": iters}
        for it in iters:
            c = np.array([r[f"iters_{it}"]["cos"] for r in rows])
            summary[f"iters_{it}"] = {"cos_mean_per_site": c.mean(axis=0).tolist(), "cos_min_per_site": c.min(axis=0).tolist(), "frac_positive": (c > 0).mean(axis=0).tolist(),
                                      "r_k_mean": float(np.mean([r[f"iters_{it}"]["r_k"] for r in rows])),
                                      "norm_ratio_sur_over_exact": float(np.mean([np.mean(np.array(r[f"iters_{it}"]["sur_norm"]) / np.array(r["exact_norm"])) for r in rows]))}
        (OUT / "surrogate_check.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1))
        print(json.dumps(summary), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
