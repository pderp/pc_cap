"""Frozen, complete-pair analysis of one editing stream (PDF D.11).

Expected input rows have arm, realization, order, item_id, ret_gs, es, ls.
RET-GS is an item-level paraphrase mean; each item has equal weight within a
run, orders have equal weight within a realization, and realizations have
 equal weight. Analyze separate datasets/scopes in separate calls.
"""

import argparse
import json
from collections.abc import Iterable, Mapping
from pathlib import Path

import numpy as np

from .bootstrap import cluster_bootstrap

MEASURES = ("ret_gs", "es", "ls")
MARGINS = {"ret_gs": 0.02, "es": -0.02, "ls": -0.01}


def _identifier(value, label):
    if not isinstance(value, (str, int)) or isinstance(value, bool):
        raise ValueError(f"{label} must be a string or integer identifier")
    return value


def _cell_key(key):
    # Stable across input row order and Python's incomparable mixed int/string IDs.
    return tuple((type(v).__name__, str(v)) for v in key)


def _fraction(value, name):
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    if not isinstance(value, (int, float)) or not np.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be a finite fraction or explicit null")
    return float(value)


def _classification(measures):
    point = {k: v["estimate"]["value"] for k, v in measures.items()}
    low = {k: v["interval"]["lower"] for k, v in measures.items()}
    high = {k: v["interval"]["upper"] for k, v in measures.items()}
    checks = {
        "ret_gs_practical_gain": point["ret_gs"] >= MARGINS["ret_gs"],
        "ret_gs_lower_above_zero": low["ret_gs"] > 0,
        "es_noninferiority": low["es"] > MARGINS["es"],
        "ls_noninferiority": low["ls"] > MARGINS["ls"],
    }
    if all(checks.values()):
        return "positive", checks
    # A bounded effect entirely below the practical target, or a constraint
    # entirely beyond its permitted harm, cannot support the primary claim.
    if (
        high["ret_gs"] < MARGINS["ret_gs"]
        or high["es"] < MARGINS["es"]
        or high["ls"] < MARGINS["ls"]
    ):
        return "negative", checks
    if (
        checks["ret_gs_practical_gain"]
        and checks["ret_gs_lower_above_zero"]
        and point["es"] >= MARGINS["es"]
        and point["ls"] >= MARGINS["ls"]
    ):
        return "qualified", checks
    return "inconclusive", checks


