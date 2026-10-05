import json

import pytest

from aw.cost_gate import check, main


@pytest.mark.parametrize("projected,expected", [(17.98, "PASS"), (40, "PASS"), (40.01, "OVER_GATE")])
def test_extensionless_file_and_gate_boundary(tmp_path, projected, expected):
    path = tmp_path / "projection"
    path.write_text(json.dumps(dict(projected_process_hours=projected)))
    assert check(path, 40)["status"] == expected
    assert main(["--input", str(path), "--gate-hours", "40"]) == (0 if expected == "PASS" else 1)


@pytest.mark.parametrize("value", [None, True, "17.9", 0, -1, float("nan"), float("inf"), [], {}])
def test_invalid_exact_field_is_rejected(tmp_path, value):
    path = tmp_path / "projection"
    path.write_text(json.dumps(dict(projected_process_hours=value, hours=1)))
    assert main(["--input", str(path), "--gate-hours", "40"]) == 2


@pytest.mark.parametrize("text", ['{}', '[]', 'broken', '{"hours":1}',
                                   '{"projected_process_hours":1,"projected_process_hours":2}'])
def test_missing_malformed_duplicate_or_wrong_field_rejected(tmp_path, text):
    path = tmp_path / "projection"
    path.write_text(text)
    assert main(["--input", str(path), "--gate-hours", "40"]) == 2


@pytest.mark.parametrize("gate", [True, None, 0, -1, float("nan"), float("inf")])
def test_gate_itself_must_be_positive_finite(tmp_path, gate):
    path = tmp_path / "projection"
    path.write_text('{"projected_process_hours":1}')
    with pytest.raises(ValueError):
        check(path, gate)


def test_file_not_directory_or_suffix_search(tmp_path):
    (tmp_path / "other.json").write_text('{"projected_process_hours":1}')
    for path in (tmp_path, tmp_path / "missing"):
        assert main(["--input", str(path), "--gate-hours", "40"]) == 2
