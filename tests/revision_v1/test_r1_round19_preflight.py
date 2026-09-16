"""CPU tests of DEC056 population and proposed cadence/Markdown-preflight patches."""

import copy
import json
import re
import types
from pathlib import Path

import pytest
from scripts import r1_76b_mquake_review as review

ROOT = Path(__file__).resolve().parents[2]


def patched_source(path, patchpath, marker):
    source = (ROOT / path).read_text()
    if marker in source:
        return source
    lines = source.splitlines(keepends=True)
    out = []
    cursor = 0
    for line in (ROOT / patchpath).read_text().splitlines(keepends=True):
        if line.startswith(("---", "+++")):
            continue
        if line.startswith("@@"):
            match = re.match(r"@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@", line)
            start = int(match[1]) - 1
            out.extend(lines[cursor:start])
            cursor = start
        elif line.startswith(" "):
            assert lines[cursor] == line[1:]
            out.append(lines[cursor])
            cursor += 1
        elif line.startswith("-"):
            assert lines[cursor] == line[1:]
            cursor += 1
        elif line.startswith("+"):
            out.append(line[1:])
    return "".join(out + lines[cursor:])


def module(path, patchpath, marker):
    m = types.ModuleType("proposed")
    m.__file__ = str(ROOT / path)
    exec(compile(patched_source(path, patchpath, marker), m.__file__, "exec"), m.__dict__)
    return m


@pytest.fixture(scope="module")
def population():
    r, p = review.review()
    return r, p


def test_historical_review_full_lineage(population):
    r, p = population
    assert r["counts"]["metadata700"] == 700
    assert r["counts"]["subject_mention_in_selected_training_query_context"] == 43
    assert r["counts"]["cleared_historical_rows"] == 657
    assert len(p["edits"]) == 300 and len(p["outside"]) == 100
    assert p["checkpoints"] == [100, 300] and p["missing_checkpoints"] == [1000]
    assert all(x["exposure_label"] == review.LABEL for x in p["edits"] + p["outside"])
    assert all(
        "locality_prompts" not in x and "near_miss_candidates" not in x
        for x in p["edits"] + p["outside"]
    )
    assert r["final_register_subjects_used"] == 0 and r["model_calls"] == 0


def test_partial_cadence_only_DEC056_mquake(population):
    _, p = population
    m = module(
        "scripts/r1_76_unseen_common.py",
        "docs/tasks/R1-76b-runner-cadence.patch",
        "partial_mquake = (",
    )
    assert m.validate_population(p) == p
    for change in ("decision", "dataset", "label", "missing"):
        bad = copy.deepcopy(p)
        if change == "decision":
            bad["decision"] = "unapproved"
        if change == "dataset":
            bad["dataset"] = "zsre"
        if change == "label":
            bad["outside"][0]["exposure_label"] = "fresh"
        if change == "missing":
            bad["missing_checkpoints"] = []
        with pytest.raises(ValueError):
            m.validate_population(bad)


def test_full_cadence_retained():
    m = module(
        "scripts/r1_76_unseen_common.py",
        "docs/tasks/R1-76b-runner-cadence.patch",
        "partial_mquake = (",
    )
    spec = json.loads((ROOT / "docs/tasks/R1-76-zsre.population.spec.json").read_text())
    p = json.loads(Path(spec["population"]["path"]).read_text())
    assert m.validate_population(p) == p


def test_dry_preflight_markdown_and_missing_receipts():
    m = module(
        "scripts/r1_58c_draw_seal_preflight.py",
        "docs/tasks/R1-58c-markdown-binding.patch",
        'parse=key != "protocol"',
    )
    s = json.loads((ROOT / "docs/tasks/R1-58c-dry-inputs-v2.json").read_text())
    for stage in m.REQUIRED:
        r = m.preflight(s, stage)
        assert {b["gate"] for b in r["blocked"]} == set(m.REQUIRED[stage])
        assert r["draws_emitted"] == 0 and not r["ready_for_owner_review"]


def test_clearance_receipt_must_meet_joint_capacity():
    m = module(
        "scripts/r1_58c_draw_seal_preflight.py",
        "docs/tasks/R1-58c-markdown-binding.patch",
        'parse=key != "protocol"',
    )
    spec = {"register": {"path": "bound-v6", "sha256": "a" * 64}}
    r = {
        "status": "closed",
        "lead_approved": True,
        "register": spec["register"],
        "policy": "DEC-048-option-C;DEC-042-CounterFact;zsRE-priority",
        "cleared_subjects": dict(zsre=4050, counterfact=4050, mquake=4050),
        **{
            k: True
            for k in (
                "alias_review_complete",
                "context_review_complete",
                "teacher_token_review_complete",
                "role_compatibility_complete",
                "cross_dataset_disjoint",
                "cumulative_exposure_current",
            )
        },
    }
    m.check_receipt("joint_clearance", r, spec)
    r["cleared_subjects"]["mquake"] = 4049
    with pytest.raises(ValueError, match="capacity"):
        m.check_receipt("joint_clearance", r, spec)
