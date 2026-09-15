"""RNG schedules: reproducibility, heldout separation and text-null draw effects."""

import unittest
from types import SimpleNamespace

import numpy as np
from scripts.r1_x9_exposure_audit import key, replay

from pccap.revision_v1.stream_train import FeatureBank


class ReplayTests(unittest.TestCase):
    def bank(self):
        items = []
        for i in range(40):

            def pf(t):
                return SimpleNamespace(ids=np.int32([t]), n=1)

            items.append(
                SimpleNamespace(
                    item_id=str(i),
                    fact_id=str(i),
                    key_last=None,
                    key_span=None,
                    code_last=None,
                    code_span=None,
                    prompt_ids=np.int32([i]),
                    own=[pf(i)],
                    paraphrases=[(None, None, [pf(i + 100)])],
                    locality=[(None, None, pf(i + 200))],
                )
            )
        return FeatureBank(items, "tiny")

    def args(self):
        return dict(
            held_out=5, n_memory=8, n_query_records=3, n_out=2, seed=4, batch=2, text_nulls=0
        )

    def test_deterministic_and_disjoint(self):
        b = self.bank()
        a = self.args()
        x = replay(b, [20, 20], a, 2)
        self.assertEqual(x, replay(b, [20, 20], a, 2))
        self.assertFalse(x[("training_reader", "own_prompt")] & x[("heldout_reader", "own_prompt")])

    def test_text_draws_change_training_schedule(self):
        b = self.bank()
        a = self.args()
        x = replay(b, [40], a, 2)
        a.update(text_nulls=8, text_windows=32)
        self.assertNotEqual(x, replay(b, [40], a, 2))

    def test_no_training_at_zero_steps(self):
        x = replay(self.bank(), [40], self.args(), 0)
        self.assertFalse(any(k[0] == "training_reader" for k in x))
        self.assertIn(key([35]), {key([i]) for i in range(35, 40)})
