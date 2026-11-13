import copy
import json
import unittest
from unittest.mock import patch

from climate import ROOT
from story_evidence import build_story_evidence, validate_story_evidence


class StoryEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch("climate.urlopen", side_effect=AssertionError("Story must stay offline")):
            cls.story = build_story_evidence()

    def test_both_complete_analyses_replay_with_matching_source(self):
        with patch("climate.urlopen", side_effect=AssertionError("Story must stay offline")):
            self.assertEqual(validate_story_evidence(self.story), 2)
        full = self.story["analyses"]["full45"]
        recent = self.story["analyses"]["recent15"]
        self.assertEqual(len(full["annual"]), 45)
        self.assertEqual(len(recent["annual"]), 15)
        self.assertEqual(recent["annual"], [row for row in full["annual"] if row["year"] >= 2011])
        self.assertEqual(full["raw_source"], recent["raw_source"])
        json.dumps(self.story, allow_nan=False)

    def test_story_retains_all_four_periods_and_short_interval_caveat(self):
        rows = self.story["comparison"]
        self.assertEqual([row["window_id"] for row in rows], ["full45", "recent35", "recent25", "recent15"])
        self.assertGreater(rows[0]["slope_per_decade"], 0)
        self.assertLess(rows[-1]["slope_per_decade"], 0)
        self.assertFalse(rows[0]["ordinary_interval_includes_zero"])
        self.assertTrue(rows[-1]["ordinary_interval_includes_zero"])
        self.assertTrue(all(row["evidence"] == "unclear" for row in rows[-1]["conditional_intervals"]))

    def test_modified_summary_is_rejected(self):
        altered = copy.deepcopy(self.story)
        altered["comparison"][0]["slope_per_decade"] += 1
        with self.assertRaisesRegex(ValueError, "story.comparison"):
            validate_story_evidence(altered)

    def test_changed_analysis_or_missing_caveat_is_rejected(self):
        for change in ("trend", "caveat"):
            altered = copy.deepcopy(self.story)
            if change == "trend":
                altered["analyses"]["recent15"]["trend"]["slope_per_decade"] -= 10
            else:
                altered["claim_limits"].pop()
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_story_evidence(altered)

    def test_build_is_deterministic_and_does_not_mutate_frozen_source(self):
        saved = json.loads((ROOT/"evaluation/source-snapshots/tehran-power.json").read_text())
        original = copy.deepcopy(saved)
        first = build_story_evidence(saved)
        second = build_story_evidence(saved)
        self.assertEqual(first, second)
        self.assertEqual(saved, original)


if __name__ == "__main__":
    unittest.main()
