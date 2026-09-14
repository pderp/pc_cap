"""Read-only R1-47 addendum for continuation jobs completed after the draft cutoff."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAGS = ("r1_24_literal_v3b", "r1_24_lm_v2b")


def collect():
    sources = {}

    def bind(path, expected=None):
        p = Path(path)
        if not p.is_absolute():
            p = ROOT / p
        with p.open("rb") as f:
            actual = hashlib.file_digest(f, "sha256").hexdigest()
        if expected and actual != expected:
            raise ValueError("source identity mismatch: " + str(p))
        sources[str(p)] = actual
        return p

    def read(path):
        return json.loads(bind(path).read_text())

    for file in (
        "scripts/r1_24_runtime.py",
        "scripts/r1_24_lm_runtime.py",
        "src/pccap/harness/runs.py",
        "src/pccap/revision_v1/learner.py",
        "src/pccap/bases/bp.py",
    ):
        bind(file)
    jobs, original_ids = [], {}
    for tag in TAGS:
        root = ROOT / "results/R1/r1_24" / tag
        summary = read(root / "summary.json")
        if summary["status"] != "complete" or summary["training"]["status"] != "complete":
            raise ValueError("closed job required")
        manifest_path = bind(summary["manifest"], summary["manifest_sha256"])
        manifest = json.loads(manifest_path.read_text())
        checkpoint = summary["checkpoint"]
        bind(checkpoint["path"], checkpoint["sha256"])
        bind(manifest["evaluation"]["theta"]["path"], manifest["evaluation"]["theta"]["sha256"])
        bind(manifest["evaluation"]["drift"]["path"], manifest["evaluation"]["drift"]["sha256"])
        steps = [
            json.loads(s) for s in bind(root / "training_steps.jsonl").read_text().splitlines()
        ]
        total = sum(s["forward_pass_tokens"] for s in steps)
        if total != summary["training"]["forward_pass_tokens"] or not all(
            s["accepted"] for s in steps
        ):
            raise ValueError("training accounting or accepted-step mismatch")
        fidelity = summary["fidelity"]
        expected_pass = (
            fidelity["ordinary_kl_nats"] <= manifest["evaluation"]["margins"]["kl_nats"]
            and fidelity["nll_increase"] <= manifest["evaluation"]["margins"]["nll_increase"]
        )
        if fidelity["fidelity_pass"] != expected_pass:
            raise ValueError("fidelity classification mismatch")
        rows = []
        for row in summary["evaluations"]:
            ds, base, cap = row["dataset"], row["base"], row["cap"]
            rd = root / ds / base / cap
            saved = read(rd / "control_endpoint.json")
            if saved != row:
                raise ValueError("summary endpoint differs")
            metrics = read(rd / "metrics.json")
            items = [json.loads(s) for s in bind(rd / "items.jsonl").read_text().splitlines()]
            final = next(c for c in read(rd / "checkpoints.json") if c["tag"] == "end")
            ids = [r["item_id"] for r in items]
            if (
                metrics["status"] != "complete"
                or len(items) != 100
                or ids != row["ordered_item_ids"]
                or ids != [r["item_id"] for r in final["rows"]]
                or {r["dataset"] for r in items} != {ds}
            ):
                raise ValueError("stream identity/completion mismatch")
            if ds in original_ids and original_ids[ds] != ids:
                raise ValueError("unpaired evaluation items")
            original_ids[ds] = ids
            observed = {
                "es_immediate": statistics.mean(i["es"] for i in items),
                "ret_es_end": statistics.mean(i["ret_es"] for i in final["rows"]),
                "ret_gs_end": statistics.mean(i["ret_gs"] for i in final["rows"]),
                "ls_complete_answer_end": final["locality"]["ls_complete_answer"],
            }
            for key, value in observed.items():
                if not math.isclose(
                    value, metrics["metrics"][key]["value"], abs_tol=1e-12
                ) or not math.isclose(
                    value, row["metrics"]["metrics"][key]["value"], abs_tol=1e-12
                ):
                    raise ValueError("stream metric mismatch")
            drift = row["drift"]
            if not math.isclose(
                math.exp(drift["loss_difference"]), drift["perplexity_ratio"], rel_tol=1e-12
            ):
                raise ValueError("drift arithmetic mismatch")
            rows.append(
                {
                    "dataset": ds,
                    "base": base,
                    "cap": cap,
                    "metrics": observed,
                    "drift": drift,
                    "base_checksum": row["base_checksum"],
                    "locality_n": final["locality"]["n"],
                    "items_n": len(items),
                    "endpoint_path": str(rd / "control_endpoint.json"),
                }
            )
        if len(rows) != 8 or len({(r["dataset"], r["base"], r["cap"]) for r in rows}) != 8:
            raise ValueError("eight unique development evaluation cells required")
        jobs.append(
            {
                "tag": tag,
                "summary_path": str(root / "summary.json"),
                "manifest": str(manifest_path),
                "checkpoint": checkpoint,
                "fidelity": fidelity,
                "training": summary["training"],
                "lease": summary["lease"],
                "rows": rows,
                "training_steps_verified": len(steps),
                "forward_tokens_recounted": total,
                "first_step": steps[0],
                "maximum_logged_gradient_norm": max(s["grad_norm"] for s in steps),
                "minimum_logged_loss": min(s["loss"] for s in steps),
                "scope": "completed development evidence; no final checkpoint admission",
            }
        )
    # S0/R0 repetitions are the same conditions/items, not fresh independent replicates.
    repeated_equal = True
    for a in [r for r in jobs[0]["rows"] if r["base"] == "original"]:
        b = next(
            r
            for r in jobs[1]["rows"]
            if (r["dataset"], r["base"], r["cap"]) == (a["dataset"], a["base"], a["cap"])
        )
        repeated_equal &= a["metrics"] == b["metrics"] and a["drift"] == b["drift"]
    for path, expected in list(sources.items()):
        bind(path, expected)
    return {
        "task": "R1-47 completion addendum",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "sources_sha256": sources,
        "jobs": jobs,
        "all_16_cells_recounted": True,
        "original_reference_metrics_drift_identical_between_jobs": repeated_equal,
        "gpu_seconds_by_reviewer": 0,
        "model_execution_by_reviewer": False,
        "full_validation_complete": False,
        "drift_policy": "each next-token prefix is an independent query; BoundaryEvaluator resets and selects at full current prefix",
        "drift_vs_fidelity": "drift uses prepared drift_tokens.npy (16256 positions); fidelity uses held-out OWT shard (8192 positions)",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository review output required")
    result = collect()
    with args.output.open("x") as f:
        f.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "cells_recounted": sum(len(j["rows"]) for j in result["jobs"]),
                "training_steps": {j["tag"]: j["training_steps_verified"] for j in result["jobs"]},
                "fidelity_pass": {j["tag"]: j["fidelity"]["fidelity_pass"] for j in result["jobs"]},
                "sources_bound": len(result["sources_sha256"]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
