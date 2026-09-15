"""Whole-cell CPU parity, crash accounting, and mutation-inventory refusals."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
import uuid
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import numpy as np
from scripts import r1_68b_dev_cell as driver
from scripts.r1_68b_integrity_runtime import DurablePhaseJournal, IndexedAdapter

from pccap.harness.ledger import Ledger
from pccap.revision_v1.adapt import adapt_record
from pccap.revision_v1.analysis import digest
from pccap.revision_v1.stage4_adapters import build_adapter
from tests.revision_v1.test_learner_cpu import _cfg, _support
from tests.revision_v1.test_stage4_cell import CAL, TinyTok, payload
from tests.revision_v1.tiny_base import TinyBase


def scientific(value):
    if isinstance(value, dict):
        return {
            key: scientific(item)
            for key, item in value.items()
            if key
            not in {
                "wall_seconds",
                "phase_wall_seconds",
                "operation_seconds",
                "ledger_delta",
                "cost",
                "returned_cost",
                "integrity_root",
            }
        }
    if isinstance(value, list):
        return [scientific(item) for item in value]
    return value


class IncrementalCellTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(driver, "code_identity", return_value="a" * 64))
        self.enterContext(
            patch.object(driver, "driver_bindings", return_value={"fixture": "b" * 64})
        )
        driver.PAYLOAD_ROOT.mkdir(parents=True, exist_ok=True)
        self.resources = Path(tempfile.mkdtemp(prefix="r1-68b-", dir=driver.PAYLOAD_ROOT))
        self.output = driver.OUTPUT_ROOT / "r1_68b_cpu_tests" / uuid.uuid4().hex
        self.base = TinyBase()
        self.config = _cfg()
        self.config.fast = replace(self.config.fast, steps=0, delta_steps=0)

    def adapter(self):
        return build_adapter(
            "R1_learned_ff",
            self.base,
            Ledger(),
            calibration=CAL,
            synthetic=True,
            revision_config=self.config,
        )

    def fixture(self, profile, *, batch=16):
        tok = TinyTok()
        data = payload(2, composition=True)
        data.update(mode=driver.MODE, banner=driver.BANNER)

        # Bind tokens before either profile sees outcomes or retry order.
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
        binding = driver.write_json(self.resources / f"payload-{profile}.json", data)
        manifest = {
            "schema_version": 1,
            "mode": driver.MODE,
            "banner": driver.BANNER,
            "test_fixture": True,
            "adapter_identity": cap.identity(),
            "code_sha256": "a" * 64,
            "payload": binding,
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
            "integrity_batch_edits": batch,
            "integrity_driver_bindings": {"fixture": "b" * 64},
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
        run = Path(result["run_dir"])
        reports = {}
        previous = None
        receipts = sorted(
            run.glob("attempt-*/checkpoint-*.receipt.json"),
            key=lambda path: json.loads(path.read_text())["checkpoint"],
        )
        for path in receipts:
            receipt = json.loads(path.read_text())
            self.assertEqual(
                receipt["receipt_sha256"],
                digest({key: value for key, value in receipt.items() if key != "receipt_sha256"}),
            )
            self.assertEqual(receipt["previous_receipt_sha256"], previous)
            self.assertEqual(driver.sha(receipt["snapshot"]["path"]), receipt["snapshot"]["sha256"])
            report = driver.read_binding(receipt["report"])
            self.assertEqual(report["state_sha256"], receipt["state_sha256"])
            if "journal" in receipt:
                DurablePhaseJournal.verify(path.parent / "phases", receipt["journal"])
            reports[receipt["checkpoint"]] = {
                "report": scientific(report),
                "receipt_scientific": {
                    "checkpoint": receipt["checkpoint"],
                    "state_sha256": receipt["state_sha256"],
                },
            }
            previous = receipt["receipt_sha256"]
        return reports

    def test_whole_cell_all_endpoints_and_mid_checkpoint_resume_parity(self):
        full = self.run_cell(self.fixture("full"))
        incremental = self.fixture("incremental")
        original = driver.CellAssays.locality
        calls = 0

        def interrupt_second_checkpoint(assays, definition):
            nonlocal calls
            calls += 1
            result = original(assays, definition)
            if calls == 2:
                raise KeyboardInterrupt("controlled mid-checkpoint interruption after charged work")
            return result

        with patch.object(driver.CellAssays, "locality", interrupt_second_checkpoint):
            with self.assertRaisesRegex(KeyboardInterrupt, "controlled"):
                self.run_cell(incremental)
        # Cell names bind a manifest hash, not the integrity profile text.
        run = next(
            path.parent
            for path in self.output.glob("*/cell.json")
            if json.loads(path.read_text())["integrity_profile"] == "incremental"
        )
        prior = {path: driver.sha(path) for path in run.rglob("*") if path.is_file()}
        charged = DurablePhaseJournal.verify(run / "attempt-0000/phases")
        self.assertTrue(any(row["status"] == "error" and row["ledger_delta"] for row in charged))
        self.assertTrue((run / "attempt-0000/checkpoint-1.receipt.json").exists())
        self.assertFalse((run / "attempt-0000/checkpoint-2.receipt.json").exists())
        resumed = self.run_cell((incremental[0], incremental[1], self.adapter()), resume=True)
        self.assertEqual(resumed["status"], "complete")
        self.assertEqual(self.reports(full), self.reports(resumed))
        self.assertTrue(all(driver.sha(path) == value for path, value in prior.items()))
        self.assertEqual(resumed["phase_timer_summary"]["edit"]["count"], 1)
        self.assertEqual(resumed["prior_attempt_timer_summary"]["locality"]["errors"], 1)
        last = self.reports(resumed)[2]["report"]
        self.assertEqual(set(last["endpoints"]), {"near_miss", "revision", "composition", "drift"})
        self.assertEqual(len(last["endpoints"]["composition"]["rows"]), 1)

    def test_hard_interruption_unclosed_intent_refuses_before_model_work(self):
        fixture = self.fixture("incremental")
        first = self.run_cell(fixture, stop_after_checkpoint=1)
        directory = Path(first["attempt_dir"]) / "phases"
        index = len(list(directory.glob("*.receipt.json")))
        driver.write_json(directory / f"batch-{index:06d}.intent.json", {"incomplete": True})
        calls_before = dict(self.base.calls)
        with self.assertRaisesRegex(ValueError, "incomplete journal"):
            self.run_cell((fixture[0], fixture[1], self.adapter()), resume=True)
        self.assertEqual(calls_before, self.base.calls)
        self.assertFalse((Path(first["run_dir"]) / "attempt-0001").exists())

    def test_record_mutations_rebuild_restore_and_bypass_refusal(self):
        adapter = IndexedAdapter(self.adapter())
        for index in range(2):
            adapt_record(adapter.learner, _support(index), adapter.cfg.fast)
        store = adapter.tracked_store()
        store.set_code("s0", np.ones_like(store.get("s0").code))
        store.set_delta("s0", np.zeros((1, 3, adapter.base.d), np.float32))
        store.set_delta("s0", None)
        adapt_record(adapter.learner, _support(3, fact="f0", rev=2), adapter.cfg.fast)
        self.assertFalse(store.get("s0").active)
        store.remove("s3", restore="s0")
        store.rebuild_keys(lambda ids: np.ones(store.dk, np.float32), store.encoder_version)
        adapter.verify()
        names = {row["method"] for row in adapter.drain_mutations()}
        self.assertTrue(
            {"add", "set_code", "set_delta", "supersede", "remove", "rebuild_keys"} <= names
        )
        before = adapter.root()
        state = adapter.export_state().clone()
        adapter.import_state(state)
        self.assertEqual(adapter.verify(), before)
        adapter.store.get("s0").active = False
        with self.assertRaisesRegex(RuntimeError, "full recomputation"):
            adapter.verify()

    def test_bypassed_query_mutation_prevents_checkpoint_receipt(self):
        fixture = self.fixture("incremental")
        original = driver.CellAssays.item

        def corrupt(assays, item):
            row = original(assays, item)
            assays.adapter.store.records[0].active = False
            return row

        with patch.object(driver.CellAssays, "item", corrupt):
            with self.assertRaisesRegex(RuntimeError, "full recomputation"):
                self.run_cell(fixture)
        self.assertFalse(list(self.output.glob("*/attempt-*/checkpoint-*.receipt.json")))

    def test_profile_and_binding_refusals(self):
        path, _, _ = self.fixture("full")
        manifest = json.loads(path.read_text())
        self.assertEqual(
            driver.profile_config(
                {key: value for key, value in manifest.items() if key != "integrity_profile"}
            )[0],
            "full",
        )
        for changes in (
            {"integrity_profile": "typo"},
            {"integrity_batch_edits": True},
            {"integrity_driver_bindings": {}},
            {"integrity_profile": "incremental", "cell": {"condition": "v0_stable"}},
        ):
            with self.assertRaises(ValueError):
                driver.profile_config({**manifest, **changes})

    def test_torn_batch_and_receipt_path_refuse(self):
        directory = self.output / "journal"
        directory.parent.mkdir(parents=True)
        journal = DurablePhaseJournal(directory, batch_edits=1)
        journal.before_phase("edit:1", {"learning": {}})
        journal.add({"phase": "edit:1", "status": "ok"})
        receipt = journal.receipt()
        self.assertEqual(len(DurablePhaseJournal.verify(directory, receipt)), 1)
        bad = copy.deepcopy(receipt)
        bad["batches"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "prefix mismatch"):
            DurablePhaseJournal.verify(directory, bad)
        other = self.output / "torn"
        other.mkdir()
        for path in directory.iterdir():
            raw = b"{" if path.name.endswith(".receipt.json") else path.read_bytes()
            with (other / path.name).open("xb") as stream:
                stream.write(raw)
        with self.assertRaises(ValueError):
            DurablePhaseJournal.verify(other)


if __name__ == "__main__":
    unittest.main()
