import copy
import json
import unittest
from unittest.mock import patch

from climate import PRESETS, ROOT, payload_hash
from evaluation.replay import verify
from window_analysis import FIXED_WINDOWS, analyze_window, analyze_windows


class FrozenWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved = {
            key: json.loads((ROOT/"evaluation/source-snapshots"/f"{key}-power.json").read_text())
            for key in PRESETS
        }
        with patch("climate.fetch_data", side_effect=AssertionError("Window comparison must stay offline")):
            cls.records = {
                (key, variable): analyze_windows(place, cls.saved[key], variable)
                for key, place in PRESETS.items()
                for variable in ("temperature", "rainfall")
            }

    def test_all_forty_preset_variable_windows_replay_without_network(self):
        self.assertEqual(sum(map(len, self.records.values())), 40)
        with patch("climate.urlopen", side_effect=AssertionError("Replay must stay offline")):
            for (key, variable), records in self.records.items():
                for record, length in zip(records, (45, 35, 25, 15)):
                    with self.subTest(place=key, variable=variable, years=length):
                        self.assertEqual(verify(record), length)
                        self.assertEqual(record["window_context"]["requested_years"], length)
                        self.assertEqual(record["period"]["end"], 2025)
                        json.dumps(record, allow_nan=False)

    def test_window_values_are_subsets_of_same_source_not_resampled(self):
        for (key, variable), records in self.records.items():
            source_hash = payload_hash(self.saved[key]["payload"])
            full = records[0]
            for record in records:
                with self.subTest(place=key, variable=variable, window=record["window_context"]["id"]):
                    start = record["period"]["start"]
                    self.assertEqual(record["annual"], [r for r in full["annual"] if r["year"] >= start])
                    self.assertEqual(record["monthly"], [r for r in full["monthly"] if r["year"] >= start])
                    self.assertEqual(record["provenance"]["payload_sha256"], source_hash)
                    self.assertEqual(record["provenance"]["request_url"], self.saved[key]["request_url"])
                    self.assertEqual(record["provenance"]["fetched_at"], self.saved[key]["fetched_at"])
                    self.assertEqual(record["raw_source"], self.saved[key]["payload"])
                    self.assertEqual(record["analysis"]["settings"], full["analysis"]["settings"])

    def test_source_and_fixed_definitions_are_not_mutated(self):
        source = copy.deepcopy(self.saved["tehran"])
        before = copy.deepcopy(source)
        definitions = copy.deepcopy(FIXED_WINDOWS)
        result = analyze_window(PRESETS["tehran"], source, "temperature", "recent15")
        result["window_context"]["label"] = "changed presentation"
        self.assertEqual(source, before)
        self.assertEqual(FIXED_WINDOWS, definitions)

    def test_mismatched_location_is_rejected_instead_of_relabelled(self):
        with self.assertRaisesRegex(ValueError, "differs"):
            analyze_window(PRESETS["ankara"], self.saved["tehran"], "temperature", "full45")

    def test_missing_month_propagates_to_each_affected_window(self):
        saved = copy.deepcopy(self.saved["tehran"])
        saved["payload"]["properties"]["parameter"]["T2M"]["200606"] = -999
        records = analyze_windows(PRESETS["tehran"], saved, "temperature")
        self.assertEqual([len(r["annual"]) for r in records], [44, 34, 24, 15])
        self.assertEqual([r["excluded_years"] for r in records], [[2006], [2006], [2006], []])
        self.assertEqual([r["checks"]["hac_available"] for r in records], [False, False, False, True])

    def test_arbitrary_window_id_and_variable_are_rejected(self):
        for variable, window in (("temperature", "best_p_value"), ("unknown", "full45")):
            with self.subTest(variable=variable, window=window), self.assertRaises(ValueError):
                analyze_window(PRESETS["tehran"], self.saved["tehran"], variable, window)


if __name__ == "__main__":
    unittest.main()
