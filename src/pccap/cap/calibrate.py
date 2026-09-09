"""S2-01: residual scales ``b_m`` and radius calibration (PDF S2 "Radius calibration", F.6).

* ``b_m`` = median raw residual norm at each bank site over cap-disabled development prefixes
  (every gold prefix of every development edit, including the terminator prefix), floored at
  1e-8 → ``results/S2/residual_scales.json``.
* Radius per bank (read variant R-h): observed key distances ``‖z(h_p(edit)) − z(h_p(paraphrase))‖``
  (coverage pairs) and ``‖z(h_p(edit)) − z(h_p(unrelated))‖`` (false-fire pairs) at the last
  prompt position; 20-quantile grid of all observed distances; choose the **largest** radius whose
  unrelated false-fire rate (fraction of unrelated prompts within the radius of *any* dev edit
  key) is ≤ 1%, ties by paraphrase coverage; every candidate stored. No positive radius → exact
  keys (radius 0) with the limitation recorded (CR-4 interpretation) →
  ``results/S2/radius_calibration.json``.

Keys and distances use exactly the cap's feature (``pccap.cap.features.z``) and the bank's
Euclidean distance, so the numbers transfer to ``CapConfig.radii`` unchanged.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from pccap.bases import gpt2_jax as g
from pccap.bases.bp import BPBase
from pccap.cap.features import z as key_feature
from pccap.contracts import SiteId
from pccap.data.tokenize import GPT2Tokenizer

ROOT = Path(__file__).resolve().parents[3]
DEV = ROOT / "manifests" / "dev"
OUT = ROOT / "results" / "S2"
FALSE_FIRE_MAX = 0.01
N_QUANTILES = 20


def _site_rows(base: BPBase, ids: np.ndarray) -> dict[int, np.ndarray]:
    fr = base.forward(ids, phase="query")
    p = len(ids) - 1
    return {m: np.asarray(fr.sites[SiteId(m, g.BANK_BLOCK[m], p)], np.float32) for m in (1, 2, 3)}


def residual_scales(base: BPBase, items: list[dict], max_items: int | None = None) -> dict:
    norms = {1: [], 2: [], 3: []}
    n_prefixes = 0
    for it in items[:max_items]:
        ids = np.asarray(it["prompt_ids"], np.int32)
        for y in [None, *it["answer_ids"]]:
            if y is not None:
                ids = np.concatenate([ids, np.int32([y])])
            if y == it["answer_ids"][-1]:
                break  # the prefix ending in the terminator is not a prediction prefix
            rows = _site_rows(base, ids)
            for m in (1, 2, 3):
                norms[m].append(float(np.linalg.norm(rows[m])))
            n_prefixes += 1
    return {"b_m": {str(m): max(1e-8, float(np.median(norms[m]))) for m in (1, 2, 3)},
            "n_prefixes": n_prefixes, "n_items": min(len(items), max_items or len(items)),
            "quantiles": {str(m): np.quantile(norms[m], [0.05, 0.25, 0.5, 0.75, 0.95]).tolist() for m in (1, 2, 3)},
            "definition": "median raw residual norm at each bank site over cap-disabled development prefixes; floor 1e-8"}


def keys_for(base: BPBase, tok: GPT2Tokenizer, prompts: list[str]) -> dict[int, np.ndarray]:
    out = {1: [], 2: [], 3: []}
    for s in prompts:
        rows = _site_rows(base, tok.encode(s))
        for m in (1, 2, 3):
            out[m].append(key_feature(rows[m]))
    return {m: np.stack(v) for m, v in out.items()}


def calibrate_radii(edit_keys: dict, para_keys: dict, para_owner: np.ndarray, unrel_keys: dict) -> dict:
    """Per bank: candidate radii from a 20-quantile grid of observed distances; largest with
    unrelated false-fire ≤ 1%; ties by paraphrase coverage."""
    result = {}
    for m in (1, 2, 3):
        E, P, U = edit_keys[m], para_keys[m], unrel_keys[m]
        d_para = np.linalg.norm(P - E[para_owner], axis=1)  # paraphrase to its own edit key
        d_unrel = np.sqrt(((U[:, None, :] - E[None, :, :]) ** 2).sum(-1)).min(axis=1)  # nearest edit key
        grid = np.unique(np.quantile(np.concatenate([d_para, d_unrel]), np.linspace(0, 1, N_QUANTILES + 1)[1:]))
        cands = []
        for r in grid:
            ff = float((d_unrel <= r).mean())
            cov = float((d_para <= r).mean())
            cands.append({"radius": float(r), "false_fire": ff, "coverage": cov, "admissible": ff <= FALSE_FIRE_MAX})
        adm = [c for c in cands if c["admissible"] and c["radius"] > 0]
        if adm:
            best = max(adm, key=lambda c: (c["radius"], c["coverage"]))
            chosen = best["radius"]
            note = "largest admissible radius (false-fire <= 1%), ties by coverage"
        else:
            chosen = 0.0
            note = "no positive radius meets the 1% false-fire criterion: exact-key pilot (CR-4 interpretation; RET-GS still scores paraphrases)"
        result[str(m)] = {"radius": chosen, "note": note, "candidates": cands,
                          "d_para_quantiles": np.quantile(d_para, [0.05, 0.5, 0.95]).tolist(),
                          "d_unrel_quantiles": np.quantile(d_unrel, [0.05, 0.5, 0.95]).tolist(),
                          "n_para": int(len(d_para)), "n_unrel": int(len(d_unrel)), "n_edits": int(len(E))}
    return result


def run(datasets=("zsre", "counterfact"), max_unrelated: int = 1000) -> dict:
    from pccap.harness.lease import gpu_lease

    OUT.mkdir(parents=True, exist_ok=True)
    tok = GPT2Tokenizer()
    with gpu_lease("S2-01", stage="S2", projected_seconds=1800) as lease:
        base = BPBase()
        scales = {}
        radii = {}
        for ds in datasets:
            man = json.loads((DEV / f"{ds}_dev.json").read_text())
            items = man["items"]
            scales[ds] = residual_scales(base, items)
            edit_prompts = [it["prompt"] for it in items]
            para_prompts, owner = [], []
            for i, it in enumerate(items):
                for p in it["paraphrases"]:
                    para_prompts.append(p)
                    owner.append(i)
            unrel = man["unrelated_prompts"][:max_unrelated]
            ek = keys_for(base, tok, edit_prompts)
            pk = keys_for(base, tok, para_prompts)
            uk = keys_for(base, tok, unrel)
            radii[ds] = calibrate_radii(ek, pk, np.asarray(owner), uk)
            print(ds, "b_m", scales[ds]["b_m"], "radii", {m: radii[ds][m]["radius"] for m in radii[ds]}, flush=True)
        # pooled (both datasets): the shared calibration for a base/read variant
        pooled_b = {str(m): float(np.median([scales[ds]["b_m"][str(m)] for ds in datasets])) for m in (1, 2, 3)}
        pooled_r = {str(m): float(min(radii[ds][str(m)]["radius"] for ds in datasets)) for m in (1, 2, 3)}
        stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        (OUT / "residual_scales.json").write_text(json.dumps({"per_dataset": scales, "pooled_b_m": pooled_b, "base": "BP",
                                                              "read": "h", "timestamp": stamp, "lease": lease.report}, indent=1))
        (OUT / "radius_calibration.json").write_text(json.dumps({"per_dataset": radii, "pooled_radii_min_over_datasets": pooled_r,
                                                                 "false_fire_max": FALSE_FIRE_MAX, "grid": f"{N_QUANTILES}-quantile",
                                                                 "base": "BP", "read": "h", "timestamp": stamp,
                                                                 "ledger": base.ledger.totals()}, indent=1))
    return {"b_m": pooled_b, "radii": pooled_r}


if __name__ == "__main__":
    print(json.dumps(run(), indent=1))
