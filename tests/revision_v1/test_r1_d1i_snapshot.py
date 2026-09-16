"""R1-D1i metadata-only rebind and fail-closed provenance checks."""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from unittest.mock import patch

from scripts import r1_d1i_register_v6 as register


class SnapshotRegisterTests(unittest.TestCase):
    def setUp(self):
        self.current = json.loads(register.REGISTER.read_text())
        self.parent = json.loads(register.PARENT.read_text())
        self.raw = register.SNAPSHOT.read_bytes()

    def test_only_binding_and_identity_metadata_change(self):
        changed = {"schema_version", "name", "task", "status", "bindings_sha256"}
        for key in set(self.parent) - changed:
            self.assertEqual(self.current[key], self.parent[key], key)
        self.assertNotIn(str(register.LIVE), self.current["bindings_sha256"])
        self.assertEqual(
            set(self.current["decision_rows"]), {f"DEC-{i:03d}" for i in range(43, 51)}
        )
        self.assertEqual(register.verify_register(self.current), self.current)

    def test_snapshot_integrity_and_policy_row_change_refused(self):
        kwargs = {"live_path": register.LIVE, "producer_ref": self.current["rebinding"]["producer"]}
        with self.assertRaisesRegex(ValueError, "snapshot bytes"):
            register.rebind(
                self.parent,
                self.current["rebinding"]["parent_v5"],
                self.current["decisions_snapshot"],
                self.raw + b"\n",
                **kwargs,
            )
        altered = self.raw.replace(
            self.parent["acceptance"]["decision_row"].encode(),
            (self.parent["acceptance"]["decision_row"] + " changed").encode(),
        )
        ref = {**self.current["decisions_snapshot"], "sha256": hashlib.sha256(altered).hexdigest()}
        with self.assertRaisesRegex(ValueError, "policy changed"):
            register.rebind(
                self.parent, self.current["rebinding"]["parent_v5"], ref, altered, **kwargs
            )

    def test_policy_mutation_and_nondeccision_hash_failure_refused(self):
        altered = copy.deepcopy(self.current)
        altered["counts"]["mquake"]["candidate_subjects"] += 1
        with self.assertRaisesRegex(ValueError, "metadata-only"):
            register.verify_register(altered)
        with patch.object(
            register, "binding_errors", return_value=[{"path": "non-decision fixture"}]
        ):
            with self.assertRaisesRegex(ValueError, "binding mismatch"):
                register.verify_register(self.current)

    def test_live_decisions_are_not_a_dependency(self):
        original = register.binding_errors

        def reject_live(bindings):
            self.assertNotIn(str(register.LIVE), bindings)
            return original(bindings)

        with patch.object(register, "binding_errors", side_effect=reject_live):
            register.verify_register(self.current)
        self.assertEqual(self.current["counts"]["mquake"]["headroom_subjects"], 168)
        self.assertEqual(
            self.current["counts"]["mquake"]["first_subject_loss_count_causing_shortfall"], 169
        )


if __name__ == "__main__":
    unittest.main()
