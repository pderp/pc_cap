"""CPU checks for scope isolation, partial inference and published bindings."""
import copy
import json
import math
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import analyze_block1 as scoped  # noqa: E402
import summarize  # noqa: E402
from scripts import r1_d14_report as formatter  # noqa: E402


@pytest.fixture(scope="module")
def analysis():
    return json.loads((HERE / "analysis.json").read_text())


def test_scope_does_not_read_later_cell_or_mutate_matrix(monkeypatch):
    calls = []

    def loader(cell, files, scope):
        calls.append(cell.get("result_dir"))
        return {}

    monkeypatch.setattr(scoped.analysis.old, "load_cell", loader)
    later = dict(block_number=2, result_dir="LIVE_CELL_DO_NOT_READ")
    with scoped.block1_view():
        scoped.analysis.old.load_cell(dict(block_number=1, result_dir="completed"), None, "confirmatory")
        value = scoped.analysis.old.load_cell(later, None, "confirmatory")
    assert calls == ["completed", None]
    assert later["result_dir"] == "LIVE_CELL_DO_NOT_READ"
    assert "outside_block1" in value["snapshot_exclusion"]
    assert scoped.analysis.old.load_cell is loader


def test_scope_restores_loader_on_error():
    original = scoped.analysis.old.load_cell
    with pytest.raises(RuntimeError), scoped.block1_view():
        raise RuntimeError("synthetic stop")
    assert scoped.analysis.old.load_cell is original


def test_missing_values_never_become_zero():
    assert summarize.stats([0, None, 0])["mean"] is None
    assert not summarize.stats([0, None, 0])["complete"]
    assert summarize.stats([0, 0, 0])["mean"] == 0
    assert summarize.stats([0, 0, 0])["sample_sd"] == 0


def test_full_family_and_no_interval_or_classifier(analysis):
    summary = summarize.build(analysis)
    assert len(summary["per_cell"]) == 45
    assert len(summary["primary_realization0"]) == 63
    assert sum(r["complete"] for r in summary["primary_realization0"]) == 12
    assert all(r["interval"] is None and r["classifier"] is None for r in summary["primary_realization0"])
    assert all(not r["complete"] for r in summary["primary_realization0"] if r["dataset"] == "mquake")
    assert len(analysis["cells"]) == 330
    assert len(analysis["prospectively_omitted_cells"]) == 75


@pytest.mark.parametrize("mutation", ["later_realization", "classifier", "interval"])
def test_contamination_is_rejected(analysis, mutation):
    data = copy.deepcopy(analysis)
    if mutation == "later_realization":
        data["cells"][0]["cell"]["realization"] = 1
    elif mutation == "classifier":
        data["contrasts"][0]["classification"] = "positive"
    else:
        data["contrasts"][0]["metrics"]["ES"]["adjusted_interval"] = dict(lower=0, upper=0)
    with pytest.raises(ValueError):
        summarize.build(data)


def test_all_materialized_table_bindings(analysis):
    model = json.loads((HERE / "appendix/report-data.json").read_text())
    documents = dict(analysis=analysis, watch=model["watch"], accounting=model["accounting"])
    count = 0
    for name, rows in model["tables"].items():
        for row, bindings in zip(rows, model["bindings"][name], strict=True):
            assert set(row) == set(bindings)
            for column, binding in bindings.items():
                if "document" not in binding:
                    expected = binding["literal"]
                else:
                    expected = formatter.resolve(documents[binding["document"]], binding["pointer"])
                    operation = binding.get("operation")
                    if operation == "length":
                        expected = len(expected)
                    elif operation == "exp_below_709":
                        expected = math.exp(expected) if expected is not None and expected < 709 else None
                    elif operation == "exp_overflow_at_709":
                        expected = expected >= 709 if expected is not None else None
                    else:
                        assert operation is None
                assert row[column] == expected
                count += 1
    assert count > 10000


def test_cost_is_full_process_not_process_plus_driver():
    audit = json.loads((HERE / "receipt-audit.json").read_text())
    process = math.fsum(r["charged_process_seconds"] for r in audit["rows"])
    assert process / 3600 == pytest.approx(audit["process_hours"])
    assert len({r["finish"]["path"] for r in audit["rows"]}) == 45
    assert all(r["uncovered_driver_seconds"] == r["unknown_costs"] == r["failures"] == 0 for r in audit["rows"])
    assert math.fsum(r["covered_driver_seconds"] for r in audit["rows"]) > 0


def test_watch_has_no_later_confirmation_cell():
    events = [json.loads(line) for line in (HERE / "watch-block1.jsonl").read_bytes().splitlines()]
    final = [e["observation"] for e in events if e["observation"]["scope"] == "confirmatory"]
    assert len(events) == 49 and len(final) == 45
    assert {r["cell"]["realization"] for r in final} == {0}


def test_ledger_preserves_all_historical_claims_and_binds_v10():
    supplement = json.loads((HERE / "talk-evidence-v6-session-v10.json").read_text())
    parent = json.loads(Path(supplement["parent"]["path"]).read_text())
    assert supplement["historical_rows"] == parent["rows"]
    assert len(supplement["historical_source_resolution"]) == 141
    assert "operator_v10" in supplement["signed_cost_receipt"]["path"]
    assert supplement["signed_cost_receipt"] != parent["signed_cost_receipt"]
    assert supplement["new_signatures"] is False
