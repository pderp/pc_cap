"""Guard publication at the approved partial-block halt; preserve unrelated claims."""

import pccap  # noqa: F401 # isort: skip

# isort: split

import copy
import json

import pytest

from aw import refresh_after_halt as r
from aw.presentation_claims import read_rows, refresh_text


def fixture():
    cells = [
        dict(cell_id=str(i), block_number=4 if i < 225 else 5 if i < 285 else 6) for i in range(330)
    ]
    report = dict(
        identity=dict(matrix=dict(sha256="matrix")),
        boundary_block=5,
        boundary_ready=False,
        complete_cells=[str(i) for i in range(270)],
        boundary_unprocessed=[str(i) for i in range(270, 285)],
        boundary_gap_cells=[],
        inventory=dict(cost=dict(unknown_attempts=[]), queue=[]),
        cost_ledger=dict(uncovered_driver_seconds=0),
        watch=dict(missing_completed_cells=[]),
        issues=[],
    )
    return cells, report


def test_intentional_partial_block_is_accepted_but_other_gaps_are_not():
    cells, report = fixture()
    r.validate_boundary(report, cells, "matrix")
    for change in (
        dict(complete_cells=report["complete_cells"][:-1]),
        dict(boundary_unprocessed=[]),
        dict(boundary_gap_cells=["33"]),
        dict(boundary_block=4),
        dict(issues=["cost unknown"]),
        dict(inventory=dict(cost=dict(unknown_attempts=["live"]), queue=[])),
    ):
        with pytest.raises(ValueError):
            r.validate_boundary(report | change, cells, "matrix")


def test_dry_run_never_writes(tmp_path, monkeypatch):
    cells, report = fixture()
    inv = copy.deepcopy(report["inventory"])
    inv["cost"]["unknown_attempts"] = ["live"]
    monkeypatch.setattr(r, "current_inventory", lambda: (cells, inv, [str(i) for i in range(252)]))
    out = tmp_path / "must-not-exist"
    p = r.prepare(out)
    assert p["observed_complete_cells"] == 252 and len(p["missing_prefix_cells"]) == 18
    assert not p["writes_performed"] and not out.exists()


def test_ledger_refresh_preserves_pc_and_conceptual_rows(tmp_path):
    original = r.LEDGER.read_text()
    text = refresh_text(original, r.PREVIOUS)
    before = {v[0]: v for v in read_rows(original)}
    after = {v[0]: v for v in read_rows(text)}
    for k in before:
        if not k.startswith(("comparator-", "R1-retention-")) and k not in (
            "resources",
            "unavailable",
            "R1-fidelity",
        ):
            assert after[k] == before[k]
    # The same refresh adds S1 rows once a real report supplies them.
    report = json.loads(r.PREVIOUS.read_text())
    native = json.loads(open(report["analysis"]["path"]).read())
    c = copy.deepcopy(next(x for x in native["contrasts"] if x["classification"] != "unavailable"))
    c["contrast"]["control"] = "S1_LM"
    native["contrasts"].append(c)
    p = tmp_path / "native.json"
    p.write_text(json.dumps(native))
    report["analysis"] = dict(path=str(p), sha256=r.sha(p))
    f = tmp_path / "report.json"
    f.write_text(json.dumps(report))
    rows = read_rows(refresh_text(original, f))
    assert any(row[0] == f"comparator-{c['dataset']}-S1_LM" for row in rows)


def test_tail_gate_detects_percentile_bug(monkeypatch):
    from aw import tail_figures

    monkeypatch.setattr(tail_figures, "statistics", lambda x: dict(es99_positive=0.0))
    with pytest.raises(ValueError, match="percentile"):
        r.tail_gate()
