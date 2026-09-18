"""Actual D11 accounting/watch with synthetic queue cells; no GPU or model."""

import copy
import json
from pathlib import Path
from uuid import uuid4

import pytest
from scripts import r1_77f_scheduler as scheduler
from scripts import r1_d12_reprice as reprice

ROOT = reprice.d11.ROOT


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n")
    return path


@pytest.fixture(scope="module")
def validated_v4():
    cost = json.loads((ROOT / "docs/tasks/R1-cost-admission-receipt-v4.json").read_text())
    reprice.costs.validate(cost)
    return cost


@pytest.fixture
def scenario(monkeypatch, validated_v4):
    root = ROOT / "logs/r1_round37/synthetic-queues" / uuid4().hex
    cost = copy.deepcopy(validated_v4)
    cp = put(root / "cost.json", cost)
    # Validate the complete real v4 evidence once above; disallow any fixture
    # mutation from bypassing it. This caches expensive immutable source reads.
    def checked(value):
        assert value == validated_v4
    monkeypatch.setattr(reprice.costs, "validate", checked)
    prices = {(r["condition"], r["dataset"]): r for r in cost["cells"]}
    cells = []
    for n in range(4):
        c = dict(condition="R1_learned_ff", dataset="zsre", realization=0, order=n,
                 attempted_edits=1000, checkpoints=[100, 300, 1000],
                 block_number=1 if n < 2 else 2, within_block_order=n + 1,
                 full_validation=cost["full_validation"],
                 manifest_sha256=str(n) * 64, result_dir=str(root / f"results/cell{n}"),
                 ceilings=prices[("R1_learned_ff", "zsre")])
        c["cell_id"] = reprice.d11.queue.analysis.coordinate_id(c)
        cells.append(c)
    matrix = dict(scope="confirmatory", cells=cells, shared_process_hours=750,
                  full_validation=cost["full_validation"], fidelity_watch=reprice.d11.watch.binding(),
                  protocol=cost["protocol"], source_matrix=copy.deepcopy(cost["matrix"]),
                  cost_admission=reprice.d11.ref(cp))
    mp = put(root / "matrix.json", matrix)
    receipts, journal = root / "logs/receipts", root / "watch.jsonl"
    complete = set()

    def load(cell, files, scope):
        done = cell["cell_id"] in complete
        return dict(status="complete" if done else "missing", artifact_complete=done,
                    missing_checkpoints=[] if done else cell["checkpoints"])
    monkeypatch.setattr(reprice.d11.queue.analysis, "load_cell", load)

    def process(n, seconds=115, seq=0, failure=None, finish=True, workers=2):
        c = cells[n]
        attempt = Path(c["result_dir"]) / f"attempt-{seq:04d}"
        put(attempt / ("failure.json" if failure else "result.json"),
            dict(attempt_wall_seconds=seconds - 1))
        start = dict(cell_id=c["cell_id"], matrix_sha256=reprice.d11.queue.sha(mp),
                     retry_policy=scheduler.POLICY, workers=workers)
        folder = receipts / f"cell{n}-process{seq}"
        sp = put(folder / "start.json", start)
        if finish:
            put(folder / "finish.json", dict(start, start_sha256=reprice.d11.queue.sha(sp),
                charged_process_wall_seconds=seconds, new_attempts=[str(attempt)], failure_class=failure))
        return folder

    def observe(n, kl=0.002):
        c = cells[n]
        coords = {k: c[k] for k in reprice.d11.queue.analysis.COORDS}
        identity = dict(mode="stage4_sealed_cell", recipe_sha256=c["manifest_sha256"], cell=coords)
        obs = dict(identity=identity, cell_id=reprice.digest(identity), cell=coords,
                   scope="confirmatory", recipe=dict(path="synthetic", sha256=c["manifest_sha256"]),
                   references={r:dict(kl=dict(mean_signed=kl), loss=dict(mean_signed=0))
                               for r in ("original", "capoff")})
        event = dict(policy=reprice.d11.watch.POLICY, observation=obs,
                     observation_sha256=reprice.digest(obs), recorded_utc="2026-09-18T14:00:00+00:00")
        with journal.open("a") as f:
            f.write(reprice.d11.watch.encoded(event))
        complete.add(c["cell_id"])

    def build(**kw):
        return reprice.build(mp, receipt_root=receipts, journal=journal, cost_receipt=cp,
                             boundary_block=kw.pop("boundary_block", 1), synthetic=kw.pop("synthetic", True), **kw)
    return dict(root=root, matrix=matrix, mp=mp, cost=cost, cp=cp, cells=cells,
                receipts=receipts, journal=journal, process=process, observe=observe,
                build=build, complete=complete)


