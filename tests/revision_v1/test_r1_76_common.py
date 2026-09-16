"""R1-76 common outside identity, source capacity, exact occupancy and query purity."""

from __future__ import annotations

import copy
import json
import unittest
import uuid
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import patch

from scripts import r1_76_unseen_common as common

from pccap.harness.ledger import Ledger
from pccap.revision_v1.stage4_adapters import build_adapter
from tests.revision_v1.test_learner_cpu import _cfg
from tests.revision_v1.test_stage4_cell import CAL, TinyTok, payload
from tests.revision_v1.tiny_base import TinyBase


class CommonTests(unittest.TestCase):
    def fixture(self):
        data = payload(3)
        p = common.choose_population(
            "mquake",
            data["items"],
            data["endpoints"]["unseen"]["rows"],
            [],
            checkpoints=[1, 2, 3],
            outside_n=1,
            test_fixture=True,
        )
        cfg = _cfg()
        cfg.fast = replace(cfg.fast, steps=0, delta_steps=0)
        adapter = build_adapter(
            "R1_learned_ff",
            TinyBase(),
            Ledger(),
            calibration=CAL,
            synthetic=True,
            revision_config=cfg,
        )
        tok = TinyTok()
        for row in [*p["edits"], *p["outside"]]:
            tok.encode(row["prompt"])
            if row.get("answer"):
                tok.encode(" " + row["answer"] + "\n")
        output = common.ROOT / "results/R1/r1_76_cpu_tests" / uuid.uuid4().hex
        return adapter, tok, p, output

    def test_fixed_population_one_stream_three_checkpoints_and_query_purity(self):
        a, t, p, out = self.fixture()
        result = common.run_population(a, t, p, out, test_fixture=True, max_new=4)
        self.assertEqual(result["attempted_edits"], 3)
        rows = [json.loads((out / f"checkpoint-{k}.json").read_text()) for k in (1, 2, 3)]
        self.assertEqual(len({r["query_population_sha256"] for r in rows}), 1)
        self.assertEqual(len({r["report"]["requested_item_ids_sha256"] for r in rows}), 1)
        self.assertEqual(len({r["report"]["pool_query_metadata_sha256"] for r in rows}), 1)
        self.assertEqual([r["report"]["edited_items"] for r in rows], [1, 2, 3])
        self.assertTrue(all(r["report"]["state_restored"] for r in rows))
        self.assertEqual(a.state_hash(), rows[-1]["state_sha256"])
        self.assertEqual(len(list(out.glob("edit-*.json"))), 3)
        self.assertEqual(len(result["paired_occupancy"]), 2)

    def test_largest_future_edit_overlap_refuses_before_output_or_model_work(self):
        a, t, p, out = self.fixture()
        p["edits"][-1]["subject"] = p["outside"][0]["subject"].upper()
        calls = copy.deepcopy(a.base.calls)
        with self.assertRaisesRegex(ValueError, "overlapping"):
            common.run_population(a, t, p, out, test_fixture=True, max_new=4)
        self.assertEqual(a.base.calls, calls)
        self.assertFalse(out.exists())

    def test_shortfall_no_fallback_and_exact_query_training_exclusion(self):
        data = payload(3)
        with self.assertRaisesRegex(ValueError, "need 1100"):
            common.choose_population("mquake", data["items"], [], [])
        training = [
            {
                **data["items"][0],
                "item_id": "trained",
                "fact_id": "trained",
                "subject": "trained",
                "prompt": "train?",
                "locality_prompts": ["outside?"],
            }
        ]
        with self.assertRaisesRegex(ValueError, "only 3"):
            common.choose_population(
                "mquake",
                data["items"],
                data["endpoints"]["unseen"]["rows"],
                training,
                checkpoints=[1, 2, 3],
                outside_n=1,
                test_fixture=True,
            )

    def test_missing_occupancy_is_not_reported_as_target_rate(self):
        a, t, p, out = self.fixture()
        original = a.update_item

        def update(item):
            if item.item_id == p["edits"][0]["item_id"]:
                return original(item)
            return SimpleNamespace(
                code="rejected_no_improvement", codes=[], cost=SimpleNamespace(as_dict=lambda: {})
            )

        with patch.object(a, "update_item", side_effect=update):
            r = common.run_population(a, t, p, out, test_fixture=True, max_new=4)
        self.assertEqual(r["checkpoints"][-1]["exact_size_status"], "unavailable")
        self.assertIsNone(r["checkpoints"][-1]["exact_size_false_fire_rate"])
        self.assertTrue(all(x["delta_fire_rate"] is None for x in r["paired_occupancy"]))

    def test_readonly_mutation_stops_and_retains_failure(self):
        a, t, p, out = self.fixture()
        original = common.CellAssays.unseen

        def corrupt(assays, *args, **kwargs):
            r = original(assays, *args, **kwargs)
            assays.adapter.learner.store.records.clear()
            return r

        with patch.object(common.CellAssays, "unseen", corrupt):
            with self.assertRaisesRegex(RuntimeError, "mutated memory"):
                common.run_population(a, t, p, out, test_fixture=True, max_new=4)
        self.assertTrue((out / "failure.json").is_file())
        self.assertFalse((out / "checkpoint-1.json").exists())
        self.assertFalse((out / "result.json").exists())

    def test_repository_capacity_and_training_prefix_proof(self):
        for ds in ("zsre", "counterfact"):
            p = common.prepare(ds)
            self.assertEqual(len(p["edits"]), 1000)
            self.assertEqual(len(p["outside"]), 100)
            self.assertEqual(
                p["training_prefix_counts"], {"zsre": 1000, "counterfact": 1000, "mquake": 500}
            )
            common.validate_population(p)
        with self.assertRaisesRegex(ValueError, "only 100.*need 1100"):
            common.prepare("mquake")


if __name__ == "__main__":
    unittest.main()
