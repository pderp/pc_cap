"""Synthetic evidence tree: table integrity and nonoverlapping cost accounting."""

import json
from pathlib import Path

import pytest

from aw.additional_work_assembly import build, copied_table, receipt_total, sha
from aw.supplemental_audit import Audit


def evidence(tmp_path):
    source = tmp_path / "canonical.md"
    block = "| Metric | Value |\n| --- | --- |\n| RET-GS | 0.123456789 |\n"
    source.write_text("# Canonical\n\n" + block + "\nUnrelated interpretation.\n")
    receipt = tmp_path / "run/cost.json"
    receipt.parent.mkdir()
    receipt.write_text(json.dumps(dict(elapsed_process_seconds=3600.25, status="resource_stop")))
    entries = [dict(path="run/cost.json", scope="run", group="test", field="elapsed_process_seconds")]
    return block, entries


def test_assembly_copies_bytes_keeps_failure_and_audits(tmp_path):
    block, entries = evidence(tmp_path)
    out, document = tmp_path / "output", tmp_path / "report.md"
    record = build(out, document, root=tmp_path, sources={"A": "canonical.md"},
                   sections=[("Question", "A", [("| Metric |", 0)], "Exposed fixture.", ["test"])],
                   entries=entries, gaps=[])
    assert block in document.read_text()
    assert record["accounting"]["known_process_seconds"] == 3600.25
    assert record["accounting"]["receipts"][0]["status"] == "resource_stop"
    assert Audit().report("fixture", out / "assembly.json")["status"] == "PASS"
    # Updating a self-declared document hash must not hide a changed table.
    document.write_text(document.read_text().replace("0.123456789", "0.99"))
    record["document"]["sha256"] = sha(document)
    (out / "assembly.json").write_text(json.dumps(record))
    audit = Audit().report("fixture", out / "assembly.json")
    assert audit["status"] == "FAIL"
    assert not audit["independent_checks"]["copied_tables_match"]
    with pytest.raises(FileExistsError):
        build(out, document, root=tmp_path)


@pytest.mark.parametrize("value", [None, "30", True, -1, float("nan"), float("inf")])
def test_invalid_receipt_never_becomes_zero(tmp_path, value):
    _, entries = evidence(tmp_path)
    (tmp_path / "run/cost.json").write_text(json.dumps(dict(elapsed_process_seconds=value)))
    with pytest.raises(ValueError):
        receipt_total(tmp_path, entries)


def test_missing_duplicate_and_nested_receipts_fail(tmp_path):
    _, entries = evidence(tmp_path)
    with pytest.raises(ValueError, match="duplicate"):
        receipt_total(tmp_path, entries * 2)
    nested = tmp_path / "run/child/cost.json"
    nested.parent.mkdir()
    nested.write_text('{"elapsed_process_seconds": 3}')
    with pytest.raises(ValueError, match="nested"):
        receipt_total(tmp_path, entries + [dict(entries[0], path="run/child/cost.json", scope="run/child")])
    with pytest.raises(FileNotFoundError):
        receipt_total(tmp_path, [dict(entries[0], path="absent/cost.json", scope="absent")])


def test_unknown_attempt_remains_unknown_and_cost_tamper_fails(tmp_path):
    _, entries = evidence(tmp_path)
    (tmp_path / "failed.log").write_text("failed before separate duration recorded")
    out, document = tmp_path / "out", tmp_path / "report.md"
    record = build(out, document, root=tmp_path, sources={"A": "canonical.md"}, sections=[],
                   entries=entries, gaps=[dict(path="failed.log", seconds=None)])
    assert record["accounting"]["lower_bound"]
    record["accounting"]["known_process_seconds"] += 1
    (out / "assembly.json").write_text(json.dumps(record))
    result = Audit().report("fixture", out / "assembly.json")
    assert result["status"] == "FAIL"
    assert not result["independent_checks"]["receipt_total_matches"]


def test_missing_or_ambiguous_tables_fail():
    block = "| a | b |\n| --- | --- |\n| 1 | 2 |\n"
    with pytest.raises(ValueError):
        copied_table(block, "| absent |")
    with pytest.raises(ValueError):
        copied_table(block + "\n" + block, "| a |")
    assert copied_table(block + "\n" + block, "| a |", 1)[0] == block


def test_native_source_mutation_is_detected(tmp_path):
    _, entries = evidence(tmp_path)
    out, document = tmp_path / "out", tmp_path / "report.md"
    build(out, document, root=tmp_path, sources={"A": "canonical.md"}, sections=[], entries=entries, gaps=[])
    (tmp_path / "canonical.md").write_text("different native result")
    assert Audit().report("fixture", out / "assembly.json")["status"] == "FAIL"


def test_receipt_status_and_amount_cannot_be_relabelled(tmp_path):
    _, entries = evidence(tmp_path)
    record = build(tmp_path / "out", tmp_path / "report.md", root=tmp_path,
                   sources={"A": "canonical.md"}, sections=[], entries=entries, gaps=[])
    record["accounting"]["receipts"][0]["status"] = "complete"
    path = Path(tmp_path / "out/assembly.json")
    path.write_text(json.dumps(record))
    assert Audit().report("fixture", path)["status"] == "FAIL"
