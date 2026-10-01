"""Qualify the closed random-direction and completed offered-budget controls."""

from __future__ import annotations

import statistics
from pathlib import Path

from aw.pc_control_report import read, read_lines, table, verify
from aw.pc_historical import ROOT, sha

MATCHED = ROOT / "logs/additional_work/PC-v0/matched-report-20261001/report.json"
RANDOM = ROOT / "results/additional_work/PC-v0/random-control/run-20260929"


def build(evidence):
    refs = evidence.bindings
    matched = read(MATCHED, refs)
    evidence.check(matched["sources_sha256"])
    means = []
    for ds in ("zsre", "counterfact"):
        for arm in ("SE-A", "SE-AM"):
            cells = [c for c in matched["cells"] if c["dataset"] == ds and c["arm"] == arm]
            if len(cells) != 3:
                raise ValueError("three completed realizations per arm required")
            means.append(
                dict(
                    dataset=ds,
                    arm=arm,
                    metrics={
                        k: statistics.mean(c["metrics"][k] for c in cells)
                        for k in cells[0]["metrics"]
                    },
                    learning={
                        k: statistics.mean(c["finish"]["ledger"]["learning"][k] for c in cells)
                        for k in ("full_forwards", "partial_forwards", "reverses", "wall_seconds")
                    },
                    budget=[c["budget"] for c in cells] if arm == "SE-AM" else None,
                )
            )
    plan = read(RANDOM / "plan.json", refs)
    summary = read(RANDOM / "summary.json", refs)
    evidence.check(plan["sources"])
    if len(plan["cells"]) != 12 or len(summary["finished"]) != 2 or summary["complete"]:
        raise ValueError("random run is not the expected stopped first pair")
    rows, configs, item_rows = [], [], []
    for arm in ("SE-A", "SE-R"):
        folder = RANDOM / ("zsre-r0-o100-" + arm)
        cfg, finish, metrics = (
            read(folder / name, refs) for name in ("config.json", "finish.json", "metrics.json")
        )
        items = read_lines(folder / "items.jsonl", refs)
        for binding in (dict(path=cfg["manifest"], sha256=cfg["manifest_sha256"]), cfg["drift"]):
            verify(binding["path"], binding["sha256"], refs)
        n = len(items)
        if (
            cfg["sources"] != plan["sources"]
            or finish["base_hash_before"] != finish["base_hash_after"]
            or cfg["base_hash_before"] != finish["base_hash_before"]
            or cfg["control_treatment"] != finish["control_treatment"]
            or [i["item_id"] for i in items] != cfg["item_ids"][:n]
            or metrics["items_completed"] != n
            or finish["items_completed"] != n
            or metrics["status"] != finish["status"]
        ):
            raise ValueError("random partial record/identity mismatch")
        value = statistics.mean(i["es"] for i in items)
        if metrics["metrics"]["es_immediate"]["value"] != value:
            raise ValueError("random immediate success does not reproduce")
        rows.append(
            dict(
                arm=arm,
                n=n,
                status=finish["status"],
                es=value,
                process_seconds=finish["elapsed_process_seconds"],
                ledger=finish["ledger"],
                partial_metrics=metrics["metrics"],
            )
        )
        configs.append(cfg)
        item_rows.append(items)
    if [(c["status"], c["n"]) for c in rows] != [("complete", 1000), ("resource_stop", 993)]:
        raise ValueError("stopped random experiment differs")
    for key in (
        "weights_sha256",
        "manifest_sha256",
        "item_ids",
        "named_seeds",
        "base_hash_before",
        "locality_prompts_sha256",
        "drift",
    ):
        if configs[0][key] != configs[1][key]:
            raise ValueError("random paired identity differs: " + key)
    refs[str(Path(__file__).resolve())] = sha(__file__)
    return dict(
        matched=matched,
        matched_means=means,
        random=rows,
        common_prefix_es=[statistics.mean(i["es"] for i in items[:993]) for items in item_rows],
        unstarted_cells=10,
        uncompleted_random_items=7,
        harm_status="no separate PC-12 full-vector harm readout supplied; native drift retained, not substituted for ES99",
    )


def render(r):
    text = "\n## Direction and offered-budget controls (DEC-075/079)\n\n"
    text += "The random-direction run is **closed by resource rule**, not a complete 12-cell experiment. Only its first zsRE realization-0/order-100 pair was attempted: adjoint completed 1,000 items; random credit stopped after 993. The planned group contains ten unstarted cells (five remaining pairs), not eleven. These partial observations are not pooled with the complete depth comparisons.\n\n"
    text += table(
        [
            "Arm",
            "Status",
            "Items",
            "Immediate ES",
            "Process seconds",
            "Total forwards",
            "Total reverses",
        ],
        [
            [
                c["arm"],
                c["status"],
                c["n"],
                c["es"],
                c["process_seconds"],
                c["ledger"]["total"]["full_forwards"],
                c["ledger"]["total"]["reverses"],
            ]
            for c in r["random"]
        ],
    )
    text += f"\nOn the common first 993 items, immediate ES is {r['common_prefix_es'][0]:.6f} for adjoint and {r['common_prefix_es'][1]:.6f} for random credit. Three random-arm immediate answers succeed; even all seven remaining answers succeeding would give only 0.010 over 1,000 items. That bound concerns immediate ES, not the unobserved final memory or retention. Random credit retains the true eight-step credit's norm and pays for its calculation before replacing the direction. This one stream supports the practical importance of informative credit in this implementation; it does not establish a general impossibility result for random search or a PC advantage over adjoint.\n\n"
    text += "The additional-update adjoint control completed all twelve cells (six pairs). The PC arm's budget was **offered, not consumed**. Per-item operation counts include forwards, partial forwards and reverses; they are not FLOPs. Most records hit the stopping thresholds without spending the allowance, and some incomplete rounds roll back while their compute remains charged.\n\n"
    text += table(
        [
            "Dataset",
            "Arm",
            "ES",
            "RET-ES",
            "RET-GS",
            "LS",
            "Learning forwards",
            "Learning reverses",
            "Learning seconds",
        ],
        [
            [
                c["dataset"],
                c["arm"],
                *c["metrics"].values(),
                c["learning"]["full_forwards"],
                c["learning"]["reverses"],
                c["learning"]["wall_seconds"],
            ]
            for c in r["matched_means"]
        ],
    )
    text += "\n" + table(
        [
            "Dataset",
            "r",
            "Offered ops",
            "Used ops",
            "Fraction used",
            "Threshold stops",
            "Incomplete rollbacks",
        ],
        [
            [
                c["dataset"],
                c["realization"],
                c["budget"]["offered"],
                c["budget"]["used"],
                c["budget"]["used"] / c["budget"]["offered"],
                c["budget"]["threshold_stops"],
                c["budget"]["incomplete_round_rollbacks"],
            ]
            for c in r["matched"]["cells"]
            if "budget" in c
        ],
    )
    text += "\nThe control does not recover the eight-step own-prompt retention gain, but also does not spend an equal measured compute budget. Its stopping logic/prefix traversal differ; the small behavior changes cannot be attributed to extra updates alone. These results leave **direction versus extra effective compute unresolved**. CounterFact's saturated own-prompt and zero paraphrase scores limit discrimination. Exact per-realization differences and process/operation costs are in `PC-matched-control_report.md`. Separate full-vector PC-12 harm curves were not supplied; native drift summaries are available but cannot fill an ES99 slot.\n"
    return text
