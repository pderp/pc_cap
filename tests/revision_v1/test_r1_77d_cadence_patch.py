"""Proposed real cadence guard: accept only bound option-D cells, leave disk intact."""

import copy
import json
from pathlib import Path

import pytest
from scripts.r1_d9_layouts import digest, production

from pccap.revision_v1 import stage4_cell as core
from tests.revision_v1.r1_77d_patch_support import install


def fixture(monkeypatch, dataset):
    install(monkeypatch)
    root = Path(__file__).resolve().parents[2]
    matrix = json.loads((root / "manifests/revision_v1/run_matrix_v5_2_option_D.json").read_text())
    cell = next(c for c in matrix["cells"] if c["dataset"] == dataset)
    binding = {"path": "matrix", "sha256": "bound"}
    protocol = dict(
        schema_version=2,
        mode="stage4_final_protocol",
        lead_approved=True,
        open_gates=[],
        population_decision="DEC-060-option-D",
        dataset_layouts=production("D"),
        layout_sha256=digest(production("D")),
        max_new=32,
        locality_score="bounded_text_equality_DEC053",
        experiment_deadline="2026-10-09",
        matrix=binding,
        extension_admitted=False,
    )
    m = dict(
        cell={k: cell[k] for k in ("dataset", "condition", "realization", "order")},
        population_contract_version=2,
        protocol={"path": "protocol", "sha256": "bound"},
        matrix=binding,
        checkpoints=cell["checkpoints"],
    )
    monkeypatch.setattr(
        core, "read_binding", lambda b: protocol if b["path"] == "protocol" else matrix
    )
    return m, protocol, matrix


@pytest.mark.parametrize("dataset", ["zsre", "counterfact", "mquake"])
def test_exact_dataset_cadence_accepted(monkeypatch, dataset):
    m, _, _ = fixture(monkeypatch, dataset)
    assert core.registered_checkpoints(m) == (
        [100, 300] if dataset == "mquake" else [100, 300, 1000]
    )


@pytest.mark.parametrize(
    "fault",
    [
        "unapproved",
        "open",
        "wrong_decision",
        "wrong_dataset_cadence",
        "matrix",
        "missing_cell",
        "extension",
        "layout_bool",
        "missing_version",
        "recipe_matrix",
    ],
)
def test_unbound_or_wrong_cadence_refused(monkeypatch, fault):
    m, p, x = fixture(monkeypatch, "mquake")
    if fault == "unapproved":
        p["lead_approved"] = False
    if fault == "open":
        p["open_gates"] = ["U08"]
    if fault == "wrong_decision":
        p["population_decision"] = "other"
    if fault == "wrong_dataset_cadence":
        m["checkpoints"] = [100, 300, 1000]
    if fault == "matrix":
        x["name"] = "other"
    if fault == "missing_cell":
        m["cell"]["order"] = 999
    if fault == "extension":
        m["cell"]["condition"] = "R1_learned_ff_v2"
    if fault == "layout_bool":
        p["dataset_layouts"]["mquake"]["realizations"][0] = False
    if fault == "missing_version":
        del m["population_contract_version"]
    if fault == "recipe_matrix":
        m["matrix"] = copy.deepcopy(m["matrix"])
        m["matrix"]["sha256"] = "changed"
    with pytest.raises(ValueError):
        core.registered_checkpoints(m, p)
