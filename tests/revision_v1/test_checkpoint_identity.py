"""The reader's MLP layers are list-indexed; hashing must preserve every layer."""

import tempfile
import unittest
from pathlib import Path

import numpy as np

from pccap.revision_v1.checkpoint_identity import checkpoint_tree
from pccap.revision_v1.reader import params_hash
from pccap.revision_v1.stage4_cell import ROOT


class CheckpointIdentityTests(unittest.TestCase):
    def test_distinct_list_layers_survive_with_exact_hash(self):
        value = {"reader": {"mlp": [{"w": np.float32([1, 2])}, {"w": np.float32([3, 4])}]}}
        with tempfile.TemporaryDirectory(dir=ROOT.parent / "assets") as td:
            p = Path(td) / "weights.npz"
            np.savez(
                p,
                **{
                    "['reader']['mlp'][0]['w']": value["reader"]["mlp"][0]["w"],
                    "['reader']['mlp'][1]['w']": value["reader"]["mlp"][1]["w"],
                },
            )
            loaded = checkpoint_tree(p)
            self.assertEqual(params_hash(loaded), params_hash(value))
            self.assertEqual(len(loaded["reader"]["mlp"]), 2)

    def test_gaps_and_bad_key_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT.parent / "assets") as td:
            for i, key in enumerate(("['r'][1]['w']", "['r'][-1]", "garbage")):
                p = Path(td) / f"bad{i}.npz"
                np.savez(p, **{key: np.float32([1])})
                with self.assertRaises(ValueError):
                    checkpoint_tree(p)

    def test_nonfinite_or_wrong_dtype_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT.parent / "assets") as td:
            for i, value in enumerate((np.float32([np.nan]), np.int32([1]))):
                p = Path(td) / f"bad{i}.npz"
                np.savez(p, **{"['r']": value})
                with self.assertRaises(ValueError):
                    checkpoint_tree(p)
