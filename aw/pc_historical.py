"""Explicit, read-only source resolution for completed pre-PC-9/10 experiments.

Only the five originals named in the staged patch manifests and the explicitly
bound pre-repair v5 harm driver may resolve to the preserved archive. A hash
mismatch elsewhere is fatal. This verifies historical
inputs; it does not certify that present-day execution reproduces those runs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import FunctionType, ModuleType

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "docs/tasks/PC-9-candidate"


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


class Sources:
    def __init__(self, root=ROOT, stage=STAGE):
        self.root, self.stage = Path(root), Path(stage)
        self.allowed = {}
        self.bindings = {}
        self.substitutions = {}
        for name in ("sources.json", "reporting-sources.json"):
            path = self.stage / name
            self.bindings[str(path)] = sha(path)
            for rel, entry in json.loads(path.read_bytes()).items():
                if entry["before_sha256"] is not None:
                    self.allowed[rel] = entry["before_sha256"]
        # Separate, documented owner repair: the v5 harm driver added a missing
        # smoke key after it had finished and written the measured report.
        # Preserved from commit 35d9866; exact recorded pre-repair digest only.
        self.allowed["aw/pc_v1_harm.py"] = (
            "e32152cbac89fadbd75a49a1fd9878e8a2687cbda200daa561f1b2bbc0a9b9e5"
        )

    def resolve(self, name, expected):
        path = Path(name)
        path = path if path.is_absolute() else self.root / path
        if path.exists() and sha(path) == expected:
            self.bindings[str(path)] = expected
            return path
        try:
            rel = str(path.relative_to(self.root))
        except ValueError:
            raise ValueError(f"external input identity differs: {path}") from None
        if self.allowed.get(rel) != expected:
            raise ValueError(f"unapproved source drift: {path}")
        archived = self.stage / "old" / path.name
        if not archived.is_file() or sha(archived) != expected:
            raise ValueError(f"missing or changed historical source: {archived}")
        self.bindings[str(archived)] = expected
        self.substitutions[str(path)] = dict(path=str(archived), sha256=expected)
        return archived

    def historical_sha(self, name):
        path = Path(name)
        try:
            rel = str(path.relative_to(self.root))
        except ValueError:
            return sha(path)
        expected = self.allowed.get(rel)
        return sha(self.resolve(path, expected)) if expected else sha(path)

    def check(self, entries):
        for name, expected in entries.items():
            self.resolve(name, expected)

    def verify_unchanged(self):
        for name, expected in self.bindings.items():
            if sha(name) != expected:
                raise ValueError(f"evidence changed during read: {name}")

    def module(self, name):
        rel = "aw/" + name + ".py"
        path = self.resolve(rel, self.allowed[rel])
        module = ModuleType("historical_" + name)
        # Keep original ROOT/path semantics; sha resolves only approved originals.
        module.__file__ = str(self.root / rel)
        exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
        module.sha = self.historical_sha
        return module


def bind(fn, **changes):
    scope = dict(fn.__globals__)
    scope.update(changes)
    result = FunctionType(fn.__code__, scope, fn.__name__, fn.__defaults__, fn.__closure__)
    result.__kwdefaults__ = fn.__kwdefaults__
    return result


class SourceRoot:
    """Audit-only ROOT / name resolver; all other paths retain their real location."""

    def __init__(self, sources, expected):
        self.sources, self.expected = sources, expected

    def __truediv__(self, name):
        if str(name) in self.expected:
            return self.sources.resolve(name, self.expected[str(name)])
        return self.sources.root / name
