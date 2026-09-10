#!/usr/bin/env python3
"""Lane V: synthetic CPU evidence; never opens real confirmation payloads.

All study fixtures live in a fresh assets/tmp directory. The caller captures stdout
in a new pc_cap log. No shared code, board, environment or real run is changed.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ.update(CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu", PYTHONDONTWRITEBYTECODE="1")
sys.dont_write_bytecode = True

import pytest  # noqa: E402

import pccap  # noqa: E402
from pccap.analysis import s4_05, s4_06  # noqa: E402
from pccap.analysis.paired import analyze_paired  # noqa: E402
from pccap.harness import runner, runs, stage_s4, stage_s5  # noqa: E402
from pccap.harness.freeze import build  # noqa: E402
from pccap.harness.schedule import jobs_from_manifest  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT.parent / "assets/tmp/review_repairs_r2_study"

spec = importlib.util.spec_from_file_location("existing_confirm_controls", ROOT / "tests/harness/test_confirm_cli.py")
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as out:
        json.dump(data, out, default=float)


class FakeEvaluator:
    """Finite synthetic outcomes and deterministic query costs; no model calls."""

    def __init__(self, base, *args):
        self.ledger = base.ledger

    def items(self, learner, items):
        from pccap.contracts import CostRecord
        self.ledger.charge(CostRecord(phase="query", accel_seconds=0.2 * len(items)))
        return [{"es": 1.0, "gs": 1.0, "gs_n": 1, "nll": 0.0,
                 "generated": "a", "stopped_by": "newline"} for _ in items]

    def item(self, learner, item):
        return self.items(learner, [item])[0]

    def locality(self, learner):
        return {"ls_complete_answer": 1.0, "ls_first_token": 1.0, "ls_kl_mean": 0.0, "n": 1}

    def drift(self, learner):
        return None


def main():
    assert not TMP.exists(), "refusing an existing synthetic study directory"
    draft = json.loads((ROOT / "manifests/frozen.draft.json").read_text())
    old_jobs = [j for j in jobs_from_manifest(draft) if j["status"] == "scheduled"]
    literal = Counter(str(runner.run_dir_for(SimpleNamespace(**j))) for j in old_jobs)
    adapted = Counter(str(runner.run_dir_for(SimpleNamespace(**j), "review-freeze", j["dataset"])) for j in old_jobs)
    evidence = {
        "path_probe": {"jobs": len(old_jobs), "literal_old_call_paths": len(literal),
                       "current_api_paths": len(adapted), "note": "The path helper now takes dataset and experiment arguments."}
    }
    denied_reads = []
    with patch.object(Path, "exists", lambda p: str(p) == "/synthetic-only/realization.json"), \
         patch.object(Path, "read_bytes", lambda p: denied_reads.append(str(p)) or b"{}"), \
         contextlib.redirect_stderr(io.StringIO()):
        rc = runner.main(SimpleNamespace(manifest="/synthetic-only/realization.json", mode="confirm"))
    evidence["original_denial_probe"] = {"exit": rc, "payload_reads": len(denied_reads)}

    frozen, pending = build(draft=False)
    bindings = {"zsre": {}, "counterfact": {}, "grammar": None}
    payloads = {}
    for ds in ("zsre", "counterfact"):
        for r in range(3):
            man = helpers.synthetic_manifest(ds, r)
            for item in man["items"]:
                item["paraphrases"] = ["synthetic paraphrase"]
            path = TMP / "manifests" / "confirm" / f"{ds}_r{r}.json"
            write_json(path, man)
            payloads[(ds, r)] = man
            bindings[ds][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    sums = TMP / "manifests" / "confirm" / "SHA256SUMS"
    with sums.open("x") as out:
        for ds in ("zsre", "counterfact"):
            for name, digest in bindings[ds].items():
                out.write(f"{digest}  {name}\n")
    frozen.update(name="synthetic-lane-v", draft=False, dataset_ids=bindings,
                  confirm_dir="manifests/confirm", checkpoints=[2],
                  stream_lengths={"zsre": 8, "counterfact": 6, "c0_initial": 4, "grammar_train_count": None},
                  arm_availability={"B4": "unavailable (synthetic)"})
    frozen["resource_rules"] = {**frozen.get("resource_rules", {}), "run_allowance_seconds": 100.0}
    write_json(TMP / "manifests/frozen.json", frozen)
    events, captures = [], []
    lease_depth = [0]

    @contextlib.contextmanager
    def fake_lease(*args, **kwargs):
        events.append("lease_enter")
        lease_depth[0] += 1
        try:
            yield
        finally:
            lease_depth[0] -= 1
            events.append("lease_exit")

    def det_report():
        events.append("backend_report_inside_lease" if lease_depth[0] else "backend_report_before_lease")
        return {"backend": "synthetic"}

    def base_factory(label, ledger):
        events.append("construct_" + label)
        return SimpleNamespace(name=label, ledger=ledger, checksum=lambda: "synthetic-weight-hash")

    def stream_capture(*args, **kwargs):
        captures.append({"allowance": kwargs.get("resource_stop_seconds"),
                         "checkpoints": list(kwargs.get("checkpoints", []))})
        return runs.run_stream(*args, **kwargs)

    with pytest.MonkeyPatch.context() as mp, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        for module in (runner, runs, stage_s4, stage_s5, s4_06):
            mp.setattr(module, "ROOT", TMP)
        mp.setattr(runner, "RESULTS", TMP / "results")
        mp.setattr(runs, "ASSETS_ROOT", str(TMP / "resources"))
        mp.setattr(runner, "code_commit", lambda: "synthetic-current-code")
        mp.setattr(pccap, "determinism_report", det_report)
        mp.setattr(pccap, "assert_determinism", det_report)
        from pccap.harness import lease
        mp.setattr(lease, "gpu_lease", fake_lease)
        for module in (stage_s4, stage_s5):
            mp.setattr(module, "BPBase", lambda *, ledger: base_factory("BP", ledger))
            mp.setattr(module, "GPT2Tokenizer", lambda: SimpleNamespace())
            mp.setattr(module, "load_dev_items", lambda *args, **kwargs: ([], []))
            mp.setattr(module, "drift_sample", lambda *args: None)
            mp.setattr(module, "Evaluator", FakeEvaluator)
            mp.setattr(module, "run_stream", stream_capture)
        mp.setattr(stage_s4, "make_learner", lambda arm, base, ledger, **kw: helpers.FakeLearner(ledger))
        mp.setattr(stage_s4, "router_for", lambda *args, **kwargs: None)
        mp.chdir(TMP)
        jobs = [j for j in jobs_from_manifest(frozen) if j["status"] == "scheduled"]
        codes = [runner.main(helpers._args(j, no_lease=False)) for j in jobs]
        assert codes == [0] * 150, Counter(codes)
        evidence["real_s4_pipeline"] = {
            "jobs": len(jobs), "successes": codes.count(0),
            "stage": "actual run_s4; actual confirmation loader, selection, run_stream, snapshots and collectors",
            "replacements": "CPU fake base, learner, evaluator, tokenizer, locality inputs and lease only",
            "first_events": events[:5], "first_stream_config": captures[0],
            "paired": {},
        }
        for ds in ("zsre", "counterfact"):
            rows, notes = s4_06.collect_rows(TMP / "results/S4", ds)
            expected = s4_06.expected_from_loader(ds)
            result = analyze_paired(rows, expected_items=expected, stream_id=ds, draws=100)
            evidence["real_s4_pipeline"]["paired"][ds] = {
                "rows": len(rows), "notes": notes, "classification": result["classification"],
                "contrast_status": {k: v["status"] for k, v in result["contrasts"].items()},
            }

        first = next(j for j in jobs if j["dataset"] == "zsre" and j["arm"] == "C2")
        refusal = runner.main(helpers._args(first, no_lease=False))
        forced = runner.main(helpers._args(first, no_lease=False, force=True))
        rows, _ = s4_06.collect_rows(TMP / "results/S4", "zsre")
        try:
            analyze_paired(rows, expected_items=s4_06.expected_from_loader("zsre"), draws=100)
            duplicate = None
        except ValueError as exc:
            duplicate = str(exc)
        all_runs = s4_05.discover([TMP / "results/S4"])
        evidence["archive_probe"] = {
            "refused_exit": refusal, "forced_exit": forced,
            "collector_includes_archives": any(".superseded-" in r["dir"] for r in all_runs),
            "paired_error_after_force": duplicate,
            "asset_checkpoint_policy": "run_stream derives checkpoint directory from unarchived result identity; --force only moves results",
        }

        calibration_calls = []
        def calibration(label, dataset):
            calibration_calls.append({"base": label, "dataset": dataset, "source": "mutable development calibration function"})
            return {1: 1.0, 2: 1.0, 3: 1.0}, {1: 0.0, 2: 0.0, 3: 0.0}
        mp.setattr(stage_s5, "calibration_for", calibration)
        mp.setattr(stage_s5, "Cap", lambda base, config, ledger: helpers.FakeLearner(ledger))
        mp.setattr(stage_s5, "make_router", lambda *args: None)
        # Deliberately change the authoritative in-memory frozen definition:
        # selection should happen before model construction.
        fz5 = {**frozen, "substrate_arms": {"SB": {"base": "EPC", "credit": "adjoint", "credit_iters": 8}},
               "resource_rules": {"run_allowance_seconds": 1.2}}
        cfg = {"arm": "SB", "manifest": "manifests/confirm/zsre_r0.json", "mode": "confirm",
               "dataset": "zsre", "realization": 0, "perm": 0}
        events.clear()
        s5dir = TMP / "results/S5/synthetic/SB"
        m5 = stage_s5.run_s5({"config": cfg, "manifest": None, "frozen": fz5}, s5dir)
        evidence["s5_probe"] = {
            "frozen_base": "EPC", "constructed_base_events": events,
            "calibration_calls": calibration_calls, "stream_arguments": captures[-1],
            "frozen_allowance": 1.2, "frozen_checkpoints": [2], "items_completed": m5["items_completed"],
            "ledger_total": m5["ledger_totals"]["total"]["accel_seconds"], "status": m5["status"],
        }
    evidence["fixture_root"] = str(TMP)
    evidence["production_freeze_or_payload_access"] = False
    evidence["pending_inputs_in_synthetic_seed_only"] = pending
    print(json.dumps(evidence, indent=2, default=float))


if __name__ == "__main__":
    main()
