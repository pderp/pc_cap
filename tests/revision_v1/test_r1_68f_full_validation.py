"""DEC-063 bounded full validation, both references, overlap parity and integrity."""

import copy
import json
import uuid
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from scripts import ht_audit_existing as ht
from scripts import r1_68c_dev_cell as driver
from scripts import r1_68f_full_validation as full
from scripts import r1_77b_sealed_backend as backend
from scripts.r1_68c_batched_drift import batched_drift
from scripts.r1_68e_batched_drift_v0 import CONDITION_CLASSES
from scripts.r1_68e_batched_drift_v0 import batched_drift as v0_drift
from scripts.r1_68f_prepare import BACKEND, DRIVER, proposed_sources

from pccap.harness.ledger import Ledger
from pccap.revision_v1.endpoints_composition import as_edit
from pccap.revision_v1.stage4_adapters import build_adapter
from pccap.revision_v1.stage4_assays import CellAssays
from tests.revision_v1 import test_r1_68c_driver as old_tests
from tests.revision_v1.r1_68f_patch_support import install
from tests.revision_v1.test_learner_cpu import _cfg
from tests.revision_v1.test_r1_68e_batched_drift_v0 import adapter, populate
from tests.revision_v1.test_r1_77b_sealed_backend import make  # noqa: F401 -- pytest fixture
from tests.revision_v1.test_stage4_cell import CAL, TinyTok, payload
from tests.revision_v1.tiny_base import TinyBase


@pytest.fixture
def paths():
    name = uuid.uuid4().hex
    assets = full.ROOT.parent / "assets/runs/pc_cap/R1/r1_68f_tests" / name
    output = full.ROOT / "logs/r1_round30/cpu_fixtures" / name
    assets.mkdir(parents=True)
    output.mkdir(parents=True)
    return assets, output


def fixture(paths, *, width=8, windows=4, sample=2):
    assets, output = paths
    tokens = (np.arange(width * windows + 3, dtype=np.int32) % 53) + 2
    source = assets / "tokens.npy"
    np.save(source, tokens)
    inventory = assets / "lm-sets.json"
    inventory.write_text(
        json.dumps(
            dict(
                files=dict(
                    drift_tokens={**full.ref(source), "shape": [len(tokens)], "dtype": "int32"}
                )
            )
        )
    )
    manifest = dict(
        test_fixture=True,
        adapter_identity=dict(base_sha256="tiny"),
        full_validation=full.make_spec(inventory=inventory, fixture=True, window_tokens=width),
        drift_batch_size=4,
        checkpoints=[1, 2],
    )
    definition = dict(
        windows=tokens[: sample * width].reshape(sample, width).tolist(),
        expected_positions=sample * (width - 1),
    )
    return manifest, definition, output / "vectors.npz"


def primary(condition="R1_learned_ff", *, occupied=True):
    cfg = _cfg(null_threshold=1.1)
    cfg.fast = replace(cfg.fast, steps=0, delta_steps=1)
    cap = build_adapter(
        condition, TinyBase(), Ledger(), calibration=CAL, synthetic=True, revision_config=cfg
    )
    cap.learner.cfg.null_threshold = 1.1
    cap.learner.cfg.rare_overlap_min = None
    if occupied:
        for row in payload(2)["items"]:
            cap.update_item(as_edit(row, TinyTok()))
    return cap


def evaluate(cap, manifest, definition, output):
    assays = CellAssays(cap, None)
    sample = (batched_drift if cap.condition.startswith("R1_") else v0_drift)(
        assays, definition, batch_size=manifest["drift_batch_size"]
    )
    assays.events = []
    before = cap.state_hash()
    result = full.run(
        assays, manifest, definition, sample, output, checkpoint=2, manifest_sha256="a" * 64
    )
    assert cap.state_hash() == before == result["state_sha256"]
    assert len(assays.events) <= 6  # aggregated model work, never per-prefix event retention
    assert (
        result["batch_audit"]["selection_count"]
        == manifest["full_validation"]["expected_positions"]
    )
    assert result["device_peak_mem_mib"] is None  # CPU has no allocator telemetry
    assert result["wall_seconds"] > 0
    with np.load(output, allow_pickle=False) as stored:
        values = stored["values"].copy()
    assert np.isfinite(values).all()
    assert values.dtype == np.float64
    return result, values, sample


