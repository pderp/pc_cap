"""S7-01/02 CPU controls: cloning leaves the original untouched; commuting updates give D = 0 and the same endpoint;
a planted non-commuting pair gives D > 0 and a nonzero damage entry; strata bookkeeping; inventory invariants."""

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from tests.cap.mock_base import make_cap, make_item

from pccap.analysis import s7_01
from pccap.contracts import Budget
from pccap.routers import Full

ROOT = Path(__file__).resolve().parents[2]


class _State:
    def __init__(self, bias):
        self.bias = np.array(bias, np.float64)

    def clone(self):
        return _State(self.bias.copy())


class _Out:
    def __init__(self, code="accepted", rounds=1):
        self.code, self.rounds_used = code, rounds


class _Fake:
    """Logit-bias learner: ``add`` mode commutes exactly; ``overwrite`` mode is order dependent (last writer wins)."""

    def __init__(self, vocab=6, mode="add"):
        self.vocab, self.mode = vocab, mode
        self.state = _State(np.zeros(vocab))

    def export_state(self):
        return self.state.clone()

    def import_state(self, st):
        self.state = st.clone()

    def state_hash(self):
        return hashlib.sha256(self.state.bias.tobytes()).hexdigest()

    def predict(self, ids):
        class R:
            pass

        r = R()
        r.logits = np.tile(self.state.bias, (len(ids), 1))
        return r

    def update_item(self, it):
        y = int(it.answer_ids[0])
        if self.mode == "add":
            self.state.bias[y] += 2.0
        else:
            self.state.bias[:] = 0.0
            self.state.bias[y] = 3.0
        return _Out()


def _items():
    return make_item("i", prompt=(1, 2), answer=(3,)), make_item("j", prompt=(2, 1), answer=(4,))


def test_commuting_updates_give_zero_divergence():
    a, b = _items()
    f = _Fake(mode="add")
    Q = s7_01.evaluation_set(a, b, controls=[np.asarray([0, 1], np.int32)])
    r = s7_01.reversal(lambda: _Fake(mode="add"), f.export_state(), a, b, Q, Full(), Budget())
    assert r["D_ij"]["value"] == 0.0 and r["same_endpoint"]
    assert r["I_ij"] == pytest.approx(r["I_ji"])  # symmetric additive updates: equal (normalizer-only) damage in both orders
    assert r["n_Q"] == {"Q_i": 1, "Q_j": 1, "controls": 1}


def test_planted_non_commuting_pair():
    a, b = _items()
    f = _Fake(mode="overwrite")
    Q = s7_01.evaluation_set(a, b)
    r = s7_01.reversal(lambda: _Fake(mode="overwrite"), f.export_state(), a, b, Q, Full(), Budget())
    assert r["D_ij"]["value"] > 0.0 and not r["same_endpoint"]
    assert r["D_ij"]["value"] <= np.log(2) + 1e-9
    assert r["I_ij"] > 0 and r["I_ji"] > 0  # the later edit overwrites the earlier one: harm in both orders
    assert r["accuracy"]["ij"]["j"][1] == 1.0 and r["accuracy"]["ij"]["i"][1] == 0.0


def test_cloning_leaves_the_checkpoint_untouched_on_the_cap():
    base, cap = make_cap(arm="C1", radii=0.8)
    a, b = make_item("i", prompt=(1, 2, 3), answer=(5,)), make_item("j", prompt=(3, 2, 1), answer=(6,))
    state = cap.export_state()
    h0 = cap.state_hash()
    Q = s7_01.evaluation_set(a, b, controls=[np.asarray([7, 8, 9], np.int32)])

    def mk():
        return make_cap(arm="C1", radii=0.8)[1]

    r = s7_01.reversal(mk, state, a, b, Q, Full(), Budget(A=2.0, R=3, tau_edit=0.1))
    assert cap.state_hash() == h0 and state.content_hash() == cap.export_state().content_hash()
    assert 0.0 <= r["D_ij"]["value"] <= np.log(2) + 1e-9
    for t in ("ij", "ji"):
        assert r["updates"][t]["first"]["rounds"] >= 0 and "allocations" in r["updates"][t]["first"]
    # replaying the same order on a fresh clone reproduces the endpoint (item-keyed randomness, PC-9)
    r2 = s7_01.reversal(mk, state, a, b, Q, Full(), Budget(A=2.0, R=3, tau_edit=0.1))
    assert r2["state_hash"] == r["state_hash"]


