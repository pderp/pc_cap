"""DEC-075 operation-budget adjoint runner. CPU plan; owner-controlled GPU use."""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import json
import math
from pathlib import Path

from aw import pc_random_run, pc_v0
from aw.pc_historical import Sources, bind, sha
from aw.pc_matched_credit import TREATMENT, MatchedCreditCap, units
from pccap.harness.records import append_jsonl

ARMS = ("SE-A", "SE-AM")
OUTPUT = pc_v0.OUTPUT / "matched-control"
REFERENCE = pc_v0.OUTPUT / "replication-60-20260927"
PROFILE = pc_v0.OUTPUT / "dev-profile-20260927"


def settings(arm, credit_iters=8, error_lr=0.1):
    if arm not in ARMS or credit_iters != 8 or error_lr != 0.1:
        raise ValueError("matched control requires SE-A/SE-AM, k=8/rate=0.1 reference")
    return dict(
        pc_v0.settings("SE-A"),
        control_treatment=dict(
            TREATMENT,
            arm=arm,
            credit="adjoint-matched" if arm == "SE-AM" else "adjoint",
            role="additional_updates" if arm == "SE-AM" else "adjoint_control",
        ),
    )


def sources():
    result = pc_v0.source_identities()
    for name in (
        "aw/pc_matched_run.py",
        "aw/pc_matched_credit.py",
        "aw/pc_random_run.py",
        "aw/pc_random_credit.py",
        "aw/pc_historical.py",
    ):
        result[name] = sha(pc_v0.ROOT / name)
    return result


def reference(dataset, realization, population):
    root = PROFILE if population == "development" else REFERENCE
    folder = root / f"{dataset}-r{realization}-o100-SE-E"
    evidence = Sources()
    records = {}
    for name in ("plan.json",):
        evidence.bindings[str(root / name)] = sha(root / name)
    for name in ("config.json", "finish.json", "items.jsonl"):
        evidence.bindings[str(folder / name)] = sha(folder / name)
    cfg = json.loads((folder / "config.json").read_bytes())
    finish = json.loads((folder / "finish.json").read_bytes())
    plan = json.loads((root / "plan.json").read_bytes())
    expected_population = (
        "development"
        if population == "development"
        else "exposed historical S5; supplemental defect-correction replication"
    )
    if (
        finish["status"] != "complete"
        or finish["items_completed"] != cfg["items"]
        or cfg["population"] != expected_population
        or cfg["arm"] != "SE-E"
        or cfg["sources"] != plan["sources"]
        or cfg["credit_iters"] != 8
        or cfg["error_lr"] != 0.1
        or cfg["sources"] != evidence.module("pc_v0").source_identities()
    ):
        raise ValueError("wrong or incomplete bound eight-step reference")
    evidence.check(cfg["sources"])
    rows = [json.loads(line) for line in (folder / "items.jsonl").read_text().splitlines()]
    if [r["item_id"] for r in rows] != cfg["item_ids"] or len(rows) != cfg["items"]:
        raise ValueError("reference item order/count differs")
    for i, row in enumerate(rows):
        cost = row["cost"]
        if (
            row["index"] != i
            or cost["settle_iters"] % 8
            or cost["reverses"] != 9 * (cost["settle_iters"] // 8)
        ):
            raise ValueError("reference operation accounting differs")
        records[row["item_id"]] = units(cost)
    evidence.verify_unchanged()
    return cfg, records, evidence.bindings


def design(profile=False, items=10):
    if profile and items != 10:
        raise ValueError("profile must reuse the completed ten-item reference")
    return bind(pc_random_run.design, ARMS=ARMS)(profile, items)


def plan(profile=False, items=10):
    cells = design(profile, items)
    refs = {}
    for c in cells[::2]:
        _, _, bindings = reference(
            c["dataset"], c["realization"], "development" if profile else "replication"
        )
        refs.update(bindings)
    return dict(
        population="development" if profile else "exposed S5",
        cells=cells,
        credit={a: settings(a) for a in ARMS},
        control_treatment=TREATMENT,
        reference_sources_sha256=refs,
        sources=sources(),
        model_execution=False,
        claim="exploratory DEC-075 useful-update budget control; not new confirmation",
    )


new_output = bind(pc_random_run.new_output, OUTPUT=OUTPUT)


def cell(args):
    reference_cfg, allowances, bindings = reference(args.dataset, args.realization, args.population)
    expected = sources()

    def construct(base, dataset, arm, seed, frozen=None, *, credit_iters=8):
        ordinary = pc_v0.build_cap(base, dataset, "SE-A", seed, frozen)
        if ordinary.state_hash() != reference_cfg["initial_state"]:
            raise ValueError("control/reference fresh state or calibration differs")
        return (
            ordinary
            if arm == "SE-A"
            else MatchedCreditCap(base, ordinary.cfg, base.ledger, allowances=allowances)
        )

    def inputs(*a, **kw):
        loaded = pc_v0.load_inputs(*a, **kw)
        if [it.item_id for it in loaded[0]] != reference_cfg["item_ids"]:
            raise ValueError("control/reference item order differs")
        return loaded

    def stream(cap, items, router, budget, ev, out, ledger, **kw):
        if isinstance(cap, MatchedCreditCap):
            cap.router_seed = kw.get("seed", 0)
            cap.on_decision = lambda row: append_jsonl(Path(out) / "decisions.jsonl", row)
            cap.on_budget = lambda row: append_jsonl(Path(out) / "operation-budgets.jsonl", row)
        return pc_v0.run_stream(cap, items, router, budget, ev, out, ledger, **kw)

    def treatment(*a, **kw):
        return dict(settings(*a, **kw), reference_sources_sha256=bindings)

    execute = bind(
        pc_v0.run_cell,
        settings=treatment,
        build_cap=construct,
        load_inputs=inputs,
        run_stream=stream,
        source_identities=sources,
        _new_output=new_output,
    )
    result = execute(args)
    if sources() != expected or any(sha(path) != h for path, h in bindings.items()):
        raise RuntimeError("matched control inputs changed during execution")
    return result


group = bind(
    pc_random_run.group,
    new_output=new_output,
    plan=plan,
    sources=sources,
    MODULE="aw.pc_matched_run",
)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("plan", "profile", "run", "cell"))
    p.add_argument("--execute", action="store_true")
    p.add_argument("--output")
    p.add_argument("--dataset", choices=("zsre", "counterfact"), default="zsre")
    p.add_argument("--realization", type=int, choices=range(3), default=0)
    p.add_argument("--order", type=int, choices=(100,), default=100)
    p.add_argument("--arm", choices=ARMS, default="SE-AM")
    p.add_argument("--population", choices=("development", "replication"), default="replication")
    p.add_argument("--items", type=int, default=10)
    p.add_argument("--wall-seconds", type=float, default=28800)
    a = p.parse_args()
    a.credit_iters, a.error_lr, a.diagnostic = 8, 0.1, False
    if not math.isfinite(a.wall_seconds) or a.wall_seconds <= 0 or a.items < 1:
        p.error("positive finite allowance and item count required")
    if a.command == "plan":
        print(json.dumps(plan(), indent=2))
    else:
        if not a.execute or not a.output:
            p.error("--execute and a new --output required")
        if a.command == "cell":
            expected = 10 if a.population == "development" else 1000 if a.dataset == "zsre" else 300
            if a.items != expected:
                p.error("complete bound reference stream required")
            cell(a)
        else:
            group(a)


if __name__ == "__main__":
    main()