def finish_block(f):
    for n, seconds in ((0, 115), (1, 230)):
        f["process"](n, seconds=seconds)
        f["observe"](n)


def test_measured_rates_single_concurrency_and_actual_spend(scenario):
    f = scenario
    finish_block(f)
    out = f["build"]()
    c = out["classes"][0]
    assert c["expected_process_seconds"] == 172.5
    assert c["proposed_effective_ceiling_seconds"] == 345
    assert c["proposed_solo_ceiling_seconds"] == pytest.approx(300)
    assert out["projection"]["expected_total_process_hours"] == pytest.approx(690 / 3600)
    assert out["projection"]["proposed_ceiling_total_process_hours"] == pytest.approx(1035 / 3600)
    assert out["d11"]["watch"]["entries"]  # benchmark failure does not filter donors
    assert out["projection"]["elapsed_hours"] is None
    assert not out["lead_approved"] and not out["launch_authorized"]


def test_failed_attempt_charged_once_and_included_in_completed_chain(scenario):
    f = scenario
    f["process"](0, seconds=25, failure="cell")
    f["process"](0, seq=1, seconds=115)
    f["observe"](0)
    f["process"](1, seconds=100)
    f["observe"](1)
    out = f["build"]()
    assert out["classes"][0]["expected_process_seconds"] == 120
    assert out["projection"]["actual_process_hours"] == 240 / 3600
    assert out["projection"]["expected_total_process_hours"] == 480 / 3600


def test_exhausted_cells_remain_in_inventory_never_zero_donors(scenario):
    f = scenario
    f["process"](0, seconds=115)
    f["observe"](0)
    for seq in (0, 1):
        f["process"](1, seq=seq, seconds=20, failure="cell")
    out = f["build"]()
    assert out["classes"][0]["measured_cells"] == 1
    assert out["classes"][0]["expected_process_seconds"] == 115
    assert out["dec052_inventory"]["exhausted_incomplete_cells"] == [f["cells"][1]["cell_id"]]
    assert out["projection"]["expected_total_process_hours"] == 385 / 3600


@pytest.mark.parametrize("field,value", [("attempted_edits", 300), ("checkpoints", [100, 300]),
                                          ("condition", "v0_stable"), ("dataset", "counterfact")])
def test_no_unreviewed_cross_class_transfer(scenario, field, value):
    f = scenario
    f["cells"][2][field] = value
    if field in ("condition", "dataset"):
        f["cells"][2]["cell_id"] = reprice.d11.queue.analysis.coordinate_id(f["cells"][2])
    put(f["mp"], f["matrix"])
    finish_block(f)
    out = f["build"]()
    groups = [c for c in out["classes"] if f["cells"][2]["cell_id"] in c["cell_ids"]]
    assert len(groups) == 1 and groups[0]["basis"] == "retained_plan_v3_estimate"


def test_later_live_worker_blocks_repricing_even_if_boundary_is_done(scenario):
    f = scenario
    finish_block(f)
    f["process"](2, finish=False)
    with pytest.raises(ValueError, match="idle"):
        f["build"]()


def test_missing_watch_and_incomplete_boundary_refuse(scenario):
    f = scenario
    f["process"](0)
    f["complete"].add(f["cells"][0]["cell_id"])
    with pytest.raises(ValueError, match="boundary"):
        f["build"]()


def test_workers_are_not_silently_rescaled(scenario):
    f = scenario
    for n in (0, 1):
        f["process"](n, workers=1)
        f["observe"](n)
    out = f["build"]()
    assert len(out["excluded_donors"]) == 2
    assert out["classes"][0]["basis"] == "retained_plan_v3_estimate"


def test_unsigned_real_cost_cannot_become_admission(scenario):
    with pytest.raises(ValueError, match="signed cost"):
        scenario["build"](synthetic=False)


def test_changed_cost_matrix_binding_refuses(scenario):
    f = scenario
    f["matrix"]["source_matrix"]["sha256"] = "bad"
    put(f["mp"], f["matrix"])
    with pytest.raises(ValueError, match="source cost matrix"):
        f["build"]()


