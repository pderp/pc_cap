"""R1-63: assemble a hash-checked freeze candidate; never a freeze, draw or launch."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pccap.revision_v1.analysis import digest
from pccap.revision_v1.stage4_cell import ROOT, sha, write_json

PROTOCOL = ROOT / "docs/R1_stage4_protocol_draft_v2.md"
OUTPUT = ROOT / "manifests/revision_v1/freeze_candidate_v1.json"


def verify_bindings(bindings):
    for name, expected in bindings.items():
        p = Path(name).resolve()
        if "confirm" in p.parts:
            raise PermissionError("candidate assembler never opens sealed payloads")
        if not re.fullmatch("[0-9a-f]{64}", expected) or not p.is_file() or sha(p) != expected:
            raise ValueError("missing or mismatched bound file: " + name)


def gate_inventory(protocol):
    gates = []
    for line in protocol.splitlines():
        match = re.match(r"\| (U\d\d) ([^|]+)\| ([^|]+)\|", line)
        if match:
            gate, title, status = match.groups()
            gates.append(
                {
                    "gate": gate,
                    "title": title.strip(),
                    "protocol_status": status.strip(),
                    "status": "open_admission",
                    "lead_closure_receipt": None,
                }
            )
    if [g["gate"] for g in gates] != [f"U{i:02d}" for i in range(1, 19)]:
        raise ValueError("complete U01-U18 inventory required")
    return gates


def build():
    bindings = {}

    def bind(path, expected=None):
        p = Path(path)
        p = p if p.is_absolute() else ROOT / p
        p = p.resolve()
        h = expected if expected is not None else sha(p)
        verify_bindings({str(p): h})
        bindings[str(p)] = h
        return {"path": str(p), "sha256": h}

    def read(path, expected=None):
        ref = bind(path, expected)
        return json.loads(Path(ref["path"]).read_text())

    def declared(obj):
        # Explicit path/hash pairs in the selected live construction documents.
        if isinstance(obj, dict):
            if "path" in obj and "sha256" in obj:
                bind(obj["path"], obj["sha256"])
            for value in obj.values():
                declared(value)
        elif isinstance(obj, list):
            for value in obj:
                declared(value)

    primary = read("manifests/revision_v1/primary_condition_v4.json")
    declared(primary["weights"])
    declared(primary["stop_tokens"])
    for pool, h in primary["pools"].items():
        bind(f"manifests/revision_v1/{pool}.json", h)
    register = read("manifests/revision_v1/exclusions_frozen_v4.json")
    effective = read("manifests/revision_v1/exclusions_frozen_v4_supplement_v2.json")
    for name, h in {**register["bindings_sha256"], **effective["bindings_sha256"]}.items():
        bind(name, h)
    pool_inventory = sorted(ROOT.glob("manifests/revision_v1/train_pool_mquake_v*.json")) + sorted(
        ROOT.glob("manifests/dev/mquake_dev*.json")
    )
    if effective["source_inventory"] != [str(p) for p in pool_inventory]:
        raise ValueError("new MQuAKE pool version not included in effective supplement")
    for name in (
        "exclusions_frozen_v4_supplement_v1.json",
        "exclusions_frozen_v4_supplement_v1_rebound.json",
    ):
        bind("manifests/revision_v1/" + name)
    historical_training = [
        bind(f"manifests/revision_v1/train_pool_{ds}_v1.json")
        for ds in ("zsre", "counterfact", "mquake")
    ]
    proposed = bind("manifests/revision_v1/train_pool_mquake_v3.json")
    datasets = [bind(f"manifests/dev/{ds}_dev.json") for ds in ("zsre", "counterfact", "mquake")]
    datasets.append(bind("manifests/dev/mquake_dev_v3.json"))
    datasets.append(bind("manifests/dev/challenges.json"))
    for name in ("mquake_pool_v1.json", "mquake_items_v1.json", "zsre_fresh_candidates_v1.json"):
        bind("manifests/revision_v1/" + name)
    prepared = read("manifests/revision_v1/mquake_items_v1.json")
    declared(prepared["artifacts"])
    matrix_path = "manifests/revision_v1/run_matrix_draft_v3.json"
    matrix = read(matrix_path)
    recipe = read("docs/tasks/R1-64-zsre-v4.recipe.json")
    declared(recipe["construction"])
    declared(recipe["reader_provenance"])
    for name, h in recipe["construction"]["base"]["files"].items():
        bind(Path(recipe["construction"]["base"]["path"]) / name, h)
    for name, h in recipe["source_bindings_sha256"].items():
        bind(name, h)
    # The worked payload is unsealed and is not a future confirmatory population.
    bind(recipe["payload"]["path"], recipe["payload"]["sha256"])
    controls = []
    for tag in ("r1_24_literal_v3b", "r1_24_lm_v3_lr1e-8"):
        p = f"results/R1/r1_24/{tag}/summary.json"
        sm = read(p)
        declared(sm["checkpoint"])
        controls.append(
            {
                "summary": bind(p),
                "checkpoint": sm["checkpoint"],
                "status": "development checkpoint; final v4 compute/admission pending",
            }
        )
    for name in (
        "r1_24_control_v3.json",
        "r1_24_control_lm_v3_lr1e-8.json",
        "r1_24_budget_reconciliation_v1.json",
    ):
        bind("manifests/revision_v1/" + name)
    for name in (
        "docs/decisions.md",
        "docs/lead_queue.md",
        "docs/environment.md",
        "requirements.lock",
        "results/S2/radius_calibration.json",
        "results/S2/residual_scales.json",
        "docs/R1_stage2_report.md",
        "docs/R1_stage2_notes.md",
        "src/pccap/revision_v1/analysis_stage4.py",
        "src/pccap/revision_v1/analysis.py",
        "src/pccap/revision_v1/stage4_adapters.py",
        "src/pccap/revision_v1/stage4_assays.py",
        "src/pccap/revision_v1/stage4_cell.py",
        "src/pccap/revision_v1/development_cell.py",
        "scripts/r1_61_cell_driver.py",
        "scripts/r1_64_dev_cell.py",
        "scripts/r1_64_dev_payload.py",
        "scripts/r1_57b_stage4_inventory.py",
        "scripts/r1_58_draw_streams.py",
        "logs/r1_round11/exposure_audit.json",
        __file__,
    ):
        bind(name)
    protocol = bind(PROTOCOL)
    gates = gate_inventory(PROTOCOL.read_text())
    code_files = {
        str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / "src/pccap").rglob("*.py"))
    }
    for name, h in code_files.items():
        bind(name, h)
    sections = {
        "protocol_decisions_matrix_contrasts": {
            "protocol": protocol,
            "matrix": bind(matrix_path),
            "declared_cells": len(matrix["cells"]),
            "protocol_cells": 360,
            "status": "BLOCKED: matrix v3 still contains 240 cells and two datasets",
            "primary_contrasts_and_multiplicity": "lead decision required",
        },
        "executable_environment_hardware": {
            "src_pccap_tree_sha256": digest(code_files),
            "hash_convention": "analysis.digest(relative POSIX .py paths -> file SHA256)",
            "src_pccap_files": code_files,
            "environment": bind("requirements.lock"),
            "hardware_runtime_identity": "pending owner capture; no GPU queried",
        },
        "base_reader_and_continuation": {
            "reader_manifest": bind("manifests/revision_v1/primary_condition_v4.json"),
            "weights": primary["weights"],
            "reader_seeds": [0, 1, 2],
            "matrix_model_seed": matrix["axes"]["model_training_seed"],
            "original_base": recipe["construction"]["base"],
            "continued_controls": controls,
            "status": "v4 is trained on MQuAKE v2; proposed v3 slice retraining will require new weights/version",
        },
        "calibration_tokenizer_masks_stop_null_rarity": {
            "calibration": recipe["construction"]["calibration"],
            "calibration_source": recipe["reader_provenance"]["calibration"],
            "tokenizer_sha256": recipe["tokenizer_sha256"],
            "stop_tokens": primary["stop_tokens"],
            "rules": {
                "rare_overlap_min": 1,
                "rare_df_max": 2,
                "null_threshold": 0.5,
                "min_score": None,
                "hard_top1": True,
                "binary_write_mass": True,
                "top_k": 4,
                "lex_idf": False,
            },
            "masks": "bound installed observations.py; final all-dataset calibration admission pending",
        },
        "exclusions_and_exposure": {
            "register": bind("manifests/revision_v1/exclusions_frozen_v4.json"),
            "effective_supplement": bind(
                "manifests/revision_v1/exclusions_frozen_v4_supplement_v2.json"
            ),
            "counts": effective["counts"],
            "released_subjects": 0,
            "superseded_binding_policy": "v1 and rebound are historical provenance; v2 is effective. Historical embedded producer hashes are not current-code claims.",
        },
        "eligible_ordered_payloads_challenge_dependencies": {
            "development_manifests": datasets,
            "prepared_mquake": bind("manifests/revision_v1/mquake_items_v1.json"),
            "final_realizations": None,
            "final_orders": None,
            "final_roles": None,
            "final_seals": None,
            "status": "not drawn, not sealed, not admitted",
        },
        "training_validation_and_caches": {
            "historical_pools": historical_training,
            "proposed_mquake_pool": proposed,
            "reader_bound_pools": primary["pools"],
            "audit": bind("logs/r1_round11/exposure_audit.json"),
            "status": "new slices are prospective; historical exclusions persist",
        },
        "endpoint_denominators_and_references": {
            "checkpoints": [100, 300, 1000],
            "max_new": 32,
            "development_example": bind("docs/tasks/R1-64-zsre-v4.recipe.json"),
            "final_independent_inventory": None,
            "full_validation_window_binding": None,
            "status": "final denominators, LS convention and reference policy require lead admission",
        },
        "bytes_eviction_restore": {
            "implementation": bind("src/pccap/revision_v1/stage4_cell.py"),
            "status": "CPU receipts/restore implemented; all-condition physical/profile admission pending",
        },
        "ceilings_cost_ownership_retry": {
            "matrix_budget": matrix["budget"],
            "accepted_ceilings": None,
            "shared_cost_reconciliation": bind(
                "manifests/revision_v1/r1_24_budget_reconciliation_v1.json"
            ),
            "status": "legacy 15h/240-cell matrix is stale; 360-cell measured ceilings and retry policy pending",
        },
        "analysis_inventory_bootstrap_margins": {
            "adapter": bind("src/pccap/revision_v1/analysis_stage4.py"),
            "implementation": bind("src/pccap/revision_v1/analysis.py"),
            "registered_inventory": None,
            "multiplicity_admitted": False,
            "status": "CPU implementation bound; statistical admission pending",
        },
        "lead_approval": {
            "identity": None,
            "protocol_frozen": False,
            "draw_authorized": False,
            "launch_authorized": False,
        },
    }
    result = {
        "schema_version": 1,
        "name": "freeze_candidate_v1",
        "task": "R1-63",
        "mode": "dry_freeze_candidate",
        "status": "incomplete candidate; not a protocol freeze",
        "sections": sections,
        "open_gates": gates,
        "bindings_sha256": bindings,
        "freeze_ready": False,
        "draw_authorized": False,
        "launch_authorized": False,
        "sealed_payloads_opened": 0,
        "draws_emitted": 0,
        "seals_emitted": 0,
        "gpu_seconds": 0,
        "verification_scope": "Every file in bindings_sha256 is checked. Historical prose/embedded legacy references are provenance only, not recursively promoted to live requirements.",
    }
    verify_bindings(bindings)
    return result


def write_candidate(path, candidate):
    p = Path(path).resolve()
    if not p.is_relative_to(ROOT / "manifests/revision_v1") or not re.fullmatch(
        r"freeze_candidate_[A-Za-z0-9_-]+\.json", p.name
    ):
        raise PermissionError("only a versioned revision_v1 freeze_candidate filename is allowed")
    if any(
        candidate.get(k) is not False
        for k in ("freeze_ready", "draw_authorized", "launch_authorized")
    ):
        raise PermissionError("candidate cannot authorize a freeze/draw/launch")
    verify_bindings(candidate["bindings_sha256"])
    return write_json(p, candidate)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=OUTPUT)
    a = ap.parse_args(argv)
    if a.output.exists():
        raise FileExistsError("candidate already exists")
    candidate = build()
    ref = write_candidate(a.output, candidate)
    print(
        json.dumps(
            {
                "candidate": ref,
                "open_gates": [g["gate"] for g in candidate["open_gates"]],
                "matrix_cells": candidate["sections"]["protocol_decisions_matrix_contrasts"][
                    "declared_cells"
                ],
                "freeze_ready": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
