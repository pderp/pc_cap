"""Synthetic end-to-end confirmation CLI study (interim report 2 §5 acceptance gate; R2-02/03/04/05).

Uses the real ``pccap run`` entry (``runner.main``), the real scheduler, a synthetic frozen manifest
bound to synthetic realization files in a temporary tree, and a fake registered stage runner that
records what it received and opens nothing. Checks: zero payload opens on denied access (no freeze,
draft freeze, unbound file, unavailable arm); 150 scheduled jobs → 150 distinct run directories with
both hashes recorded; rerun protection and ``--force``; the selection rule gives every order the same
item subset; ``run_stream`` enforces a resource stop and reconciles ledger deltas with the ledger.
CPU only; never touches ``manifests/frozen.json`` or the sealed manifests.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

import pccap  # noqa: F401
import pccap.harness.stage_s0  # noqa: F401,E402  (register the real runners first so the fake override below survives main's imports)
import pccap.harness.stage_s3  # noqa: F401,E402
import pccap.harness.stage_s4  # noqa: F401,E402
import pccap.harness.stage_s5  # noqa: F401,E402
from pccap.analysis import s4_05, s4_06  # noqa: E402
from pccap.contracts import CostRecord, EditItem, ItemOutcome, MemoryReport
from pccap.data.selection import RULE, stream_ids, subset_ids
from pccap.harness import runner
from pccap.harness.freeze import build
from pccap.harness.ledger import Ledger
from pccap.harness.schedule import jobs_from_manifest
from pccap.harness.snapshot import LearnerState

ROOT = Path(__file__).resolve().parents[2]


def synthetic_manifest(ds: str, r: int, n: int = 12) -> dict:
    items = [{"item_id": f"{ds}-{r}-{i}", "subject": f"s{i}", "prompt": "p", "answer": "a", "aliases": ["a"], "paraphrases": [], "locality_prompts": [],
              "prompt_ids": [1, 2, 3], "answer_ids": [4, 198], "answer_tokens": 2, "dataset": ds, "fact_id": f"f{i}"} for i in range(n)]
    ids = [it["item_id"] for it in items]
    rng = np.random.default_rng(r)
    orders = {str(s): [ids[i] for i in rng.permutation(n)] for s in (100, 101, 102, 103, 104)}
    named = {str(s): {"seed_cap_init": 1000 * r + 10 * (int(s) - 100), "seed_router": 1000 * r + 10 * (int(s) - 100) + 1, "seed_replay": 1000 * r + 10 * (int(s) - 100) + 2} for s in orders}
    return {"name": f"{ds}_r{r}", "mode": "confirm", "dataset": ds, "realization": r, "seed": r, "order_seeds": [100, 101, 102, 103, 104],
            "orders": orders, "named_seeds": named, "n_items": n, "source_pool_sha256": "0" * 64, "items": items}


@pytest.fixture()
def synthetic_root(tmp_path, monkeypatch):
    root = tmp_path / "root"
    (root / "manifests" / "confirm").mkdir(parents=True)
    (root / "results").mkdir()
    ids = {"zsre": {}, "counterfact": {}, "grammar": None}
    for ds in ("zsre", "counterfact"):
        for r in range(3):
            p = root / "manifests" / "confirm" / f"{ds}_r{r}.json"
            p.write_text(json.dumps(synthetic_manifest(ds, r)))
            ids[ds][p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    man, _ = build(draft=False)
    man.update({"draft": False, "name": "synthetic-frozen", "dataset_ids": ids, "confirm_dir": "manifests/confirm",
                "stream_lengths": {"zsre": 8, "counterfact": 6, "grammar_train_count": None, "c0_initial": 4},
                "arm_availability": {"B4": "unavailable (synthetic)"}})
    (root / "manifests" / "frozen.json").write_text(json.dumps(man, default=float))
    monkeypatch.setattr(runner, "ROOT", root)
    monkeypatch.setattr(runner, "RESULTS", root / "results")
    monkeypatch.chdir(root)
    return root, man


def _args(job: dict, **kw) -> SimpleNamespace:
    base = {"stage": "S4", "arm": job["arm"], "base": "BP", "read": "h", "realization": job["realization"], "perm": job["perm"],
            "manifest": job["manifest"], "mode": "confirm", "task": None, "dry_run": False, "dataset": job["dataset"], "force": False,
            "no_lease": True, "projected_seconds": 1.0}
    base.update(kw)
    return SimpleNamespace(**base)


def test_denied_access_opens_no_payload(synthetic_root):
    root, man = synthetic_root
    job = {"arm": "C2", "realization": 0, "perm": 0, "manifest": "manifests/confirm/zsre_r0.json", "dataset": "zsre"}
    reads: list[str] = []
    real = Path.read_bytes

    def counting(self):
        reads.append(str(self))
        return real(self)

    with patch.object(Path, "read_bytes", counting):
        (root / "manifests" / "frozen.json").rename(root / "manifests" / "frozen.json.away")
        assert runner.main(_args(job)) == 2  # no freeze
        assert not any("confirm/zsre_r0.json" in r for r in reads)
        (root / "manifests" / "frozen.json.away").rename(root / "manifests" / "frozen.json")
        draft = json.loads((root / "manifests" / "frozen.json").read_text())
        draft["draft"] = True
        (root / "manifests" / "frozen.draft.json").write_text(json.dumps(draft))
        (root / "manifests" / "frozen.json").write_text(json.dumps(draft))
        assert runner.main(_args(job)) == 2  # draft flag
        (root / "manifests" / "frozen.json").write_text(json.dumps(man, default=float))
        assert runner.main(_args(job, manifest="manifests/confirm/other.json")) == 2  # unbound file
        assert runner.main(_args(job, arm="B4")) == 2  # unavailable arm
    assert not any("confirm/zsre_r0.json" in r or "confirm/other.json" in r for r in reads)


def test_schedule_paths_unique_and_hashes_recorded(synthetic_root):
    root, man = synthetic_root
    seen = {}

    def fake_runner(ctx, rd):
        seen[str(rd)] = ctx["config"]
        return {"status": "complete"}

    real = runner.RUNNERS.get("S4")
    runner.RUNNERS["S4"] = fake_runner
    try:
        jobs = [j for j in jobs_from_manifest(man) if j["status"] == "scheduled"]
        assert len(jobs) == 150
        for j in jobs:
            assert runner.main(_args(j)) == 0
        assert len(seen) == 150
        cfg = next(iter(seen.values()))
        assert cfg["frozen_manifest_sha256"] and cfg["manifest_sha256"] == man["dataset_ids"][cfg["dataset"]][Path(cfg["manifest"]).name]
        assert cfg["experiment_id"].startswith("synthetic-frozen-")
        # rerun protection
        assert runner.main(_args(jobs[0])) == 4
        assert runner.main(_args(jobs[0], force=True)) == 0
        assert any(p.name.startswith("0.superseded-") for p in (root / "results" / "S4" / cfg["experiment_id"] / "zsre" / "C0" / "BP" / "h" / "0").iterdir())
    finally:
        if real is not None:
            runner.RUNNERS["S4"] = real


def test_selection_rule_same_subset_every_order():
    man = synthetic_manifest("zsre", 1, n=12)
    sub = subset_ids(man, 8)
    for s in man["order_seeds"]:
        ids = stream_ids(man, s, 8)
        assert set(ids) == set(sub) and len(ids) == 8
        assert stream_ids(man, s, 8, 4) == ids[:4]  # C0's scope is the prefix of the same order
    assert {tuple(stream_ids(man, s, 8)) for s in man["order_seeds"]}.__len__() > 1  # permutations differ
    assert "first n items" in RULE


class _Pred(np.ndarray):
    @property
    def logits(self):
        return self


class FakeLearner:
    """Minimal learner: charges the ledger, counts updates, exports its state; predicts a fixed distribution."""

    def __init__(self, ledger, vocab=300):
        self.ledger, self.vocab, self.n = ledger, vocab, 0

    def predict(self, ids):
        with self.ledger.call("query", full_forwards=1, tokens=len(ids)):
            pass
        out = np.zeros((len(ids), self.vocab), np.float32)
        out[:, 198] = 5.0
        return out.view(_Pred)

    def last_logits_batch(self, seqs, phase="query"):
        with self.ledger.call(phase, full_forwards=len(seqs), tokens=sum(len(s) for s in seqs)):
            pass
        out = np.zeros((len(seqs), self.vocab), np.float32)
        out[:, 198] = 5.0
        return out

    def update_item(self, item):
        with self.ledger.call("learning", full_forwards=2, reverses=2, tokens=4) as rec:
            rec.accel_seconds += 0.5  # deterministic synthetic cost
        self.n += 1
        return ItemOutcome(item.item_id, "accepted", True, [], 1, CostRecord(phase="learning", full_forwards=2, reverses=2, accel_seconds=0.5), codes=["accepted"])

    def export_state(self):
        return LearnerState(scalars={"n": self.n})

    def import_state(self, st):
        self.n = int(st.scalars["n"])

    def state_hash(self):
        return self.export_state().content_hash()

    def memory_bytes(self):
        return MemoryReport(allocated_bytes=0, occupied_bytes=0, per_bank={}, index_bytes=0, key_dim=0, value_dim=0, occupancy={}, ceiling_bytes=1)


def test_run_stream_resource_stop_and_ledger_reconciliation(tmp_path, monkeypatch):
    from pccap.harness import runs
    from pccap.harness.runs import Evaluator, run_stream

    monkeypatch.setattr(runs, "ROOT", tmp_path)
    (tmp_path / "results").mkdir()
    monkeypatch.setattr(runs, "ASSETS_ROOT", str(tmp_path / "assets"))
    ledger = Ledger()
    learner = FakeLearner(ledger)
    tok = SimpleNamespace(encode=lambda s: [1, 2], decode=lambda ids: "a")
    ev = Evaluator(SimpleNamespace(), tok, [], None)
    items = [EditItem(item_id=f"i{k}", digest=hashlib.sha256(str(k).encode()).digest()[:16], prompt="p", answer="a", aliases=["a"], paraphrases=[],
                      locality_prompts=[], prompt_ids=np.asarray([1, 2, 3], np.int32), answer_ids=np.asarray([4, 198], np.int32)) for k in range(6)]
    run_dir = tmp_path / "results" / "S4" / "x"
    m = run_stream(learner, items, None, None, ev, run_dir, ledger, checkpoints=(2,), resource_stop_seconds=1.2)
    rows = [json.loads(line) for line in (run_dir / "items.jsonl").read_text().splitlines() if line.strip()]
    assert m["status"] == "resource_stop" and 1 <= len(rows) < 6 and learner.n == len(rows)
    # ledger deltas + rescoring deltas reconcile with the final ledger total (nothing uncounted)
    ck = json.loads((run_dir / "checkpoints.json").read_text())
    accounted = sum(r["ledger_delta"]["update"]["total"] + r["ledger_delta"]["immediate_eval"]["total"] for r in rows) + sum(c["rescoring_accel_seconds"]["total"] for c in ck)
    assert abs(accounted - ledger.totals()["total"]["accel_seconds"]) < 1e-9
    assert rows[-1]["ledger_delta"]["cumulative"]["total"] <= ck[-1]["ledger_accel_seconds_at_checkpoint"]["total"]


# ----------------------------------------------------------------------------- Lane V repairs (V-01..V-06)
def _writing_runner(seen):
    """Fake stage runner that writes the files the collectors read (metrics/items/checkpoints) without any model."""

    def fake(ctx, rd):
        cfg = ctx["config"]
        seen[str(rd)] = cfg
        items = [{"index": i, "item_id": f"{cfg['dataset']}-{cfg['realization']}-{i}", "es": 1.0, "gs": None, "answer_tokens": 2, "cost": {"accel_seconds": 0.1},
                  "ledger_delta": {"update": {"total": 1.0, "learning": 1.0, "query": 0.0}, "immediate_eval": {"total": 9.0 if cfg["arm"] == "C2" else 0.0, "learning": 0.0, "query": 9.0 if cfg["arm"] == "C2" else 0.0},
                                   "cumulative": {"total": 10.0 * (i + 1), "learning": 1.0 * (i + 1), "query": 9.0 * (i + 1)}}} for i in range(3)]
        (rd / "items.jsonl").write_text("\n".join(json.dumps(x) for x in items) + "\n")
        (rd / "checkpoints.json").write_text(json.dumps([{"tag": "end", "items": 3, "ret_es": 1.0, "ret_gs": 0.5, "ret_gs_n": 3, "locality": {"ls_complete_answer": 1.0},
                                                          "rows": [{"item_id": x["item_id"], "ret_es": 1.0, "ret_gs": 0.5} for x in items],
                                                          "ledger_accel_seconds_at_checkpoint": {"total": 31.0, "learning": 3.0, "query": 28.0}, "rescoring_accel_seconds": {"total": 1.0, "learning": 0.0, "query": 1.0}}]))
        (rd / "metrics.json").write_text(json.dumps({"stage": "S4", "arm": cfg["arm"], "status": "complete", "config": {"dataset": cfg["dataset"], "realization": cfg["realization"], "perm": cfg["perm"], "experiment_id": cfg["experiment_id"]},
                                                     "metrics": {"es_immediate": {"value": 1.0}}, "ledger_totals": {"total": {"accel_seconds": 31.0}}}))
        return {"status": "complete"}

    return fake


def test_v01_no_backend_discovery_before_lease(synthetic_root, monkeypatch):
    root, man = synthetic_root
    order = []
    import contextlib

    @contextlib.contextmanager
    def fake_lease(*a, **k):
        order.append("lease_enter")
        yield SimpleNamespace(report={})
        order.append("lease_exit")

    import pccap
    import pccap.harness.lease as lease_mod

    monkeypatch.setattr(lease_mod, "gpu_lease", fake_lease)
    monkeypatch.setattr(pccap, "determinism_report", lambda: order.append("determinism_report") or {"x": 1})
    monkeypatch.setattr(pccap, "assert_determinism", lambda: order.append("assert_determinism") or {"x": 1})
    real = runner.RUNNERS.get("S4")
    runner.RUNNERS["S4"] = lambda ctx, rd: order.append("runner") or {"status": "complete"}
    try:
        job = {"arm": "C2", "realization": 0, "perm": 0, "manifest": "manifests/confirm/zsre_r0.json", "dataset": "zsre"}
        assert runner.main(_args(job, no_lease=False)) == 0
    finally:
        runner.RUNNERS["S4"] = real
    assert order.index("lease_enter") < order.index("assert_determinism") < order.index("runner") < order.index("lease_exit")
    assert "determinism_report" not in order[: order.index("lease_enter") + 1]


def test_v06_schedule_and_config_validation(synthetic_root):
    root, man = synthetic_root
    real = runner.RUNNERS.get("S4")
    runner.RUNNERS["S4"] = lambda ctx, rd: {"status": "complete"}
    try:
        job = {"arm": "C2", "realization": 0, "perm": 0, "manifest": "manifests/confirm/zsre_r0.json", "dataset": "zsre"}
        assert runner.main(_args(job, perm=-1)) == 2
        assert runner.main(_args(job, perm=5)) == 2
        assert runner.main(_args(job, realization=3)) == 2
        assert runner.main(_args(job, base="EPC")) == 2
        assert runner.main(_args(job, read="g")) == 2
        assert runner.main(_args(job, arm="ZZ")) == 2
        # code drift: the frozen tree hash differs from the working tree → refused unless explicitly allowed
        m2 = dict(man)
        m2["code_commit"] = dict(man["code_commit"], src_tree_sha256="0" * 64)
        (root / "manifests" / "frozen.json").write_text(json.dumps(m2, default=float))
        assert runner.main(_args(job)) == 2
        assert runner.main(_args(job, allow_code_drift=True)) == 0
        (root / "manifests" / "frozen.json").write_text(json.dumps(man, default=float))
    finally:
        runner.RUNNERS["S4"] = real


def test_v03_archived_attempts_are_not_collected_and_v05_update_time(synthetic_root):
    from pccap.analysis.s4_05 import discover, views
    from pccap.analysis.s4_06 import collect_rows

    root, man = synthetic_root
    seen = {}
    real = runner.RUNNERS.get("S4")
    runner.RUNNERS["S4"] = _writing_runner(seen)
    try:
        for arm in ("C1", "C2", "CR"):
            for r in range(3):
                for o in range(5):
                    assert runner.main(_args({"arm": arm, "realization": r, "perm": o, "manifest": f"manifests/confirm/zsre_r{r}.json", "dataset": "zsre"})) == 0
        job = {"arm": "C2", "realization": 0, "perm": 0, "manifest": "manifests/confirm/zsre_r0.json", "dataset": "zsre"}
        assert runner.main(_args(job, force=True)) == 0  # one forced rerun → an archived attempt exists
    finally:
        runner.RUNNERS["S4"] = real
    exp = next(iter(seen.values()))["experiment_id"]
    rows, notes = collect_rows(root / "results" / "S4", "zsre", exp)
    keys = [(r["arm"], r["realization"], r["order"], r["item_id"]) for r in rows]
    assert len(keys) == len(set(keys)) == 3 * 15 * 3  # no duplicate rows from the archived attempt
    runs = discover([root / "results" / "S4"], exp)
    assert len(runs) == 45
    v = views(runs)
    cc = v["comparable_compute"]["zsre/0/0"]
    # V-05: C2 has 9 s of immediate evaluation per item, C1 none; update time is 1 s in both → comparable on update time
    assert cc["C1"]["within_20pct_update"] and abs(cc["C1"]["ratio_to_C2_update"] - 1.0) < 1e-9
    assert cc["C1"]["ratio_to_C2_update_plus_eval"] < 0.2
    per = next(p for p in v["per_run"] if p["arm"] == "C2" and p["realization"] == 0 and p["perm"] == 0)
    assert per["accel_seconds_total"] == 30.0  # from the cumulative ledger snapshot, not summed deltas


def test_v04_stage_allowance_refuses_when_exceeded(synthetic_root):
    root, man = synthetic_root
    seen = {}
    real = runner.RUNNERS.get("S4")
    runner.RUNNERS["S4"] = _writing_runner(seen)
    try:
        m2 = json.loads(json.dumps(man, default=float))
        m2["resource_rules"]["stage_allowance_seconds"] = {"S4": 40.0, "S5": None}
        m2["resource_rules"]["run_allowance_seconds"] = 20.0
        (root / "manifests" / "frozen.json").write_text(json.dumps(m2))
        job = {"arm": "C1", "realization": 0, "perm": 0, "manifest": "manifests/confirm/counterfact_r0.json", "dataset": "counterfact"}
        assert runner.main(_args(job)) == 0  # spent 0 + 20 ≤ 40
        assert runner.main(_args(dict(job, perm=1))) == 5  # spent 31 + 20 > 40 → refused
        cfg = json.loads((root / "results" / "S4" / next(iter(seen.values()))["experiment_id"] / "counterfact" / "C1" / "BP" / "h" / "0" / "0" / "config.json").read_text())
        assert cfg["stage_allowance_enforced"] is True and cfg["run_allowance_seconds"] == 20.0
        (root / "manifests" / "frozen.json").write_text(json.dumps(man, default=float))
    finally:
        runner.RUNNERS["S4"] = real


def test_v02_s5_frozen_authority(synthetic_root, tmp_path):
    from pccap.harness.stage_s5 import resolve_frozen_arm

    root, man = synthetic_root
    fz = json.loads(json.dumps(man, default=float))
    with pytest.raises(ValueError):
        resolve_frozen_arm({**fz, "substrate_arms": {}}, "SE-A")
    with pytest.raises(ValueError):
        resolve_frozen_arm({**fz, "calibration": {}}, "SB")
    spec, b_m, radii, path = resolve_frozen_arm(fz, "SB")
    assert spec["base"] == "BP" and set(b_m) == {1, 2, 3} and "zsre" in radii and path is None
    if fz.get("base_checkpoints", {}).get("epc"):
        bad = json.loads(json.dumps(fz))
        bad["base_checkpoints"]["epc"]["sha256"] = "0" * 64
        with pytest.raises(ValueError):
            resolve_frozen_arm(bad, "SE-A")


# ----------------------------------------------------------------------------- Lane V2 repairs (V2-01..V2-05)
def test_v2_01_frozen_identity_check():
    from pccap.harness.identity import PreflightRefusal, check_frozen_identity

    frozen = {"base_checkpoints": {"bp": {"param_digest": "bp-digest"}}, "tokenizer_rev": {"tokenizer_json_sha256": "tok-hash"}}
    base = SimpleNamespace(checksum=lambda: "bp-digest")
    tok = SimpleNamespace(file_sha256=lambda: "tok-hash")
    assert check_frozen_identity(frozen, base=base, base_kind="BP", tokenizer=tok) == {"bp_param_digest": "bp-digest", "tokenizer_json_sha256": "tok-hash"}
    with pytest.raises(PreflightRefusal):
        check_frozen_identity(frozen, base=SimpleNamespace(checksum=lambda: "other"), base_kind="BP", tokenizer=tok)
    with pytest.raises(PreflightRefusal):
        check_frozen_identity(frozen, base=base, base_kind="BP", tokenizer=SimpleNamespace(file_sha256=lambda: "other"))
    with pytest.raises(PreflightRefusal):  # a tokenizer that cannot report its identity is refused, not waved through
        check_frozen_identity(frozen, base=base, base_kind="BP", tokenizer=SimpleNamespace())
    with pytest.raises(PreflightRefusal):  # an absent frozen identity is a refusal too
        check_frozen_identity({"base_checkpoints": {"bp": {}}}, base=base, base_kind="BP")


def test_v2_01_stage_refusal_maps_to_exit_2_and_is_retryable(synthetic_root):
    from pccap.harness.identity import PreflightRefusal

    root, man = synthetic_root
    real = runner.RUNNERS.get("S4")
    calls = []

    def refusing(ctx, rd):
        calls.append(rd)
        if len(calls) == 1:
            raise PreflightRefusal("loaded BP base digest differs from the frozen one")
        return _writing_runner({})(ctx, rd)

    runner.RUNNERS["S4"] = refusing
    try:
        job = {"arm": "C1", "realization": 0, "perm": 0, "manifest": "manifests/confirm/zsre_r0.json", "dataset": "zsre"}
        assert runner.main(_args(job)) == 2
        cfg = json.loads((calls[0] / "config.json").read_text())
        assert cfg["status"] == "refused" and not (calls[0] / "metrics.json").exists() and (calls[0] / "error.json").exists()
        assert runner.main(_args(job)) == 0  # a refused attempt left nothing behind: retry without --force
        assert json.loads((calls[1] / "config.json").read_text())["status"] == "complete"
    finally:
        runner.RUNNERS["S4"] = real


def _two_experiment_tree(root, exp_a="exp-a", exp_b="exp-b", legacy=False):
    """Two identified experiments with the same cells (and optionally a run with no id) under results/S4."""
    seen = {}
    fake = _writing_runner(seen)
    for exp, ids in ((exp_a, exp_a), (exp_b, exp_b), ("legacy", None)):
        if exp == "legacy" and not legacy:
            continue
        for arm in ("C1", "C2"):
            rd = root / "results" / "S4" / exp / "zsre" / arm / "BP" / "h" / "0" / "0"
            rd.mkdir(parents=True)
            fake({"config": {"stage": "S4", "arm": arm, "dataset": "zsre", "realization": 0, "perm": 0, "experiment_id": ids}}, rd)
    return root / "results" / "S4"


def test_v2_02_specific_filter_excludes_unknown_identity(synthetic_root):
    root, _ = synthetic_root
    tree = _two_experiment_tree(root, legacy=True)
    runs = s4_05.discover([tree], "exp-a")
    assert len(runs) == 2 and {r["experiment_id"] for r in runs} == {"exp-a"}
    rows, notes = s4_06.collect_rows(tree, "zsre", "exp-a")
    assert len(rows) == 6 and {r["arm"] for r in rows} == {"C1", "C2"}
    assert any("unknown provenance" in n for n in notes)  # the legacy run is reported, never merged
    from pccap.analysis import s7_03

    assert set(s7_03.load_runs(tree, "zsre", "C2", "exp-a")) == {(0, 0)}


def test_v2_03_unfiltered_mixed_experiments_are_refused(synthetic_root):
    from pccap.analysis import s7_03

    root, _ = synthetic_root
    tree = _two_experiment_tree(root)
    both = s4_05.discover([tree])
    assert len(both) == 4 and {r["experiment_id"] for r in both} == {"exp-a", "exp-b"}
    with pytest.raises(ValueError, match="several experiments"):
        s4_05.views(both)
    with pytest.raises(ValueError, match="several experiments"):
        s4_06.collect_rows(tree, "zsre")
    with pytest.raises(ValueError, match="several experiments|two runs"):
        s7_03.load_runs(tree, "zsre", "C2")
    one = s4_05.views(s4_05.discover([tree], "exp-b"))
    assert one["experiment_id"] == "exp-b"
    out = root / "s7.json"
    assert s7_03.main(["--dataset", "zsre", "--arm", "C2", "--root", str(tree), "--out", str(out), "--experiment-id", "exp-a"]) == 0
    assert json.loads(out.read_text())["experiment_id"] == "exp-a"


def test_v2_04_stage_ceiling_without_run_allowance_is_refused(synthetic_root):
    root, man = synthetic_root
    seen = {}
    real = runner.RUNNERS.get("S4")
    runner.RUNNERS["S4"] = _writing_runner(seen)
    try:
        m2 = json.loads(json.dumps(man, default=float))
        m2["resource_rules"]["stage_allowance_seconds"] = {"S4": 0.01, "S5": None}
        m2["resource_rules"]["run_allowance_seconds"] = None
        (root / "manifests" / "frozen.json").write_text(json.dumps(m2))
        job = {"arm": "C1", "realization": 0, "perm": 0, "manifest": "manifests/confirm/zsre_r0.json", "dataset": "zsre"}
        assert runner.main(_args(job)) == 2 and not seen  # refused at admission: no run directory, nothing charged
        m2["resource_rules"]["run_allowance_seconds"] = 20.0
        m2["resource_rules"]["stage_allowance_seconds"] = {"S4": 60.0, "S5": None}
        (root / "manifests" / "frozen.json").write_text(json.dumps(m2))
        assert runner.main(_args(job)) == 0
        cfg = next(iter(seen.values()))
        assert cfg["effective_run_allowance_seconds"] == 20.0 and cfg["stage_allowance_enforced"] is True
        assert runner.main(_args(dict(job, perm=1))) == 0  # spent 31 + 20 ≤ 60: admitted, and bounded by the 20 s run allowance
        assert [c for c in seen.values() if c["perm"] == 1][0]["effective_run_allowance_seconds"] == 20.0
        assert runner.main(_args(dict(job, perm=2))) == 5  # spent 62 + 20 > 60 (same freeze, same experiment id)
    finally:
        runner.RUNNERS["S4"] = real
        (root / "manifests" / "frozen.json").write_text(json.dumps(man, default=float))


def test_v2_05_archived_attempts_count_toward_stage_spending(synthetic_root):
    root, man = synthetic_root
    seen = {}
    real = runner.RUNNERS.get("S4")
    runner.RUNNERS["S4"] = _writing_runner(seen)
    try:
        m2 = json.loads(json.dumps(man, default=float))
        m2["resource_rules"]["stage_allowance_seconds"] = {"S4": 70.0, "S5": None}
        m2["resource_rules"]["run_allowance_seconds"] = 20.0
        (root / "manifests" / "frozen.json").write_text(json.dumps(m2))
        job = {"arm": "C1", "realization": 0, "perm": 0, "manifest": "manifests/confirm/zsre_r0.json", "dataset": "zsre"}
        assert runner.main(_args(job)) == 0
        assert runner.main(_args(job, force=True)) == 0  # the first attempt is archived, its 31 s stay spent
        exp = next(iter(seen.values()))["experiment_id"]
        assert abs(runner._stage_spent_seconds("S4", exp) - 62.0) < 1e-9
        assert runner.main(_args(dict(job, perm=1))) == 5  # 62 + 20 > 70: refused because archived spending counts
    finally:
        runner.RUNNERS["S4"] = real
        (root / "manifests" / "frozen.json").write_text(json.dumps(man, default=float))
