"""Development firewall, payload capacity and actual TinyBase checkpoint/resume tests."""

import copy
import json
import tempfile
import unittest
import uuid
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import numpy as np
from scripts.r1_64_dev_payload import payload_from_documents, unique_stream

from pccap.harness.ledger import Ledger
from pccap.revision_v1 import development_cell as dev
from pccap.revision_v1.stage4_adapters import build_adapter
from pccap.revision_v1.stage4_cell import sha, write_json
from tests.revision_v1.test_learner_cpu import _cfg
from tests.revision_v1.test_stage4_cell import CAL, TinyTok, payload
from tests.revision_v1.tiny_base import TinyBase


class DevelopmentTests(unittest.TestCase):
    def fixture(self):
        dev.PAYLOAD_ROOT.mkdir(parents=True, exist_ok=True)
        resources = Path(tempfile.mkdtemp(prefix="tiny-r11-", dir=dev.PAYLOAD_ROOT))
        tok = TinyTok()
        base = TinyBase()
        cfg = _cfg()
        cfg.fast = replace(cfg.fast, steps=0, delta_steps=0)

        def adapter():
            return build_adapter(
                "R1_learned_ff",
                base,
                Ledger(),
                calibration=CAL,
                synthetic=True,
                revision_config=cfg,
            )

        cap = adapter()
        p = payload(2, composition=False)
        p["endpoints"]["near_miss"]["rows"] = []
        p["endpoints"]["revision"]["rows"] = []
        p.update(mode=dev.MODE, banner=dev.BANNER)
        for r in p["items"]:
            tok.encode(r["prompt"])
            tok.encode(" " + r["answer"] + "\n")
            for q in r["paraphrases"]:
                tok.encode(q)
        binding = write_json(resources / "payload.json", p)
        m = {
            "schema_version": 1,
            "mode": dev.MODE,
            "banner": dev.BANNER,
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
        }
        path = resources / "recipe.json"
        write_json(path, m)
        return resources, tok, base, adapter, cap, p, m, path

    def test_tiny_execution_resume_stamps_and_preserves_all_prior_files(self):
        resources, tok, base, factory, cap, p, m, path = self.fixture()
        output = dev.OUTPUT_ROOT / "tiny_tests" / uuid.uuid4().hex
        snapshots = resources / "snapshots"
        with patch.object(dev, "code_identity", return_value="a" * 64):
            first = dev.run_development_cell(
                path,
                sha(path),
                cap,
                tok,
                output_root=output,
                resource_root=snapshots,
                stop_after_checkpoint=1,
            )
            prior = {
                p: sha(p) for root in (output, snapshots) for p in root.rglob("*") if p.is_file()
            }
            result = dev.run_development_cell(
                path,
                sha(path),
                factory(),
                tok,
                output_root=output,
                resource_root=snapshots,
                resume=True,
            )
        self.assertEqual(result["status"], "complete")
        self.assertGreater(base.calls["forward"], 0)
        self.assertEqual(first["completed_checkpoint"], 1)
        self.assertTrue(all(sha(p) == h for p, h in prior.items()))
        for root in (output, snapshots):
            for p in root.rglob("*.json"):
                d = json.loads(p.read_text())
                self.assertEqual(d["mode"], dev.MODE)
                self.assertEqual(d["banner"], dev.BANNER)

    def test_admission_refused_before_payload_read(self):
        resources, tok, base, factory, cap, p, m, path = self.fixture()
        for flag in (
            "lead_approved",
            "protocol_frozen",
            "condition_admitted",
            "launch_authorized",
            "unknown",
        ):
            m2 = {
                **m,
                "admission": {flag: True},
                "payload": {"path": "/DO-NOT-OPEN", "sha256": "0" * 64},
            }
            q = resources / (flag + ".json")
            write_json(q, m2)
            with (
                patch.object(dev, "code_identity", return_value="a" * 64),
                self.assertRaises(PermissionError),
            ):
                dev.load_development_cell(q, sha(q))
        with self.assertRaises(PermissionError):
            dev.load_development_cell(path, sha(path), allow_sealed=True)

    def test_real_identity_cannot_claim_tiny_fixture(self):
        resources, tok, base, factory, cap, p, m, path = self.fixture()
        m["adapter_identity"]["base_sha256"] = "real-base"
        with self.assertRaises(ValueError):
            dev.validate_development_payload(m, p)

    def test_300_item_contract_and_missing_challenges(self):
        def rows(start, n):
            return [
                {
                    "item_id": str(i),
                    "fact_id": str(i),
                    "subject": str(i),
                    "dataset": "zsre",
                    "prompt": str(i) + "?",
                    "answer": "a",
                    "paraphrases": ["p" + str(i)],
                }
                for i in range(start, start + n)
            ]

        d = {"items": rows(0, 300), "unrelated_prompts": ["loc"]}
        t = {"items": rows(1000, 1200)}
        ch = {"near_neighbour": {"items": []}, "temporal_correction": {"items": []}}
        p = payload_from_documents("zsre", d, t, ch, [], np.arange(128), 300, n_windows=1)
        m = {
            "schema_version": 1,
            "mode": dev.MODE,
            "cell": {"condition": "R1_learned_ff", "dataset": "zsre", "realization": 0, "order": 0},
            "checkpoints": [100, 300],
            "max_new": 32,
        }
        dev.validate_development_payload(m, p)
        self.assertEqual(len(p["items"]), 300)
        self.assertEqual(len(p["endpoints"]["revision"]["expected_ids"]), 50)
        self.assertEqual(p["endpoints"]["revision"]["rows"], [])
        bad = copy.deepcopy(m)
        bad["checkpoints"] = [100, 300, 1000]
        with self.assertRaises(ValueError):
            dev.validate_development_payload(bad, p)

    def test_shortfall_never_fills_from_fresh_inventory(self):
        d = {"items": [{"item_id": str(i), "subject": str(i)} for i in range(100)]}
        t = {"items": [{"item_id": str(i), "subject": str(i)} for i in range(100, 600)]}
        with self.assertRaises(ValueError):
            unique_stream(d, t, 1000, 100)
