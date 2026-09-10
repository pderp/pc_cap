"""DATA-08: challenge-set construction rules on synthetic pools."""

import numpy as np

from pccap.data import challenges as ch


def test_near_neighbour_and_composition_rules():
    cf = [{"item_id": "cf-1", "prompt": "The mother tongue of A is", "answer": "English", "target_true": "French",
           "locality_prompts": ["The mother tongue of B is"], "subject": "A", "fact_id": "cf-1"},
          {"item_id": "cf-2", "prompt": "X is", "answer": "Same", "target_true": "same", "locality_prompts": ["Y is"], "subject": "X", "fact_id": "cf-2"}]
    zs = [{"item_id": "z1", "prompt": "Where was S born?", "answer": "Paris", "subject": "S", "fact_id": "z1"},
          {"item_id": "z2", "prompt": "What is the capital of Paris?", "answer": "Paris", "subject": "S", "fact_id": "z2"},
          {"item_id": "z3", "prompt": "What did S study?", "answer": "Law", "subject": "S", "fact_id": "z3"},
          {"item_id": "z4", "prompt": "Which country is Paris in?", "answer": "France", "subject": "Paris", "fact_id": "z4"}]
    nn = ch.near_neighbours(cf, zs, np.random.default_rng(0))
    assert any(n["edit_item_id"] == "cf-1" and n["neighbour_answer"] == "French" for n in nn)
    assert not any(n["edit_item_id"] == "cf-2" for n in nn)  # true == new -> not a differing-answer neighbour
    assert any(n["edit_item_id"] == "z1" and n["neighbour_prompt"] == "What did S study?" for n in nn)
    comp = ch.compositions(zs)
    assert [(c["first_item_id"], c["second_item_id"]) for c in comp] == [("z1", "z4"), ("z2", "z4")]
    temp = ch.temporal_corrections(cf, np.random.default_rng(0), n=10)
    assert len(temp) == 1 and temp[0]["versions"][0]["answer"] == "French" and temp[0]["versions"][1]["answer"] == "English"
