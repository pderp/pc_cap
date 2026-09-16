"""R1-40c: 405 coordinate-stable draft cells, DEC-051 queue and strict freeze audit.

Metadata only. No cost admission, role draw, sealed payload, model, or launch.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path

from scripts.r1_75_analysis_stage4_v1 import (
    COORDS,
    ROOT,
    all_cells,
    coordinate,
    coordinate_id,
    validate_matrix,
)

from pccap.revision_v1.analysis import digest

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
EXT = "R1_learned_ff_v2"
DATASETS = ("zsre", "counterfact", "mquake")
REALIZATIONS = (0, 1, 2)
ORDERS = (100, 101, 102, 103, 104)
CHECKPOINTS = [100, 300, 1000]


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def local(path):
    p = Path(path)
    p = (ROOT / p).resolve() if not p.is_absolute() else p.resolve()
    if not p.is_relative_to(ROOT.parent) or "confirm" in p.parts:
        raise PermissionError("local unsealed metadata/resources only")
    return p


def block(c):
    if c["condition"] == EXT:
        return 6
    if c["condition"].startswith("S1_"):
        return 5
    if c["realization"] == 2:
        return 4
    if c["realization"] == 1:
        return 3
    return 1 if c["condition"] in CORE[:3] else 2


def assemble(conditions, common, sources, candidate):
    def rows(names):
        out = []
        for condition, ds, r, o in itertools.product(names, DATASETS, REALIZATIONS, ORDERS):
            c = {"condition": condition, "dataset": ds, "realization": r, "order": o}
            c.update(
                cell_id=coordinate_id(c),
                block_number=block(c),
                checkpoints=CHECKPOINTS,
                population=None,
                result_dir=None,
                manifest_sha256=None,
                admitted=False,
                launch_allowed=False,
                model_seed=0,
            )
            recipe = conditions[condition]["recipes"][ds]
            c.update(
                recipe_family=recipe["family"],
                recipe_template=recipe["template"],
                calibration_receipt=None
                if recipe["requires_mquake_calibration"]
                else recipe.get("calibration"),
                calibration_pending=recipe["requires_mquake_calibration"],
                expected_definition_sha256=digest(
                    {
                        "coordinate": {k: c[k] for k in COORDS},
                        "condition": conditions[condition],
                        "common": common,
                        "recipe": recipe,
                        "checkpoints": CHECKPOINTS,
                    }
                ),
                ceilings={
                    "wall_seconds": None,
                    "watchdog_seconds": None,
                    "persistent_bytes": None,
                    "failure_reserve_seconds": None,
                    "checkpoint_seconds": {str(n): None for n in CHECKPOINTS},
                    "profile_receipt_sha256": None,
                    "admitted": False,
                    "remeasure_date": "2026-09-20",
                },
                pairing_id=f"{ds}/r{r}/o{o}",
                outside_population_id=f"{ds}/r{r}/outside100",
                result_path_template=f"results/R1/stage4/<freeze-id>/B{block(c)}/{c['cell_id']}",
            )
            out.append(c)
        return out

    cells = rows(CORE)
    extension = rows([EXT])
    every = cells + extension
    for b in range(1, 7):
        ordered = sorted(
            (c for c in every if c["block_number"] == b),
            key=lambda c: (
                DATASETS.index(c["dataset"]),
                (*CORE, EXT).index(c["condition"]),
                c["realization"],
                c["order"],
            ),
        )
        for i, c in enumerate(ordered, 1):
            c["within_block_order"] = i
    return {
        "schema_version": 5,
        "name": "run_matrix_v5",
        "task": "R1-40c",
        "scope": "confirmation_draft",
        "status": "draft metadata; no execution identities, populations, costs or freeze admission",
        "axes": {
            "conditions": list(CORE),
            "datasets": list(DATASETS),
            "realizations": list(REALIZATIONS),
            "orders": list(ORDERS),
        },
        "conditions": conditions,
        "common_identity": common,
        "sources_sha256": sources,
        "freeze_candidate_reference": candidate,
        "cells": cells,
        "extension": {
            "condition": EXT,
            "cells": extension,
            "interpretation": "historical two-pool v2 package, gate disabled; NOT a same-v5-weights gate-only ablation",
            "allocation_approved": False,
        },
        "launch_allowed": False,
        "draw_authorized": False,
        "confirmation_protocol_frozen": False,
        "contrasts": [
            {"id": "primary-vs-" + c, "treatment": "R1_learned_ff", "control": c, "role": "primary"}
            for c in CORE[1:]
        ]
        + [
            {
                "id": "primary-vs-historical-v2",
                "treatment": "R1_learned_ff",
                "control": EXT,
                "role": "secondary",
            }
        ],
        "bootstrap": {"seed": 0, "draws": 10000, "confidence": 0.975},
        "multiplicity": {
            "status": "unresolved_U12",
            "family": "seven primary/control contrasts per dataset across three datasets; final family/gatekeeping unresolved",
            "interval_interpretation": "draft pointwise clustered intervals; not simultaneous familywise control",
        },
        "coordinate_identity": "SHA256 of schema stage4-cell-coordinate-v1 and four coordinates, first24hex; independent of weights, ceilings and paths",
        "execution_identity": "expected_definition_sha256 binds scientific templates; final recipe/code/payload/ceilings require separate versioned receipt before launch",
        "queue": {
            "order_fields": ["block_number", "within_block_order"],
            "block_sizes": [45, 45, 90, 90, 90, 45],
            "block_labels": [
                "primary/random/stable r0",
                "matched/liveC1/liveC2 r0",
                "first six r1",
                "first six r2",
                "S1 both all realizations",
                "historical v2 extension",
            ],
            "optional_between_B3_B4": {
                "task": "HT-7h",
                "run_if": "lead decision on Q4/Q5 and separate bound budget",
                "cell_count_in_this_matrix": 0,
            },
            "attempts": "new attempt-0000, attempt-0001, ...; never overwrite a completed or failed attempt",
            "resume": "verify unique contiguous checkpoint prefix, receipt chain, recipe, code, payload, base/config/reader and snapshot/state hashes; restore last durable checkpoint",
            "incremental_resume": "verify every prior journal including failed/unreceipted work; torn/open intent or unknown spend refuses automatic resume",
            "identity_mismatch": "abort without issuing checkpoint receipt; stop queue for owner reconciliation, never silently rebind or skip",
            "retry": "no automatic retry in cell driver; owner creates new attempt only after verified resume eligibility and failure-cost reconciliation",
            "completed_cell": "skip only when a terminal receipt chain and matching completion result verify against the bound matrix",
            "training_charged_once": True,
            "failed_and_partial_work_charged": True,
            "shutdown": "stop at experiment deadline 2026-10-09; report complete blocks plus exact incomplete cell/checkpoint IDs under DEC-052",
            "freeze": "final driver/analysis/code/environment identities must be rebound after approved scoring/driver edits",
        },
        "population": {
            "candidate_subject_counts": common["candidate_subject_counts"],
            "required_subjects_each_dataset": 4050,
            "guaranteed_clearance": False,
            "final_role_population_bound": False,
        },
        "budget": {
            "core_cells": 360,
            "extension_cells": 45,
            "total_cells": 405,
            "measured_total_ceiling_seconds": None,
            "costs_admitted": False,
        },
        "open_lead_items": [
            "Q4 kappa",
            "Q5 stress",
            "U12 multiplicity",
            "U14 secondary thresholds",
            "extension package interpretation",
            "Q10 MQuAKE occupancy",
        ],
        "gpu_seconds": 0,
        "model_calls": 0,
        "sealed_payloads_opened": 0,
        "final_examples_emitted": 0,
    }


def validate(m):
    validate_matrix(m)
    for key in ("launch_allowed", "draw_authorized", "confirmation_protocol_frozen"):
        if m[key] is not False:
            raise ValueError("draft authorization violation")
    if len(m["cells"]) != 360 or len(m["extension"]["cells"]) != 45:
        raise ValueError("incorrect cell counts")
    for rows, names in ((m["cells"], CORE), (m["extension"]["cells"], [EXT])):
        if {coordinate(c) for c in rows} != set(
            itertools.product(names, DATASETS, REALIZATIONS, ORDERS)
        ):
            raise ValueError("incomplete/unexpected axes")
    for b, want in enumerate((45, 45, 90, 90, 90, 45), 1):
        rows = [c for c in all_cells(m) if c["block_number"] == b]
        if len(rows) != want or sorted(c["within_block_order"] for c in rows) != list(
            range(1, want + 1)
        ):
            raise ValueError("block order/capacity mismatch")
    for c in all_cells(m):
        if c["block_number"] != block(c) or c["checkpoints"] != CHECKPOINTS:
            raise ValueError("DEC-051/cadence mismatch")
        if c["admitted"] is not False or c["launch_allowed"] is not False:
            raise ValueError("cell admission not authorized")
        limits = c["ceilings"]
        if limits["admitted"] is not False or any(
            limits[k] is not None
            for k in (
                "wall_seconds",
                "watchdog_seconds",
                "persistent_bytes",
                "failure_reserve_seconds",
                "profile_receipt_sha256",
            )
        ):
            raise ValueError("unmeasured ceilings must remain null")
        if limits["checkpoint_seconds"] != {str(n): None for n in CHECKPOINTS}:
            raise ValueError("checkpoint ceiling not null")
        recipe = m["conditions"][c["condition"]]["recipes"][c["dataset"]]
        want = digest(
            {
                "coordinate": {k: c[k] for k in COORDS},
                "condition": m["conditions"][c["condition"]],
                "common": m["common_identity"],
                "recipe": recipe,
                "checkpoints": CHECKPOINTS,
            }
        )
        if (
            c["expected_definition_sha256"] != want
            or c["recipe_family"] != recipe["family"]
            or c["recipe_template"] != recipe["template"]
        ):
            raise ValueError("execution definition binding mismatch")
    return m


def build():
    sources = {}

    def bind(path):
        p = local(path)
        h = sha(p)
        sources[str(p)] = h
        return {"path": str(p), "sha256": h}

    def read(path):
        ref = bind(path)
        return json.loads(Path(ref["path"]).read_text()), ref

    old, oldref = read("manifests/revision_v1/run_matrix_draft_v4.json")
    primary, primaryref = read("manifests/revision_v1/primary_condition_v5.json")
    _, selection = read(primary["selection"]["manifest"])
    if selection["sha256"] != primary["selection"]["sha256"]:
        raise ValueError("selected reference mismatch")
    register, registerref = read("manifests/revision_v1/exclusions_frozen_v6.json")
    _, candidate = read("manifests/revision_v1/freeze_candidate_v4.json")
    spec, specref = read("docs/tasks/R1-73-mquake-calibration.spec.json")
    common = copy.deepcopy(old["common_identity"])
    common.update(
        selected_reference=primaryref,
        selection=selection,
        register=registerref,
        candidate_subject_counts={
            k: v["candidate_subjects"] for k, v in register["counts"].items()
        },
        locality_convention="DEC-053 bounded equality primary; termination and truncation alongside",
        historical_matrix=oldref,
        selected_training_seed=2,
    )
    conditions = {}
    for cid in (*CORE, EXT):
        templates = {}
        for ds in ("zsre", "counterfact"):
            path = (
                f"docs/tasks/R1-64-{ds}-v5.recipe.json"
                if cid == CORE[0] and ds == "counterfact"
                else "docs/tasks/R1-68b-zsre-v5-full.recipe.json"
                if cid == CORE[0]
                else f"docs/tasks/R1-64b-{ds}-{cid}.recipe.json"
            )
            doc, ref = read(path)
            if doc["cell"]["condition"] != cid or doc["cell"]["dataset"] != ds:
                raise ValueError("template coordinates mismatch")
            templates[ds] = {
                "family": "R1-64" if cid == CORE[0] else "R1-64b",
                "template": ref,
                "adapter_identity": doc["adapter_identity"],
                "construction": doc["construction"],
                "calibration": common["calibration"],
                "requires_mquake_calibration": False,
                "status": "development constructor template; final payload/code/budget recipe pending",
            }
        mq = copy.deepcopy(templates["zsre"])
        mq["family"] = (
            "R1-73-calibrated" if not cid.startswith("R1_") else templates["zsre"]["family"]
        )
        mq["requires_mquake_calibration"] = not cid.startswith("R1_")
        mq["calibration_spec"] = specref if mq["requires_mquake_calibration"] else None
        mq["status"] = (
            "no MQuAKE execution recipe admitted; new cleared payload and owner calibration receipt required"
        )
        templates["mquake"] = mq
        conditions[cid] = {
            "condition": cid,
            "recipes": templates,
            "interpretation": "selected v5"
            if cid == CORE[0]
            else "historical two-pool package, no rare gate"
            if cid == EXT
            else "registered comparator",
            "reference": primaryref
            if cid != EXT
            else bind("manifests/revision_v1/primary_condition_v2.json"),
        }
        if (
            cid == CORE[0]
            and templates["zsre"]["construction"]["weights"]["sha256"]
            != primary["weights"]["sha256"]
        ):
            raise ValueError("primary template weights do not match selected v5")
    if (
        spec["bank_scales"]
        != conditions[CORE[0]]["recipes"]["zsre"]["construction"]["calibration"]["bank_scales"]
    ):
        raise ValueError("calibration bank-scale policy mismatch")

    # File content hashes only; no parameter arrays or sealed payloads loaded.
    def declared(value):
        if isinstance(value, dict):
            if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
                actual = bind(value["path"])
                if actual["sha256"] != value["sha256"]:
                    raise ValueError("declared resource changed")
            for v in value.values():
                declared(v)
        elif isinstance(value, list):
            for v in value:
                declared(v)

    declared(conditions)
    result = assemble(conditions, common, sources, candidate)
    for p, h in sources.items():
        if sha(p) != h:
            raise ValueError("matrix input changed")
    return validate(result)


def audit_freeze(matrix, candidate):
    validate(matrix)
    bindings = candidate["bindings_sha256"]
    changed = []
    missing = []
    conflicts = []
    for name, expected in bindings.items():
        p = local(name)
        if not p.is_file():
            missing.append(name)
        elif sha(p) != expected:
            changed.append(name)
    for name, h in matrix["sources_sha256"].items():
        if sha(local(name)) != h:
            raise ValueError("matrix source changed: " + name)
        if name in bindings and bindings[name] != h:
            conflicts.append(name)
    for field in ("primary_condition", "selection", "register"):
        key = {"primary_condition": "selected_reference"}.get(field, field)
        if candidate[field] != matrix["common_identity"][key]:
            conflicts.append("authority:" + field)
    new_bindings = sorted(set(matrix["sources_sha256"]) - set(bindings))
    return {
        "task": "R1-40c",
        "structural_valid": True,
        "ready_for_freeze": False,
        "candidate_name": candidate["name"],
        "candidate_stale_bindings": changed,
        "candidate_missing_files": missing,
        "binding_conflicts": conflicts,
        "new_bindings_required": new_bindings,
        "coordinate_count": 405,
        "block_counts": [45, 45, 90, 90, 90, 45],
        "candidate_matrix_is_predecessor": candidate["matrix"]
        == matrix["common_identity"]["historical_matrix"],
        "must_rebind": [
            "matrix v5",
            "protocol v5",
            "approved scoring and R1-68d driver",
            "new analysis/runner modules",
            "final populations and costs",
            "closed gate receipts",
        ],
        "no_admission_reason": "dry candidate v4 binds historical matrix/protocol and open gates; matching subset is not final approval",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--matrix", type=Path)
    ap.add_argument("--freeze-audit-output", type=Path)
    a = ap.parse_args(argv)
    if bool(a.output) == bool(a.matrix):
        ap.error("choose --output (new draft) or --matrix (validate)")
    paths = [p.resolve() for p in (a.output, a.freeze_audit_output) if p is not None]
    if any(p.exists() or not p.is_relative_to(ROOT) for p in paths):
        ap.error("new repo outputs only")
    m = build() if a.output else validate(json.loads(a.matrix.read_text()))
    candidate = json.loads(Path(m["freeze_candidate_reference"]["path"]).read_text())
    if sha(m["freeze_candidate_reference"]["path"]) != m["freeze_candidate_reference"]["sha256"]:
        raise ValueError("candidate reference changed")
    audit = audit_freeze(m, candidate)
    for p, obj in ((a.output, m), (a.freeze_audit_output, audit)):
        if p is not None:
            with p.open("x") as f:
                json.dump(obj, f, indent=2, sort_keys=True, allow_nan=False)
                f.write("\n")
    print(json.dumps(audit, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
