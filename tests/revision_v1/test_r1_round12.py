"""CPU invariants for round-12 population accounting, matrix identities and IDF population."""

from __future__ import annotations

import copy
from types import SimpleNamespace

import numpy as np
import pytest
from scripts.r1_40d_matrix import CORE, EXTENSION, Binder, assemble, build, validate
from scripts.r1_d7_population_options import (
    QUERY_REASONS,
    query_exception_view,
    role_capacity,
    temporal_inventory,
)

from pccap.revision_v1.learner import RevisionCap
from pccap.revision_v1.reader import ReaderConfig, idf_weights, lex_feature
from pccap.revision_v1.train import lex_matrix


@pytest.mark.parametrize(
    "r,e,demand,fits",
    [
        (2, 1000, 2700, False),
        (3, 650, 3000, False),
        (3, 350, 2100, True),
        (3, 300, 1950, True),
        (2, 700, 2100, True),
    ],
)
def test_role_reserves_cannot_be_omitted(r, e, demand, fits):
    result = role_capacity(2100, r, e)
    assert result["full_role_demand"] == demand
    assert result["fits_before_additional_clearance"] is fits


@pytest.mark.parametrize("args", [(1, 0, 1), (-1, 3, 1), (100, True, 1), (100, 3, -1)])
def test_capacity_rejects_invalid_counts(args):
    with pytest.raises(ValueError):
        role_capacity(*args)


def test_query_exception_retains_primary_and_independent_exclusions():
    query = sorted(QUERY_REASONS)[0]
    s = {
        "candidates": {"mquake": [{"canonical_subject": "kept"}]},
        "removals": {
            "mquake": [
                {"canonical_subject": "released", "reasons": [query]},
                {
                    "canonical_subject": "primary",
                    "reasons": [query, "mquake_training_reserved_subject"],
                },
                {"canonical_subject": "overlap", "reasons": [query, "cross_dataset_overlap"]},
                {"canonical_subject": "released", "reasons": [query]},
            ]
        },
    }
    assert query_exception_view(s)["subjects"] == 2
    assert query_exception_view(s)["items"] == 3


def test_temporal_cases_are_not_distinct_edits_or_subjects():
    rewrite = {"subject": "Ａlice", "relation_id": "P1", "target_new": {"id": "Q2"}}
    cases = [
        {
            "case_id": i,
            "requested_rewrite": [rewrite],
            "orig": {"edit_triples": [["Q1", "P1", "Q2"]]},
        }
        for i in range(20)
    ]
    result = temporal_inventory(cases, {"existing": {"alice"}})
    assert (
        result["cases"],
        result["distinct_subjects"],
        result["distinct_subject_relation_edits"],
    ) == (20, 1, 1)
    assert result["subject_overlap"]["existing"] == 1
    assert result["teacher_eligible_new_subjects"] is None


@pytest.fixture
def matrix():
    return assemble(
        {k: {"reader": {"sha256": k}, "settings": {}} for k in (*CORE, EXTENSION)},
        {"base": "fixture"},
    )


def test_matrix_inventory_is_separate_and_deterministic(matrix):
    assert validate(matrix) is matrix
    assert len(matrix["cells"]) == 360
    assert len(matrix["extension"]["cells"]) == 45
    other = assemble(copy.deepcopy(matrix["conditions"]), copy.deepcopy(matrix["common_identity"]))
    assert other == matrix
    assert all(c["condition_id"] != EXTENSION for c in matrix["cells"])


@pytest.mark.parametrize(
    "mutation", ["missing", "duplicate", "checkpoint", "identity", "launch", "ceiling"]
)
def test_matrix_rejects_inventory_and_admission_drift(matrix, mutation):
    if mutation == "missing":
        matrix["cells"].pop()
    elif mutation == "duplicate":
        matrix["cells"][1] = copy.deepcopy(matrix["cells"][0])
    elif mutation == "checkpoint":
        matrix["cells"][0]["checkpoint_schedule"] = [100]
    elif mutation == "identity":
        matrix["cells"][0]["condition_identity"]["settings"]["bad"] = True
    elif mutation == "launch":
        matrix["launch_allowed"] = True
    else:
        matrix["cells"][0]["ceilings"]["wall_seconds"] = 1150
    with pytest.raises(ValueError):
        validate(matrix)


