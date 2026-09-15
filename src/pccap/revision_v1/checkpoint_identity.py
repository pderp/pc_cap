"""Read a NumPy checkpoint's JAX key paths without collapsing list-indexed layers."""

from __future__ import annotations

import re

import numpy as np


def checkpoint_tree(path):
    result = {}
    with np.load(path, allow_pickle=False) as archive:
        if len(set(archive.files)) != len(archive.files):
            raise ValueError("duplicate checkpoint array name")
        for name in archive.files:
            tokens = re.findall(r"\['([^']+)'\]|\[(\d+)\]", name)
            keys = [text if text else int(index) for text, index in tokens]
            if (
                not keys
                or not isinstance(keys[0], str)
                or "".join(f"[{k!r}]" if isinstance(k, str) else f"[{k}]" for k in keys) != name
            ):
                raise ValueError("unsupported checkpoint key path")
            value = archive[name]
            if value.dtype != np.float32 or not np.isfinite(value).all():
                raise ValueError("checkpoint arrays must be finite float32")
            node = result
            for i, k in enumerate(keys):
                if isinstance(k, int):
                    if not isinstance(node, list) or not 0 <= k < 1000:
                        raise ValueError("invalid checkpoint list index")
                    while len(node) <= k:
                        node.append(None)
                elif not isinstance(node, dict):
                    raise ValueError("checkpoint container collision")
                last = i == len(keys) - 1
                existing = node[k] if isinstance(node, list) else node.get(k)
                if last:
                    if existing is not None:
                        raise ValueError("duplicate checkpoint leaf")
                    node[k] = value
                else:
                    container = list if isinstance(keys[i + 1], int) else dict
                    if existing is None:
                        node[k] = container()
                    elif not isinstance(existing, container):
                        raise ValueError("checkpoint container collision")
                    node = node[k]

    def complete(node):
        if node is None:
            raise ValueError("checkpoint list contains an unfilled index")
        if isinstance(node, (dict, list)):
            for v in node.values() if isinstance(node, dict) else node:
                complete(v)

    complete(result)
    return result
