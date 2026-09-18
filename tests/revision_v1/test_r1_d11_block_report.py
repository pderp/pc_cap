"""Synthetic receipt accounting and report cursors; never execute a model."""

import json
from pathlib import Path
from uuid import uuid4

import pytest
from scripts import r1_77f_scheduler as scheduler
from scripts import r1_d11_block_report as report


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n")
    return path


@pytest.fixture
def fixture(monkeypatch):
    root = report.ROOT.parent / "assets/runs/pc_cap/R1/rehearsal_fixtures/round35" / uuid4().hex
    root.mkdir(parents=True)
    monkeypatch.setattr(report, "ROOT", root)
    monkeypatch.setattr(report.queue, "ROOT", root)
    monkeypatch.setattr(report.queue.analysis, "ROOT", root)
    cells = []
    for n in range(3):
        cell = dict(
            condition="synthetic",
            dataset="zsre",
            realization=0,
            order=n,
            block_number=1 if n < 2 else 2,
            within_block_order=n + 1,
            checkpoints=[1],
            manifest_sha256=str(n) * 64,
            result_dir=str(root / f"results/cell{n}"),
            ceilings=dict(wall_seconds=100),
        )
        cell["cell_id"] = report.queue.analysis.coordinate_id(cell)
        cells.append(cell)
    mp = put(
        root / "matrix.json",
        dict(
            scope="confirmatory",
            cells=cells,
            shared_process_hours=750,
            fidelity_watch=report.watch.binding(),
        ),
    )
    receipts, journal = root / "logs/queue", root / "results/watch/observations.jsonl"
    complete = set()

    def load(cell, files, scope):
        done = cell["cell_id"] in complete
        return dict(
            status="complete" if done else "missing",
            artifact_complete=done,
            missing_checkpoints=[] if done else [1],
        )

    # Only certification is stubbed. Actual queue inventory, receipt verification,
    # retry history, attempt replacement and watch replay run unchanged.
    monkeypatch.setattr(report.queue.analysis, "load_cell", load)

    def process(n, seq=0, *, seconds=10, driver_seconds=None, failure=False, finish=True):
        cell = cells[n]
        attempt = Path(cell["result_dir"]) / f"attempt-{seq:04d}"
        if driver_seconds is not None:
            put(
                attempt / ("failure.json" if failure else "result.json"),
                dict(attempt_wall_seconds=driver_seconds),
            )
        start = dict(
            cell_id=cell["cell_id"],
            matrix_sha256=report.queue.sha(mp),
            retry_policy=scheduler.POLICY,
        )
        folder = receipts / f"cell{n}-process{seq}"
        sp = put(folder / "start.json", start)
        if finish:
            put(
                folder / "finish.json",
                dict(
                    start,
                    start_sha256=report.queue.sha(sp),
                    charged_process_wall_seconds=seconds,
                    new_attempts=[str(attempt)] if driver_seconds is not None else [],
                    failure_class="cell" if failure else None,
                ),
            )
        return folder

    def observe(n, *, kl=0.002, dev=False):
        cell = cells[n]
        coords = {k: cell[k] for k in report.queue.analysis.COORDS}
        identity = dict(
            mode="stage4_development_cell" if dev else "stage4_sealed_cell",
            recipe_sha256=cell["manifest_sha256"],
            cell=coords,
        )
        obs = dict(
            identity=identity,
            cell_id=report.watch.full.digest(identity),
            cell=coords,
            scope="development" if dev else "confirmatory",
            recipe=dict(path="synthetic", sha256=cell["manifest_sha256"]),
            references={
                r: dict(kl=dict(mean_signed=kl), loss=dict(mean_signed=0.0))
                for r in ("original", "capoff")
            },
        )
        event = dict(
            policy=report.watch.POLICY,
            observation=obs,
            observation_sha256=report.watch.full.digest(obs),
            recorded_utc="2026-09-18T12:00:00+00:00",
        )
        journal.parent.mkdir(parents=True, exist_ok=True)
        with journal.open("a") as stream:
            stream.write(report.watch.encoded(event))

    def build(**kw):
        return report.build(mp, receipt_root=receipts, journal=journal, **kw)

    return dict(
        root=root,
        cells=cells,
        mp=mp,
        receipts=receipts,
        journal=journal,
        complete=complete,
        process=process,
        observe=observe,
        build=build,
    )


def test_overlap_and_failed_startup_are_charged_without_double_count(fixture):
    f = fixture
    f["process"](0, seconds=20, driver_seconds=15)
    f["process"](1, seconds=30, failure=True)  # Failed before creating an attempt.
    f["complete"].add(f["cells"][0]["cell_id"])
    out = f["build"]()
    assert out["cost_ledger"]["charged_seconds"] == 50
    assert out["cost_ledger"]["uncovered_driver_seconds"] == 0
    assert out["inventory"]["cost"]["known_attempt_hours"] == 50 / 3600
    assert out["inventory"]["cost"]["projected_total_hours"] == pytest.approx((50 + 2 * 115) / 3600)
    assert "not an elapsed-time forecast" in report.text(out)


def test_exhausted_failure_is_incomplete_but_processed_boundary(fixture):
    f = fixture
    f["process"](0, seconds=20, driver_seconds=15)
    f["complete"].add(f["cells"][0]["cell_id"])
    f["process"](1, seconds=7, failure=True)
    f["process"](1, seq=1, seconds=8, failure=True)
    out = f["build"](boundary_block=1)
    assert out["boundary_ready"]
    assert len(out["inventory"]["incomplete_cells"]) == 2
    assert out["cost_ledger"]["charged_seconds"] == 35
    # Entire matrix projection still includes untouched block 2.
    assert out["inventory"]["cost"]["projected_total_hours"] == pytest.approx(150 / 3600)
    assert "exhausted=True" in report.text(out)


