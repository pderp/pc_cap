"""Hook/site definitions shared by the wrappers (PDF F.1; SD-7).

GPT-2 small (D = 12): l_m = round(m*12/3) = 4, 8, 12 -> block indices 3, 7, 11 (HF
``transformer.h[l]`` outputs; the last is taken before ``ln_f``).
Six-layer grammar base (D = 6): l_m = 2, 4, 6 -> block indices 1, 3, 5.
"""

from __future__ import annotations

from pccap.contracts import SiteId


def bank_blocks(n_layer: int) -> dict[int, int]:
    out = {m: round(m * n_layer / 3) - 1 for m in (1, 2, 3)}
    assert len(set(out.values())) == 3, out
    return out


def sites_for(n_layer: int, position: int = -1) -> list[SiteId]:
    bb = bank_blocks(n_layer)
    return [SiteId(m, bb[m], position) for m in (1, 2, 3)]


assert bank_blocks(12) == {1: 3, 2: 7, 3: 11}
assert bank_blocks(6) == {1: 1, 2: 3, 3: 5}
