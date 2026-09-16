"""R1-68c CPU parity, prefix independence, phase scopes and mutation refusal."""

from __future__ import annotations

import json
import tempfile
import types
import unittest
import uuid
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import numpy as np
from scripts import r1_68c_dev_cell as driver
from scripts.r1_68c_batched_drift import PositionBatchReader, batched_drift

from pccap.harness.ledger import Ledger
from pccap.revision_v1.endpoints_composition import as_edit
from pccap.revision_v1.stage4_adapters import build_adapter
from pccap.revision_v1.stage4_assays import CellAssays
from tests.revision_v1.test_learner_cpu import _cfg
from tests.revision_v1.test_r1_68b_incremental_cell import scientific
from tests.revision_v1.test_stage4_cell import CAL, TinyTok, payload
from tests.revision_v1.tiny_base import TinyBase


class BatchDriftTests(unittest.TestCase):
    def test_per_position_scalar_parity_for_delta_controller_hardnull_and_single_site(self):
        definition = {"windows": [[2, 3, 4, 5], [3, 4, 5, 6, 7]], "expected_positions": 7}
        for delta, threshold, single_site in (
            (0, 1.1, False),
            (1, 1.1, False),
            (1, 1.1, True),
            (0, -0.1, False),
        ):
            with self.subTest(delta=delta, threshold=threshold, single_site=single_site):
                cfg = _cfg(null_threshold=threshold, single_site=single_site)
                cfg.fast = replace(cfg.fast, steps=0, delta_steps=delta)
                cap = build_adapter(
                    "R1_learned_ff",
                    TinyBase(),
                    Ledger(),
                    calibration=CAL,
                    synthetic=True,
                    revision_config=cfg,
                )
                cap.learner.cfg.null_threshold = threshold
                cap.learner.cfg.rare_overlap_min = None
                tok = TinyTok()
                for row in payload(2)["items"]:
                    cap.update_item(as_edit(row, tok))
                assays = CellAssays(cap, tok)
                before = cap.state_hash()
                scalar = assays.drift(definition)
                count = cap.cost_counters["selection_passes"]
                batched = batched_drift(assays, definition, batch_size=4)
                self.assertEqual(cap.cost_counters["selection_passes"] - count, 7)
                self.assertEqual(cap.state_hash(), before)
                for a, b in zip(scalar["rows"], batched["rows"], strict=True):
                    self.assertEqual(a["item_id"], b["item_id"])
                    np.testing.assert_allclose(
                        [a[k] for k in ("capoff", "original", "cap")],
                        [b[k] for k in ("capoff", "original", "cap")],
                        atol=2e-5,
                        rtol=2e-6,
                    )
                if threshold < 0:
                    for row in batched["rows"]:
                        self.assertEqual(row["cap"], row["capoff"])
                selections = [s for event in assays.events for s in event.get("selections", [])]
                self.assertEqual([r["prompt_len"] for r in selections], [1, 2, 3, 1, 2, 3, 4])

    def test_invalid_batch_and_inventory_refuse(self):
        cfg = _cfg()
        cap = build_adapter(
            "R1_learned_ff",
            TinyBase(),
            Ledger(),
            calibration=CAL,
            synthetic=True,
            revision_config=cfg,
        )
        with self.assertRaises(ValueError):
            PositionBatchReader(cap, batch_size=33)
        with self.assertRaises(ValueError):
            batched_drift(
                CellAssays(cap, TinyTok()), {"windows": [[2, 3]], "expected_positions": 2}
            )


class DriverTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(driver, "code_identity", return_value="a" * 64))
        self.enterContext(
            patch.object(driver, "driver_bindings", return_value={"fixture": "b" * 64})
        )
        driver.PAYLOAD_ROOT.mkdir(parents=True, exist_ok=True)
        self.resources = Path(tempfile.mkdtemp(prefix="r1-68c-", dir=driver.PAYLOAD_ROOT))
        self.output = driver.OUTPUT_ROOT / "r1_68c_cpu_tests" / uuid.uuid4().hex
        self.base = TinyBase()
        self.cfg = _cfg()
        self.cfg.fast = replace(self.cfg.fast, steps=0, delta_steps=0)

    def adapter(self):
        return build_adapter(
            "R1_learned_ff",
            self.base,
            Ledger(),
            calibration=CAL,
            synthetic=True,
            revision_config=self.cfg,
        )

    def fixture(self, profile):
        tok = TinyTok()
        data = payload(2, composition=True)
        data.update(mode=driver.MODE, banner=driver.BANNER)

        def prime(value, key=""):
            if isinstance(value, dict):
                for child, item in sorted(value.items()):
                    prime(item, child)
            elif isinstance(value, list):
                for item in value:
                    prime(item, key)
            elif isinstance(value, str) and key in {
                "prompt",
                "edit_prompt",
                "neighbour_prompt",
                "paraphrases",
                "questions",
                "answer",
                "edit_answer",
                "new_answer",
            }:
                tok.encode(" " + value + "\n" if "answer" in key else value)

        prime(data)
        cap = self.adapter()
        ref = driver.write_json(self.resources / f"payload-{profile}.json", data)
        manifest = {
            "schema_version": 1,
            "mode": driver.MODE,
            "banner": driver.BANNER,
            "test_fixture": True,
            "adapter_identity": cap.identity(),
            "code_sha256": "a" * 64,
            "payload": ref,
            "cell": {
                "condition": cap.condition,
                "dataset": "mquake",
                "realization": "tiny",
                "order": "0",
            },
            "checkpoints": [1, 2],
            "max_new": 4,
            "admission": {},
            "integrity_profile": profile,
            "integrity_batch_edits": 1,
            "integrity_driver_bindings": {"fixture": "b" * 64},
            "drift_batch_size": 4,
        }
        path = self.resources / f"recipe-{profile}.json"
        driver.write_json(path, manifest)
        return path, tok, cap

    def run_cell(self, fixture, **kwargs):
        path, tok, cap = fixture
        return driver.run_development_cell(
            path,
            driver.sha(path),
            cap,
            tok,
            output_root=self.output,
            resource_root=self.resources / "snapshots",
            **kwargs,
        )

    def reports(self, result):
        reports = {}
        for path in Path(result["run_dir"]).glob("attempt-*/checkpoint-*.receipt.json"):
            receipt = json.loads(path.read_text())
            reports[receipt["checkpoint"]] = driver.read_binding(receipt["report"])
        return reports

    def test_full_incremental_checkpoint_resume_scientific_parity_and_timers(self):
        full = self.run_cell(self.fixture("full"))
        fixture = self.fixture("incremental")
        self.run_cell(fixture, stop_after_checkpoint=1)
        inc = self.run_cell((fixture[0], fixture[1], self.adapter()), resume=True)
        self.assertEqual(inc["status"], "complete")
        a, b = self.reports(full), self.reports(inc)
        for cp in (1, 2):
            self.assertEqual(a[cp]["state_sha256"], b[cp]["state_sha256"])
            for key in ("history", "retention", "locality", "unseen"):
                self.assertEqual(scientific(a[cp][key]), scientific(b[cp][key]))
        for x, y in zip(
            a[2]["endpoints"]["drift"]["rows"], b[2]["endpoints"]["drift"]["rows"], strict=True
        ):
            np.testing.assert_allclose(
                [x[k] for k in ("capoff", "original", "cap")],
                [y[k] for k in ("capoff", "original", "cap")],
                atol=2e-5,
                rtol=2e-6,
            )
        timers = inc["detailed_phase_timers"]
        self.assertTrue(timers)
        readonly = [
            t
            for t in timers
            if t["phase"].split(":")[0] in ("immediate", "retention", "locality", "unseen", "drift")
        ]
        self.assertTrue(readonly)
        self.assertTrue(all(t["clone_seconds"] == t["restore_seconds"] == 0 for t in readonly))
        self.assertTrue(all(t["identity_verification_seconds"] == 0 for t in timers))
        self.assertTrue(all(t["identity_check_seconds"] > 0 for t in timers))
        self.assertTrue(
            all(t["identity_check_kind"] == "in_memory_structure_and_configuration" for t in timers)
        )
        self.assertEqual(
            [r["boundary"] for r in inc["boundary_identity_checks"]],
            ["attempt_start", "resume_after_restore", "checkpoint:2", "completion"],
        )
        self.assertTrue(all(t["file_write_seconds"] > 0 for t in timers))

    def test_readonly_mutation_aborts_without_checkpoint(self):
        fixture = self.fixture("incremental")
        original = driver.CellAssays.item

        def corrupt(assays, item):
            result = original(assays, item)
            assays.adapter.learner.store.records.clear()
            return result

        with patch.object(driver.CellAssays, "item", corrupt):
            with self.assertRaisesRegex(RuntimeError, "mutated checkpoint"):
                self.run_cell(fixture)
        self.assertFalse(list(self.output.glob("*/attempt-*/checkpoint-*.receipt.json")))
        failures = list(self.output.glob("*/attempt-*/failure.json"))
        self.assertEqual(len(failures), 1)
        self.assertGreater(json.loads(failures[0].read_text())["attempt_wall_seconds"], 0)

    def test_full_identity_only_at_boundaries_and_checkpoint_mismatch_refuses_receipt(self):
        fixture = self.fixture("incremental")
        cap = fixture[2]
        with patch.object(cap, "identity", wraps=cap.identity) as identity:
            result = self.run_cell(fixture)
        self.assertEqual(identity.call_count, 4)
        self.assertEqual(
            [r["boundary"] for r in result["boundary_identity_checks"]],
            ["attempt_start", "checkpoint:1", "checkpoint:2", "completion"],
        )
        self.assertGreater(result["boundary_identity_seconds"], 0)

        fixture = self.fixture("full")
        original = fixture[2].identity()
        changed = {**original, "base_sha256": "changed-in-place"}
        with patch.object(fixture[2], "identity", side_effect=[original, changed]):
            with self.assertRaisesRegex(ValueError, "immutable adapter identity changed"):
                self.run_cell(fixture)
        failed = [p.parent for p in self.output.glob("*/attempt-*/failure.json")]
        self.assertEqual(len(failed), 1)
        self.assertFalse(list(failed[0].glob("checkpoint-*.receipt.json")))

    def test_parameter_replacement_is_detected_within_phase(self):
        fixture = self.fixture("incremental")
        original = driver.CellAssays.item

        def corrupt(assays, item):
            result = original(assays, item)
            assays.adapter.learner.params = dict(assays.adapter.learner.params)
            return result

        with patch.object(driver.CellAssays, "item", corrupt):
            with self.assertRaisesRegex(RuntimeError, "immutable in-memory"):
                self.run_cell(fixture)
        self.assertFalse(list(self.output.glob("*/attempt-*/checkpoint-*.receipt.json")))

    def test_original_driver_scientific_results_and_receipt_chain_parity(self):
        legacy = types.ModuleType("r1_68d_legacy")
        source = driver.ROOT / "docs/tasks/R1-68d-driver-before.py"
        exec(compile(source.read_text(), str(source), "exec"), legacy.__dict__)
        for profile in ("full", "incremental"):
            with self.subTest(profile=profile):
                fixture = self.fixture(profile)
                with (
                    patch.object(legacy, "code_identity", return_value="a" * 64),
                    patch.object(legacy, "driver_bindings", return_value={"fixture": "b" * 64}),
                ):
                    old = legacy.run_development_cell(
                        fixture[0],
                        driver.sha(fixture[0]),
                        fixture[2],
                        fixture[1],
                        output_root=self.output / "before",
                        resource_root=self.resources / "old",
                    )
                new = self.run_cell((fixture[0], fixture[1], self.adapter()))
                a, b = self.reports(old), self.reports(new)
                for cp in (1, 2):
                    for key in (
                        "state_sha256",
                        "history",
                        "retention",
                        "locality",
                        "unseen",
                        "endpoints",
                    ):
                        self.assertEqual(scientific(a[cp][key]), scientific(b[cp][key]))
                for result in (old, new):
                    previous = None
                    for p in sorted(
                        Path(result["run_dir"]).glob("attempt-*/checkpoint-*.receipt.json")
                    ):
                        row = json.loads(p.read_text())
                        self.assertEqual(row["previous_receipt_sha256"], previous)
                        self.assertEqual(
                            row["receipt_sha256"],
                            driver.digest({k: v for k, v in row.items() if k != "receipt_sha256"}),
                        )
                        previous = row["receipt_sha256"]
                    self.assertEqual(result["last_receipt_sha256"], previous)


if __name__ == "__main__":
    unittest.main()
