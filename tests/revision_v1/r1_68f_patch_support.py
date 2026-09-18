"""Exercise exact proposed driver/backend bytes in memory; never edit installed sources."""

import hashlib
import json
import types

from scripts import r1_68c_dev_cell as driver
from scripts import r1_68f_full_validation as full
from scripts import r1_77b_sealed_backend as backend
from scripts.r1_68f_prepare import BACKEND, DRIVER, ROOT, proposed_sources


def install(monkeypatch):
    if hasattr(driver, "full_validation"):
        record = json.loads((ROOT / "logs/r1_round30/r1-68f-patch.json").read_text())
        for path, expected in record["proposed_files_sha256"].items():
            if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
                raise ValueError("installed full-validation hook differs from reviewed patch")
        return "installed"
    _, sources = proposed_sources()
    for path, module in ((DRIVER, driver), (BACKEND, backend)):
        namespace = dict(vars(module))
        exec(compile(sources[path], str(module.__file__), "exec"), namespace)
        monkeypatch.setattr(module, "full_validation", full, raising=False)
        for name, value in namespace.items():
            if isinstance(value, types.FunctionType) and value.__module__ == module.__name__:
                bound = types.FunctionType(
                    value.__code__, vars(module), name, value.__defaults__, value.__closure__
                )
                bound.__kwdefaults__ = value.__kwdefaults__
                monkeypatch.setattr(module, name, bound)
        for name in ("DRIVER_FILES", "DONOR_SHA256"):
            if name in namespace:
                monkeypatch.setattr(module, name, namespace[name])
    return "memory"
