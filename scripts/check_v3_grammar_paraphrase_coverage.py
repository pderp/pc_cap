"""Count deterministic paraphrase coverage of the v3 inventory, without model execution."""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

os.environ.update(JAX_PLATFORMS="cpu", CUDA_VISIBLE_DEVICES="", PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="2")

import pccap  # noqa: E402,F401
from pccap.data.grammar_streams import stream  # noqa: E402
from pccap.fixtures.grammar_eval import with_paraphrases  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main():
    dst = ROOT / "logs/p2_x2_v3_transition/paraphrase_coverage.json"
    if dst.exists():
        raise SystemExit("Refusing to replace coverage evidence")
    raw = (ROOT / "manifests/frozen.json").read_bytes()
    frozen = json.loads(raw)
    records = []
    for r in frozen["realizations"]:
        items = with_paraphrases(stream(r, 0, int(frozen["stream_lengths"]["grammar_train_count"])))
        rec = {"realization": r, "items": len(items), "paraphrases_per_item": dict(Counter(len(it.paraphrases) for it in items)),
               "zero_paraphrase_item_ids": [it.item_id for it in items if not it.paraphrases]}
        records.append(rec)
        print(json.dumps(rec), flush=True)
    out = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "frozen_name": frozen["name"],
           "frozen_sha256": hashlib.sha256(raw).hexdigest(), "records": records,
           "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in
                             ("src/pccap/fixtures/grammar_eval.py", "src/pccap/data/grammar_streams.py", "src/pccap/analysis/paired.py")},
           "gpu_seconds": 0, "model_weights_loaded": False,
           "limits": "Generator/inventory coverage only; no learner outcomes or prediction metrics. Deterministic seeds need not guarantee a nonempty paraphrase search. Frozen missing-pair rules still apply."}
    with dst.open("x") as f:
        json.dump(out, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
