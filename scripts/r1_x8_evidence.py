"""R1-59/X8: recount stored profiles, streams and unseen summaries on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def collect():
    sources = {}

    def bind(p):
        p = Path(p)
        if not p.is_absolute():
            p = ROOT / p
        with p.open("rb") as f:
            sources[str(p)] = hashlib.file_digest(f, "sha256").hexdigest()
        return p

    def read(p):
        return json.loads(bind(p).read_text())

    profiles = []
    for tag in ("text_s0", "nonlearned", "nonlearned_v2"):
        for ds in ("zsre", "counterfact"):
            directory = ROOT / f"results/R1/p1_profile/{tag}_{ds}"
            summary, edits, queries = (
                read(directory / name) for name in ("summary.json", "edits.json", "queries.json")
            )
            if (
                len(edits) != 1000
                or [r["i"] for r in edits] != list(range(1000))
                or len({r["item_id"] for r in edits}) != 1000
            ):
                raise ValueError("profile edit coverage mismatch")
            checkpoints = []
            for cp in summary["checkpoints"]:
                rows = [r for r in queries if r["checkpoint"] == cp["label"]]
                times = [r["wall_s"] for r in rows]
                if len(rows) != cp["query_wall_s"]["n"] or not math.isclose(
                    float(np.median(times)), cp["query_wall_s"]["p50"], abs_tol=1e-12
                ):
                    raise ValueError("profile query recount mismatch")
                rates = {
                    role: sum(r["fired"] for r in rows if r["role"] == role)
                    / sum(r["role"] == role for r in rows)
                    for role in ("own", "locality")
                }
                if rates != cp["fired_by_role"]:
                    raise ValueError("profile firing recount mismatch")
                if cp["bytes"]["total"] != sum(v for k, v in cp["bytes"].items() if k != "total"):
                    raise ValueError("profile byte sum mismatch")
                checkpoints.append(
                    {
                        "occupancy": cp["occupancy"],
                        "records_total": cp["records_total"],
                        "bytes": cp["bytes"],
                        "ceiling_fraction": cp["ceiling_fraction"],
                        "restore": cp["restore"],
                        "query_count": len(rows),
                        "query_p50_seconds": float(np.median(times)),
                        "query_p95_seconds": float(np.percentile(times, 95)),
                        "fired_by_role": rates,
                        "delta_positions": cp["delta_positions"],
                        "device_peak_mib": cp["device_peak_mib"],
                        "rss_mib": cp["rss_mib"],
                    }
                )
            profiles.append(
                {
                    "path": str(directory / "summary.json"),
                    "tag": tag,
                    "dataset": ds,
                    "semantic_config": summary["semantic_config"],
                    "theta": summary["theta"],
                    "memory_content": summary["memory_content"],
                    "checkpoints": checkpoints,
                    "edit_wall_sum_seconds": sum(r["wall_s"] for r in edits),
                    "warm_edit_median_seconds": float(np.median([r["wall_s"] for r in edits[1:]])),
                    "query_wall_sum_seconds": sum(r["wall_s"] for r in queries),
                    "profile_wall_seconds": summary["wall_seconds"],
                    "edit_codes": summary["edit_codes"],
                    "all_1000_rows_recounted": True,
                    "query_prompt_ids_saved": any(
                        "item_id" in r or "prompt_ids" in r for r in queries
                    ),
                    "query_answer_text_saved": any("generated" in r for r in queries),
                }
            )
    unseen = []
    for path in sorted((ROOT / "results/R1/endpoints").glob("text_*_unseen_*/summary.json")):
        s = read(path)
        report_path = path.parent / "report.json"
        report = read(report_path)
        rows = report["rows"]
        counts = {
            "scored_n": sum(r["status"] == "ok" for r in rows),
            "false_fires": sum(r.get("false_fire") is True for r in rows),
            "answer_changes": sum(r.get("answer_changed") is True for r in rows),
            "both_answers_terminated_n": sum(
                r.get("both_answers_terminated") is True for r in rows
            ),
            "complete_answer_preserved_n": sum(
                r.get("complete_answer_preserved") is True for r in rows
            ),
        }
        if [r["item_id"] for r in rows] != s["outside_item_ids"]:
            raise ValueError("outside summary/report order mismatch")
        for key, value in counts.items():
            if key in s["summary"] and s["summary"][key] != value:
                raise ValueError("unseen denominator/count mismatch")
        if counts["scored_n"] == s["summary"]["expected_n"]:
            expected = counts["complete_answer_preserved_n"] / counts["scored_n"]
            if expected != s["summary"]["complete_answer_preservation_rate_full_inventory"]:
                raise ValueError("strict complete-preservation denominator mismatch")
        unseen.append(
            {
                "path": str(path),
                "tag": path.parent.name,
                "dataset": s["dataset"],
                "n_edits": s.get("n_edits", 100),
                "outside_source": s.get("outside_source", "dev_remainder"),
                "outside_ids": s["outside_item_ids"],
                "edited_ids": s["edited_item_ids"],
                "summary": s["summary"],
                "counts_recounted": counts,
                "wall_seconds": s["wall_seconds"],
                "theta": s["theta"],
                "gate_in_summary": "rare_overlap_min" in s.get("reader", {})
                or "semantic_config" in s,
            }
        )
    overlaps = []
    for ds in ("zsre", "counterfact"):
        tags = [
            f"text_s0_n100pool_unseen_{ds}",
            f"text_s0_n300_unseen_{ds}",
            f"text_s0_n1000_unseen_{ds}",
        ]
        rows = [next(r for r in unseen if r["tag"] == tag) for tag in tags]
        for a, b in zip(rows, rows[1:]):
            overlaps.append(
                {
                    "dataset": ds,
                    "from": a["tag"],
                    "to": b["tag"],
                    "outside_overlap": len(set(a["outside_ids"]) & set(b["outside_ids"])),
                    "same_ordered_outside": a["outside_ids"] == b["outside_ids"],
                    "edited_overlap": len(set(a["edited_ids"]) & set(b["edited_ids"])),
                }
            )
    streams = []
    for seed in (0, 1, 2):
        stem = "mixed_text" + (f"_s{seed}" if seed else "")
        for gate in (False, True):
            for ds in ("zsre", "counterfact"):
                tag = (
                    stem
                    + ("_rare1" if gate else "")
                    + "_null0.5"
                    + (f"@{ds}" if ds != "zsre" else "")
                )
                s = read(f"results/R1/stream_eval_{tag}.json")
                directory = ROOT / "results/R1/streams_revision" / tag
                with bind(directory / "items.jsonl").open() as f:
                    items = [json.loads(line) for line in f]
                cp = next(r for r in read(directory / "checkpoints.json") if r["tag"] == "end")
                expected = {
                    "es_immediate": float(np.mean([r["es"] for r in items])),
                    "ret_es_end": float(np.mean([r["ret_es"] for r in cp["rows"]])),
                    "ret_gs_end": float(np.mean([r["ret_gs"] for r in cp["rows"]])),
                    "ls_complete_answer_end": cp["locality"]["ls_complete_answer"],
                }
                if [r["item_id"] for r in items] != [r["item_id"] for r in cp["rows"]] or len(
                    items
                ) != 100:
                    raise ValueError("development stream identity mismatch")
                if any(
                    not math.isclose(expected[k], s["stream_metrics"][k], abs_tol=1e-12)
                    for k in expected
                ):
                    raise ValueError("development stream metric mismatch")
                streams.append(
                    {
                        "tag": tag,
                        "dataset": ds,
                        "reader_seed": seed,
                        "rare_gate": gate,
                        "metrics": expected,
                        "items": 100,
                        "locality_n": cp["locality"]["n"],
                        "path": f"results/R1/stream_eval_{tag}.json",
                    }
                )
    drift = []
    for stem in ("r1_50_stream_mixed", "r1_50_stream_mixed_text"):
        for ds in ("zsre", "counterfact"):
            path = f"results/R1/drift_assay_{stem}_{ds}.json"
            d = read(path)
            for rule, result in d["rules"].items():
                if not math.isclose(
                    math.exp(result["delta_nats"]), result["ppl_ratio"], rel_tol=1e-12
                ):
                    raise ValueError("drift ratio mismatch")
                n = d["windows"] * (d["window"] - 1)
                drift.append(
                    {
                        "path": path,
                        "reader": stem,
                        "dataset": ds,
                        "rule": rule,
                        "scored_positions": n,
                        "probe_positions": d["windows"] * 3,
                        **result,
                        "recounted_fires": round(n * result["fire_rate_all_scored_positions"])
                        if "fire_rate_all_scored_positions" in result
                        else None,
                    }
                )
    primary = read("manifests/revision_v1/primary_condition_v3.json")
    for ref in primary["weights"].values():
        p = bind(ref["path"])
        if sources[str(p)] != ref["sha256"]:
            raise ValueError("primary reader weights changed")
    for name in (
        "scripts/r1_55_p1_profile.py",
        "scripts/r1_44_unseen_run.py",
        "scripts/r1_43_endpoints_run.py",
        "scripts/r1_54_drift_assay.py",
        "src/pccap/revision_v1/learner.py",
        "src/pccap/revision_v1/memory.py",
    ):
        bind(name)
    # Recheck every source, including result files that could advance concurrently.
    for path, expected in list(sources.items()):
        with Path(path).open("rb") as f:
            actual = hashlib.file_digest(f, "sha256").hexdigest()
        if actual != expected:
            raise ValueError("review input changed during recount")
    return {
        "task": "R1-X8/R1-59",
        "profiles": profiles,
        "unseen": unseen,
        "outside_population_overlaps": overlaps,
        "streams": streams,
        "drift": drift,
        "sources_sha256": sources,
        "gpu_seconds": 0,
        "model_execution": False,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT / "logs"):
        raise ValueError("new review output under logs required")
    result = collect()
    with args.output.open("x") as f:
        f.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "profiles": len(result["profiles"]),
                "unseen": len(result["unseen"]),
                "streams": len(result["streams"]),
                "sources_bound": len(result["sources_sha256"]),
                "overlaps": result["outside_population_overlaps"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
