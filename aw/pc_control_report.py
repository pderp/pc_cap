"""PC-12 CPU-only report for explicitly labelled random/useful-update controls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aw.pc_v0_report import METRICS, SECONDARY, read, sha, table, verify


def build(group, document, output):
    group, output, document = Path(group), Path(output), Path(document)
    refs = {}
    plan = read(group / "plan.json", refs)
    if plan["population"] != "exposed S5" or len(plan["cells"]) != 12:
        raise ValueError("complete 12-cell exposed control plan required")
    control = plan["control_treatment"]["arm"]
    if control not in ("SE-R", "SE-AM"):
        raise ValueError("explicit PC-12 control label required")
    expected = {
        (ds, r, 100, a)
        for ds in ("zsre", "counterfact")
        for r in range(3)
        for a in ("SE-A", control)
    }
    if {
        tuple(c[k] for k in ("dataset", "realization", "order", "arm")) for c in plan["cells"]
    } != expected:
        raise ValueError("control coordinate inventory differs")
    for name, h in plan["sources"].items():
        verify(name, h, refs)
    cells, indexed = [], {}
    for c in plan["cells"]:
        folder = group / f"{c['dataset']}-r{c['realization']}-o{c['order']}-{c['arm']}"
        cfg, finish = (read(folder / name, refs) for name in ("config.json", "finish.json"))
        if (
            any(cfg[k] != v for k, v in c.items())
            or cfg["sources"] != plan["sources"]
            or any(cfg[k] != v or finish.get(k) != v for k, v in plan["credit"][c["arm"]].items())
            or finish["status"] != "complete"
            or finish["items_completed"] != c["items"]
        ):
            raise ValueError("control plan/config/finish mismatch or incomplete cell")
        if (
            finish["base_hash_before"] != finish["base_hash_after"]
            or cfg["base_hash_before"] != finish["base_hash_before"]
        ):
            raise ValueError("control base changed")
        if cfg["control_treatment"]["role"] != (
            "adjoint_control"
            if c["arm"] == "SE-A"
            else "random_direction"
            if control == "SE-R"
            else "additional_updates"
        ):
            raise ValueError("control treatment label differs")
        verify(cfg["manifest"], cfg["manifest_sha256"], refs)
        verify(cfg["drift"]["path"], cfg["drift"]["sha256"], refs)
        for path, h in cfg.get("reference_sources_sha256", {}).items():
            verify(path, h, refs)
        items = read_lines(folder / "items.jsonl", refs)
        if [it["item_id"] for it in items] != cfg["item_ids"] or len(items) != c["items"]:
            raise ValueError("control item order/count differs")
        native = read(folder / "metrics.json", refs)
        if native["status"] != "complete" or native["items_completed"] != c["items"]:
            raise ValueError("incomplete control metrics")
        row = dict(
            c,
            metrics={label: native["metrics"][key]["value"] for label, key in METRICS.items()},
            secondary=read(folder / "secondary-summary.json", refs),
            finish=finish,
        )
        if c["arm"] == "SE-AM":
            budgets = read_lines(folder / "operation-budgets.jsonl", refs)
            if [b["item_id"] for b in budgets] != cfg["item_ids"] or any(
                b["used"] > b["allowance"] for b in budgets
            ):
                raise ValueError("matched allowance violation/coverage")
            row["budget"] = dict(
                offered=sum(b["allowance"] for b in budgets),
                used=sum(b["used"] for b in budgets),
                threshold_stops=sum(b["stop"] == "thresholds_attained" for b in budgets),
                incomplete_round_rollbacks=sum(b["rolled_back_incomplete_round"] for b in budgets),
            )
        cells.append(row)
        indexed[(c["dataset"], c["realization"], c["arm"])] = (row, cfg)
    pairs = []
    for ds in ("zsre", "counterfact"):
        for r in range(3):
            (a, ac), (e, ec) = (indexed[ds, r, arm] for arm in ("SE-A", control))
            for key in (
                "item_ids",
                "weights_sha256",
                "manifest_sha256",
                "named_seeds",
                "locality_prompts_sha256",
                "base_hash_before",
                "drift",
            ):
                if ac[key] != ec[key]:
                    raise ValueError("paired control inputs differ: " + key)
            pairs.append(
                dict(
                    dataset=ds,
                    realization=r,
                    difference={
                        k: None
                        if a["metrics"][k] is None or e["metrics"][k] is None
                        else e["metrics"][k] - a["metrics"][k]
                        for k in METRICS
                    },
                    secondary_difference={
                        k: None
                        if a["secondary"][k] is None or e["secondary"][k] is None
                        else e["secondary"][k] - a["secondary"][k]
                        for k in SECONDARY
                    },
                )
            )
    report = dict(
        schema="pc12-control-report-v1",
        treatment=plan["control_treatment"],
        cells=cells,
        pairs=pairs,
        sources_sha256=refs,
        population="exposed S5; exploratory DEC-075 control; one order, three realizations",
    )
    output.mkdir(parents=True, exist_ok=False)
    document.parent.mkdir(parents=True, exist_ok=True)
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    text = (
        f"# PC-12 {control} control\n\n"
        + report["population"]
        + f". Differences are {control} minus SE-A.\n\n"
    )
    text += "Treatment: `" + json.dumps(plan["control_treatment"], sort_keys=True) + "`.\n\n"
    text += table(
        ["Dataset", "Realization", *METRICS, *SECONDARY],
        [
            [
                p["dataset"],
                p["realization"],
                *p["difference"].values(),
                *p["secondary_difference"].values(),
            ]
            for p in pairs
        ],
    )
    text += table(
        [
            "Dataset",
            "Realization",
            "Arm",
            "Process seconds",
            "Forwards",
            "Partial forwards",
            "Reverses",
            "Settling",
        ],
        [
            [
                c["dataset"],
                c["realization"],
                c["arm"],
                c["finish"]["elapsed_process_seconds"],
                *[
                    c["finish"]["ledger"]["total"][k]
                    for k in ("full_forwards", "partial_forwards", "reverses", "settle_iters")
                ],
            ]
            for c in cells
        ],
    )
    text += "Three realizations, one order each; no independence or superiority claim from tokens. The matched arm has an equal offered operation allowance, not guaranteed equal realized spend or FLOPs. The random arm pays the true error-credit cost before replacing orientation. Separate ordinary-text harm is not inferred from efficacy.\n"
    if control == "SE-AM":
        text += "\n" + table(
            [
                "Dataset",
                "Realization",
                "Offered ops",
                "Used ops",
                "Threshold stops",
                "Incomplete round rollbacks",
            ],
            [
                [c["dataset"], c["realization"], *c["budget"].values()]
                for c in cells
                if "budget" in c
            ],
        )
    document.write_text(text)
    return report


def read_lines(path, refs):
    refs[str(path.resolve())] = sha(path)
    return [json.loads(line) for line in path.read_text().splitlines()]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", required=True)
    p.add_argument("--document", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    build(a.run, a.document, a.output)


if __name__ == "__main__":
    main()
