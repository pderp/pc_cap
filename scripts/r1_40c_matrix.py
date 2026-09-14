"""R1-40c: unfrozen matrix v3 with unseen/scale endpoints and DEC-040 S1 treatments."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW_CONDITIONS = {"S1_literal": "literal", "S1_LM": "lm"}
ENDPOINTS = ("memory_size_profile", "unseen_edit_prompt")


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def identity(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()[:24]


def validate(m):
    cells, conditions = m["cells"], m["conditions"]
    if len(cells) != 240 or len(conditions) != 8 or not set(NEW_CONDITIONS) <= set(conditions):
        raise ValueError("six core plus two DEC-040 conditions require 240 cells")
    axes = {
        (c["condition_id"], c["dataset"], c["realization_seed"], c["order_seed"]) for c in cells
    }
    if len(axes) != 240 or len({c["cell_id"] for c in cells}) != 240:
        raise ValueError("duplicate cell or axes")
    if len({c["result_path_template"] for c in cells}) != 240:
        raise ValueError("duplicate result path")
    if m["primary_condition"] != "R1_learned_ff":
        raise ValueError("learned reference remains primary")
    profiles = {p["id"] for p in m["profiling_jobs"]}
    for c in cells:
        ceiling = c["ceilings"]
        if c["launch_allowed"] or ceiling["frozen"] or c["stream_length"] != 1000:
            raise ValueError("draft launch/freeze/stream-length violation")
        if (
            ceiling["proposed_seconds"] is not None
            or ceiling["failure_reserve_seconds"] is not None
        ):
            raise ValueError("expanded endpoint ceilings require actual profiles")
        if ceiling["failure_reserve_fraction"] != 0.2:
            raise ValueError("failure reserve convention lost")
        if not set(ENDPOINTS) <= set(c["endpoint_ids"]):
            raise ValueError("required new endpoint omitted")
        if c["checkpoint_schedule"] != [100, 300, 1000]:
            raise ValueError("checkpoint schedule changed")
        if c["checkpoint_ids"] != conditions[c["condition_id"]]["checkpoint_ids"]:
            raise ValueError("checkpoint mismatch")
        if not set(c["profile_dependencies"]) <= profiles:
            raise ValueError("unknown profile dependency")
    if m["endpoint_catalog"]["unseen_edit_prompt"]["expected_n_per_checkpoint"] != 100:
        raise ValueError("draft outside query count must be explicitly re-versioned")
    for contrast in m["contrasts"]:
        if not set(contrast["conditions"]) <= set(conditions):
            raise ValueError("contrast references an absent condition")
    total = sum(
        c["ceilings"]["legacy_endpoint_proxy_seconds"]
        + c["ceilings"]["legacy_failure_reserve_seconds"]
        for c in cells
    )
    if total != m["budget"]["legacy_endpoint_proxy_subtotal_seconds"]:
        raise ValueError("proxy subtotal mismatch")
    if m["budget"]["expanded_full_matrix_ceiling_seconds"] is not None:
        raise ValueError("unmeasured full matrix ceiling cannot be inferred")
    return m


def build():
    sources = {}

    def bind(rel, expected=None):
        path = Path(rel)
        if not path.is_absolute():
            path = ROOT / path
        value = sha(path)
        if expected and value != expected:
            raise ValueError("source hash mismatch: " + str(path))
        sources[str(path)] = value
        return path

    def load(rel):
        return json.loads(bind(rel).read_text())

    old = load("manifests/revision_v1/run_matrix_draft_v2.json")
    primary = load("manifests/revision_v1/primary_condition_v1.json")
    cf = load("manifests/revision_v1/counterfact_fresh_candidates_v1.json")
    budget_basis = load("manifests/revision_v1/r1_24_budget_reconciliation_v1.json")
    recipes = {
        "literal": load("manifests/revision_v1/r1_24_control_v3.json"),
        "lm": load("manifests/revision_v1/r1_24_control_lm_v2.json"),
    }
    recipe_paths = {
        "literal": "manifests/revision_v1/r1_24_control_v3.json",
        "lm": "manifests/revision_v1/r1_24_control_lm_v2.json",
    }
    for rel in (
        "docs/ongoing.md",
        "docs/decisions.md",
        "docs/updated_plan9.md",
        "docs/R1_stage2_notes.md",
        "scripts/r1_40c_matrix.py",
        "src/pccap/revision_v1/endpoints_unseen.py",
        "src/pccap/revision_v1/endpoints.py",
        "src/pccap/revision_v1/learner.py",
        "src/pccap/revision_v1/reader.py",
        "src/pccap/revision_v1/controller.py",
        "src/pccap/revision_v1/memory.py",
        "src/pccap/data/decode.py",
        "logs/r1_round7/x6_audit.json",
    ):
        bind(rel)
    stop = load(primary["stop_tokens"]["path"])
    if sha(ROOT / primary["stop_tokens"]["path"]) != primary["stop_tokens"]["sha256"]:
        raise ValueError("stop-list identity mismatch")
    for name, value in primary["pools"].items():
        bind("manifests/revision_v1/" + name + ".json", value)
    for ref in primary["weights"].values():
        bind(ref["path"], ref["sha256"])
    m = copy.deepcopy(old)
    registry = m["checkpoint_registry"]
    for ref in registry.values():
        bind(ref["path"], ref["sha256"])
    if registry["reader_mixed"]["sha256"] != primary["weights"]["seed0"]["sha256"]:
        raise ValueError("matrix differs from selected development reference")
    conditions = m["conditions"]
    conditions["R1_learned_ff"]["settings"].update(top_k=4, tie_heads=True, cosine=True)
    conditions["R1_nonlearned"]["settings"].update(top_k=4, tie_heads=True, cosine=True)
    for cid, treatment in NEW_CONDITIONS.items():
        recipe = recipes[treatment]
        if recipe["decision"] != "DEC-040 (both treatments)":
            raise ValueError("continuation directive mismatch")
        bind(recipe["reference_condition"]["path"], recipe["reference_condition"]["sha256"])
        bind(recipe["evaluation"]["theta"]["path"], recipe["evaluation"]["theta"]["sha256"])
        if recipe["evaluation"]["theta"]["sha256"] != primary["weights"]["seed0"]["sha256"]:
            raise ValueError("continuation evaluation reader differs from reference")
        if recipe["evaluation"]["reader"]["stop_tokens"] != stop["tokens"]:
            raise ValueError("continuation stop list differs")
        if recipe["budget"]["matched_tokens"] != budget_basis["training_forward_pass_tokens"]:
            raise ValueError("continuation budget is not reconciled")
        base_id = "base_continued_" + treatment
        registry[base_id] = {
            "path": None,
            "sha256": None,
            "status": "owner_completed_checkpoint_binding_required_before_freeze",
            "training_job": "continuation_" + treatment,
            "recipe_manifest": recipe_paths[treatment],
            "recipe_sha256": sources[str(ROOT / recipe_paths[treatment])],
            "same_architecture_as": "base_original",
        }
        cond = copy.deepcopy(conditions["v0_stable"])
        cond.update(
            scope="DEC040_continuation",
            role="comparator",
            checkpoint_ids=[base_id],
            training_job_ids=["continuation_" + treatment],
        )
        cond["settings"].update(
            base_treatment=treatment,
            cap_retrained=False,
            locality_reference="original base, common DEC-040 LS reference",
            unseen_reference="this condition's continued cap-off base; cap-induced change",
            recipe_manifest=recipe_paths[treatment],
        )
        conditions[cid] = cond
        m["shared_training_jobs"]["continuation_" + treatment] = {
            "status": "owner_development_execution_separate_from_final_admission",
            "recipe_manifest": recipe_paths[treatment],
            "recipe_sha256": sources[str(ROOT / recipe_paths[treatment])],
            "charge_once": True,
            "multiply_by_evaluation_cells": False,
            "planned_arithmetic": copy.deepcopy(recipe["budget"]["arithmetic"]),
            "shared_reference_budget_tokens": budget_basis["training_forward_pass_tokens"],
            "exact_accelerator_seconds": None,
            "scope": "forward-pass-token matched with explicit reverse work and exposure; not FLOP/time matched",
        }
    calibration_path = recipes["literal"]["evaluation"]["calibration"]
    calibration = json.loads(bind(calibration_path).read_text())
    m["reference_condition_binding"] = {
        "path": "manifests/revision_v1/primary_condition_v1.json",
        "sha256": sources[str(ROOT / "manifests/revision_v1/primary_condition_v1.json")],
        "base_weights_sha256": registry["base_original"]["sha256"],
        "reader_weights_sha256": registry["reader_mixed"]["sha256"],
        "stop_tokens_sha256": primary["stop_tokens"]["sha256"],
        "calibration_path": calibration_path,
        "calibration_sha256": sources[str(Path(calibration_path))],
        "A": 0.3,
        "b_m": calibration["b_m"],
        "decode_max_new_tokens": 32,
        "rule": "top-k4, hard top1, null0.5, no cosine gate, binary mass, delta5/lr0.1",
        "selected_for_final_confirmation": False,
    }
    m["endpoint_catalog"] = {
        "memory_size_profile": {
            "target_active_record_counts": [100, 300, 1000],
            "stream_measurement_checkpoints": [100, 300, 1000],
            "report": [
                "attempted edits",
                "active/retained records",
                "bytes",
                "candidate recall",
                "own firing",
                "null by role",
                "complete-answer ES/RET-GS/LS",
                "unseen prompt metrics",
            ],
            "population": "paired fixed development IDs for profile; fresh predeclared IDs for confirmation",
            "occupancy_rule": "attempted edits are not active records; report actual occupancy; mark an exact-size point unavailable if target is not reached, without resampling",
            "paired_profile_rule": "same memory and query IDs for top-k/reader variants; report all per-role denominators",
            "duplicates": "duplicate-key fixtures allowed only for labelled throughput/capacity stress, never generalization metrics",
            "implementation": "owner driver invokes existing metrics and R1-44 at checkpoints; cached bank-only diagnostics do not complete the endpoint",
        },
        "unseen_edit_prompt": {
            "module": "pccap.revision_v1.endpoints_unseen.UnseenPromptEvaluator",
            "source_sha256": sources[str(ROOT / "src/pccap/revision_v1/endpoints_unseen.py")],
            "expected_n_per_checkpoint": 100,
            "checkpoints": [100, 300, 1000],
            "max_new_tokens": 32,
            "numerators": [
                "hard-gate false fires",
                "bounded decoded-text changes",
                "complete-answer preservation",
            ],
            "denominator": "one equally weighted original prompt per predeclared outside item; no acquisition/firing conditioning",
            "shortfalls": "retain missing/unreachable/resource statuses; full-inventory rate null until all planned cases scored",
            "reserve": "100 distinct outside facts per realization, disjoint from every final edit realization and other reserved populations; same IDs paired across orders/conditions/checkpoints",
            "reference": "cap-off of the same base condition; report original-base drift separately",
            "differs_from_LS": "same-pool absent-fact edit prompts, not NQ or relation-neighbour locality",
            "firing_instrumentation": "RevisionCap observer implemented; all v0/comparator adapters must expose actual memory facts and decisions before freeze",
            "generation_work": "300 prompt pairs per cell = 600 greedy decodes; not included in legacy cost proxies",
            "decision_margin": None,
            "confirmation_selection_frozen": False,
        },
    }
    profiles = copy.deepcopy(old["profiling_jobs"])
    profiles[0].update(
        scope="all eight conditions on both datasets; exact continuation bases and reference config",
        status="not_run_for_v3_scope",
        allowance_status="old 1800s proposal requires review for expanded scope",
    )
    profiles[1].update(
        status="not_run_for_v3_scope",
        allowance_status="old 3600s proposal requires review for expanded scope",
    )
    profiles.extend(
        [
            {
                "id": "P3-unseen-scale",
                "owner": "orchestrator",
                "gpu_lease_required": True,
                "status": "not_run",
                "proposed_seconds": None,
                "target_active_records": [100, 300, 1000],
                "outside_queries_per_point": 100,
                "scope": "eight conditions, two datasets; paired exact-size selection diagnostics and full same-pool unseen generations",
                "requires": [
                    "reviewed development bank/pool of at least 1100 distinct eligible facts",
                    "complete cache identity",
                    "all comparator observer/memory adapters",
                ],
                "measure": [
                    "actual per-role coverage",
                    "candidate/selection/null errors",
                    "cap-off and cap-on decode costs",
                    "state restoration and query reset costs",
                    "logical/physical byte peaks",
                    "truncation",
                    "paired IDs across top-k/reader alternatives",
                    "prompt-token and answer-length buckets",
                ],
                "freeze_gate": "replace per-cell unpriced unseen/scale components with measured ceilings and reserves",
            },
            {
                "id": "P4-continuation",
                "owner": "orchestrator",
                "gpu_lease_required": True,
                "status": "not_run_for_final_scope",
                "proposed_seconds": None,
                "scope": "literal S1 and informative-LM S1 full-endpoint evaluation with shared S0/R0 references",
                "measure": [
                    "forward tokens and separate reverse positions",
                    "teacher/student/source exposures",
                    "cold compilation and warm accelerator time",
                    "base fidelity and complete drift assay",
                    "base-specific observation/calibration/cache admission",
                    "final base checkpoint/config hashes",
                ],
                "freeze_gate": "pin admitted continuation outputs; profile expanded 1000-edit runs, not just active 100-edit pilots",
            },
        ]
    )
    m["profiling_jobs"] = profiles
    m["contrasts"].extend(
        [
            {
                "id": "literal_vs_S0",
                "conditions": ["S1_literal", "v0_stable"],
                "reuse_existing_cells": True,
            },
            {"id": "LM_vs_S0", "conditions": ["S1_LM", "v0_stable"], "reuse_existing_cells": True},
            {
                "id": "R0_vs_literal_S1",
                "conditions": ["R1_learned_ff", "S1_literal"],
                "reuse_existing_cells": True,
            },
            {
                "id": "R0_vs_LM_S1",
                "conditions": ["R1_learned_ff", "S1_LM"],
                "reuse_existing_cells": True,
            },
            {
                "id": "informative_vs_literal",
                "conditions": ["S1_LM", "S1_literal"],
                "reuse_existing_cells": True,
            },
        ]
    )
    for contrast in m["contrasts"]:
        if contrast["id"] == "learned_component":
            contrast["interpretation"] = (
                "deployed-package comparison; architecture/lexical/gate changes prevent pure-learning attribution"
            )
    templates = list(copy.deepcopy(old["cells"]))
    for cid in NEW_CONDITIONS:
        for original in old["cells"]:
            if original["condition_id"] == "v0_stable":
                cell = copy.deepcopy(original)
                cell["condition_id"] = cid
                templates.append(cell)
    cells = []
    for c in templates:
        cid = c["condition_id"]
        cond = conditions[cid]
        ceiling = c["ceilings"]
        c["ceilings"] = {
            "persistent_bytes": ceiling["persistent_bytes"],
            "frozen": False,
            "proposed_seconds": None,
            "failure_reserve_seconds": None,
            "failure_reserve_fraction": 0.2,
            "legacy_endpoint_proxy_seconds": ceiling["proposed_seconds"],
            "legacy_failure_reserve_seconds": ceiling["failure_reserve_seconds"],
            "legacy_proxy_origin": "v2 stable comparator borrowed for S1"
            if cid in NEW_CONDITIONS
            else "same v2 condition",
            "unpriced_components": [
                "full unseen generations at three checkpoints",
                "exact memory-size diagnostics",
                "new source/continued-base rate changes where applicable",
            ],
            "source": "replace from P1/P2/P3/P4 before any admission",
        }
        c["condition_role"], c["scope"] = cond["role"], cond["scope"]
        c["checkpoint_ids"] = cond["checkpoint_ids"]
        c["endpoint_ids"] = [
            "ES",
            "RET-ES",
            "RET-GS",
            "LS",
            "near_miss",
            "revision",
            "full_drift",
            *ENDPOINTS,
        ]
        c["endpoints"] = [*c["endpoints"], *ENDPOINTS]
        c["profile_dependencies"] = ["P1-edit-memory", "P2-outer-endpoint", "P3-unseen-scale"]
        if cid in NEW_CONDITIONS:
            c["profile_dependencies"].append("P4-continuation")
            c["cost_evidence"]["borrowed"] = True
            c["cost_evidence"]["limitations"] += (
                "; S1 borrows stable original-base rates and is not measured"
            )
            c["tokens"]["exact_training_pass_tokens"] = None
        c["unseen_reserve_id"] = f"{c['dataset']}/r{c['realization_seed']}/outside100"
        c["admission"] = (
            "v3 population/source decision + complete R1-X6 cache/admission gates + all endpoints/adapters + P1/P2/P3/P4 as applicable + selected checkpoint hashes + explicit budget + lead freeze"
        )
        c["cell_id"] = identity(
            {
                "version": 3,
                "condition": cond,
                "dataset": c["dataset"],
                "realization": c["realization_seed"],
                "order": c["order_seed"],
                "checkpoints": {k: registry[k] for k in cond["checkpoint_ids"]},
                "endpoints": m["endpoint_catalog"],
            }
        )
        suffix = f"<freeze-id>/{cid}/{c['dataset']}/r{c['realization_seed']}/o{c['order_seed']}/{c['cell_id']}"
        c["result_path_template"] = "results/R1/confirm_draft_v3/" + suffix
        c["checkpoint_path_template"] = "assets/runs/R1/confirm_draft_v3/" + suffix
        cells.append(c)
    subtotal = sum(
        c["ceilings"]["legacy_endpoint_proxy_seconds"]
        + c["ceilings"]["legacy_failure_reserve_seconds"]
        for c in cells
    )
    m.update(
        schema_version=3,
        name="run_matrix_draft_v3",
        task="R1-40c",
        status="unlaunchable_unfrozen_expanded_endpoints_and_DEC040",
        sources_sha256=sources,
        cells=cells,
        gpu_seconds=0,
        final_examples_emitted=0,
        sealed_payloads_opened=0,
        extension={
            "previous_core_cells": 180,
            "new_S1_cells": 60,
            "total_cells": 240,
            "S0_reused": "v0_stable",
            "R0_reused": "R1_learned_ff",
            "continued_learned_reader_cells": "owner pilot diagnostics only; not added to DEC-040 S1 primary comparison",
            "model_seed": 0,
        },
    )
    for name in ("continuation_self_stable", "continuation_lm_stable"):
        m["deferred_conditions"].pop(name, None)
    m["budget"] = {
        "evaluation_cells": 240,
        "legacy_endpoint_proxy_subtotal_seconds": subtotal,
        "previous_180_cell_legacy_proxy_seconds": old["budget"][
            "core_draft_seconds_including_20pct_reserve"
        ],
        "new_S1_borrowed_stable_proxy_seconds": subtotal
        - old["budget"]["core_draft_seconds_including_20pct_reserve"],
        "expanded_full_matrix_ceiling_seconds": None,
        "confirmatory_envelope_seconds": 54000,
        "legacy_proxy_alone_exceeds_15h": subtotal > 54000,
        "full_budget_fit": "undetermined until profiling; existing proxies already exceed envelope",
        "profile_full_scope_seconds": None,
        "legacy_P1_P2_allowances_seconds": 5400,
        "new_unseen_prompt_pairs": 240 * 3 * 100,
        "new_unseen_greedy_decodes": 240 * 3 * 100 * 2,
        "shared_training_charge_once": True,
        "interpretation": "legacy proxies are not measured lower bounds or new limits; expanded costs are explicitly unpriced",
    }
    m["data_gates"].update(
        counterfact_candidate_manifest="manifests/revision_v1/counterfact_fresh_candidates_v1.json",
        counterfact_candidate_manifest_sha256=sources[
            str(ROOT / "manifests/revision_v1/counterfact_fresh_candidates_v1.json")
        ],
        counterfact_strict_v3_candidates=cf["counts"]["strict_v3_candidates_without_exception"],
        counterfact_conditional_remainder_candidates=cf["counts"][
            "conditional_remainder_candidates"
        ],
        counterfact_source_option_selected=None,
        minimum_distinct_edit_plus_outside_facts_per_dataset=3300,
        final_edit_realizations=3,
        edits_per_realization=1000,
        outside_reserve_per_realization=100,
        outside_reserve_status="not_drawn_or_sealed",
    )
    m["pruning"]["note"] += (
        "; v3 adds the two DEC-040 S1 conditions as an explicit 60-cell extension"
    )
    m["analysis"]["unseen_margin"] = None
    m["analysis"]["unseen_precision"] = (
        "100 distinct outside prompts per realization is a proposed descriptive sample, not automatic certification of a 1% population false-fire rate"
    )
    m["unresolved"].extend(
        [
            "bind complete continuation checkpoints and matched final evaluation configurations",
            "implement all comparator adapters for memory identities and firing observations",
            "fix exact unseen reserve and statistical rule; distinguish attempted-edit checkpoints from active-memory size",
            "expanded four-profile plan and budget/scope decision",
        ]
    )
    for path, expected in sources.items():
        if sha(path) != expected:
            raise RuntimeError("source changed during matrix build: " + path)
    return validate(m)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository matrix required")
    result = build()
    with args.output.open("x") as f:
        f.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "extension": result["extension"],
                "budget": result["budget"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
