"""PC-5 (probe half): signed probe scores on an analytic 1-D loss; abstention below threshold;
CR reproduces its choice for the same key across reversed-order replays."""

import numpy as np

from pccap.contracts import DirectionResult, RoundContext, SiteId
from pccap.routers import Measured, Random
from pccap.transport.transport import Transport


def ctx_for(loss, directions, scales=None, permitted=None, key=(0, b"x" * 16, 0, 0)):
    return RoundContext(prefix_ids=np.array([1, 2, 3], np.int32), loss=loss, directions=directions,
                        bank_scales=scales or {1: 1.0, 2: 1.0, 3: 1.0}, rng_material=key, permitted_banks=permitted)


def analytic():
    """One loss with three additive sites: Loss(h1,h2,h3) = (w·(h1+h2+h3) − y)²; a probe at bank m
    adds v to h_m. The baseline L is common to all banks (as for a real base)."""
    w = np.array([1.0, 2.0], np.float32)
    h0 = {1: np.array([1.0, 0.0], np.float32), 2: np.array([0.0, 1.0], np.float32), 3: np.array([2.0, 2.0], np.float32)}
    y = 3.0

    def loss(h):
        return float((w @ sum(h.values()) - y) ** 2)

    return w, h0, y, loss


def test_helpful_positive_harmful_negative_abstain():
    w, h0, y, loss = analytic()
    L = loss(h0)
    tr = Transport()
    g = 2 * (w @ sum(h0.values()) - y) * w  # dL/dh_m is the same at every site
    dirs = {m: tr.direction(g, SiteId(m, 0, 2)) for m in h0}
    calls = []

    def probe(m, v):
        calls.append(m)
        h = dict(h0)
        h[m] = h0[m] + v
        return loss(h)

    r = Measured(probe, epsilon=0.01).schedule(ctx_for(L, dirs))
    assert all(s > 0 for s in r.scores.values()) and r.banks and not r.abstain
    assert r.cost.router_probes == 3 and calls == [1, 2, 3]
    # harmful probe: flip the directions -> negative scores -> abstain
    bad = {m: DirectionResult(d.site, -d.direction, "ok", d.signal_norm) for m, d in dirs.items()}
    r2 = Measured(probe, epsilon=0.01).schedule(ctx_for(L, bad))
    assert all(s < 0 for s in r2.scores.values()) and r2.abstain and "abstain" in r2.codes
    # below threshold: tiny improvement relative to loss -> abstain
    r3 = Measured(lambda m, v: L - 1e-12, epsilon=0.01).schedule(ctx_for(L, dirs))
    assert r3.abstain


def test_largest_positive_score_ties_smallest_index():
    L = 10.0
    dirs = {m: DirectionResult(SiteId(m, 0, 0), np.ones(2, np.float32), "ok", 1.0) for m in (1, 2, 3)}
    gains = {1: 0.5, 2: 0.5, 3: 0.2}
    r = Measured(lambda m, v: L - gains[m], epsilon=0.01).schedule(ctx_for(L, dirs))
    assert r.banks == [1]
    gains = {1: 0.1, 2: 0.9, 3: 0.2}
    r = Measured(lambda m, v: L - gains[m], epsilon=0.01).schedule(ctx_for(L, dirs))
    assert r.banks == [2]


def test_no_direction_banks_are_logged_not_probed():
    dirs = {1: DirectionResult(SiteId(1, 0, 0), None, "no_direction", 0.0),
            2: DirectionResult(SiteId(2, 0, 0), np.ones(2, np.float32), "ok", 1.0)}
    r = Measured(lambda m, v: 1.0).schedule(ctx_for(2.0, dirs))
    assert "no_direction:1" in r.codes and "no_direction:3" in r.codes and 1 not in r.scores


def test_cr_item_keyed_reproducible_and_distribution():
    rt = Random({1: 0.2, 2: 0.3, 3: 0.5})
    dirs = {m: DirectionResult(SiteId(m, 0, 0), np.ones(2, np.float32), "ok", 1.0) for m in (1, 2, 3)}
    keys = [(7, bytes([i]) * 16, i % 3, i % 5) for i in range(200)]
    forward = [rt.schedule(ctx_for(1.0, dirs, key=k)).banks for k in keys]
    backward = [rt.schedule(ctx_for(1.0, dirs, key=k)).banks for k in reversed(keys)]
    assert forward == list(reversed(backward))
    counts = {m: sum(b == [m] for b in forward) for m in (1, 2, 3)}
    assert counts[3] > counts[1]
    assert rt.schedule(ctx_for(1.0, dirs, key=keys[0])).codes[-1].startswith("cr_draw:")
