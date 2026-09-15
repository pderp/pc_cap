"""R1-57b: three-dataset Stage 4 inventory and checkpoint analysis.

Expected cells are declared before reading results. Development observations
never fill confirmatory slots. Orders remain nested within realizations.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

from pccap.revision_v1.analysis import (
    Reader,
    analyze,
    classify,
    digest,
    fraction,
    measure,
    ordered_rows,
    paired_metric,
)
from pccap.revision_v1.stage4_adapters import CORE_CONDITIONS, SECONDARY_CONDITION
from pccap.revision_v1.stage4_cell import CHECKPOINTS, ROOT

SECONDARY = {
    "unseen_false_fire": ("unseen", "false_fire", "item_id"),
    "unseen_answer_change": ("unseen", "answer_changed", "item_id"),
    "composition": ("composition", "composition_success", "composition_id"),
    "revision_latest_answer": ("revision", "latest_answer_success", "item_id"),
}


def expected_inventory():
    axes = {
        "conditions": list(CORE_CONDITIONS),
        "datasets": ["zsre", "counterfact", "mquake"],
        "realizations": [0, 1, 2],
        "orders": [0, 1, 2, 3, 4],
    }
    cells = []
    for condition, ds, r, o in itertools.product(
        axes["conditions"], axes["datasets"], axes["realizations"], axes["orders"]
    ):
        cells.append(
            {
                "condition": condition,
                "dataset": ds,
                "realization": r,
                "order": o,
                "checkpoints": list(CHECKPOINTS),
                "manifest_sha256": None,
                "result_dir": None,
                "admitted": None,
            }
        )
    extra = [
        {**c, "condition": SECONDARY_CONDITION} for c in cells if c["condition"] == "R1_learned_ff"
    ]
    return {
        "schema_version": 1,
        "scope": "draft",
        "task": "R1-57b",
        "axes": axes,
        "cells": cells,
        "populations": [],
        "secondary_cells": extra,
        "registered_cell_count": 360,
        "secondary_additional_cell_count": 45,
        "checkpoints": list(CHECKPOINTS),
        "contrasts": [
            {
                "id": "v3_minus_" + c,
                "treatment": "R1_learned_ff",
                "control": c,
                "role": "primary_comparator",
            }
            for c in CORE_CONDITIONS
            if c != "R1_learned_ff"
        ]
        + [
            {
                "id": "v3_minus_v2",
                "treatment": "R1_learned_ff",
                "control": SECONDARY_CONDITION,
                "role": "declared_secondary",
            }
        ],
        "secondary_margins": None,
        "population_status": "unbound; no fresh identities selected, reserved, read or inferred from results",
        "v2_allocation_note": "45 optional additional cells are not included in the registered 360; no allocation or launch authorized",
        "bootstrap": {"seed": 157, "draws": 10000, "confidence": 0.975},
        "inference_note": "margins and multiplicity remain subject to protocol freeze; U14 secondary endpoints are descriptive",
    }


def cell_key(cell):
    return (cell["dataset"], cell["condition"], cell["realization"], cell["order"])


def population_key(cell):
    return (cell["dataset"], cell["realization"], cell["order"])


def validate(inv):
    template = expected_inventory()
    if (
        inv.get("schema_version") != 1
        or inv["axes"] != template["axes"]
        or inv["checkpoints"] != list(CHECKPOINTS)
    ):
        raise ValueError("registered three-dataset axes/checkpoints required")
    if inv["contrasts"] != template["contrasts"]:
        raise ValueError("declared primary and v2 secondary contrasts must be retained")
    declarations = {}
    for group in ("cells", "secondary_cells"):
        expected = {cell_key(c) for c in template[group]}
        actual = [cell_key(c) for c in inv[group]]
        if len(actual) != len(set(actual)) or set(actual) != expected:
            raise ValueError("inventory must retain every expected cell including missing controls")
        declarations.update({cell_key(c): c for c in inv[group]})
    populations = {}
    for p in inv["populations"]:
        key = population_key(p)
        if key in populations or key not in {population_key(c) for c in inv["cells"]}:
            raise ValueError("duplicate/unexpected population")
        ids = p["item_ids"]
        if (
            len(ids) != 1000
            or len(set(ids)) != 1000
            or len(p["paraphrase_counts"]) != 1000
            or any(type(n) is not int or n < 1 for n in p["paraphrase_counts"])
        ):
            raise ValueError("independent 1000-item and paraphrase inventory required")
        for name in ("locality", "unseen", "near_miss", "revision", "composition"):
            eps = p["endpoints"][name]
            if len(set(eps)) != len(eps) or (not eps and name != "composition"):
                raise ValueError("independent endpoint identities required")
        populations[key] = p
    for ds in inv["axes"]["datasets"]:
        seen = set()
        for r in inv["axes"]["realizations"]:
            rows = [p["item_ids"] for k, p in populations.items() if k[:2] == (ds, r)]
            if not rows:
                continue
            ids = set(rows[0])
            if any(set(x) != ids for x in rows) or ids & seen:
                raise ValueError("orders must share membership; realizations must be disjoint")
            seen.update(ids)
    return declarations, populations


def endpoint_summary(rows, expected_ids, field, *, id_key="item_id", firing=False):
    by_id = ordered_rows(rows, expected_ids, id_key)
    if not expected_ids:
        return {
            "planned": 0,
            "scored": 0,
            "numerator": 0,
            "value": None,
            "evaluated_value": None,
            "status": "not_applicable",
            "status_counts": {},
        }
    vals, statuses = [], Counter()
    for iid in expected_ids:
        row = by_id.get(iid)
        status = row.get("status", "unavailable") if row else "missing"
        value = row.get(field) if row and status == "ok" else None
        if firing and row and row.get("firing_status") != "ok":
            value, status = None, "firing_unavailable"
        statuses[status] += 1
        vals.append(fraction(value))
    result = measure(vals, len(expected_ids), statuses)
    result["evaluable"] = sum(bool(r.get("evaluable", r.get("status") == "ok")) for r in rows)
    return result


def summarize_checkpoint(report, population, n):
    ids = population["item_ids"][:n]
    h = report.get("history", [])
    ret = report.get("retention", {}).get("rows", [])
    for rows in (h, ret):
        ordered_rows(rows, ids, "item_id")
        by_id = {r["item_id"]: r for r in rows}
        for i, iid in enumerate(ids):
            row = by_id.get(iid)
            if row and row.get("paraphrase_n") != population["paraphrase_counts"][i]:
                raise ValueError("observed paraphrase denominator differs from inventory")
    primary = {
        "ES": endpoint_summary(h, ids, "es"),
        "RET-ES": endpoint_summary(ret, ids, "es"),
        "RET-GS": endpoint_summary(ret, ids, "gs"),
        "LS": endpoint_summary(
            report.get("locality", {}).get("rows", []),
            population["endpoints"]["locality"],
            "preserved",
        ),
    }
    secondary = {}
    for name, (group, field, key) in SECONDARY.items():
        if group in ("composition", "revision") and n != 1000:
            continue
        rows = (
            report.get("unseen", {}).get("rows", [])
            if group == "unseen"
            else report.get("endpoints", {}).get(group, {}).get("rows", [])
        )
        secondary[name] = endpoint_summary(
            rows,
            population["endpoints"][group],
            field,
            id_key=key,
            firing=name == "unseen_false_fire",
        )
        secondary[name]["interpretation"] = (
            "secondary descriptive; no registered margin or binary verdict"
        )
    return {"primary": primary, "secondary": secondary}


def read_completed_cell(reader, cell, population):
    result = {
        "cell": {k: cell[k] for k in ("condition", "dataset", "realization", "order")},
        "status": "missing",
        "checkpoints": {},
        "missing_checkpoints": list(CHECKPOINTS),
    }
    directory = cell.get("result_dir")
    if not directory:
        return result
    directory = Path(directory)
    if not directory.is_absolute():
        directory = reader.root / directory
    meta = reader.read(str(directory / "cell.json"))
    if meta is None:
        return result
    if meta.get("cell") != result["cell"] or meta.get("manifest_sha256") != cell["manifest_sha256"]:
        raise ValueError("observed cell identity differs from inventory")
    if population is None:
        result["status"] = "population_unbound"
        return result
    if meta.get("checkpoints") != list(CHECKPOINTS):
        raise ValueError("cell has a different checkpoint contract")
    receipts = []
    for path in directory.glob("attempt-*/checkpoint-*.receipt.json"):
        rec = reader.read(str(path))
        if digest({k: v for k, v in rec.items() if k != "receipt_sha256"}) != rec["receipt_sha256"]:
            raise ValueError("receipt hash mismatch")
        receipts.append(rec)
    receipts.sort(key=lambda r: r["checkpoint"])
    if [r["checkpoint"] for r in receipts] != list(CHECKPOINTS[: len(receipts)]):
        raise ValueError("duplicate or noncontiguous completed checkpoint inventory")
    prev = None
    for rec in receipts:
        if (
            rec["previous_receipt_sha256"] != prev
            or rec["manifest_sha256"] != cell["manifest_sha256"]
        ):
            raise ValueError("receipt chain differs from expected cell")
        path = Path(rec["report"]["path"]).resolve()
        if not path.is_relative_to(directory.resolve()):
            raise ValueError("checkpoint report escapes expected cell directory")
        report = reader.read(str(path))
        if report is None or reader.sources[str(path)] != rec["report"]["sha256"]:
            raise ValueError("checkpoint report hash mismatch")
        if (
            report["checkpoint"] != rec["checkpoint"]
            or report["state_sha256"] != rec["state_sha256"]
        ):
            raise ValueError("checkpoint report identity mismatch")
        n = rec["checkpoint"]
        result["checkpoints"][str(n)] = summarize_checkpoint(report, population, n)
        prev = rec["receipt_sha256"]
    result["missing_checkpoints"] = [n for n in CHECKPOINTS if str(n) not in result["checkpoints"]]
    result["status"] = "complete" if not result["missing_checkpoints"] else "incomplete"
    result["scientific_admission"] = (
        cell.get("admitted") is True and meta.get("mode") == "stage4_sealed_cell"
    )
    # Artifact completion is separate from metric/endpoint coverage.
    result["metrics_complete"] = (
        all(
            v["status"] == "complete"
            for cp in result["checkpoints"].values()
            for v in cp["primary"].values()
        )
        and not result["missing_checkpoints"]
    )
    return result


def analyze_stage4(inv, *, root=ROOT):
    declarations, populations = validate(inv)
    reader = Reader(root)
    loaded = {
        key: read_completed_cell(reader, c, populations.get(population_key(c)))
        for key, c in declarations.items()
    }
    accounting = {}
    for condition in (*CORE_CONDITIONS, SECONDARY_CONDITION):
        rows = [v for k, v in loaded.items() if k[1] == condition]
        accounting[condition] = {
            "planned": len(rows),
            "missing": sum(r["status"] == "missing" for r in rows),
            "incomplete_or_unbound": sum(r["status"] not in ("complete", "missing") for r in rows),
            "artifact_complete": sum(r["status"] == "complete" for r in rows),
            "metrics_complete": sum(r.get("metrics_complete", False) for r in rows),
            "missing_checkpoints": sum(len(r["missing_checkpoints"]) for r in rows),
        }
    comparisons = []
    for ds, contrast, n in itertools.product(
        inv["axes"]["datasets"], inv["contrasts"], CHECKPOINTS
    ):
        stats = {}
        for metric in ("ES", "RET-ES", "RET-GS", "LS", *SECONDARY):
            if metric in ("composition", "revision_latest_answer") and n != 1000:
                continue
            grid = []
            for r in inv["axes"]["realizations"]:
                values = []
                for o in inv["axes"]["orders"]:
                    pair = []
                    for condition in (contrast["treatment"], contrast["control"]):
                        cp = loaded[(ds, condition, r, o)]["checkpoints"].get(str(n), {})
                        group = "secondary" if metric in SECONDARY else "primary"
                        pair.append(cp.get(group, {}).get(metric, {}).get("value"))
                    values.append(pair[0] - pair[1] if all(x is not None for x in pair) else None)
                grid.append(values)
            stats[metric] = paired_metric(grid, **inv["bootstrap"])
            stats[metric]["interpretation"] = (
                "descriptive; unregistered secondary margin"
                if metric in SECONDARY
                else contrast["role"]
            )
        admitted = all(
            loaded[(ds, c, r, o)].get("scientific_admission") is True
            for c in (contrast["treatment"], contrast["control"])
            for r in inv["axes"]["realizations"]
            for o in inv["axes"]["orders"]
        )
        verdict = classify(stats, admitted=admitted and inv.get("scope") == "confirmatory")
        if contrast["role"] == "declared_secondary":
            verdict = "secondary_descriptive"
        comparisons.append(
            {
                "dataset": ds,
                "checkpoint": n,
                "contrast": contrast,
                "metrics": stats,
                "classification": verdict,
            }
        )
    reader.verify()
    return {
        "schema_version": 1,
        "banner": "NOT CONFIRMATORY — development/draft analysis"
        if inv.get("scope") != "confirmatory"
        else "Stage 4 inventory analysis; admission and protocol review required",
        "registered_cells": 360,
        "secondary_additional_cells": 45,
        "missing_by_condition": accounting,
        "cells": list(loaded.values()),
        "comparisons": comparisons,
        "sources_sha256": reader.sources,
        "inventory_sha256": digest(inv),
        "population_bindings": len(populations),
        "secondary_margin_policy": "composition and unseen are descriptive; this adapter does not invent an inferential rule for any future margin",
        "uncertainty_unit": "realization; the five orders are retained together, not independent observations",
    }


def development_dry_run(development_inventory, *, root=ROOT):
    if development_inventory.get("scope") != "development":
        raise ValueError("development inventory required")
    development_inventory = json.loads(json.dumps(development_inventory))
    # Legacy analysis represents missing cells by an absent declaration. Keep
    # all expected axes so these cells remain in every planned denominator.
    development_inventory["cells"] = [
        c for c in development_inventory["cells"] if c.get("stream_dir")
    ]
    legacy = analyze(development_inventory, root=root)
    return {
        "banner": "NOT CONFIRMATORY — development outputs only",
        "registered_inventory": analyze_stage4(expected_inventory(), root=root),
        "development": legacy,
        "interpretation": "development cells do not satisfy any of the 360 fresh cells; reader seeds on one dev population are not independent data realizations",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventory", type=Path)
    ap.add_argument("--development-inventory", type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args(argv)
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT / "logs"):
        ap.error("new output under repository logs required")
    if args.inventory and args.development_inventory:
        ap.error("choose Stage 4 or development inventory")
    if args.development_inventory:
        result = development_dry_run(json.loads(args.development_inventory.read_text()))
    else:
        inv = json.loads(args.inventory.read_text()) if args.inventory else expected_inventory()
        result = analyze_stage4(inv)
    with args.output.open("x") as f:
        f.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(result["banner"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
