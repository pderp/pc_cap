"""PC-1 (PDF F.5, E.1): on the constructed fixture the supplied router (CO) recovers >= 19/20
planted targets within the round budget with unrelated outputs unchanged within 1e-6; the full
fixture oracle reaches >= 95% of planted deterministic targets; the wrong-router variant fails."""

import json
from pathlib import Path

import pytest

from pccap.fixtures import modular_control as mc

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "S0" / "controls"


def test_pc1_twenty_planted_targets_oracle():
    base = mc.ModularControlBase(seed=0)
    items = base.make_items(n_private=12, n_shared=4, n_mixed=4, n_heldout=0)
    unrelated = base.make_items(n_private=0, n_shared=0, n_mixed=0, n_heldout=10, start_index=300)  # different latents, never edited
    # unrelated must have distinct indices from the edited items
    assert {u.index for u in unrelated}.isdisjoint({i.index for i in items})
    res = mc.learn_and_score(base, items, "CO", A=1.0, radius=0.0, unrelated=unrelated)
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "pc1_planted.json").write_text(json.dumps({"control": "PC-1", **{k: v for k, v in res.items() if k != "rows"},
                                                         "rows": res["rows"]}, indent=1, default=float))
    assert res["recovered"] >= 19, res["recovered"]
    assert res["unrelated_max_abs_dp"] <= 1e-6


@pytest.mark.slow
def test_pc1_full_fixture_oracle_and_wrong_router():
    base = mc.ModularControlBase(seed=0)
    items = base.make_items(n_private=45, n_shared=30, n_mixed=45, n_heldout=0)
    res = mc.learn_and_score(base, items, "CO", A=1.0, radius=0.0)
    wrong_base = mc.ModularControlBase(seed=0)
    wrong_items = wrong_base.make_items(n_private=30, n_shared=0, n_mixed=0, n_heldout=0, wrong_router=True)
    wrong = mc.learn_and_score(wrong_base, wrong_items, "CO", A=1.0, radius=0.0)
    (RESULTS / "pc1_full_fixture.json").write_text(json.dumps({"oracle": {k: v for k, v in res.items() if k != "rows"},
                                                              "wrong_router": {k: v for k, v in wrong.items() if k != "rows"}}, indent=1, default=float))
    assert res["recovery_rate"] >= 0.95, res["recovery_rate"]
    assert wrong["recovery_rate"] < 0.5, wrong["recovery_rate"]
