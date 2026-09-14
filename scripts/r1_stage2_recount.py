"""R1-X4 read-only ledger/table recount. No model, checkpoint load or GPU work."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = ("es_immediate", "ret_es_end", "ret_gs_end", "ls_complete_answer_end")
ADDITIVE = ("full_forwards", "partial_forwards", "reverses", "tokens", "accel_seconds")


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def mean(values):
    v = [x for x in values if x is not None]
    return sum(v) / len(v) if v else None


def ledger_check(ledger):
    return {k: ledger["total"][k] - ledger["learning"][k] - ledger["query"][k] for k in ADDITIVE}


def tables(text):
    result, current, heading = [], None, ""
    for line_no, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            heading = line[3:]
        if not line.startswith("|"):
            current = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r"[-: ]+", c) for c in cells):
            continue
        if current is None:
            current = {"heading": heading, "line": line_no, "header": cells, "rows": []}
            result.append(current)
        else:
            current["rows"].append({"line": line_no, "cells": cells})
    return result


def number_tokens(cell):
    return re.findall(
        r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?", cell.replace("**", ""), re.IGNORECASE
    )


def cell_check(cell, values):
    if not isinstance(values, list):
        values = [values]
    tokens = number_tokens(cell)[: len(values)]
    if not tokens or len(tokens) != len(values):
        return {"printed": cell, "source_values": values, "status": "not_numeric_or_not_reported"}
    if any(v is None for v in values):
        return {"printed": cell, "source_values": values, "status": "source_field_unavailable"}
    tolerances = []
    for token in tokens:
        if "e" in token.lower():
            tolerances.append(abs(float(token)) * 1e-8)
        else:
            places = len(token.split(".")[1]) if "." in token else 0
            tolerances.append(0.5 * 10 ** (-places))
    ok = all(abs(float(t) - v) <= tol + 1e-10 for t, v, tol in zip(tokens, values, tolerances))
    return {
        "printed": cell,
        "source_values": values,
        "status": "agrees_at_printed_precision" if ok else "mismatch",
    }


def recount():
    sources = {}

    def load(path, lines=False):
        p = Path(path)
        if not p.is_absolute():
            p = ROOT / p
        sources[str(p)] = sha(p)
        text = p.read_text()
        return [json.loads(s) for s in text.splitlines() if s] if lines else json.loads(text)

    def bind_text(path):
        p = ROOT / path
        sources[str(p)] = sha(p)
        return p.read_text()

    notes = bind_text("docs/R1_stage2_notes.md")
    stream_table = bind_text("results/R1/stream_eval.md")
    for path in (
        "scripts/r1_stage2_recount.py",
        "scripts/r1_21_pilot.py",
        "scripts/r1_13_stream_eval.py",
        "src/pccap/revision_v1/train.py",
        "src/pccap/revision_v1/epc_train.py",
        "src/pccap/revision_v1/adapt.py",
        "src/pccap/revision_v1/learner.py",
        "src/pccap/harness/runs.py",
        "docs/revision_v1_losses.md",
    ):
        bind_text(path)
    streams, stream_raw = [], {}
    for path in sorted((ROOT / "results/R1").glob("stream_eval_*.json")):
        obj = load(path)
        stem = path.stem[len("stream_eval_") :]
        ds = obj.get(
            "dataset",
            obj["args"].get("dataset", "counterfact" if "@counterfact" in stem else "zsre"),
        )
        root = ROOT / "results/R1/streams_revision" / stem
        legacy = ROOT / "results/R1/streams_revision" / stem.split("@")[0]
        if not root.exists() and legacy.exists():
            root = legacy
        detail = {"path": str(root), "available": root.exists(), "attribution": "missing"}
        if (root / "items.jsonl").exists():
            items = load(root / "items.jsonl", True)
            datasets = sorted({r.get("dataset") for r in items})
            detail.update(
                item_rows=len(items),
                datasets=datasets,
                item_ids_sha256=hashlib.sha256(
                    json.dumps([r["item_id"] for r in items]).encode()
                ).hexdigest(),
                attribution="dataset_matches"
                if datasets == [ds]
                else "different_dataset_collision",
                immediate_es=mean([r.get("es") for r in items]),
                immediate_gs=mean([r.get("gs") for r in items]),
                item_returned_cost_sum={
                    k: sum(r.get("cost", {}).get(k, 0) for r in items) for k in ADDITIVE
                },
            )
            if (root / "checkpoints.json").exists():
                checkpoints = load(root / "checkpoints.json")
                end = next((r for r in reversed(checkpoints) if r["tag"] == "end"), None)
                if end is not None:
                    rows = end["rows"]
                    metrics = {
                        "es_immediate": detail["immediate_es"],
                        "ret_es_end": mean([r.get("ret_es") for r in rows]),
                        "ret_gs_end": mean([r.get("ret_gs") for r in rows]),
                        "ls_complete_answer_end": end["locality"]["ls_complete_answer"],
                    }
                    detail.update(
                        recounted_metrics=metrics,
                        retained_item_denominator=len(rows),
                        retained_gs_item_denominator=sum(r.get("ret_gs") is not None for r in rows),
                        locality_denominator=end["locality"]["n"],
                        metric_differences={
                            k: metrics[k] - obj["stream_metrics"][k]
                            for k in METRICS
                            if metrics[k] is not None
                        },
                        gs_unit="mean within item, then mean across items; CounterFact normally two paraphrases/item",
                        locality_recount_scope="aggregate endpoint record only; per-locality generated rows not retained here",
                    )
            if (root / "cost.json").exists():
                cost = load(root / "cost.json")
                detail["cost_phase_sum_residuals"] = ledger_check(cost)
                detail["stream_end_ledger"] = cost
                detail["poststream_summary_query_delta"] = {
                    k: obj["ledger"]["query"][k] - cost["query"][k] for k in ADDITIVE
                }
                detail["learning_summary_minus_stream_end"] = {
                    k: obj["ledger"]["learning"][k] - cost["learning"][k] for k in ADDITIVE
                }
            if (root / "metrics.json").exists():
                metrics = load(root / "metrics.json")
                detail["completed"] = metrics["items_completed"]
                detail["status"] = metrics["status"]
                if "recounted_metrics" in detail:
                    detail["recount_minus_saved_metric"] = {
                        k: detail["recounted_metrics"][k] - metrics["metrics"][k]["value"]
                        for k in METRICS
                    }
        row = {
            "tag": stem,
            "dataset": ds,
            "path": str(path),
            "sha256": sources[str(path)],
            "args": obj["args"],
            "summary_metrics": obj["stream_metrics"],
            "n_requested": obj["args"]["n"],
            "bytes": obj.get("bytes"),
            "wall_seconds": obj["wall_seconds"],
            "ledger_elapsed_wall_seconds": obj["ledger"]["elapsed_wall_seconds"],
            "learning_accel_seconds": obj["ledger"]["learning"]["accel_seconds"],
            "query_accel_seconds": obj["ledger"]["query"]["accel_seconds"],
            "total_accel_seconds": obj["ledger"]["total"]["accel_seconds"],
            "phase_sum_residuals": ledger_check(obj["ledger"]),
            "null_mass": obj.get("null_mass"),
            "best_scores": obj.get("best_scores"),
            "detail": detail,
        }
        streams.append(row)
        stream_raw[stem] = obj
    # Also inventory every detailed item file, including any without a matching summary.
    detail_inventory = []
    for path in sorted((ROOT / "results/R1/streams_revision").glob("*/items.jsonl")):
        items = load(path, True)
        detail_inventory.append(
            {
                "path": str(path),
                "sha256": sources[str(path)],
                "rows": len(items),
                "datasets": sorted({r.get("dataset") for r in items}),
                "immediate_es": mean([r.get("es") for r in items]),
                "immediate_gs": mean([r.get("gs") for r in items]),
            }
        )
    pilots, pilot_raw = [], {}
    for path in sorted((ROOT / "results/R1/pilot").glob("*/summary.json")):
        obj = load(path)
        tag = obj["args"].get("tag", path.parent.name)
        pilots.append(
            {
                "tag": tag,
                "path": str(path),
                "sha256": sources[str(path)],
                "steps": obj["args"]["steps"],
                "args": obj["args"],
                "train_wall_seconds": obj["train_wall_s"],
                "total_wall_seconds": obj["total_wall_s"],
                "ledger_elapsed_wall_seconds": obj["ledger"]["elapsed_wall_seconds"],
                "learning_accel_seconds": obj["ledger"]["learning"]["accel_seconds"],
                "total_accel_seconds": obj["ledger"]["total"]["accel_seconds"],
                "ledger_learning": obj["ledger"]["learning"],
                "ledger_query": obj["ledger"]["query"],
                "phase_sum_residuals": ledger_check(obj["ledger"]),
                "dev_before": obj["dev_before"],
                "dev_after": obj["dev_after"],
                "behavioural_dev": obj["behavioural_dev"],
                "best_dev": obj.get("best_dev"),
                "final_after": obj.get("final_after"),
                "answer_roles": obj.get("answer_roles"),
                "metric_scope": "fixed-length pilot behavioral probe; not stream complete-answer endpoint",
                "zero_step_evaluation": obj["args"]["steps"] == 0,
            }
        )
        pilot_raw[tag] = obj

    def behavior(obj, role, preservation=False):
        r = obj["behavioural_dev"][role]
        return (
            r.get("unchanged_from_capoff")
            if preservation and "unchanged_from_capoff" in r
            else r.get("label_exact", r.get("exact_or_preserved"))
        )

    checked = []
    for table in tables(notes):
        heading = table["heading"]
        for row in table["rows"]:
            cells = row["cells"]
            checks = []
            provenance = []
            if table["header"][0] == "tag":
                tag = next(
                    (t for t in sorted(pilot_raw, key=len, reverse=True) if cells[0].startswith(t)),
                    None,
                )
                if tag:
                    o = pilot_raw[tag]
                    provenance = [f"pilot/{tag}/summary.json"]
                    checks += [
                        cell_check(cells[i], [o["dev_before"][key], o["dev_after"][key]])
                        for i, key in ((5, "answer"), (6, "retrieval"), (7, "preserve"))
                    ]
                    checks += [
                        cell_check(cells[i], behavior(o, role, i in (10, 11)))
                        for i, role in (
                            (8, "new_paraphrase"),
                            (9, "old_fact"),
                            (10, "near_miss"),
                            (11, "unrelated"),
                        )
                    ]
                    checks += [
                        cell_check(
                            cells[12],
                            [
                                o["behavioural_dev"][r]["null_mass_mean"]
                                for r in ("new_paraphrase", "near_miss", "unrelated")
                            ],
                        ),
                        cell_check(cells[13], o["train_wall_s"] / 60),
                    ]
            elif heading.startswith("Matched estimator comparison"):
                mapping = {
                    "answer NLL": "answer",
                    "retrieval CE (exact in both)": "retrieval",
                    "preservation KL": "preserve",
                }
                for i, tag in enumerate(("bp_500_lr1e-3", "epc_500_lr1e-3_sd24"), 1):
                    o = pilot_raw[tag]
                    provenance.append(f"pilot/{tag}/summary.json")
                    if cells[0] in mapping:
                        value = o["dev_after"][mapping[cells[0]]]
                    elif cells[0].startswith("paraphrase exact"):
                        value = [behavior(o, r) for r in ("new_paraphrase", "old_fact")]
                    elif cells[0].startswith("near-miss"):
                        value = [behavior(o, r, True) for r in ("near_miss", "unrelated")]
                    elif cells[0] == "wall":
                        value = o["train_wall_s"] / 60
                    else:
                        value = None
                    checks.append(cell_check(cells[i], value))
            else:
                tag = None
                offset = 1
                if table["header"][0] == "min cosine":
                    gate = cells[0].replace("**", "")
                    tag = (
                        "random_tied_cos_pdelta5_top1_nonull"
                        if gate == "none"
                        else "random_tied_cos_min" + gate
                    )
                elif heading.startswith("Trained similarity"):
                    tag = (
                        "random_tied_cos_min0.93"
                        if "random" in cells[1]
                        else "pairnull_delta5_gate0.93_bin"
                    )
                    offset = 2
                elif heading.startswith("Combined reader"):
                    tag = "pairown_delta5_null" + cells[1]
                    offset = 2
                elif heading.startswith("Balanced reader"):
                    tag = "pairownbal_delta5_null0.5"
                if tag:
                    if cells[0] == "CounterFact":
                        tag += "@counterfact"
                    o = stream_raw[tag]
                    provenance = [f"stream_eval_{tag}.json"]
                    checks.extend(
                        cell_check(cells[offset + i], o["stream_metrics"][key])
                        for i, key in enumerate(METRICS)
                    )
                    if heading.startswith("Balanced reader"):
                        checks.append(
                            cell_check(
                                cells[5],
                                [
                                    o["null_mass"][key]
                                    for key in ("prompt_mean", "paraphrase_mean", "unrelated_mean")
                                ],
                            )
                        )
            checked.append(
                {
                    "heading": heading,
                    "line": row["line"],
                    "cells": cells,
                    "provenance": provenance,
                    "checks": checks,
                    "status": "checked" if checks else "unmapped_requires_review",
                }
            )
    by_status = Counter(c["status"] for row in checked for c in row["checks"])
    collisions = [
        s["tag"] for s in streams if s["detail"]["attribution"] == "different_dataset_collision"
    ]
    report = {
        "task": "R1-X4",
        "sources_sha256": sources,
        "streams": streams,
        "pilots": pilots,
        "detailed_item_inventory": detail_inventory,
        "notes_table_rows": checked,
        "raw_stream_markdown_tables": tables(stream_table),
        "summary": {
            "stream_summaries": len(streams),
            "pilot_summaries": len(pilots),
            "completed_training_pilots": sum(not p["zero_step_evaluation"] for p in pilots),
            "detailed_item_files": len(detail_inventory),
            "notes_table_rows": len(checked),
            "numeric_check_statuses": dict(by_status),
            "unmapped_notes_rows": sum(r["status"] != "checked" for r in checked),
            "dataset_collisions": collisions,
            "completed_pilot_training_wall_seconds": sum(
                p["train_wall_seconds"] for p in pilots if not p["zero_step_evaluation"]
            ),
        },
        "gpu_seconds": 0,
        "model_queries_executed": 0,
        "limitations": [
            "Summary-derived rates are not independent raw-example recounts when detailed paths were overwritten.",
            "Per-locality decodes are not retained; only the saved aggregate can be checked.",
            "Integer phase sums can agree while direct autodiff/base work is missing from the ledger.",
            "Sources are development artifacts and reused thresholds; no confirmation inference.",
        ],
    }
    for path, h in sources.items():
        if sha(path) != h:
            raise RuntimeError("source changed during recount; use a fresh snapshot: " + path)
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    if a.output.exists() or not a.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository output required")
    report = recount()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open("x") as f:
        json.dump(report, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
