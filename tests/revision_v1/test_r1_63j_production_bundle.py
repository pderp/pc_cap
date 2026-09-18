"""Full inventory assembly over actual synthetic D9 receipts, with real metadata guards."""

import copy
import json
from pathlib import Path
from uuid import uuid4

import pytest
from scripts import r1_63j_production_bundle as bundle
from scripts import r1_d9_receipts as d9
from scripts.r1_49j_normative_closure import closure
from scripts.r1_d10a_review import ROOT, write_new

from tests.revision_v1.test_r1_58h_cost_receipt import complete


@pytest.fixture(scope="module")
def assembly_inputs():
    root = ROOT / "docs/tasks/R1-63j-rehearsal" / uuid4().hex
    root.mkdir(parents=True)
    # Immutable prior rehearsal: actual public D9 clearance/draw/constructor/seal.
    summary = ROOT / "logs/r1_round24/rehearsal/6b4dd4bdd6f24ae3bc658be282ede176/summary.json"
    if not summary.exists():
        summary = sorted((ROOT / "logs/r1_round24/rehearsal").glob("*/summary.json"))[0]
    info = json.loads(summary.read_text())
    seal = d9.read_metadata(info["receipts"]["seal_receipt"])
    spec = {
        k: seal[k]
        for k in (
            "register",
            "matrix",
            "protocol",
            "dataset_layouts",
            "layout_sha256",
            "near_miss_family_contract",
        )
    }
    spec.update(schema_version=3, receipts=copy.deepcopy(info["receipts"]))
    common = {k: v for k, v in spec.items() if k not in ("schema_version", "receipts")}
    common.update(contract_version=2, status="closed", lead_approved=True, synthetic=True)
    _, cost = complete(root)
    cost.update(common)
    spec["receipts"]["chain_i_cell_ceilings"] = write_new(root / "cost.json", cost)
    spec["receipts"]["september20_admission"] = write_new(
        root / "schedule.json",
        dict(
            common,
            admission_date="2026-09-20",
            experimental_completion_date="2026-10-09",
            full_scope_retained=True,
        ),
    )
    gates = {g: write_new(root / f"{g}.json", dict(common, gate=g)) for g in bundle.backend.GATES}
    spec["receipts"]["closed_gate_receipts"] = write_new(
        root / "gates.json", dict(common, gates=gates)
    )
    templates = bundle.template_catalog()
    write_new(root / "inputs.json", spec)
    write_new(root / "templates.json", templates)
    return root, spec, templates


def test_real_unsigned_inspection_never_opens_resources(monkeypatch):
    spec = d9.read_metadata(d9.ref(ROOT / "docs/tasks/R1-D9-inputs-v7.json"))
    monkeypatch.setattr(
        d9, "read_resource", lambda _: pytest.fail("resource read before admission")
    )
    result = bundle.inspect(spec)
    assert result["blocked"] and result["payloads_opened"] == 0


def test_whole_synthetic_package_passes_actual_queue_and_backend(assembly_inputs):
    root, spec, templates = assembly_inputs
    before = (ROOT / bundle.backend.FROZEN_RELATIVE).exists()
    result = bundle.assemble(spec, templates, root / "staged", normative=closure())
    assert result["verification"]["cells"] == 360
    assert not result["published"] and not result["verification"]["model_constructed"]
    assert (ROOT / bundle.backend.FROZEN_RELATIVE).exists() == before
    doc = d9.read_metadata(result["bundle"])
    from scripts.r1_58g_operator import publication_preview

    publication_preview(result["bundle"], spec)
    assert len(doc["artifacts"]) == 364
    assert all(not Path(a["destination"]).exists() for a in doc["artifacts"])
    write_new(
        ROOT / f"logs/r1_round29/assembler-rehearsal-{root.name}.json",
        dict(result, synthetic=True, source=d9.ref(root / "inputs.json")),
    )


@pytest.mark.parametrize(
    "fault",
    [
        "seal_chain",
        "missing_population",
        "wrong_runtime",
        "cost_unsigned",
        "gate",
        "order",
        "extension",
    ],
)
def test_invalid_inputs_refused(assembly_inputs, fault):
    root, original, templates = assembly_inputs
    spec, templates = copy.deepcopy(original), copy.deepcopy(templates)
    folder = root / fault
    folder.mkdir()

    def change(name, mutate):
        v = d9.read_metadata(spec["receipts"][name])
        mutate(v)
        spec["receipts"][name] = write_new(folder / f"{name}.json", v)

    if fault == "seal_chain":
        change(
            "seal_receipt", lambda v: v.update(draw_receipt={"path": "wrong", "sha256": "0" * 64})
        )
    if fault == "cost_unsigned":
        change("chain_i_cell_ceilings", lambda v: v.update(lead_approved=False))
    if fault == "gate":
        change("closed_gate_receipts", lambda v: v["gates"].pop("U03"))
    if fault == "extension":
        change("protocol_admission", lambda v: v.update(extension_admitted=True))
    if fault == "wrong_runtime":
        templates["R1_learned_ff:zsre"] = templates["v0_stable:zsre"]
    if fault in ("missing_population", "order"):
        sealed = d9.read_metadata(spec["receipts"]["seal_receipt"])
        pop = d9.read_resource(sealed["analysis_population"])
        key = next(iter(pop["cells"]))
        if fault == "missing_population":
            del pop["cells"][key]
        else:
            pop["cells"][key]["item_ids"].reverse()
        resource = ROOT.parent / "assets/test_scratch/r1_round29" / root.name / f"{fault}.json"
        resource.parent.mkdir(parents=True, exist_ok=True)
        sealed["analysis_population"] = d9.new_json(resource, pop)
        spec["receipts"]["seal_receipt"] = write_new(folder / "seal.json", sealed)
    with pytest.raises((ValueError, PermissionError)):
        bundle.assemble(spec, templates, folder / "staged")


def test_tampered_receipt_bytes_refused(assembly_inputs):
    root, original, templates = assembly_inputs
    spec = copy.deepcopy(original)
    b = write_new(root / "tampered.json", d9.read_metadata(spec["receipts"]["seal_receipt"]))
    spec["receipts"]["seal_receipt"] = b
    Path(b["path"]).write_text("{}")
    with pytest.raises(PermissionError, match="identity mismatch"):
        bundle.assemble(spec, templates, root / "tampered-stage")
