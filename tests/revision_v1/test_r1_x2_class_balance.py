"""R1-X2 controls for the concurrent cfc6db6 class-balance change (CPU)."""
from dataclasses import replace

import numpy as np

from pccap.revision_v1.episodes import synthetic_episode
from pccap.revision_v1.observations import ObservationEncoder
from pccap.revision_v1.train import featurize, retrieval_loss
from tests.revision_v1.test_train_reference import RC, _setup


def test_balanced_loss_is_mean_of_class_means_and_duplicate_class_invariant():
    base, feats, theta = _setup()
    null = [q for q in feats.queries if q.target_record < 0]
    record = [q for q in feats.queries if q.target_record >= 0]
    assert null and record
    n = replace(feats, queries=null)
    r = replace(feats, queries=record)
    expected = .5 * (float(retrieval_loss(theta, RC, n, False)) + float(retrieval_loss(theta, RC, r, False)))
    balanced = float(retrieval_loss(theta, RC, feats, True))
    np.testing.assert_allclose(balanced, expected, atol=1e-6)
    duplicated = replace(feats, queries=null*5 + record)
    np.testing.assert_allclose(retrieval_loss(theta, RC, duplicated, True), balanced, atol=1e-6)
    assert abs(float(retrieval_loss(theta, RC, duplicated, False))-float(retrieval_loss(theta, RC, feats, False))) > 1e-6


def test_single_class_falls_back_to_finite_query_mean():
    base, feats, theta = _setup()
    for want_null in (True,False):
        only = replace(feats, queries=[q for q in feats.queries if (q.target_record < 0)==want_null])
        b = float(retrieval_loss(theta, RC, only, True))
        u = float(retrieval_loss(theta, RC, only, False))
        assert np.isfinite(b)
        np.testing.assert_allclose(b,u,atol=1e-6)


def test_history_own_prompt_supervision_is_explicit_opt_in():
    base, feats, theta = _setup()
    ep = synthetic_episode(3)
    all_own = featurize(base, ObservationEncoder(base,taps=RC.taps), ep, RC, own_prompt_history=True)
    assert sum(q.role=="own_prompt" for q in feats.queries)==len(ep.inputs.new_support)
    assert sum(q.role=="own_prompt" for q in all_own.queries)==len(ep.inputs.new_support)+len(ep.inputs.support_history)
