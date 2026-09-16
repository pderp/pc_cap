"""Metadata recipes must reproduce installed adapter identity, including controls."""

from dataclasses import asdict

import pytest
from scripts.r1_64b_comparator_recipes import metadata_identity

from pccap.contracts import Budget
from pccap.harness.ledger import Ledger
from pccap.revision_v1.controller import ControllerConfig, init_controller
from pccap.revision_v1.reader import ReaderConfig, init_reader
from pccap.revision_v1.stage4_adapters import CORE_CONDITIONS, SECONDARY_CONDITION, build_adapter
from tests.revision_v1.tiny_base import TinyBase

CAL = {"bank_scales": {"1": 1.1, "2": 2.2, "3": 3.3}, "radii": {"1": 0.0, "2": 0.02, "3": 0.03}}


@pytest.mark.parametrize("condition", [*CORE_CONDITIONS, SECONDARY_CONDITION])
def test_metadata_identity_matches_actual_tiny_factory(condition):
    import jax

    base, original = TinyBase(), TinyBase()
    original.checksum = lambda recompute=False: "distinct_original_identity"
    params = None
    stop = (0, 1)
    if condition.startswith("R1_"):
        k1, k2 = jax.random.split(jax.random.PRNGKey(3))
        random = condition == "R1_nonlearned"
        params = {
            "reader": init_reader(
                k1,
                ReaderConfig(
                    d=base.d, lexical=not random, pairwise_null=not random, stop_tokens=stop
                ),
            ),
            "controller": init_controller(
                k2, ControllerConfig(d=base.d, A=0.3, bank_scales=(1.1, 2.2, 3.3))
            ),
        }
    adapter = build_adapter(
        condition,
        base,
        Ledger(),
        calibration=CAL,
        params=params,
        seed=3,
        stop_tokens=stop,
        locality_base=original,
    )
    expected = metadata_identity(
        condition,
        d=base.d,
        base_hash=base.checksum(),
        original_hash=original.checksum(),
        calibration=CAL,
        seed=3,
        stop_tokens=stop,
        params=params,
    )
    assert expected == adapter.identity()
    assert expected["locality_base_sha256"] != expected["base_sha256"]
    assert expected["budget"] == asdict(Budget(A=0.3))
    if condition == "matched_update":
        assert expected["rule"]["steps"] == 5


@pytest.mark.parametrize(
    "calibration",
    [
        {"bank_scales": {"1": 1.0}, "radii": {"1": 0.0}},
        {
            "bank_scales": {"1": 1.0, "2": 2.0, "3": float("nan")},
            "radii": {"1": 0.0, "2": 0.0, "3": 0.0},
        },
        {"bank_scales": {"1": 1.0, "2": 2.0, "3": 3.0}, "radii": {"1": 0.0, "2": 0.0, "3": -0.01}},
    ],
)
def test_invalid_calibration_is_not_emitted(calibration):
    with pytest.raises(ValueError, match="calibrated"):
        metadata_identity(
            "v0_stable", d=8, base_hash="a", original_hash="a", calibration=calibration
        )


def test_missing_and_wrong_family_parameters_refused():
    with pytest.raises(ValueError, match="pinned"):
        metadata_identity("R1_nonlearned", d=8, base_hash="a", original_hash="a", calibration=CAL)
    with pytest.raises(ValueError, match="v0"):
        metadata_identity(
            "v0_stable", d=8, base_hash="a", original_hash="a", calibration=CAL, params={}
        )