def test_condition_change_rekeys_only_affected_cells(matrix):
    cond = copy.deepcopy(matrix["conditions"])
    cond["R1_learned_ff"]["reader"]["sha256"] = "changed"
    new = assemble(cond, matrix["common_identity"])
    assert sum(a["cell_id"] != b["cell_id"] for a, b in zip(matrix["cells"], new["cells"])) == 45


def test_missing_and_changed_identity_refuse(tmp_path):
    b = Binder(tmp_path)
    with pytest.raises(FileNotFoundError):
        b.bind("missing")
    p = tmp_path / "weight"
    p.write_bytes(b"first")
    ref = b.bind(p)
    with pytest.raises(ValueError):
        b.bind(p, "0" * 64)
    p.write_bytes(b"second")
    with pytest.raises(ValueError):
        b.verify()
    assert ref["sha256"] != Binder(tmp_path).bind(p)["sha256"]


def test_real_matrix_builder_uses_selected_weight_and_continuation_identities():
    m = build()
    assert len(m["sources_sha256"]) >= 30
    assert m["conditions"]["R1_learned_ff"]["reference_manifest"]["path"].endswith(
        "primary_condition_v4.json"
    )
    assert m["conditions"][EXTENSION]["reference_manifest"]["path"].endswith(
        "primary_condition_v3.json"
    )
    assert m["conditions"][EXTENSION]["settings"]["rare_overlap_min"] is None
    assert m["conditions"]["R1_learned_ff"]["reader"] != m["conditions"][EXTENSION]["reader"]
    assert m["conditions"]["S1_LM"]["recipe"]["path"].endswith("r1_24_control_lm_v3_lr1e-8.json")
    assert m["conditions"]["S1_LM"]["fidelity"]["fidelity_pass"]
    assert m["population_gate"]["candidate_subjects"]["mquake"] == 2100


def test_idf_training_and_deployment_agree_given_identical_memory():
    prompts = [np.array([1, 10]), np.array([1, 20]), np.array([1, 30])]
    cfg = ReaderConfig(lexical=True, lex_idf=True, stop_tokens=())
    query = np.array([1, 10, 99])
    feats = SimpleNamespace(
        supports=[SimpleNamespace(prompt_ids=p) for p in prompts],
        queries=[SimpleNamespace(query_ids=query)],
    )
    cap = RevisionCap.__new__(RevisionCap)
    cap.cfg = SimpleNamespace(reader=cfg)
    records = [SimpleNamespace(source_ids=p) for p in prompts]
    cap.store = SimpleNamespace(lexical_version=0, active_records=lambda: records)
    weights = cap._lex_weights()
    assert weights == idf_weights(prompts, ())
    np.testing.assert_allclose(
        lex_matrix(cfg, feats)[0], [lex_feature(query, p, (), weights) for p in prompts], rtol=1e-6
    )
    cached = cap._lex_weights()
    assert cached is weights
    records.append(SimpleNamespace(source_ids=np.array([1, 10])))
    cap.store.lexical_version += 1
    assert cap._lex_weights() != weights
    # Restore uses a different store identity even if the lexical epoch is equal.
    cap.store = SimpleNamespace(
        lexical_version=1, active_records=lambda: [SimpleNamespace(source_ids=prompts[0])]
    )
    assert cap._lex_weights() == {1: 0.0, 10: 0.0}


def test_idf_population_size_and_frequency_change_the_feature():
    small = idf_weights([np.array([1, 10])] + [np.array([1, 20])] * 63, ())
    large = idf_weights([np.array([1, 10])] + [np.array([1, 20])] * 999, ())
    assert small[1] == large[1] == 0
    assert small[10] == pytest.approx(1 - np.log(2) / np.log(65))
    assert large[10] == pytest.approx(1 - np.log(2) / np.log(1001))
    assert lex_feature([1, 10, 99], [1, 10], (), small) != lex_feature(
        [1, 10, 99], [1, 10], (), large
    )
    assert idf_weights([None], ()) == {}