@pytest.mark.parametrize(
    "condition", ["R1_learned_ff", "R1_nonlearned", "R1_learned_ff_v2", *CONDITION_CLASSES]
)
def test_all_families_both_references_and_scalar_parity(paths, condition):
    manifest, definition, output = fixture(paths)
    cap = primary(condition) if condition.startswith("R1_") else adapter(condition)
    if not condition.startswith("R1_"):
        populate(cap)
    result, values, _ = evaluate(cap, manifest, definition, output)
    windows, _ = full.population(manifest["full_validation"]["source"], window_tokens=8)
    scalar = CellAssays(cap, None).drift(dict(windows=windows.tolist(), expected_positions=28))
    expected = np.asarray([[r[k] for k in ("cap", "capoff", "original")] for r in scalar["rows"]])
    np.testing.assert_allclose(values.reshape(-1, 5)[:, :3], expected, atol=1e-4, rtol=0)
    assert result["coverage"]["trailing_tokens_dropped"] == 3
    assert np.all(values[:, :, 3:] >= 0)
    if condition.startswith("S1_"):
        assert np.max(np.abs(values[:, :, 1] - values[:, :, 2])) > 0.01
        assert np.max(values[:, :, 4]) > 0.01
    else:
        np.testing.assert_array_equal(values[:, :, 1], values[:, :, 2])
        np.testing.assert_array_equal(values[:, :, 3], values[:, :, 4])


@pytest.mark.parametrize("condition", ["R1_learned_ff", "v0_stable"])
@pytest.mark.parametrize("occupied", [False, True])
def test_first_128_complete_128_token_windows_match_sample(paths, condition, occupied):
    manifest, definition, output = fixture(paths, width=128, windows=129, sample=128)
    manifest["drift_batch_size"] = 32
    cap = primary(occupied=occupied) if condition.startswith("R1_") else adapter(condition)
    if occupied and condition == "v0_stable":
        populate(cap)
    result, values, sample = evaluate(cap, manifest, definition, output)
    assert result["scored_positions"] == 129 * 127
    assert result["sample_parity"]["positions"] == 128 * 127
    np.testing.assert_allclose(
        values[:128, :, 0].ravel(), [r["cap"] for r in sample["rows"]], atol=1e-4, rtol=0
    )
    if not occupied:
        np.testing.assert_array_equal(values[:, :, 0], values[:, :, 1])
        assert np.count_nonzero(values[:, :, 3:]) == 0


def test_tail_statistics_match_ht1_fractional_boundary():
    values = [-2.0, 0.0, 0.001, 0.01, 0.1, 0.2, 1.0, 1.1, 3.0] * 7
    locations = [f"w{i // 7}:p{1 + i % 7}" for i in range(len(values))]
    expected = ht.statistics(values, locations)
    result = full.tail_statistics(values, 7)
    for key in (
        "mean_signed",
        "mean_positive",
        "ES95_positive",
        "maximum_signed",
        "maximum_positive",
    ):
        assert result[key] == pytest.approx(expected[key], abs=1e-12)
    for key in ("maximum_location", "maximum_tie_count", "exceedances_nats"):
        assert result[key] == expected[key]


def test_kl_direction_and_finite_refusal():
    p = np.log([[0.7, 0.3]])
    q = np.log([[0.2, 0.8]])
    result = full.metrics(q, p, p, np.array([0]))
    assert result[0, 3] == pytest.approx(0.7 * np.log(0.7 / 0.2) + 0.3 * np.log(0.3 / 0.8))
    with pytest.raises(FloatingPointError):
        full.metrics(q, p * np.nan, p, np.array([0]))


