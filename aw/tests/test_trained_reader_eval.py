import pccap  # noqa: F401 # isort: skip

# isort: split

import json

import numpy as np
import pytest
from tests.revision_v1.tiny_base import TinyBase

from aw.interface import ALL, InterfaceCap, InterfaceConfig
from aw.interface_readout import InterfacePositionBatchReader
from aw.pc_harm_readout import read_arm, window_hash
from aw.tests.test_interface import delta_cfg
from aw.tests.test_pc_v1_run import fixture
from aw.tests.test_wrapper import _queries, _support
from aw.trained_reader_eval import run_stream
from pccap.harness.ledger import Ledger
from pccap.revision_v1.adapt import adapt_record
from pccap.revision_v1.stage4_adapters import CellAdapter


@pytest.mark.parametrize("taps,sites", [(ALL, ALL), ((2, 3), ALL), (ALL, (3,)), ((2, 3), (3,))])
def test_interface_batch_matches_scalar_on_all_factorial_arms(taps, sites):
    base = TinyBase()
    cfg = delta_cfg()
    cap = InterfaceCap(base, cfg, Ledger(), interface=InterfaceConfig(taps, sites))
    adapt_record(cap, _support(0), cap.cfg.fast)
    queries = [np.asarray(s, np.int32) for s in _queries()]
    scalar = []
    for ids in queries:
        cap.reset_queries()
        scalar.append(np.asarray(cap.predict(ids).logits))
    adapter = CellAdapter(cap, "R1_learned_ff")
    reader = InterfacePositionBatchReader(adapter, batch_size=2)
    before = cap.state_hash()
    actual = []
    for start in range(0, len(queries), 2):
        actual.extend(reader.last_logits_batch(queries[start : start + 2]))
    np.testing.assert_allclose(actual, scalar, atol=3e-6, rtol=3e-5)
    assert cap.state_hash() == before
    assert all(e["starting_bank"] == min(sites) for e in reader.events if "starting_bank" in e)
    inactive = [i - 1 for i in ALL if i not in sites]
    if inactive:
        assert not np.any(cap.store.records[0].delta[:, inactive])


def test_native_endpoints_snapshots_and_harm_use_new_reader_without_memory_leak(tmp_path):
    tok, items, endpoints = fixture()
    # Convert the tiny EditItems back to the same minimal public row contract.
    payload = dict(
        items=[
            dict(
                item_id=it.item_id,
                fact_id=it.fact_id,
                prompt=it.prompt,
                answer="z",
                aliases=["z"],
                paraphrases=[it.prompt + "?"],
                dataset="zsre",
            )
            for it in items
        ],
        endpoints=endpoints,
    )
    base = TinyBase()
    cfg = delta_cfg()
    cfg.fast.delta_steps = 1
    cap = InterfaceCap(base, cfg, Ledger(), interface=InterfaceConfig((2, 3), (3,)))
    adapter = CellAdapter(cap, "R1_learned_ff")
    out = tmp_path / "stream"
    finish = run_stream(
        adapter,
        tok,
        payload,
        [1, 2],
        out,
        tmp_path / "resources",
        dict(population="cpu_smoke"),
        max_new=2,
        guard=lambda: None,
    )
    assert finish["status"] == "complete" and len(cap.store.records) == 2
    cp = json.loads((out / "checkpoint-2.json").read_text())
    assert cp["metrics"]["RET-ES"]["planned"] == 2
    assert cp["metrics"]["near_miss"]["scored"] == cp["metrics"]["revision"]["scored"] == 1
    assert cp["snapshot"]["acquisition"] == "adjoint"
    reader = InterfacePositionBatchReader(adapter, batch_size=2)
    w = np.int32([[4, 11, 17]])
    result = read_arm(
        reader, w, dict(positions=2, windows_sha256=window_hash(w)), tmp_path / "harm"
    )
    assert result["state_sha256"] == cap.state_hash()
