"""S1-06: P6 finite settling, cost and informativeness (PDF D.6; plan §6.7).

For each prompt (development edit prompts at the last position, current-target clamp = the gold
first answer token): ``E_0…E_64``, ``r_8``, ``r_64``, the first iteration attaining 95% of the
reduction ``E_0 − E_64`` (only when positive), the 16-step diagnostic, the cosine between the
settled error and the adjoint (``−∂L/∂h``) at the three bank sites at 8 and 64 iterations, the
error–loss Spearman correlation across prompts (error norm at each site vs the token loss), actual
forward/reverse counts and runtime per call. Label: "settled" only if ``r_64 ≤ 1e-3`` and the
terminal energy change is small; otherwise "finite-iteration error credit".

Weights: BP teacher (the ePC rows proper wait for REG-03; the coverage matrix marks them pending).

    python -m pccap.analysis.s1_p6 --n 64     # GPU lease
→ results/S1/P6_bp.json and results/S1/coverage.json (P6 row).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from pccap.bases import gpt2_jax as g
from pccap.bases.epc import EPCBase
from pccap.contracts import SiteId, metric
from pccap.data.tokenize import GPT2Tokenizer
from pccap.harness.ledger import Ledger

ROOT = Path(__file__).resolve().parents[3]
DEV = ROOT / "manifests" / "dev"
S1 = ROOT / "results" / "S1"
HORIZONS = (8, 16, 64)


def prompts_from_dev(n: int, seed: int = 31) -> list[tuple[np.ndarray, int, str]]:
    out = []
    for ds in ("zsre", "counterfact"):
        man = json.loads((DEV / f"{ds}_dev.json").read_text())
        rng = np.random.default_rng(seed)
        for i in rng.permutation(len(man["items"]))[: n // 2]:
            it = man["items"][i]
            out.append((np.asarray(it["prompt_ids"], np.int32), int(it["answer_ids"][0]), it["item_id"]))
    return out


def cos(a, b) -> float | None:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return None
    return float(np.dot(a, b) / (na * nb))


def update_coverage(rows: dict) -> None:
    p = S1 / "coverage.json"
    cov = json.loads(p.read_text()) if p.exists() else {}
    cov.update(rows)
    p.write_text(json.dumps(cov, indent=1))


def run(n: int = 64, weights_label: str = "bp_teacher") -> dict:
    from pccap.harness.lease import gpu_lease

    S1.mkdir(parents=True, exist_ok=True)
    tok = GPT2Tokenizer()  # noqa: F841  (kept for prompt decoding in records)
    with gpu_lease("S1-06", stage="S1", projected_seconds=3600) as lease:
        ledger = Ledger()
        base = EPCBase(ledger=ledger)
        rows = []
        for ids, target, iid in prompts_from_dev(n):
            p = len(ids) - 1
            t0 = time.perf_counter()
            er64 = base.infer_errors(ids, target, iters=64)
            dt64 = time.perf_counter() - t0
            t0 = time.perf_counter()
            er8 = base.infer_errors(ids, target, iters=8)
            dt8 = time.perf_counter() - t0
            er16 = base.infer_errors(ids, target, iters=16)
            E = np.asarray(er64.energies)
            red = E[0] - E[-1]
            first95 = None
            if red > 0:
                hit = np.flatnonzero((E[0] - E) >= 0.95 * red)
                first95 = int(hit[0]) if hit.size else None
            grads, L, _ = base.adjoint(ids, target, [], return_loss=True)
            site_cos = {}
            err_norms = {}
            for m in (1, 2, 3):
                site = SiteId(m, g.BANK_BLOCK[m], p)
                adj = -np.asarray(grads[site], np.float64)
                e8 = np.asarray(base.error_at_site(er8, m), np.float64)
                e64 = np.asarray(base.error_at_site(er64, m), np.float64)
                site_cos[str(m)] = {"cos_e8_negadj": cos(e8, adj), "cos_e64_negadj": cos(e64, adj), "cos_e8_e64": cos(e8, e64)}
                err_norms[str(m)] = {"e8": float(np.linalg.norm(e8)), "e64": float(np.linalg.norm(e64))}
            rows.append({"item_id": iid, "n_tokens": int(len(ids)), "loss": L, "E": E.tolist(), "E0": float(E[0]), "E8": float(E[8]),
                         "E16": float(er16.energies[-1]), "E64": float(E[-1]), "r_8": er8.r_k, "r_16": er16.r_k, "r_64": er64.r_k,
                         "first_iter_95pct": first95, "terminal_change_E63_to_E64": float(E[-2] - E[-1]) if len(E) > 1 else None,
                         "cos": site_cos, "err_norms": err_norms, "seconds_8": dt8, "seconds_64": dt64,
                         "reverses_8": er8.cost.reverses, "reverses_64": er64.cost.reverses})
        # aggregates
        r64 = np.asarray([r["r_64"] for r in rows])
        settled = bool(np.all(r64 <= 1e-3) and np.all(np.abs([r["terminal_change_E63_to_E64"] for r in rows]) <= 1e-3 * np.asarray([r["E0"] for r in rows])))
        label = "settled" if settled else "finite-iteration error credit"
        losses = np.asarray([r["loss"] for r in rows])
        spearman = {}
        for m in ("1", "2", "3"):
            for k in ("e8", "e64"):
                x = np.asarray([r["err_norms"][m][k] for r in rows])
                if np.ptp(x) == 0 or np.ptp(losses) == 0:
                    spearman[f"bank{m}_{k}"] = metric(None, units="spearman", status="undefined", n=len(rows), exclusions=["constant vector"])
                else:
                    rho = float(spearmanr(x, losses).statistic)
                    spearman[f"bank{m}_{k}"] = metric(rho, units="spearman", n=len(rows))
        cosines = {m: {k: metric(float(np.mean([r["cos"][m][k] for r in rows if r["cos"][m][k] is not None])), units="cosine", n=len(rows))
                       for k in ("cos_e8_negadj", "cos_e64_negadj", "cos_e8_e64")} for m in ("1", "2", "3")}
        out = {
            "stage": "S1", "property": "P6", "base": "EPC-wrapper on BP weights", "weights": weights_label, "metrics": {
                "r_8_mean": metric(float(np.mean([r["r_8"] for r in rows])), units="ratio", n=len(rows)),
                "r_64_mean": metric(float(np.mean(r64)), units="ratio", n=len(rows)),
                "r_64_max": metric(float(np.max(r64)), units="ratio", n=len(rows)),
                "E0_minus_E64_mean": metric(float(np.mean([r["E0"] - r["E64"] for r in rows])), units="nats", n=len(rows)),
                "first_iter_95pct_median": metric(float(np.median([r["first_iter_95pct"] for r in rows if r["first_iter_95pct"] is not None])) if any(r["first_iter_95pct"] is not None for r in rows) else None,
                                                  units="iterations", n=sum(r["first_iter_95pct"] is not None for r in rows),
                                                  status="ok" if any(r["first_iter_95pct"] is not None for r in rows) else "undefined"),
                "seconds_per_call_8": metric(float(np.mean([r["seconds_8"] for r in rows])), units="s", n=len(rows)),
                "seconds_per_call_64": metric(float(np.mean([r["seconds_64"] for r in rows])), units="s", n=len(rows)),
                "reverses_per_call_8": metric(float(np.mean([r["reverses_8"] for r in rows])), units="count", n=len(rows)),
                **{f"spearman_{k}": v for k, v in spearman.items()},
                **{f"cos_bank{m}_{k}": v for m in cosines for k, v in cosines[m].items()},
            },
            "label": label, "settled_criterion": "r_64 <= 1e-3 for every prompt and |E63 - E64| <= 1e-3 * E0",
            "solver": rows and base.infer_errors(prompts_from_dev(2)[0][0], prompts_from_dev(2)[0][1], iters=1).solver,
            "inherited_claim_check": {"claim": "cos(settled error, adjoint) > 0.998 (PDF §2.2, ref [5])",
                                      "note": "measured on BP weights with the declared solver; ePC checkpoint rows pending REG-03"},
            "rows": rows, "lease": lease.report, "ledger": ledger.totals(), "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    (S1 / "P6_bp.json").write_text(json.dumps(out, indent=1, default=float))
    update_coverage({"P6": {"bp_adjoint": "complete", "epc_adjoint": "pending (REG-03)", "epc_error": "pending (REG-03); procedure measured on BP weights: results/S1/P6_bp.json"}})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=64)
    args = ap.parse_args(argv)
    out = run(args.n)
    print(json.dumps({k: v for k, v in out["metrics"].items() if k.startswith(("r_", "E0", "first", "seconds", "cos_bank3"))}, indent=1, default=float))
    print("label:", out["label"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
