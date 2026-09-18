"""Report binding, missing-data and prospective-scope regressions; CPU only."""

import copy
import json
import re
from pathlib import Path

import pytest
from scripts import r1_d14_report as report

EXAMPLE = Path(__file__).parents[1] / "fixtures/r1_d14_report_example.json"


@pytest.fixture
def analysis():
    return json.loads(EXAMPLE.read_text())


def test_every_output_field_resolves_to_bound_value(analysis):
    watch = report.watch_snapshot(None, analysis)
    result = report.build(analysis, watch)
    documents = dict(analysis=analysis, watch=watch)
    assert len(result["tables"]["primary"]) == 63
    for name, rows in result["tables"].items():
        for row, bindings in zip(rows, result["bindings"][name], strict=True):
            assert set(row) == set(bindings)
            for column, binding in bindings.items():
                if "literal" in binding:
                    expected = binding["literal"]
                else:
                    expected = report.resolve(documents[binding["document"]], binding["pointer"])
                    if binding.get("operation") == "length":
                        expected = len(expected)
                assert row[column] == expected


def test_unavailable_mquake_intervals_and_omissions_stay_distinct(analysis):
    rows = report.build(analysis, report.watch_snapshot(None, analysis))["tables"]
    mq = [r for r in rows["primary"] if r["dataset"] == "mquake"]
    assert len(mq) == 21
    assert all(r["estimate"] is None and r["adjusted_interval"] is None for r in mq)
    assert len(rows["omissions"]) == 75
    assert len(rows["mquake300"]) == 1  # one saved schema-example cell per dataset
    assert all(r["admission_veto"] is False for r in rows["fidelity"])
    assert any(r["mean_kl_label"] == "fail" for r in rows["fidelity"])
    assert any(r["scientific_admission"] for r in rows["primary"])


def test_missing_cell_and_watch_never_become_zero_or_pass(analysis):
    cell = analysis["cells"][0]
    cell["checkpoints"] = {}
    cell.pop("cap_fidelity_benchmark")
    cell.pop("endpoint_complete")
    cell.update(
        status="missing",
        artifact_complete=False,
        scientific_admission=False,
        missing_checkpoints=[100, 300, 1000],
    )
    analysis["incomplete_cells"] = [
        dict(cell_id=cell["cell_id"], reason="missing synthetic result")
    ]
    ws = report.watch_snapshot(None, analysis)
    rows = report.build(analysis, ws)["tables"]
    assert rows["incomplete"][0]["reason"] == "missing synthetic result"
    assert rows["cell_inventory"][0]["endpoint_complete"] is None
    assert rows["fidelity"][0]["mean_kl_nats"] is None
    assert rows["fidelity"][0]["mean_kl_label"] == "unavailable"
    assert ws["breach_entries"] is None and ws["creep_alerts"] is None
    assert ws["events"] is None and ws["queue_observations"] is None


def test_template_fills_with_real_shaped_tables_and_json_braces(analysis, tmp_path):
    model = report.build(analysis, report.watch_snapshot(None, analysis))
    text = "\n".join(report.table_text(k, model, tmp_path) for k in model["tables"])
    values = dict.fromkeys(report.TOKENS, text + '\n{"outer":{"nested":1}}')
    rendered = report.fill((report.ROOT / "docs/R1_stage4_report_skeleton.md").read_text(), values)
    assert not re.search(r"\{\{[A-Z0-9_]+\}\}", rendered)
    assert "unavailable" in rendered
    assert (tmp_path / "primary.csv").read_text().count("\n") == 64


@pytest.mark.parametrize("change", ["unknown", "duplicate", "omitted", "nested"])
def test_placeholder_contract_rejects_unbound_fields(change):
    template = "\n".join("{{" + k + "}}" for k in sorted(report.TOKENS))
    values = dict.fromkeys(report.TOKENS, "bound")
    if change == "unknown":
        template += "{{UNKNOWN}}"
    elif change == "duplicate":
        template += "{{PRIMARY}}"
    elif change == "omitted":
        values.pop("PRIMARY")
    else:
        values["PRIMARY"] = "{{UNBOUND}}"
    with pytest.raises(ValueError):
        report.fill(template, values)


def test_bad_json_pointer_is_an_error_not_a_missing_result(analysis):
    bad = copy.deepcopy(analysis)
    del bad["contrasts"][0]["metrics"]["ES"]["estimate"]
    with pytest.raises(ValueError, match="unbound report field"):
        report.build(bad, report.watch_snapshot(None, bad))


def test_reduced_family_is_rejected(analysis):
    analysis["contrasts"].pop()
    with pytest.raises(ValueError, match="21 contrasts"):
        report.build(analysis, report.watch_snapshot(None, analysis))


def test_torn_watch_journal_is_rejected(analysis, tmp_path):
    path = tmp_path / "watch.jsonl"
    path.write_text("{}")
    with pytest.raises(ValueError, match="torn"):
        report.watch_snapshot(path, analysis)


def test_endpoint_counts_and_truncation_diagnostics_are_retained(analysis):
    tables = report.build(analysis, report.watch_snapshot(None, analysis))["tables"]
    revision = next(r for r in tables["secondary_cells"] if r["benchmark"] == "revision_latest")
    assert revision["planned"] == 50 and revision["scored"] == 50
    assert revision["numerator"] == 50 and revision["wilson95"]["confidence"] == 0.95
    locality = next(r for r in tables["endpoint_observations"] if r["endpoint"] == "locality")
    assert locality["observation"]["preserved_terminated_n"] == 50
    assert locality["observation"]["truncated_pair_n"] == 0