def test_damage_matrix_strata_bookkeeping():
    a, b = _items()
    Q = s7_01.evaluation_set(a, b)
    pairs = [("p0", "shared", a, b, Q), ("p1", "private", a, b, Q)]
    out = s7_01.run_pairs(lambda: _Fake(mode="overwrite"), _Fake(mode="overwrite").export_state(), pairs, Full(), Budget())
    dm = out["damage_matrix"]
    assert dm["shared"]["n"] == 1 and dm["private"]["n"] == 1 and dm["near_neighbour"]["status"] == "undefined" and dm["all"]["n"] == 2
    assert dm["all"]["I_positive_fraction"] == 1.0 and dm["all"]["D_ij_mean"] > 0


def test_inventory_invariants():
    if not s7_01.MANIFEST.exists():
        pytest.skip("inventory not built")
    man = json.loads(s7_01.MANIFEST.read_text())
    from pccap.metrics.editing import normalize_answer

    ids = [p["pair_id"] for v in man["pairs"].values() for p in v]
    assert len(ids) == len(set(ids))
    for p in man["pairs"]["zsre"] + man["pairs"]["counterfact"]:
        a, b = p["a"], p["b"]
        assert normalize_answer(a["answer"]) != normalize_answer(b["answer"])
        key = "template" if p["dataset"] == "zsre" else "relation_id"
        if p["stratum"] == "shared":
            assert normalize_answer(a["subject"]) == normalize_answer(b["subject"]) and a[key] != b[key]
        elif p["stratum"] == "near_neighbour":
            assert normalize_answer(a["subject"]) != normalize_answer(b["subject"]) and a[key] == b[key]
        else:
            assert normalize_answer(a["subject"]) != normalize_answer(b["subject"]) and a[key] != b[key]
    from pccap.data import grammar_streams as gs

    lo, hi = gs.SEED_TRAIN, gs.SEED_HELDOUT + gs.TASK_STRIDE * 8 + 10_000
    for p in man["pairs"]["grammar"]:
        for m in ("a", "b"):
            assert not (lo <= p[m]["grammar"]["seed"] < hi)
    for ds, v in man["counts"].items():
        assert all(v[st] <= man["expected"][ds][st] for st in s7_01.STRATA)
    assert man["sha256_pairs"] == hashlib.sha256(json.dumps(man["pairs"], sort_keys=True).encode()).hexdigest()


def test_materialize_grammar_pair():
    man = {"item_id": "g7-2-shared_1-900001", "dataset": "grammar", "grammar": {"context": 2, "kind": "shared_1", "seed": 940_001}}
    it = s7_01.materialize(man)
    assert it.dataset == "grammar" and len(it.answer_ids) == 1 and it.strata["kind"] == "shared_1"


