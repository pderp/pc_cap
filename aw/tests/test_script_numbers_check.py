"""Numerical audit must retain potential errors instead of blessing coincidences."""

import pytest

from aw.script_numbers_check import close, inventory, numbers, resolved


def test_decimals_signs_percentages_and_exponents():
    found = numbers("minus .097, −.2, 96 percent, 0.1594%, 1e-3 and 245,237")
    assert [n["value"] for n in found] == [-0.097, -0.2, 0.96, 0.001594, 0.001, 245237]
    assert found[2]["tolerance"] == 0.005
    assert found[-1]["tolerance"] == 0


def test_spelled_numbers_and_separate_counts():
    text = "two hundred forty-five thousand, two hundred thirty-seven; three and five; one tenth; one-third"
    assert [n["value"] for n in numbers(text)] == [245237, 3, 5, 0.1, 1 / 3]
    assert [n["value"] for n in numbers("one hundred and three hundred")] == [100, 300]
    assert [n["value"] for n in numbers("124 million parameters; 124M")] == [124000000, 124000000]
    assert [n["value"] for n in numbers("0.7 to 1.2 percentage points")] == pytest.approx(
        [0.007, 0.012]
    )


def test_wrapped_spoken_number_is_single_occurrence():
    found = inventory(
        "Say:\n\ntwo hundred forty-five thousand, two hundred\nthirty-seven positions",
        "script",
        {},
        [],
    )
    assert [r["value"] for r in found] == [245237]


def test_rounding_keeps_sign_and_exact_counts():
    assert close(numbers("96 percent")[0], numbers(".960333")[0])
    assert not close(numbers("96 percent")[0], numbers(".978")[0])
    assert not close(numbers("−.0028")[0], numbers(".0028")[0])
    assert not close(numbers("100")[0], numbers("100.1")[0])
    assert not close(numbers("19e99999")[0], numbers("0")[0])


def test_ledger_match_stays_candidate_and_wrong_count_unmatched():
    rows = {"claim": {"text": "16 cells", "source": "canonical/report.json"}}
    text = "## 1. Count\n\nSixteen cells, but 17 claimed.\n\nEvidence: `claim`.\n"
    found = inventory(text, "qa", rows, [])
    assert [(r["value"], r["status"]) for r in found] == [
        (1, "metadata"),
        (16, "ledger_candidate"),
        (17, "unmatched"),
    ]


def test_slot_span_cannot_certify_adjacent_literal():
    text, spans = resolved("Say:\n\n{{effect}} and .9.\n", {"effect": "−.0028"})
    found = inventory(text, "script", {}, [], spans)
    assert [r["status"] for r in found] == ["verified_slot", "unmatched"]
    assert found[0]["slot"] == "effect"
    assert resolved("{{missing}}", {})[0] == "PENDING"


def test_report_candidate_requires_a_local_citation_and_stays_unverified():
    reports = {
        "R_report.md": [
            dict(value=0.1234, raw=".1234", path="canonical/R.md", line=5, context="result .1234")
        ]
    }
    text = "## 1. Result\n\n.1234\n\nEvidence: [R](R_report.md)\n"
    result = inventory(text, "qa", {}, [], reports=reports)
    assert result[1]["status"] == "report_candidate"
    assert result[1]["report_candidates"][0]["line"] == 5
    assert (
        inventory(text.replace("R_report.md", "other.md"), "qa", {}, [], reports=reports)[1][
            "status"
        ]
        == "unmatched"
    )


@pytest.mark.parametrize("name", ["v5", "ES99", "SD-24"])
def test_identifier_digits_are_retained_but_separated(name):
    found = inventory("Say:\n\n" + name, "script", {}, [])
    assert len(found) == 1
    assert found[0]["status"] == "identifier"
