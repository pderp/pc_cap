"""Dry assembler refuses missing identities, launch flags and frozen output paths."""

import tempfile
import unittest
from pathlib import Path

from scripts.r1_63_freeze_package import gate_inventory, verify_bindings, write_candidate

from pccap.revision_v1.stage4_cell import ROOT, sha


class FreezeCandidateTests(unittest.TestCase):
    def test_missing_or_wrong_hash_refused(self):
        with tempfile.TemporaryDirectory(dir=ROOT.parent / "assets") as td:
            p = Path(td) / "source"
            p.write_text("one")
            verify_bindings({str(p): sha(p)})
            with self.assertRaises(ValueError):
                verify_bindings({str(p): "0" * 64})
            with self.assertRaises(ValueError):
                verify_bindings({str(Path(td) / "absent"): "0" * 64})

    def test_sealed_reference_refused_without_open(self):
        with self.assertRaises(PermissionError):
            verify_bindings({str(ROOT / "manifests" / "confirm" / "DO-NOT-OPEN.json"): "0" * 64})

    def test_frozen_filename_and_authorization_refused(self):
        c = {
            "freeze_ready": False,
            "draw_authorized": False,
            "launch_authorized": False,
            "bindings_sha256": {},
        }
        with self.assertRaises(PermissionError):
            write_candidate(ROOT / "manifests/frozen.json", c)
        c["launch_authorized"] = True
        with self.assertRaises(PermissionError):
            write_candidate(ROOT / "manifests/revision_v1/freeze_candidate_test.json", c)

    def test_gate_inventory_complete_or_refuse(self):
        text = "\n".join(f"| U{i:02d} scope | Open |" for i in range(1, 19))
        self.assertEqual(len(gate_inventory(text)), 18)
        with self.assertRaises(ValueError):
            gate_inventory(text.splitlines()[0])
