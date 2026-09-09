"""S1-03: P3 error localization and coverage (PDF D.3; plan §6.7).

For the 1,000 P3 sequences (128 tokens, summed next-token loss): mass per (layer, token) =
squared adjoint norm at every block output (BP adjoint; ePC adjoint and ePC finite errors when
REG-03 exists). Per sequence: PR, nPR = PR/N, final-block share, active fraction (cells above 1%
of the sequence maximum), zero fields counted separately; raw and layer-scale-normalized
(each layer's mass divided by the median residual norm² of that layer over the set). Dataset
layer shares aggregated. Final-block share > 0.4 → alert (not a failure).

    python -m pccap.analysis.s1_p3      # GPU lease
→ results/S1/P3_bp.json, coverage row.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from pccap.bases.bp import BPBase
from pccap.contracts import metric
from pccap.harness.ledger import Ledger
from pccap.metrics.participation import active_fraction, pr

ROOT = Path(__file__).resolve().parents[3]
LM_MANIFEST = ROOT / "manifests" / "dev" / "lm_sets.json"
S1 = ROOT / "results" / "S1"
ACTIVE_THRESHOLD = 0.01
FINAL_SHARE_ALERT = 0.4


def _load(name: str) -> np.ndarray:
    inv = json.loads(LM_MANIFEST.read_text())
    return np.load(inv["files"][name]["path"])


def mass_fields(base: BPBase, seqs: np.ndarray, batch: int = 16) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns (mass [N, 12, T-1], losses [N], layer_scale [12]) — the last position has no target."""
    masses, losses, scales = [], [], []
    for i in range(0, len(seqs), batch):
        chunk = seqs[i : i + batch]
        loss, grads = base.seq_adjoints_batch(chunk)  # grads [B, 12, T, d]
        hs = base.all_hidden_batch(chunk)[:, 1:]  # block outputs [B, 12, T, d]
        masses.append((grads[:, :, :-1, :].astype(np.float64) ** 2).sum(-1))
        scales.append((hs[:, :, :-1, :].astype(np.float64) ** 2).sum(-1))  # residual norm² per (layer, token)
        losses.append(loss)
    mass = np.concatenate(masses)
    scale = np.median(np.concatenate(scales), axis=(0, 2))  # [12]
    return mass, np.concatenate(losses), scale


def summarize(mass: np.ndarray, label: str) -> dict:
    N_cells = mass.shape[1] * mass.shape[2]
    prs, nprs, final_share, active, zero = [], [], [], [], 0
    layer_share_sum = np.zeros(mass.shape[1])
    for m in mass:
        tot = m.sum()
        if tot <= 0:
            zero += 1
            continue
        p = pr(m)
        prs.append(p["value"])
        nprs.append(p["value"] / N_cells)
        final_share.append(float(m[-1].sum() / tot))
        active.append(active_fraction(m, threshold=ACTIVE_THRESHOLD)["value"])
        layer_share_sum += m.sum(1) / tot
    n = len(prs)
    ls = (layer_share_sum / n).tolist() if n else None
    return {
        f"pr_mean_{label}": metric(float(np.mean(prs)) if n else None, units="cells", n=n, status="ok" if n else "undefined"),
        f"npr_mean_{label}": metric(float(np.mean(nprs)) if n else None, units="fraction", n=n, status="ok" if n else "undefined"),
        f"final_block_share_mean_{label}": metric(float(np.mean(final_share)) if n else None, units="fraction", n=n, status="ok" if n else "undefined",
                                                 strata={"alert_above_0.4": bool(np.mean(final_share) > FINAL_SHARE_ALERT) if n else None}),
        f"active_fraction_mean_{label}": metric(float(np.mean(active)) if n else None, units="fraction", n=n, status="ok" if n else "undefined"),
        f"zero_fields_{label}": metric(zero, units="count", n=len(mass)),
        f"distribution_{label}": {"pr_quantiles": np.quantile(prs, [0.05, 0.25, 0.5, 0.75, 0.95]).tolist() if n else None,
                                  "final_share_quantiles": np.quantile(final_share, [0.05, 0.25, 0.5, 0.75, 0.95]).tolist() if n else None,
                                  "dataset_layer_shares": ls},
    }


def run(label: str = "bp") -> dict:
    from pccap.harness.lease import gpu_lease

    S1.mkdir(parents=True, exist_ok=True)
    with gpu_lease("S1-03", stage="S1", projected_seconds=1800) as lease:
        ledger = Ledger()
        base = BPBase(ledger=ledger)
        P3 = _load("P3_sequences")
        mass, losses, scale = mass_fields(base, P3)
        raw = summarize(mass, "raw")
        normalized = summarize(mass / scale[None, :, None], "layer_normalized")
        out = {"stage": "S1", "property": "P3", "base": label, "signal": "BP adjoint of the summed next-token loss; mass = squared adjoint norm per (block output, token)",
               "sequences": int(mass.shape[0]), "cells_per_sequence": int(mass.shape[1] * mass.shape[2]),
               "metrics": {k: v for k, v in {**raw, **normalized}.items() if not k.startswith("distribution")},
               "distributions": {k: v for k, v in {**raw, **normalized}.items() if k.startswith("distribution")},
               "layer_scale_median_residual_norm2": scale.tolist(), "loss_mean": float(losses.mean()), "coordinates": "raw fp32 residual coordinates; normalized variant divides each layer's mass by its median residual norm² (neither is coordinate invariant, D.3)",
               "mechanism_strata": "grammar-only (pending GRAM-02/DATA-06)", "lease": lease.report, "ledger": ledger.totals(),
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    (S1 / f"P3_{label}.json").write_text(json.dumps(out, indent=1, default=float))
    np.save(Path("/home/derp/cap/assets/runs/S1") / f"P3_mass_{label}.npy", mass.astype(np.float32)) if Path("/home/derp/cap/assets/runs/S1").mkdir(parents=True, exist_ok=True) is None else None
    from pccap.analysis.s1_p6 import update_coverage

    update_coverage({"P3": {"bp_adjoint": "complete", "epc_adjoint": "pending (REG-03)", "epc_error": "pending (REG-03)", "grammar_strata": "pending (GRAM-02)"}})
    return out


if __name__ == "__main__":
    o = run()
    print({k: v["value"] for k, v in o["metrics"].items()})
