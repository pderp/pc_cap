"""X21 G1--G4 acceptance: report semantics, source bindings and accounting replay."""

import copy
import hashlib
import json
import math
from pathlib import Path

import pytest
from scripts import ht_audit_existing as audit
from scripts import r1_d11_block_report as d11
from scripts import r1_d13_daily as daily
from scripts import r1_d14_report as report
from scripts import r1_d14b_accounting as accounting

from tests.revision_v1 import test_r1_d11_block_report as queue_fixtures

fixture = queue_fixtures.fixture
FIXTURES = Path(__file__).parents[1] / "fixtures"


@pytest.fixture
def analysis():
    result = json.loads((FIXTURES / "r1_d14_report_example.json").read_text())
    result["historical_pointwise_contrasts"] = json.loads(
        (FIXTURES / "r1_d14b_historical_example.json").read_text()
    )["contrasts"]
    return result


def tables(analysis, account=None):
    return report.build(analysis, report.watch_snapshot(None, analysis), account)["tables"]


def test_primary_family_and_bindings_unchanged(analysis):
    rows = tables(analysis)["primary"]
    expected = json.loads((report.ROOT / "logs/r1_round41/primary-before.json").read_text())
    assert rows == expected["primary"]
    assert (
        report.build(analysis, report.watch_snapshot(None, analysis))["bindings"]["primary"]
        == expected["bindings"]
    )
    assert len(rows) == 63


@pytest.mark.parametrize("values", [[0.1, 2, 2, -1], [-4, -3, -2, -1], [0, 0, 0, 0]])
def test_signed_maximum_ties_and_zero_atoms(analysis, values):
    sec = analysis["cells"][0]["checkpoints"]["1000"]["secondary"]
    expected = audit.statistics(values, ["w0:p1", "w0:p2", "w1:p1", "w1:p2"])
    expected["ES99_positive"] = audit.tail_sum([max(0, x) for x in values], 0.01) / 0.04
    for metric in ("loss", "kl"):
        sec["full_validation"]["references"]["capoff"][metric] = copy.deepcopy(expected)
    rows = [
        r
        for r in tables(analysis)["tails"]
        if r["cell_id"] == analysis["cells"][0]["cell_id"]
        and r["checkpoint"] == 1000
        and r["reference"] == "capoff"
        and r["population"] == "full_validation"
    ]
    for row in rows:
        for field in (
            "maximum_signed",
            "maximum_positive",
            "maximum_location",
            "maximum_tie_count",
            "atom_zero_signed",
            "atom_zero_positive",
        ):
            assert row[field] == expected[field]
        assert row["maximum_location_basis"] == "signed maximum"
        assert "exact equality" in row["maximum_tie_convention"]
    if max(values) < 0:
        assert rows[0]["maximum_signed"] == -1 and rows[0]["maximum_positive"] == 0
        assert rows[0]["atom_zero_positive"] == dict(count=4, denominator=4)
        assert rows[0]["atom_zero_signed"] == dict(count=0, denominator=4)


@pytest.mark.parametrize(
    "mean,overflow",
    [(1, False), (-2, False), (708.9, False), (709, True), (1000, True), (None, None)],
)
def test_sample_explicit_exponential_derivation_and_missing_fields(analysis, mean, overflow):
    sec = analysis["cells"][0]["checkpoints"]["1000"]["secondary"]
    sec["sampled_drift"]["references"]["capoff"]["mean_signed_nats"] = mean
    result = report.build(analysis, report.watch_snapshot(None, analysis))
    row_index, row = next(
        (i, r)
        for i, r in enumerate(result["tables"]["tails"])
        if r["cell_id"] == analysis["cells"][0]["cell_id"]
        and r["checkpoint"] == 1000
        and r["reference"] == "capoff"
        and r["population"] == "sampled_drift"
    )
    assert row["exp_mean_signed_overflow"] is overflow
    assert row["exp_mean_signed"] == (math.exp(mean) if overflow is False else None)
    assert row["maximum_signed"] is None and row["maximum_tie_count"] is None
    assert row["atom_zero_signed"] is None and row["atom_zero_positive"] is None
    assert row["zero_positive_n"] == 1 and row["zero_positive_denominator"] == 2
    assert row["maximum_location"] == "w0:p1"
    binding = result["bindings"]["tails"][row_index]["exp_mean_signed"]
    assert binding["derived"] is True and binding["operation"] == "exp_below_709"
    assert report.resolve(analysis, binding["pointer"]) == mean
    json.dumps(row, allow_nan=False)


