"""Review guards: representative capacities, fixed inventories and pending runs."""

import copy
import hashlib
import json
from pathlib import Path
from tempfile import mkdtemp

import pytest
from scripts import ht4e_claim_ledger as ledger
from scripts import r1_x15_review as review


def test_independent_real_subject_counts_and_all_hall_subsets():
    report = json.loads((review.ROOT / "logs/r1_round25/r1-x15-independent.json").read_text())
    assert {d: x["subjects"] for d, x in report["counts"].items()} == {
        "zsre": 6084, "counterfact": 6121, "mquake": 2161}
    assert sum(len(x["hall"]) for x in report["counts"].values()) == 93
    assert all(c["margin"] >= 0 for x in report["counts"].values() for c in x["hall"])
    assert report["counts"]["mquake"]["role_subjects"]["revision"] == 2158
    assert report["teacher_baseline"]["zsre"]["empty_newline_one_step"] == 6036
    assert not report["ready_for_draw_seal_freeze_or_launch"]


def test_later_entity_row_does_not_improve_role_capacity():
    layout, candidates, dispositions = {}, {}, []
    for ds in review.DATASETS:
        layout[ds] = {"demand_subjects": 2, "demand_by_role": {"edits": 1, "revision": 1}}
        candidates[ds] = []
        for i, roles in enumerate((["edits"], ["edits", "revision"])):
            meta = dict(item_id=str(i), canonical_subject="same", payload_sha256=str(i))
            candidates[ds].append(meta)
            dispositions.append(dict(meta, dataset=ds, decision="eligible", reasons=[],
                                     entity_id=ds, roles=roles, alias_clear=True, context_clear=True,
                                     exposure_clear=True, teacher_pass=True, tokens_pass=True))
    result = review.reproduce({"candidates": candidates}, {"dispositions": dispositions}, layout)
    for value in result.values():
        assert value["eligible_items"] == 2 and value["subjects"] == 1
        assert value["role_subjects"]["revision"] == 0
        assert not value["all_hall_checks_pass"]
    bad = copy.deepcopy(dispositions)
    bad[-1]["payload_sha256"] = "tampered"
    with pytest.raises(ValueError, match="identity differs"):
        review.reproduce({"candidates": candidates}, {"dispositions": bad}, layout)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True))
    return ledger.ref(path)


@pytest.fixture
def profile_fixture(tmp_path, monkeypatch):
    resources = Path(mkdtemp(prefix="round25-ledger-", dir=ledger.ROOT.parent / "assets/test_scratch"))
    payload = dict(items=[dict(item_id=str(i)) for i in range(300)],
                   endpoints={"locality": {"expected_ids": ["q"]}})
    pb = write(resources / "payload.json", payload)
    recipe = write(tmp_path / "docs/tasks/test.recipe.json", {"payload": pb})
    directory = tmp_path / "results/cell"
    inspection = dict(recipe=recipe, cell={"condition": "v0_stable"},
                      locality_overlap_count=0, expected_result_directory=str(directory))
    write(tmp_path / "docs/tasks/R1-73d-post77d/inspection-receipts.json", [inspection])
    monkeypatch.setattr(ledger, "ROOT", tmp_path)
    yield directory, recipe


def test_pending_profile_never_borrows_old_results(profile_fixture):
    directory, _ = profile_fixture
    assert ledger.profile_inventory()[0]["status"] == "pending"
    write(directory.parent / "old-cell/attempt-0000/result.json", {"status": "complete"})
    assert ledger.profile_inventory()[0]["status"] == "pending"


@pytest.mark.parametrize("fault", [None, "manifest", "retention", "receipt", "duplicate"])
def test_completed_profile_requires_bound_full_inventory(profile_fixture, fault):
    directory, recipe = profile_fixture
    attempt = directory / "attempt-0000"
    retention = {"planned": 300, "rows": [dict(item_id=str(i), es=1., gs=0.5) for i in range(300)]}
    if fault == "retention":
        retention["rows"].pop()
    checkpoint = write(attempt / "checkpoint-300.json", dict(
        locality={"expected_ids": ["q"], "summary": {"expected_n": 1, "preserved_n": 1}},
        retention=retention, observation={}))
    receipt = dict(manifest_sha256=recipe["sha256"], report=checkpoint)
    receipt["receipt_sha256"] = hashlib.sha256(json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    write(attempt / "checkpoint-300.receipt.json", receipt)
    result = dict(status="complete", completed_checkpoint=300,
                  manifest_sha256="bad" if fault == "manifest" else recipe["sha256"],
                  last_receipt_sha256="bad" if fault == "receipt" else receipt["receipt_sha256"],
                  attempt_wall_seconds=1.)
    write(attempt / "result.json", result)
    if fault == "duplicate":
        write(directory / "attempt-0001/result.json", result)
    if fault:
        with pytest.raises(ValueError):
            ledger.profile_inventory()
    else:
        row = ledger.profile_inventory()[0]
        assert row["status"] == "complete"
        assert row["retention"] == {"planned": 300, "es": 1., "gs": 0.5}
