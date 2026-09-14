"""R1-47: read-only recount and source inventory for the Stage 2 draft."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def collect():
    sources, streams, problems = {}, [], []

    def bind(rel):
        p = Path(rel)
        if not p.is_absolute():
            p = ROOT / p
        sources[str(p)] = sha(p)
        return p

    def read(rel):
        return json.loads(bind(rel).read_text())

    for file in (
        "scripts/r1_47_evidence.py",
        "docs/pc_cap_month_plan_readable.pdf",
        "docs/report.md",
        "docs/R1_diagnosis.md",
        "docs/R1_stage2_notes.md",
        "docs/updated_plan9.md",
        "docs/decisions.md",
        "results/R1/stream_eval.md",
        "logs/review_r1_stage2.md",
        "logs/review_r1_50.md",
        "logs/review_r1_50_response.md",
        "logs/audit_r1_28b.md",
        "manifests/revision_v1/primary_condition_v1.json",
        "manifests/revision_v1/run_matrix_draft_v3.json",
        "manifests/revision_v1/counterfact_fresh_candidates_v1.json",
        "manifests/revision_v1/r1_24_budget_reconciliation_v1.json",
        "manifests/revision_v1/r1_24_control_v3.json",
        "manifests/revision_v1/r1_24_control_lm_v2.json",
        "src/pccap/harness/runs.py",
        "src/pccap/data/decode.py",
        "src/pccap/revision_v1/endpoints_unseen.py",
        "scripts/r1_13_stream_eval.py",
        "scripts/r1_50_stream_train.py",
    ):
        bind(file)
    ids_by_tag = {}
    for file in sorted((ROOT / "results/R1").glob("stream_eval_*.json")):
        d = read(file)
        tag = d["tag"]
        dataset = d.get("dataset", d["args"].get("dataset", "zsre"))
        entry = {
            "tag": tag,
            "summary_path": str(file),
            "dataset": dataset,
            "args": d["args"],
            "theta_hash": d["theta_hash"],
            "metrics": d["stream_metrics"],
            "records": d["records"],
            "wall_seconds": d["wall_seconds"],
            "bytes": d.get("bytes"),
            "detail_status": "missing",
            "ls_verification": "aggregate only; individual locality generation pairs not persisted",
        }
        rd = ROOT / "results/R1/streams_revision" / tag
        item_path = rd / "items.jsonl"
        if item_path.exists():
            rows = [json.loads(line) for line in bind(item_path).read_text().splitlines()]
            datasets = {r["dataset"] for r in rows}
            entry["detail_datasets"] = sorted(datasets)
            if datasets != {dataset}:
                entry["detail_status"] = "historical_overwritten_by_other_dataset"
            else:
                metrics = read(rd / "metrics.json")
                checkpoints = read(rd / "checkpoints.json")
                final = next(c for c in checkpoints if c["tag"] == "end")
                ids = [r["item_id"] for r in rows]
                end = final["rows"]
                if len(ids) != len(set(ids)) or ids != [r["item_id"] for r in end]:
                    problems.append({"tag": tag, "problem": "identity mismatch"})
                ids_by_tag[tag] = set(ids)
                recount = {
                    "es_immediate": statistics.mean(r["es"] for r in rows),
                    "ret_es_end": statistics.mean(r["ret_es"] for r in end),
                    "ret_gs_end": statistics.mean(
                        r["ret_gs"] for r in end if r["ret_gs"] is not None
                    ),
                    "ls_complete_answer_end": final["locality"]["ls_complete_answer"],
                }
                entry.update(
                    detail_status="dataset_matches_recounted",
                    recount=recount,
                    status=metrics["status"],
                    items=len(ids),
                    paraphrase_count_histogram=dict(Counter(r["gs_n"] for r in rows)),
                    immediate_answer_token_histogram=dict(
                        Counter(r["answer_tokens"] for r in rows)
                    ),
                    counts={k: metrics["metrics"][k]["n"] for k in recount},
                    ordered_item_ids_sha256=hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
                    full_drift_status=metrics["metrics"]["lm_drift_loss_difference"]["status"],
                    base_hash_before=metrics.get("base_hash_before"),
                    base_hash_after=metrics.get("base_hash_after"),
                )
                for k, value in recount.items():
                    if not math.isclose(value, d["stream_metrics"][k], abs_tol=1e-12):
                        problems.append(
                            {
                                "tag": tag,
                                "metric": k,
                                "recount": value,
                                "summary": d["stream_metrics"][k],
                            }
                        )
                    if not math.isclose(value, metrics["metrics"][k]["value"], abs_tol=1e-12):
                        problems.append(
                            {"tag": tag, "metric": k, "problem": "detail aggregate mismatch"}
                        )
        streams.append(entry)
    controls = {
        k: read("results/R1/" + k + ".json")
        for k in ("v0_stable_C1", "v0_stable_C2", "matched_update_C1", "matched_update_C2")
    }
    pilot = read("results/R1/pilot/r1_50_stream_mixed/summary.json")
    profiles = {
        k: read("results/R1/scale_profile_" + k + ".json")
        for k in ("r1_50_stream_mixed", "r1_50_stream_mixed_top16", "r1_50_stream_mixed_m256")
    }
    audit = read("logs/r1_round7/x6_audit.json")
    overlap = {}
    for ds, suffix in (("zsre", ""), ("counterfact", "@counterfact")):
        a, b = ids_by_tag["mixed_null0.5" + suffix], ids_by_tag["mixed_stream22_null0.5" + suffix]
        overlap[ds] = {"stream21_n": len(a), "stream22_n": len(b), "shared_items": len(a & b)}
    # Active owner continuation jobs deliberately excluded from this closed evidence inventory.
    result = {
        "task": "R1-47",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "sources_sha256": sources,
        "stream_summaries": streams,
        "stream_recount_discrepancies": problems,
        "detail_status_counts": dict(Counter(r["detail_status"] for r in streams)),
        "stream_overlap": overlap,
        "controls": controls,
        "primary_training": {
            k: pilot[k]
            for k in (
                "args",
                "bank_wall_s",
                "train_wall_s",
                "total_wall_s",
                "best_step",
                "theta_hash",
                "dev_after_best",
            )
        },
        "scale_profiles": profiles,
        "scale_audit_risks": audit["risks"],
        "active_continuation_results": "not included; owner completion/admission review pending",
        "gpu_seconds": 0,
        "model_execution": False,
        "sealed_payloads_opened": 0,
    }
    for path, expected in sources.items():
        if sha(path) != expected:
            raise RuntimeError("source changed during recount: " + path)
    if problems:
        raise ValueError(json.dumps(problems, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository evidence path required")
    result = collect()
    with args.output.open("x") as f:
        f.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                k: result[k]
                for k in ("detail_status_counts", "stream_overlap", "stream_recount_discrepancies")
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