def test_full_exponential_is_copied_including_overflow_not_reestimated(analysis):
    sec = analysis["cells"][0]["checkpoints"]["1000"]["secondary"]
    loss = sec["full_validation"]["references"]["capoff"]["loss"]
    loss.update(mean_signed=710, exp_mean_signed=None, exp_mean_signed_overflow=True)
    rows = tables(analysis)["tails"]
    row = next(r for r in rows if r["population"] == "full_validation" and r["metric"] == "loss")
    assert row["exp_mean_signed"] is None and row["exp_mean_signed_overflow"] is True
    assert all(r["exp_mean_signed"] is None for r in rows if r["metric"] == "kl")


@pytest.mark.parametrize(
    "kl,nll,passes",
    [
        (0, 0, True),
        (0.001, 0.01, True),
        (0.00101, 0, False),
        (0, 0.01001, False),
        (None, None, None),
    ],
)
@pytest.mark.parametrize("reference", ["capoff", "original"])
def test_joint_flag_reference_failures_bounds_and_unavailability(
    analysis, kl, nll, passes, reference
):
    before = tables(analysis)["primary"]
    c = analysis["cells"][0]
    benchmark = c["cap_fidelity_benchmark"]
    for ref in benchmark["references"].values():
        ref.update(
            mean_kl_nats=0,
            mean_signed_nll_increase_nats=0,
            mean_kl_label="pass",
            mean_nll_label="pass",
        )
    benchmark["references"][reference].update(
        mean_kl_nats=kl,
        mean_signed_nll_increase_nats=nll,
        mean_kl_label="unavailable" if kl is None else "pass" if kl <= 0.001 else "fail",
        mean_nll_label="unavailable" if nll is None else "pass" if nll <= 0.01 else "fail",
    )
    benchmark.update(passes=passes, status="complete" if passes is not None else "unavailable")
    out = tables(analysis)
    assert out["primary"] == before
    for row in out["fidelity"][:2]:
        assert row["joint_cap_benchmark_passes"] is passes
        assert row["scientific_admission"] == c["scientific_admission"]
        assert row["admission_veto"] is False
    del benchmark["passes"]
    assert tables(analysis)["fidelity"][0]["joint_cap_benchmark_passes"] is None


def test_historical_extension_keeps_24_descriptive_rows_and_no_mquake_1000(analysis):
    primary = tables(analysis)["primary"]
    rows = tables(analysis)["historical_v2"]
    assert len(rows) == 24
    assert all(r["classification"] == "secondary_descriptive" for r in rows)
    assert all(len(r["realizations"]) == 3 for r in rows)
    assert not any(r["dataset"] == "mquake" and r["checkpoint"] == 1000 for r in rows)
    # Legacy primary rows must never be promoted into the descriptive collection.
    legacy = copy.deepcopy(analysis["historical_pointwise_contrasts"][0])
    legacy["contrast"]["role"] = "primary"
    analysis["historical_pointwise_contrasts"].append(legacy)
    assert len(tables(analysis)["historical_v2"]) == 24
    for metric in analysis["historical_pointwise_contrasts"][0]["metrics"].values():
        metric.update(
            observed_pairs=14, status="incomplete", estimate=None, interval=None, bootstrap=None
        )
    missing = tables(analysis)["historical_v2"][:3]
    assert all(
        r["observed_pairs"] == 14
        and r["planned_pairs"] == 15
        and r["interval"] is None
        and r["realizations"] is None
        for r in missing
    )
    analysis["historical_pointwise_contrasts"] = []
    assert "historical_v2" not in tables(analysis)
    assert tables(analysis)["primary"] == primary


def test_validation_completion_does_not_complete_near_revision_or_composition(analysis):
    c = analysis["cells"][0]
    c.update(
        artifact_complete=True,
        endpoint_complete=True,
        full_validation_complete=True,
        sampled_drift_complete=True,
        primary_metrics_complete=True,
        unreceipted_checkpoints=[300],
    )
    c["checkpoints"]["1000"]["secondary"]["composition"] = dict(
        status="unavailable", planned=3, scored=0, missing=3
    )
    analysis["secondary_benchmarks"]["cells"][0]["benchmarks"]["revision_latest"].update(
        status="incomplete", planned=50, scored=49, passes=None, value=None
    )
    analysis["near_miss_family"]["cells"][0].update(planned=100, evaluated=98, missing=2)
    out = tables(analysis)
    assert out["cell_inventory"][0]["endpoint_complete"] is True
    assert (
        out["cell_inventory"][0]["endpoint_complete_scope"]
        == "full_validation AND sampled_drift only"
    )
    assert out["cell_inventory"][0]["unreceipted_checkpoints"] == [300]
    assert out["near_miss"][0]["missing"] == 2
    assert (
        next(r for r in out["secondary_cells"] if r["benchmark"] == "revision_latest")["scored"]
        == 49
    )
    assert (
        next(r for r in out["endpoint_observations"] if r["endpoint"] == "composition")[
            "observation"
        ]["scored"]
        == 0
    )


