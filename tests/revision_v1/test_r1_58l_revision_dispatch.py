"""Unknown cost revisions fail closed until their explicit validator is installed."""

import pytest
from scripts import r1_58h_cost_contract as contract

from tests.revision_v1.test_r1_58h_cost_receipt import complete


@pytest.mark.parametrize("revision", [None, True, 2.0, "3", 0, 1, 5, 99])
def test_new_or_malformed_revision_cannot_bypass_supplement(tmp_path, revision):
    _, receipt = complete(tmp_path)
    receipt["receipt_revision"] = revision
    with pytest.raises(ValueError, match="explicit validator required"):
        contract.validate(receipt)


def test_original_and_explicit_v2_remain_valid(tmp_path):
    _, receipt = complete(tmp_path)
    assert contract.validate(receipt)["typed_cost_rows"] == 27
    assert contract.validate({**receipt, "receipt_revision": 2})["typed_cost_rows"] == 27


def test_revision3_still_requires_its_supplement(tmp_path, monkeypatch):
    from scripts import r1_58j_cost_receipt as revision3

    _, receipt = complete(tmp_path)

    def reject(_):
        raise ValueError("revision3 supplement visited")

    monkeypatch.setattr(revision3, "validate_supplement", reject)
    with pytest.raises(ValueError, match="supplement visited"):
        contract.validate({**receipt, "receipt_revision": 3})