def test_real_source_inventory_no_model_calls():
    spec = full.make_spec()
    assert full.validate_spec(dict(full_validation=spec)) == spec
    assert (
        spec["complete_windows"],
        spec["expected_positions"],
        spec["trailing_tokens_dropped"],
    ) == (1931, 245237, 121)
    for path in (full.ROOT / "docs/tasks/R1-64f").glob("*.recipe.json"):
        recipe = json.loads(path.read_text())
        data = json.loads(Path(recipe["payload"]["path"]).read_text())
        full.validate_sample({**recipe, "full_validation": spec}, data["endpoints"]["drift"])


@pytest.mark.parametrize("fault", ["hash", "tail", "count", "shape", "subset", "sample", "fixture"])
def test_contract_and_source_tampering_refuse(paths, fault):
    manifest, definition, _ = fixture(paths)
    spec = manifest["full_validation"]
    if fault == "hash":
        spec["source"]["sha256"] = "b" * 64
    elif fault == "tail":
        spec["tail_policy"] = "include"
    elif fault == "count":
        spec["expected_positions"] -= 1
    elif fault == "shape":
        source = Path(spec["source"]["path"])
        np.save(source, np.array([[1, 2]], dtype=np.int32))
    elif fault == "subset":
        spec["complete_windows"] -= 1
    elif fault == "sample":
        definition["windows"][0][0] += 1
    elif fault == "fixture":
        manifest["adapter_identity"]["base_sha256"] = "real"
    with pytest.raises(ValueError):
        full.validate_sample(manifest, definition)


def test_failure_preserves_charged_work_without_vector_receipt(paths, monkeypatch):
    manifest, definition, output = fixture(paths)
    cap = adapter("v0_stable")
    assays = CellAssays(cap, None)
    sample = v0_drift(assays, definition, batch_size=4)
    assays.events = []
    original = full.metrics
    calls = 0

    def corrupt(*args):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise FloatingPointError("injected nonfinite")
        return original(*args)

    monkeypatch.setattr(full, "metrics", corrupt)
    with pytest.raises(FloatingPointError):
        full.run(
            assays, manifest, definition, sample, output, checkpoint=2, manifest_sha256="a" * 64
        )
    assert not output.exists()
    charged = [e for e in assays.events if e.get("returned_cost")]
    assert sum(e["returned_cost"].get("full_forwards", 0) for e in charged) == 8
    assert assays.events[-1]["completed_positions"] == 4


def test_stream_inventory_is_complete_unique_bounded_and_same_bucket():
    windows = np.arange(131 * 128).reshape(131, 128)
    seen = set()
    for chunk in full.chunks(windows, 17):
        assert 1 <= len(chunk) <= 17
        assert len({full.g.bucket_len(pos) for _, pos, _, _ in chunk}) == 1
        for wi, pos, prefix, target in chunk:
            assert (wi, pos) not in seen
            seen.add((wi, pos))
            np.testing.assert_array_equal(prefix, windows[wi, :pos])
            assert target == windows[wi, pos]
    assert len(seen) == 131 * 127


