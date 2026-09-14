"""Recount closed R1-24 development records; no model or accelerator execution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.r1_47_continuation_review import collect

ROOT = Path(__file__).resolve().parents[1]
BUDGET_SHA = "93bfdd619187a2df748d9cbbfa8f6206d011d09ce63f096184249a14d4fa419b"


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def review():
    result = collect()
    path = ROOT / "manifests/revision_v1/r1_24_budget_reconciliation_v1.json"
    if sha(path) != BUDGET_SHA:
        raise ValueError("review requires the declared reference budget")
    result["sources_sha256"][str(path)] = BUDGET_SHA
    budget = json.loads(path.read_text())
    if (
        budget["training_forward_pass_tokens"]
        != budget["outer_forward_tokens"] + budget["bank_construction_tokens"]
    ):
        raise ValueError("reference forward-token reconciliation failed")
    for source, expected in budget["pilot_sources_sha256"].items():
        if sha(source) != expected:
            raise ValueError("reference ledger execution identity changed")
        result["sources_sha256"][source] = expected
    result["sources_sha256"][str(Path(__file__).resolve())] = sha(__file__)
    result["reference_budget"] = budget
    result["contrasts"] = []
    for job in result["jobs"]:
        train = job["training"]
        used = job["forward_tokens_recounted"]
        is_literal = "literal" in job["tag"]
        expected_used = (
            2 * (budget["training_forward_pass_tokens"] // 2)
            if is_literal
            else budget["training_forward_pass_tokens"]
        )
        if used != expected_used or not train["matched_budget_claim"]:
            raise ValueError("continuation training budget mismatch")
        job["forward_budget_remainder"] = budget["training_forward_pass_tokens"] - used
        job["fidelity_eligible"] = job["fidelity"]["fidelity_pass"]
        job["exact_parameter_noop"] = (
            job["checkpoint"]["original_tensor_digest"]
            == job["checkpoint"]["continued_tensor_digest"]
        )
        if not all(
            row["base_checksum"]
            == job["checkpoint"][
                "original_tensor_digest" if row["base"] == "original" else "continued_tensor_digest"
            ]
            for row in job["rows"]
        ):
            raise ValueError("evaluation base checksum mismatch")
        for dataset in ("zsre", "counterfact"):
            rows = [r for r in job["rows"] if r["dataset"] == dataset]

            def row(base, learned, rows=rows):
                return next(
                    r for r in rows if r["base"] == base and (r["cap"] != "v0_stable_C1") == learned
                )

            s0, s1, r0 = row("original", False), row("continued", False), row("original", True)
            for name, treatment, control in (("S1_minus_S0", s1, s0), ("R0_minus_S1", r0, s1)):
                delta = {
                    k: treatment["metrics"][k] - control["metrics"][k]
                    for k in ("es_immediate", "ret_es_end", "ret_gs_end", "ls_complete_answer_end")
                }
                result["contrasts"].append(
                    {
                        "job": job["tag"],
                        "dataset": dataset,
                        "contrast": name,
                        "treatment_endpoint": treatment["endpoint_path"],
                        "control_endpoint": control["endpoint_path"],
                        "difference": delta,
                        "items": treatment["items_n"],
                        "locality_prompts": treatment["locality_n"],
                        "point_only_margin_checks": {
                            "ret_gs_at_least_0.05": delta["ret_gs_end"] >= 0.05 - 1e-12,
                            "es_at_least_minus_0.02": delta["es_immediate"] >= -0.02 - 1e-12,
                            "ls_at_least_minus_0.01": delta["ls_complete_answer_end"]
                            >= -0.01 - 1e-12,
                        },
                        "fidelity_eligible": job["fidelity_eligible"],
                        "classification": "development_point_estimate_only_no_cluster_interval",
                    }
                )
    result["task"] = "R1-X7"
    result["matched_interpretation"] = (
        "forward-pass-token matching only; a failed fidelity gate remains failed"
    )
    result["independent_confirmatory_realizations"] = 0
    result["no_cap_attribution_resolved"] = False
    result["notes_snapshot"] = "logs/r1_round8/source_snapshot/docs/R1_stage2_notes.md"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository output required")
    result = review()
    with args.output.open("x") as f:
        f.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "cells_recounted": 16,
                "contrasts": len(result["contrasts"]),
                "sources_bound": len(result["sources_sha256"]),
                "training_steps": {j["tag"]: j["training_steps_verified"] for j in result["jobs"]},
                "fidelity_pass": {j["tag"]: j["fidelity_eligible"] for j in result["jobs"]},
                "gpu_seconds": 0,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