def save_account(f, **kwargs):
    snap = f["build"](**kwargs)
    p = queue_fixtures.put(f["root"] / "logs/d11.json", snap)
    a = dict(matrix_file=d11.ref(f["mp"]), cells=f["cells"], sources_sha256={})
    return p, a, snap


def test_verified_accounting_retry_host_unknown_partial_block_and_no_double_charge(fixture):
    f = fixture
    f["process"](0, seconds=20, driver_seconds=15)
    f["complete"].add(f["cells"][0]["cell_id"])
    f["process"](1, seconds=7, failure=True)
    f["process"](1, seq=1, seconds=8, failure=True)
    folder = f["process"](2, seconds=3)
    finish = json.loads((folder / "finish.json").read_text())
    finish["failure_class"] = "host"
    queue_fixtures.put(folder / "finish.json", finish)
    f["process"](2, seq=1, finish=False)
    path, analysis, snap = save_account(f, boundary_block=1)
    doc = accounting.load(path, analysis, receipt_root=f["receipts"])
    assert doc["snapshot"]["cost_ledger"]["charged_seconds"] == 38
    assert doc["snapshot"]["cost_ledger"]["uncovered_driver_seconds"] == 0
    assert snap["inventory"]["queue"][1]["retry"]["exhausted"] is True
    assert snap["inventory"]["cost"]["projected_total_hours"] is None
    assert snap["inventory"]["cost"]["unknown_attempts"]
    assert snap["boundary_ready"] is True and not snap["inventory"]["blocks"][0]["complete"]
    assert sum(p["failure_class"] == "host" for p in doc["process_finishes"]) == 1
    output = report.Tables({})
    accounting.add_tables(output, doc, report.at)
    for name, rows in output.tables.items():
        for row, bindings in zip(rows, output.bindings[name], strict=True):
            for field, binding in bindings.items():
                assert row[field] == report.resolve(doc, binding["pointer"])


@pytest.mark.parametrize(
    "mutation", ["matrix", "root", "totals", "new_attempt", "source", "analysis_source"]
)
def test_accounting_mismatch_tampering_and_different_snapshot_refused(fixture, mutation):
    f = fixture
    folder = f["process"](0, seconds=20, driver_seconds=15)
    path, analysis, snap = save_account(f)
    root = f["receipts"]
    if mutation == "matrix":
        analysis["matrix_file"] = dict(analysis["matrix_file"], sha256="0" * 64)
    elif mutation == "root":
        root = root.parent / "other"
    elif mutation == "totals":
        snap["cost_ledger"]["charged_seconds"] += 100
        snap["report_sha256"] = d11.watch.full.digest(
            {k: v for k, v in snap.items() if k != "report_sha256"}
        )
        queue_fixtures.put(path, snap)
    elif mutation == "new_attempt":
        f["process"](1, finish=False)
    elif mutation == "source":
        (folder / "finish.json").write_text("{}\n")
    else:
        analysis["sources_sha256"][str(folder / "finish.json")] = "0" * 64
    with pytest.raises(ValueError):
        accounting.load(path, analysis, receipt_root=root)


def test_daily_d13_wrapper_and_explicit_unavailable(analysis, fixture, monkeypatch):
    f = fixture
    monkeypatch.setattr(daily, "ROOT", f["root"])
    _, a, snap = save_account(f)
    # Real D13 emitter preserves its D11 digest and writes the separate binding.
    doc = dict(
        task="R1-D13",
        version=1,
        mode="daily",
        d11=snap,
        health=dict(
            memory=dict(status="unavailable", read_issues=[]),
            gpu=dict(status="unavailable", read_issues=[]),
        ),
    )
    path = daily.emit(doc, f["root"] / "logs/daily")["path"]
    verified = accounting.load(path, a, receipt_root=f["receipts"])
    assert verified["snapshot"] == snap
    with pytest.raises(ValueError, match="explicit accounting receipt root"):
        accounting.load(path, a)
    absent = tables(analysis)["accounting_summary"][0]
    assert absent["status"] == "unavailable_not_supplied"
    assert absent["known_process_hours"] is None and absent["host_failures"] is None


def test_primary_golden_file_itself_is_bound():
    prior = json.loads((report.ROOT / "logs/r1_round41/primary-before.json").read_text())
    canonical = json.dumps(prior["primary"], sort_keys=True, separators=(",", ":")).encode()
    assert (
        hashlib.sha256(canonical).hexdigest()
        == "475014532abf18d58a5c739f9e01edd8de367b26b4713d69de6295cb70027dd0"
    )