def test_open_process_cost_is_unknown_and_boundary_refuses(fixture):
    f = fixture
    f["process"](0, seconds=20, finish=False)
    out = f["build"](boundary_block=1)
    assert out["inventory"]["cost"]["projected_total_hours"] is None
    assert out["inventory"]["cost"]["unknown_attempts"]
    assert not out["boundary_ready"]
    assert "lower bound" in report.text(out)


def test_next_block_can_run_while_finished_boundary_is_reported(fixture):
    f = fixture
    for n in (0, 1):
        f["process"](n, seconds=20)
        f["complete"].add(f["cells"][n]["cell_id"])
    f["process"](2, finish=False)
    out = f["build"](boundary_block=1)
    assert out["boundary_ready"]
    assert out["boundary_known_process_hours"] == 40 / 3600
    assert out["inventory"]["cost"]["projected_total_hours"] is None
    assert "lower bound" in report.text(out)


def test_uncovered_legacy_driver_time_remains_visible(fixture):
    f = fixture
    put(
        Path(f["cells"][0]["result_dir"]) / "attempt-0000/result.json", dict(attempt_wall_seconds=3)
    )
    out = f["build"]()
    assert out["cost_ledger"]["uncovered_driver_seconds"] == 3
    assert "startup overhead is not fully measured" in report.text(out)


def test_bad_process_receipt_cannot_hide_cost(fixture):
    folder = fixture["process"](0)
    end = json.loads((folder / "finish.json").read_text())
    end["start_sha256"] = "wrong"
    put(folder / "finish.json", end)
    with pytest.raises(ValueError, match="start identity changed"):
        fixture["build"]()


def test_watch_delta_uses_prefix_and_keeps_development_scope(fixture):
    f = fixture
    f["observe"](0, kl=0.002, dev=True)
    first = f["build"]()
    assert first["watch"]["entries"][0]["queue_cell_id"] is None
    assert first["watch"]["alerts"] == []
    previous = put(f["root"] / "logs/first.json", first)
    f["observe"](1, kl=0.005)
    second = f["build"](previous=previous)
    assert second["watch"]["new_observations"] == 1
    assert second["watch"]["new_queue_observations"] == 1
    assert len(second["watch"]["entries"]) == len(second["watch"]["alerts"]) == 1
    assert second["watch"]["entries"][0]["queue_cell_id"] == f["cells"][1]["cell_id"]
    assert "CREEP ALERT" in report.text(second)
    same = f["build"](previous=put(f["root"] / "logs/second.json", second))
    assert same["watch"]["entries"] == same["watch"]["alerts"] == []
    # Re-reporting against the last POSTED report does not silently mark delivery.
    assert f["build"](previous=previous)["watch"]["entries"] == second["watch"]["entries"]


@pytest.mark.parametrize("mutation", ["truncate", "rewrite", "torn"])
def test_watch_history_damage_rejected(fixture, mutation):
    f = fixture
    f["observe"](0, dev=True)
    prior = put(f["root"] / "logs/first.json", f["build"]())
    raw = f["journal"].read_bytes()
    if mutation == "truncate":
        f["journal"].write_bytes(b"")
    elif mutation == "rewrite":
        f["journal"].write_bytes(raw.replace(b"12:00:00", b"12:01:00"))
    else:
        f["journal"].write_bytes(raw + b"{")
    with pytest.raises(ValueError, match="prefix rewritten|torn watch"):
        f["build"](previous=prior)


def test_previous_report_identity_and_digest_checked(fixture):
    f = fixture
    prior = f["build"]()
    path = put(f["root"] / "logs/first.json", prior)
    with pytest.raises(ValueError, match="different queue"):
        f["build"](previous=path, workers=1)
    prior["complete_cells"].append("fabricated")
    put(path, prior)
    with pytest.raises(ValueError, match="digest differs"):
        f["build"](previous=path)


def test_missing_required_watch_prevents_boundary(fixture, monkeypatch):
    f = fixture
    monkeypatch.setattr(report.queue, "validate_watch", lambda m: True)
    for n in (0, 1):
        f["process"](n)
        f["complete"].add(f["cells"][n]["cell_id"])
    assert not f["build"](boundary_block=1)["boundary_ready"]
    f["observe"](0)
    f["observe"](1)
    assert f["build"](boundary_block=1)["boundary_ready"]


def test_concurrent_new_process_refuses_incoherent_snapshot(fixture, monkeypatch):
    original = report.cost_ledger

    def changing(inv):
        fixture["process"](0)
        return original(inv)

    monkeypatch.setattr(report, "cost_ledger", changing)
    with pytest.raises(ValueError, match="queue changed"):
        fixture["build"]()


def test_new_output_only_and_no_queue_or_watch_writes(fixture, capsys):
    f = fixture
    f["observe"](0, dev=True)
    before = {p: p.read_bytes() for p in f["root"].rglob("*") if p.is_file()}
    output = f["root"] / "logs/report"
    argv = [
        "--matrix",
        str(f["mp"]),
        "--receipt-root",
        str(f["receipts"]),
        "--journal",
        str(f["journal"]),
        "--output-dir",
        str(output),
    ]
    assert report.main(argv) == 0
    assert all(p.read_bytes() == raw for p, raw in before.items())
    assert not f["receipts"].exists()
    assert (output / "lead-queue.txt").read_text() == capsys.readouterr().out
    with pytest.raises(FileExistsError):
        report.main(argv)


def test_undeclared_block_and_sealed_input_refused(fixture):
    with pytest.raises(ValueError, match="declared block"):
        fixture["build"](boundary_block=99)
    with pytest.raises(PermissionError, match="unsealed"):
        report.local(fixture["root"] / "manifests/confirm/secret.json")
