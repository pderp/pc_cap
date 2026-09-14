"""R1-57: inventory-driven paired revision analysis, without model execution.

The inventory declares axes, ordered populations, artifact paths, and optional
endpoint row identities independently of observed results. It is never inferred
by globbing completed jobs. CLI execution requires --dry-run in this version.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

from pccap.analysis.bootstrap import cluster_bootstrap

METRICS = ("ES", "RET-ES", "RET-GS", "LS")
MARGINS = {"RET-GS": 0.05, "ES": -0.02, "LS": -0.01}
ROOT = Path(__file__).resolve().parents[3]


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def fraction(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    if not isinstance(value, (float, int)) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("finite fraction in [0,1] required")
    return float(value)


def measure(values, planned, statuses=None):
    valid = [fraction(x) for x in values if x is not None]
    if len(values) > planned or planned < 1:
        raise ValueError("invalid planned denominator")
    total = math.fsum(valid)
    return {
        "planned": planned,
        "scored": len(valid),
        "numerator": total,
        "value": total / planned if len(valid) == planned else None,
        "evaluated_value": total / len(valid) if valid else None,
        "status": "complete" if len(valid) == planned else "incomplete",
        "status_counts": dict(statuses or {}),
    }


def classify(metrics, *, admitted=True, required_endpoints_complete=True):
    """Draft §6 inequalities, fixed revision margins; no v0 arm-name assumptions."""
    if not required_endpoints_complete or any(
        metrics[k].get("status") != "complete" for k in ("ES", "RET-GS", "LS")
    ):
        return "incomplete"
    if admitted is not True:
        return "ineligible" if admitted is False else "unadmitted"
    if any(metrics[k].get("interval") is None for k in ("ES", "RET-GS", "LS")):
        return "descriptive_insufficient_clusters"
    gs, es, ls = (metrics[k] for k in ("RET-GS", "ES", "LS"))
    if (
        gs["estimate"] >= 0.05
        and gs["interval"]["lower"] > 0
        and es["interval"]["lower"] > -0.02
        and ls["interval"]["lower"] > -0.01
    ):
        return "positive"
    if (
        gs["interval"]["upper"] < 0.05
        or es["interval"]["upper"] < -0.02
        or ls["interval"]["upper"] < -0.01
    ):
        return "negative"
    if (
        gs["estimate"] >= 0.05
        and gs["interval"]["lower"] > 0
        and es["estimate"] >= -0.02
        and ls["estimate"] >= -0.01
    ):
        return "qualified"
    return "inconclusive"


def validate_inventory(inv):
    if inv.get("schema_version") != 1:
        raise ValueError("inventory schema_version 1 required")
    axes = inv["axes"]
    for name in ("datasets", "conditions", "realizations", "orders"):
        vals = axes[name]
        if not vals or len(set(vals)) != len(vals):
            raise ValueError("nonempty unique axis required: " + name)
    expected = set(itertools.product(axes["datasets"], axes["realizations"], axes["orders"]))
    populations = {}
    for p in inv["populations"]:
        key = (p["dataset"], p["realization"], p["order"])
        if key in populations or key not in expected:
            raise ValueError("duplicate or unexpected population")
        ids = p["item_ids"]
        if not ids or len(set(ids)) != len(ids):
            raise ValueError("independent unique item inventory required")
        if len(p["paraphrase_counts"]) != len(ids) or any(
            not isinstance(n, int) or n < 1 for n in p["paraphrase_counts"]
        ):
            raise ValueError("predeclared positive paraphrase counts required")
        if not p["locality_ids"] or len(set(p["locality_ids"])) != len(p["locality_ids"]):
            raise ValueError("unique locality prompt inventory required")
        for n in p["checkpoints"].values():
            if not isinstance(n, int) or not 0 < n <= len(ids):
                raise ValueError("checkpoint outside expected item inventory")
        for ep in p.get("endpoints", {}).values():
            if not ep["expected_ids"] or len(set(ep["expected_ids"])) != len(ep["expected_ids"]):
                raise ValueError("independent endpoint identities required")
        populations[key] = p
    if set(populations) != expected:
        raise ValueError("expected populations cannot be inferred from completed cells")
    for ds in axes["datasets"]:
        seen = set()
        for r in axes["realizations"]:
            ordered = [populations[(ds, r, o)]["item_ids"] for o in axes["orders"]]
            items = set(ordered[0])
            if any(set(row) != items for row in ordered):
                raise ValueError("orders of one realization must contain the same items")
            if seen & items:
                raise ValueError(
                    "realizations share items; cannot treat repeated data as independent clusters"
                )
            seen.update(items)
    cells = {}
    for c in inv["cells"]:
        key = (c["dataset"], c["condition"], c["realization"], c["order"])
        if (
            key in cells
            or (key[0], key[2], key[3]) not in expected
            or key[1] not in axes["conditions"]
        ):
            raise ValueError("duplicate or unexpected cell identity")
        cells[key] = c
    contrast_ids = []
    for c in inv["contrasts"]:
        contrast_ids.append(c["id"])
        if c["treatment"] == c["control"] or any(
            c[k] not in axes["conditions"] for k in ("treatment", "control")
        ):
            raise ValueError("invalid contrast")
    if not contrast_ids or len(set(contrast_ids)) != len(contrast_ids):
        raise ValueError("unique declared contrasts required")
    return populations, cells


class Reader:
    def __init__(self, root):
        self.root, self.sources = Path(root), {}

    def read(self, name, *, jsonl=False):
        if not name:
            return None
        p = Path(name)
        if not p.is_absolute():
            p = self.root / p
        if not p.exists():
            return None
        raw = p.read_bytes()
        self.sources[str(p.resolve())] = hashlib.sha256(raw).hexdigest()
        return (
            [json.loads(line) for line in raw.decode().splitlines()] if jsonl else json.loads(raw)
        )

    def verify(self):
        for path, expected in self.sources.items():
            if hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected:
                raise ValueError("input changed during analysis: " + path)


def ordered_rows(rows, expected, id_key):
    ids = [r[id_key] for r in rows]
    if len(set(ids)) != len(ids) or any(i not in expected for i in ids):
        raise ValueError("duplicate or unexpected observed row")
    if ids != [i for i in expected if i in set(ids)]:
        raise ValueError("observed update/query order differs from inventory")
    return {r[id_key]: r for r in rows}


def endpoint(reader, definition, paths):
    expected = definition["expected_ids"]
    result = measure([], len(expected), {"not_run": len(expected)})
    summary = reader.read(paths.get("summary"))
    rows = reader.read(paths.get("rows"))
    if isinstance(rows, dict):
        rows = rows.get("rows")
    if rows is None:
        result["reason"] = "missing per-case endpoint identities/results"
        result["reported_summary"] = summary
        return result
    by_id = ordered_rows(rows, expected, definition.get("id_key", "source_row_sha256"))
    values, statuses = [], Counter()
    for identity in expected:
        row = by_id.get(identity)
        status = row.get("status", "unavailable") if row else "missing"
        value = row.get(definition["row_metric"]) if row and status == "ok" else None
        if definition["row_metric"] == "false_fire" and row and row.get("firing_status") != "ok":
            value, status = None, "firing_unavailable"
        statuses[status] += 1
        values.append(fraction(value))
    result = measure(values, len(expected), statuses)
    if summary is not None:
        node = summary
        for key in definition.get("summary_path", ["summary"]):
            node = node.get(key, {}) if isinstance(node, dict) else {}
        result["reported_summary"] = node
        reported = node.get(definition.get("summary_metric", "full_inventory_fraction"))
        if (
            result["value"] is not None
            and reported is not None
            and not math.isclose(result["value"], fraction(reported), abs_tol=1e-12)
        ):
            raise ValueError("endpoint row/summary disagreement")
    return result


def load_cell(reader, cell, population, checkpoint, *, development):
    n = population["checkpoints"][checkpoint]
    wanted = population["item_ids"][:n]
    empty = {m: measure([], n if m != "LS" else len(population["locality_ids"])) for m in METRICS}
    result = {
        "metrics": empty,
        "endpoints": {},
        "identity_limitations": [],
        "status": "missing_cell",
        "admitted": None,
    }
    if cell is None:
        for name, definition in population.get("endpoints", {}).items():
            result["endpoints"][name] = measure([], len(definition["expected_ids"]))
        return result
    result["admitted"] = cell.get("admitted")
    directory = Path(cell["stream_dir"])
    sm = reader.read(cell["stream_summary"])
    metrics_file = reader.read(directory / "metrics.json")
    items = reader.read(directory / "items.jsonl", jsonl=True)
    checks = reader.read(directory / "checkpoints.json")
    for name, definition in population.get("endpoints", {}).items():
        result["endpoints"][name] = endpoint(
            reader, definition, cell.get("endpoints", {}).get(name, {})
        )
    if sm is None or metrics_file is None or items is None or checks is None:
        result["reason"] = "missing stream artifacts"
        return result
    if sm.get("dataset", sm.get("args", {}).get("dataset")) != population["dataset"]:
        raise ValueError("stream dataset mismatch")
    for key, value in cell.get("expected_summary", {}).items():
        if sm.get(key) != value:
            raise ValueError("stream condition identity mismatch: " + key)
    for key, value in cell.get("expected_args", {}).items():
        if sm.get("args", {}).get(key) != value:
            raise ValueError("stream recipe/order mismatch: " + key)
    all_ids = population["item_ids"]
    by_id = ordered_rows(items, all_ids, "item_id")
    index_of = {i: j for j, i in enumerate(all_ids)}
    for item in items:
        i = index_of[item["item_id"]]
        if item["dataset"] != population["dataset"] or item["index"] != i:
            raise ValueError("item dataset/update order mismatch")
        if item.get("gs_n") != population["paraphrase_counts"][i]:
            raise ValueError("item paraphrase denominator mismatch")
    selected = [c for c in checks if str(c["tag"]) == checkpoint]
    if len(selected) > 1:
        raise ValueError("duplicate checkpoint")
    cp = selected[0] if selected else None
    retained = ordered_rows(cp["rows"], wanted, "item_id") if cp else {}
    for metric, field, rows in (
        ("ES", "es", by_id),
        ("RET-ES", "ret_es", retained),
        ("RET-GS", "ret_gs", retained),
    ):
        vals, statuses = [], Counter()
        for identity in wanted:
            r = rows.get(identity)
            original = by_id.get(identity)
            failed_resource = original and original.get("outcome") == "acquisition_failure"
            value = r.get(field) if r and not failed_resource else None
            statuses[
                "resource_failure"
                if failed_resource
                else ("scored" if value is not None else "missing")
            ] += 1
            vals.append(fraction(value))
        result["metrics"][metric] = measure(vals, n, statuses)
    locality = cp.get("locality", {}) if cp else {}
    local_n = len(population["locality_ids"])
    if locality.get("n") == local_n:
        local_ids = locality.get("prompt_ids")
        if local_ids is not None and local_ids != population["locality_ids"]:
            raise ValueError("locality identity mismatch")
        if local_ids is None:
            result["identity_limitations"].append(
                "legacy LS aggregate lacks prompt IDs; expected source inventory supplies intended pairing"
            )
        value = fraction(locality.get("ls_complete_answer"))
        if value is not None and (development or local_ids is not None):
            result["metrics"]["LS"] = measure([value] * local_n, local_n)
    if cp and cp.get("items") != n:
        raise ValueError("checkpoint item count differs from independent inventory")
    if checkpoint == "end":
        saved_keys = {
            "ES": "es_immediate",
            "RET-ES": "ret_es_end",
            "RET-GS": "ret_gs_end",
            "LS": "ls_complete_answer_end",
        }
        for name, key in saved_keys.items():
            value = result["metrics"][name]["value"]
            saved = metrics_file.get("metrics", {}).get(key, {})
            reported = sm.get("stream_metrics", {}).get(key)
            if value is not None:
                if saved.get("n") != result["metrics"][name]["planned"]:
                    raise ValueError("summary metric denominator mismatch")
                for observed in (saved.get("value"), reported):
                    if observed is None or not math.isclose(
                        value, fraction(observed), abs_tol=1e-12
                    ):
                        raise ValueError("stream item/summary disagreement")
    if metrics_file.get("status") != "complete":
        result["reason"] = "stream reports incomplete status"
        for value in result["metrics"].values():
            value["value"], value["status"] = None, "incomplete"
    result["status"] = (
        "complete"
        if all(v["value"] is not None for v in result["metrics"].values())
        else "incomplete"
    )
    result["failed_acquisition_count"] = sum(
        not r.get("threshold", False) for r in items if r["item_id"] in wanted
    )
    result["behavioral_rejections_retained"] = sum(
        r.get("outcome") == "rejected_no_improvement" for r in items if r["item_id"] in wanted
    )
    return result


def paired_metric(grid, *, seed=0, draws=10000, confidence=0.975):
    available = [x for row in grid for x in row if x is not None]
    result = {
        "paired_differences": grid,
        "planned_pairs": sum(map(len, grid)),
        "observed_pairs": len(available),
        "observed_pair_mean_diagnostic": math.fsum(available) / len(available)
        if available
        else None,
        "estimate": None,
        "interval": None,
        "status": "incomplete",
    }
    if len(available) != result["planned_pairs"]:
        return result
    values = np.asarray(grid, np.float64)
    result.update(
        status="complete",
        estimate=float(values.mean()),
        clusters=len(grid),
        order_means=values.mean(axis=1).tolist(),
    )
    if len(grid) < 2:
        result["uncertainty"] = "one realization: no cluster interval; no independent replication"
        return result
    boot = cluster_bootstrap(
        values,
        seed=seed,
        draws=draws,
        confidence=confidence,
        expected_realizations=len(grid),
        expected_orders=len(grid[0]),
    )
    result["interval"] = boot["interval"]
    result["bootstrap"] = boot
    result["uncertainty"] = "preliminary realization-cluster interval; orders are kept together"
    return result


def analyze(inv, *, root=ROOT, checkpoint="end"):
    populations, declarations = validate_inventory(inv)
    axes, reader = inv["axes"], Reader(root)
    development = inv.get("scope") != "confirmatory"
    if any(checkpoint not in p["checkpoints"] for p in populations.values()):
        raise ValueError("checkpoint must be declared for every population")
    for path, expected in inv.get("source_bindings_sha256", {}).items():
        if (
            reader.read(path) is None
            or reader.sources[str((Path(root) / path).resolve())] != expected
        ):
            raise ValueError("independent inventory source binding changed")
    loaded = {}
    for dataset, condition, realization, order in itertools.product(
        axes["datasets"], axes["conditions"], axes["realizations"], axes["orders"]
    ):
        key = (dataset, condition, realization, order)
        loaded[key] = load_cell(
            reader,
            declarations.get(key),
            populations[(dataset, realization, order)],
            checkpoint,
            development=development,
        )
    comparisons = []
    params = {
        k: inv.get("bootstrap", {}).get(k, default)
        for k, default in (("seed", 0), ("draws", 10000), ("confidence", 0.975))
    }
    for ds, contrast in itertools.product(axes["datasets"], inv["contrasts"]):
        names = set(METRICS)
        for (dataset, _r, _o), p in populations.items():
            if dataset == ds:
                names.update(p.get("endpoints", {}))
        stats, missing, admissions, required_complete = {}, [], [], True
        for name in sorted(names):
            grid = []
            for r in axes["realizations"]:
                row = []
                for o in axes["orders"]:
                    p = populations[(ds, r, o)]
                    a = loaded[(ds, contrast["treatment"], r, o)]
                    b = loaded[(ds, contrast["control"], r, o)]
                    group = "metrics" if name in METRICS else "endpoints"
                    av, bv = (c[group].get(name, {}).get("value") for c in (a, b))
                    delta = av - bv if av is not None and bv is not None else None
                    row.append(delta)
                    if name == "ES":
                        admissions.extend((a["admitted"], b["admitted"]))
                    if delta is None:
                        missing.append({"realization": r, "order": o, "metric": name})
                        if name not in METRICS and p.get("endpoints", {}).get(name, {}).get(
                            "required", False
                        ):
                            required_complete = False
                grid.append(row)
            stats[name] = paired_metric(grid, **params)
        admission = (
            False if False in admissions else (True if all(x is True for x in admissions) else None)
        )
        comparisons.append(
            {
                "dataset": ds,
                "contrast": contrast["id"],
                "treatment": contrast["treatment"],
                "control": contrast["control"],
                "checkpoint": checkpoint,
                "metrics": stats,
                "missing_pairs": missing,
                "classification": classify(
                    stats, admitted=admission, required_endpoints_complete=required_complete
                ),
                "scope": "development, not confirmatory"
                if development
                else "inventory-declared confirmation; freeze/multiplicity admission remains caller responsibility",
            }
        )
    reader.verify()
    return {
        "schema_version": 1,
        "task": "R1-57",
        "inventory_sha256": digest(inv),
        "margins": MARGINS,
        "scope": "development, not confirmatory" if development else "confirmatory",
        "checkpoint": checkpoint,
        "comparisons": comparisons,
        "cells": [
            {"dataset": k[0], "condition": k[1], "realization": k[2], "order": k[3], **v}
            for k, v in loaded.items()
        ],
        "sources_sha256": reader.sources,
        "model_execution": False,
        "gpu_seconds": 0,
        "multiplicity": inv.get("multiplicity", "not adopted; no familywise claim"),
    }


def table(result):
    lines = [
        "DEVELOPMENT, NOT CONFIRMATORY",
        "",
        "| dataset | contrast | checkpoint | ΔES | ΔRET-GS | ΔLS | status |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for c in result["comparisons"]:
        vals = [c["metrics"][m]["estimate"] for m in ("ES", "RET-GS", "LS")]
        formatted = ["unavailable" if x is None else f"{x:+.4f}" for x in vals]
        lines.append(
            "| "
            + " | ".join(
                [str(c["dataset"]), c["contrast"], c["checkpoint"], *formatted, c["classification"]]
            )
            + " |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--checkpoint", default="end")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.dry_run:
        parser.error("this CLI requires --dry-run; no confirmation admission is implemented")
    inv = json.loads(args.inventory.read_text())
    if inv.get("scope") == "confirmatory":
        parser.error("dry-run CLI only accepts development/synthetic inventories")
    if args.output and (
        args.output.exists() or not args.output.resolve().is_relative_to(ROOT / "logs")
    ):
        parser.error("choose a new output file under logs")
    result = analyze(inv, checkpoint=args.checkpoint)
    print(table(result))
    if args.output:
        with args.output.open("x") as f:
            f.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
