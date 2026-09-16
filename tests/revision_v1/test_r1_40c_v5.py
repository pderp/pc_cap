"""R1-40c draft identity, block, ceiling and missing-matrix contracts."""

from __future__ import annotations

import copy
import json
import unittest

from scripts import r1_40c_matrix_v5 as matrix
from scripts.r1_75_analysis_stage4_v1 import all_cells, analyze, coordinate_id


class MatrixTests(unittest.TestCase):
    def setUp(self):
        self.value = json.loads(
            (matrix.ROOT / "manifests/revision_v1/run_matrix_v5.json").read_text()
        )

    def test_complete_axes_blocks_stable_coordinate_and_selected_binding(self):
        m = matrix.validate(self.value)
        self.assertEqual(len(m["cells"]), 360)
        self.assertEqual(len(m["extension"]["cells"]), 45)
        self.assertEqual(
            [sum(c["block_number"] == b for c in all_cells(m)) for b in range(1, 7)],
            [45, 45, 90, 90, 90, 45],
        )
        c = m["cells"][0]
        changed = {**c, "result_dir": "another", "ceilings": {"wall_seconds": 123}}
        self.assertEqual(coordinate_id(c), coordinate_id(changed))
        self.assertEqual(
            m["common_identity"]["selected_reference"]["path"],
            str(matrix.ROOT / "manifests/revision_v1/primary_condition_v5.json"),
        )
        self.assertEqual(len(m["contrasts"]), 8)
        self.assertTrue(
            all(
                c["calibration_pending"]
                for c in all_cells(m)
                if c["dataset"] == "mquake" and not c["condition"].startswith("R1_")
            )
        )

    def test_tampering_and_unmeasured_cost_refuse(self):
        variants = []
        m = copy.deepcopy(self.value)
        m["cells"].pop()
        variants.append(m)
        m = copy.deepcopy(self.value)
        m["cells"][0]["block_number"] = 6
        variants.append(m)
        m = copy.deepcopy(self.value)
        m["cells"][0]["ceilings"]["wall_seconds"] = 100
        variants.append(m)
        m = copy.deepcopy(self.value)
        m["conditions"]["R1_learned_ff"]["interpretation"] = "different"
        variants.append(m)
        m = copy.deepcopy(self.value)
        m["launch_allowed"] = True
        variants.append(m)
        for value in variants:
            with self.subTest(value=value["cells"][0]["cell_id"]):
                with self.assertRaises(ValueError):
                    matrix.validate(value)

    def test_all_unlaunched_cells_visible_in_execution_order(self):
        r = analyze(self.value)
        self.assertEqual(len(r["incomplete_cells"]), 405)
        self.assertEqual(r["complete_blocks"], [])
        self.assertEqual(
            [c["block_number"] for c in r["incomplete_cells"]],
            sorted(c["block_number"] for c in r["incomplete_cells"]),
        )
        self.assertTrue(
            all(c["missing_checkpoints"] == [100, 300, 1000] for c in r["incomplete_cells"])
        )
        self.assertTrue(all(c["metrics"]["RET-GS"]["estimate"] is None for c in r["contrasts"]))


if __name__ == "__main__":
    unittest.main()
