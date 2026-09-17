"""Generate exact idle-boundary cadence patches without editing installed files."""

from __future__ import annotations

import difflib
import hashlib
import json

from scripts.r1_d9_receipts import ref
from scripts.r1_d10a_review import ROOT

HELPER = '''def registered_checkpoints(manifest, protocol=None):
    """Require the frozen protocol and exact DEC-060 dataset/matrix contract."""
    version = manifest.get("population_contract_version")
    if version is None:
        if protocol is not None and protocol.get("schema_version") != 1:
            raise ValueError("versioned protocol requires versioned recipe")
        return list(CHECKPOINTS)
    if type(version) is not int or version != 2:
        raise ValueError("unsupported population contract version")
    protocol = read_binding(manifest["protocol"]) if protocol is None else protocol
    if (protocol.get("schema_version") != 2 or protocol.get("mode") != "stage4_final_protocol"
        or protocol.get("lead_approved") is not True or protocol.get("open_gates") != []
        or protocol.get("population_decision") != "DEC-060-option-D"
        or protocol.get("max_new") != 32
        or protocol.get("locality_score") != "bounded_text_equality_DEC053"
        or protocol.get("experiment_deadline") != "2026-10-09"):
        raise ValueError("admitted DEC-060 final protocol required")
    expected = {}
    for ds in ("zsre", "counterfact", "mquake"):
        roles = dict(edits=300 if ds == "mquake" else 1000, outside=100,
                     near_miss_support=100, near_miss_neighbour=100, revision=50)
        expected[ds] = dict(realizations=[0, 1, 2], roles_per_realization=roles,
                            checkpoints=[100, 300] if ds == "mquake" else [100, 300, 1000],
                            demand_per_realization=sum(roles.values()),
                            demand_subjects=3*sum(roles.values()),
                            demand_by_role={r: 3*n for r, n in roles.items()})
    if content_digest(protocol.get("dataset_layouts")) != content_digest(expected) or protocol.get("layout_sha256") != content_digest(expected):
        raise ValueError("protocol role demand/cadence differs from DEC-060")
    if manifest.get("matrix") != protocol.get("matrix"):
        raise ValueError("recipe/protocol matrix binding differs")
    matrix = read_binding(protocol["matrix"])
    if (matrix.get("name") != "run_matrix_v5_2_option_D" or matrix.get("option") != "D"
        or content_digest(matrix.get("dataset_layouts")) != content_digest(expected)
        or matrix.get("layout_sha256") != content_digest(expected)):
        raise ValueError("bound option-D matrix required")
    cells = list(matrix["cells"])
    if protocol.get("extension_admitted") is True:
        cells += matrix.get("extension", {}).get("cells", [])
    elif protocol.get("extension_admitted") is not False:
        raise ValueError("explicit extension admission required")
    cell = manifest["cell"]
    matched = [c for c in cells if all(str(c[k]) == str(cell[k]) for k in ("condition", "dataset", "realization", "order"))]
    if len(matched) != 1 or cell["dataset"] not in expected:
        raise ValueError("recipe cell absent/duplicated in admitted matrix")
    checkpoints = expected[cell["dataset"]]["checkpoints"]
    if matched[0]["checkpoints"] != checkpoints or manifest["checkpoints"] != checkpoints:
        raise ValueError("cell/recipe/protocol dataset cadence differs")
    return checkpoints


'''


def proposed_sources():
    core_path = ROOT / "src/pccap/revision_v1/stage4_cell.py"
    backend_path = ROOT / "scripts/r1_77b_sealed_backend.py"
    original = {
        str(core_path.relative_to(ROOT)): core_path.read_text(),
        str(backend_path.relative_to(ROOT)): backend_path.read_text(),
    }
    revised = dict(original)
    a = str(core_path.relative_to(ROOT))
    if "def registered_checkpoints(" in original[a]:
        raise ValueError("cadence patch already present; reconcile against recorded identities")
    needle = '    if real and (cps != list(CHECKPOINTS) or manifest["max_new"] != 32):'
    if original[a].count(needle) != 1:
        raise ValueError("installed payload guard changed")
    revised[a] = (
        original[a]
        .replace(
            "def validate_payload(manifest, payload):",
            HELPER + "def validate_payload(manifest, payload):",
        )
        .replace(
            needle,
            '    if real and (cps != registered_checkpoints(manifest) or manifest["max_new"] != 32):',
        )
    )
    b = str(backend_path.relative_to(ROOT))
    revised[b] = (
        original[b]
        .replace(
            'protocol.get("schema_version") != 1', 'protocol.get("schema_version") not in (1, 2)'
        )
        .replace('        or protocol.get("checkpoints") != list(core.CHECKPOINTS)\n', "")
        .replace(
            '    if m["checkpoints"] != protocol["checkpoints"] or m["max_new"] != protocol["max_new"]:',
            '    cadence = core.registered_checkpoints(m, protocol)\n    if protocol.get("schema_version") == 1 and protocol.get("checkpoints") != cadence:\n        raise ValueError("legacy protocol cadence differs")\n    if m["checkpoints"] != cadence or m["max_new"] != protocol["max_new"]:',
        )
    )
    if revised[b] == original[b]:
        raise ValueError("backend guard changed")
    return original, revised


def main():
    original, revised = proposed_sources()
    output = ROOT / "docs/tasks/R1-77d-cadence.patch"
    patch = "".join(
        "".join(
            difflib.unified_diff(
                original[p].splitlines(True),
                revised[p].splitlines(True),
                fromfile="a/" + p,
                tofile="b/" + p,
            )
        )
        for p in original
    )
    with output.open("x") as f:
        f.write(patch)
    report = dict(
        task="R1-77d",
        status="prepared_not_applied",
        producer=ref(__file__),
        patch=ref(output),
        original_files=[ref(ROOT / p) for p in original],
        proposed_files_sha256={
            p: hashlib.sha256(v.encode()).hexdigest() for p, v in revised.items()
        },
        requires_rebuild=[
            "installed source identity",
            "driver identity",
            "backend binding",
            "final recipes",
            "freeze candidate v8",
        ],
        installed_files_modified=False,
    )
    with (ROOT / "logs/r1_round24/r1-77d-patch.json").open("x") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
