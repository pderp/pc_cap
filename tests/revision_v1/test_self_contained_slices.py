"""CPU invariants for query-local slices and immutable support labels."""

import copy
import unittest

from scripts.r1_d4b_self_contained import self_contained, validate_slice


class SliceTests(unittest.TestCase):
    def rows(self):
        return [
            {
                "item_id": str(i),
                "subject": str(i),
                "prompt": str(i) + "?",
                "answer": "edit",
                "target_true": "base" + str(i),
                "relation_id": "r" if i < 3 else "s",
                "prompt_ids": [i],
                "answer_ids": [1],
                "paraphrases": ["p" + str(i)],
            }
            for i in range(4)
        ]

    def test_locality_and_near_stay_inside_slice(self):
        rows = self.rows()
        before = copy.deepcopy(rows)
        got = self_contained(rows)
        self.assertEqual(rows, before)
        self.assertEqual(got[0]["locality_prompts"], ["1?", "2?"])
        self.assertEqual(got[0]["locality_answers"], ["base1", "base2"])
        self.assertTrue(
            all(
                n["type"] == "other_relation_in_slice_fallback"
                for n in got[3]["near_miss_candidates"]
            )
        )
        self.assertEqual(self_contained(rows), got)

    def test_reject_escape_or_changed_answer(self):
        rows = self.rows()
        got = self_contained(rows)
        got[0]["locality_prompts"][0] = "outside"
        with self.assertRaises(ValueError):
            validate_slice(got, rows)
        got = self_contained(rows)
        got[0]["answer"] = "changed"
        with self.assertRaises(ValueError):
            validate_slice(got, rows)

    def test_neighbour_reference_tokens_and_identity(self):
        rows = self.rows()
        got = self_contained(rows)
        got[0]["near_miss_candidates"][0]["prompt_ids"] = [999]
        with self.assertRaises(ValueError):
            validate_slice(got, rows)

    def test_single_subject_rejected(self):
        with self.assertRaises(ValueError):
            self_contained(self.rows()[:1])
