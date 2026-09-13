"""S8-02: the fixed exploratory ablations (D3 memo §6.4), development mode, three realizations × two orders each,
labelled exploratory. GPU lease per ablation.

(b) fixed-byte memory at half and double the reference for C1 and C2 on zsRE (300 development edits per run);
(c) the grammar with paraphrase keys at a positive radius calibrated at 5% false-fire (C1, C2, CR; 128 sequences per run);
(a) cap-disabled stable keys vs edited keys is NOT run (needs the optional read variant R-h0, CAP-08, not implemented).

    python scripts/s8_02_ablations.py [--which b,c] → results/S8/ablations/<name>/…, results/S8/ablations.json"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "S8" / "ablations"
REALIZATIONS = (0, 1, 2)
ORDERS = (0, 1)


def _order(items, realization, order):
    rng = np.random.default_rng(10_000 + 100 * realization + order)
    return [items[i] for i in rng.permutation(len(items))]


def run_b(frozen) -> list[dict]:
    from pccap.bases.bp import BPBase
    from pccap.cap.cap import Cap, CapConfig
    from pccap.contracts import Budget
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.arms import router_for
    from pccap.harness.ledger import Ledger
    from pccap.harness.runs import Evaluator, run_stream
    from pccap.harness.stage_s2 import load_dev_items
    from pccap.harness.stage_s3 import drift_sample

    rows = []
    budget = Budget(A=float(frozen["A"]), epsilon=float(frozen["epsilon"]), R=int(frozen["R"]), tau_edit=float(frozen["tau_edit"]))
    radii = {int(k): float(v) for k, v in frozen["radii"]["bank"]["zsre"].items()}
    b_m = {int(k): float(v) for k, v in frozen["b_m"].items()}
    for factor in (0.5, 1.0, 2.0):
        for arm in ("C1", "C2"):
            for r in REALIZATIONS:
                items, unrelated = load_dev_items("zsre", 300, seed=41 + r)
                for o in ORDERS:
                    rd = OUT / "b_byte_ceiling" / f"x{factor}" / arm / f"r{r}" / f"o{o}"
                    if (rd / "metrics.json").exists():  # a finished run is reused, never recomputed
                        m = json.loads((rd / "metrics.json").read_text())
                        accel = m["ledger_totals"]["total"]["accel_seconds"]
                    else:
                        ledger = Ledger()
                        base = BPBase(ledger=ledger)
                        tok = GPT2Tokenizer()
                        cap = Cap(base, CapConfig(arm=arm, read=frozen["radii"]["read"], radii=radii, bank_scales=b_m, seed=1000 * r + 10 * o, d=base.d, ceiling_factor=factor), ledger)
                        ev = Evaluator(base, tok, unrelated[:200], drift_sample(4096))
                        m = run_stream(cap, _order(items, r, o), router_for(arm, cr_distribution=None), budget, ev, rd, ledger, checkpoints=(100,), seed=1000 * r + 10 * o + 1, arm=arm)
                        accel = ledger.totals()["total"]["accel_seconds"]
                    k = m["metrics"]
                    rows.append({"ablation": "b_byte_ceiling", "factor": factor, "arm": arm, "realization": r, "order": o, "items": m["items_completed"],
                                 "es": k["es_immediate"]["value"], "ret_es": k["ret_es_end"]["value"], "ret_gs": k["ret_gs_end"]["value"], "ls": k["ls_complete_answer_end"]["value"],
                                 "occupied_bytes": k["memory_occupied_bytes"]["value"], "accel_s": accel})
                    print(json.dumps(rows[-1]), flush=True)
    return rows


def run_c(frozen) -> list[dict]:
    from pccap.cap.calibrate import calibrate_radii, residual_scales
    from pccap.cap.features import z as zfeat
    from pccap.contracts import Budget
    from pccap.data import grammar_streams as gs
    from pccap.fixtures.grammar_eval import (
        Grammar,
        GrammarTokenizer,
        grammar_context,
        locality_prefixes,
        with_paraphrases,
    )
    from pccap.fixtures.grammar_generator import CONTEXTS
    from pccap.fixtures.grammar_model import WEIGHTS, GrammarBase
    from pccap.harness.arms import make_learner, router_for
    from pccap.harness.ledger import Ledger
    from pccap.harness.runs import Evaluator, run_stream

    # 5% false-fire calibration (the frozen criterion is 1%, under which no positive radius exists for the grammar, SD-20)
    base0 = GrammarBase(weights=WEIGHTS)
    g = Grammar()
    items = with_paraphrases([it for t in range(CONTEXTS) for it in gs.load_task_items(t, 0, 300 // CONTEXTS, g)], g)
    tok = GrammarTokenizer()

    def keys_for(prefixes):
        out = {1: [], 2: [], 3: []}
        for k in range(0, len(prefixes), 64):
            _, rws, _, _ = base0.forward_batch(prefixes[k: k + 64], None, phase="query")
            rws = np.asarray(rws)
            for m in (1, 2, 3):
                out[m].append(np.asarray(zfeat(rws[:, m - 1])))
        return {m: np.concatenate(v) for m, v in out.items()}

    ek = keys_for([it.prompt_ids for it in items])
    para, owner = [], []
    for i, it in enumerate(items):
        for p in it.paraphrases:
            para.append(np.asarray(tok.encode(p), np.int32))
            owner.append(i)
    pk = keys_for(para)
    uk = keys_for(locality_prefixes(1000, g=g))
    cal5 = calibrate_radii(ek, pk, np.asarray(owner), uk, false_fire_max=0.05)
    radii5 = {m: float(cal5[str(m)]["radius"]) for m in (1, 2, 3)}
    scales = residual_scales(base0, [{"prompt_ids": it.prompt_ids.tolist(), "answer_ids": it.answer_ids.tolist(), "prompt": it.prompt} for it in items])
    b_m = {int(m): float(v) for m, v in scales["b_m"].items()}
    (OUT / "c_grammar_radius5").mkdir(parents=True, exist_ok=True)
    (OUT / "c_grammar_radius5" / "calibration_5pct.json").write_text(json.dumps({"false_fire_max": 0.05, "radii": radii5, "per_bank": cal5, "b_m": b_m}, indent=1, default=float))
    print("5% radii", radii5, "notes", {m: cal5[str(m)].get("note") for m in (1, 2, 3)})
    rows = []
    budget = Budget(A=float(frozen["A"]), epsilon=float(frozen["epsilon"]), R=int(frozen["R"]), tau_edit=float(frozen["tau_edit"]))
    for label, radii in (("radius_5pct", radii5), ("exact_keys_frozen", {1: 0.0, 2: 0.0, 3: 0.0})):
        for arm in ("C1", "C2", "CR"):
            for r in REALIZATIONS:
                for o in ORDERS:
                    ledger = Ledger()
                    gc = grammar_context(r, o, 16, ledger=ledger)
                    learner = make_learner(arm, gc["base"], ledger, radii=radii, bank_scales=b_m, read="h", seed=1000 * r + 10 * o)
                    ev = Evaluator(gc["base"], gc["tok"], gc["unrelated"], gc["drift"], drift_positions=len(gc["drift"]), drift_window=gc["drift_window"], max_new=1)
                    rd = OUT / "c_grammar_radius5" / label / arm / f"r{r}" / f"o{o}"
                    m = run_stream(learner, gc["items"], router_for(arm, cr_distribution=None), budget, ev, rd, ledger, checkpoints=(64,), seed=1000 * r + 10 * o + 1, arm=arm)
                    k = m["metrics"]
                    rows.append({"ablation": "c_grammar_radius5", "keys": label, "arm": arm, "realization": r, "order": o, "items": m["items_completed"],
                                 "es": k["es_immediate"]["value"], "ret_es": k["ret_es_end"]["value"], "ret_gs": k["ret_gs_end"]["value"], "ls": k["ls_complete_answer_end"]["value"],
                                 "accel_s": ledger.totals()["total"]["accel_seconds"]})
                    print(json.dumps(rows[-1]), flush=True)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--which", default="b,c")
    args = ap.parse_args()
    import pccap  # noqa: F401
    from pccap.harness.lease import gpu_lease

    frozen = json.loads((ROOT / "manifests" / "frozen.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    t0 = time.time()
    with gpu_lease("S8:ablations", stage="S8", projected_seconds=4 * 3600.0):
        if "b" in args.which.split(","):
            rows += run_b(frozen)
        if "c" in args.which.split(","):
            rows += run_c(frozen)
    out = {"label": "S8-02 exploratory ablations (development data; 3 realizations × 2 orders; not confirmatory)", "written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "list_fixed_in": "docs/D3_decision.md §6.4", "not_run": {"a_stable_keys": "needs the optional read variant R-h0 (CAP-08), not implemented this month"},
           "rows": rows, "wall_seconds": time.time() - t0}
    (ROOT / "results" / "S8" / "ablations.json").write_text(json.dumps(out, indent=1, default=float))
    print("wall", round(out["wall_seconds"]), "s; rows", len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
