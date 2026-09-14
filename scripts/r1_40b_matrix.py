"""R1-40b: current learned-primary matrix, honest cost proxies and answer-position bytes."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COUNTERS = ("full_forwards", "partial_forwards", "reverses", "tokens", "accel_seconds")


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def identity(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()[:24]


def delta_bytes(
    records, answer_positions, prompt_tokens, weights, *, width=256, code=256, sites=3, d=768
):
    if any(
        type(x) is not int or x < 0 for x in (records, answer_positions, prompt_tokens, weights)
    ):
        raise ValueError("nonnegative integer dimensions/counts required")
    per = width * 4 + code * 4 + 128 + prompt_tokens * 4 + answer_positions * sites * d * 4
    return {
        "weights": weights,
        "per_record": per,
        "records": records,
        "total": weights + records * per,
        "delta_bytes_per_position": sites * d * 4,
    }


def memory_plan(summary, n=1000):
    b = summary["bytes"]
    count = summary["args"]["n"]
    weights = b["weights"]
    per = (b["total"] - weights) / count
    cap = 64 * 1024 * 1024
    expected = math.ceil(weights + n * per)
    with_clones = math.ceil(weights + (n + 2) * per)
    worst = delta_bytes(n + 2, 32, 992, weights)
    max_positions = math.floor(
        ((cap - weights) / (n + 2) - 256 * 4 - 256 * 4 - 128 - 992 * 4) / 9216
    )
    bounded = delta_bytes(n + 2, max_positions, 992, weights)
    return {
        "policy_bytes": cap,
        "parameter_bytes": weights,
        "counted_record_metadata_bytes": 128,
        "observed_answer_positions_mean": b["deltas"] / (9216 * count),
        "observed_prompt_tokens_mean": b["tokens"] / (4 * count),
        "estimate_from_observed_100_edit_mix": {
            "stream_records": n,
            "total_bytes": expected,
            "fits": expected <= cap,
            "with_two_extra_clone_records_bytes": with_clones,
            "fits_with_clone_records": with_clones <= cap,
            "max_records_at_observed_average": math.floor((cap - weights) / per),
        },
        "declared_maximum_32_answer_positions_992_prompt_tokens": {
            **worst,
            "fits": worst["total"] <= cap,
        },
        "bounded_position_option": {
            "max_delta_positions_for_1002_max_prompt_records": max_positions,
            "total_bytes": bounded["total"],
            "fits": bounded["total"] <= cap,
            "selected": False,
            "caveat": "limits delta coverage on longer answers; new condition/decision, never a silent truncation of labels or endpoints",
        },
        "admission_status": "observed_mean_fits_but_final_length_inventory_required",
        "exact_final_fit": None,
        "bounded_position_write_needed_if_final_bytes_exceed_ceiling": True,
        "limitations": [
            "float32 logical arrays plus current fixed metadata model; not certified physical RSS/device peak",
            "include all retained inactive revisions; query clones add up to two supports and do not permanently enlarge the primary stream",
            "32-position answer support cannot be guaranteed for 1000 records under 64 MiB; do not assume the mean proves a hard maximum",
        ],
    }


def validate(m):
    cells = m["cells"]
    if len(cells) != 180 or len(m["conditions"]) != 6 or len(m["profiling_jobs"]) != 2:
        raise ValueError(
            "retain six conditions, 180 paired natural-language cells and two profiles"
        )
    if len({c["cell_id"] for c in cells}) != len(cells) or len(
        {c["result_path_template"] for c in cells}
    ) != len(cells):
        raise ValueError("duplicate physical cell")
    for c in cells:
        if c["launch_allowed"] or c["ceilings"]["frozen"] or c["stream_length"] != 1000:
            raise ValueError("draft launch/freeze/length violation")
        if c["checkpoint_ids"] != m["conditions"][c["condition_id"]]["checkpoint_ids"]:
            raise ValueError("checkpoint mismatch")
        if c["ceilings"]["failure_reserve_seconds"] < 0.2 * c["ceilings"]["proposed_seconds"]:
            raise ValueError("failure reserve lost")
    if m["primary_condition"] != "R1_learned_ff":
        raise ValueError("current lead directive retains learned primary")
    settings = m["conditions"]["R1_learned_ff"]["settings"]
    if settings["null_threshold"] != 0.5 or settings["min_score"] is not None:
        raise ValueError("current single deployment rule required")
    for contrast in m["contrasts"]:
        if not set(contrast["conditions"]) <= set(m["conditions"]):
            raise ValueError("contrast references a deferred condition")
    total = sum(
        c["ceilings"]["proposed_seconds"] + c["ceilings"]["failure_reserve_seconds"] for c in cells
    )
    if total != m["budget"]["core_draft_seconds_including_20pct_reserve"]:
        raise ValueError("budget total mismatch")
    return m


def build():
    sources = {}

    def load(rel):
        p = ROOT / rel
        sources[str(p)] = sha(p)
        return json.loads(p.read_text())

    old = load("manifests/revision_v1/run_matrix_draft.json")
    register = load("manifests/revision_v1/exclusions_v3.json")
    stop = load("manifests/revision_v1/stop_tokens_v1.json")
    del stop
    for rel in (
        "docs/ongoing.md",
        "docs/lead_queue.md",
        "docs/updated_plan9.md",
        "docs/R1_stage2_notes.md",
        "src/pccap/revision_v1/memory.py",
        "src/pccap/revision_v1/learner.py",
        "src/pccap/revision_v1/controller.py",
    ):
        p = ROOT / rel
        sources[str(p)] = sha(p)
    sources[str(Path(__file__).resolve())] = sha(__file__)
    m = {k: copy.deepcopy(old[k]) for k in ("axes", "profiling_jobs", "analysis")}
    retained = {k: v for k, v in old["conditions"].items() if v["scope"] == "core"}
    conditions = copy.deepcopy(retained)
    conditions["R1_learned_ff"]["checkpoint_ids"] = ["base_original", "reader_mixed"]
    conditions["R1_learned_ff"]["training_job_ids"] = ["reader_mixed"]
    conditions["R1_learned_ff"]["settings"].update(
        null_threshold=0.5,
        min_score=None,
        lexical=True,
        query_null=True,
        stop_tokens_manifest="manifests/revision_v1/stop_tokens_v1.json",
        stop_tokens_sha256=sources[str(ROOT / "manifests/revision_v1/stop_tokens_v1.json")],
        reader_training="mixed-domain stream-scale, 64 records, seed0, selected best development retrieval checkpoint",
    )
    conditions["R1_nonlearned"]["settings"].update(
        lexical=False,
        pairwise_null=False,
        null_threshold=1.01,
        min_score=0.93,
        runtime_note="explicitly disable new lexical defaults to reproduce regenerated historical random reference",
    )
    for cid, cond in conditions.items():
        cond["role"] = "primary" if cid == "R1_learned_ff" else "comparator"
    registry = {
        k: copy.deepcopy(old["checkpoint_registry"][k]) for k in ("base_original", "reader_random")
    }
    pilot = load("results/R1/pilot/r1_50_stream_mixed/summary.json")
    theta = Path(pilot["theta_path"])
    registry["reader_mixed"] = {
        "path": str(theta),
        "sha256": sha(theta),
        "params_hash": pilot["theta_hash"],
        "status": "working_development_candidate_not_final_frozen",
        "training_job": "reader_mixed",
    }
    for checkpoint in registry.values():
        if sha(checkpoint["path"]) != checkpoint["sha256"]:
            raise ValueError("checkpoint changed")
        sources[checkpoint["path"]] = checkpoint["sha256"]
    evidence = {
        k: copy.deepcopy(v)
        for k, v in old["cost_evidence"].items()
        if not k.startswith(("random:", "learned:"))
    }
    for e in evidence.values():
        p = ROOT / e["path"]
        sources[str(p)] = sha(p)
        if sources[str(p)] != old["sources_sha256"][str(p)]:
            raise ValueError("historical cost source changed")
        e["limitations"] = (
            "historical proxy retained; matched control used 3 rather than proposed 5 steps; CounterFact borrowing explicitly marked"
        )
    summaries = {}
    for family, tag in (("random", "ref_nonlearned_gate0.93_v2"), ("learned", "mixed_null0.5")):
        for ds in ("zsre", "counterfact"):
            rel = (
                f"results/R1/stream_eval_{tag}{'@counterfact' if ds == 'counterfact' else ''}.json"
            )
            obj = load(rel)
            summaries[family + ":" + ds] = obj
            rates = {
                phase: {k: obj["ledger"][phase][k] / obj["args"]["n"] for k in COUNTERS}
                for phase in ("learning", "query")
            }
            evidence[family + ":" + ds] = {
                "path": rel,
                "sha256": sources[str(ROOT / rel)],
                "n": obj["args"]["n"],
                "runtime_args": obj["args"],
                "summary_metrics": obj["stream_metrics"],
                "per_edit": rates,
                "wall_seconds": obj["wall_seconds"],
                "wall_per_edit": obj["wall_seconds"] / obj["args"]["n"],
                "limitations": "summary ledger includes post-stream diagnostic queries; wall span is the stream scope; outer training not priced by these counters",
            }
    cells = []
    for original in old["cells"]:
        if original["scope"] != "core":
            continue
        c = copy.deepcopy(original)
        cid, ds = c["condition_id"], c["dataset"]
        cond = conditions[cid]
        c["checkpoint_ids"] = cond["checkpoint_ids"]
        key = cond["profile_family"] + ":" + ds
        borrowed = key not in evidence
        if borrowed:
            key = cond["profile_family"] + ":zsre"
        e = evidence[key]
        rates = e["per_edit"]
        update = 1000 * rates["learning"]["accel_seconds"]
        query = 1400 * max(0, e["wall_per_edit"] - rates["learning"]["accel_seconds"])
        challenge = 200 * e["wall_per_edit"]
        raw = update + query + challenge + 780
        ceiling = 60 * math.ceil(1.25 * raw / 60)
        c["cost_evidence"] = {
            "id": key,
            "borrowed": borrowed,
            "point_seconds_proxy": raw,
            "components": {
                "updates": update,
                "checkpoint_query_proxy": query,
                "challenge_proxy": challenge,
                "full_split_drift_proxy": 780,
            },
            "limitations": "unchanged v1 proxy formula; not a measured 1000-edit/full-endpoint cost; all occupancy, token, diagnostic-scope and JIT accounting gates remain",
        }
        c["ceilings"].update(
            proposed_seconds=ceiling, failure_reserve_seconds=math.ceil(0.2 * ceiling), frozen=False
        )
        if cid in ("R1_learned_ff", "R1_nonlearned"):
            c["memory_projection"] = memory_plan(summaries[key])
        else:
            ceiling_bytes = c["ceilings"]["persistent_bytes"]
            c["memory_projection"] = {
                "policy_bytes": ceiling_bytes,
                "allocation_model": "fixed v0-cap allocation",
                "total_allocated_bytes": ceiling_bytes,
                "fits_64_mib": ceiling_bytes <= 64 * 1024 * 1024,
                "admission_status": "fixed_allocation_not_a_guarantee_of_retention_without_eviction",
                "bounded_position_write_needed": False,
                "exact_final_fit": "fixed logical allocation; physical/profile checks pending",
            }
        c["expected_base_calls_per_edit"] = {
            phase: {k: rates[phase][k] for k in ("full_forwards", "partial_forwards", "reverses")}
            for phase in ("learning", "query")
        }
        c["tokens"].update(
            learning_ledger_input_tokens_proxy=1000 * rates["learning"]["tokens"],
            query_ledger_input_tokens_proxy=1000 * rates["query"]["tokens"],
            support_sequence_positions_estimate=None,
            exact_final_stream_tokens=None,
            exact_training_pass_tokens=None,
            note="final inventory is unsealed; do not retain v1 pre-reservation token means as exact v3 counts",
        )
        c["condition_role"] = cond["role"]
        c["cell_id"] = identity(
            {
                "version": 2,
                "condition": cond,
                "dataset": ds,
                "realization": c["realization_seed"],
                "order": c["order_seed"],
                "checkpoints": {name: registry[name]["sha256"] for name in c["checkpoint_ids"]},
            }
        )
        suffix = (
            f"<freeze-id>/{cid}/{ds}/r{c['realization_seed']}/o{c['order_seed']}/{c['cell_id']}"
        )
        c["result_path_template"] = "results/R1/confirm_draft_v2/" + suffix
        c["checkpoint_path_template"] = "assets/runs/R1/confirm_draft_v2/" + suffix
        c["admission"] = (
            "v3 exclusions + reviewed fresh eligible inventory + selected hash-bound checkpoint/config + R50 gates + measured full endpoint costs + lead revision freeze"
        )
        cells.append(c)
    contrasts = [
        copy.deepcopy(c) for c in old["contrasts"] if set(c["conditions"]) <= set(conditions)
    ]
    deferred = {
        k: {
            "previous_scope": v["scope"],
            "reason": "outside current working learned-primary comparison; requires own implementation/selection/profile decision, not a negative result",
        }
        for k, v in old["conditions"].items()
        if k not in conditions
    }
    total = sum(
        c["ceilings"]["proposed_seconds"] + c["ceilings"]["failure_reserve_seconds"] for c in cells
    )
    m.update(
        schema_version=2,
        task="R1-40b",
        name="run_matrix_draft_v2",
        status="unlaunchable_unfrozen_learned_primary_draft",
        primary_condition="R1_learned_ff",
        lead_policy="current round-6 learned-reader recovery directive; DEC-038 drop-learned proposal withdrawn",
        sources_sha256=sources,
        conditions=conditions,
        checkpoint_registry=registry,
        cost_evidence=evidence,
        cells=cells,
        contrasts=contrasts,
        deferred_conditions=deferred,
        pruning={
            "previous_all_cells": len(old["cells"]),
            "retained_cells": len(cells),
            "removed_conditional_cells": len(old["cells"]) - len(cells),
            "required_core_cells_silently_removed": 0,
            "note": "retain C1/C2, stable, matched, random and working learned comparisons; no non-learned-primary assumption survives",
        },
        shared_training_jobs={
            "reader_mixed": {
                "status": "completed_development_training_shared_once",
                "summary_path": "results/R1/pilot/r1_50_stream_mixed/summary.json",
                "train_wall_seconds": pilot["train_wall_s"],
                "bank_load_wall_seconds": pilot["bank_wall_s"],
                "total_wall_seconds": pilot["total_wall_s"],
                "reported_learning_tokens": pilot["ledger"]["learning"]["tokens"],
                "exact_training_pass_tokens": None,
                "bank_build_cost": "shared cached resource construction must be separately bound/charged once; not included by multiplying this job across 30 cells",
            }
        },
        data_gates={
            "register": "manifests/revision_v1/exclusions_v3.json",
            "register_sha256": sources[str(ROOT / "manifests/revision_v1/exclusions_v3.json")],
            "zsre_prior_clear_primary_subject_survivors": register["counts_v3"][
                "prior_clear_primary_subject_survivors"
            ],
            "zsre_teacher_eligible_fresh": None,
            "context_alias_review_required": True,
            "counterfact": "fresh-source or registered remainder exception still requires lead decision; training/development subjects excluded",
            "no_final_payloads_read_or_emitted": True,
        },
        budget={
            "core_cells": len(cells),
            "core_draft_seconds_including_20pct_reserve": total,
            "previous_core_draft_seconds": old["budget"][
                "core_draft_seconds_including_20pct_reserve"
            ],
            "confirmatory_envelope_seconds": 54000,
            "core_fits_15h_at_draft_ceilings": total <= 54000,
            "profile_job_proposed_seconds": sum(p["proposed_seconds"] for p in m["profiling_jobs"]),
            "unmeasured_full_split_drift_floor_with_headroom_and_reserve_seconds": len(cells)
            * 780
            * 1.25
            * 1.2,
            "shared_training_billed_once_outside_cells": True,
            "interpretation": "proxy ceilings, not measured runtime; fewer conditional cells do not make the retained core fit the allocation",
        },
        unresolved=[
            "exact 1000-edit answer/token inventory and logical/physical byte profile",
            "R50 cache, population, query and cost gates",
            "five-step matched-update control profiling",
            "full-split drift/challenge cost and revised budget/scope decision",
            "formal final learned checkpoint/rule and RNG-axis decision",
            "fresh source/teacher/context/final sealing",
            "pure-learning attribution needs matched lexical architecture and gate controls; package comparison alone is insufficient",
        ],
        gpu_seconds=0,
        final_examples_emitted=0,
        sealed_payloads_opened=0,
    )
    m["profiling_jobs"][0]["scope"] = (
        "six retained conditions on both datasets; exact mixed theta/lexical stop list/null0.5/no gate; random reference explicitly lexical off"
    )
    m["profiling_jobs"][0]["measure"].extend(
        [
            "actual weights + every retained answer-position delta + support-token bytes",
            "32-position worst-case and proposed bounded-position alternative as separate conditions",
            "memory occupancy 1000 plus two independent-clone support records",
        ]
    )
    m["profiling_jobs"][1]["measure"].append(
        "R50 bank and differentiated outer-loop work accounting, all independent query boundaries"
    )
    for path, expected in sources.items():
        if sha(path) != expected:
            raise RuntimeError("planning source changed during build: " + path)
    return validate(m)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository matrix required")
    m = build()
    payload = json.dumps(m, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with args.output.open("x") as f:
        f.write(payload)
    print(
        json.dumps(
            {"output": str(args.output), "budget": m["budget"], "pruning": m["pruning"]}, indent=2
        )
    )


if __name__ == "__main__":
    main()
