#!/usr/bin/env python3
"""Lane V2: synthetic CPU evidence; never opens real confirmation payloads.

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
TMP = ROOT.parent / ("assets/tmp/review_repairs_r2b_" + __import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))

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
                  confirm_dir="manifests/confirm",
                  stream_lengths={"zsre": 8, "counterfact": 6, "c0_initial": 4, "grammar_train_count": None},
                  arm_availability={"B4": "unavailable (synthetic)"})
    frozen["resource_rules"] = {**frozen.get("resource_rules", {}), "run_allowance_seconds": 100.0}
    from pccap.harness.schema import validate
    validate("manifest_frozen", frozen)
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
        mp.setattr(runner, "ASSETS_RUNS", TMP / "resources/runs")
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
            "asset_checkpoint_policy": "Results and checkpoint directories now archive together; distinct-state byte check follows",
        }


        # Fresh synthetic variants of the freeze, never the production final manifest.
        import copy

        from pccap.analysis import s7_03
        from pccap.harness.freeze import tree_sha
        def set_freeze(obj):
            (TMP / "manifests/frozen.json").write_text(json.dumps(obj, default=float))
        def variant(name, mutate=None):
            obj = copy.deepcopy(frozen)
            obj["name"] = "v2-" + name
            if mutate:
                mutate(obj)
            set_freeze(obj)
            return obj
        def invoke_job(obj, **kw):
            return runner.main(helpers._args(first, no_lease=False, **kw))
        negatives = {}
        for label, kw in [("negative_order", {"perm": -1}), ("past_last_order", {"perm": 5}),
                          ("wrong_realization", {"realization": 3}), ("wrong_base", {"base": "EPC"}),
                          ("wrong_read", {"read": "g"}), ("unknown_arm", {"arm": "ZZ"})]:
            obj = variant(label)
            negatives[label] = invoke_job(obj, **kw)
        obj = variant("changed-code", lambda f: f["code_commit"].update(src_tree_sha256="0"*64))
        negatives["changed_code"] = invoke_job(obj)
        negatives["approved_code_drift_flag"] = invoke_job(obj, allow_code_drift=True)
        # False frozen hashes suffice to test whether actual runtime artifacts are bound:
        # no real model/tokenizer resource bytes need to be changed.
        obj = variant("wrong-bp-hash", lambda f: f["base_checkpoints"]["bp"].update(param_digest="1"*64, safetensors_sha256="2"*64))
        negatives["bp_frozen_digest_mismatch"] = invoke_job(obj)
        obj = variant("wrong-tokenizer-hash", lambda f: f["tokenizer_rev"].update(tokenizer_json_sha256="3"*64))
        negatives["tokenizer_frozen_hash_mismatch"] = invoke_job(obj)
        evidence["negative_controls"] = negatives
        assert all(negatives[k] == 2 for k in ("negative_order", "past_last_order", "wrong_realization", "wrong_base", "wrong_read", "unknown_arm", "changed_code"))
        assert negatives["approved_code_drift_flag"] == 0

        # Missing S5 authority and checkpoint mismatch must refuse before construction.
        epc_file = TMP / "resources/synthetic-epc.npz"
        epc_file.parent.mkdir(parents=True, exist_ok=True)
        epc_file.write_bytes(b"synthetic checkpoint for hash-only control")
        epc_identity = {"path": str(epc_file), "sha256": hashlib.sha256(epc_file.read_bytes()).hexdigest()}
        s5_results = {}
        def make_s5(name):
            obj = variant(name)
            obj["substrate_arms"]["SB"] = {"base": "EPC", "credit": "adjoint", "credit_iters": 8}
            obj["base_checkpoints"]["epc"] = epc_identity.copy()
            obj["calibration"]["EPC"] = copy.deepcopy(obj["calibration"]["BP"])
            obj["calibration"]["EPC"]["b_m"] = {"1": 7., "2": 8., "3": 9.}
            obj["calibration"]["EPC"]["radii"]["zsre"] = {"1": .21, "2": .22, "3": .23}
            obj["resource_rules"]["run_allowance_seconds"] = 1.2
            return obj
        mp.setattr(stage_s5, "EPCBase", SimpleNamespace(from_npz=lambda path, ledger: base_factory("EPC", ledger)))
        cap_configs = []
        def fake_cap(base, config, ledger):
            cap_configs.append({"read": config.read, "radii": config.radii, "b_m": config.bank_scales})
            return helpers.FakeLearner(ledger)
        mp.setattr(stage_s5, "Cap", fake_cap)
        mp.setattr(stage_s5, "make_router", lambda *a: None)
        mp.setattr(stage_s5, "calibration_for", lambda *a: (_ for _ in ()).throw(AssertionError("mutable calibration read")))
        mp.setattr(stage_s5, "epc_weights", lambda: (_ for _ in ()).throw(AssertionError("mutable checkpoint read")))
        for name in ("missing-arm", "missing-calibration", "bad-checkpoint", "valid-frozen"):
            obj = make_s5(name)
            if name == "missing-arm":
                obj["substrate_arms"].pop("SB")
            elif name == "missing-calibration":
                obj["calibration"].pop("EPC")
            elif name == "bad-checkpoint":
                obj["base_checkpoints"]["epc"]["sha256"] = "0"*64
            set_freeze(obj)
            events.clear()
            rc = runner.main(helpers._args(first, stage="S5", arm="SB", no_lease=False))
            s5_results[name] = {"exit": rc, "events": list(events)}
            if name == "valid-frozen":
                s5_results[name]["stream"] = captures[-1]
                s5_results[name]["cap_config"] = cap_configs[-1]
        evidence["s5_frozen_authority"] = s5_results
        assert s5_results["valid-frozen"]["exit"] == 0
        assert all(not any(e.startswith("construct_") for e in s5_results[n]["events"]) for n in ("missing-arm", "missing-calibration", "bad-checkpoint"))

        # Force the same cell to a distinct learned state; both result and external
        # checkpoint bytes must remain present at the archived identity.
        obj = variant("force-state")
        assert invoke_job(obj) == 0
        _, fsha, _ = runner.load_manifest(TMP/"manifests/frozen.json", "confirm")
        exp = runner.experiment_id(helpers._args(first), obj, fsha)
        rd = runner.run_dir_for(helpers._args(first), exp, first["dataset"])
        ck = runner.ASSETS_RUNS / rd.relative_to(runner.RESULTS) / "learner_end.ckpt"
        old_bytes = ck.read_bytes()
        old_hash = json.loads((rd/"checkpoints.json").read_text())[-1]["state_hash"]
        class ChangedLearner(helpers.FakeLearner):
            def __init__(self, ledger):
                super().__init__(ledger)
                self.n = 100
        with pytest.MonkeyPatch.context() as sub:
            sub.setattr(stage_s4, "make_learner", lambda arm, base, ledger, **kw: ChangedLearner(ledger))
            assert invoke_job(obj, force=True) == 0
        new_hash = json.loads((rd/"checkpoints.json").read_text())[-1]["state_hash"]
        archived_ck = list(ck.parent.parent.glob(ck.parent.name+".superseded-*/learner_end.ckpt"))
        archived_rd = list(rd.parent.glob(rd.name+".superseded-*"))
        evidence["force_distinct_state"] = {"old_state_hash": old_hash, "new_state_hash": new_hash,
            "distinct": old_hash != new_hash, "archived_checkpoints": len(archived_ck),
            "old_checkpoint_bytes_preserved": len(archived_ck)==1 and archived_ck[0].read_bytes()==old_bytes,
            "archived_result_dirs": len(archived_rd)}
        assert evidence["force_distinct_state"]["distinct"]
        assert evidence["force_distinct_state"]["old_checkpoint_bytes_preserved"]

        # Two experiments with the same cells. Explicit filters must select exactly
        # one; the unfiltered APIs must not silently erase experiment identity.
        first_exp = exp
        obj = variant("second-experiment")
        assert invoke_job(obj) == 0
        _, fsha, _ = runner.load_manifest(TMP/"manifests/frozen.json", "confirm")
        second_exp = runner.experiment_id(helpers._args(first), obj, fsha)
        mini = TMP / "two_experiments"
        # Links are inside the new fixture tree and read existing synthetic results only.
        mini.mkdir()
        (mini/first_exp).symlink_to(TMP/"results/S4"/first_exp, target_is_directory=True)
        (mini/second_exp).symlink_to(TMP/"results/S4"/second_exp, target_is_directory=True)
        # Path.rglob does not recurse directory symlinks on all supported Python versions;
        # use real copies of this synthetic result subset for portable collector controls.
        import shutil
        physical = TMP / "two_experiment_copies"
        shutil.copytree(TMP/"results/S4"/first_exp, physical/first_exp)
        shutil.copytree(TMP/"results/S4"/second_exp, physical/second_exp)
        both = s4_05.discover([physical])
        filtered = s4_05.discover([physical], first_exp)
        pair_rows, _ = s4_06.collect_rows(physical, "zsre", first_exp)
        unfiltered_rows, _ = s4_06.collect_rows(physical, "zsre")
        order_all = s7_03.load_runs(physical, "zsre", "C2")
        order_one = s7_03.load_runs(physical, "zsre", "C2", first_exp)
        evidence["two_experiments"] = {"unfiltered_resource_runs": len(both), "filtered_resource_runs": len(filtered),
            "filtered_paired_rows": len(pair_rows), "unfiltered_paired_rows": len(unfiltered_rows),
            "unfiltered_order_cells": len(order_all), "filtered_order_cells": len(order_one),
            "resource_view_cells": len(s4_05.views(both)["comparable_compute"])}
        assert len(both)==2 and len(filtered)==1 and len(pair_rows)==8 and len(unfiltered_rows)==16
        # A legacy/unknown identity is not safe to include in a selected experiment.
        legacy_dir = physical / "legacy"
        shutil.copytree(TMP/"results/S4"/second_exp, legacy_dir)
        for path in legacy_dir.rglob("metrics.json"):
            data = json.loads(path.read_text())
            data["config"].pop("experiment_id", None)
            path.write_text(json.dumps(data))
        evidence["unknown_experiment_filter"] = {
            "resource_runs": len(s4_05.discover([physical], first_exp)),
            "paired_rows": len(s4_06.collect_rows(physical, "zsre", first_exp)[0]),
            "expected_resource_runs": 1, "expected_paired_rows": 8}

        # Stage allowance ordinary gate, None-run loophole, archive spend loss.
        obj = variant("stage-limited")
        obj["resource_rules"].update(run_allowance_seconds=20., stage_allowance_seconds={"S4": 25., "S5": None})
        set_freeze(obj)
        first_rc = invoke_job(obj)
        second_rc = invoke_job(obj, perm=1)
        evidence["stage_allowance"] = {"first_exit": first_rc, "second_exit": second_rc}
        obj = variant("stage-without-run-cap")
        obj["resource_rules"].update(run_allowance_seconds=None, stage_allowance_seconds={"S4": .01, "S5": None})
        set_freeze(obj)
        rc = invoke_job(obj)
        _, fsha, _ = runner.load_manifest(TMP/"manifests/frozen.json", "confirm")
        stage_exp = runner.experiment_id(helpers._args(first), obj, fsha)
        rd = runner.run_dir_for(helpers._args(first), stage_exp, first["dataset"])
        cfg = json.loads((rd/"config.json").read_text()) if (rd/"config.json").exists() else {}
        evidence["stage_without_run_allowance"] = {"exit": rc, "declared_enforced": cfg.get("stage_allowance_enforced"),
            "stage_allowance": .01, "recorded_spend": runner._stage_spent_seconds("S4", stage_exp)}
        # Keep original freeze for expected-item collection provenance.
        set_freeze(frozen)
        evidence["source_tree_end"] = tree_sha(ROOT/"src/pccap")
    evidence["fixture_root"] = str(TMP)
    evidence["production_freeze_or_payload_access"] = False
    evidence["pending_inputs_in_synthetic_seed_only"] = pending
    print(json.dumps(evidence, indent=2, default=float))


if __name__ == "__main__":
    main()
