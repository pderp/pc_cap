"""R1-75 adversarial inventories, missing pairs, tails and real TinyBase receipts."""

from __future__ import annotations

import copy
import json
import unittest
import uuid
from pathlib import Path

from scripts import r1_75_analysis_stage4_v1 as analysis

from pccap.revision_v1.endpoints import row_hash


def plan(payload):
    ep = payload["endpoints"]
    return {
        "item_ids": [r["item_id"] for r in payload["items"]],
        "paraphrase_counts": [len(r["paraphrases"]) for r in payload["items"]],
        "endpoints": {k: v["expected_ids"] for k, v in ep.items() if k != "drift"},
        "drift": {
            "expected_positions": ep["drift"]["expected_positions"],
            "source_sha256": row_hash(ep["drift"]),
        },
    }


def matrix(cells):
    return {
        "name": "test",
        "scope": "development",
        "cells": cells,
        "contrasts": [],
        "axes": {
            plural: list(dict.fromkeys(c[key] for c in cells))
            for key, plural in (
                ("condition", "conditions"),
                ("dataset", "datasets"),
                ("realization", "realizations"),
                ("order", "orders"),
            )
        },
        "multiplicity": {"status": "unresolved_U12"},
    }


class AnalysisTests(unittest.TestCase):
    def test_saved_development_counts_missing_rows_and_fractional_tail(self):
        m = json.loads((analysis.ROOT / "docs/tasks/R1-75-development.matrix.json").read_text())
        r = analysis.analyze(m)
        self.assertEqual(r["complete_blocks"], [1])
        self.assertEqual(r["incomplete_cells"], [])
        by = {c["cell"]["dataset"]: c["checkpoints"]["300"] for c in r["cells"]}
        cf = by["counterfact"]
        self.assertEqual(cf["primary"]["LS"]["numerator"], 49)
        self.assertEqual(cf["secondary"]["LS_terminated"]["numerator"], 36)
        self.assertEqual(cf["secondary"]["near_miss_bounded"]["numerator"], 100)
        self.assertEqual(cf["secondary"]["near_miss_terminated"]["numerator"], 63)
        self.assertEqual(cf["secondary"]["revision_latest"]["numerator"], 50)
        self.assertEqual(
            cf["secondary"]["drift"]["references"]["original"]["count_above_0_1_nats"], 52
        )
        self.assertAlmostEqual(
            cf["secondary"]["drift"]["references"]["original"]["ES99_positive_nats"],
            0.6384798650734221,
            places=7,
        )
        self.assertIsNone(by["zsre"]["secondary"]["near_miss_bounded"]["value"])
        self.assertEqual(by["zsre"]["secondary"]["near_miss_bounded"]["scored"], 0)
        self.assertEqual(by["zsre"]["primary"]["LS"]["numerator"], 50)
        self.assertTrue(cf["secondary"]["unseen_false_fire"]["wilson_full_inventory"]["upper"] > 0)

    def test_tinybase_receipt_chain_and_corruption_rejection(self):
        from tests.revision_v1.test_r1_68c_driver import DriverTests

        case = DriverTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        f = case.fixture("incremental")
        result = case.run_cell(f)
        recipe = json.loads(f[0].read_text())
        p = json.loads(Path(recipe["payload"]["path"]).read_text())
        c = {
            **recipe["cell"],
            "cell_id": analysis.coordinate_id(recipe["cell"]),
            "block_number": 1,
            "within_block_order": 1,
            "checkpoints": [1, 2],
            "result_dir": result["run_dir"],
            "manifest_sha256": case.reports(result)
            and analysis.Files().read(Path(result["run_dir"]) / "cell.json")["manifest_sha256"],
            "population": plan(p),
        }
        m = matrix([c])
        r = analysis.analyze(m)
        self.assertEqual(r["cells"][0]["status"], "complete_artifacts")
        self.assertEqual(
            r["cells"][0]["checkpoints"]["2"]["secondary"]["revision_latest"]["planned"], 1
        )
        bad = copy.deepcopy(m)
        bad["cells"][0]["manifest_sha256"] = "wrong"
        self.assertEqual(analysis.analyze(bad)["cells"][0]["status"], "invalid_cell")
        # New corrupted copy; never alter the original driver's result.
        target = analysis.ROOT / "results/R1/r1_75_cpu_tests" / uuid.uuid4().hex
        for old in Path(result["run_dir"]).rglob("*.json"):
            relative = old.relative_to(result["run_dir"])
            dest = target / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            row = json.loads(old.read_text())
            if old.name == "checkpoint-1.json":
                row["state_sha256"] = "corrupt"
            dest.open("x").write(
                json.dumps(row, indent=2, sort_keys=True) + "\n"
                if old.name == "checkpoint-1.json"
                else old.read_text()
            )
        bad = copy.deepcopy(m)
        bad["cells"][0]["result_dir"] = str(target)
        r = analysis.analyze(bad)
        self.assertEqual(r["cells"][0]["status"], "invalid_cell")
        self.assertIn("hash mismatch", r["cells"][0]["reason"])
        # Missing terminal checkpoint is reported, not filled by another cell.
        target2 = analysis.ROOT / "results/R1/r1_75_cpu_tests" / uuid.uuid4().hex
        for old in Path(result["run_dir"]).rglob("*.json"):
            if old.name.startswith("checkpoint-2") or old.name == "result.json":
                continue
            dest = target2 / old.relative_to(result["run_dir"])
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.open("x").write(old.read_text())
        bad["cells"][0]["result_dir"] = str(target2)
        r = analysis.analyze(bad)
        self.assertEqual(r["incomplete_cells"][0]["missing_checkpoints"], [2])
        self.assertFalse(r["blocks"][0]["complete"])

    def test_wilson_counts_and_tail_definition(self):
        ci = analysis.wilson(10, 100)
        self.assertAlmostEqual(ci["lower"], 0.055229, places=5)
        self.assertAlmostEqual(ci["upper"], 0.174366, places=5)
        self.assertIsNone(analysis.wilson(0, 0))
        with self.assertRaises(ValueError):
            analysis.wilson(101, 100)
        rows = [
            {"item_id": str(i), "cap": 2.0 if i == 0 else 0.0, "original": 0.0, "capoff": 0.0}
            for i in range(150)
        ]
        result = analysis.drift_summary({"rows": rows}, {"expected_positions": 150})
        self.assertAlmostEqual(result["references"]["original"]["ES99_positive_nats"], 2 / 1.5)
        self.assertEqual(result["references"]["original"]["count_above_0_1_nats"], 1)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            analysis.drift_summary({"rows": rows + [rows[0]]}, {"expected_positions": 151})

    def test_paired_clusters_no_imputation_or_multiplicity_admission(self):
        cells = []
        loaded = {}
        for r in range(3):
            for o in range(2):
                for condition in ("t", "c"):
                    cell = {
                        "condition": condition,
                        "dataset": "zsre",
                        "realization": r,
                        "order": o,
                        "checkpoints": [1],
                        "population": {"item_ids": [f"r{r}"]},
                        "block_number": 1,
                        "within_block_order": len(cells) + 1,
                    }
                    cell["cell_id"] = analysis.coordinate_id(cell)
                    cells.append(cell)
                    loaded[cell["cell_id"]] = {
                        "checkpoints": {
                            "1": {
                                "primary": {
                                    k: {
                                        "value": (0.8 if condition == "t" else 0.7)
                                        if k == "RET-GS"
                                        else 1.0
                                    }
                                    for k in ("ES", "RET-GS", "LS")
                                }
                            }
                        }
                    }
        m = matrix(cells)
        m["bootstrap"] = {"seed": 0, "draws": 100, "confidence": 0.975}
        m["contrasts"] = [{"id": "t-c", "treatment": "t", "control": "c", "role": "primary"}]
        a = analysis.pair_contrasts(m, loaded)[0]
        self.assertAlmostEqual(a["metrics"]["RET-GS"]["estimate"], 0.1)
        self.assertIsNotNone(a["metrics"]["RET-GS"]["interval"])
        self.assertEqual(a["classification"], "unadmitted_multiplicity")
        sparse = copy.deepcopy(loaded)
        sparse.pop(cells[0]["cell_id"])
        b = analysis.pair_contrasts(m, sparse)[0]
        self.assertIsNone(b["metrics"]["RET-GS"]["estimate"])
        self.assertEqual(b["metrics"]["RET-GS"]["status"], "incomplete")
        duplicate = copy.deepcopy(m)
        for cell in duplicate["cells"]:
            cell["population"] = {"item_ids": ["same"]}
        c = analysis.pair_contrasts(duplicate, loaded)[0]
        self.assertEqual(c["metrics"]["RET-GS"]["status"], "dependent_realizations")
        self.assertIsNone(c["metrics"]["RET-GS"]["interval"])

    def test_duplicate_coordinates_and_unavailable_observer(self):
        m = json.loads((analysis.ROOT / "docs/tasks/R1-75-development.matrix.json").read_text())
        m["cells"].append(copy.deepcopy(m["cells"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            analysis.validate_matrix(m)
        out = analysis.scalar_rows(
            [{"item_id": "a", "status": "ok", "false_fire": False, "firing_status": "unavailable"}],
            ["a"],
            "false_fire",
        )
        self.assertIsNone(out["value"])
        self.assertEqual(out["scored"], 0)


if __name__ == "__main__":
    unittest.main()
