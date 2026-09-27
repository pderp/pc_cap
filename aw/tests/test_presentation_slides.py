"""Speaker/diagram claims must resolve, and the draft exports must be valid SVG."""

import json
import re
import xml.etree.ElementTree as ET

from aw import presentation_slides as s
from aw.presentation_claims import append_concepts, read_rows


def test_all_speaker_and_diagram_claims_exist():
    claims = {row[0] for row in read_rows((s.ROOT / "docs/talk_claim_ledger_v7.md").read_text())}
    specs = json.loads((s.SOURCE / "diagram-specs.json").read_text())["slides"]
    assert [x["number"] for x in specs] == [
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
    ]
    for spec in specs:
        assert set(spec["claims"]) <= claims
        ET.fromstring(s.diagram(spec, allow_tail=False))
        paths = list(s.SOURCE.glob("slide" + spec["number"] + "-*.md"))
        assert len(paths) == 1
        text = paths[0].read_text()
        assert "Draft speaker text" in text
        for group in re.findall(r"\[(`[^\]]+)\]", text):
            assert set(re.findall(r"`([^`]+)`", group)) <= claims


def test_ledger_literal_pipes_round_trip():
    base = "Example\n\n| ID | theme | status | measured result | population | control | supports | does not support | source |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
    row = [
        "test",
        "theme",
        "concept",
        "norm ||e||",
        "pop",
        "control",
        "support",
        "limits",
        "source",
    ]
    assert read_rows(append_concepts(base, [row])) == [row]