# ----------------------------------------------------------------------------- Lane X regressions (findings 1-3)
class _ParaphraseOnlyLearner:
    """Learning j raises item i's loss only after i's PARAPHRASE prefix (prefix [9, 9]); the prompt prefix is untouched."""

    decode_key_positions = False

    def __init__(self, vocab=6):
        self.vocab, self.state = vocab, _State(np.zeros(vocab))
        self.hurt = 0.0

    def export_state(self):
        st = _State(self.state.bias.copy())
        st.hurt = self.hurt
        return st

    def import_state(self, st):
        self.state, self.hurt = _State(st.bias.copy()), getattr(st, "hurt", 0.0)

    def state_hash(self):
        return hashlib.sha256(self.state.bias.tobytes() + bytes([int(self.hurt)])).hexdigest()

    def predict(self, ids):
        class R:
            pass

        r = R()
        row = self.state.bias.copy()
        if list(np.asarray(ids)[:2]) == [9, 9]:  # the paraphrase prefix
            row = row - self.hurt * (np.arange(self.vocab) == 3)
        r.logits = np.tile(row, (len(ids), 1))
        return r

    def update_item(self, it):
        y = int(it.answer_ids[0])
        if it.item_id == "j":
            self.hurt += 4.0  # damages i's paraphrase answer (token 3) by 4 nats, not its prompt
        else:
            self.state.bias[y] += 2.0
        return _Out()


def test_damage_is_averaged_over_every_prefix_of_Q_i():
    a, b = _items()  # i answers token 3 after prompt [1, 2]
    tok = SimpleNamespace(encode=lambda s: [9, 9], decode=lambda ids: "")
    a = make_item("i", prompt=(1, 2), answer=(3,))
    a = a.__class__(**{**a.__dict__, "paraphrases": ["para"]})
    Q = s7_01.evaluation_set(a, b, tok=tok)
    assert len(Q["Q_i"]) == 2
    r = s7_01.reversal(lambda: _ParaphraseOnlyLearner(), _ParaphraseOnlyLearner().export_state(), a, b, Q, Full(), Budget())
    # the prompt-only diagnostic sees nothing; the D.9 mean over Q_i sees half the 4-nat paraphrase damage
    assert r["I_prompt_only"]["ij"] == pytest.approx(0.0, abs=1e-9)
    ops = r["I_operands"]["ij"]
    per_prefix = [b - a for a, b in zip(ops["after_i"], ops["after_ij"])]
    assert ops["n"] == 2 and per_prefix[0] == pytest.approx(0.0, abs=1e-9) and per_prefix[1] > 1.0
    assert r["I_ij"] == pytest.approx(sum(per_prefix) / 2, abs=1e-9)  # the D.9 mean over Q_i, not the prompt-only value


class _BoundarySpy:
    decode_key_positions = True

    def __init__(self):
        self.calls = []

    def last_logits_batch(self, seqs, phase="query", key_positions=None):
        self.calls.append(([len(s) for s in seqs], None if key_positions is None else list(key_positions)))
        return np.zeros((len(seqs), 6), np.float32)

    def state_hash(self):
        return "x"


def test_s7_losses_carry_the_original_prompt_boundary():
    it = make_item("boundary", prompt=(1, 2), answer=(0, 0))
    spy = _BoundarySpy()
    s7_01.prefix_losses(spy, [np.asarray([1, 2], np.int32), np.asarray([7, 7, 7], np.int32)], it.answer_ids)
    assert spy.calls[0] == ([2, 3, 3, 4], [1, 1, 2, 2])  # each prefix keeps its own original boundary while the answer grows
    spy.calls.clear()
    s7_01.item_exact(spy, it)
    assert all(kp == [1] for _, kp in spy.calls) and [ln for ln, _ in spy.calls] == [[2], [3]]


def test_grammar_seed_block_is_disjoint_from_p4_and_data06():
    from pccap.analysis import (
        s1_p4,  # noqa: F401  (P4 seeds: 1_000_000 + 100_000 k + i; 2_000_000 + 10_000 c + i; 3_000_000 + …; 4_000_000 + …)
    )
    from pccap.data import grammar_streams as gs

    lo = s7_01.GRAMMAR_SEED_BASE
    hi = lo + s7_01.GRAMMAR_STRIDE * 8 + 10_000 + 10_000
    assert lo > 4_200_000 and lo > gs.SEED_HELDOUT + gs.TASK_STRIDE * 8 + 10_000
    assert hi < 10_000_000
