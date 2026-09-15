"""Snapshot symlinks become exact regular files; reuse never overwrites resources."""

import tempfile
import unittest
from pathlib import Path

from scripts.r1_64_materialize_base import materialize_base

from pccap.revision_v1.stage4_cell import ROOT, sha


class MaterializationTests(unittest.TestCase):
    def test_external_blob_links_materialize_and_reuse(self):
        with tempfile.TemporaryDirectory(dir=ROOT.parent / "assets") as td:
            root = Path(td)
            source = root / "source"
            source.mkdir()
            blobs = root / "blobs"
            blobs.mkdir()
            files = {}
            for name in ("config.json", "model.safetensors", "tokenizer.json"):
                blob = blobs / name
                blob.write_bytes(name.encode())
                (source / name).symlink_to(blob)
                files[name] = sha(blob)
            b = {"path": str(source), "files": files}
            out = materialize_base(b, root / "copies")
            before = {p: sha(p) for p in Path(out["path"]).iterdir()}
            self.assertTrue(all(not p.is_symlink() for p in before))
            self.assertEqual(materialize_base(b, root / "copies"), out)
            self.assertTrue(all(sha(p) == h for p, h in before.items()))

    def test_bad_source_hash_refused(self):
        with tempfile.TemporaryDirectory(dir=ROOT.parent / "assets") as td:
            p = Path(td)
            files = {}
            for name in ("config.json", "model.safetensors", "tokenizer.json"):
                (p / name).write_text(name)
                files[name] = "0" * 64
            with self.assertRaises(ValueError):
                materialize_base({"path": str(p), "files": files}, p / "copies")
