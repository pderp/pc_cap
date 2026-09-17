"""Dry v7 inventory for DEC-060 option D, retaining context and execution gates."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from scripts import r1_68c_dev_cell as driver
from scripts import r1_77b_sealed_backend as backend
from scripts.r1_d9_receipts import ref, sha
from scripts.r1_d10a_review import ROOT, write_new
from scripts.r1_d10a_review_core import digest
from scripts.r1_d10d_options import build_matrix, layouts


def verify(candidate):
    if candidate["option"] != "D" or candidate["dataset_layouts"] != layouts("D"):
        raise ValueError("DEC-060 option D layout required")
    for name, expected in candidate["bindings_sha256"].items():
        if sha(name) != expected:
            raise ValueError("candidate binding changed: " + name)
    if driver.code_identity() != candidate["installed_driver_code_sha256"]:
        raise ValueError("installed driver identity changed")
    if sha(ROOT / "scripts/r1_68c_dev_cell.py") != backend.DONOR_SHA256:
        raise ValueError("sealed donor reconciliation differs")
    for key in (
        "confirmation_protocol_frozen",
        "draw_authorized",
        "launch_authorized",
        "context_adjudication_admitted",
    ):
        if candidate[key] is not False:
            raise ValueError("dry candidate grants no admission: " + key)
    if [g["gate"] for g in candidate["gate_inventory"]] != [f"U{i:02}" for i in range(1, 19)]:
        raise ValueError("complete gate inventory required")
    if candidate["operative_clearance_evidence"] != candidate["context_review"]["v4"]:
        raise ValueError("unreviewed v5 must not replace operative v4")
    return dict(
        bindings=len(candidate["bindings_sha256"]),
        open_gates=[g["gate"] for g in candidate["remaining_gates"]],
        frozen=False,
        context_review_admitted=False,
    )


def assemble():
    parent_path = ROOT / "manifests/revision_v1/freeze_candidate_v6.json"
    parent = json.loads(parent_path.read_text())
    matrix_path = ROOT / "manifests/revision_v1/run_matrix_v5_2_option_D.json"
    matrix = json.loads(matrix_path.read_text())
    v51 = json.loads((ROOT / "manifests/revision_v1/run_matrix_v5_1.json").read_text())
    expected, _ = build_matrix(v51, "D")
    for key in ("cells", "extension", "dataset_layouts", "multiplicity", "queue", "budget"):
        if matrix[key] != expected[key]:
            raise ValueError("matrix differs from exact option D producer: " + key)
    bindings = {}

    def bind(path, expected=None):
        p = Path(path).resolve()
        if (
            not p.is_relative_to(ROOT.parent)
            or "confirm" in p.parts
            or "stage4_sealed_payloads" in p.parts
        ):
            raise PermissionError("unsealed local evidence/code only")
        binding = ref(p)
        if expected is not None and binding["sha256"] != expected:
            raise ValueError("evidence identity changed: " + str(p))
        if str(p) in bindings and bindings[str(p)] != binding["sha256"]:
            raise ValueError("source changed during assembly")
        bindings[str(p)] = binding["sha256"]
        return binding

    for field in (
        "historical_matrix",
        "protocol",
        "calibration",
        "primary_condition",
        "producer",
        "preteacher_evidence",
    ):
        bind(matrix[field]["path"], matrix[field]["sha256"])
    context_path = ROOT / "logs/r1_round23/r1-d10e-adjudication.json"
    context = json.loads(context_path.read_text())
    near_path = ROOT / "logs/r1_round23/r1-d10f-feasibility.json"
    near = json.loads(near_path.read_text())
    for report in (context, near):
        for b in report["evidence_bindings"]:
            bind(b["path"], b["sha256"])
    for b in (context["parent_v4"], context["candidate_v5"], context["worksheet"], near["detail"]):
        bind(b["path"], b["sha256"])
    # Follow the evidence's declared immutable input bindings; no source scan,
    # model loading or opaque sealed payload access.
    v4 = json.loads(Path(context["parent_v4"]["path"]).read_text())
    for b in v4["evidence_bindings"]:
        bind(b["path"], b["sha256"])
    sources = {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / "src/pccap").rglob("*.py"))}
    script_sources = {
        str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / "scripts").glob("*.py"))
    }
    for path, h in {**sources, **script_sources}.items():
        bind(ROOT / path, h)
    d9_path = ROOT / "docs/tasks/R1-D10d-option-D/d9-inputs.json"
    d9 = json.loads(d9_path.read_text())
    templates = {}
    for name, b in d9["receipts"].items():
        if b.get("path"):
            templates[name] = bind(b["path"], b["sha256"])
    for name in ("protocol-admission", "rng-admission", "endpoint-construction"):
        templates[name] = bind(ROOT / f"docs/tasks/R1-D9-{name}-template-v2.json")
    gates = copy.deepcopy(parent["gate_inventory"])
    closures = {
        "U01": "DEC-060 option D selected; adopt reviewed v5.2 matrix/protocol; extension remains separately admitted.",
        "U06": "Orchestrator reviews R1-D10e rule/overlay and current exposure supplement; teacher + joint role clearance for 4050/4050/1950; versioned D9 layout/RNG receipts.",
        "U07": "Admit variable-layout receipt/backend validation; authorized actual draw, endpoint construction and seals with independent expected populations.",
        "U08": "Bind 100/300/1000 for zsRE/CF and 100/300 for MQuAKE; final challenge/full-validation cadence and cost inventory required; calibration v3 bound.",
        "U09": "Admit NM-template-v1 semantics; actual postdraw compatible pairs and missing slots; revision/alias/version observers remain audited.",
        "U11": "R1-68e hook and R1-77c donor landed; sealed 300-edit cadence still refused by current backend and installed payload validator; coordinated versioned repair and real-base receipts required.",
        "U12": "Retain all 63 intervals; unavailable seven MQuAKE 1000 contrasts; versioned analysis layout adapter and final independent populations required.",
        "U14": "MQuAKE 1000/1000-minus-100 benchmarks unavailable under D; preserve zsRE/CF thresholds; admit endpoints/ceilings and complete reporting.",
        "U16": "Price the option-D 360 core/45 extension cells with actual near/revision/full-validation costs; September20 admission; no ceilings inferred from reduced cadence.",
        "U17": "Close context/endpoint/heterogeneous-layout and other gates; bind final environment, recipes, backend, code and receipts after any coordinated edits.",
    }
    for gate in gates:
        if gate["gate"] in closures:
            gate.update(status="open", closure=closures[gate["gate"]])
    decision = next(
        line
        for line in (ROOT / "docs/decisions.md").read_text().splitlines()
        if line.startswith("| DEC-060 |")
    )
    if "option D" not in decision:
        raise ValueError("recorded lead option D required")
    result = dict(
        schema_version=7,
        name="freeze_candidate_v7",
        task="R1-63f",
        option="D",
        status="dry_candidate_selected_D_context_review_pending_not_frozen",
        producer=bind(__file__),
        historical_candidate=bind(parent_path),
        matrix=bind(matrix_path),
        protocol=matrix["protocol"],
        calibration=matrix["calibration"],
        primary_condition=matrix["primary_condition"],
        register=bind(ROOT / "manifests/revision_v1/exclusions_frozen_v6.json"),
        dataset_layouts=matrix["dataset_layouts"],
        core_cells=360,
        extension_cells=45,
        decisions={
            **matrix["accepted_decisions"],
            "DEC-060": {"row": decision, "sha256": hashlib.sha256(decision.encode()).hexdigest()},
        },
        operative_clearance_evidence=context["parent_v4"],
        context_review={
            "report": bind(context_path),
            "v4": context["parent_v4"],
            "candidate_v5": context["candidate_v5"],
            "orchestrator_review_receipt": None,
            "proposed_counts": context["counts"],
            "promotion": "new evidence resource after review; operative v4 and source dispositions unchanged",
        },
        near_family_review=bind(near_path),
        d9_inputs=bind(d9_path),
        d9_templates=templates,
        installed_driver=bind(ROOT / "scripts/r1_68c_dev_cell.py"),
        installed_driver_code_sha256=driver.code_identity(),
        sealed_backend=bind(ROOT / "scripts/r1_77b_sealed_backend.py"),
        sealed_backend_donor_sha256=backend.DONOR_SHA256,
        src_pccap_files=sources,
        src_pccap_tree_sha256=digest(sources),
        script_sources=script_sources,
        gate_inventory=gates,
        remaining_gates=[g for g in gates if g["status"] == "open"],
        accepted_primary_intervals=63,
        context_adjudication_admitted=False,
        confirmation_protocol_frozen=False,
        draw_authorized=False,
        launch_authorized=False,
        experiment_stop="2026-10-09",
        bindings_sha256=bindings,
        gpu_seconds=0,
        sealed_payloads_opened=0,
    )
    verify(result)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    if not args.output.resolve().is_relative_to(ROOT / "manifests/revision_v1"):
        ap.error("candidate manifest belongs in repository revision_v1 manifests")
    value = assemble()
    write_new(args.output, value)
    print(json.dumps(verify(value), indent=2))


if __name__ == "__main__":
    main()
