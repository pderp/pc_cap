"""R1-27 fixtures superseding R1-26 assumptions, without editing the old audit.

CPU-only. Driver preflight statements are compiled from the actual source;
only the assets root is relocated into the test directory. No model main runs.
"""

from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import pccap  # noqa: F401
from pccap.harness.ledger import Ledger
from pccap.harness.snapshot import ItemGuard
from pccap.revision_v1.adapt import FastConfig, adapt_record
from pccap.revision_v1.contracts import MemoryRecord
from pccap.revision_v1.learner import RevisionCap
from pccap.revision_v1.memory import CapacityError, RecordStore
from pccap.revision_v1.reader import pair_scores
from tests.revision_v1.test_learner_cpu import _cfg, _support
from tests.revision_v1.tiny_base import TinyBase

ROOT = Path(__file__).resolve().parents[2]


def cap_config():
    return replace(_cfg(null_threshold=1.01), fast=FastConfig(steps=0))


def test_constructor_and_different_valid_requested_ceiling():
    cfg = cap_config()
    cap = RevisionCap(TinyBase(), cfg, Ledger())
    with pytest.raises(CapacityError):
        RevisionCap(cap.base, replace(cfg, ceiling_bytes=1), Ledger(), params=cap.params)
    adapt_record(cap, _support(0), cfg.fast)
    small = RevisionCap(
        cap.base,
        replace(cfg, ceiling_bytes=cap.store.weights_bytes + 1),
        Ledger(),
        params=cap.params,
    )
    before = small.state_hash()
    with pytest.raises(RuntimeError, match="semantic configuration"):
        small.import_state(cap.export_state())
    assert small.state_hash() == before
    assert small.store.bytes()["total"] <= small.cfg.ceiling_bytes


def test_import_validates_before_adoption_and_recomputes_weight_charge():
    cfg = cap_config()
    base = TinyBase()
    template = RevisionCap(base, cfg, Ledger())
    cfg = replace(cfg, ceiling_bytes=template.store.weights_bytes + 250)
    cap = RevisionCap(base, cfg, Ledger(), params=template.params)
    adapt_record(cap, _support(0), cfg.fast)
    before = cap.state_hash()
    forged = cap.export_state().clone()
    forged.scalars["ceiling_bytes"] = 10**12
    forged.scalars["weights_bytes"] = 0
    forged.arrays["delta/s0"] = np.ones((3, 3, cfg.reader.d), np.float32)
    with pytest.raises(CapacityError):
        cap.import_state(forged)
    assert cap.state_hash() == before
    clean = cap.export_state().clone()
    clean.scalars["weights_bytes"] = 0
    cap.import_state(clean)
    assert cap.state_hash() == before


def test_raw_store_requires_explicit_validation():
    cap = RevisionCap(TinyBase(), cap_config(), Ledger())
    forged = cap.export_state().clone()
    forged.scalars["ceiling_bytes"] = 1
    raw = RecordStore.from_state(forged)
    # The raw constructor is still unchecked; cap.import_state calls validate.
    with pytest.raises(CapacityError):
        raw.validate()


def test_failed_delta_revision_is_atomic_billed_and_guard_restorable():
    cfg = cap_config()
    base = TinyBase()
    template = RevisionCap(base, cfg, Ledger())
    # 212 bytes per tiny support, plus one spare byte: both records fit, deltas do not.
    cfg = replace(cfg, ceiling_bytes=template.store.weights_bytes + 425)
    cap = RevisionCap(base, cfg, Ledger(), params=template.params)
    adapt_record(cap, _support(0), cfg.fast)
    before, before_bytes = cap.state_hash(), cap.store.bytes()
    tr, cost = adapt_record(
        cap, _support(1, fact="f0", rev=2), FastConfig(steps=0, delta_steps=2, delta_lr=0.1)
    )
    assert tr.rolled_back_reason == "delta_capacity" and cost.full_forwards > 0
    assert cap.state_hash() == before and cap.store.bytes() == before_bytes
    assert cap.store.get("s0").active and cap.store.get("s0").superseded_by is None
    assert "s1" not in cap.store._by_id
    with ItemGuard(cap, cap.ledger):
        cap.store.remove("s0")
    assert cap.state_hash() == before and cap.store.bytes() == before_bytes


def test_mixed_adaptation_refused_before_base_work():
    cap = RevisionCap(TinyBase(), cap_config(), Ledger())
    before, calls = cap.state_hash(), dict(cap.base.calls)
    with pytest.raises(NotImplementedError):
        adapt_record(cap, _support(0), FastConfig(steps=1, delta_steps=1))
    assert cap.state_hash() == before and cap.base.calls == calls


