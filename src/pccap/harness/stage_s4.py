"""Stage S4 runner: one confirmatory stream through ``pccap run --stage S4 --mode confirm`` (plan §6.10
S4-04; PDF S4, D.8, D.11). The runner is registered like S0/S3 and:

* refuses unless ``manifests/frozen.json`` exists (the CLI already checks; §4.5 rule 4) and reads
  the sealed realization manifest through ``pccap.data.confirm.load`` (DATA-02a) — the only reader;
* takes every numeric from the frozen manifest (radii per dataset, b_m, A, ε, R, τ_edit, CR
  distribution, LoRA lr/rank/steps, seeds by the manifest's named-seed rule), never from the
  development files;
* orders the items by the realization's committed order for ``--perm`` and runs ``run_stream`` with
  the frozen checkpoints; the base is hashed before and after (``assert_frozen``).
"""

from __future__ import annotations

import json
from pathlib import Path

from pccap.bases.bp import BPBase
from pccap.bases.checksum import assert_frozen
from pccap.contracts import Budget, EditItem
from pccap.data.tokenize import GPT2Tokenizer
from pccap.harness.arms import make_learner, router_for
from pccap.harness.ledger import Ledger
from pccap.harness.runner import RUNNERS
from pccap.harness.runs import Evaluator, run_stream
from pccap.harness.stage_s2 import load_dev_items
from pccap.harness.stage_s3 import drift_sample

ROOT = Path(__file__).resolve().parents[3]


def _items_from(records: list[dict]) -> list[EditItem]:
    out = []
    for r in records:
        out.append(EditItem(item_id=r["item_id"], digest=r.get("digest", ""), prompt=r["prompt"], answer=r["answer"], aliases=list(r.get("aliases", [])),
                            paraphrases=list(r.get("paraphrases", [])), locality_prompts=list(r.get("locality_prompts", [])),
                            prompt_ids=r["prompt_ids"], answer_ids=r["answer_ids"], dataset=r["dataset"], fact_id=r.get("fact_id", ""),
                            version=int(r.get("version", 0)), revision=None, strata={"answer_tokens": int(r.get("answer_tokens", len(r["answer_ids"])))}))
    return out


def run_s4(ctx: dict, run_dir: Path) -> dict:
    from pccap.data.confirm import load as load_confirm

    cfg = ctx["config"]
    frozen = json.loads((ROOT / "manifests" / "frozen.json").read_text())
    man = load_confirm(Path(cfg["manifest"]), frozen=ROOT / "manifests" / "frozen.json")
    ds, r, perm = man["dataset"], int(man["realization"]), int(cfg["perm"])
    oseed = frozen["order_seeds"][perm]
    seeds = man["named_seeds"][str(oseed)]
    by_id = {it["item_id"]: it for it in man["items"]}
    ordered = [by_id[i] for i in man["orders"][str(oseed)]]
    arm = cfg["arm"]
    n = frozen["stream_lengths"]["c0_initial"] if arm == "C0" else frozen["stream_lengths"][ds]
    items = _items_from(ordered[: int(n)])
    ledger = Ledger()
    base = BPBase(ledger=ledger)
    tok = GPT2Tokenizer()
    radii = {int(k): float(v) for k, v in frozen["radii"]["bank"][ds].items()}
    b_m = {int(k): float(v) for k, v in frozen["b_m"].items()}
    budget = Budget(A=float(frozen["A"]), epsilon=float(frozen["epsilon"]), R=int(frozen["R"]), tau_edit=float(frozen["tau_edit"]))
    learner_seed = int(seeds["seed_replay"] if arm == "B3" else seeds["seed_cap_init"])
    learner = make_learner(arm, base, ledger, radii=radii, bank_scales=b_m, read=frozen["radii"]["read"], seed=learner_seed,
                           lora_lr=float(frozen["lora"]["lr"]), lora_rank=int(frozen["lora"]["rank"]), lora_steps=int(frozen["lora"]["steps"]))
    cr = frozen["cr_distribution"].get(ds) if frozen.get("cr_distribution") else None
    router = router_for(arm, cr_distribution=cr, cr_label=frozen["cr_distribution"]["labels"].get(ds, "cr_frozen") if cr else "cr_profile_uniform")
    _, unrelated = load_dev_items(ds, 1, seed=int(seeds["seed_router"]))  # locality prompts come from the development unrelated pool (not confirmation items)
    h_before = base.checksum()
    ev = Evaluator(base, tok, unrelated[:200], drift_sample(4096))
    metrics = run_stream(learner, items, router, budget, ev, run_dir, ledger, checkpoints=tuple(frozen["checkpoints"]),
                         seed=int(seeds["seed_router"]), arm=arm)
    h_after = base.checksum()
    assert_frozen(h_before, h_after)
    metrics["base_hash_before"], metrics["base_hash_after"] = h_before, h_after
    metrics["config"] = {"dataset": ds, "realization": r, "perm": perm, "order_seed": oseed, "named_seeds": seeds, "n_items": len(items),
                         "frozen_sha256": ctx["config"].get("manifest_sha256"), "A": budget.A, "radii": radii, "b_m": b_m, "lora": frozen["lora"]}
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=1, default=float))
    return metrics


RUNNERS["S4"] = run_s4
