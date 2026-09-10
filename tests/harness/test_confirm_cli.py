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
