"""R1-X10 CPU recount of stored development evidence and loader behavior."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def loader_probe(source, manifest, n, dataset="zsre"):
    """Execute only the exact manifest-loading AST branch, with in-memory file content.
    No main(), model, tokenizer, lease or output path is executed.
    """
    tree = ast.parse(source)
    branch = next(
        x
        for x in ast.walk(tree)
        if isinstance(x, ast.If)
        and isinstance(x.test, ast.Attribute)
        and x.test.attr == "dev_manifest"
    )

    class MemoryPath:
        def __truediv__(self, other):
            return self

        def read_text(self):
            return json.dumps(manifest)

    ns = {
        "ROOT": MemoryPath(),
        "json": json,
        "args": SimpleNamespace(dev_manifest="fixture.json", stream_seed=21, n=n, dataset=dataset),
    }
    exec(compile(ast.Module(body=branch.body, type_ignores=[]), "<manifest-branch>", "exec"), ns)
    return ns["items"], ns["unrelated"]


def build():
    bindings = {}

    def read(path):
        p = Path(path)
        if not p.is_absolute():
            p = ROOT / p
        raw = p.read_bytes()
        bindings[str(p)] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)

    for rel in (
        "scripts/r1_d5_mquake_teacher.py",
        "scripts/r1_d6_mquake_split.py",
        "scripts/r1_60_composition_run.py",
        "scripts/r1_13_stream_eval.py",
        "src/pccap/revision_v1/reader.py",
        "src/pccap/revision_v1/learner.py",
        "src/pccap/revision_v1/train.py",
        "src/pccap/revision_v1/train_fast.py",
        "src/pccap/revision_v1/endpoints.py",
        "src/pccap/revision_v1/endpoints_composition.py",
        "docs/R1_stage2_notes.md",
    ):
        bindings[str(ROOT / rel)] = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    primary = read("manifests/revision_v1/primary_condition_v4.json")
    summary = read("results/R1/endpoints/v4_s0_dev300_composition/summary.json")
    report = read("results/R1/endpoints/v4_s0_dev300_composition/report.json")
    rows = report["rows"]
    scored = [r for r in rows if r["status"] == "ok"]
    queries = [q for r in scored for q in r["queries"]]
    composition = {
        "planned": len(rows),
        "scored_cases": len(scored),
        "queries": len(queries),
        "unavailable": [
            {"composition_id": r.get("composition_id"), "reason": r.get("reason")}
            for r in rows
            if r["status"] != "ok"
        ],
        "all_three_successes": sum(r["composition_success"] for r in scored),
        "query_counts": {
            key: sum(q[key] for q in queries)
            for key in (
                "post_edit_exact",
                "pre_edit_answer_reappeared",
                "cap_off_pre_edit_exact",
                "cap_off_post_edit_exact",
            )
        },
        "null_mass_below_half": sum(
            q["cap_query"]["selection"] is not None
            and q["cap_query"]["selection"]["null_mass"] < 0.5
            for q in queries
        ),
        "hard_null_present_in_every_trace": all(
            "hard_null" in (q["cap_query"]["selection"] or {}) for q in queries
        ),
        "reference_termination": dict(Counter(q["reference"]["stopped_by"] for q in queries)),
        "cap_termination": dict(Counter(q["cap_query"]["stopped_by"] for q in queries)),
        "state_restored_all_rows": all(r["state_restored"] for r in rows),
        "dependency_count_histogram_planned": summary["dependency_count_hist"],
        "summary_matches": summary["summary"] == report["summary"],
        "reader_is_v4_seed0": summary["theta"]["sha256"] == primary["weights"]["seed0"]["sha256"],
        "full_inventory_fraction": summary["summary"]["full_inventory_fraction"],
        "wall_seconds": summary["wall_seconds"],
    }
    streams = []
    for prefix in ("tri_text", "tri2_text", "idf_text"):
        for seed in (0, 1, 2):
            for dataset, suffix in (
                ("zsre", ""),
                ("counterfact", "@counterfact"),
                ("mquake", "@mquake"),
            ):
                path = f"results/R1/stream_eval_{prefix}_s{seed}_rare1_null0.5{suffix}.json"
                d = read(path)
                streams.append(
                    {
                        "path": path,
                        "family": prefix,
                        "seed": seed,
                        "dataset": dataset,
                        "theta_hash": d["theta_hash"],
                        "stream_metrics": d["stream_metrics"],
                        "n_requested": d["args"]["n"],
                        "stream_seed": d["args"]["stream_seed"],
                    }
                )
    pool = read("manifests/revision_v1/mquake_pool_v1.json")
    prepared = read("manifests/revision_v1/mquake_items_v1.json")
    p = Path(prepared["artifacts"]["items"]["path"])
    raw = p.read_bytes()
    bindings[str(p)] = hashlib.sha256(raw).hexdigest()
    if bindings[str(p)] != prepared["artifacts"]["items"]["sha256"]:
        raise ValueError("prepared source identity mismatch")
    source_rows = {r["item_id"]: r for r in map(json.loads, raw.splitlines())}
    support_fields = (
        "prompt",
        "answer",
        "prompt_ids",
        "answer_ids",
        "digest",
        "subject",
        "fact_id",
        "relation_id",
    )
    mismatches = [
        r["item_id"]
        for r in pool["items"]
        if any(r[k] != source_rows[r["item_id"]][k] for k in support_fields)
    ]
    toy = {
        "item_id": "toy",
        "digest": "00" * 32,
        "prompt": "fixture",
        "answer": "answer",
        "aliases": ["answer"],
        "paraphrases": ["fixture?"],
        "locality_prompts": ["other"],
        "prompt_ids": [1],
        "answer_ids": [2],
        "fact_id": "toy",
    }
    source = (ROOT / "scripts/r1_13_stream_eval.py").read_text()
    accepted, _ = loader_probe(
        source,
        {"mode": "confirm", "dataset": "mquake", "items": [toy], "unrelated_prompts": []},
        100,
    )
    negative, _ = loader_probe(source, {"items": [toy] * 3, "unrelated_prompts": []}, -1)
    return {
        "task": "R1-X10",
        "sources_sha256": bindings,
        "composition": composition,
        "streams": streams,
        "teacher": {
            "counts": pool["counts"],
            "support_field_mismatches": mismatches,
            "termination": dict(Counter(r["teacher_stopped_by"] for r in pool["items"])),
            "producer_base_tokenizer_identity_recorded": all(
                k in pool for k in ("producer_sha256", "base_sha256", "tokenizer_sha256")
            ),
        },
        "dev_manifest_probe": {
            "fixture_only": True,
            "requested_n": 100,
            "accepted_n": len(accepted),
            "confirm_mode_dataset_mismatch_accepted": accepted[0].dataset == "zsre",
            "negative_n_minus1_from_three": len(negative),
            "token_arrays_accepted_without_tokenization": accepted[0].prompt_ids.tolist() == [1],
        },
        "gpu_seconds": 0,
        "real_base_execution": False,
        "sealed_payloads_opened": 0,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository output required")
    result = build()
    with args.output.open("x") as f:
        json.dump(result, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    print(
        json.dumps(
            {k: result[k] for k in ("composition", "teacher", "dev_manifest_probe")}, indent=2
        )
    )


if __name__ == "__main__":
    main()
