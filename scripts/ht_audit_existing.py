"""HT-1: descriptive distributions from stored development results; no model calls.

Every series stays separate by source, checkpoint, outcome and reference. Binary
or fractional task errors are not nats. Pairing is descriptive on shared keys;
no independence, causal, power-law, or population-tail inference is asserted.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = (
    "stage4_dev_cells/*/attempt-*/checkpoint-*.json",
    "streams_revision/*/items.jsonl",
    "streams_revision/*/checkpoints.json",
    "endpoints/*/*.json",
    "drift_assay_*.json",
    "stream_eval_*.json",
)
SUCCESS_FIELDS = (
    "es",
    "gs",
    "ret_es",
    "ret_gs",
    "preserved",
    "complete_answer_preserved",
    "composition_success",
    "near_miss_success",
    "revision_success",
    "edit_exact",
    "latest_answer_success",
    "paraphrase_new_exact_fraction",
)
HARM_FIELDS = (
    "false_fire",
    "answer_changed",
    "generated_tokens_changed",
    "old_answer_reappeared",
    "neighbour_changed",
)


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def quantile(values, q):
    ordered = sorted(values)
    x = (len(ordered) - 1) * q
    lo = math.floor(x)
    return ordered[lo] + (x - lo) * (ordered[min(lo + 1, len(ordered) - 1)] - ordered[lo])


def tail_sum(values, fraction):
    ordered = sorted(values, reverse=True)
    mass = len(ordered) * fraction
    whole = math.floor(mass)
    return math.fsum(ordered[:whole]) + (mass - whole) * (
        ordered[whole] if whole < len(ordered) else 0
    )


def statistics(values, locations, unit="nats"):
    if len(values) != len(locations) or not values:
        raise ValueError("nonempty paired values/locations required")
    if any(not math.isfinite(x) for x in values):
        raise ValueError("nonfinite values are a failed assay, never dropped")
    n = len(values)
    positive = [max(0.0, v) for v in values]
    total = math.fsum(positive)
    maximum = max(values)
    ties = [loc for v, loc in zip(values, locations, strict=True) if v == maximum]
    return {
        "n": n,
        "unit": unit,
        "mean_signed": math.fsum(values) / n,
        "mean_positive": total / n,
        "median_positive": quantile(positive, 0.5),
        "p95_positive": quantile(positive, 0.95),
        "p99_positive": quantile(positive, 0.99),
        "ES95_positive": tail_sum(positive, 0.05) / (0.05 * n),
        "maximum_signed": maximum,
        "maximum_positive": max(positive),
        "maximum_location": ties[0],
        "maximum_tie_count": len(ties),
        "exceedances_nats": {
            str(t): {"count": sum(x > t for x in values), "denominator": n}
            for t in (0.01, 0.1, 1.0)
        }
        if unit == "nats"
        else None,
        "worst_1pct_positive_sum": tail_sum(positive, 0.01),
        "total_positive_sum": total,
        "worst_1pct_share_positive": tail_sum(positive, 0.01) / total if total else None,
        "atom_zero_signed": {"count": sum(x == 0 for x in values), "denominator": n},
        "atom_zero_positive": {"count": sum(x == 0 for x in positive), "denominator": n},
        "negative_count": sum(x < 0 for x in values),
        "quantile_definition": "linear interpolation, index (n-1)*q; positive harms",
        "tail_definition": "fractional empirical tail mass; ES95=sum of largest 0.05*n positive harms / (0.05*n), including fractional boundary observation",
    }


def row_sets(value, address="$", context=None):
    if isinstance(value, dict):
        context = {
            **(context or {}),
            **{
                k: value[k]
                for k in (
                    "checkpoint",
                    "tag",
                    "source_sha256",
                    "dataset",
                    "edited_items",
                    "reference_policy",
                    "reference_base_sha256",
                    "items",
                )
                if k in value and not isinstance(value[k], (list, dict))
            },
        }
        if isinstance(value.get("rows"), list):
            yield address + ".rows", value["rows"], context
        if isinstance(value.get("history"), list):
            yield address + ".history", value["history"], context
        for key, child in value.items():
            if key not in ("rows", "history") and isinstance(child, (dict, list)):
                yield from row_sets(child, address + "." + key, context)
    elif isinstance(value, list):
        if value and all(isinstance(r, dict) and ("item_id" in r or "case_id" in r) for r in value):
            yield address, value, context or {}
            return
        for i, child in enumerate(value):
            yield from row_sets(child, f"{address}[{i}]", context)


def series_from_rows(rows, address, context):
    if not rows:
        return [], [
            {"address": address, "reason": "empty row set; endpoint unavailable/not exercised"}
        ]
    if not all(isinstance(r, dict) for r in rows):
        return [], [{"address": address, "reason": "unsupported non-object row schema"}]
    available = set.intersection(*(set(r) for r in rows))
    fields = []
    if {"cap", "capoff", "original"} <= available:
        for reference in ("original", "capoff"):
            fields.append(
                (
                    f"preservation_nll_minus_{reference}",
                    "nats",
                    lambda r, ref=reference: float(r["cap"]) - float(r[ref]),
                )
            )
    for field in SUCCESS_FIELDS:
        if field in available:
            fields.append(
                (field + "_error", "error_fraction", lambda r, f=field: 1.0 - float(r[f]))
            )
    for field in HARM_FIELDS:
        if field in available:
            fields.append((field, "error_fraction", lambda r, f=field: float(r[f])))
    if "nll" in available:
        fields.append(
            ("new_answer_learning_nll", "target_nats_not_preservation", lambda r: float(r["nll"]))
        )
    outputs, missing = [], []
    for name, unit, get in fields:
        try:
            values = [get(r) for r in rows]
            if any(r.get("status", "ok") not in ("ok", "accepted") for r in rows):
                raise ValueError("non-ok row status; outcome not counted as success/zero")
            if unit == "error_fraction" and any(not 0 <= x <= 1 for x in values):
                raise ValueError("error fraction outside [0,1]")
            locations, keys, windows = [], [], set()
            pairing_strength = (
                "source item identity; prompt/target equality not independently certified"
            )
            for i, row in enumerate(rows):
                identity = row.get("item_id", row.get("case_id"))
                if identity is None:
                    raise ValueError("row identity missing")
                locations.append({"item_id": identity, "row": i})
                if name.startswith("preservation_nll"):
                    source = context.get("source_sha256")
                    if not source:
                        raise ValueError("window source hash missing")
                    window = str(identity).split(":p")[0]
                    windows.add(window)
                    # Matching reference value guards mismatched base/context scores.
                    ref = "original" if name.endswith("original") else "capoff"
                    key = [source, identity, row[ref]]
                    pairing_strength = "same bound window source, position ID and reference NLL"
                else:
                    prompt = row.get("query", row.get("reference", {})).get("prompt_sha256")
                    source = row.get("source_row_sha256")
                    key = [row.get("dataset", context.get("dataset")), identity, source, prompt]
                keys.append(digest(key))
            if len(set(keys)) != len(keys):
                raise ValueError("duplicate within-series identities")
            stat = statistics(values, locations, "nats" if unit == "nats" else unit)
            outputs.append(
                {
                    "address": address,
                    "metric": name,
                    "statistics": stat,
                    "context": context,
                    "items": len(set(r.get("item_id", r.get("case_id")) for r in rows)),
                    "windows": len(windows) if windows else None,
                    "pairing_strength": pairing_strength,
                    "_values": dict(zip(keys, values, strict=True)),
                    "_locations": dict(zip(keys, locations, strict=True)),
                }
            )
        except (ValueError, TypeError, OverflowError) as exc:
            missing.append(
                {"address": address, "metric": name, "reason": str(exc), "status": "failed"}
            )
    if not fields:
        missing.append(
            {
                "address": address,
                "reason": "no supported per-item outcome fields",
                "available_fields": sorted(available),
            }
        )
    return outputs, missing


def audit(output):
    result_root = ROOT / "results/R1"
    paths = sorted({p for pattern in PATTERNS for p in result_root.glob(pattern)})
    series, sources, missing, excluded = [], [], [], []
    for path in paths:
        if path.is_symlink() or not path.resolve().is_relative_to(result_root):
            raise PermissionError("external result path refused")
        raw = path.read_bytes()
        h = hashlib.sha256(raw).hexdigest()
        name = str(path.relative_to(ROOT))
        sources.append({"path": name, "sha256": h, "bytes": len(raw)})
        try:
            document = (
                [json.loads(line) for line in raw.splitlines() if line.strip()]
                if path.suffix == ".jsonl"
                else json.loads(raw)
            )
        except (ValueError, UnicodeError) as exc:
            missing.append(
                {
                    "path": name,
                    "status": "failed",
                    "reason": "incomplete/malformed input: " + str(exc),
                }
            )
            continue
        if path.suffix == ".jsonl":
            sets = [("$", document, {})]
        else:
            sets = list(row_sets(document))
        if not sets:
            if ".receipt." in path.name:
                excluded.append({"path": name, "reason": "checkpoint receipt, not assay rows"})
            else:
                missing.append(
                    {
                        "path": name,
                        "reason": "aggregate only; per-item distributions cannot be reconstructed",
                    }
                )
        expanded = []
        for address, rows, context in sets:
            groups_by_dataset = defaultdict(list)
            for row in rows:
                groups_by_dataset[row.get("dataset") if isinstance(row, dict) else None].append(row)
            if len(groups_by_dataset) > 1:
                for ds, subset in groups_by_dataset.items():
                    expanded.append((address + "@" + str(ds), subset, {**context, "dataset": ds}))
            else:
                expanded.append((address, rows, context))
        for address, rows, context in expanded:
            # A dataset label may be absent in the assay wrapper, but present in rows.
            datasets = sorted(
                {r["dataset"] for r in rows if isinstance(r, dict) and r.get("dataset")}
            )
            if len(datasets) == 1:
                context = {**context, "dataset": datasets[0]}
            extracted, gaps = series_from_rows(rows, address, context)
            for item in extracted:
                item.update(source=name, source_sha256=h, series_id=f"s{len(series):05d}")
                series.append(item)
            missing.extend({"path": name, **gap} for gap in gaps)
        # A streamed file that changed during parsing is not admitted in this snapshot.
        if hashlib.sha256(path.read_bytes()).hexdigest() != h:
            raise RuntimeError(
                "input changed during audit; rerun into a new output directory: " + name
            )
    # Exhaustive shared-row comparisons, streamed to avoid retaining a quadratic output.
    groups = defaultdict(list)
    for item in series:
        groups[(item["metric"], item["statistics"]["unit"])].append(item)
    paired_count = 0
    with gzip.open(output / "paired.jsonl.gz", "xt", encoding="utf-8") as stream:
        for group in groups.values():
            for a, b in itertools.combinations(group, 2):
                if a["source"] == b["source"]:
                    continue
                keys = sorted(a["_values"].keys() & b["_values"].keys())
                if not keys:
                    continue
                delta = [b["_values"][key] - a["_values"][key] for key in keys]
                row = {
                    "left": a["series_id"],
                    "right": b["series_id"],
                    "metric": a["metric"],
                    "shared_n": len(keys),
                    "left_only": len(a["_values"]) - len(keys),
                    "right_only": len(b["_values"]) - len(keys),
                    "shared_identity_sha256": digest(keys),
                    "comparison": "right minus left on shared observations; exploratory, checkpoint/population differences retained in source series",
                    "statistics": statistics(
                        delta, [a["_locations"][key] for key in keys], a["statistics"]["unit"]
                    ),
                }
                stream.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
                paired_count += 1
    for item in series:
        del item["_values"], item["_locations"]
    report = {
        "task": "HT-1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_inventory": sources,
        "series": series,
        "missing_data": missing,
        "excluded": excluded,
        "paired_series_comparisons": paired_count,
        "patterns": PATTERNS,
        "test_fixtures": "nested test directories do not match these one-level assay globs",
        "limits": [
            "Snapshot of development results only; repeat on final selected reader before freeze.",
            "No NLL preservation inference from new-answer learning loss or binary task failure.",
            "Pairing is descriptive shared-observation analysis, not matched training or causal attribution.",
            "Positions within windows and orders within realizations are dependent; no iid intervals or power-law fit.",
            "Unchanged-source check covers each read; concurrent newly created files await the next audit.",
            "Historical near-miss/revision summaries without row files remain unavailable.",
        ],
        "gpu_seconds": 0,
        "model_calls": 0,
    }
    for source in sources:
        p = ROOT / source["path"]
        if hashlib.sha256(p.read_bytes()).hexdigest() != source["sha256"]:
            raise RuntimeError("source changed before snapshot completion: " + source["path"])
    with (output / "audit.json").open("x") as stream:
        json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(
        json.dumps(
            {
                "source_files": len(sources),
                "series": len(series),
                "paired_comparisons": paired_count,
                "missing_records": len(missing),
            }
        )
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT / "logs/heavy_tail"):
        parser.error("new directory under logs/heavy_tail required")
    output.mkdir(parents=True)
    audit(output)


if __name__ == "__main__":
    main()
