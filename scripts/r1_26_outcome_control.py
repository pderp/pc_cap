"""CPU evidence: distinguish atomic rollback from public outcome classification."""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import replace
from pathlib import Path

import numpy as np
from tests.revision_v1.test_learner_cpu import _cfg, _support
from tests.revision_v1.tiny_base import TinyBase

import pccap  # noqa: F401
from pccap.contracts import EditItem
from pccap.harness.ledger import Ledger
from pccap.revision_v1.adapt import FastConfig, adapt_record
from pccap.revision_v1.learner import RevisionCap

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    out = ap.parse_args().output
    if out.exists() or not out.resolve().is_relative_to(ROOT):
        raise ValueError("new repository output required")
    cap = RevisionCap(TinyBase(), replace(_cfg(null_threshold=1.01), fast=FastConfig(steps=0, delta_steps=5, delta_lr=.1)), Ledger())
    adapt_record(cap, _support(0), FastConfig(steps=0))
    cap.store.ceiling_bytes = cap.store.bytes()["total"] + 213
    support = _support(1, fact="f0", rev=2)
    item = EditItem(item_id=support.record_id, digest=b"fixture", prompt="fixture", answer="fixture",
                    aliases=[], paraphrases=[], locality_prompts=[], prompt_ids=np.asarray(support.prompt_ids, np.int32),
                    answer_ids=np.asarray(support.answer_ids, np.int32), dataset="fixture", fact_id=support.fact_id,
                    version=support.revision)
    before = cap.state_hash()
    outcome = cap.update_item(item)
    files = [Path(__file__), ROOT / "src/pccap/revision_v1/learner.py", ROOT / "src/pccap/revision_v1/adapt.py"]
    result = {"task":"R1-X3", "control":"public outcome of delta-capacity rejection", "outcome_code":outcome.code,
              "outcome_codes":outcome.codes, "same_state_hash":before == cap.state_hash(),
              "failed_full_forwards_charged":outcome.cost.full_forwards,
              "sources_sha256":{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}, "gpu_seconds":0}
    with out.open("x") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
