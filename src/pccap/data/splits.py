"""Development reservation (S0-09): the S0 development sample and reserved subjects.

40 zsRE (``zsre_mend_eval``) + 40 CounterFact items chosen by seed 7, written to
``manifests/dev/s0_sample.json`` (with SHA-256 of the source files and of the item texts) and
their subjects/facts to ``manifests/dev/reserved_subjects.json`` so that DATA-02 excludes them
from confirmation. Field mapping follows DATA-00 / SD-9:

* zsRE: prompt ``src``, canonical answer ``answers[0]``, aliases = the ``answers`` list
  deduplicated after normalization (SD-9), paraphrase ``rephrase``, locality ``loc``/``loc_ans``,
  subject ``subject``; the MEND counterfactual ``alt`` is recorded as ``alt`` and not used;
* CounterFact: prompt ``requested_rewrite.prompt.format(subject)``, answer ``target_new.str``,
  aliases ``[target_new.str]``, paraphrases ``paraphrase_prompts``, locality
  ``neighborhood_prompts``, fact id ``case_id``, subject ``requested_rewrite.subject``.

``python -m pccap.data.splits --audit`` prints counts (DATA-01 extends this).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from pccap import ASSETS_ROOT
from pccap.metrics.editing import normalize_answer

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(ASSETS_ROOT) / "data" / "raw"
DEV = ROOT / "manifests" / "dev"
S0_SEED = 7
S0_N = 40


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_zsre(split: str = "eval") -> list[dict]:
    return json.loads((RAW / "zsre" / f"zsre_mend_{split}.json").read_text())


def load_counterfact() -> list[dict]:
    return json.loads((RAW / "counterfact" / "counterfact.json").read_text())


def zsre_item(i: int, r: dict) -> dict:
    answers = [a for a in r.get("answers", []) if a and a.strip()]
    aliases = sorted({normalize_answer(a) for a in answers})
    return {
        "item_id": f"zsre-eval-{i}", "dataset": "zsre", "prompt": r["src"], "answer": answers[0] if answers else "",
        "aliases": aliases, "paraphrases": [r["rephrase"]] if r.get("rephrase") else [],
        "locality_prompts": [r["loc"]] if r.get("loc") else [], "locality_answers": [r["loc_ans"]] if r.get("loc_ans") else [],
        "subject": r["subject"], "fact_id": f"zsre-{i}", "alt": r.get("alt"),
    }


def counterfact_item(r: dict) -> dict:
    rw = r["requested_rewrite"]
    return {
        "item_id": f"cf-{r['case_id']}", "dataset": "counterfact", "prompt": rw["prompt"].format(rw["subject"]),
        "answer": rw["target_new"]["str"], "aliases": [normalize_answer(rw["target_new"]["str"])],
        "paraphrases": list(r.get("paraphrase_prompts", [])), "locality_prompts": list(r.get("neighborhood_prompts", [])),
        "locality_answers": [rw["target_true"]["str"]] * len(r.get("neighborhood_prompts", [])),
        "subject": rw["subject"], "fact_id": f"cf-{r['case_id']}", "target_true": rw["target_true"]["str"],
        "relation_id": rw.get("relation_id"),
    }


def item_digest(item: dict) -> str:
    return hashlib.sha256(f"{item['item_id']}|{item['prompt']}|{item['answer']}".encode()).hexdigest()[:32]


def build_s0_sample(seed: int = S0_SEED, n: int = S0_N) -> dict:
    rng = np.random.default_rng(seed)
    z = load_zsre("eval")
    c = load_counterfact()
    zi = sorted(rng.choice(len(z), size=n, replace=False).tolist())
    ci = sorted(rng.choice(len(c), size=n, replace=False).tolist())
    items = [zsre_item(i, z[i]) for i in zi] + [counterfact_item(c[i]) for i in ci]
    for it in items:
        it["digest"] = item_digest(it)
    return {
        "name": "s0_sample", "mode": "dev", "stage": "S0", "seed": seed,
        "sources": {"zsre_mend_eval.json": _sha(RAW / "zsre" / "zsre_mend_eval.json"),
                    "counterfact.json": _sha(RAW / "counterfact" / "counterfact.json")},
        "zsre_indices": zi, "counterfact_indices": ci, "items": items,
        "sha256_items": hashlib.sha256(json.dumps(items, sort_keys=True).encode()).hexdigest(),
    }


def write_s0_sample() -> tuple[Path, Path]:
    DEV.mkdir(parents=True, exist_ok=True)
    s = build_s0_sample()
    p = DEV / "s0_sample.json"
    p.write_text(json.dumps(s, indent=1) + "\n")
    reserved = {
        "source": "s0_sample.json", "sha256_items": s["sha256_items"],
        "subjects": sorted({it["subject"] for it in s["items"]}),
        "fact_ids": sorted(it["fact_id"] for it in s["items"]),
        "prompts": sorted(it["prompt"] for it in s["items"]),
    }
    q = DEV / "reserved_subjects.json"
    q.write_text(json.dumps(reserved, indent=1) + "\n")
    return p, q


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--write-s0", action="store_true")
    args = ap.parse_args(argv)
    if args.write_s0:
        p, q = write_s0_sample()
        print("wrote", p, q)
    if args.audit:
        s = json.loads((DEV / "s0_sample.json").read_text())
        print(json.dumps({"s0_items": len(s["items"]), "zsre": sum(i["dataset"] == "zsre" for i in s["items"]),
                          "counterfact": sum(i["dataset"] == "counterfact" for i in s["items"]),
                          "sha256_items": s["sha256_items"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
