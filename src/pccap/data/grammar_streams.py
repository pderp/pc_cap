"""DATA-06: grammar task streams, evaluation sets, held-out combinations and the joint-training reference
(plan §6.6 DATA-06; PDF E.1). Items are addressed by generator seeds, so manifests stay small and every
sequence regenerates byte-identically from ``manifests/grammar/generator.json``.

* task ``i`` (i = 0..7) = context ``i`` with its private switch flipped and both shared switches flipped
  (consistent across the stream); the learning item of a sequence is ``(tokens[:p*], tokens[p*])`` — one
  sequence/target pair, never 64 positions;
* three realizations (seeds 0, 1, 2) × five balanced orders (``grammar_generator.balanced_orders``);
  training count per task ∈ {256, 1024, 10000} chosen at S4-02 (all three are addressable);
* evaluation: 2,000 sequences per task (seed block 500_000 + 20_000·context); held-out switch
  combinations (private-only and shared-only flips, 1,000 each per context; seed block 600_000);
* joint-training reference: the union of the eight tasks' training items with the same total count.

``load_task_items(task, realization, n)`` returns ``EditItem`` objects (dataset ``grammar``; ``strata`` =
the causal label); ``stream(realization, order_index, n_per_task)`` concatenates the tasks in the
committed order (the continual stream); ``manifests/grammar/streams.json`` records the addressing.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from pccap.contracts import EditItem
from pccap.fixtures.grammar_generator import (
    CONTEXTS,
    MANIFEST_DIR,
    Grammar,
    Switches,
    balanced_orders,
)

TRAIN_COUNTS = (256, 1024, 10000)
EVAL_PER_TASK = 2000
HELDOUT_PER_TASK = 1000
SEED_TRAIN = 300_000
SEED_EVAL = 500_000
SEED_HELDOUT = 600_000
TASK_STRIDE = 20_000
REAL_STRIDE = 1_000  # realization offset inside a task block (10,000 items max → blocks do not overlap across tasks)


def _item(toks: np.ndarray, p: int, label: dict, item_id: str, task: int) -> EditItem:
    return EditItem(item_id=item_id, digest=hashlib.sha256(item_id.encode()).digest()[:16], prompt="", answer=str(int(toks[p])),
                    aliases=[str(int(toks[p]))], paraphrases=[], locality_prompts=[], prompt_ids=np.asarray(toks[:p], np.int32),
                    answer_ids=np.asarray([toks[p]], np.int32), dataset="grammar", fact_id=f"task{task}", strata=dict(label, task=task))


def train_seed(task: int, realization: int, i: int) -> int:
    return SEED_TRAIN + TASK_STRIDE * task + 10_000 * realization + i  # realizations are disjoint seed ranges


def load_task_items(task: int, realization: int, n: int, grammar: Grammar | None = None) -> list[EditItem]:
    g = grammar or Grammar()
    sw = Switches.task(task)
    out = []
    for i in range(n):
        s = train_seed(task, realization, i)
        toks, p, label = g.sequence(task, sw, s)
        out.append(_item(toks, p, label, f"g{task}-r{realization}-{i}", task))
    return out


def eval_items(task: int, grammar: Grammar | None = None, n: int = EVAL_PER_TASK) -> list[EditItem]:
    g = grammar or Grammar()
    sw = Switches.task(task)
    return [_item(*g.sequence(task, sw, SEED_EVAL + TASK_STRIDE * task + i), f"ge{task}-{i}", task) for i in range(n)]


def heldout_items(task: int, which: str, grammar: Grammar | None = None, n: int = HELDOUT_PER_TASK) -> list[EditItem]:
    g = grammar or Grammar()
    sw = Switches.heldout(task, which)
    off = 0 if which == "private_only" else 5_000
    return [_item(*g.sequence(task, sw, SEED_HELDOUT + TASK_STRIDE * task + off + i), f"gh{task}-{which}-{i}", task) for i in range(n)]


def stream(realization: int, order_index: int, n_per_task: int, grammar: Grammar | None = None) -> list[EditItem]:
    order = balanced_orders(realization)[order_index]
    items: list[EditItem] = []
    for task in order:
        items += load_task_items(task, realization, n_per_task, grammar)
    return items


def joint_reference(realization: int, n_per_task: int, seed: int = 0, grammar: Grammar | None = None) -> list[EditItem]:
    """The same training items as the stream, interleaved uniformly at random (same total count)."""
    items = [it for task in range(CONTEXTS) for it in load_task_items(task, realization, n_per_task, grammar)]
    rng = np.random.default_rng(seed)
    return [items[i] for i in rng.permutation(len(items))]


def write_streams_manifest(out: Path = MANIFEST_DIR / "streams.json") -> dict:
    man = {"generator": "manifests/grammar/generator.json", "tasks": {str(t): {"context": t, "switches": Switches.task(t).to_dict()} for t in range(CONTEXTS)},
           "realizations": [0, 1, 2], "orders": {str(r): balanced_orders(r) for r in range(3)}, "train_counts": list(TRAIN_COUNTS),
           "eval_per_task": EVAL_PER_TASK, "heldout_per_task": HELDOUT_PER_TASK, "heldout_kinds": ["private_only", "shared_only"],
           "seeds": {"train": "300000 + 20000*task + 10000*realization + i", "eval": "500000 + 20000*task + i", "heldout": "600000 + 20000*task + {0|5000} + i"},
           "item_rule": "one sequence/target pair per item: prompt = tokens[:p*], target = tokens[p*] (E.1); no 64-way expansion",
           "joint_reference": "union of the eight tasks' training items at the same per-task count, uniformly interleaved (seed 0)",
           "label": "replacement fixture, no continuity with R8/R9 (PA-2)"}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(man, indent=1))
    return man


if __name__ == "__main__":
    print(json.dumps(write_streams_manifest()["orders"], indent=0))
