"""R1-40d: identity-bound 360-cell draft plus a separate 45-cell historical extension.
Reads existing identities only. Does not draw, seal, load a model or authorize execution.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = (
    "R1_learned_ff",
    "R1_nonlearned",
    "v0_stable",
    "matched_update",
    "v0_live_C1",
    "v0_live_C2",
    "S1_LM",
    "S1_literal",
)
EXTENSION = "R1_learned_ff_v2"
DATASETS = ("zsre", "counterfact", "mquake")
CHECKPOINTS = [100, 300, 1000]
SEEDS = (0, 1, 2)
ORDERS = (100, 101, 102, 103, 104)


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


class Binder:
    def __init__(self, root):
        self.root = Path(root)
        self.sources = {}

    def bind(self, path, expected=None):
        p = Path(path)
        if not p.is_absolute():
            p = self.root / p
        p = p.resolve(strict=True)
        value = sha(p)
        if expected is not None and value != expected:
            raise ValueError("identity mismatch: " + str(p))
        self.sources[str(p)] = value
        return {"path": str(p), "sha256": value}

    def load(self, path, expected=None):
        ref = self.bind(path, expected)
        return json.loads(Path(ref["path"]).read_text()), ref

    def verify(self):
        for path, expected in self.sources.items():
            if sha(path) != expected:
                raise ValueError("identity changed during build: " + path)


def assemble(conditions, common):
    def cells(ids, block):
        out = []
        for cid, ds, realization, order in itertools.product(ids, DATASETS, SEEDS, ORDERS):
            binding = {"condition_sha256": digest(conditions[cid]), "common_sha256": digest(common)}
            key = {
                "condition_id": cid,
                "dataset": ds,
                "realization_seed": realization,
                "order_seed": order,
                "model_seed": 0,
                "block": block,
                "stream_length": 1000,
                "checkpoint_schedule": CHECKPOINTS,
                "bindings": binding,
            }
            cell_id = digest(key)[:24]
            profile = f"results/R1/stage4_dev_cells/pending_r1_40d_{cid}_{ds}/"
            out.append(
                {
                    **key,
                    "cell_id": cell_id,
                    "launch_allowed": False,
                    "condition_identity": copy.deepcopy(conditions[cid]),
                    "result_path_template": f"results/R1/confirm_draft_v4/<freeze-id>/{block}/{cid}/{ds}/r{realization}/o{order}/{cell_id}",
                    "ceilings": {
                        "wall_seconds": None,
                        "watchdog_seconds": None,
                        "persistent_bytes": None,
                        "failure_reserve_seconds": None,
                        "checkpoint_seconds": {str(k): None for k in CHECKPOINTS},
                        "source": profile,
                        "profile_receipt_sha256": None,
                        "frozen": False,
                    },
                    "profile_status": "future owner evidence target; no completed result inferred",
                    "pairing_id": f"{ds}/r{realization}/o{order}",
                    "unseen_reserve_id": f"{ds}/r{realization}/outside100",
                    "endpoint_ids": [
                        "ES",
                        "RET-ES",
                        "RET-GS",
                        "LS",
                        "near_miss",
                        "revision",
                        "full_drift",
                        "memory_size_profile",
                        "unseen_edit_prompt",
                    ]
                    + (["composition_descriptive"] if ds == "mquake" else []),
                }
            )
        return out

    return {
        "schema_version": 4,
        "name": "run_matrix_draft_v4",
        "task": "R1-40d",
        "status": "draft; capacity, final reference, profiles and lead admission unresolved",
        "primary_condition": "R1_learned_ff",
        "conditions": conditions,
        "common_identity": common,
        "axes": {
            "conditions": list(CORE),
            "datasets": list(DATASETS),
            "realization_seeds": list(SEEDS),
            "order_seeds": list(ORDERS),
            "model_seeds": [0],
        },
        "cells": cells(CORE, "core"),
        "extension": {
            "condition": EXTENSION,
            "cells": cells([EXTENSION], "v2_extension"),
            "cell_count": 45,
            "allocation_approved": False,
            "interpretation": "v3 two-pool weights with rare gate disabled; versus v4 both training and gate differ; not a gate-only ablation",
        },
        "launch_allowed": False,
        "draw_authorized": False,
        "confirmation_protocol_frozen": False,
        "gpu_seconds": 0,
        "final_examples_emitted": 0,
        "sealed_payloads_opened": 0,
        "budget": {
            "core_cells": 360,
            "extension_cells": 45,
            "combined_cells": 405,
            "full_matrix_ceiling_seconds": None,
            "shared_training_charged_once": True,
            "historical_15_hour_limit_superseded_by_DEC044": True,
            "scenario_only_1150_seconds_times_360_plus_20pct_hours": 138,
            "scenario_only_with_extension_hours": 155.25,
        },
        "population_gate": {
            "subjects_required_each_dataset": 4050,
            "per_realization": {
                "edits": 1000,
                "outside": 100,
                "near_support": 100,
                "near_neighbour": 100,
                "revision": 50,
            },
            "capacity_policy_decision": None,
            "options_memo": "docs/tasks/R1-D7.md",
            "reduced_MQuAKE_scope_adopted": False,
        },
        "admission": [
            "lead reference and population decision",
            "teacher/context/alias clearance",
            "fresh independent role allocation and payload seals",
            "complete endpoint and analysis inventories",
            "exact per-condition/dataset profiles and checkpoint/watchdog ceilings",
            "shared training/control budget reconciliation",
            "lead protocol/code/environment freeze",
        ],
        "analysis": {
            "independent_clusters": "3 fresh realizations; five orders nested",
            "model_seed_axis": "fixed seed0; other reader training seeds remain development evidence",
            "v3_fallback": "separate gated two-pool reference requires versioned matrix; not extension",
            "gate_only_contrast": "requires identical reader weights, training and all settings except gate",
        },
    }


def validate(matrix):
    if any(
        matrix[k] for k in ("launch_allowed", "draw_authorized", "confirmation_protocol_frozen")
    ):
        raise ValueError("draft authorization violation")
    all_cells = matrix["cells"] + matrix["extension"]["cells"]
    if len(matrix["cells"]) != 360 or len(matrix["extension"]["cells"]) != 45:
        raise ValueError("incorrect block sizes")
    expected_core = set(itertools.product(CORE, DATASETS, SEEDS, ORDERS))
    expected_extension = set(itertools.product([EXTENSION], DATASETS, SEEDS, ORDERS))

    def axes(rows):
        return {
            (r["condition_id"], r["dataset"], r["realization_seed"], r["order_seed"]) for r in rows
        }

    if (
        axes(matrix["cells"]) != expected_core
        or axes(matrix["extension"]["cells"]) != expected_extension
    ):
        raise ValueError("incorrect axes")
    if (
        len({c["cell_id"] for c in all_cells}) != 405
        or len({c["result_path_template"] for c in all_cells}) != 405
    ):
        raise ValueError("duplicate identity or path")
    for c in all_cells:
        cond = matrix["conditions"][c["condition_id"]]
        if c["condition_identity"] != cond or c["bindings"] != {
            "condition_sha256": digest(cond),
            "common_sha256": digest(matrix["common_identity"]),
        }:
            raise ValueError("cell condition binding mismatch")
        key = {
            k: c[k]
            for k in (
                "condition_id",
                "dataset",
                "realization_seed",
                "order_seed",
                "model_seed",
                "block",
                "stream_length",
                "checkpoint_schedule",
                "bindings",
            )
        }
        if c["cell_id"] != digest(key)[:24]:
            raise ValueError("cell identity mismatch")
        if (
            c["launch_allowed"]
            or c["ceilings"]["frozen"]
            or c["checkpoint_schedule"] != CHECKPOINTS
            or c["stream_length"] != 1000
        ):
            raise ValueError("draft cell settings violation")
        ceiling = c["ceilings"]
        if any(
            ceiling[k] is not None
            for k in (
                "wall_seconds",
                "watchdog_seconds",
                "persistent_bytes",
                "failure_reserve_seconds",
                "profile_receipt_sha256",
            )
        ) or ceiling["checkpoint_seconds"] != {str(k): None for k in CHECKPOINTS}:
            raise ValueError("unmeasured ceiling must stay null")
        if not ceiling["source"].startswith("results/R1/stage4_dev_cells/"):
            raise ValueError("missing named profile source")
    return matrix


def build(root=ROOT):
    binder = Binder(root)
    old, _ = binder.load("manifests/revision_v1/run_matrix_draft_v3.json")
    primary = {}
    refs = {}
    for version in (3, 4):
        p, ref = binder.load(f"manifests/revision_v1/primary_condition_v{version}.json")
        primary[version], refs[version] = p, ref
        binder.bind(p["stop_tokens"]["path"], p["stop_tokens"]["sha256"])
        for name, expected in p["pools"].items():
            binder.bind("manifests/revision_v1/" + name + ".json", expected)
        for w in p["weights"].values():
            binder.bind(w["path"], w["sha256"])
    original = binder.bind(
        old["checkpoint_registry"]["base_original"]["path"],
        old["checkpoint_registry"]["base_original"]["sha256"],
    )
    random = old["checkpoint_registry"]["reader_random"]
    random_ref = binder.bind(random["path"], random["sha256"])
    calibration_path = (
        "manifests/archive/frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json"
    )
    calibration, cal_ref = binder.load(calibration_path)
    model_dir = Path(old["checkpoint_registry"]["base_original"]["path"]).parent
    common = {
        "original_base": original,
        "base_config": binder.bind(model_dir / "config.json"),
        "tokenizer": binder.bind(model_dir / "tokenizer.json"),
        "calibration": cal_ref,
        "A": float(calibration["A"]),
        "tau_edit": float(calibration["tau_edit"]),
        "bank_scales": calibration["b_m"],
        "max_new_tokens": 32,
        "selected_reference": refs[4],
        "gated_fallback": refs[3],
    }
    register, register_ref = binder.load(
        "manifests/revision_v1/exclusions_frozen_v4_supplement_v2.json"
    )
    for rel in (
        "manifests/revision_v1/exclusions_frozen_v4.json",
        "manifests/revision_v1/exclusions_frozen_v4_supplement_v1_rebound.json",
    ):
        binder.bind(rel)
    binder.bind(register["parent"]["path"], register["parent"]["sha256"])
    common["register"] = register_ref
    settings = copy.deepcopy(old["conditions"]["R1_learned_ff"]["settings"])
    settings.update(
        reader_training="v4: historical MQ v2 pool; self-contained v3 retrain needs new identity",
        rare_overlap_min=1,
        rare_df_max=2,
        lex_idf=False,
        fast_steps=0,
        delta_steps=5,
        delta_lr=0.1,
        null_threshold=0.5,
        min_score=None,
    )
    conditions = {}
    for cid in CORE:
        conditions[cid] = {
            "model_seed": 0,
            "settings": copy.deepcopy(old["conditions"][cid]["settings"]),
            "base": original,
            "reference_manifest": refs[4],
        }
    conditions["R1_learned_ff"].update(
        settings=settings,
        reader=binder.bind(
            primary[4]["weights"]["seed0"]["path"], primary[4]["weights"]["seed0"]["sha256"]
        ),
    )
    conditions["R1_nonlearned"].update(reader=random_ref)
    conditions["R1_nonlearned"]["settings"].update(
        rare_overlap_min=None, lex_idf=False, fast_steps=0
    )
    for cid, recipe_name, tag in (
        ("S1_literal", "r1_24_control_v3", "r1_24_literal_v3b"),
        ("S1_LM", "r1_24_control_lm_v3_lr1e-8", "r1_24_lm_v3_lr1e-8"),
    ):
        recipe, recipe_ref = binder.load(f"manifests/revision_v1/{recipe_name}.json")
        summary, summary_ref = binder.load(f"results/R1/r1_24/{tag}/summary.json")
        if (
            summary["manifest_sha256"] != recipe_ref["sha256"]
            or not summary["fidelity"]["fidelity_pass"]
        ):
            raise ValueError("continuation identity/fidelity admission mismatch")
        ck = summary["checkpoint"]
        conditions[cid].update(
            base=binder.bind(ck["path"], ck["sha256"]),
            tensor_digest=ck["continued_tensor_digest"],
            recipe=recipe_ref,
            result=summary_ref,
            fidelity=summary["fidelity"],
            shared_training_forward_tokens=recipe["budget"]["matched_tokens"],
            budget_status="historical two-pool matching basis; v4 total-cost reconciliation pending",
        )
        conditions[cid]["settings"]["recipe_manifest"] = recipe_ref["path"]
        binder.bind(recipe["reference_condition"]["path"], recipe["reference_condition"]["sha256"])
        binder.bind(recipe["evaluation"]["theta"]["path"], recipe["evaluation"]["theta"]["sha256"])
    ext = copy.deepcopy(conditions["R1_learned_ff"])
    ext.update(
        reference_manifest=refs[3],
        reader=binder.bind(
            primary[3]["weights"]["seed0"]["path"], primary[3]["weights"]["seed0"]["sha256"]
        ),
    )
    ext["settings"].update(rare_overlap_min=None, reader_training="v3 two-pool text-null weights")
    ext["deployment_override"] = (
        "v3 manifest is gated; explicitly disable rare_overlap_min for historical v2 extension"
    )
    conditions[EXTENSION] = ext
    for rel in (
        "scripts/r1_40d_matrix.py",
        "scripts/r1_61_cell_driver.py",
        "src/pccap/revision_v1/stage4_adapters.py",
        "src/pccap/revision_v1/analysis_stage4.py",
    ):
        binder.bind(rel)
    m = assemble(conditions, common)
    m["population_gate"]["candidate_subjects"] = {
        k: v["candidate_subjects"] for k, v in register["counts"].items()
    }
    m["sources_sha256"] = binder.sources
    binder.verify()
    return validate(m)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository output required")
    matrix = build()
    with args.output.open("x") as f:
        json.dump(matrix, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "core": len(matrix["cells"]),
                "extension": len(matrix["extension"]["cells"]),
                "identities": len(matrix["sources_sha256"]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