def analyze_paired(
    rows: Iterable[Mapping],
    *,
    realizations=(0, 1, 2),
    orders=(0, 1, 2, 3, 4),
    expected_items: Mapping | None = None,
    seed: int = 0,
    draws: int = 10_000,
    confidence: float = 0.975,
    stream_id: str | None = None,
) -> dict:
    """Analyze both required contrasts, without inferring missing paired outcomes.

    ``expected_items`` optionally maps realization IDs to their frozen item ID
    lists. Supply it in confirmation to detect omissions common to every arm.
    Without it, coverage is checked against the union of observed required-arm
    IDs across all orders, and is explicitly labelled observed-only.

    Null outcome values or absent pairs produce an incomplete comparison and no
    bootstrap. Duplicates, nonfinite values and incompatible scope are errors.
    """
    realizations, orders = tuple(realizations), tuple(orders)
    if len(realizations) != 3 or len(orders) != 5:
        raise ValueError("confirmatory analysis requires three realizations and five orders")
    for ids, label in ((realizations, "realization"), (orders, "order")):
        for identifier in ids:
            _identifier(identifier, label)
        if len(set(ids)) != len(ids):
            raise ValueError(f"duplicate {label} IDs")
    required_arms = {"C2", "C1", "CR"}
    indexed, universes = {}, {r: set() for r in realizations}
    observed_streams = set()
    for source in rows:
        if not isinstance(source, Mapping):
            raise TypeError("each table row must be a mapping")
        arm = source.get("arm")
        if arm not in required_arms:
            continue
        if "stream_id" in source:
            observed_streams.add(source["stream_id"])
        r, o = source.get("realization"), source.get("order")
        _identifier(r, "realization")
        _identifier(o, "order")
        if r not in realizations or o not in orders:
            raise ValueError("row realization/order is outside the frozen schedule")
        item = _identifier(source.get("item_id"), "item_id")
        key = (arm, r, o, item)
        if key in indexed:
            raise ValueError(f"duplicate item row: {key}")
        for name in MEASURES:
            if name not in source:
                raise ValueError(
                    f"missing field {name}; use explicit null for unavailable outcomes"
                )
        indexed[key] = {name: _fraction(source[name], name) for name in MEASURES}
        universes[r].add(item)
    if len(observed_streams) > 1 or (
        stream_id is not None and observed_streams and observed_streams != {stream_id}
    ):
        raise ValueError("analyze each dataset/scope separately; mixed stream_id values")
    if expected_items is not None:
        if set(expected_items) != set(realizations):
            raise ValueError("expected_items must specify each frozen realization")
        for r in realizations:
            items = list(expected_items[r])
            for item in items:
                _identifier(item, "item_id")
            if len(set(items)) != len(items):
                raise ValueError("duplicate item in frozen inventory")
            unexpected = universes[r] - set(items)
            if unexpected:
                raise ValueError(
                    f"unexpected items for realization {r}: {sorted(unexpected, key=str)}"
                )
            universes[r] = set(items)
    contrasts = {}
    for comparator in ("C1", "CR"):
        cells, missing, losses = [], [], []
        arrays = {name: np.empty((3, 5), dtype=np.float64) for name in MEASURES}
        for ri, r in enumerate(realizations):
            for oi, o in enumerate(orders):
                items = sorted(universes[r], key=lambda item: _cell_key((item,)))
                cell_missing, differences = [], {name: [] for name in MEASURES}
                if not items:
                    cell_missing.append({"reason": "empty_realization_inventory"})
                for item in items:
                    left, right = (
                        indexed.get(("C2", r, o, item)),
                        indexed.get((comparator, r, o, item)),
                    )
                    absent = [
                        arm for arm, entry in (("C2", left), (comparator, right)) if entry is None
                    ]
                    if absent:
                        cell_missing.append(
                            {"item_id": item, "reason": "missing_pair", "arms": absent}
                        )
                        continue
                    nulls = [
                        {"arm": arm, "measure": name}
                        for arm, entry in (("C2", left), (comparator, right))
                        for name in MEASURES
                        if entry[name] is None
                    ]
                    if nulls:
                        cell_missing.append(
                            {"item_id": item, "reason": "unavailable_outcome", "fields": nulls}
                        )
                        continue
                    for name in MEASURES:
                        differences[name].append(left[name] - right[name])
                    if left["ret_gs"] != right["ret_gs"]:
                        losses.append(
                            {
                                "realization": r,
                                "order": o,
                                "item_id": item,
                                "c2_ret_gs": left["ret_gs"],
                                "comparator_ret_gs": right["ret_gs"],
                                "direction": "lost"
                                if left["ret_gs"] < right["ret_gs"]
                                else "gained",
                                "all_comparator_paraphrase_success_lost": right["ret_gs"] > 0
                                and left["ret_gs"] == 0,
                            }
                        )
                cell = {
                    "realization": r,
                    "order": o,
                    "n_expected": len(items),
                    "n_complete_pairs": len(differences["ret_gs"]),
                }
                if cell_missing:
                    cell.update(status="incomplete", differences=None)
                    missing.extend(
                        {"realization": r, "order": o, **entry} for entry in cell_missing
                    )
                else:
                    means = {name: float(np.mean(differences[name])) for name in MEASURES}
                    cell.update(status="complete", differences=means)
                    for name in MEASURES:
                        arrays[name][ri, oi] = means[name]
                cells.append(cell)
        result = {
            "treatment": "C2",
            "comparator": comparator,
            "paired_table": cells,
            "missing": missing,
            "item_changes": losses,
            "item_change_note": "Item RET-GS changes are paraphrase-mean changes, not identities of individual lost paraphrases.",
        }
        if missing:
            result.update(
                status="incomplete", classification="incomplete", measures=None, checks=None
            )
        else:
            measured = {
                name: cluster_bootstrap(array, seed=seed, draws=draws, confidence=confidence)
                for name, array in arrays.items()
            }
            classification, checks = _classification(measured)
            result.update(
                status="complete", classification=classification, measures=measured, checks=checks
            )
        contrasts[f"C2-{comparator}"] = result
    classes = [c["classification"] for c in contrasts.values()]
    if "incomplete" in classes:
        overall = "incomplete"
    elif all(c == "positive" for c in classes):
        overall = "positive"
    elif "negative" in classes:
        overall = "negative"
    elif all(c in ("positive", "qualified") for c in classes):
        overall = "qualified"
    else:
        overall = "inconclusive"
    return {
        "schema_version": 1,
        "stream_id": stream_id or next(iter(observed_streams), None),
        "primary_endpoint": "endpoint_ret_gs",
        "classification": overall,
        "primary_claim_supported": overall == "positive",
        "contrasts": contrasts,
        "coverage_basis": "frozen_inventory"
        if expected_items is not None
        else "observed_union_only",
        "realizations": list(realizations),
        "orders": list(orders),
        "margins": dict(MARGINS),
        "inference": {
            "seed": seed,
            "draws": draws,
            "confidence": confidence,
            "cluster_unit": "realization",
            "requires_both_contrasts": True,
        },
        "comparable_compute_claim": "not_assessed_requires_resource_evidence",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="one stream's item-level JSONL table")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--stream-id")
    parser.add_argument(
        "--inventory", type=Path, help='JSON list: [{"realization":0,"item_ids":[...]}]'
    )
    args = parser.parse_args(argv)
    rows = [json.loads(line) for line in args.input.read_text().splitlines() if line.strip()]
    inventory = None
    if args.inventory:
        records = json.loads(args.inventory.read_text())
        inventory = {r["realization"]: r["item_ids"] for r in records}
        if len(inventory) != len(records):
            raise ValueError("duplicate realization in inventory")
    report = analyze_paired(
        rows, seed=args.seed, stream_id=args.stream_id, expected_items=inventory
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return 0 if report["classification"] != "incomplete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