@pytest.mark.parametrize("profile", ["full", "incremental"])
def test_proposed_driver_cadence_receipts_and_resume_tamper(paths, monkeypatch, profile):
    install(monkeypatch)
    case = old_tests.DriverTests()
    case.setUp()
    try:
        path, tok, cap = case.fixture(profile)
        manifest = json.loads(path.read_text())
        prepared, definition, _ = fixture(paths)
        manifest["full_validation"] = prepared["full_validation"]
        data_path = Path(manifest["payload"]["path"])
        data = json.loads(data_path.read_text())
        data["endpoints"]["drift"] = definition
        data_path.write_text(json.dumps(data))
        manifest["payload"]["sha256"] = driver.sha(data_path)
        path.write_text(json.dumps(manifest))
        case.run_cell((path, tok, cap), stop_after_checkpoint=1)
        result = case.run_cell((path, tok, case.adapter()), resume=True)
        reports = case.reports(result)
        assert "drift" in reports[1]["endpoints"]
        assert "full_validation" not in reports[1]["endpoints"]
        endpoint = reports[2]["endpoints"]["full_validation"]
        assert endpoint["state_sha256"] == reports[2]["state_sha256"]
        assert endpoint["sample_parity"]["status"] == "pass"
        assert (
            sum(t["phase"].startswith("full_validation:") for t in result["detailed_phase_timers"])
            == 1
        )
        if profile == "incremental":
            timer = next(
                t
                for t in result["detailed_phase_timers"]
                if t["phase"].startswith("full_validation:")
            )
            assert timer["clone_seconds"] == timer["restore_seconds"] == 0
        case.run_cell((path, tok, case.adapter()), resume=True)
        Path(endpoint["vectors"]["path"]).write_bytes(b"tampered")
        with pytest.raises(ValueError, match="vectors escaped report attempt or changed"):
            case.run_cell((path, tok, case.adapter()), resume=True)
    finally:
        case.doCleanups()


def test_both_proposed_execution_bodies_have_matching_full_validation_hook():
    original, revised = proposed_sources()
    for path in (DRIVER, BACKEND):
        assert (full.ROOT / path).read_text() in (original[path], revised[path])
        source = revised[path]
        assert source.count("lambda n=n, ep=ep, cp=cp: full_validation.run(") == 1
        assert source.count("full_validation.verify_report(") == 1
        assert source.count('if n != len(items) and "full_validation" in manifest:') == 1
        assert source.count('"full_validation",') == 1
    assert full.hashlib.sha256(revised[DRIVER].encode()).hexdigest() in revised[BACKEND]


def test_parity_rejects_changed_exceedance_or_nonfinite(paths):
    manifest, definition, output = fixture(paths)
    _, values, sampled = evaluate(adapter("v0_stable"), manifest, definition, output)
    bad = copy.deepcopy(sampled)
    bad["rows"][0]["cap"] += 1
    with pytest.raises(ValueError, match="parity failed"):
        full.parity(values, bad)


def test_sealed_execution_hook_with_isolated_tiny_admission(make, paths, monkeypatch):  # noqa: F811
    install(monkeypatch)
    # The proposed donor lives in memory. The synthetic admission fixture binds
    # installed file bytes; retain that disk pin only for this isolated test.
    monkeypatch.setattr(backend, "DONOR_SHA256", driver.sha(driver.__file__))
    manifest, definition, _ = fixture(paths)
    validate = full.validate_spec

    def tiny_population(m):
        # Sealed admission correctly forbids test_fixture on its recipe. Inject
        # the TinyBase-only population exception into this test process, without
        # relaxing the actual sealed loader, gate, population or recipe checks.
        return validate({**m, "test_fixture": True})

    monkeypatch.setattr(full, "validate_spec", tiny_population)
    data = payload(2, composition=True)
    data["endpoints"]["drift"] = definition

    def enable(m, frozen, data):
        m["full_validation"] = manifest["full_validation"]

    f = make(change=enable, data_override=data)
    result = f["execute"]()
    assert result["status"] == "complete"
    reports = [
        json.loads(p.read_text())
        for p in Path(result["run_dir"]).glob("attempt-*/checkpoint-*.json")
        if not p.name.endswith(".receipt.json")
    ]
    reports.sort(key=lambda r: r["checkpoint"])
    assert "drift" in reports[0]["endpoints"]
    assert "full_validation" not in reports[0]["endpoints"]
    assert reports[1]["endpoints"]["full_validation"]["status"] == "complete"
    with pytest.raises(ValueError, match="already complete"):
        f["execute"](resume=True)
