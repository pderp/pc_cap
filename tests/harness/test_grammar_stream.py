"""Grammar streams through the shared harness (S3-03 / R2-09): a development run via the real CLI on the CPU,
the scheduler's grammar jobs, and the latent-paraphrase definition (SD-20)."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import numpy as np
import pytest

from pccap.data import grammar_streams as gs
from pccap.fixtures.grammar_eval import GrammarTokenizer, calibration_paths, with_paraphrases
from pccap.fixtures.grammar_generator import Grammar, balanced_orders
from pccap.harness.schedule import jobs_from_manifest

ROOT = Path(__file__).resolve().parents[2]


def test_latent_paraphrases_share_the_target():
    items = with_paraphrases(gs.load_task_items(2, 0, 6))
    tok = GrammarTokenizer()
    g = Grammar()
    for it in items:
        assert 1 <= len(it.paraphrases) <= 2
        for p in it.paraphrases:
            ids = np.asarray(tok.encode(p), np.int32)
            assert not np.array_equal(ids, it.prompt_ids)
            sw = __import__("pccap.fixtures.grammar_generator", fromlist=["Switches"]).Switches(**{k: (tuple(v) if isinstance(v, list) else v) for k, v in it.strata["switches"].items()})
            tgt, kind = g.rule_target(ids, int(it.strata["context"]), sw)
            assert tgt == int(it.answer_ids[0]) and kind == it.strata["kind"]


def test_schedule_has_grammar_jobs():
    man = json.loads((ROOT / "manifests" / "frozen.draft.json").read_text())
    jobs = jobs_from_manifest(man)
    gram = [j for j in jobs if j["dataset"] == "grammar"]
    assert len(gram) == 4 * 15 and all(j["base"] == "GRAM" and j["manifest"] == "manifests/grammar/streams.json" for j in gram)


@pytest.mark.skipif(not all(p.exists() for p in calibration_paths()), reason="grammar calibration absent")
def test_grammar_stream_through_cli(tmp_path):
    import subprocess
    import sys

    man = tmp_path / "s3_gram.json"
    man.write_text(json.dumps({"name": "t", "mode": "dev", "stage": "S3", "seed": 0, "dataset": "grammar", "n_per_task": 2, "locality_prompts": 8, "drift_windows": 2, "checkpoints": [8]}))
    out = ROOT / "results" / "S3" / "dev" / "grammar" / "C1" / "BP" / "h" / "0" / "1"
    shutil.rmtree(out, ignore_errors=True)
    env = dict(os.environ, JAX_PLATFORMS="cpu")
    r = subprocess.run([sys.executable, "-m", "pccap.cli", "run", "--stage", "S3", "--arm", "C1", "--dataset", "grammar", "--perm", "1", "--manifest", str(man), "--no-lease", "--force"],
                       capture_output=True, text=True, env=env, timeout=600)
    assert r.returncode == 0, r.stderr[-800:]
    m = json.loads((out / "metrics.json").read_text())
    assert m["status"] == "complete" and m["config"]["dataset"] == "grammar" and m["config"]["task_order"] == balanced_orders(0)[1]
    assert m["metrics"]["es_immediate"]["value"] is not None and m["metrics"]["gs_immediate"]["value"] is not None
    shutil.rmtree(out, ignore_errors=True)
    shutil.rmtree(Path(os.environ.get("PCCAP_ASSETS", "/home/derp/cap/assets")) / "runs" / "S3" / "dev" / "grammar" / "C1" / "BP" / "h" / "0" / "1", ignore_errors=True)
