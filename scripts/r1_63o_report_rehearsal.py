"""Reanalyze existing synthetic observations under D.5; no new experiment data."""

from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
from pathlib import Path
from unittest.mock import patch

from scripts import r1_49g_analyze as analyze
from scripts import r1_49o_protocol_matrix as producer
from scripts import r1_63l_full_validation_contract as full
from scripts import r1_d14_report as report
from scripts.r1_d14b_rehearsal import put, verify_bindings

ROOT = producer.ROOT


def run(output):
    output = Path(output)
    declared = producer.document()
    results = {}
    for name, old_path in [
        ("complete", ROOT / "logs/r1_round39/d14-complete-final/analysis.json"),
        ("partial", ROOT / "logs/r1_round39/d14-partial-v1/analysis.json"),
    ]:
        old = json.loads(old_path.read_text())
        matrix = json.loads(Path(old["matrix_file"]["path"]).read_text())
        assert matrix["synthetic"] and matrix["research_results"] is False
        by_id = {c["cell_id"]: c for c in matrix["cells"] + matrix["extension"]["cells"]}
        for section in ("cells", "extension"):
            source = declared["cells"] if section == "cells" else declared["extension"]["cells"]
            ordered = []
            for c in source:
                original = by_id[c["cell_id"]]
                original.update(
                    {
                        k: c[k]
                        for k in (
                            "block_number",
                            "within_block_order",
                            "expected_definition_sha256",
                            "previous_D4_definition_sha256",
                        )
                    }
                )
                ordered.append(original)
            if section == "cells":
                matrix["cells"] = ordered
            else:
                matrix["extension"]["cells"] = ordered
        for key in (
            "policy_revision",
            "inference_interpretation",
            "queue",
            "analysis_implementation",
        ):
            matrix[key] = copy.deepcopy(declared[key])
        target = output / name
        matrix_path = (
            ROOT
            / "docs/tasks/R1-63o-report-rehearsal"
            / output.name
            / name
            / "synthetic-matrix.json"
        )
        put(matrix_path, matrix)
        with patch.object(
            full,
            "production_contract",
            lambda matrix=matrix: copy.deepcopy(matrix["full_validation"]),
        ):
            observed = analyze.run(matrix_path, target / "analysis")
            rendered = report.run(target / "analysis.json", target / "report")
        old_stats = [c["metrics"] for c in old["contrasts"]]
        new_stats = [
            {m: {k: v for k, v in s.items() if k != "preliminary"} for m, s in c["metrics"].items()}
            for c in observed["contrasts"]
        ]
        assert old_stats == new_stats
        assert [c["classification"] for c in old["contrasts"]] == [
            c["classification"] for c in observed["contrasts"]
        ]
        data = json.loads((target / "report/report-data.json").read_text())
        checked = verify_bindings(data, observed)
        assert len(data["tables"]["primary"]) == 63 and len(data["tables"]["historical_v2"]) == 24
        for row in data["tables"]["primary"]:
            assert (
                len(row["order_dispersion"]) == 3
                and row["t_sensitivity"]["degrees_of_freedom"] == 2
            )
        exports = None
        if name == "complete":
            rendered_figures = subprocess.run(
                [
                    "/usr/bin/python3",
                    "-m",
                    "scripts.r1_d14_figures",
                    "--data",
                    str(target / "report/report-data.json"),
                ],
                cwd=ROOT,
                env={**os.environ, "MPLCONFIGDIR": str(ROOT / "logs/r1_63o/mpl-cache")},
                check=True,
                capture_output=True,
                text=True,
            )
            exports = json.loads(rendered_figures.stdout)
        results[name] = dict(
            report=rendered,
            checked_fields=checked,
            figures=exports,
            registered_numbers_and_classifiers_unchanged=True,
            incomplete_cells=len(observed["incomplete_cells"]),
        )
    value = dict(
        task="R1-63o",
        synthetic=True,
        research_results=False,
        results=results,
        gpu_seconds=0,
        model_calls=0,
    )
    put(output / "verification.json", value)
    return value


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(run(args.output), indent=2))
