"""Establish validation coverage from bytes, without evaluating a model."""

from __future__ import annotations

import json

import numpy as np
from scripts import r1_d9_receipts as d9
from scripts.r1_d10a_review import ROOT


def audit():
    inventory = json.loads((ROOT / "manifests/dev/lm_sets.json").read_text())
    tokens_binding = inventory["files"]["drift_tokens"]
    if d9.sha(tokens_binding["path"]) != tokens_binding["sha256"]:
        raise ValueError("validation token source changed")
    tokens = np.load(tokens_binding["path"], allow_pickle=False, mmap_mode="r")
    if list(tokens.shape) != tokens_binding["shape"] or tokens.ndim != 1:
        raise ValueError("validation source shape differs")
    rows = []
    for p in sorted((ROOT / "docs/tasks/R1-64f").glob("*.recipe.json")):
        m = d9.read_metadata(d9.ref(p))
        payload = d9.read_resource(m["payload"])
        drift = payload["endpoints"]["drift"]
        windows = drift["windows"]
        flat = [t for w in windows for t in w]
        rows.append(
            dict(
                recipe=d9.ref(p),
                payload=m["payload"],
                windows=len(windows),
                scored_positions=sum(len(w) - 1 for w in windows),
                declared_positions=drift["expected_positions"],
                source_prefix_equal=np.array_equal(tokens[: len(flat)], flat),
            )
        )
    n = len(tokens)
    full, tail = divmod(n, 128)
    return dict(
        task="R1-58j",
        status="pending",
        model_calls=0,
        producer=d9.ref(__file__),
        source=d9.ref(tokens_binding["path"]),
        source_inventory=d9.ref(ROOT / "manifests/dev/lm_sets.json"),
        validation_tokens=n,
        full_128_token_windows=full,
        complete_window_prediction_positions=full * 127,
        trailing_tokens=tail,
        proposed_tail_inclusive_positions=full * 127 + max(tail - 1, 0),
        tail_policy_admitted=False,
        full_validation_evidence_status="pending",
        recipes=rows,
        governing_sources=[
            d9.ref(ROOT / "docs/updated_plan9.md"),
            d9.ref(ROOT / "docs/R1_stage4_protocol_draft_v5_1.md"),
        ],
        historical_v0_supplement=d9.ref(ROOT / "results/S4/drift_supplement.md"),
        missing_run="Current revision-v1 endpoint states (1000 edits zsRE/CF, actual300 MQuAKE) on the complete declared validation population, cap-on/original and own cap-off references, per-position reselection, finite vectors, measured outer wall/RSS/GPU costs; explicit tail/context and checkpoint policy admission.",
        interpretation="128 windows (16256 predictions) are a disclosed prefix subsample. Driver input-validation/rehash phases check integrity, not LM predictions. Neither can reconstruct unscored losses or costs; historical v0 full-split results have different model states.",
    )


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
