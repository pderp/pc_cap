"""Missing PC values stay pending; experiment populations and pairing are explicit."""

import copy
import json

import pytest

from aw import presentation_pc as p
from aw.pc_v0_report import compare, expected_cells


def report():
    rows = []
    for c in expected_cells(5):
        value = 0.7 if c["arm"] == "SE-A" else 0.6
        rows.append(
            dict(
                c,
                status="complete",
                pair_identity={"same_inputs": True},
                metrics={k: value for k in ("ES", "RET-ES", "RET-GS", "LS")},
                secondary={
                    k: None
                    for k in (
                        "bounded_es_immediate",
                        "bounded_ret_es_end",
                        "bounded_ret_gs_end",
                        "bounded_ls_end",
                    )
                },
                finish=dict(
                    elapsed_process_seconds=10,
                    ledger=dict(total=dict(full_forwards=9, reverses=9, settle_iters=8)),
                ),
            )
        )
    cells, pairs, aggregates = compare(rows, expected_cells(5))
    return dict(
        smoke=False,
        expected_cells=60,
        cells=cells,
        pairs=pairs,
        aggregates=aggregates,
        sources_sha256={},
    )


def test_pc3_slots_preserve_adverse_direction_and_realization_values():
    slots = {}
    r = report()
    assert p.v0_values(r, slots, {}).startswith("measured")
    assert slots["v0.zsre.ret_gs"] == "-0.1"
    assert slots["v0.zsre.ret_gs.realizations"] == "-0.1, -0.1, -0.1"
    assert slots["v0.SE-E.seconds"] == "300"
    bad = copy.deepcopy(r)
    bad["aggregates"][0]["mean"] = 1
    with pytest.raises(ValueError, match="reproduce"):
        p.v0_values(bad, {}, {})
    bad = copy.deepcopy(r)
    bad["smoke"] = True
    with pytest.raises(ValueError, match="smoke"):
        p.v0_values(bad, {}, {})


def test_pending_does_not_insert_partial_effects(tmp_path):
    r = report()
    r["cells"][0]["status"] = "unfinished"
    slots = {}
    assert p.v0_values(r, slots, {}).startswith("pending") and not slots
    register = tmp_path / "sources.json"
    register.write_text(
        json.dumps(dict(sources={"v0_report": dict(path=str(tmp_path / "future-output.json"))}))
    )
    resolved = p.resolve(register)
    assert not resolved["slots"] and "pending" in resolved["status"]["v0_report"]
    assert p.substitute("Δ={{v0.zsre.ret_gs}}", resolved["slots"]) == "Δ=PENDING"
    assert p.substitute("{{x}}", {"x": p.present(None)}) == "UNAVAILABLE"


def test_harm_refuses_wrong_population_and_duplicate_pairs():
    with pytest.raises(ValueError, match="fixture"):
        p.harm_values(dict(smoke=True), "v0", {}, {})
    with pytest.raises(ValueError, match="coverage"):
        p.harm_values(dict(smoke=False, selection=dict(positions=6), cells=[]), "v0", {}, {})
    from aw.pc_v1_run import design

    cells = design(False)
    pair = dict(dataset="zsre", realization=0, order=100)
    with pytest.raises(ValueError, match="duplicate"):
        p.harm_values(
            dict(smoke=False, selection=dict(positions=245237), cells=cells, pairs=[pair, pair]),
            "v1",
            {},
            {},
        )


def test_fixed_v5_slots_require_all_cells_and_select_final_checkpoint(tmp_path):
    from aw.pc_v1_run import cell_name, plan

    design = plan(False)
    (tmp_path / "plan.json").write_text(json.dumps(design))
    folders = []
    for c in design["cells"]:
        folder = tmp_path / cell_name(c)
        folder.mkdir()
        folders.append(folder)
        cfg = dict(
            cell=c,
            population=design["population"],
            sources=design["sources"],
            inputs=design["recipes"][c["dataset"]],
            item_ids=["same-inputs"],
            endpoints_sha256="same-endpoints",
            initial_inference_state="fresh-memory",
            base_sha256="same-base",
            reader_sha256="same-reader",
        )
        (folder / "config.json").write_text(json.dumps(cfg))
        for n in (100, 300):
            snap = folder / f"fixture-{n}.snapshot"
            snap.write_bytes(b"synthetic presentation fixture; not a model checkpoint")
            value = 0.5 if c["arm"] == "SE-A" else (0.75 if n == 100 else 0.25)
            cp = dict(
                checkpoint=n,
                snapshot=dict(
                    path=str(snap), sha256=p.sha(snap), credit=design["credit"]["arms"][c["arm"]]
                ),
                metrics={
                    k: dict(value=value)
                    for k in ("ES", "RET-ES", "RET-GS", "LS", "near_miss", "revision")
                },
            )
            (folder / f"checkpoint-{n}.json").write_text(json.dumps(cp))
        finish = dict(
            status="complete",
            items_completed=300,
            checkpoints_completed=[100, 300],
            config_sha256=p.sha(folder / "config.json"),
            base_hash_after="same-base",
            reader_hash_after="same-reader",
            elapsed_process_seconds=12,
        )
        (folder / "finish.json").write_text(json.dumps(finish))
    slots = {}
    assert p.v1_values(tmp_path, slots, {}).startswith("measured")
    assert slots["v1.zsre.100.ret_gs"] == "0.25"
    assert slots["v1.zsre.ret_gs"] == slots["v1.zsre.300.ret_gs"] == "-0.25"
    assert slots["v1.SE-E.seconds"] == "24"
    finish["status"] = "failed"
    (folders[-1] / "finish.json").write_text(json.dumps(finish))
    slots = {}
    assert p.v1_values(tmp_path, slots, {}).startswith("pending") and not slots


def test_every_authored_slot_has_a_resolvable_family():
    import re
    from pathlib import Path

    files = list((p.ROOT / "docs/presentation/deck_v3").glob("slide*.md"))
    files.append(p.ROOT / "docs/presentation/deck_v3/diagram-specs.json")
    for f in files:
        for slot in re.findall(r"\{\{([^}]+)\}\}", Path(f).read_text()):
            assert slot.startswith(("v0.", "v1.", "awb.", "depth.", "control."))
            assert re.fullmatch(
                r"(v0|v1)\.(zsre|counterfact)\.(?:(100|300)\.)?(es|ret_es|ret_gs|ls|near_miss|revision|harm_es99_difference|harm_mean_difference)(\.(realizations|range))?|(v0|v1)\.(SE-A|SE-E|harm)\.seconds|awb\.(hours|(zsre|counterfact)\.gs_change)|depth\.(1|8|32)\.RET-(ES|GS)|control\.random\.(es|n)",
                slot,
            )
