"""Owner-gated R1-D9 producers; default inspection never draws or seals.

Each of the three public entry points has an independent request and receipt.
Review evidence is an input: this tool cannot certify semantic alias/teacher
judgments or grant itself the lead's approval.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
from scripts import r1_d9_receipt_core as core
from scripts.r1_58c_draw_seal_preflight import check_receipt, read_metadata
from scripts.r1_75_analysis_stage4_v1 import COORDS, coordinate_id
from scripts.r1_d1i_register_v6 import verify_register

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
REQUIRED = {
    "clearance": ["clearance_authorization"],
    "draw": [
        "clearance_authorization",
        "joint_clearance",
        "protocol_admission",
        "rng_admission",
        "draw_authorization",
    ],
    "seal": [
        "joint_clearance",
        "protocol_admission",
        "rng_admission",
        "draw_authorization",
        "draw_receipt",
        "endpoint_construction",
        "seal_authorization",
    ],
}
RECEIPT_NAMES = {"clearance": "joint_clearance", "draw": "draw_receipt", "seal": "seal_receipt"}


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def ref(path):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": sha(path)}


def read_resource(binding):
    """Only explicitly bound unsealed input resources, never an implicit search."""
    core.require(
        isinstance(binding, dict)
        and isinstance(binding.get("path"), str)
        and isinstance(binding.get("sha256"), str),
        "required unsealed resource path/SHA binding is not supplied",
    )
    p = Path(binding["path"]).resolve()
    if not p.is_relative_to(ASSETS) or "confirm" in p.parts:
        raise PermissionError("explicit assets resource required")
    if sha(p) != binding["sha256"]:
        raise ValueError("resource hash mismatch: " + str(p))
    value = json.loads(p.read_text())
    if sha(p) != binding["sha256"]:
        raise ValueError("resource changed during read")
    return value


def implementation_bindings():
    names = [
        "scripts/r1_58_draw_streams.py",
        "scripts/r1_58c_draw_seal_preflight.py",
        "scripts/r1_d1i_register_v6.py",
        "scripts/r1_75_analysis_stage4_v1.py",
        "scripts/r1_77b_sealed_backend.py",
    ]
    names += [str(p.relative_to(ROOT)) for p in sorted((ROOT / "src/pccap").rglob("*.py"))]
    return {n: sha(ROOT / n) for n in names}


def contract(spec, stage):
    """No authorization self-hash or output receipt enters its own request."""
    return core.content_digest(
        {
            "stage": stage,
            "register": spec["register"],
            "matrix": spec["matrix"],
            "protocol": spec["protocol"],
            "configuration": spec["d9"][stage],
            "prerequisites": {
                n: spec["receipts"].get(n) for n in REQUIRED[stage] if n != stage + "_authorization"
            },
            "producer": ref(__file__),
            "core": ref(ROOT / "scripts/r1_d9_receipt_core.py"),
            "dependencies": implementation_bindings(),
        }
    )


def admitted_receipts(spec, stage):
    receipts, errors = {}, []
    for name in REQUIRED[stage]:
        try:
            binding = spec["receipts"][name]
            core.require(
                bool(binding.get("path")) and bool(binding.get("sha256")), "receipt not supplied"
            )
            receipt = read_metadata(binding)
            check_receipt(name, receipt, spec)
            receipts[name] = receipt
        except (OSError, KeyError, TypeError, ValueError, PermissionError) as error:
            errors.append(name + ": " + str(error))
    core.require(not errors, "; ".join(errors))
    auth = receipts[stage + "_authorization"]
    core.require(
        auth.get("operation") == stage and auth.get("request_sha256") == contract(spec, stage),
        "authorization does not bind this exact producer request",
    )
    return receipts


def source_rows(register):
    wrapper_path = ROOT / "manifests/revision_v1/exclusions_frozen_v3.json"
    core.require(
        register["bindings_sha256"].get(str(wrapper_path)) == sha(wrapper_path),
        "source wrapper not bound by register",
    )
    wrapper = json.loads(wrapper_path.read_text())
    sources = {
        "zsre": wrapper["zsre"]["historical_review_resources"]["clear_candidates"]["path"],
        "counterfact": wrapper["counterfact"]["conditional_old_remainder"]["path"],
        "mquake": str(ASSETS / "data/prepared/revision_v1/r1_d4_v1/items.jsonl"),
    }
    result = {}
    for ds, name in sources.items():
        path = Path(name).resolve()
        core.require(path.is_relative_to(ASSETS), "source must be an assets resource")
        wanted = {r["item_id"] for r in register["candidates"][ds]}
        expected = register["bindings_sha256"][str(path)]
        core.require(sha(path) == expected, "prepared source changed")
        rows = []
        with path.open() as f:
            for line in f:
                r = json.loads(line)
                if r["item_id"] in wanted:
                    rows.append(r)
        core.require(sha(path) == expected, "prepared source changed during read")
        result[ds] = rows
    return result


def clearance_value(spec, register, evidence, rows):
    core.require(evidence.get("register") == spec["register"], "review/register binding differs")
    eligible, counts = core.review_candidates(register, rows, evidence)
    for binding in evidence.get("evidence_bindings", []):
        path = Path(binding["path"]).resolve()
        core.require(
            path.is_relative_to(ROOT.parent)
            and "confirm" not in path.parts
            and sha(path) == binding["sha256"],
            "clearance evidence binding changed",
        )
    core.require(
        bool(evidence.get("evidence_bindings")),
        "underlying review/teacher/exposure evidence must be bound",
    )
    return {
        "schema_version": 1,
        "mode": "reviewed_unsealed_candidates",
        "register": spec["register"],
        "evidence": spec["d9"]["clearance"]["evidence"],
        "candidates": eligible,
        "counts": counts,
        "all_dispositions": evidence["dispositions"],
        "base_tensor_sha256": evidence["base_tensor_sha256"],
        "tokenizer_sha256": evidence["tokenizer_sha256"],
    }


def paired_orders(reservations):
    orders, streams = {}, {}
    for g in reservations["allocations"]:
        if g["role"] != "edits":
            continue
        ids = [r["item_id"] for r in g["items"]]
        for order in range(100, 105):
            coordinate = {
                "namespace": "R1-D9-order-v1",
                "seed": reservations["seed"],
                "register_sha256": reservations["register"]["sha256"],
                "dataset": g["dataset"],
                "realization": g["realization"],
                "order": order,
            }
            derived = int(core.content_digest(coordinate)[:32], 16)
            rng = np.random.Generator(np.random.PCG64(derived))
            initial = copy.deepcopy(rng.bit_generator.state)
            key = f"{g['dataset']}:{g['realization']}:{order}"
            orders[key] = [ids[int(i)] for i in rng.permutation(len(ids))]
            streams[key] = {
                "coordinates": coordinate,
                "derived_seed": derived,
                "initial_state": initial,
                "final_state": rng.bit_generator.state,
            }
    return {"orders": orders, "order_rng_substreams": streams}


def planned_compositions(reservations, catalog):
    result = {}
    for g in reservations["allocations"]:
        if g["role"] != "edits":
            continue
        ids = {r["item_id"] for r in g["items"]}
        all_cases = catalog.get(g["dataset"], [])
        core.require(
            len({c["composition_id"] for c in all_cases}) == len(all_cases),
            "duplicate composition catalog IDs",
        )
        # Predetermined membership rule, never an outcome-based selection.
        included = [c for c in all_cases if set(core.dependency_ids(c)) <= ids]
        result[f"{g['dataset']}:{g['realization']}"] = included
    return result


def draw_value(spec, receipts):
    cfg = spec["d9"]["draw"]
    clearance = receipts["joint_clearance"]
    candidates = read_resource(clearance["cleared_candidates"])
    core.require(candidates["register"] == spec["register"], "clearance candidate register differs")
    rng = receipts["rng_admission"]
    core.require(
        rng.get("rng_rule") == core.RNG_RULE
        and rng.get("numpy_version") == np.__version__
        and rng.get("master_seed") == cfg["master_seed"],
        "RNG algorithm/version/seed not admitted",
    )
    core.require(
        rng.get("paired_order_rule")
        == "R1-D9-order-v1; orders100..104; same order for every condition"
        and rng.get("composition_rule")
        == "all bound catalog cases with every dependency in the realization edit set",
        "paired order/composition rule not admitted",
    )
    core.require(
        receipts["draw_authorization"].get("cumulative_exposure_current") is True,
        "draw-time exposure attestation required",
    )
    # Recheck the original review resources at draw time, not just receipt booleans.
    evidence = read_resource(candidates["evidence"])
    for b in evidence["evidence_bindings"]:
        core.require(sha(b["path"]) == b["sha256"], "review evidence changed after clearance")
    allocation = core.allocate(
        candidates["candidates"],
        seed=cfg["master_seed"],
        register_sha256=spec["register"]["sha256"],
    )
    reservation = core.reservation_document(allocation, spec["register"])
    core.audit_reservations(reservation)
    reservation.update(paired_orders(reservation))
    reservation["planned_compositions"] = planned_compositions(
        reservation, read_resource(cfg["composition_catalog"])
    )
    reservation["composition_catalog"] = cfg["composition_catalog"]
    reservation["clearance_receipt"] = spec["receipts"]["joint_clearance"]
    reservation["rng_admission"] = spec["receipts"]["rng_admission"]
    return reservation


def matrix_cells(matrix, protocol):
    core.require(
        protocol.get("matrix") == matrix["binding"], "protocol admission must bind current matrix"
    )
    cells = list(matrix["document"]["cells"])
    if protocol.get("extension_admitted") is True:
        cells += matrix["document"].get("extension", {}).get("cells", [])
    elif protocol.get("extension_admitted") is not False:
        raise ValueError("explicit extension admission required")
    return [{k: r[k] for k in COORDS} for r in cells]


def seal_values(spec, receipts, matrix):
    cfg = spec["d9"]["seal"]
    draw = receipts["draw_receipt"]
    reservation = read_resource(draw["reservations"])
    core.require(
        reservation["register"] == spec["register"]
        and reservation["mode"] == "unsealed_fact_reservations",
        "unsealed v6 draw required",
    )
    construction = receipts["endpoint_construction"]
    core.require(
        construction.get("draw_receipt") == spec["receipts"]["draw_receipt"]
        and construction.get("reservations") == draw["reservations"],
        "endpoint construction must bind exact draw",
    )
    core.require(
        construction.get("bundle") == cfg["bundle"]
        and construction.get("independent_population") == cfg["independent_population"],
        "endpoint receipt differs from requested bundle/population",
    )
    bundle = read_resource(cfg["bundle"])
    population = read_resource(cfg["independent_population"])
    cells = matrix_cells(matrix, receipts["protocol_admission"])
    payloads, by_binding, by_content = {}, {}, {}
    for cid, binding in bundle["payloads"].items():
        key = (binding["path"], binding["sha256"])
        if key not in by_binding:
            value = read_resource(binding)
            content = core.content_digest(value)
            by_content.setdefault(content, value)
            by_binding[key] = by_content[content]
        payloads[cid] = by_binding[key]
    identities = core.validate_seal(reservation, cells, payloads, population)
    for cell in cells:
        cid = coordinate_id(cell)
        group = f"{cell['dataset']}:{cell['realization']}"
        order = group + ":" + str(cell["order"])
        core.require(
            [r["item_id"] for r in payloads[cid]["items"]] == reservation["orders"][order],
            "paired edit order differs from draw",
        )
        ep = payloads[cid]["endpoints"]["composition"]
        planned = reservation["planned_compositions"][group]
        core.require(
            ep["expected_ids"] == [c["composition_id"] for c in planned] and ep["rows"] == planned,
            "composition differs from pre-outcome membership plan",
        )
    sealed = copy.deepcopy(reservation)
    sealed["mode"] = "content_sealed_fact_reservations"
    sealed["seal_scope"] = (
        "exact reserved rows and constructed endpoints; launch needs final freeze"
    )
    return sealed, payloads, population, identities


def validate_outputs(cfg):
    receipt = Path(cfg["receipt_output"]).resolve()
    resource = Path(cfg["resource_output"]).resolve()
    core.require(
        receipt.is_relative_to(ROOT / "docs/tasks")
        and resource.is_relative_to(ASSETS / "runs/pc_cap/R1"),
        "receipt in docs/tasks; data resources in assets/runs/pc_cap/R1 required",
    )
    core.require(
        not receipt.exists() and not resource.exists(), "outputs must be new; no overwrite/resume"
    )
    return receipt, resource


def new_json(path, value):
    path = Path(path)
    with path.open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        f.write("\n")
    return ref(path)


def check_matrix_layout(matrix):
    from pccap.revision_v1.stage4_adapters import CORE_CONDITIONS

    axes = matrix["axes"]
    core.require(
        matrix.get("name") == "run_matrix_v5_1"
        and axes["datasets"] == list(core.DATASETS)
        and axes["realizations"] == [0, 1, 2]
        and axes["orders"] == [100, 101, 102, 103, 104]
        and axes["conditions"] == list(CORE_CONDITIONS),
        "registered v5.1 matrix axes required",
    )
    expected = {
        (condition, ds, r, o)
        for condition in CORE_CONDITIONS
        for ds in core.DATASETS
        for r in range(3)
        for o in range(100, 105)
    }
    observed = [tuple(cell[k] for k in COORDS) for cell in matrix["cells"]]
    core.require(
        len(observed) == len(expected)
        and set(observed) == expected
        and all(c["checkpoints"] == [100, 300, 1000] for c in matrix["cells"]),
        "complete 360-cell population/cadence required",
    )
    extension = matrix["extension"]["cells"]
    expected_extension = {
        ("R1_learned_ff_v2", ds, r, o)
        for ds in core.DATASETS
        for r in range(3)
        for o in range(100, 105)
    }
    core.require(
        len(extension) == 45
        and {tuple(c[k] for k in COORDS) for c in extension} == expected_extension
        and all(c["checkpoints"] == [100, 300, 1000] for c in extension),
        "complete declared optional 45-cell extension required",
    )
    core.require(
        matrix["population"]["required_subjects_each_dataset"] == 4050, "matrix role demand changed"
    )


def prepare(spec, stage, *, evaluate_clearance=True):
    blockers = []
    report = {
        "task": "R1-D9" + {"clearance": "a", "draw": "b", "seal": "c"}[stage],
        "stage": stage,
        "dry_run": True,
        "blocked": blockers,
        "rng_used": False,
        "draws_emitted": 0,
        "seals_emitted": 0,
        "launch_authorized": False,
    }
    state = {}
    try:
        register = read_metadata(spec["register"])
        verify_register(register)
        core.require(register["schema_version"] == 6, "register v6 required")
        state["register"] = register
        report["nominal_subjects"] = {
            d: register["counts"][d]["candidate_subjects"] for d in core.DATASETS
        }
        matrix = read_metadata(spec["matrix"])
        check_matrix_layout(matrix)
        read_metadata(spec["protocol"], parse=False)
        state["matrix"] = {"binding": spec["matrix"], "document": matrix}
        cfg = spec["d9"][stage]
        validate_outputs(cfg)
        report["would_write"] = [cfg["receipt_output"], cfg["resource_output"]]
        report["request_sha256"] = contract(spec, stage)
    except (OSError, KeyError, TypeError, ValueError, PermissionError) as e:
        blockers.append({"gate": "bound_inputs_or_outputs", "reason": str(e)})
    try:
        state["receipts"] = admitted_receipts(spec, stage)
    except (OSError, KeyError, TypeError, ValueError, PermissionError) as e:
        blockers.append({"gate": "owner_receipts", "reason": str(e)})
    if stage == "clearance" and "register" in state and evaluate_clearance:
        try:
            evidence = read_resource(spec["d9"][stage]["evidence"])
            value = clearance_value(
                spec, state["register"], evidence, source_rows(state["register"])
            )
            state["clearance"] = value
            report["usable_subjects"] = {
                d: row["usable_subjects"] for d, row in value["counts"].items()
            }
        except (OSError, KeyError, TypeError, ValueError, PermissionError) as e:
            blockers.append({"gate": "exhaustive_clearance_review", "reason": str(e)})
    report["ready_for_owner_execution"] = not blockers
    return report, state


def execute(spec, stage):
    report, state = prepare(spec, stage)
    if report["blocked"]:
        raise PermissionError(json.dumps(report["blocked"]))
    cfg = spec["d9"][stage]
    receipt_path, directory = validate_outputs(cfg)
    receipts = state["receipts"]
    receipt = {
        "schema_version": 1,
        "task": report["task"],
        "status": "closed",
        "lead_approved": True,
        "register": spec["register"],
        "producer": ref(__file__),
        "core": ref(ROOT / "scripts/r1_d9_receipt_core.py"),
        "authorization": spec["receipts"][stage + "_authorization"],
        "request_sha256": report["request_sha256"],
        "launch_authorized": False,
        "gpu_seconds": 0,
    }
    if stage == "clearance":
        value = state["clearance"]
        receipt.update(
            policy=core.POLICY,
            cleared_subjects={d: r["usable_subjects"] for d, r in value["counts"].items()},
            **{k: True for k in core.REVIEW_FLAGS},
        )
        artifacts = {"cleared-candidates.json": value}
    elif stage == "draw":
        value = draw_value(spec, receipts)
        artifacts = {"reservations-unsealed.json": value}
        receipt.update(
            master_seed=cfg["master_seed"],
            rng_rule=core.RNG_RULE,
            numpy_version=np.__version__,
            paired_orders=[100, 101, 102, 103, 104],
        )
    else:
        value, payloads, population, identities = seal_values(spec, receipts, state["matrix"])
        artifacts = {
            "reservations-content-sealed.json": value,
            "analysis-population.json": population,
        }
        # Identical payloads shared by conditions are written once, all cells bind that file.
        payload_names = {
            cid: "payload-" + core.content_digest(p) + ".json" for cid, p in payloads.items()
        }
        artifacts.update({payload_names[cid]: p for cid, p in payloads.items()})
    if stage != "clearance":
        receipt.update(
            datasets=list(core.DATASETS),
            realizations=3,
            roles_per_realization=core.ROLES,
            all_roles_disjoint=True,
            composition_dependencies_closed=True,
        )
    # Check every metadata source again immediately before writes. A failed write leaves
    # incomplete new artifacts, never a success receipt or a replacement of old files.
    verify_register(read_metadata(spec["register"]))
    admitted_receipts(spec, stage)
    read_metadata(spec["matrix"])
    read_metadata(spec["protocol"], parse=False)
    directory.mkdir(parents=True, exist_ok=False)
    bindings = {name: new_json(directory / name, v) for name, v in artifacts.items()}
    if stage == "clearance":
        receipt["cleared_candidates"] = bindings["cleared-candidates.json"]
    elif stage == "draw":
        receipt["reservations"] = bindings["reservations-unsealed.json"]
        receipt["clearance_receipt"] = spec["receipts"]["joint_clearance"]
    else:
        inventory = {
            "schema_version": 1,
            "cells": {
                cid: {"payload": bindings[name], **identities[cid]}
                for cid, name in payload_names.items()
            },
        }
        receipt.update(
            reservations=bindings["reservations-content-sealed.json"],
            analysis_population=bindings["analysis-population.json"],
            payload_inventory=new_json(directory / "payload-inventory.json", inventory),
            draw_receipt=spec["receipts"]["draw_receipt"],
        )
    check_receipt(RECEIPT_NAMES[stage], receipt, spec)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    binding = new_json(receipt_path, receipt)
    # Round-trip all written files before returning success to the caller.
    for b in [*bindings.values(), binding]:
        core.require(sha(b["path"]) == b["sha256"], "written artifact identity changed")
    return {"receipt": binding, "stage": stage, "launch_authorized": False}


def main(stage, argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--dry-run", action="store_true")
    choice.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    spec = read_metadata(ref(args.inputs))
    if args.execute:
        result = execute(spec, stage)
    else:
        result, _ = prepare(spec, stage)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 2 if result.get("blocked") else 0