def test_versioned_emission_with_watch_and_inventory_no_overwrite(scenario):
    f = scenario
    finish_block(f)
    first = f["build"]()
    output = f["root"] / "logs/block1"
    ref = reprice.emit(first, output)
    assert (output / "execution-plan-v4.md").exists()
    assert (output / "fidelity-watch.json").exists()
    assert (output / "dec052-inventory.json").exists()
    with pytest.raises(FileExistsError):
        reprice.emit(first, output)
    for n in (2, 3):
        f["process"](n, seconds=80)
        f["observe"](n, kl=0.005)
    second = f["build"](boundary_block=2, previous_plan=ref["path"],
                        previous_report=output / "d11-report.json")
    assert second["plan_version"] == 5
    assert second["d11"]["watch"]["new_queue_observations"] == 2
    assert second["d11"]["watch"]["alerts"]
    assert not second["dec052_inventory"]["incomplete_cells"]
    assert second["projection"]["remaining_expected_process_hours"] == 0
    reprice.emit(second, f["root"] / "logs/block2")
    # Retain a reproducible worked example under the round's log directory.
    (f["root"] / "example.json").write_text(json.dumps(dict(first=ref, second=str(f["root"] / "logs/block2/plan.json"))))


def test_changed_snapshot_blocks_publication(scenario):
    f = scenario
    finish_block(f)
    out = f["build"]()
    f["process"](2, finish=False)
    with pytest.raises(ValueError, match="queue changed"):
        reprice.emit(out, f["root"] / "logs/refused")
    assert not (f["root"] / "logs/refused").exists()


def test_changed_previous_plan_digest_and_wrong_queue_refuse(scenario):
    f = scenario
    finish_block(f)
    first = f["build"]()
    first["plan_version"] = 100
    prior = put(f["root"] / "tampered-plan.json", first)
    with pytest.raises(ValueError, match="digest"):
        f["build"](previous_plan=prior)


def test_host_failure_does_not_establish_a_replacement_rate(scenario):
    f = scenario
    f["process"](0, seconds=25, failure="host")
    f["process"](0, seq=1, seconds=115)
    f["observe"](0)
    f["process"](1, seconds=115)
    f["observe"](1)
    out = f["build"]()
    assert out["excluded_donors"][0]["reason"] == "host failure needs owner reconciliation"
    assert out["projection"]["actual_process_hours"] == 255 / 3600


def test_prior_charged_files_cannot_be_removed_to_reduce_spending(scenario):
    f = scenario
    finish_block(f)
    first = f["build"]()
    prior = put(f["root"] / "prior.json", first)
    # Preserve internally valid start/finish hashes, but rewrite an old cost.
    path = next(f["receipts"].glob("cell0-*/finish.json"))
    end = json.loads(path.read_text())
    end["charged_process_wall_seconds"] -= 10
    put(path, end)
    for n in (2, 3):
        f["process"](n)
        f["observe"](n)
    with pytest.raises(ValueError, match="previous charged evidence"):
        f["build"](boundary_block=2, previous_plan=prior)


def test_prior_plan_alone_preserves_watch_prefix(scenario):
    f = scenario
    finish_block(f)
    first = f["build"]()
    prior = put(f["root"] / "prior.json", first)
    # Same valid observations in reversed order: replay is possible but history changed.
    lines = f["journal"].read_text().splitlines(keepends=True)
    f["journal"].write_text("".join(reversed(lines)))
    for n in (2, 3):
        f["process"](n)
        f["observe"](n)
    with pytest.raises(ValueError, match="watch history"):
        f["build"](boundary_block=2, previous_plan=prior)


def test_real_mode_checks_cell_admission_and_freeze_not_inherited_top_flag(scenario, monkeypatch):
    f = scenario
    # Disclosed synthetic signed metadata, never a real source receipt/signature.
    f["cost"].update(lead_approved=True, status="closed", operator_request_sha256="a" * 64,
                      lead_signature=dict(name="SYNTHETIC TEST ONLY", date="2026-09-18"))
    put(f["cp"], f["cost"])
    monkeypatch.setattr(reprice.costs, "validate", lambda c: None)  # signature-branch fixture only
    f["matrix"]["cost_admission"] = reprice.d11.ref(f["cp"])
    f["matrix"]["launch_allowed"] = False  # exact assembler's inherited top-level value
    fp = put(f["root"] / "synthetic-freeze.json", dict(
        lead_approved=True, launch_authorized=True, open_gates=[],
        cost_admission=reprice.d11.ref(f["cp"])))
    f["matrix"]["freeze"] = reprice.d11.ref(fp)
    for cell in f["cells"]:
        cell.update(admitted=True, launch_allowed=True,
                    population=dict(full_validation=f["cost"]["full_validation"],
                                    item_ids=[f"synthetic-{n}" for n in range(1000)],
                                    paraphrase_counts=[1] * 1000, endpoints={}))
    put(f["mp"], f["matrix"])
    finish_block(f)
    out = f["build"](synthetic=False)
    assert out["inputs"]["published_freeze"] == reprice.d11.ref(fp)
    assert not out["lead_approved"] and not out["launch_authorized"]
    # This intentionally shaped fixture is never emitted as a real-mode report.
