"""Install proposed function bodies in this test process only; no source writes."""

import hashlib
import json
import types
from pathlib import Path

from scripts import r1_77b_sealed_backend as backend
from scripts.r1_77d_prepare import proposed_sources

from pccap.revision_v1 import stage4_cell as core


def install(monkeypatch):
    if hasattr(core, "registered_checkpoints"):
        root = Path(__file__).resolve().parents[2]
        record = json.loads((root / "logs/r1_round24/r1-77d-patch.json").read_text())
        identities = dict(record["proposed_files_sha256"])
        full = json.loads((root / "logs/r1_round30/r1-68f-patch.json").read_text())
        final = json.loads((root / "logs/r1_round31/r1-63l-backend-patch.json").read_text())
        target = "scripts/r1_77b_sealed_backend.py"
        if (
            identities[target] != full["original_files_sha256"][target]
            or full["proposed_files_sha256"][target] != final["original_sha256"]
        ):
            raise ValueError("installed backend successor chain is not reviewed")
        identities[target] = final["proposed_sha256"]
        for path, expected in identities.items():
            if hashlib.sha256((root / path).read_bytes()).hexdigest() != expected:
                raise ValueError("installed cadence patch differs from reviewed bytes")
        return "installed"
    _, revised = proposed_sources()
    for path, module, names in (
        (
            "src/pccap/revision_v1/stage4_cell.py",
            core,
            ("registered_checkpoints", "validate_payload"),
        ),
        ("scripts/r1_77b_sealed_backend.py", backend, ("inspect_manifest",)),
    ):
        namespace = dict(vars(module))
        exec(compile(revised[path], str(module.__file__), "exec"), namespace)
        for name in names:
            fn = namespace[name]
            bound = types.FunctionType(
                fn.__code__, vars(module), name, fn.__defaults__, fn.__closure__
            )
            bound.__kwdefaults__ = fn.__kwdefaults__
            monkeypatch.setattr(module, name, bound, raising=False)
    return "memory"
