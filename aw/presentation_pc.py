"""Resolve PC slide slots from completed, identified research outputs only.

Missing sources remain PENDING. Smoke results and mismatched populations are
refused. This does not choose a positive/negative narrative from the outcomes.
"""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path

from aw.pc_v0_report import ROOT, compare, expected_cells, sha

REGISTER = ROOT / "docs/presentation/deck_v3/pc-result-sources.json"


def read(path, bindings):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    value = json.loads(path.read_bytes())
    bindings[str(path.resolve())] = sha(path)
    return value


def verify_sources(report, bindings):
    for name, identity in report.get("sources_sha256", {}).items():
        path = Path(name)
        if not path.is_absolute():
            path = ROOT / path
        if bindings.get(str(path)) != identity and sha(path) != identity:
            raise ValueError("PC presentation source differs: " + str(path))
        bindings[str(path)] = identity


def present(value):
    if value is None:
        return "UNAVAILABLE"
    if isinstance(value, list):
        return ", ".join(present(x) for x in value)
    if isinstance(value, (float, int)):
        return f"{value:.4g}"
    return str(value)


def v0_values(report, slots, bindings):
    if report.get("smoke"):
        raise ValueError("CPU smoke cannot populate PC result slides")
    if (
        report.get("expected_cells") != 60
        or len(report.get("cells", [])) != 60
        or any(c["status"] != "complete" for c in report["cells"])
    ):
        return "pending complete 60-cell report"
    _, pairs, aggregates = compare(report["cells"], expected_cells(5))
    if pairs != report["pairs"] or aggregates != report["aggregates"]:
        raise ValueError("PC-3 tables do not reproduce from reported cells")
    if any(not c.get("pair_identity") for c in report["cells"]):
        raise ValueError("PC-3 cells lack experimental identity")
    verify_sources(report, bindings)
    for row in aggregates:
        metric = {"ES": "es", "RET-ES": "ret_es", "RET-GS": "ret_gs", "LS": "ls"}.get(row["metric"])
        if metric:
            key = f"v0.{row['dataset']}.{metric}"
            slots[key] = present(row["mean"])
            slots[key + ".realizations"] = present(row["realizations"])
            slots[key + ".range"] = present([row["minimum"], row["maximum"]])
    for arm in ("SE-A", "SE-E"):
        cells = [c for c in report["cells"] if c["arm"] == arm]
        slots[f"v0.{arm}.seconds"] = present(
            sum(c["finish"]["elapsed_process_seconds"] for c in cells)
        )
        for counter in ("full_forwards", "reverses", "settle_iters"):
            slots[f"v0.{arm}.{counter}"] = present(
                sum(c["finish"]["ledger"]["total"][counter] for c in cells)
            )
    return "measured: completed exposed-S5 comparison"


def v1_values(directory, slots, bindings):
    from aw.pc_v1_run import POPULATION, cell_name, plan

    directory = Path(directory)
    p = read(directory / "plan.json", bindings)
    if p.get("population") != POPULATION:
        raise ValueError("fixed-v5 slide requires exposed realization-0 population")
    if p != plan(False):
        raise ValueError("fixed-v5 design/code differs from installed experiment")
    reports = {}
    identity = {}
    for c in p["cells"]:
        folder = directory / cell_name(c)
        if not (folder / "finish.json").exists():
            return "pending four completed fixed-v5 cells"
        f = read(folder / "finish.json", bindings)
        if (
            f["status"] != "complete"
            or f["items_completed"] != 300
            or f["checkpoints_completed"] != [100, 300]
        ):
            return "pending complete fixed-v5 endpoints"
        cfg = read(folder / "config.json", bindings)
        if (
            sha(folder / "config.json") != f["config_sha256"]
            or cfg["population"] != POPULATION
            or cfg["cell"] != c
        ):
            raise ValueError("fixed-v5 finish/config identity differs")
        if cfg["sources"] != p["sources"] or cfg["inputs"] != p["recipes"][c["dataset"]]:
            raise ValueError("fixed-v5 config differs from plan")
        pair_identity = {
            k: cfg[k]
            for k in (
                "item_ids",
                "endpoints_sha256",
                "initial_inference_state",
                "base_sha256",
                "reader_sha256",
                "sources",
                "inputs",
            )
        }
        if c["dataset"] in identity and identity[c["dataset"]] != pair_identity:
            raise ValueError("fixed-v5 arms do not share inputs")
        identity[c["dataset"]] = pair_identity
        for key, before in (
            ("base_hash_after", "base_sha256"),
            ("reader_hash_after", "reader_sha256"),
        ):
            if f[key] != cfg[before]:
                raise ValueError("fixed-v5 immutable weights changed")
        cps = {}
        for n in (100, 300):
            cp = read(folder / f"checkpoint-{n}.json", bindings)
            if cp["checkpoint"] != n or cp["snapshot"]["credit"] != p["credit"]["arms"][c["arm"]]:
                raise ValueError("wrong fixed-v5 checkpoint/arm")
            if sha(cp["snapshot"]["path"]) != cp["snapshot"]["sha256"]:
                raise ValueError("fixed-v5 checkpoint bytes changed")
            bindings[cp["snapshot"]["path"]] = cp["snapshot"]["sha256"]
            cps[n] = cp
        reports[(c["dataset"], c["arm"])] = dict(finish=f, checkpoints=cps)
    # Write slots only after the whole four-cell design has passed.
    for ds in ("zsre", "counterfact"):
        for n in (100, 300):
            for label, metric in (
                ("es", "ES"),
                ("ret_es", "RET-ES"),
                ("ret_gs", "RET-GS"),
                ("ls", "LS"),
                ("near_miss", "near_miss"),
                ("revision", "revision"),
            ):
                a, e = [
                    reports[ds, arm]["checkpoints"][n]["metrics"][metric]["value"]
                    for arm in ("SE-A", "SE-E")
                ]
                slots[f"v1.{ds}.{n}.{label}"] = present(
                    e - a if a is not None and e is not None else None
                )
                if n == 300:
                    slots[f"v1.{ds}.{label}"] = slots[f"v1.{ds}.{n}.{label}"]
    for arm in ("SE-A", "SE-E"):
        slots[f"v1.{arm}.seconds"] = present(
            sum(
                reports[ds, arm]["finish"]["elapsed_process_seconds"]
                for ds in ("zsre", "counterfact")
            )
        )
    return "measured: one exposed realization per dataset"


