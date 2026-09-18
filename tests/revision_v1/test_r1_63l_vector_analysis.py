"""Independent numerical recomputation and missing/corrupt full-vector admission checks."""

import copy
import uuid

import numpy as np
import pytest
from scripts import r1_63l_full_validation_contract as contract
from scripts import r1_68f_full_validation as execution

from tests.revision_v1.test_r1_63l_consumers import tiny_contract  # noqa: F401


def evidence(spec):
    directory = contract.ROOT / "results/R1/r1_63l_cpu_tests" / uuid.uuid4().hex / "attempt-0000"
    directory.mkdir(parents=True)
    path = directory / "full-validation-300.npz"
    values = np.full((2, 2, 5), 2.0)
    values[:, :, 0] += np.array([[0.2, -0.1], [0.0, 0.0]])
    values[:, :, 3:] = 0.0001
    np.savez_compressed(path, values=values)
    rows = [
        dict(item_id=f"w0:p{i + 1}", cap=float(values[0, i, 0]), capoff=2.0, original=2.0)
        for i in range(2)
    ]
    report = dict(checkpoint=300, state_sha256="s" * 64, endpoints=dict(drift=dict(rows=rows)))
    section = dict(
        status="complete",
        policy=execution.POLICY,
        checkpoint=300,
        state_sha256=report["state_sha256"],
        manifest_sha256="a" * 64,
        contract_sha256=contract.digest(spec),
        source=spec["source"],
        source_inventory=spec["source_inventory"],
        coverage={
            k: spec[k]
            for k in (
                "source_tokens",
                "window_tokens",
                "complete_windows",
                "expected_positions",
                "trailing_tokens_dropped",
                "windows_int64le_sha256",
            )
        },
        scored_positions=4,
        reference_base_sha256=dict(own_capoff="tiny", original_base="tiny"),
        vectors={
            **contract.ref(path),
            "fields": contract.FIELDS,
            "shape": [2, 2, 5],
            "dtype": "float64",
        },
        statistics={
            k: execution.tail_statistics(v, 2)
            for k, v in (
                ("loss_delta_capoff", values[:, :, 0] - values[:, :, 1]),
                ("loss_delta_original", values[:, :, 0] - values[:, :, 2]),
                ("kl_capoff_to_cap", values[:, :, 3]),
                ("kl_original_to_cap", values[:, :, 4]),
            )
        },
    )
    return section, report, path, values


def analyze(spec, section, report, path):
    return contract.summary(
        section,
        spec,
        report,
        path.parent / "checkpoint-300.json",
        "a" * 64,
        dict(base_sha256="tiny", locality_base_sha256="tiny"),
        {},
        sampled_population={"expected_positions": 2},
    )


def test_tail_and_fidelity_recomputed_from_vectors(tiny_contract):  # noqa: F811
    s, r, p, _ = evidence(tiny_contract)
    out = analyze(tiny_contract, s, r, p)
    assert out["complete"] and out["scored"] == out["planned"] == 4
    h = out["references"]["original"]["loss"]
    assert h["ES95_positive"] == pytest.approx(0.2)
    assert h["ES99_positive"] == pytest.approx(0.2)
    assert h["exceedances_nats"]["0.1"]["count"] == 1
    assert not out["fidelity"]["passes"]
    assert out["fidelity"]["references"]["original"]["mean_kl_pass"]


def test_sample_tails_and_full_tails_have_distinct_report_rows(tiny_contract):  # noqa: F811
    from scripts.r1_75_analysis_stage4_v1 import drift_summary

    s, r, p, _ = evidence(tiny_contract)
    full = analyze(tiny_contract, s, r, p)
    sampled = drift_summary(r["endpoints"]["drift"], {"expected_positions": 2})
    assert sampled["references"]["original"]["ES95_positive_nats"] == pytest.approx(0.2)
    assert sampled["references"]["original"]["exceedances_nats"]["0.1"] == 1
    text = "\n".join(
        contract.report_lines(
            [
                dict(
                    cell_id="test",
                    checkpoints={
                        "300": dict(secondary=dict(full_validation=full, sampled_drift=sampled))
                    },
                )
            ]
        )
    )
    assert "128-window sample (descriptive) | 2 / 2" in text
    assert "full validation | 4 / 4" in text
    assert contract.report_lines([dict(cell_id="legacy", checkpoints={})]) == []


@pytest.mark.parametrize(
    "fault",
    [
        "hash",
        "shape",
        "nan",
        "negative",
        "source",
        "reference",
        "sample",
        "stats",
        "coverage",
        "fields",
    ],
)
def test_corrupt_complete_endpoint_refuses(tiny_contract, fault):  # noqa: F811
    s, r, p, v = evidence(tiny_contract)
    if fault in ("hash", "shape", "nan", "negative"):
        v = v[:, :1] if fault == "shape" else v
        if fault == "nan":
            v[0, 0, 0] = np.nan
        if fault == "negative":
            v[0, 0, 3] = -0.1
        if fault == "hash":
            v[0, 0, 0] += 0.1
        np.savez_compressed(p, values=v)
        if fault != "hash":
            s["vectors"].update(contract.ref(p))
    if fault == "source":
        s["source"] = {**s["source"], "sha256": "b" * 64}
    if fault == "reference":
        s["reference_base_sha256"]["original_base"] = "wrong"
    if fault == "sample":
        r["endpoints"]["drift"]["rows"].pop()
    if fault == "stats":
        s["statistics"]["loss_delta_original"]["ES95_positive"] = 1.0
    if fault == "coverage":
        s["coverage"] = {**s["coverage"], "expected_positions": 3}
    if fault == "fields":
        s["vectors"]["fields"] = list(reversed(contract.FIELDS))
    with pytest.raises((ValueError, KeyError)):
        analyze(tiny_contract, s, r, p)


def test_missing_full_and_missing_vector_remain_unavailable(tiny_contract):  # noqa: F811
    s, r, p, _ = evidence(tiny_contract)
    out = analyze(tiny_contract, None, r, p)
    assert not out["complete"] and out["fidelity"] is None and out["planned"] == 4
    p.rename(p.with_suffix(".held"))
    out = analyze(tiny_contract, s, r, p)
    assert out["status"] == "missing_full_validation_vectors" and not out["complete"]


def test_backend_contract_requires_every_binding(tiny_contract):  # noqa: F811
    implementation = contract.ref(contract.__file__)
    m = dict(full_validation=tiny_contract, full_validation_implementation=implementation)
    protocol = dict(m, schema_version=2)
    frozen = dict(m, bindings_sha256={implementation["path"]: implementation["sha256"]})
    contract.admit(m, protocol, frozen)
    for where in ("recipe", "protocol", "freeze", "implementation"):
        a, b, c = copy.deepcopy((m, protocol, frozen))
        if where == "recipe":
            a.pop("full_validation")
        elif where == "protocol":
            b.pop("full_validation")
        elif where == "freeze":
            c.pop("full_validation")
        else:
            c["bindings_sha256"] = {}
        with pytest.raises(ValueError):
            contract.admit(a, b, c)
