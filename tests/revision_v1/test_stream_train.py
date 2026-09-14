"""Stream-scale episodes on the tiny CPU base: bank building, populations, no label leakage into query inputs, trainer step."""

from __future__ import annotations

import os

os.environ.setdefault("JAX_PLATFORMS", "cpu")

import jax  # noqa: E402
import numpy as np  # noqa: E402

from pccap.revision_v1.controller import ControllerConfig, init_controller  # noqa: E402
from pccap.revision_v1.observations import ObservationEncoder  # noqa: E402
from pccap.revision_v1.reader import ReaderConfig, init_reader  # noqa: E402
from pccap.revision_v1.stream_train import build_bank, stream_episode  # noqa: E402
from pccap.revision_v1.train import LossConfig, Trainer  # noqa: E402
from tests.revision_v1.tiny_base import CFG, TinyBase  # noqa: E402

RC = ReaderConfig(d=CFG.d, width=8, hidden=8, d_code=6, top_k=2)
CC = ControllerConfig(d=CFG.d, width=8, d_code=6, hidden=8, A=0.3, bank_scales=(1.0, 1.0, 1.0))


class _Tok:
    def encode(self, text):
        return [3 + (ord(c) % 50) for c in text][:12]

    def decode(self, ids):
        return "".join(chr(97 + (i % 26)) for i in ids)


def _rows(n=12):
    r = np.random.default_rng(0)
    rows = []
    for i in range(n):
        rows.append({"item_id": f"cf-{i}", "fact_id": f"cf-{i}", "dataset": "counterfact", "prompt": f"prompt {i}", "answer": "x",
                     "prompt_ids": [int(x) for x in r.integers(1, 60, size=6)], "answer_ids": [int(x) for x in r.integers(1, 60, size=2)],
                     "paraphrases": [f"para {i} a", f"para {i} b"], "locality_prompts": [f"loc {i} a", f"loc {i} b"], "subject": f"s{i}"})
    return rows


def test_bank_and_episode_populations_and_training_step(monkeypatch):
    import pccap.revision_v1.stream_train as st
    monkeypatch.setattr(st, "tokenize_pair", lambda tok, p, a: type("P", (), {"prompt_ids": np.asarray(tok.encode(p), np.int32), "answer_ids": np.asarray([5, 6], np.int32)})())
    base = TinyBase()
    enc = ObservationEncoder(base, taps=RC.taps)
    bank = build_bank(base, enc, _rows(), RC, tok=_Tok())
    assert len(bank.items) == 12 and all(len(it.paraphrases) == 2 and len(it.locality) == 2 for it in bank.items)
    rng = np.random.default_rng(1)
    ep = stream_episode(bank, rng, n_memory=8, n_query_records=3, n_out=2)
    roles = [q.role for q in ep.queries]
    assert len(ep.supports) == 8 and roles.count("own_prompt") == 3 and roles.count("new_paraphrase") == 3 and roles.count("unrelated") == 3 and roles.count("unrelated_no_kl") == 2
    assert all(q.target_record == -1 for q in ep.queries if q.role in ("unrelated", "unrelated_no_kl"))
    assert all(0 <= q.target_record < 8 for q in ep.queries if q.role in ("own_prompt", "new_paraphrase"))
    # locality prefixes carry cap-off logits for the KL; out-of-memory nulls carry none and are L2-only
    assert all(q.prefixes[0].capoff_logits is not None for q in ep.queries if q.role == "unrelated")
    k1, k2 = jax.random.split(jax.random.PRNGKey(0))
    theta = {"reader": init_reader(k1, RC), "controller": init_controller(k2, CC)}
    tr = Trainer(RC, CC, base.params, base.cfg, LossConfig(), lr=1e-3)
    st_ = tr.init(theta)
    theta2, st_, m = tr.outer_step(theta, st_, [ep])
    assert np.isfinite(m["grad_norm"]) and m["retrieval"] > 0 and m["answer_n"] > 0 and m["preserve_n"] == 3
