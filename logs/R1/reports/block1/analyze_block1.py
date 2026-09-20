"""Run the locked analyzer with an explicit, outcome-independent block-1 view.

The original 330-cell matrix and all registered inference code remain unchanged.
Only load_cell is scoped: later blocks receive the native no-result observation.
No later-block report, payload, model or GPU is accessed. The wrapper restores
the original loader even on failure and binds itself into the output provenance.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from scripts import r1_49g_analyze as analysis  # noqa: E402

HERE = Path(__file__).resolve().parent
MATRIX = ROOT / "manifests/revision_v1/run_matrix_final.json"


@contextlib.contextmanager
def block1_view():
    original = analysis.old.load_cell

    def selected(cell, files, scope):
        if cell["block_number"] == 1:
            return original(cell, files, scope)
        result = original(dict(cell, result_dir=None), files, scope)
        result["snapshot_exclusion"] = "outside_block1_report_scope; not a current run failure"
        return result

    analysis.old.load_cell = selected
    try:
        yield
    finally:
        analysis.old.load_cell = original


def main():
    matrix = json.loads(MATRIX.read_bytes())
    cells = analysis.old.all_cells(matrix)
    selected = [c for c in cells if c["block_number"] == 1]
    if len(cells) != 330 or len(selected) != 45 or {c["realization"] for c in selected} != {0}:
        raise ValueError("expected exactly 45 realization-0 block-1 cells in the 330-cell matrix")
    with block1_view():
        report = analysis.run(MATRIX, HERE / "analysis-native")
    # Preserve the installed analyzer's untouched output as analysis-native.*.
    # Add explicit scope/provenance to a distinct artifact for reporting.
    report["snapshot_scope"] = dict(
        block_numbers=[1], included_cell_ids=[c["cell_id"] for c in selected],
        excluded_planned_cells=285,
        interpretation="Later blocks are outside this historical snapshot, not failed or absent in the live run.",
        inference="One realization; no primary classification, cluster interval or t interval available.",
    )
    report["analysis_source_sha256"][str(Path(__file__).relative_to(ROOT))] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if report["complete_blocks"] != [1] or sum(c["artifact_complete"] for c in report["cells"]) != 45:
        raise ValueError("not all 45 selected cells pass native receipt validation")
    if any(c["classification"] != "unavailable" for c in report["contrasts"]):
        raise ValueError("partial report must not contain primary classifier labels")
    with (HERE / "analysis.json").open("x") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps(dict(status="complete", cells=330, included=45, complete_blocks=[1],
                          primary_rows=63, classifier_labels_available=0, gpu_seconds=0)))


if __name__ == "__main__":
    main()
