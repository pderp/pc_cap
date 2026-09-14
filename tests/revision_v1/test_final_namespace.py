"""R1-20c controls use a separate fixture namespace; no reserved final examples."""
from dataclasses import replace
from unittest.mock import patch

import pytest

from pccap.revision_v1 import final_namespace as ns

FIXTURE = ns.Namespace(version="unit-fixture-namespace", entity_start=128, surface_start=160, marker=166, fixture_only=True)


def test_reservation_is_disjoint_and_does_not_emit():
    with patch.object(ns.old, "synthetic_episode", side_effect=AssertionError("must not generate")):
        manifest = ns.reservation()
    assert manifest["final_generation_ready"] and not manifest["final_emission_authorized"]
    assert manifest["final_examples_emitted"] == 0
    sets = [set(v["entity_tokens"]) for v in manifest["partitions"].values()]
    assert all(not a & b for i, a in enumerate(sets) for b in sets[i+1:])
    assert not set(manifest["namespace_tokens"]) & set(range(64))


def test_overlap_and_authorization_refused_before_emission():
    with patch.object(ns.old, "synthetic_episode", side_effect=AssertionError("must not generate")):
        with pytest.raises(ValueError, match="overlaps"):
            ns.generate_episode(0, exposed_namespace_tokens=[64])
        with pytest.raises(ValueError, match="overlaps"):
            ns.generate_episode(0, exposed_entity_ids=["grammar-private-scope-v2:entity-64"])
        with pytest.raises(PermissionError):
            ns.generate_episode(1_000_000, "test")
        with pytest.raises(ValueError, match="seed"):
            ns.generate_episode(1_000_000, "train")
    with pytest.raises(ValueError, match="vocabulary"):
        ns.validate_namespace(ns.DEFAULT, vocab_size=64)


@pytest.mark.parametrize("split,seed", [("train", 0), ("dev", 500000), ("test", 1000000)])
@pytest.mark.parametrize("revision", [False, True])
def test_fixture_transport_semantics_and_label_boundary(split, seed, revision):
    ep = ns.generate_episode(seed, split, spec=FIXTURE, revision=revision)
    assert ep == ns.generate_episode(seed, split, spec=FIXTURE, revision=revision)
    supports = ep.inputs.support_history + ep.inputs.new_support
    qmap = {q.query_id: q for q in ep.inputs.queries}
    for lab in ep.query_labels:
        q = qmap[lab.query_id]
        assert ns.semantic_oracle(q, supports, ep.provenance) == lab.target_ids
        assert q.prompt_ids[0] == FIXTURE.marker
        assert not hasattr(q, "target_ids")
    paras = [qmap[l.query_id] for l in ep.query_labels if l.role == "new_paraphrase"]
    assert len({q.prompt_ids for q in paras}) >= 2
    assert not {q.prompt_ids for q in paras} & {s.prompt_ids for s in supports}
    poison = replace(ep, query_labels=())
    assert poison.prediction_inputs() == ep.prediction_inputs()


def test_whole_episode_rejected_when_paraphrases_exhausted():
    with patch.object(ns.old, "_prefix", side_effect=ValueError("paraphrase family exhausted")):
        with pytest.raises(ValueError, match="paraphrase family exhausted"):
            ns.generate_episode(1, spec=FIXTURE)
