"""Actual producer clearance/draw/endpoints/seal with synthetic DEC-062 only."""

import pytest
from scripts import r1_d9f_allocation as allocation
from scripts.r1_d9_receipts import read_metadata

from tests.revision_v1.test_r1_58e_rehearsal import stages  # noqa: F401


@pytest.mark.parametrize("stages", ["family_coordinated"], indirect=True)
def test_coordinated_mode_through_real_producer_and_seal(stages):  # noqa: F811
    report = read_metadata(stages["record"])
    assert report["synthetic"] and not report["production_admission"]
    assert not report["endpoint_missing"]
    sealed = stages["sealed"]
    assert sealed["near_allocation"] == "family_coordinated"
    allocation.audit(sealed)
    assert len(sealed["near_pair_receipts"]) == 9
    assert all(
        r["matched"] == 100 and not r["missing"] for r in sealed["near_pair_receipts"].values()
    )
    assert len(stages["payloads"]) == 360