def harm_values(report, prefix, slots, bindings):
    if report.get("smoke"):
        raise ValueError("CPU harm fixture cannot populate research slides")
    required_positions = 4064 if prefix == "v0" else 245237
    expected = {
        (ds, r, o, a)
        for ds in ("zsre", "counterfact")
        for r in (range(3) if prefix == "v0" else [0])
        for o in (range(100, 105) if prefix == "v0" else [100])
        for a in ("SE-A", "SE-E")
    }

    def coord(c):
        return tuple(c[k] for k in ("dataset", "realization", "order", "arm"))

    if (
        report["selection"]["positions"] != required_positions
        or {coord(c) for c in report["cells"]} != expected
        or len(report["cells"]) != len(expected)
    ):
        raise ValueError("harm population/coverage differs from slide design")
    if len(report["pairs"]) != len(expected) // 2:
        raise ValueError("incomplete harm pairs")
    pair_coords = {(p["dataset"], p["realization"], p["order"]) for p in report["pairs"]}
    if pair_coords != {c[:3] for c in expected}:
        raise ValueError("duplicate or unexpected harm pair")
    for cell in report["cells"]:
        if cell["readout"]["selection"] != report["selection"]:
            raise ValueError("readout position selection differs")
    for row in [*[c["readout"] for c in report["cells"]], *report["pairs"]]:
        vector = row["vectors"]
        if sha(vector["path"]) != vector["sha256"]:
            raise ValueError("harm vector bytes changed")
        bindings[vector["path"]] = vector["sha256"]
    verify_sources(report, bindings)
    for ds in ("zsre", "counterfact"):
        pairs = [p for p in report["pairs"] if p["dataset"] == ds]
        slots[f"{prefix}.{ds}.harm_es99_difference"] = present(
            statistics.mean(p["difference_of_arm_es99"]["original"] for p in pairs)
        )
        slots[f"{prefix}.{ds}.harm_mean_difference"] = present(
            statistics.mean(p["positionwise"]["original"]["loss"]["mean_signed"] for p in pairs)
        )
        for arm in ("SE-A", "SE-E"):
            cells = [c for c in report["cells"] if c["dataset"] == ds and c["arm"] == arm]
            slots[f"{prefix}.{ds}.{arm}.mean_kl"] = present(
                statistics.mean(
                    c["readout"]["summary"]["original"]["kl"]["mean_signed"] for c in cells
                )
            )
            slots[f"{prefix}.{ds}.{arm}.es99"] = present(
                statistics.mean(
                    c["readout"]["summary"]["original"]["loss"]["es99_positive"] for c in cells
                )
            )
    return "measured matched-position harm"


def resolve(register=REGISTER):
    bindings, slots, status = {}, {}, {}
    config = read(register, bindings)
    for name, row in config["sources"].items():
        path = ROOT / row["path"]
        exists = (path / "plan.json").exists() if name == "v1_run" else path.exists()
        if not exists:
            status[name] = "pending source (configured future output path)"
            continue
        if name == "v1_run":
            status[name] = v1_values(path, slots, bindings)
        else:
            report = read(path, bindings)
            if name == "v0_report":
                status[name] = v0_values(report, slots, bindings)
            else:
                if name == "v1_harm":
                    if not status.get("v1_run", "").startswith("measured"):
                        status[name] = "pending verified final fixed-v5 checkpoints"
                        continue
                    from aw.pc_v1_run import cell_name

                    run = ROOT / config["sources"]["v1_run"]["path"]
                    for cell in report["cells"]:
                        checkpoint = read(run / cell_name(cell) / "checkpoint-300.json", bindings)
                        if (
                            cell["readout"]["state_sha256"]
                            != checkpoint["snapshot"]["state_sha256"]
                        ):
                            raise ValueError(
                                "fixed-v5 harm is not from the final 300-edit checkpoint"
                            )
                cost_path = path.parent / "cost.json"
                if not cost_path.exists():
                    status[name] = "pending readout completion/cost"
                    continue
                cost = read(cost_path, bindings)
                if cost["status"] != "complete":
                    status[name] = "pending completed readout"
                    continue
                status[name] = harm_values(report, name[:2], slots, bindings)
                slots[name[:2] + ".harm.seconds"] = present(cost["elapsed_process_seconds"])
    return dict(
        slots=slots,
        status=status,
        sources_sha256=bindings,
        qualification="Differences are SE-E minus SE-A. Behavior higher is better; loss/KL higher is worse. No automatic superiority claim.",
    )


def substitute(value, slots):
    if isinstance(value, str):
        return re.sub(
            r"\{\{([a-zA-Z0-9_.-]+)\}\}", lambda match: slots.get(match[1], "PENDING"), value
        )
    if isinstance(value, list):
        return [substitute(x, slots) for x in value]
    if isinstance(value, dict):
        return {k: substitute(v, slots) for k, v in value.items()}
    return value
