"""Stage a complete publication proposal; never publish, sign, or open cell payloads.

The operator's exact freeze signature authorizes copying these reviewed bytes to
their final paths. Until then the fixed final freeze path remains absent.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from unittest.mock import patch

from scripts import ht8_fidelity_watch as watch
from scripts import r1_49m_fidelity_policy as fidelity_policy
from scripts import r1_58c_draw_seal_preflight as preflight
from scripts import r1_63l_full_validation_contract as full_contract
from scripts import r1_68c_dev_cell as driver
from scripts import r1_77_queue as queue
from scripts import r1_77b_sealed_backend as backend
from scripts import r1_d9_receipts as d9
from scripts.r1_49m_normative_closure import closure
from scripts.r1_77f_scheduler import CEILING_DEFINITION
from scripts.r1_d10a_review import ROOT, write_new

from pccap.revision_v1 import stage4_cell as core

RECEIPTS = tuple(n for n in preflight.REQUIRED["freeze"] if n != "freeze_authorization")
RUNTIME_KEYS = (
    "adapter_identity",
    "tokenizer_sha256",
    "construction",
    "integrity_profile",
    "integrity_batch_edits",
    "drift_batch_size",
    "drift_implementation",
    "integrity_driver_bindings",
    "code_sha256",
    "full_validation",
    "full_validation_implementation",
)


def inspect(spec):
    """Unsigned real inputs return reasons without opening any resource."""
    blocked, receipts = [], {}
    for name in RECEIPTS:
        try:
            r = d9.read_metadata(spec["receipts"][name])
            preflight.check_receipt(name, r, spec)
            receipts[name] = r
        except (OSError, KeyError, TypeError, ValueError) as error:
            blocked.append(dict(input=name, reason=str(error)))
    matrix = d9.read_metadata(spec["matrix"])
    d9.read_metadata(spec["protocol"], parse=False)
    d9.check_matrix_layout(matrix)
    if not blocked:
        draw, ep, seal = (
            receipts[n] for n in ("draw_receipt", "endpoint_construction", "seal_receipt")
        )
        if (
            seal["draw_receipt"] != spec["receipts"]["draw_receipt"]
            or ep["draw_receipt"] != spec["receipts"]["draw_receipt"]
            or ep["reservations"] != draw["reservations"]
        ):
            raise ValueError("draw/endpoint/seal receipt chain mismatch")
        auth = d9.read_metadata(seal["authorization"])
        if (
            auth.get("operation") != "seal"
            or auth.get("request_sha256") != seal["request_sha256"]
            or auth.get("lead_approved") is not True
            or auth.get("status") != "closed"
        ):
            raise ValueError("seal authorization mismatch")
    return dict(
        blocked=blocked,
        receipts=receipts,
        matrix=matrix,
        payloads_opened=0,
        published=False,
        signed=False,
    )


def template_catalog(output=None):
    """Refresh runtime metadata only; preserve source construction/adapter identity.

    A development code digest and a sealed code digest hash different inventories.
    No historical execution is relabelled by this explicit runtime-only conversion.
    """
    from uuid import uuid4

    output = Path(output) if output else ROOT / "docs/tasks/R1-63j-runtime" / uuid4().hex
    sources = {}
    for directory in ("R1-post68f-active/R1-64e", "R1-post68f-active/R1-73d-post68f", "R1-64g"):
        for p in sorted((ROOT / "docs/tasks" / directory).glob("*.recipe.json")):
            m = d9.read_metadata(d9.ref(p))
            if m["code_sha256"] != driver.code_identity():
                raise ValueError("current development source changed")
            driver.profile_config(m)
            sources[m["cell"]["condition"] + ":" + m["cell"]["dataset"]] = p
    # This measured primary CF recipe predates the integrity-driver refresh.
    # Preserve its scientific identity; declare the same current incremental
    # execution policy as the other primary recipes, with original bytes bound.
    sources["R1_learned_ff:counterfact"] = ROOT / "docs/tasks/R1-64-counterfact-v5.recipe.json"
    result = {}
    for key, path in sorted(sources.items()):
        old = d9.read_metadata(d9.ref(path))
        value = {k: copy.deepcopy(old[k]) for k in RUNTIME_KEYS if k in old}
        value.update(
            schema_version=1,
            mode="stage4_runtime_template",
            cell=old["cell"],
            code_sha256=core.code_identity(ROOT),
            integrity_driver_bindings=driver.driver_bindings(),
            source_recipe=d9.ref(path),
            producer=d9.ref(__file__),
            note="runtime metadata conversion only; no historical result reused as sealed execution",
            full_validation=full_contract.production_contract(),
            full_validation_implementation=full_contract.ref(full_contract.__file__),
        )
        if key == "R1_learned_ff:counterfact":
            value.update(
                integrity_profile="incremental", integrity_batch_edits=16, drift_batch_size=16
            )
        driver.profile_config(value)
        result[key] = write_new(output / f"{key.replace(':', '-')}.runtime.json", value)
    write_new(output / "catalog.json", result)
    return result


def virtual_validate(bundle, documents, *, code_root=ROOT):
    """Use the real queue/backend against an in-memory final-path overlay.

    Only unpublished metadata reads are redirected. Every normal source hash,
    cadence, closed gate, recipe contract and full matrix check still executes.
    No model or payload loader is called. Call in a dedicated CPU process.
    """
    read_binding, metadata, qread, qsha = core.read_binding, backend.metadata, queue.read, queue.sha
    bsha, binspect = backend.sha, backend.inspect_manifest

    def value(b):
        p = str(Path(b["path"]).resolve())
        if p not in documents:
            return read_binding(b)
        v, h = documents[p]
        if h != b["sha256"]:
            raise ValueError("staged metadata hash mismatch")
        return copy.deepcopy(v)

    def meta(b):
        return value(b) if str(Path(b["path"]).resolve()) in documents else metadata(b)

    def file_sha(p):
        key = str(Path(p).resolve())
        return documents[key][1] if key in documents else qsha(p)

    def read(p):
        key = str(Path(p).resolve())
        return copy.deepcopy(documents[key][0]) if key in documents else qread(p)

    with (
        patch.object(core, "read_binding", value),
        patch.object(backend, "metadata", meta),
        patch.object(backend, "read_binding", value),
        patch.object(
            backend,
            "sha",
            lambda p: (
                documents[str(Path(p).resolve())][1]
                if str(Path(p).resolve()) in documents
                else bsha(p)
            ),
        ),
        patch.object(backend, "inspect_manifest", lambda p, h: binspect(p, h, code_root=code_root)),
        patch.object(queue, "read", read),
        patch.object(queue, "sha", file_sha),
    ):
        queue.verify_sealed_matrix(value(bundle["matrix"]), value(bundle["bindings"]))
    return dict(
        queue_backend_validation="passed",
        cells=len(value(bundle["bindings"])["recipes"]),
        payloads_opened=0,
        model_constructed=False,
        published=False,
    )


def assemble(spec, templates, staging, *, final_root=ROOT, code_root=ROOT, normative=None):
    state = inspect(spec)
    if state["blocked"]:
        raise PermissionError(json.dumps(state["blocked"]))
    staging, final_root = Path(staging).resolve(), Path(final_root).resolve()
    if not staging.is_relative_to(ROOT / "docs/tasks") or staging.exists():
        raise ValueError("new staging directory under docs/tasks required")
    if final_root != ROOT and not final_root.is_relative_to(ROOT / "logs/r1_round29"):
        raise ValueError("nonproduction destination must be an isolated round29 fixture")
    receipts, declaration = state["receipts"], state["matrix"]
    admitted = receipts["protocol_admission"]
    required = d9.matrix_cells(dict(document=declaration, binding=spec["matrix"]), admitted)
    ids = {queue.analysis.coordinate_id(c) for c in required}
    seal = receipts["seal_receipt"]
    if receipts["chain_i_cell_ceilings"].get("cost_schema_version") != 2:
        raise ValueError("typed cost evidence schema v2 required")
    inventory = d9.read_resource(seal["payload_inventory"])["cells"]
    population = d9.read_resource(seal["analysis_population"])
    if set(inventory) != ids or set(population["cells"]) != ids:
        raise ValueError("sealed inventory/population must equal whole admitted matrix")
    fidelity_policy.validate(declaration.get("cap_fidelity_policy"))
    fidelity_policy.validate_matrix(declaration, queue.analysis.all_cells(declaration))
    validation = full_contract.validate(spec.get("full_validation"))
    if (
        declaration.get("full_validation") != validation
        or population.get("full_validation") != validation
    ):
        raise ValueError("DEC-063 matrix/independent population contract mismatch")
    for pop in population["cells"].values():
        if pop.get("full_validation") != validation:
            raise ValueError("DEC-063 missing from a sealed cell population")
    # Population is an independent metadata inventory; cell payloads and reservations stay opaque.
    costs = {
        c["condition"] + ":" + c["dataset"]: c for c in receipts["chain_i_cell_ceilings"]["cells"]
    }
    if len(costs) != len(receipts["chain_i_cell_ceilings"]["cells"]):
        raise ValueError("duplicate cost coordinates")
    norm = closure() if normative is None else normative
    if final_root == ROOT and norm != closure():
        raise ValueError("production normative closure differs")
    metadata_bindings = {
        str(code_root / "requirements.lock"): d9.sha(code_root / "requirements.lock")
    }
    metadata_bindings.update(norm["bindings_sha256"])
    watch_contract = watch.binding()
    for b in [*declaration["analysis_implementation"].values(), *watch_contract["implementations"]]:
        d9.read_metadata(b, parse=False)
        metadata_bindings[b["path"]] = b["sha256"]
    for name in ("r1_77_queue", "r1_77f_scheduler"):
        b = d9.ref(ROOT / f"scripts/{name}.py")
        metadata_bindings[b["path"]] = b["sha256"]
    implementation = full_contract.ref(full_contract.__file__)
    metadata_bindings[implementation["path"]] = implementation["sha256"]
    for b in [spec["matrix"], spec["protocol"], *spec["receipts"].values()]:
        if b.get("path"):
            d9.read_metadata(b, parse=False)
            metadata_bindings[b["path"]] = b["sha256"]
    matrix_calibration = declaration.get("calibration")
    if matrix_calibration:
        calibration = d9.read_metadata(matrix_calibration)
        metadata_bindings[matrix_calibration["path"]] = matrix_calibration["sha256"]
    else:
        raise ValueError("matrix must bind calibration v3")
    primary = d9.read_metadata(declaration["primary_condition"])
    metadata_bindings[declaration["primary_condition"]["path"]] = declaration["primary_condition"][
        "sha256"
    ]
    for p in sorted((code_root / "src/pccap").rglob("*.py")):
        metadata_bindings[str(p)] = d9.sha(p)
    for p in (Path(__file__), Path(backend.__file__), Path(driver.__file__)):
        metadata_bindings[str(p)] = d9.sha(p)

    artifacts, documents = [], {}
    staging.mkdir(parents=True)

    def stage(name, destination, document):
        destination = Path(destination).resolve()
        if destination.exists() or not any(
            destination.is_relative_to(final_root / d)
            for d in ("docs/tasks", "manifests/revision_v1")
        ):
            raise ValueError("destination must be new final metadata path")
        source = write_new(staging / name, document)
        artifacts.append(dict(source=source, destination=str(destination)))
        documents[str(destination)] = (document, source["sha256"])
        return dict(path=str(destination), sha256=source["sha256"])

    protocol = dict(
        schema_version=2,
        mode="stage4_final_protocol",
        lead_approved=True,
        open_gates=[],
        population_decision="DEC-060-option-D",
        dataset_layouts=spec["dataset_layouts"],
        layout_sha256=spec["layout_sha256"],
        matrix=spec["matrix"],
        extension_admitted=admitted["extension_admitted"],
        max_new=32,
        locality_score="bounded_text_equality_DEC053",
        experiment_deadline="2026-10-09",
        protocol_text=spec["protocol"],
        normative_closure=norm,
        near_miss_family_contract=spec["near_miss_family_contract"],
        near_allocation=admitted.get("near_allocation"),
        near_allocation_decision=admitted.get("near_allocation_decision"),
        protocol_admission=spec["receipts"]["protocol_admission"],
        effective_only_after_exact_signed_publication=True,
        cap_fidelity_policy=declaration["cap_fidelity_policy"],
        fidelity_watch=watch_contract,
        full_validation=validation,
        full_validation_implementation=implementation,
    )
    protocol_binding = stage(
        "protocol.json", final_root / "manifests/revision_v1/stage4_final_protocol.json", protocol
    )
    recipes = {}
    runtime_cache = {}
    cells = [c for c in queue.analysis.all_cells(declaration) if c["cell_id"] in ids]
    for cell in cells:
        key = cell["condition"] + ":" + cell["dataset"]
        if key not in runtime_cache:
            b = templates[key]
            m = d9.read_metadata(b)
            if (
                m["cell"]["condition"] + ":" + m["cell"]["dataset"] != key
                or m["code_sha256"] != core.code_identity(code_root)
                or m["adapter_identity"]["condition"] != cell["condition"]
            ):
                raise ValueError("runtime template coordinate/code identity mismatch")
            driver.profile_config(m, code_root)
            if (
                m.get("full_validation") != validation
                or m.get("full_validation_implementation") != implementation
            ):
                raise ValueError("runtime template lacks current DEC-063 contract/implementation")
            bp = calibration["calibration"]["BP"]
            expected_cal = dict(bank_scales=bp["b_m"], radii=bp["radii"][cell["dataset"]])
            if m["construction"]["calibration"] != expected_cal:
                raise ValueError("runtime template calibration differs from admitted v3")
            if (
                cell["condition"] == "R1_learned_ff"
                and m["construction"]["weights"] != primary["weights"]
            ):
                raise ValueError("runtime primary weights differ from selected v5")
            runtime_cache[key] = {k: copy.deepcopy(m[k]) for k in RUNTIME_KEYS if k in m}
            metadata_bindings[b["path"]] = b["sha256"]
        cid = cell["cell_id"]
        inv = inventory[cid]
        if inv["ordered_item_ids_sha256"] != core.digest(population["cells"][cid]["item_ids"]):
            raise ValueError("sealed order/independent population mismatch")
        m = copy.deepcopy(runtime_cache[key])
        m.update(
            schema_version=1,
            mode=backend.MODE,
            cell={k: cell[k] for k in d9.COORDS},
            backend=backend.backend_binding(),
            population_contract_version=2,
            matrix=spec["matrix"],
            checkpoints=cell["checkpoints"],
            max_new=32,
            protocol=protocol_binding,
            reservations=seal["reservations"],
            population=seal["analysis_population"],
            payload=inv["payload"],
            calibration=matrix_calibration,
            runtime_template=templates[key],
            ceilings=copy.deepcopy(costs[key]),
            admission=dict(
                lead_approved=True,
                protocol_frozen=True,
                condition_admitted=True,
                launch_authorized=True,
                endpoint_bundle_sha256=inv["endpoint_bundle_sha256"],
                ordered_item_ids_sha256=inv["ordered_item_ids_sha256"],
            ),
            publication_condition="effective only after operator's exact signed freeze publication",
        )
        recipes[cid] = m
    frozen = dict(
        schema_version=1,
        mode="stage4_final_freeze",
        lead_approved=True,
        launch_authorized=True,
        open_gates=[],
        closed_gates=receipts["closed_gate_receipts"]["gates"],
        protocol=protocol_binding,
        reservations=seal["reservations"],
        population=seal["analysis_population"],
        protocol_admission=spec["receipts"]["protocol_admission"],
        seal_receipt=spec["receipts"]["seal_receipt"],
        cost_admission=spec["receipts"]["chain_i_cell_ceilings"],
        calibration=matrix_calibration,
        backend=backend.backend_binding(),
        code_sha256=core.code_identity(code_root),
        integrity_driver_bindings=driver.driver_bindings(code_root),
        cap_fidelity_policy=declaration["cap_fidelity_policy"],
        fidelity_watch=watch_contract,
        bindings_sha256=metadata_bindings,
        recipe_contracts={cid: backend.contract_digest(m) for cid, m in recipes.items()},
        publication_condition="proposal only until exact signed operator freeze publication",
        full_validation=validation,
        full_validation_implementation=implementation,
    )
    freeze = stage("freeze-proposal.json", final_root / backend.FROZEN_RELATIVE, frozen)
    bindings = {}
    for cid, m in recipes.items():
        m["freeze"] = freeze
        bindings[cid] = dict(
            stage(
                f"recipes/{cid}.json",
                final_root / f"docs/tasks/R1-final-cell-recipes/{cid}.json",
                m,
            ),
            backend=backend.backend_binding(),
        )
    final = copy.deepcopy(declaration)
    final.update(
        scope="confirmatory",
        queue_ceiling_contract=CEILING_DEFINITION,
        source_matrix=spec["matrix"],
        fidelity_watch=watch_contract,
        freeze=freeze,
        shared_process_hours=receipts["chain_i_cell_ceilings"]["shared_process_hours"],
        cost_admission=spec["receipts"]["chain_i_cell_ceilings"],
        endpoint_contract_version=1,
        full_validation=validation,
    )
    for cell in cells:
        cid = cell["cell_id"]
        m, b = recipes[cid], bindings[cid]
        cell.update(
            admitted=True,
            launch_allowed=True,
            recipe_template=None,
            manifest_sha256=b["sha256"],
            payload_sha256=m["payload"]["sha256"],
            population=population["cells"][cid],
            ceilings=m["ceilings"],
            adapter_identity=m["adapter_identity"],
            code_sha256=m["code_sha256"],
            result_dir=str(backend.OUTPUT_ROOT / core.cell_name(m, b["sha256"])),
            full_validation=validation,
        )
    final["cells"] = [c for c in cells if c["block_number"] != 6]
    final["extension"]["cells"] = [c for c in cells if c["block_number"] == 6]
    final["extension"]["allocation_approved"] = admitted["extension_admitted"]
    mb = stage("matrix.json", final_root / "manifests/revision_v1/run_matrix_final.json", final)
    rb = stage(
        "queue-bindings.json",
        final_root / "docs/tasks/R1-final-queue-bindings.json",
        dict(
            recipes=bindings,
            matrix=mb,
            freeze=freeze,
            cost_admission=spec["receipts"]["chain_i_cell_ceilings"],
        ),
    )
    bundle = dict(
        schema_version=1,
        task="R1-63j",
        artifacts=artifacts,
        matrix=mb,
        bindings=rb,
        freeze=freeze,
        published=False,
        publication_requires_exact_lead_signature=True,
        source_inputs_sha256=core.content_digest(spec),
        templates=templates,
    )
    proof = virtual_validate(bundle, documents, code_root=code_root)
    binding = write_new(staging / "publication-bundle.json", bundle)
    return dict(bundle=binding, verification=proof, staged_files=len(artifacts), published=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inputs", type=Path, default=ROOT / "docs/tasks/R1-D9-inputs-v7.json")
    ap.add_argument("--staging", type=Path)
    ap.add_argument("--templates", type=Path)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    spec = d9.read_metadata(d9.ref(args.inputs))
    report = inspect(spec)
    report.pop("receipts")
    report.pop("matrix")
    if args.staging:
        if not args.templates:
            ap.error("--templates is required for staging the reviewed runtime catalog")
        report = assemble(spec, d9.read_metadata(d9.ref(args.templates)), args.staging)
    write_new(args.report, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
