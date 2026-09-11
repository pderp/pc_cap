"""Grammar streams through the shared harness (S3-03 / S4 grammar jobs; R2-09).

* ``GrammarTokenizer``: the token shim the evaluator and decoder need (``encode("3 17 22") -> ids``,
  ``decode(ids) -> "3 17 22"``); answers are single tokens, so the common decoder runs with ``max_new = 1``
  and the GPT-2 stop ids never occur in the 64-token vocabulary.
* ``paraphrases`` of a grammar item (SD-20): other sequences of the same context with the same latent
  (the sequence's class-3 value, regenerated through the generator's ``latent_override`` with different
  filler seeds) evaluated at a position where the same mechanism fires — they have the same forced target,
  so GS / RET-GS are defined exactly as for the editing streams.
* locality prompts: base-grammar prefixes at designated positions (the base's own greedy token is the
  reference); LM drift: base-grammar sequences as 64-token windows (per-token NLL under the common
  full-recompute protocol).
* ``grammar_context(...)`` assembles base, tokenizer, items, locality prefixes, drift tokens and the
  calibration for a stage runner; ``calibrate_grammar()`` runs the S2-01 procedure on the grammar base
  (keys of items, paraphrases and unrelated prefixes at the three sites).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from pccap.contracts import EditItem
from pccap.data import grammar_streams as gs
from pccap.fixtures.grammar_generator import (
    CONTEXT_POSITIONS,
    CONTEXTS,
    Grammar,
    Switches,
    class_of,
)
from pccap.fixtures.grammar_model import WEIGHTS, GrammarBase

ROOT = Path(__file__).resolve().parents[3]
N_PARAPHRASES = 2


class GrammarTokenizer:
    name = "grammar-token-shim"

    def encode(self, s) -> list[int]:
        if isinstance(s, str):
            return [int(x) for x in s.split()] if s.strip() else []
        return [int(x) for x in s]

    def decode(self, ids) -> str:
        return " ".join(str(int(x)) for x in ids)


def paraphrase_prefixes(g: Grammar, item: EditItem, n: int = N_PARAPHRASES) -> list[str]:
    """Sequences with the same (context, class-3 latent, mechanism kind) as ``item`` — the same forced target —
    from different filler seeds; returned encoded as shim strings."""
    st = item.strata
    c, kind = int(st["context"]), st["kind"]
    sw = Switches(**{k: (tuple(v) if isinstance(v, list) else v) for k, v in gs_switches(st).items()})
    prefix = np.asarray(item.prompt_ids)
    occ = [i for i in range(len(prefix)) if i not in CONTEXT_POSITIONS and class_of(int(prefix[i])) == 3]
    # the latent = the copy chains' seed values (one under lag 6, two alternating under lag 12): the first two class-3 occurrences
    latent = {"class3": [int(prefix[i]) for i in occ[:2]]} if occ and kind != "shared_1" else None
    out = []
    seed = 800_000 + 7 * int(st.get("seed", 0)) if "seed" in st else 800_000 + hash(item.item_id) % 100_000
    tries = 0
    while len(out) < n and tries < 50:
        toks, p, label = g.sequence(c, sw, seed + tries, kind, latent_override=latent)
        tries += 1
        if int(toks[p]) == int(item.answer_ids[0]) and not np.array_equal(toks[:p], prefix):
            out.append(" ".join(str(int(x)) for x in toks[:p]))
    return out


def gs_switches(strata: dict) -> dict:
    return strata.get("switches") or Switches.task(int(strata["context"])).to_dict()


def with_paraphrases(items: list[EditItem], g: Grammar | None = None) -> list[EditItem]:
    g = g or Grammar()
    out = []
    for it in items:
        st = dict(it.strata)
        st.setdefault("switches", Switches.task(int(st["context"])).to_dict())
        it2 = EditItem(item_id=it.item_id, digest=it.digest, prompt=" ".join(map(str, it.prompt_ids.tolist())), answer=it.answer, aliases=it.aliases,
                       paraphrases=paraphrase_prefixes(g, EditItem(**{**it.__dict__, "strata": st})), locality_prompts=[], prompt_ids=it.prompt_ids,
                       answer_ids=it.answer_ids, dataset="grammar", fact_id=it.fact_id, version=it.version, revision=it.revision, strata=st)
        out.append(it2)
    return out


def locality_prefixes(n: int = 200, seed0: int = 230_000, g: Grammar | None = None) -> list[np.ndarray]:
    g = g or Grammar()
    out = []
    for i in range(n):
        toks, p, _ = g.sequence(i % CONTEXTS, Switches.base(), seed0 + i)
        out.append(np.asarray(toks[:p], np.int32))
    return out


def drift_tokens(n_windows: int = 64, seed0: int = 240_000, g: Grammar | None = None) -> np.ndarray:
    g = g or Grammar()
    return np.concatenate([g.sequence(i % CONTEXTS, Switches.base(), seed0 + i)[0] for i in range(n_windows)]).astype(np.int32)


def calibration_paths() -> tuple[Path, Path]:
    return ROOT / "results" / "S2" / "radius_calibration_GRAM.json", ROOT / "results" / "S2" / "residual_scales_GRAM.json"


def calibrate_grammar(n_items: int = 300, n_unrelated: int = 1000, out_dir: Path | None = None) -> dict:
    """S2-01 on the grammar base: residual scales b_m and per-bank radii from item keys, paraphrase keys and
    unrelated prefixes (the same ``calibrate_radii`` as the editing streams)."""
    from pccap.cap.calibrate import FALSE_FIRE_MAX, N_QUANTILES, calibrate_radii, residual_scales
    from pccap.cap.features import z as zfeat

    base = GrammarBase(weights=WEIGHTS)
    g = Grammar()
    items = with_paraphrases([it for t in range(CONTEXTS) for it in gs.load_task_items(t, 0, n_items // CONTEXTS, g)], g)
    tok = GrammarTokenizer()

    def keys_for(prefixes):
        out = {1: [], 2: [], 3: []}
        for k in range(0, len(prefixes), 64):
            logits, rows, full, n = base.forward_batch(prefixes[k: k + 64], None, phase="query")
            rows = np.asarray(rows)
            for m in (1, 2, 3):
                out[m].append(np.asarray(zfeat(rows[:, m - 1])))
        return {m: np.concatenate(v) for m, v in out.items()}

    scales = residual_scales(base, [{"prompt_ids": it.prompt_ids.tolist(), "answer_ids": it.answer_ids.tolist(), "prompt": it.prompt} for it in items])
    ek = keys_for([it.prompt_ids for it in items])
    para, owner = [], []
    for i, it in enumerate(items):
        for p in it.paraphrases:
            para.append(np.asarray(tok.encode(p), np.int32))
            owner.append(i)
    pk = keys_for(para)
    uk = keys_for(locality_prefixes(n_unrelated, g=g))
    radii = calibrate_radii(ek, pk, np.asarray(owner), uk)
    rc, rs = calibration_paths() if out_dir is None else (out_dir / "radius_calibration_GRAM.json", out_dir / "residual_scales_GRAM.json")
    rc.parent.mkdir(parents=True, exist_ok=True)
    rs.write_text(json.dumps({"per_dataset": {"grammar": scales}, "pooled_b_m": scales["b_m"], "base": "GRAM", "weights": str(WEIGHTS)}, indent=1))
    rc.write_text(json.dumps({"per_dataset": {"grammar": radii}, "pooled_radii_min_over_datasets": {m: radii[m]["radius"] for m in radii}, "false_fire_max": FALSE_FIRE_MAX,
                              "grid": f"{N_QUANTILES}-quantile", "base": "GRAM", "weights": str(WEIGHTS), "read": "h", "paraphrases": "SD-20: same (context, latent, kind), different filler"}, indent=1))
    return {"b_m": scales["b_m"], "radii": {m: radii[m]["radius"] for m in radii}}


def grammar_context(realization: int, perm: int, n_per_task: int, locality: int = 200, drift_windows: int = 64, ledger=None) -> dict:
    """Everything a stage runner needs to run a grammar stream: base (trained replacement), tokenizer shim, items
    (the committed task order with paraphrases), locality prefixes, drift tokens, calibration, max_new = 1."""
    g = Grammar()
    base = GrammarBase(weights=WEIGHTS, ledger=ledger)
    items = with_paraphrases(gs.stream(realization, perm, n_per_task, g), g)
    rc, rs = calibration_paths()
    if not (rc.exists() and rs.exists()):
        raise FileNotFoundError("grammar calibration missing: run pccap.fixtures.grammar_eval.calibrate_grammar()")
    radii = {int(m): float(v["radius"]) for m, v in json.loads(rc.read_text())["per_dataset"]["grammar"].items()}
    b_m = {int(m): float(v) for m, v in json.loads(rs.read_text())["pooled_b_m"].items()}
    return {"base": base, "tok": GrammarTokenizer(), "items": items, "unrelated": locality_prefixes(locality, g=g), "drift": drift_tokens(drift_windows, g=g),
            "radii": radii, "b_m": b_m, "max_new": 1, "drift_window": 64}


if __name__ == "__main__":
    print(json.dumps(calibrate_grammar(), indent=1))
