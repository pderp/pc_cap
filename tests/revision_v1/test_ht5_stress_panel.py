"""HT-5 CPU execution, population pairing, recovery, resume and resource guards."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import uuid
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import numpy as np
from scripts import ht5_dev_cell as driver
from scripts import ht5_panel as panel
from scripts import ht5_probe_assays as probes
from scripts import ht5_recipes as recipes

from pccap.harness.ledger import Ledger
from pccap.revision_v1.stage4_adapters import build_adapter
from tests.revision_v1.test_learner_cpu import _cfg
from tests.revision_v1.test_stage4_cell import CAL, payload
from tests.revision_v1.tiny_base import TinyBase


class FixedTokenizer:
    def encode(self, text):
        if text == " new\n":
            return np.asarray([62, 63], np.int32)
        if text == "\n":
            return np.asarray([63], np.int32)
        # Stable bounded vocabulary; synthetic queries need no mutable dictionary.
        raw = sum((i + 1) * ord(c) for i, c in enumerate(text))
        return np.asarray([2 + raw % 59, 2 + (raw // 59) % 59], np.int32)

    def decode(self, ids):
        tokens = list(map(int, ids))
        if tokens == [62, 63]:
            return " new\n"
        return "".join(" new" if t == 62 else "\n" if t == 63 else "?" for t in tokens)


def measured(change=0.0, exact=0):
    facts = [
        {"item_id": str(i), "status": "ok", "es": int(i < exact), "gs": 0.0} for i in range(20)
    ]
    rows = [
        {
            "key": str(i),
            "item_id": str(i),
            "prompt_index": 0,
            "target_index": 0,
            "target_token": 2,
            "cap_nll": 1.0 + change,
            "original_nll": 2.0,
        }
        for i in range(20)
    ]
    return {"status": "complete", "facts": facts, "tokens": rows}


class ProbeContractTests(unittest.TestCase):
    def test_recovery_sustained_interval_and_censor(self):
        history = {
            20: measured(),
            60: measured(0.02),
            70: measured(),
            80: measured(),
            100: measured(),
        }
        self.assertEqual(probes.recovery(history)["lag_interval_updates"], [0, 10])
        history[80] = measured(0.02)
        self.assertEqual(probes.recovery(history)["lag_interval_updates"], [20, 40])
        history[100] = measured(0.02)
        self.assertTrue(probes.recovery(history)["right_censored"])
        self.assertEqual(probes.recovery({20: measured()})["status"], "provisional")
        self.assertEqual(
            probes.recovery(dict.fromkeys(probes.CADENCE, measured()))["lag_interval_updates"],
            [0, 0],
        )

    def test_failed_acquisition_stays_and_missing_nonfinite_refuse(self):
        out = probes.relative(measured(0.1), measured())
        self.assertEqual(len(out["fact_rows"]), 20)
        self.assertAlmostEqual(out["mean_positive_delta_nats"], 0.1)
        for bad in (measured(), measured()):
            bad["tokens"].pop()
            with self.assertRaises(ValueError):
                probes.relative(bad, measured())
        bad = measured()
        bad["tokens"][0]["cap_nll"] = float("nan")
        with self.assertRaises(FloatingPointError):
            probes.relative(bad, measured())
        self.assertFalse(
            probes.relative(measured(exact=1), measured(exact=2))["within_recovery_band"]
        )

    def test_sources_and_paired_schedules(self):
        contract, inventories = recipes.panel_data(recipes.binding(recipes.PANEL))
        self.assertEqual(len(contract["cells"]), 6)
        for ds, spec in contract["datasets"].items():
            for ids in spec["ordered_item_ids"].values():
                self.assertEqual(len([inventories[ds][i] for i in ids]), 100)
                self.assertEqual(ids[:20], spec["fixed_old_fact_probe_ids"])
            n = len(spec["difficult_item_ids"])
            self.assertEqual(
                set(spec["ordered_item_ids"]["clustered"][60 - n : 60]),
                set(spec["difficult_item_ids"]),
            )


class StressCellTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(driver, "code_identity", return_value="a" * 64))
        self.enterContext(
            patch.object(driver, "driver_bindings", return_value={"fixture": "b" * 64})
        )
        driver.PAYLOAD_ROOT.mkdir(parents=True, exist_ok=True)
        self.assets = Path(tempfile.mkdtemp(prefix="ht5-cpu-", dir=driver.PAYLOAD_ROOT))
        self.output = driver.OUTPUT_ROOT / "cpu_tests" / uuid.uuid4().hex
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
        data = payload(100, composition=False)
        data = {
            "mode": driver.MODE,
            "banner": driver.BANNER,
            "items": data["items"],
            "fixed_old_fact_probe_ids": [r["item_id"] for r in data["items"][:20]],
        }
        cap = self.adapter()
        data_ref = driver.write_json(self.assets / f"{profile}-payload.json", data)
        recipe = {
            "schema_version": 1,
            "recipe_family": "ht_stress_panel_v1",
            "mode": driver.MODE,
            "banner": driver.BANNER,
            "test_fixture": True,
            "adapter_identity": cap.identity(),
            "code_sha256": "a" * 64,
            "payload": data_ref,
            "cell": {
                "condition": cap.condition,
                "dataset": "mquake",
                "realization": "tiny",
                "order": "shuffled",
            },
            "checkpoints": probes.CADENCE,
            "max_new": 2,
            "admission": {},
            "integrity_profile": profile,
            "integrity_batch_edits": 16,
            "integrity_driver_bindings": {"fixture": "b" * 64},
        }
        ref = driver.write_json(self.assets / f"{profile}-recipe.json", recipe)
        return ref, cap, FixedTokenizer()

    def run_cell(self, fixture, **kwargs):
        ref, cap, tok = fixture
        return driver.run_development_cell(
            ref["path"],
            ref["sha256"],
            cap,
            tok,
            output_root=self.output,
            resource_root=self.assets / "snapshots",
            **kwargs,
        )

    def reports(self, result):
        reports = {}
        for path in Path(result["run_dir"]).glob("attempt-*/checkpoint-*.receipt.json"):
            receipt = json.loads(path.read_text())
            reports[receipt["checkpoint"]] = driver.read_binding(receipt["report"])
        return reports

    def test_tinybase_100_edit_full_incremental_resume_parity(self):
        full = self.run_cell(self.fixture("full"))
        fixture = self.fixture("incremental")
        paused = self.run_cell(fixture, stop_after_checkpoint=20)
        self.assertEqual(paused["status"], "paused_at_checkpoint")
        resumed = self.run_cell((fixture[0], self.adapter(), fixture[2]), resume=True)
        self.assertEqual(resumed["status"], "complete")
        a, b = self.reports(full), self.reports(resumed)
        self.assertEqual(sorted(a), probes.CADENCE)
        self.assertEqual(sorted(b), probes.CADENCE)
        for t in probes.CADENCE:
            self.assertEqual(a[t]["state_sha256"], b[t]["state_sha256"])
            self.assertEqual(a[t]["ht_relative"], b[t]["ht_relative"])
            self.assertEqual(len(b[t]["history"]), t)
            self.assertEqual(b[t]["ht_probes"]["planned_facts"], 20)
            self.assertEqual(b[t]["ht_probes"]["scored_positions"], 80)
        self.assertEqual(full["ht_recovery"], resumed["ht_recovery"])

    def test_nonfinite_probe_fails_without_checkpoint_and_keeps_cost(self):
        fixture = self.fixture("incremental")
        with patch.object(driver, "probe", side_effect=FloatingPointError("nonfinite probe")):
            with self.assertRaises(FloatingPointError):
                self.run_cell(fixture, stop_after_checkpoint=20)
        failures = list(self.output.glob("*/attempt-*/failure.json"))
        self.assertEqual(len(failures), 1)
        self.assertFalse(list(self.output.glob("*/attempt-*/checkpoint-*.receipt.json")))
        self.assertGreater(json.loads(failures[0].read_text())["attempt_wall_seconds"], 0)

    def test_readonly_state_mutation_refused_and_restored(self):
        fixture = self.fixture("full")
        original = driver.probe
        observed = {}

        def corrupt(assays, items):
            result = original(assays, items)
            observed["before"] = assays.adapter.state_hash()
            assays.adapter.learner.store.records.clear()
            return result

        with patch.object(driver, "probe", corrupt):
            with self.assertRaisesRegex(RuntimeError, "mutated checkpoint"):
                self.run_cell(fixture, stop_after_checkpoint=20)
        self.assertEqual(fixture[1].state_hash(), observed["before"])


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.output = driver.OUTPUT_ROOT / "cpu_tests" / uuid.uuid4().hex
        self.output.mkdir(parents=True)

    def test_unknown_spend_and_start_tamper_refuse(self):
        start = driver.write_json(self.output / "000000.start.json", {"intent_id": "000000"})
        with self.assertRaisesRegex(RuntimeError, "unclosed"):
            panel.spent(self.output)
        driver.write_json(
            self.output / "000000.result.json",
            {"intent_id": "000000", "start_sha256": start["sha256"], "charged_wall_seconds": 3.0},
        )
        self.assertEqual(panel.spent(self.output), 3.0)

    def test_watchdog_charges_timeout_and_memory_guard(self):
        result = panel.supervise(
            [sys.executable, "-c", "import time; time.sleep(5)"],
            allowance=0.1,
            output=self.output / "child.log",
            env=os.environ.copy(),
            memory=lambda: 10 * 1024**3,
        )
        self.assertEqual(result["reason"], "budget_timeout")
        self.assertNotEqual(result["returncode"], 0)
        with self.assertRaisesRegex(RuntimeError, "3 GiB"):
            panel.supervise(
                [sys.executable, "-c", "pass"],
                allowance=1,
                output=self.output / "never.log",
                env=os.environ.copy(),
                memory=lambda: 0,
            )


if __name__ == "__main__":
    unittest.main()
