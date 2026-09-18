"""Install just the proposed admission functions in a CPU test process."""

import types

from scripts import r1_63l_full_validation_contract as contract
from scripts import r1_77b_sealed_backend as backend
from scripts.r1_63l_prepare_backend import proposed


def install(monkeypatch):
    _, source = proposed()
    namespace = dict(vars(backend))
    exec(compile(source, backend.__file__, "exec"), namespace)
    monkeypatch.setattr(backend, "full_contract", contract, raising=False)
    for name in ("inspect_manifest", "load_sealed_cell"):
        value = namespace[name]
        bound = types.FunctionType(
            value.__code__, vars(backend), name, value.__defaults__, value.__closure__
        )
        bound.__kwdefaults__ = value.__kwdefaults__
        monkeypatch.setattr(backend, name, bound)
