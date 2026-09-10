"""DATA-07 verification: the D.10 score on a hand-built three-outcome example; weak pairs excluded and counted;
pairs change exactly one latent and the forced target differs."""

from __future__ import annotations

import numpy as np

from pccap.fixtures.tracing import classify, make_pairs, restoration_score


def test_score_hand_built():
    # clean 0.9, corrupt 0.2 → gap 0.7; restore 0.55 → R = 0.5; restore 0.9 → 1.0; restore 1.0 → overshoot 1.14
    assert abs(restoration_score(0.9, 0.2, 0.55)[0] - 0.5) < 1e-9
    assert abs(restoration_score(0.9, 0.2, 0.9)[0] - 1.0) < 1e-9
    assert restoration_score(0.9, 0.2, 1.0)[0] > 1.0
    assert restoration_score(0.25, 0.2, 0.9) == (None, "weak")
    assert classify({"a": 0.9, "b": 0.1}) == "single_site" and classify({"a": 0.9, "b": 0.7}) == "multi_site"
    assert classify({"a": 0.2, "b": 0.1}) == "no_site" and classify({"a": 1.3, "b": 0.1}) == "overshoot"


def test_pairs_change_one_latent():
    pairs = make_pairs(n_per_kind=5, seed=1)
    assert len(pairs) == 15
    for pr in pairs:
        c, k = np.asarray(pr["clean"]), np.asarray(pr["corrupt"])
        diff = np.flatnonzero(c[: pr["p_star"]] != k[: pr["p_star"]]).tolist()  # the prefix is what the model sees
        assert diff == sorted(pr["changed_positions"]) and pr["target_clean"] != pr["target_corrupt"]
        if pr["kind"] == "shared_1":
            assert diff == [pr["t_in"]]
        else:  # one latent (the class-3 value) changed consistently: only class-3 and class-4 positions can differ
            from pccap.fixtures.grammar_generator import class_of
            assert all(class_of(int(c[i])) in (3, 4) for i in diff) and pr["t_in"] in diff
        assert {s["position"] for s in pr["patch_sites"]} <= {pr["t_in"], pr["p_star"] - 1} and len(pr["patch_sites"]) in (3, 6)
