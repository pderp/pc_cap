"""Review the unapplied R1-68e driver patch without changing the live driver."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from scripts import r1_68e_batched_drift_v0 as batch

from pccap.revision_v1.stage4_assays import CellAssays
from tests.revision_v1.test_r1_68e_batched_drift_v0 import adapter, populate

ROOT = Path(__file__).resolve().parents[2]


def projected_driver():
    path = ROOT / "scripts/r1_68c_dev_cell.py"
    source = path.read_text()
    if "def run_drift_assay(" not in source:
        from tests.revision_v1.test_r1_round19_preflight import patched_source

        source = patched_source("scripts/r1_68c_dev_cell.py", "docs/tasks/R1-68e-driver.patch", "def run_drift_assay(")
    spec = importlib.util.spec_from_file_location("scripts._r1_68e_projected_driver", path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def test_hook_is_opt_in_and_preserves_existing_dispatch(monkeypatch):
    driver = projected_driver()
    monkeypatch.setattr(driver, "v0_batched_drift", lambda *a, **kw: "v0")
    monkeypatch.setattr(driver, "batched_drift", lambda *a, **kw: "revision")
    assays = SimpleNamespace(drift=lambda d: "scalar")
    assert driver.run_drift_assay(assays, {}, {}, "full") == "scalar"
    assert driver.run_drift_assay(assays, {}, {}, "incremental") == "revision"
    assert (
        driver.run_drift_assay(assays, {}, {"drift_implementation": batch.IMPLEMENTATION}, "full")
        == "v0"
    )
    with pytest.raises(ValueError):
        driver.run_drift_assay(assays, {}, {"drift_implementation": "unknown"}, "full")


@pytest.mark.parametrize("condition", list(batch.CONDITION_CLASSES))
def test_hook_profile_admission_and_module_hash(condition):
    driver = projected_driver()
    bindings = driver.driver_bindings()
    assert "scripts/r1_68e_batched_drift_v0.py" in bindings
    manifest = {
        "cell": {"condition": condition},
        "integrity_profile": "full",
        "integrity_driver_bindings": bindings,
        "drift_implementation": batch.IMPLEMENTATION,
    }
    assert driver.profile_config(manifest) == ("full", 16)
    manifest["integrity_profile"] = "incremental"
    with pytest.raises(ValueError):
        driver.profile_config(manifest)
    manifest["integrity_profile"] = "full"
    manifest["cell"]["condition"] = "R1_learned_ff"
    with pytest.raises(ValueError):
        driver.profile_config(manifest)
    manifest["cell"]["condition"] = condition
    manifest["integrity_driver_bindings"] = {}
    with pytest.raises(ValueError):
        driver.profile_config(manifest)


def test_hook_tinybase_dispatch_matches_scalar():
    driver = projected_driver()
    a = adapter("v0_live_C1")
    populate(a)
    definition = {"windows": [[2, 3, 4]], "expected_positions": 2}
    scalar = CellAssays(a, None).drift(definition)
    result = driver.run_drift_assay(
        CellAssays(a, None),
        definition,
        {"drift_implementation": batch.IMPLEMENTATION, "drift_batch_size": 2},
        "full",
    )
    np.testing.assert_allclose(
        [r["cap"] for r in result["rows"]], [r["cap"] for r in scalar["rows"]], rtol=0, atol=1e-4
    )


def test_context_buckets_and_order_are_preserved():
    a = adapter("v0_stable")
    definition = {"windows": [list(range(1, 35))], "expected_positions": 33}
    assays = CellAssays(a, None)
    result = batch.batched_drift(assays, definition, batch_size=4)
    assert [r["item_id"] for r in result["rows"]] == [f"w0:p{i}" for i in range(1, 34)]
    assert all(r["cap"] == r["capoff"] for r in result["rows"])
    reader = batch.V0PositionBatchReader(a, batch_size=2)
    with pytest.raises(ValueError, match="bucket"):
        reader.last_logits_batch([[1], [1] * 33])
