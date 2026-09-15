"""Immutable driver receipt compatibility with independently planned analysis."""

from pathlib import Path

import pytest

from pccap.revision_v1.analysis import Reader, digest
from pccap.revision_v1.analysis_stage4 import expected_inventory, read_completed_cell
from pccap.revision_v1.stage4_cell import write_json
from tests.revision_v1.test_analysis_stage4 import population, report


@pytest.mark.parametrize("bad", [None, "report_hash", "chain"])
def test_checkpoint_receipts_are_verified_before_aggregation(tmp_path, bad):
    cell = {
        **expected_inventory()["cells"][0],
        "dataset": "mquake",
        "manifest_sha256": "a" * 64,
        "result_dir": str(tmp_path),
        "admitted": True,
    }
    p = population()
    meta = {
        "cell": {k: cell[k] for k in ("condition", "dataset", "realization", "order")},
        "manifest_sha256": "a" * 64,
        "checkpoints": [100, 300, 1000],
        "mode": "synthetic",
    }
    write_json(tmp_path / "cell.json", meta)
    previous = None
    for n in (100, 300, 1000):
        attempt = tmp_path / f"attempt-{n}"
        attempt.mkdir()
        cp = {**report(n), "checkpoint": n, "state_sha256": str(n)}
        binding = write_json(attempt / "report.json", cp)
        if bad == "report_hash" and n == 300:
            binding["sha256"] = "b" * 64
        rec = {
            "checkpoint": n,
            "manifest_sha256": "a" * 64,
            "previous_receipt_sha256": previous,
            "report": binding,
            "state_sha256": str(n),
        }
        if bad == "chain" and n == 300:
            rec["previous_receipt_sha256"] = "c" * 64
        rec["receipt_sha256"] = digest(rec)
        write_json(attempt / f"checkpoint-{n}.receipt.json", rec)
        previous = rec["receipt_sha256"]
    reader = Reader(Path("/"))
    if bad:
        with pytest.raises(ValueError, match="hash|chain"):
            read_completed_cell(reader, cell, p)
    else:
        result = read_completed_cell(reader, cell, p)
        assert result["metrics_complete"] and result["status"] == "complete"
        assert result["missing_checkpoints"] == []
        assert not result["scientific_admission"]
        assert result["checkpoints"]["1000"]["secondary"]["composition"]["planned"] == 1
        assert result["checkpoints"]["1000"]["secondary"]["composition"]["value"] is None
        reader.verify()
