"""Stage S0 runner: the development smoke edit (S0-10) through ``pccap run --stage S0``.

Manifest fields (``manifests/dev/s0_smoke.json``): ``items`` = list of s0-sample item ids (or
``"s0_sample[0]"``), ``budget`` = {A, epsilon, R, tau_edit}, ``radii``, ``bank_scales``.
Writes ``decisions.jsonl``, ``metrics.json``, ``cost.json`` and ``config.json`` into the run
directory and the learner checkpoint to ``assets/runs/<same relative path>/learner.ckpt``
(DEC-004; path and hash recorded in ``metrics.json``). Base hash before and after (Op. rule 10).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from pccap import ASSETS_ROOT
from pccap.bases.bp import BPBase
from pccap.bases.checksum import assert_frozen
from pccap.cap.cap import Cap, CapConfig
from pccap.contracts import Budget, EditItem, metric
from pccap.data.decode import greedy_decode, score_generation, teacher_forced_nll
from pccap.data.tokenize import GPT2Tokenizer, tokenize_pair
from pccap.harness import runner
from pccap.harness.ledger import Ledger
from pccap.harness.records import append_jsonl
from pccap.harness.snapshot import save
from pccap.routers import make_router
from pccap.transport.transport import Transport

ROOT = Path(__file__).resolve().parents[3]


def load_items(spec, tok: GPT2Tokenizer) -> list[EditItem]:
    sample = json.loads((ROOT / "manifests" / "dev" / "s0_sample.json").read_text())
    by_id = {it["item_id"]: it for it in sample["items"]}
    ids = []
    for s in spec:
        if isinstance(s, str) and s.startswith("s0_sample["):
            ids.append(sample["items"][int(s[len("s0_sample[") : -1])]["item_id"])
        else:
            ids.append(s)
    out = []
    for iid in ids:
        it = by_id[iid]
        te = tokenize_pair(tok, it["prompt"], it["answer"])
        if te.excluded:
            continue
        out.append(EditItem(item_id=iid, digest=bytes.fromhex(it["digest"]), prompt=it["prompt"], answer=it["answer"],
                            aliases=it["aliases"], paraphrases=it["paraphrases"], locality_prompts=it["locality_prompts"],
                            prompt_ids=te.prompt_ids, answer_ids=te.answer_ids, dataset=it["dataset"], fact_id=it["fact_id"]))
    return out


def evaluate_item(cap: Cap, item: EditItem, tok: GPT2Tokenizer, phase: str = "query") -> dict:
    predict = lambda ids: cap.edited_forward(ids, phase=phase).logits  # noqa: E731
    dec = greedy_decode(predict, item.prompt_ids, tok, state_hash=cap.state_hash)
    es = score_generation(dec, item.aliases)
    nll = teacher_forced_nll(predict, item.prompt_ids, item.answer_ids)
    return {"generated": dec.text, "stopped_by": dec.stopped_by, "es": es, "teacher_forced_nll": nll}


@runner.register("S0")
def run_s0(ctx: dict, run_dir: Path) -> dict:
    cfg, manifest = ctx["config"], ctx["manifest"]
    ledger = Ledger()
    base = BPBase(ledger=ledger)
    tok = GPT2Tokenizer()
    b = manifest.get("budget", {})
    budget = Budget(A=b.get("A", 0.1), epsilon=b.get("epsilon", 0.01), R=b.get("R", 5), tau_edit=b.get("tau_edit", 0.1))
    radii = {int(k): float(v) for k, v in manifest.get("radii", {"1": 0.0, "2": 0.0, "3": 0.0}).items()}
    scales = {int(k): float(v) for k, v in manifest.get("bank_scales", {"1": 1.0, "2": 1.0, "3": 1.0}).items()}
    cap = Cap(base, CapConfig(arm=cfg["arm"], read=cfg["read"], radii=radii, bank_scales=scales, seed=manifest.get("seed", 0)), ledger)
    if cfg["arm"] == "C2":
        raise NotImplementedError("C2 needs the probe binding (S2/S3 harness); S0 smoke uses C0/C1/CR")
    router = make_router(cfg["arm"]) if cfg["arm"] != "C2" else None
    items = load_items(manifest.get("items", ["s0_sample[0]"]), tok)
    h_before = base.checksum()
    (run_dir / "config.json").write_text(json.dumps({**cfg, "base_hash_before": h_before}, indent=1))
    dec_path = run_dir / "decisions.jsonl"
    if dec_path.exists():
        dec_path.unlink()
    results = []
    for item in items:
        pre = evaluate_item(cap, item, tok)
        out = cap.update_item.__func__(cap, item, router, budget) if False else None  # placeholder (see below)
        from pccap.cap.learn import update_item

        out = update_item(cap, item, router, budget, Transport(), on_decision=lambda r: append_jsonl(dec_path, r),
                          seed=manifest.get("seed", 0))
        post = evaluate_item(cap, item, tok)
        results.append({"item_id": item.item_id, "outcome": out.code, "rounds": out.rounds_used,
                        "prefixes": out.prefix_outcomes, "es_before": pre["es"]["value"], "es_after": post["es"]["value"],
                        "generated_before": pre["generated"], "generated_after": post["generated"],
                        "nll_before": pre["teacher_forced_nll"]["value"], "nll_after": post["teacher_forced_nll"]["value"]})
    h_after = base.checksum()
    assert_frozen(h_before, h_after)
    n = len(results)
    acq = sum(r["outcome"] == "accepted" for r in results)
    es_after = sum(r["es_after"] or 0 for r in results)
    ckpt_dir = Path(ASSETS_ROOT) / "runs" / run_dir.relative_to(ROOT / "results")
    ckpt_sha = save(cap.export_state(), ckpt_dir / "learner.ckpt")
    mem_rep = cap.memory_bytes()
    metrics = {
        "stage": "S0", "arm": cfg["arm"], "base": cfg["base"],
        "metrics": {
            "threshold_acquisition": metric(acq / n if n else None, units="fraction", numerator=acq, denominator=n, n=n,
                                            status="ok" if n else "undefined"),
            "es_immediate": metric(es_after / n if n else None, units="fraction", numerator=es_after, denominator=n, n=n,
                                   status="ok" if n else "undefined"),
            "memory_occupied_bytes": metric(mem_rep.occupied_bytes, units="bytes", n=1),
            "memory_allocated_bytes": metric(mem_rep.allocated_bytes, units="bytes", n=1),
        },
        "items": results, "learner_ckpt": {"path": str(ckpt_dir / "learner.ckpt"), "sha256": ckpt_sha,
                                            "state_hash": cap.state_hash()},
        "memory": mem_rep.__dict__, "base_hash_before": h_before, "base_hash_after": h_after,
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=1, default=float))
    ledger.write(run_dir)
    return {"base_hash_before": h_before, "base_hash_after": h_after, "status": "complete"}
