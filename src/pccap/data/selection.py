"""Frozen selection rule for confirmatory streams (R2-04 repair; PDF App. B, D.11).

A realization manifest carries its full item list (the realization's canonical order = the
realization-seed permutation of its subject-disjoint block) and five committed orders (permutations of
all item ids). The confirmatory scope ``n`` selects the **same subset for every order**:

    subset(realization, n) = the first n items of the realization's canonical list
    stream(order, n)       = the committed order filtered to that subset (relative order preserved)
    arm scope n_arm ≤ n    = the first n_arm items of stream(order, n)

so all five orders within a realization edit exactly the same items, and an arm with a smaller scope
(C0 at 300) edits the first 300 items of the same order as the other arms — paired with their
300-item checkpoint. This module is the only place the rule lives; execution (S4/S5), the expected
inventory of the paired analysis (S4-06) and S7 all call it. The rule text is copied into the frozen
manifest (``selection_rule``). No sealed payload is opened here: callers pass the loaded manifest.
"""

from __future__ import annotations

RULE = ("subset = first n items of the realization's canonical item list; each committed order is filtered to that "
        "subset (relative order preserved); an arm with scope n_arm <= n edits the first n_arm items of the filtered order")


def subset_ids(manifest: dict, n: int) -> list[str]:
    ids = [it["item_id"] for it in manifest["items"]]
    if n > len(ids):
        raise ValueError(f"scope {n} exceeds the realization's {len(ids)} items")
    return ids[: int(n)]


def stream_ids(manifest: dict, order_seed: int | str, n: int, n_arm: int | None = None) -> list[str]:
    keep = set(subset_ids(manifest, n))
    order = manifest["orders"][str(order_seed)]
    filtered = [i for i in order if i in keep]
    if len(filtered) != len(keep):
        raise ValueError("committed order does not cover the selected subset")
    return filtered[: int(n_arm)] if n_arm is not None else filtered


def stream_items(manifest: dict, order_seed: int | str, n: int, n_arm: int | None = None) -> list[dict]:
    by_id = {it["item_id"]: it for it in manifest["items"]}
    return [by_id[i] for i in stream_ids(manifest, order_seed, n, n_arm)]