def test_dot_reader_and_store_select_same_record():
    cfg = cap_config()
    cap = RevisionCap(TinyBase(), replace(cfg, reader=replace(cfg.reader, cosine=False)), Ledger())
    q = np.zeros(8, np.float32)
    q[:2] = [1, 1]
    k1, k2 = np.zeros(8, np.float32), np.zeros(8, np.float32)
    k1[0], k2[0], k2[1] = 10, 1, 0.1
    for rid, key in (("large", k1), ("aligned", k2)):
        cap.store.add(MemoryRecord(rid, rid, 1, -1, key, np.zeros(6, np.float32)))
    idx = int(np.asarray(pair_scores(cap.cfg.reader, q, np.stack([k1, k2]))).argmax())
    assert cap.store.metric == "dot"
    assert ["large", "aligned"][idx] == cap.store.retrieve(q, 1)[0].record_id == "large"


def test_selection_forward_returned_once_per_query():
    cap = RevisionCap(TinyBase(), replace(cap_config(), cache_prompt_pass=False), Ledger())
    adapt_record(cap, _support(0), cap.cfg.fast)
    ids = np.asarray(_support(0).prompt_ids, np.int32)
    cap.reset_queries()
    before = cap.base.calls["forward"]
    first = cap.predict(ids)
    assert first.cost.full_forwards == cap.base.calls["forward"] - before == 2
    before = cap.base.calls["forward"]
    later = cap.predict(np.concatenate([ids, np.int32([4])]))
    assert later.cost.full_forwards == cap.base.calls["forward"] - before == 1


def admission(tmp_path):
    tree = ast.parse((ROOT / "scripts/r1_13_stream_eval.py").read_text())
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    names = {"tag", "rd", "destinations", "taken"}
    statements = [
        n
        for n in main.body
        if (
            isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id in names for t in n.targets)
        )
        or (isinstance(n, ast.If) and ast.unparse(n.test) == "taken")
    ]
    assert len(statements) == 6, "preflight changed: review extraction"
    fn = ast.parse("def preflight(args, OUT, ROOT):\n    return tag, rd, destinations\n").body[0]
    fn.body = statements + fn.body
    assets = tmp_path / "assets"

    def relocated_path(value):
        return assets / "runs" if str(value) == "/home/derp/cap/assets/runs" else Path(value)

    scope = {"Path": relocated_path}
    exec(
        compile(
            ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
            "<driver-preflight>",
            "exec",
        ),
        scope,
    )
    root = tmp_path / "repo"
    return scope["preflight"], root, assets


def test_dataset_and_orphan_summary_preflight(tmp_path):
    fn, root, _ = admission(tmp_path)
    out = root / "results/R1"
    a = SimpleNamespace(tag="fixture", dataset="zsre", theta="unused/theta.npz")
    ztag, zpath, _ = fn(a, out, root)
    ctag, cpath, _ = fn(SimpleNamespace(**{**vars(a), "dataset": "counterfact"}), out, root)
    assert ztag != ctag and zpath != cpath
    out.mkdir(parents=True)
    (out / f"stream_eval_{ztag}.json").write_text("{}")
    with pytest.raises(SystemExit, match="already has artifacts"):
        fn(a, out, root)


def test_existing_run_directory_preflight(tmp_path):
    fn, root, _ = admission(tmp_path)
    out = root / "results/R1"
    a = SimpleNamespace(tag="existing", dataset="zsre", theta="unused")
    _, rd, _ = fn(a, out, root)
    rd.mkdir(parents=True)
    with pytest.raises(SystemExit):
        fn(a, out, root)


def test_actual_orphan_checkpoint_root_is_refused(tmp_path):
    fn, root, assets = admission(tmp_path)
    out = root / "results/R1"
    a = SimpleNamespace(tag="orphan-checkpoint", dataset="zsre", theta="unused")
    _, rd, _ = fn(a, out, root)
    # Same expression as harness.runs.run_stream; assert its source has not changed.
    tree = ast.parse((ROOT / "src/pccap/harness/runs.py").read_text())
    run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run_stream")
    ckpt = next(
        n.value
        for n in run.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "ckpt_dir" for t in n.targets)
    )
    actual = eval(
        compile(ast.Expression(ckpt), "<harness-checkpoint-path>", "eval"),
        {"Path": Path, "ASSETS_ROOT": str(assets), "run_dir": rd, "ROOT": root},
    )
    actual.mkdir(parents=True)
    with pytest.raises(SystemExit):
        fn(a, out, root)
